import json
import mysql.connector

# --- CONFIG ---
json_path = r"C:\Users\slimm\Desktop\WahapediaExport\OPR Data Export\data.json"
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "Warhammer40K!",
    "database": "wargaming_erp"
}

def deep_dive_opr_import():
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    entries = data if isinstance(data, list) else [data]
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # 1. Create the Relationship Tables if they don't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS opr_army_settings (
            army_name VARCHAR(100) PRIMARY KEY,
            setting_name VARCHAR(100)
        )
    """)
    
    # NEW Table for Upgrade Logic
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS opr_unit_upgrades (
            id INT AUTO_INCREMENT PRIMARY KEY,
            unit_id VARCHAR(50),
            section_label VARCHAR(255),
            option_label VARCHAR(255),
            cost INT
        )
    """)

    for entry in entries:
        army = entry.get('army')
        # Map 'grimdark-future' to 'Grimdark Future'
        raw_system = entry.get('system', 'Unknown')
        clean_system = raw_system.replace('-', ' ').title()
        
        # A. Populate Army-to-System Mapping
        cursor.execute("""
            INSERT IGNORE INTO opr_army_settings (army_name, setting_name) 
            VALUES (%s, %s)
        """, (army, clean_system))

        # B. Populate Unit Upgrades (Deep Dive)
        unit_id = entry.get('id')
        for section in entry.get('upgradeSets', []):
            section_label = section.get('label')
            for opt in section.get('options', []):
                cursor.execute("""
                    INSERT INTO opr_unit_upgrades (unit_id, section_label, option_label, cost)
                    VALUES (%s, %s, %s, %s)
                """, (unit_id, section_label, opt['label'], opt['cost']))

    conn.commit()
    conn.close()
    print(f"Deep dive complete. Mapped {len(entries)} units and their dependencies.")

if __name__ == "__main__":
    deep_dive_opr_import()
