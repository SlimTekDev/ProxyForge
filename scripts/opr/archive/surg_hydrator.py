import json
import mysql.connector

# --- CONFIGURATION ---
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Warhammer40K!", # Update this!
    "database": "wargaming_erp"
}

JSON_PATH = r"C:\Users\slimm\Desktop\WahapediaExport\OPR Data Export\data.json"

def sync_missing_opr_details():
    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File not found at {JSON_PATH}")
        return

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Surgical Update Query
        sql = """
            UPDATE opr_units 
            SET size = %s, 
                game_system = %s, 
                base_size_round = %s, 
                generic_name = %s,
                image_url = %s
            WHERE opr_unit_id = %s
        """

        print(f"🔄 Starting sync for {len(data)} units...")
        
        count = 0
        for entry in data:
            u_data = entry.get('unit', {})
            
            # Prepare values from JSON
            unit_id = entry.get('id')
            size = entry.get('size', 1)
            system = entry.get('system', 'grimdark-future')
            base = u_data.get('bases', {}).get('round', 'N/A')
            g_name = u_data.get('genericName', 'Unknown')
            img = u_data.get('product', {}).get('imageUrl', '')

            cursor.execute(sql, (size, system, base, g_name, img, unit_id))
            
            if cursor.rowcount > 0:
                count += 1
                if count % 10 == 0:
                    print(f"✅ Updated {count} units...")

        conn.commit()
        print(f"🏁 Final: Successfully updated {count} units in the database.")

    except mysql.connector.Error as err:
        print(f"❌ MySQL Error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    sync_missing_opr_details()
