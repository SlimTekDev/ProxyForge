import json
import mysql.connector
from database_utils import get_db_connection

def sync_opr_rules_from_local():
    # 1. Your specific path
    json_path = r"C:\Users\slimm\Desktop\WahapediaExport\OPR Data Export\data.json"
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Could not find file at: {json_path}")
        return

    # 2. Extract every rule description found in the JSON
    # OPR data can be nested in many places; we'll check them all.
    glossary = {}

    def extract_rules(obj):
        """Recursively find rule definitions in the JSON."""
        if isinstance(obj, dict):
            # If we find a rule block with a name and a description
            if 'name' in obj and 'description' in obj:
                if obj['description'] and len(obj['description']) > 5:
                    glossary[obj['name']] = obj['description']
            
            # Check for common OPR keys
            for key in ['specialRules', 'rules', 'units', 'armies']:
                if key in obj:
                    extract_rules(obj[key])
        elif isinstance(obj, list):
            for item in obj:
                extract_rules(item)

    print("🔍 Parsing JSON for rule definitions...")
    extract_rules(data)

    # 3. Sync to Database
    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """
        INSERT INTO opr_specialrules (rule_id, name, description) 
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE description = VALUES(description)
    """

    count = 0
    for name, desc in glossary.items():
        # Create a unique ID from the name
        rule_id = name.lower().replace(" ", "_")
        cursor.execute(sql, (rule_id, name, desc))
        count += 1

    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ Success! Hydrated {count} unique OPR rules into your database.")

if __name__ == "__main__":
    sync_opr_rules_from_local()
