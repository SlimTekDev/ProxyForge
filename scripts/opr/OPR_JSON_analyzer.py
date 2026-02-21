import json
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
except ImportError:
    pass

import mysql.connector

# --- CONFIG: same as ProxyForge/newest_hydrator ---
_REPO = Path(__file__).resolve().parents[2]
JSON_PATH = os.environ.get("OPR_DATA_JSON") or str(_REPO / "data" / "opr" / "data.json")
DB_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
    "user": os.environ.get("MYSQL_USER", "hobby_admin"),
    "password": os.environ.get("MYSQL_PASSWORD", ""),
    "database": os.environ.get("MYSQL_DATABASE", "wargaming_erp"),
}

def deep_dive_opr_import():
    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"JSON not found at {JSON_PATH}")
        return

    entries = data if isinstance(data, list) else [data]
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        print(f"Connection failed: {err}")
        return

    try:
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
                    """, (unit_id, section_label, opt.get('label', ''), opt.get('cost') or 0))

        conn.commit()
        print(f"Deep dive complete. Mapped {len(entries)} units and their dependencies.")
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals():
            try:
                conn.close()
            except Exception:
                pass

if __name__ == "__main__":
    deep_dive_opr_import()
