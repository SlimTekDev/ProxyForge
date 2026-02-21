import json
import os
import mysql.connector
from pathlib import Path

# Use same DB as ProxyForge: load .env or ENV_FILE (e.g. .env.cloud) so hydrator and app use the same DB
_REPO_ROOT = Path(__file__).resolve().parents[2]
_env_file = os.environ.get("ENV_FILE")
if _env_file:
    _env_path = _REPO_ROOT / _env_file.lstrip(os.sep + "/\\")
else:
    _env_path = _REPO_ROOT / ".env"
if not _env_path.exists() and not _env_file:
    _env_cloud = _REPO_ROOT / ".env.cloud"
    if _env_cloud.exists():
        _env_path = _env_cloud
if _env_path.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env_path)
    except ImportError:
        pass

DB_CONFIG = {
    "host": os.environ.get("MYSQL_HOST") or "localhost",
    "user": os.environ.get("MYSQL_USER") or "root",
    "password": (os.environ.get("MYSQL_PASSWORD") or "").strip(),
    "database": os.environ.get("MYSQL_DATABASE") or "wargaming_erp",
}
_port = (os.environ.get("MYSQL_PORT") or "").strip()
if _port:
    DB_CONFIG["port"] = int(_port)

# Default: data/opr/data.json (same output as scripts/opr/fetch_opr_json.py)
JSON_PATH = _REPO_ROOT / "data" / "opr" / "data.json"

def dual_system_sync():
    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ JSON not found at {JSON_PATH}")
        return

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # INSERT logic that respects the new COMPOSITE KEY (ID + System)
    sql = """
        INSERT INTO opr_units (
            opr_unit_id, name, army, base_cost, quality, defense, wounds, 
            size, game_system, base_size_round, generic_name, image_url
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            base_cost = VALUES(base_cost),
            size = VALUES(size),
            quality = VALUES(quality),
            defense = VALUES(defense),
            game_system = VALUES(game_system)
    """

    print(f"🚀 Syncing {len(data)} units across all OPR systems...")
    
    count = 0
    for entry in data:
        u = entry.get('unit', {})
        # OPR uses 'system' slug (e.g., 'grimdark-future' or 'grimdark-future-firefight')
        sys_slug = entry.get('system', 'grimdark-future')
        
        val = (
            entry.get('id'),
            entry.get('name'),
            entry.get('army'),
            entry.get('cost'),
            entry.get('quality'),
            entry.get('defense'),
            entry.get('wounds', 1),
            entry.get('size', 1),
            sys_slug,
            u.get('bases', {}).get('round', 'N/A'),
            u.get('genericName', 'Unknown'),
            u.get('product', {}).get('imageUrl', '')
        )
        cursor.execute(sql, val)
        count += 1

    conn.commit()
    cursor.close()
    conn.close()
    print(f"🏁 DONE! Database now contains {count} unique system-unit entries.")

if __name__ == "__main__":
    dual_system_sync()
