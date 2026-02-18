import json
import mysql.connector
import os

# --- CONFIG ---
# Using raw string (r) to handle Windows backslashes in the path
json_file_path = r"C:\Users\slimm\Desktop\WahapediaExport\OPR Data Export\data.json"
db_password = "Warhammer40K!"

def import_opr_json(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle both single unit JSONs and lists of units
    entries = data if isinstance(data, list) else [data]
    
    try:
        conn = mysql.connector.connect(
            host="localhost", 
            user="root", 
            password=db_password, 
            database="wargaming_erp"
        )
        cursor = conn.cursor()

        for entry in entries:
            # Navigate to the 'unit' block for core stats
            u = entry.get('unit', {})
            if not u: continue 
            
            unit_id = u.get('id')
            unit_name = u.get('name')
            army_name = entry.get('army', 'Unknown')
            cost = u.get('cost', 0)
            quality = u.get('quality', 0)
            defense = u.get('defense', 0)
            wounds = u.get('wounds', 1)
            # Default to entry level wounds if unit level is missing
            if wounds == 1: wounds = entry.get('wounds', 1)
            
            img_url = u.get('product', {}).get('imageUrl', '')

            # 1. Update/Insert the Unit Stats
            sql_unit = """
                INSERT INTO opr_units (opr_unit_id, name, army, base_cost, quality, defense, wounds, image_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                name=VALUES(name), army=VALUES(army), base_cost=VALUES(base_cost),
                quality=VALUES(quality), defense=VALUES(defense), wounds=VALUES(wounds), image_url=VALUES(image_url)
            """
            cursor.execute(sql_unit, (unit_id, unit_name, army_name, cost, quality, defense, wounds, img_url))

            # 2. Insert Weapons
            for w in u.get('weapons', []):
                # Extract AP from weapon special rules if present
                ap_val = 0
                if 'specialRules' in w:
                    for r in w['specialRules']:
                        if r.get('name') == 'AP':
                            ap_val = r.get('rating', 0)
                
                rules_str = w.get('label', '') # Using the pre-formatted label for simplicity

                sql_wpn = """
                    INSERT INTO opr_unitweapons (unit_id, weapon_label, attacks, ap, special_rules, count)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE 
                    attacks=VALUES(attacks), ap=VALUES(ap), special_rules=VALUES(special_rules), count=VALUES(count)
                """
                cursor.execute(sql_wpn, (unit_id, w.get('name'), w.get('attacks', 0), ap_val, rules_str, w.get('count', 1)))

        conn.commit()
        print(f"Successfully processed {len(entries)} OPR records!")
        
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    import_opr_json(json_file_path)
