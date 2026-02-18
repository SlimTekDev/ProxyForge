import json
import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_password_here",
    "database": "wargaming_erp"
}

# Ensure this path points to your FULL OPR export containing both systems
JSON_PATH = r"C:\Users\slimm\Desktop\WahapediaExport\OPR Data Export\data.json"

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
            defense = VALUES(defense)
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
