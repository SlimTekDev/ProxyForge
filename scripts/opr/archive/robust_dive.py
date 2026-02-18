import json
import mysql.connector
import os

# --- CONFIG ---
json_path = r"C:\Users\slimm\Desktop\WahapediaExport\OPR Data Export\data.json"
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "Warhammer40K!",
    "database": "wargaming_erp"
}

def deep_dive_opr_import():
    if not os.path.exists(json_path):
        print(f"File not found: {json_path}")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    entries = data if isinstance(data, list) else [data]
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # 1. Create the Relationship Tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS opr_army_settings (
            army_name VARCHAR(100) PRIMARY KEY,
            setting_name VARCHAR(100)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS opr_unit_upgrades (
            id INT AUTO_INCREMENT PRIMARY KEY,
            unit_id VARCHAR(50),
            section_label VARCHAR(255),
            option_label VARCHAR(255),
            cost INT
        )
    """)
    
    # Clear old upgrades to prevent duplicates on re-run
    cursor.execute("TRUNCATE TABLE opr_unit_upgrades")

    print("Analyzing dependencies...")

    for entry in entries:
        army = entry.get('army')
        if not army: continue
        
        # Map 'grimdark-future' to 'Grimdark Future'
        raw_system = entry.get('system', 'Unknown')
        clean_system = raw_system.replace('-', ' ').title()
        
        # A. Populate Army-to-System Mapping
        cursor.execute("""
            INSERT IGNORE INTO opr_army_settings (army_name, setting_name) 
            VALUES (%s, %s)
        """, (army, clean_system))

        # B. Populate Unit Upgrades with Safety Checks
        unit_id = entry.get('id')
        upgrade_sets = entry.get('upgradeSets', [])
        
        if upgrade_sets:
            for section in upgrade_sets:
                # This check prevents the 'NoneType' error
                if section and isinstance(section, dict):
                    section_label = section.get('label', 'General Upgrade')
                    options = section.get('options', [])
                    if options:
                        for opt in options:
                            if opt and isinstance(opt, dict):
                                cursor.execute("""
                                    INSERT INTO opr_unit_upgrades (unit_id, section_label, option_label, cost)
                                    VALUES (%s, %s, %s, %s)
                                """, (unit_id, section_label, opt.get('label'), opt.get('cost', 0)))

    conn.commit()
    conn.close()
    print(f"Done! Mapped {len(entries)} units. Settings and Upgrades are now normalized.")

if __name__ == "__main__":
    deep_dive_opr_import()
