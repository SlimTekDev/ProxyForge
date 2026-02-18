import argparse
import hashlib
import json
import sys
from pathlib import Path

import mysql.connector

DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "hobby_admin",
    "password": "Warhammer40K!",
    "database": "wargaming_erp"
}

# Default: data/mmf/mmf_download.json next to repo root (scripts/mmf -> repo root = parent.parent)
_BASE = Path(__file__).resolve().parent
_REPO_ROOT = _BASE.parent.parent
JSON_PATH = _REPO_ROOT / "data" / "mmf" / "mmf_download.json"
LAST_SYNC_PATH = _REPO_ROOT / "data" / "mmf" / "last_sync.json"


def hydrate_mmf_library(force=False):
    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ JSON not found: {JSON_PATH}")
        print("   Run fetch_mmf_library.py first to pull your MMF library.")
        return
    except Exception as e:
        print(f"❌ Error loading JSON: {e}")
        return

    # Optional sync check: skip DB write if content hash unchanged
    if not force and LAST_SYNC_PATH.exists():
        try:
            payload_bytes = json.dumps(data, sort_keys=True, ensure_ascii=False).encode("utf-8")
            current_hash = hashlib.sha256(payload_bytes).hexdigest()
            with open(LAST_SYNC_PATH, 'r', encoding='utf-8') as f:
                last = json.load(f)
            if last.get("hash") == current_hash:
                print("⏭️ MMF data unchanged (same hash); skipping DB update. Use --force to run anyway.")
                return
        except Exception:
            pass

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Optional extra columns (run migrations/add_stl_library_mmf_detail.sql if present)
    sql_base = """
        INSERT INTO stl_library (mmf_id, name, creator_name, preview_url, mmf_url)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            name = VALUES(name),
            preview_url = VALUES(preview_url)
    """
    sql_extended = """
        INSERT INTO stl_library (mmf_id, name, creator_name, preview_url, mmf_url, description, price, status, has_pdf)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            name = VALUES(name),
            preview_url = VALUES(preview_url),
            description = VALUES(description),
            price = VALUES(price),
            status = VALUES(status),
            has_pdf = VALUES(has_pdf)
    """

    print(f"🚀 Hydrating {len(data)} STL entries...")
    use_extended = False
    try:
        cursor.execute(
            "SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'stl_library' AND COLUMN_NAME = 'description' LIMIT 1"
        )
        use_extended = cursor.fetchone() is not None
        if use_extended:
            print("   Using extended columns (description, price, status, has_pdf).")
        else:
            print("   Using base columns only. Run migrations/add_stl_library_mmf_detail.sql then re-run to fill price/description.")
    except Exception as e:
        print(f"   Using base columns only ({e}). Run migrations/add_stl_library_mmf_detail.sql then re-run.")

    for obj in data:
        url_path = obj.get('url') or ''
        mmf_url = f"https://www.myminifactory.com{url_path}" if url_path.startswith('/') else url_path or None
        if use_extended:
            val = (
                obj.get('id'),
                obj.get('name'),
                (obj.get('creator') or {}).get('name'),
                obj.get('previewUrl'),
                mmf_url,
                (obj.get('description') or None),
                (obj.get('price') or None),
                (obj.get('status') or None),
                1 if obj.get('hasPdf') else 0,
            )
            cursor.execute(sql_extended, val)
        else:
            val = (
                obj.get('id'),
                obj.get('name'),
                (obj.get('creator') or {}).get('name'),
                obj.get('previewUrl'),
                mmf_url
            )
            cursor.execute(sql_base, val)

    conn.commit()
    conn.close()
    print(f"✅ Digital Library Hydrated!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync MMF library JSON into wargaming_erp.stl_library")
    parser.add_argument("--force", action="store_true", help="Run even if last_sync hash is unchanged")
    args = parser.parse_args()
    hydrate_mmf_library(force=args.force)