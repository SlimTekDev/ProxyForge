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

def process_nested_data(cursor, obj, unit_id):
    """Deep-dives into a unit to find and link rules and weapons."""
    
    # 1. FIND SPECIAL RULES (Try common keys: 'specialRules', 'rules', 'traits')
    rules_keys = ['specialRules', 'rules', 'traits']
    rules = []
    for k in rules_keys:
        if k in obj and isinstance(obj[k], list):
            rules = obj[k]
            break

    for r in rules:
        if isinstance(r, dict) and ('id' in r or 'name' in r):
            r_id = r.get('id', r.get('name')) # Fallback to name if ID missing
            r_name = r.get('name', 'Unknown Rule')
            
            # Clean rating (e.g., the '3' in Tough(3))
            rating = r.get('rating')
            try: rating = int(rating)
            except: rating = None

            # Insert Rule Definition
            cursor.execute("INSERT IGNORE INTO opr_SpecialRules (rule_id, name) VALUES (%s, %s)", (r_id, r_name))
            # Link to Unit
            cursor.execute("INSERT IGNORE INTO opr_UnitRules (unit_id, rule_id, rating, label) VALUES (%s, %s, %s, %s)",
                         (unit_id, r_id, rating, r_name))

    # 2. FIND WEAPONS (Try common keys: 'equipment', 'weapons', 'profiles')
    equip_keys = ['equipment', 'weapons', 'profiles']
    equipment = []
    for k in equip_keys:
        if k in obj and isinstance(obj[k], list):
            equipment = obj[k]
            break

    for e in equipment:
        # A weapon is usually defined by having 'attacks'
        if isinstance(e, dict) and 'attacks' in e:
            w_label = e.get('name', 'Weapon')
            
            # Extract sub-rules for the weapon (e.g., AP(1))
            w_rules_list = []
            for r_key in rules_keys:
                if r_key in e and isinstance(e[r_key], list):
                    w_rules_list = [sub_r.get('name', '') for sub_r in e[r_key] if isinstance(sub_r, dict)]
                    break
            
            w_rules_str = ", ".join(filter(None, w_rules_list))
            
            cursor.execute("""
                INSERT IGNORE INTO opr_UnitWeapons (unit_id, weapon_label, attacks, ap, special_rules, count)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (unit_id, w_label, e.get('attacks', 0), e.get('ap', 0), w_rules_str, e.get('count', 1)))

def crawl_for_nesting(cursor, obj, army_context="Grimdark Future"):
    """Recursive crawl looking for units, then processing their children."""
    count = 0
    if isinstance(obj, dict):
        # Update Army Name if found
        if 'name' in obj and ('units' in obj or 'armies' in obj):
            army_context = obj['name']

        # Is this a unit? (ID, Name, and Cost are the holy trinity of OPR units)
        if all(k in obj for k in ['id', 'name', 'cost']):
            unit_id = obj['id']
            # Re-verify unit exists and process children
            process_nested_data(cursor, obj, unit_id)
            count += 1
        
        for v in obj.values():
            count += crawl_for_nesting(cursor, v, army_context)
            
    elif isinstance(obj, list):
        for item in obj:
            count += crawl_for_nesting(cursor, item, army_context)
    return count

def main():
    try:
        print(f"--- 📂 Analyzing Nested Data in: {FILE_PATH} ---")
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            full_data = json.load(f)
        
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("--- 🧠 Linking Rules and Weapons... ---")
        total = crawl_for_nesting(cursor, full_data)
        
        conn.commit()
        print(f"\n--- 🏁 Success! Processed Nested Data for {total} units. ---")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    main()