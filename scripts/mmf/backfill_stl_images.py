"""
Backfill stl_library.images_json from MMF API for all (or missing) records.
Updates the database directly; does not modify mmf_download.json.

Usage:
  Set MMF_API_KEY or MMF_SESSION_COOKIE (same as fetch_mmf_library.py).
  Then:
    python scripts/mmf/backfill_stl_images.py              # update all records
    python scripts/mmf/backfill_stl_images.py --skip-filled  # only rows with no/empty images_json
    python scripts/mmf/backfill_stl_images.py --limit 100    # test run (first 100)

Requires: images_json column (run ProxyForge/migrations/add_stl_library_images_json.sql first).
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

try:
    import mysql.connector
except ImportError:
    print("Install mysql-connector-python: pip install mysql-connector-python")
    sys.exit(1)
try:
    import requests
except ImportError:
    print("Install requests: pip install requests")
    sys.exit(1)

# Add parent so we can import from fetch_mmf_library
_BASE = Path(__file__).resolve().parent
if str(_BASE) not in sys.path:
    sys.path.insert(0, str(_BASE))

try:
    from dotenv import load_dotenv
    load_dotenv(_BASE.parent.parent / ".env")
except ImportError:
    pass

from fetch_mmf_library import (
    MMF_API_BASE,
    MMF_API_KEY,
    MMF_SESSION_COOKIE,
    ENRICH_DELAY,
    _extract_images_list,
    _numeric_id_from_obj_id,
)
try:
    from curl_cffi import Session as CurlSession
    CURL_CFFI_AVAILABLE = True
except ImportError:
    CurlSession = None
    CURL_CFFI_AVAILABLE = False

DB_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
    "user": os.environ.get("MYSQL_USER", "hobby_admin"),
    "password": os.environ.get("MYSQL_PASSWORD", ""),
    "database": os.environ.get("MYSQL_DATABASE", "wargaming_erp"),
}


def _get_full_object(numeric_id: int, headers: dict, use_curl_cffi: bool) -> dict | None:
    """GET /api/v2/objects/{id} and return JSON dict or None."""
    url = f"{MMF_API_BASE}/objects/{numeric_id}"
    try:
        if use_curl_cffi and CurlSession:
            with CurlSession(impersonate="chrome") as s:
                r = s.get(url, headers=headers, timeout=30)
        else:
            r = requests.get(url, headers=headers, timeout=30)
        if not r.ok:
            return None
        data = r.json()
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser(description="Backfill stl_library.images_json from MMF API")
    parser.add_argument("--skip-filled", action="store_true", help="Skip rows that already have non-empty images_json")
    parser.add_argument("--limit", type=int, default=0, help="Max number of rows to update (0 = all)")
    args = parser.parse_args()

    if not (MMF_API_KEY or MMF_SESSION_COOKIE):
        print("Set MMF_API_KEY or MMF_SESSION_COOKIE (same as fetch_mmf_library.py).")
        sys.exit(1)

    # If user pasted the cookie into MMF_API_KEY by mistake, use it as session cookie
    session_cookie = MMF_SESSION_COOKIE
    api_key = MMF_API_KEY
    if MMF_API_KEY and ("PHPSESSID" in MMF_API_KEY or "cf_clearance" in MMF_API_KEY or ("=" in MMF_API_KEY and ";" in MMF_API_KEY)):
        print("Note: MMF_API_KEY looks like a session cookie; using it as Cookie header (set MMF_SESSION_COOKIE next time).")
        session_cookie = MMF_API_KEY
        api_key = ""

    use_curl_cffi = bool(session_cookie and CURL_CFFI_AVAILABLE)
    if session_cookie and not CURL_CFFI_AVAILABLE:
        print("Warning: Using session cookie but curl_cffi not installed; requests may get 403.")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.myminifactory.com/library",
    }
    if session_cookie:
        headers["Cookie"] = session_cookie
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Check images_json column exists
    cursor.execute(
        "SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'stl_library' AND COLUMN_NAME = 'images_json' LIMIT 1"
    )
    if cursor.fetchone() is None:
        print("Column images_json not found. Run ProxyForge/migrations/add_stl_library_images_json.sql first.")
        conn.close()
        sys.exit(1)

    # Fetch mmf_ids to update
    if args.skip_filled:
        cursor.execute(
            "SELECT mmf_id FROM stl_library WHERE images_json IS NULL OR TRIM(COALESCE(images_json, '')) = '' OR TRIM(images_json) = '[]' ORDER BY mmf_id"
        )
    else:
        cursor.execute("SELECT mmf_id FROM stl_library ORDER BY mmf_id")
    rows = cursor.fetchall()
    mmf_ids = [r[0] for r in rows]
    if args.limit > 0:
        mmf_ids = mmf_ids[: args.limit]

    total = len(mmf_ids)
    if total == 0:
        print("No rows to update.")
        conn.close()
        return
    print(f"Updating images_json for {total} STL library records (rate limit: {ENRICH_DELAY}s per request).")

    updated = 0
    for i, mmf_id in enumerate(mmf_ids):
        num_id = _numeric_id_from_obj_id(str(mmf_id))
        if num_id is None:
            continue
        full = _get_full_object(num_id, headers, use_curl_cffi)
        if full is None:
            if (i + 1) % 100 == 0 or i == 0:
                print(f"   [{i + 1}/{total}] skipped (no response) mmf_id={mmf_id}")
            if ENRICH_DELAY > 0:
                time.sleep(ENRICH_DELAY)
            continue
        images = _extract_images_list(full)
        json_val = json.dumps(images)
        cursor.execute("UPDATE stl_library SET images_json = %s WHERE mmf_id = %s", (json_val, mmf_id))
        updated += 1
        if ENRICH_DELAY > 0:
            time.sleep(ENRICH_DELAY)
        if (i + 1) % 50 == 0 or (i + 1) == total:
            conn.commit()
            print(f"   [{i + 1}/{total}] updated {updated} so far")

    conn.commit()
    conn.close()
    print(f"Done. Updated images_json for {updated} records.")


if __name__ == "__main__":
    main()
