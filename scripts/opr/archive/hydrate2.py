import json
import mysql.connector

# --- 1. CONFIGURATION ---
DB_CONFIG = {
    "host": "localhost",
    "user": "root",        # Update if different
    "password": "Warhammer40K!", # Update with your password
    "database": "wargaming_erp"
}

JSON_PATH = r"C:\Users\slimm\Desktop\WahapediaExport\OPR Data Export\data.json"

def hydrate_opr_rules():
    # Load JSON
    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File not found at {JSON_PATH}")
        return

    glossary = {}

    # Recursive parser to find 'name' and 'description' pairs
    def extract(obj):
        if isinstance(obj, dict):
            if 'name' in obj and 'description' in obj:
                if obj['description'] and len(obj['description']) > 5:
                    glossary[obj['name']] = obj['description']
            for key in obj: extract(obj[key])
        elif isinstance(obj, list):
            for item in obj: extract(item)

    print("🔍 Searching for OPR rule definitions...")
    extract(data)

    # Connect to DB
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        sql = """
            INSERT INTO opr_specialrules (rule_id, name, description) 
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE description = VALUES(description)
        """

        count = 0
        for name, desc in glossary.items():
            rule_id = name.lower().replace(" ", "_")
            cursor.execute(sql, (rule_id, name, desc))
            count += 1

        conn.commit()
        print(f"✅ Success! Hydrated {count} unique OPR rules into your database.")
        
    except mysql.connector.Error as err:
        print(f"❌ Database Error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    hydrate_opr_rules()
