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

def insert_unit(cursor, obj, army_name):
    """Inserts an object if it meets the criteria of being a 'Unit'."""
    u_id = obj.get('id')
    u_name = obj.get('name')
    u_cost = obj.get('cost')
    
    # Validation: A unit must have an ID, Name, and a Cost value
    if not u_id or not u_name or u_cost is None:
        return 0

    # Determine Hero Status
    rules = obj.get('specialRules', [])
    is_hero = any(r.get('name') == 'Hero' for r in rules) if isinstance(rules, list) else False
    
    try:
        # 1. Insert Unit
        cursor.execute("""
            INSERT INTO opr_Units (opr_unit_id, name, army, base_cost, round_base_mm, is_hero)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE base_cost=VALUES(base_cost), name=VALUES(name)
        """, (u_id, u_name, army_name, u_cost, obj.get('baseSize', 32), is_hero))

        # 2. Insert Rules
        if isinstance(rules, list):
            for r in rules:
                if 'id' in r:
                    # Attempt to clean rating
                    rating = r.get('rating')
                    try: rating = int(rating)
                    except: rating = None
                    
                    cursor.execute("INSERT IGNORE INTO opr_SpecialRules (rule_id, name) VALUES (%s, %s)", 
                                 (r['id'], r.get('name', '')))
                    cursor.execute("INSERT IGNORE INTO opr_UnitRules (unit_id, rule_id, rating, label) VALUES (%s, %s, %s, %s)",
                                 (u_id, r['id'], rating, r.get('name')))

        # 3. Insert Weapons (Equipment)
        equip = obj.get('equipment', [])
        if isinstance(equip, list):
            for e in equip:
                if 'attacks' in e:
                    rules_str = ", ".join([r.get('name', '') for r in e.get('specialRules', [])]) if 'specialRules' in e else ""
                    cursor.execute("""
                        INSERT IGNORE INTO opr_UnitWeapons (unit_id, weapon_label, attacks, ap, special_rules, count)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (u_id, e.get('name', 'Weapon'), e.get('attacks', 0), e.get('ap', 0), rules_str, e.get('count', 1)))
        
        return 1
    except Exception as err:
        return 0

def crawl_everything(cursor, obj, army_context="Grimdark Future"):
    """Crawls every dictionary and list in the file looking for unit-like objects."""
    count = 0
    
    if isinstance(obj, dict):
        # If this dict looks like an Army Book, update the context
        if 'name' in obj and ('units' in obj or 'armies' in obj):
            army_context = obj['name']
            print(f"--- 📂 Entering Context: {army_context} ---")

        # Try to treat the current dictionary as a Unit
        count += insert_unit(cursor, obj, army_context)
        
        # Keep crawling all values
        for v in obj.values():
            count += crawl_everything(cursor, v, army_context)
            
    elif isinstance(obj, list):
        for item in obj:
            count += crawl_everything(cursor, item, army_context)
            
    return count

def main():
    try:
        print(f"--- 📂 Opening file: {FILE_PATH} ---")
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            full_data = json.load(f)
        
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("--- 🧠 Searching for units... ---")
        total_found = crawl_everything(cursor, full_data)
        
        conn.commit()
        print(f"\n--- 🏁 Success! Total Units Imported: {total_found} ---")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    main()