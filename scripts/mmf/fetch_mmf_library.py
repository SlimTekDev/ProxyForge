"""
Fetch MyMiniFactory library for a user and write JSON in the shape expected by mmf_hydrator.
  - data_library: read IDs from data/mmf/library_ids.txt and fetch via /api/data-library/objects (full library).
  - objects: GET /users/{username}/objects (objects you uploaded).
Writes last_sync.json with content hash for sync-check (only run hydrator when changed).

Setup:
  - MMF_USERNAME: your MyMiniFactory username.
  - MMF_LIBRARY_SOURCE: "data_library" (default when library_ids.txt has IDs) or "objects" (your uploads only).
  - Auth: MMF_API_KEY (OAuth token) or MMF_SESSION_COOKIE (browser cookie; F12 -> Network -> copy Cookie header).
  - Output: data/mmf/mmf_download.json and data/mmf/last_sync.json.
  - MMF_ENRICH_PREVIEW=1: after data-library fetch, for each object missing previewUrl, GET /api/v2/objects/{id}
    to fill preview (and url) from full object. Slower but ensures images; set MMF_ENRICH_DELAY (default 0.3).
  - MMF_ENRICH_IMAGES=1: after fetch (and optional _enrich_previews), GET /api/v2/objects/{id} for every
    object and merge full image list (for Digital Library gallery carousel). Updates all records; may take
    a long time (rate-limited). Run hydrator after. Alternative: use scripts/mmf/backfill_stl_images.py to
    update images_json in the DB only (no full library re-fetch).
"""

import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    print("Install requests: pip install requests")
    sys.exit(1)

try:
    from curl_cffi import Session as CurlSession
    CURL_CFFI_AVAILABLE = True
except ImportError:
    CurlSession = None
    CURL_CFFI_AVAILABLE = False

# -----------------------------------------------------------------------------
# Config: override via env or .env (copy .env.example to .env)
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parent.parent
try:
    from dotenv import load_dotenv
    load_dotenv(REPO_ROOT / ".env")
except ImportError:
    pass

DATA_MMF = REPO_ROOT / "data" / "mmf"
OUTPUT_JSON = DATA_MMF / "mmf_download.json"
LAST_SYNC_JSON = DATA_MMF / "last_sync.json"

MMF_API_BASE = "https://www.myminifactory.com/api/v2"
MMF_WEB_BASE = "https://www.myminifactory.com"  # for non-v2 endpoints like /api/data-library/objects
# Set your MyMiniFactory username here (or set env MMF_USERNAME).
MMF_USERNAME = (os.environ.get("MMF_USERNAME") or "").strip()
MMF_API_KEY = (os.environ.get("MMF_API_KEY") or "").strip()  # OAuth2 access token from get_mmf_token.py
MMF_SESSION_COOKIE = (os.environ.get("MMF_SESSION_COOKIE") or "").strip()  # Browser Cookie header; alternative to API key
# What to fetch:
#   - "data_library": read IDs from library_ids.txt, use /api/data-library/objects (full library)
#   - "objects": your uploads via /users/{username}/objects
MMF_LIBRARY_SOURCE = (os.environ.get("MMF_LIBRARY_SOURCE") or "").strip().lower()
if MMF_LIBRARY_SOURCE not in ("objects", "data_library"):
    MMF_LIBRARY_SOURCE = "data_library"
LIBRARY_IDS_FILE = DATA_MMF / "library_ids.txt"  # one numeric ID per line, e.g. 763934

def _resolve_library_ids_file() -> Path:
    """Use repo data/mmf/library_ids.txt; fallback to cwd/data/mmf/ or cwd/library_ids.txt."""
    if LIBRARY_IDS_FILE.exists():
        return LIBRARY_IDS_FILE
    cwd = Path.cwd()
    for candidate in (cwd / "data" / "mmf" / "library_ids.txt", cwd / "library_ids.txt"):
        if candidate.exists():
            return candidate
    return LIBRARY_IDS_FILE

_ids_file_count: int = 0
_LIBRARY_IDS_FILE_RESOLVED = _resolve_library_ids_file()
if _LIBRARY_IDS_FILE_RESOLVED.exists():
    try:
        with open(_LIBRARY_IDS_FILE_RESOLVED, "r", encoding="utf-8") as f:
            _id_lines = [ln.strip() for ln in f if ln.strip() and ln.strip().isdigit()]
        _ids_file_count = len(_id_lines)
        if _ids_file_count and MMF_LIBRARY_SOURCE != "objects":
            # Use full library from file unless they explicitly asked for "objects" (uploaded only)
            MMF_LIBRARY_SOURCE = "data_library"
    except Exception:
        pass
DATA_LIBRARY_CHUNK_SIZE = int(os.environ.get("MMF_LIBRARY_CHUNK_SIZE", "50"))  # IDs per request; 50 = fewer requests for 10k+ libs
DATA_LIBRARY_DELAY = float(os.environ.get("MMF_LIBRARY_DELAY", "0.5"))  # seconds between requests (avoid rate limiting)
PER_PAGE = 100
# Enrich objects missing previewUrl by fetching full object from GET /api/v2/objects/{id} (slower but gets images)
MMF_ENRICH_PREVIEW = os.environ.get("MMF_ENRICH_PREVIEW", "").strip().lower() in ("1", "true", "yes")
# Enrich all objects that have no images: GET full object and merge images (for Digital Library gallery)
MMF_ENRICH_IMAGES = os.environ.get("MMF_ENRICH_IMAGES", "").strip().lower() in ("1", "true", "yes")
ENRICH_DELAY = float(os.environ.get("MMF_ENRICH_DELAY", "0.3"))  # seconds between enrichment requests
MMF_DEBUG_IMAGES = os.environ.get("MMF_DEBUG_IMAGES", "").strip().lower() in ("1", "true", "yes")  # log first full-object keys


def _extract_images_list(api_obj: dict) -> list:
    """Extract list of {url, thumbnailUrl} from API object. Tries 'images', 'Images', nested 'media.images', etc.
    Handles MMF full-object shape where each image has 'original': {'url': '...'} instead of top-level 'url'."""
    raw = (
        api_obj.get("images")
        or api_obj.get("Images")
        or (isinstance(api_obj.get("media"), dict) and api_obj["media"].get("images"))
        or api_obj.get("gallery")
    )
    if not isinstance(raw, list) or len(raw) == 0:
        return []
    out = []
    for img in raw[:50]:
        if isinstance(img, dict):
            # MMF full object uses original: {url: "..."}; list may use top-level url/thumbnailUrl
            u = img.get("url") or (img.get("original") or {}).get("url") or img.get("thumbnailUrl")
            if not u and isinstance(img.get("thumbnail"), dict):
                u = img.get("thumbnail", {}).get("url")
            if not u and isinstance(img.get("thumbnail"), str):
                u = img.get("thumbnail")
            u = (u or "").strip()
            thumb = img.get("thumbnailUrl") or (img.get("thumbnail") or {}).get("url") if isinstance(img.get("thumbnail"), dict) else img.get("thumbnail") or u
            thumb = (thumb or u).strip() if isinstance(thumb, str) else (u or "")
            if u:
                out.append({"url": u, "thumbnailUrl": thumb or u})
        elif isinstance(img, str) and img.strip():
            u = img.strip()
            out.append({"url": u, "thumbnailUrl": u})
    return out


def _normalize_object(api_obj: dict) -> dict:
    """Map MMF API object (full or minimal) to the shape mmf_hydrator expects: id, name, creator.name, previewUrl, url."""
    raw_id = api_obj.get("id") or api_obj.get("originalId")
    if raw_id is None:
        return None
    if isinstance(raw_id, (int, float)):
        obj_id = f"object-{int(raw_id)}"
        numeric_id = int(raw_id)
    else:
        s = str(raw_id).strip()
        if s.startswith("object-"):
            obj_id = s
            try:
                numeric_id = int(s.split("-", 1)[1].split("-")[-1])
            except (IndexError, ValueError):
                numeric_id = None
        else:
            try:
                numeric_id = int(s)
                obj_id = f"object-{numeric_id}"
            except ValueError:
                obj_id = s
                numeric_id = None

    name = api_obj.get("name") or api_obj.get("title") or ""

    creator = api_obj.get("creator") or {}
    creator_name = (
        creator.get("name") or creator.get("full_name") or creator.get("username")
        if isinstance(creator, dict) else ""
    )

    # Preview image: try all known API keys (full object has previewUrl; list may have images[] only)
    preview_url = (
        api_obj.get("previewUrl")
        or api_obj.get("preview_url")
        or api_obj.get("head_image")
        or api_obj.get("thumbnail")
        or api_obj.get("preview")
        or (api_obj.get("cover_image") or {}).get("url") if isinstance(api_obj.get("cover_image"), dict) else None
    )
    images_for_preview = _extract_images_list(api_obj)
    if not preview_url and images_for_preview:
        preview_url = images_for_preview[0].get("url") or images_for_preview[0].get("thumbnailUrl") or ""
    preview_url = (preview_url or "").strip()

    # Object URL path: full object may have url as slug "clint-gobswood-763934"; list may have "/object/3d-print-..."
    url_path = api_obj.get("url") or api_obj.get("slug") or ""
    if isinstance(url_path, str):
        url_path = url_path.strip()
    else:
        url_path = ""
    if url_path and not url_path.startswith("/"):
        url_path = "/object/3d-print-" + url_path.lstrip("/")
    if not url_path and numeric_id is not None:
        url_path = f"/object/3d-print-{numeric_id}"

    # Extra fields from full object API (for library view)
    description = api_obj.get("description") or ""
    if isinstance(description, str):
        description = description.strip()
    else:
        description = ""
    price_raw = api_obj.get("price")
    if price_raw is not None and price_raw != "":
        price = str(price_raw).strip()
    else:
        price = ""
    status = (api_obj.get("status") or "").strip() if isinstance(api_obj.get("status"), str) else ""
    has_pdf = bool(api_obj.get("hasPdf") or api_obj.get("has_pdf"))

    # Full image list for gallery (list of {url, thumbnailUrl})
    # API may use "images", "Images", or nested structure; items may be dicts or URL strings
    images = _extract_images_list(api_obj)

    return {
        "id": obj_id,
        "name": name,
        "creator": {"name": creator_name},
        "previewUrl": preview_url,
        "url": url_path,
        "description": description[:5000] if description else "",  # cap length
        "price": price[:50] if price else "",
        "status": status[:50] if status else "",
        "hasPdf": has_pdf,
        "images": images[:50] if images else [],  # cap for DB size
    }


def _current_user(headers: dict) -> str:
    """GET /user to see who is logged in; return username or empty string."""
    try:
        r = requests.get(f"{MMF_API_BASE}/user", headers=headers, timeout=10)
        if r.ok:
            data = r.json()
            return (data.get("username") or data.get("slug") or "").strip()
    except Exception:
        pass
    return ""


def _load_library_ids() -> list[int]:
    """Read library IDs from resolved IDs file (one numeric ID per line)."""
    ids: list[int] = []
    try:
        with open(_LIBRARY_IDS_FILE_RESOLVED, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                # Accept either plain numbers (763934) or "object-763934"
                if line.startswith("object-"):
                    line = line.split("object-", 1)[1]
                if not line.isdigit():
                    continue
                ids.append(int(line))
    except FileNotFoundError:
        return []
    return sorted(set(ids))


def fetch_library_by_ids(api_key: str, session_cookie: str = "") -> list:
    """Fetch library objects via /api/data-library/objects using IDs from LIBRARY_IDS_FILE."""
    ids = _load_library_ids()
    if not ids:
        print(f"No IDs found in {_LIBRARY_IDS_FILE_RESOLVED}. Add one numeric ID per line (e.g. 763934).")
        return []

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": f"{MMF_WEB_BASE}/library",
    }
    if session_cookie:
        headers["Cookie"] = session_cookie
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    all_items: list[dict] = []
    total_ids = len(ids)
    num_chunks = (total_ids + DATA_LIBRARY_CHUNK_SIZE - 1) // DATA_LIBRARY_CHUNK_SIZE
    print(f"Fetching library via /api/data-library/objects for {total_ids} IDs ({num_chunks} chunks of {DATA_LIBRARY_CHUNK_SIZE})...")
    if DATA_LIBRARY_DELAY > 0:
        print(f"   Rate limit: {DATA_LIBRARY_DELAY}s between requests (set MMF_LIBRARY_DELAY=0 to disable).")

    # Use curl_cffi with Chrome TLS when cookie auth: Cloudflare often blocks plain requests even with valid cookie
    use_curl_cffi = bool(session_cookie and CURL_CFFI_AVAILABLE)
    if use_curl_cffi:
        print("   Using curl_cffi (Chrome TLS) so Cloudflare accepts the session cookie.")
    http_session = CurlSession(impersonate="chrome") if use_curl_cffi else None

    for chunk_idx, start in enumerate(range(0, total_ids, DATA_LIBRARY_CHUNK_SIZE), 1):
        if chunk_idx > 1 and DATA_LIBRARY_DELAY > 0:
            time.sleep(DATA_LIBRARY_DELAY)
        chunk = ids[start : start + DATA_LIBRARY_CHUNK_SIZE]
        params = [("ids[]", str(i)) for i in chunk]
        url = f"{MMF_WEB_BASE}/api/data-library/objects"
        try:
            if http_session:
                r = http_session.get(url, params=params, headers=headers, timeout=60)
            else:
                r = requests.get(url, params=params, headers=headers, timeout=60)
            r.raise_for_status()
        except Exception as e:
            resp = getattr(e, "response", None)
            code = resp.status_code if resp is not None else None
            body = (getattr(resp, "text", None) or "")[:500] if resp else ""
            print(f"API request failed for chunk {chunk_idx}/{num_chunks} (index {start}): {e}")
            if body:
                print(f"   Response ({code or '?'}): {body[:200]}...")
            if code == 403 or (body and ("Just a moment" in body or "<!DOCTYPE" in body)):
                print("   403 / bot block: refresh MMF_SESSION_COOKIE from the browser (F12 → Network → copy Cookie header) while logged in.")
                if not CURL_CFFI_AVAILABLE:
                    print("   Then install curl_cffi so requests use Chrome TLS: pip install curl_cffi")
            return []

        data = r.json()
        if not isinstance(data, list):
            print(f"   Chunk {chunk_idx}/{num_chunks}: unexpected response (expected list), skipping.")
            continue

        for obj in data:
            if not isinstance(obj, dict):
                continue
            normalized = _normalize_object(obj)
            if normalized:
                all_items.append(normalized)

        # Progress: one short line per chunk; every 20 chunks print a running total
        if chunk_idx % 20 == 0 or chunk_idx == num_chunks:
            print(f"   [{chunk_idx}/{num_chunks}] {len(all_items)} objects so far")
        else:
            print(f"   [{chunk_idx}/{num_chunks}] OK", end="\r")

    if num_chunks % 20 != 0:
        print()  # newline after final \r
    if total_ids and len(all_items) < total_ids:
        print(f"   Note: {total_ids} IDs in file → {len(all_items)} objects returned (some IDs may be deleted or inaccessible).")

    # Optional: fetch full object for items missing previewUrl (GET /api/v2/objects/{id} has previewUrl/images)
    if MMF_ENRICH_PREVIEW and (MMF_API_KEY or MMF_SESSION_COOKIE):
        all_items = _enrich_previews(all_items, MMF_API_KEY, MMF_SESSION_COOKIE, use_curl_cffi)
    # Optional: fetch full object for all items with no images (for Digital Library gallery carousel)
    if MMF_ENRICH_IMAGES and (MMF_API_KEY or MMF_SESSION_COOKIE):
        all_items = _enrich_images(all_items, MMF_API_KEY, MMF_SESSION_COOKIE, use_curl_cffi)
    return all_items


def _numeric_id_from_obj_id(obj_id: str) -> int | None:
    """Extract numeric id from 'object-763934', 'object-clint-gobswood-763934', or '763934'."""
    if not obj_id:
        return None
    s = str(obj_id).strip()
    if s.startswith("object-"):
        s = s.split("object-", 1)[1]
    parts = s.split("-")
    try:
        return int(parts[-1])
    except (ValueError, IndexError):
        try:
            return int(s)
        except ValueError:
            return None


def _enrich_previews(
    all_items: list[dict], api_key: str, session_cookie: str, use_curl_cffi: bool
) -> list[dict]:
    """For each item with empty previewUrl, GET /api/v2/objects/{id} and merge previewUrl (and url) from full object."""
    to_enrich = [i for i in all_items if not (i.get("previewUrl") or "").strip()]
    if not to_enrich:
        return all_items
    n = len(to_enrich)
    print(f"   Enriching {n} objects missing preview (GET /api/v2/objects/{{id}})…")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": f"{MMF_WEB_BASE}/library",
    }
    if session_cookie:
        headers["Cookie"] = session_cookie
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    done = 0
    for idx, item in enumerate(to_enrich):
        num_id = _numeric_id_from_obj_id(item.get("id"))
        if num_id is None:
            continue
        url = f"{MMF_API_BASE}/objects/{num_id}"
        try:
            if use_curl_cffi:
                with CurlSession(impersonate="chrome") as s:
                    r = s.get(url, headers=headers, timeout=30)
            else:
                r = requests.get(url, headers=headers, timeout=30)
            if not r.ok:
                continue
            full = r.json()
            if not isinstance(full, dict):
                continue
            norm = _normalize_object(full)
            if norm and (norm.get("previewUrl") or "").strip():
                item["previewUrl"] = norm["previewUrl"]
                if (norm.get("url") or "").strip():
                    item["url"] = norm["url"]
                # Merge full image list for gallery (Digital Library carousel)
                if isinstance(norm.get("images"), list) and len(norm["images"]) > 0:
                    item["images"] = norm["images"]
        except Exception:
            continue
        done += 1
        if ENRICH_DELAY > 0:
            time.sleep(ENRICH_DELAY)
        if (idx + 1) % 50 == 0 or (idx + 1) == n:
            print(f"   Enriched {idx + 1}/{n} (preview filled for {done} so far)")
    print(f"   Enrichment done: {done} objects now have preview URLs.")
    return all_items


def _enrich_images(
    all_items: list[dict], api_key: str, session_cookie: str, use_curl_cffi: bool
) -> list[dict]:
    """For each item, GET /api/v2/objects/{id} and merge full image list (for Digital Library gallery).
    When MMF_ENRICH_IMAGES=1, enriches ALL items so every STL gets images_json. May take a long time (rate-limited)."""
    to_enrich = all_items  # enrich every item so all records get full image details
    if not to_enrich:
        return all_items
    n = len(to_enrich)
    print(f"   Enriching all {n} objects for image gallery (GET /api/v2/objects/{{id}})…")
    print(f"   This may take a while (rate limit: {ENRICH_DELAY}s per request). Use MMF_ENRICH_DELAY=0.2 to speed up.")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": f"{MMF_WEB_BASE}/library",
    }
    if session_cookie:
        headers["Cookie"] = session_cookie
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    done = 0
    for idx, item in enumerate(to_enrich):
        num_id = _numeric_id_from_obj_id(item.get("id"))
        if num_id is None:
            continue
        url = f"{MMF_API_BASE}/objects/{num_id}"
        try:
            if use_curl_cffi:
                with CurlSession(impersonate="chrome") as s:
                    r = s.get(url, headers=headers, timeout=30)
            else:
                r = requests.get(url, headers=headers, timeout=30)
            if not r.ok:
                continue
            full = r.json()
            if not isinstance(full, dict):
                continue
            if MMF_DEBUG_IMAGES and done == 0 and idx == 0:
                print(f"   [DEBUG] Full object keys: {list(full.keys())}")
                for k in ("images", "Images", "media", "gallery", "photos"):
                    if k in full:
                        v = full[k]
                        preview = str(v)[:200] + "..." if (isinstance(v, (list, dict)) and len(str(v)) > 200) else v
                        print(f"   [DEBUG] full[{k!r}] = {preview}")
            norm = _normalize_object(full)
            if norm:
                if isinstance(norm.get("images"), list) and len(norm["images"]) > 0:
                    item["images"] = norm["images"]
                    done += 1
                if (norm.get("previewUrl") or "").strip() and not (item.get("previewUrl") or "").strip():
                    item["previewUrl"] = norm["previewUrl"]
                if (norm.get("url") or "").strip():
                    item["url"] = norm["url"]
        except Exception:
            continue
        if ENRICH_DELAY > 0:
            time.sleep(ENRICH_DELAY)
        if (idx + 1) % 50 == 0 or (idx + 1) == n:
            print(f"   Image enrich {idx + 1}/{n} ({done} with images so far)")
    print(f"   Image enrichment done: {done} objects now have image lists.")
    return all_items


def fetch_user_objects(username: str, api_key: str, session_cookie: str = "") -> list:
    """Paginate GET /users/{username}/objects (objects you uploaded). Auth: api_key and/or session_cookie."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
    }
    if session_cookie:
        headers["Cookie"] = session_cookie
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
        headers["X-API-Key"] = api_key

    path = "objects"
    all_items = []
    page = 1
    while True:
        url = f"{MMF_API_BASE}/users/{username}/{path}"
        params = {"page": page, "per_page": PER_PAGE}
        if api_key:
            params["key"] = api_key
        try:
            r = requests.get(url, params=params, headers=headers, timeout=30)
            if page == 1:
                print(f"   Request: GET /users/{username}/{path} -> {r.status_code} {r.reason}")
            r.raise_for_status()
        except requests.RequestException as e:
            print(f"API request failed: {e}")
            if hasattr(e, "response") and e.response is not None:
                code = e.response.status_code
                try:
                    body = (e.response.text or "")[:400]
                    if body:
                        print(f"   Response ({code}): {body}")
                except Exception:
                    pass
                if code == 401:
                    print("   This endpoint requires authentication.")
                    print("   Option A (session cookie): Log in at myminifactory.com, F12 -> Network -> copy Cookie header.")
                    print("      Then: $env:MMF_SESSION_COOKIE = \"paste_cookie_here\"")
                    print("   Option B (OAuth): See docs/MMF-Fetcher-Setup.md and get_mmf_token.py.")
                    print("   Cookie method ref: https://gist.github.com/deliriyum/d353b9528e970e242b1915bb51da2a61")
            return []

        data = r.json()
        items = data.get("items") or data.get("objects") or []
        total_count = data.get("total_count", 0)

        if page == 1 and not items and total_count == 0:
            print(f"   API returned 0 objects (total_count=0) for user '{username}'.")
            if session_cookie:
                current = _current_user(headers)
                if current:
                    print(f"   Logged-in user (from cookie): {current}")
                    if current.lower() != username.lower():
                        print(f"   Username mismatch: you requested '{username}' but cookie is for '{current}'.")
                else:
                    print("   Could not get current user from API (cookie may be for a different session).")
            print("   If you expect items:")
            if path == "objects":
                print("     - The API may only return *published* objects; drafts/private might not appear.")
            else:
                print("     - Ensure MMF_USERNAME matches your account and the cookie is from that session.")

        for obj in items:
            normalized = _normalize_object(obj)
            if normalized:
                all_items.append(normalized)

        if len(items) < PER_PAGE or len(all_items) >= total_count:
            break
        page += 1

    return all_items


def main():
    username = (MMF_USERNAME or "").strip()
    if not username or username == "YOUR_MMF_USERNAME_HERE":
        print("Set your MyMiniFactory username:")
        print("  • Edit MMF_USERNAME at the top of this script (replace YOUR_MMF_USERNAME_HERE), or")
        print("  • Set environment variable: MMF_USERNAME=YourUsername")
        sys.exit(1)

    DATA_MMF.mkdir(parents=True, exist_ok=True)

    # So we always see whether the IDs file was found (repo path vs cwd fallback)
    print(f"Library IDs file: {_LIBRARY_IDS_FILE_RESOLVED.resolve()} (exists: {_LIBRARY_IDS_FILE_RESOLVED.exists()}, numeric lines: {_ids_file_count})")

    if not MMF_API_KEY and not MMF_SESSION_COOKIE:
        print("Set MMF_SESSION_COOKIE (browser cookie) or MMF_API_KEY (OAuth token). See script docstring.")
        sys.exit(1)

    if MMF_LIBRARY_SOURCE == "data_library":
        n_ids = _ids_file_count or len(_load_library_ids())
        print(f"Using source: data_library — {n_ids} IDs from {_LIBRARY_IDS_FILE_RESOLVED.resolve()}")
        objects = fetch_library_by_ids(MMF_API_KEY, MMF_SESSION_COOKIE)
    else:
        print(f"Using source: {MMF_LIBRARY_SOURCE} (set MMF_LIBRARY_SOURCE=data_library or add IDs to data/mmf/library_ids.txt for full library)")
        print(f"Fetching library for user: {username} (source: {MMF_LIBRARY_SOURCE})")
        objects = fetch_user_objects(username, MMF_API_KEY, MMF_SESSION_COOKIE)
    if not objects:
        print("No objects returned. Check username and auth (cookie or API key).")
        sys.exit(1)

    print(f"Fetched {len(objects)} objects.")

    # Write JSON in hydrator shape
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(objects, f, indent=2, ensure_ascii=False)

    # Sync check: hash of payload so orchestrator can skip hydrator when unchanged
    payload_bytes = json.dumps(objects, sort_keys=True, ensure_ascii=False).encode("utf-8")
    content_hash = hashlib.sha256(payload_bytes).hexdigest()
    last_sync = {
        "hash": content_hash,
        "at": datetime.now(timezone.utc).isoformat(),
        "count": len(objects),
        "username": username,
    }
    with open(LAST_SYNC_JSON, "w", encoding="utf-8") as f:
        json.dump(last_sync, f, indent=2)

    print(f"Wrote {OUTPUT_JSON}")
    print(f"   last_sync.json hash={content_hash[:16]}... (use this to skip hydrator when unchanged)")


if __name__ == "__main__":
    main()
