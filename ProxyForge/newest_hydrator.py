import json
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

import mysql.connector

DB_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
    "user": os.environ.get("MYSQL_USER", "hobby_admin"),
    "password": os.environ.get("MYSQL_PASSWORD", ""),
    "database": os.environ.get("MYSQL_DATABASE", "wargaming_erp"),
}

# OPR export JSON: set OPR_DATA_JSON path or place data.json in repo data/opr/
_REPO = Path(__file__).resolve().parent.parent
JSON_PATH = os.environ.get("OPR_DATA_JSON") or str(_REPO / "data" / "opr" / "data.json")

def dual_system_sync():
    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ JSON not found at {JSON_PATH}")
        return

    try:
        # Connect using the new hobby_admin credentials
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        sql = """
            INSERT INTO opr_units (
                opr_unit_id, name, army, base_cost, quality, defense, wounds, 
                size, game_system, base_size_round, generic_name, image_url
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                name = VALUES(name),
                army = VALUES(army),
                base_cost = VALUES(base_cost),
                size = VALUES(size),
                quality = VALUES(quality),
                defense = VALUES(defense),
                wounds = VALUES(wounds),
                base_size_round = VALUES(base_size_round),
                generic_name = VALUES(generic_name),
                image_url = VALUES(image_url)
        """

        print(f"🚀 Syncing {len(data)} units...")
        
        count = 0
        for entry in data:
            u = entry.get('unit', {})
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
        print(f"🏁 DONE! Database now contains {count} entries.")

    except mysql.connector.Error as err:
        print(f"❌ Connection Failed: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    dual_system_sync()
