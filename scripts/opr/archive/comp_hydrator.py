import json
import mysql.connector

# --- CONFIGURATION ---
DB_CONFIG = {
    "host": "127.0.0.1", # Using IP for better stability
    "user": "hobby_admin",
    "password": "Warhammer40K!",
    "database": "wargaming_erp"
}

JSON_PATH = r"C:\Users\slimm\Desktop\WahapediaExport\OPR Data Export\data.json"

def full_dual_system_sync():
    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File not found at {JSON_PATH}")
        return

    try:
        # Use the new hobby_admin user
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # The 'Surgical Hammer': Handle new Composite Primary Key (opr_unit_id, game_system)
        sql = """
            INSERT INTO opr_units (
                opr_unit_id, name, army, base_cost, quality, defense, wounds, 
                size, game_system, base_size_round, generic_name, image_url
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                name = VALUES(name),
                army = VALUES(army),
                base_cost = VALUES(base_cost),
                quality = VALUES(quality),
                defense = VALUES(defense),
                wounds = VALUES(wounds),
                size = VALUES(size),
                base_size_round = VALUES(base_size_round),
                generic_name = VALUES(generic_name),
                image_url = VALUES(image_url)
        """

        print(f"🚀 Starting Dual-System Sync for {len(data)} entries...")
        
        count = 0
        for entry in data:
            u_data = entry.get('unit', {})
            
            # Prepare values exactly as the SQL expects them (12 total)
            val = (
                entry.get('id'),
                entry.get('name'),
                entry.get('army'),
                entry.get('cost'),
                entry.get('quality'),
                entry.get('defense'),
                entry.get('wounds', 1),
                entry.get('size', 1),
                entry.get('system', 'grimdark-future'), # The second half of our Primary Key
                u_data.get('bases', {}).get('round', 'N/A'),
                u_data.get('genericName', 'Unknown'),
                u_data.get('product', {}).get('imageUrl', '')
            )

            cursor.execute(sql, val)
            count += 1
            if count % 500 == 0:
                print(f"✅ Processed {count} units...")

        conn.commit()
        print(f"🏁 Final: Successfully synchronized {count} unit entries.")

    except mysql.connector.Error as err:
        print(f"❌ MySQL Error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    full_dual_system_sync()
