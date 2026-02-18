import json
import mysql.connector
from mysql.connector import Error

# --- CONFIGURATION ---
FILE_PATH = r"C:\Users\slimm\Desktop\WahapediaExport\OPR Data Export\data.json"

DB_CONFIG = {
    'user': 'root',
    'password': 'Warhammer40K!', 
    'host': 'localhost',
    'database': 'Wargaming_ERP'
}

def process_unit(cursor, unit, army_name):
    """Logic to insert a single unit and its children."""
    u_id = unit.get('id')
    u_name = unit.get('name')
    if not u_id or not u_name:
        return 0

    # Identify 'Hero' status
    u_rules = unit.get('specialRules', [])
    is_hero = any(r.get('name') == 'Hero' for r in u_rules)
    
    # 1. Insert Unit
    cursor.execute("""
        INSERT INTO opr_Units (opr_unit_id, name, army, base_cost, round_base_mm, is_hero)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE base_cost=VALUES(base_cost), name=VALUES(name), army=VALUES(army)
    """, (u_id, u_name, army_name, unit.get('cost', 0), unit.get('baseSize', 32), is_hero))

    # 2. Unit -> Rules Junction
    for rule in u_rules:
        raw_rating = rule.get('rating')
        try:
            rating = int(raw_rating) if raw_rating else None
        except:
            rating = None
        
        cursor.execute("""
            INSERT IGNORE INTO opr_UnitRules (unit_id, rule_id, rating, label)
            VALUES (%s, %s, %s, %s)
        """, (u_id, rule.get('id'), rating, rule.get('name')))

    # 3. Unit -> Weapons Junction
    for equip in unit.get('equipment', []):
        if 'attacks' in equip:
            w_rules = equip.get('specialRules', [])
            w_rules_str = ", ".join([r.get('name', '') for r in w_rules if r.get('name')])
            
            cursor.execute("""
                INSERT IGNORE INTO opr_UnitWeapons (unit_id, weapon_label, attacks, ap, special_rules, count)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (u_id, equip.get('name', 'Weapon'), equip.get('attacks', 0), 
                  equip.get('ap', 0), w_rules_str, equip.get('count', 1)))
    return 1

def find_and_import(cursor, data, current_army="Unknown"):
    """Recursively crawls the JSON to find 'units' arrays."""
    count = 0
    
    # If this block is an Army Book, update the name
    if isinstance(data, dict):
        if 'name' in data and 'units' in data:
            current_army = data['name']
            print(f"--- 📥 Processing Army: {current_army} ---")
        
        # If we find a units list, process them
        if 'units' in data and isinstance(data['units'], list):
            for u in data['units']:
                count += process_unit(cursor, u, current_army)
        
        # If we find global special rules, insert them
        if 'specialRules' in data and isinstance(data['specialRules'], list):
            for rule in data['specialRules']:
                if 'id' in rule and 'name' in rule:
                    cursor.execute("INSERT IGNORE INTO opr_SpecialRules (rule_id, name, description) VALUES (%s, %s, %s)", 
                                 (rule['id'], rule['name'], rule.get('description', '')))

        # Crawl deeper into any dictionaries or lists
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                count += find_and_import(cursor, value, current_army)
                
    elif isinstance(data, list):
        for item in data:
            count += find_and_import(cursor, item, current_army)
            
    return count

def main():
    try:
        print(f"--- 📂 Opening file: {FILE_PATH} ---")
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        total = find_and_import(cursor, raw_data)
        
        conn.commit()
        print(f"\n--- 🏁 Success! Total Units Imported: {total} ---")

    except Error as e:
        print(f"❌ Database Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    main()