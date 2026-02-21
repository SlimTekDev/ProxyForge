"""
Hydrate opr_army_detail from data/opr/army_details.json (produced by fetch_opr_json.py).
Run after the OPR fetcher so Army Book view shows background, rules and spells.

Usage:
  python scripts/opr/hydrate_opr_army_detail.py
  python scripts/opr/hydrate_opr_army_detail.py --file path/to/army_details.json

Requires: opr_army_detail table (run ProxyForge/migrations/add_opr_army_detail.sql first).
Uses .env for DB (MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE).
"""
import argparse
import json
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
except ImportError:
    pass

import mysql.connector

_REPO = Path(__file__).resolve().parents[2]
DEFAULT_FILE = _REPO / "data" / "opr" / "army_details.json"
DB_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
    "user": os.environ.get("MYSQL_USER", "hobby_admin"),
    "password": os.environ.get("MYSQL_PASSWORD", ""),
    "database": os.environ.get("MYSQL_DATABASE", "wargaming_erp"),
}


def main():
    ap = argparse.ArgumentParser(description="Hydrate opr_army_detail from army_details.json")
    ap.add_argument("--file", type=Path, default=DEFAULT_FILE, help="Path to army_details.json")
    args = ap.parse_args()

    if not args.file.exists():
        print(f"File not found: {args.file}")
        print("Run the OPR fetcher first to generate data/opr/army_details.json")
        return 1

    with open(args.file, "r", encoding="utf-8") as f:
        details = json.load(f)
    if not isinstance(details, list):
        details = [details]

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        print(f"Connection failed: {err}")
        return 1

    cursor = conn.cursor()
    sql = """
        INSERT INTO opr_army_detail (army_name, game_system, background, army_wide_rules, special_rules, aura_rules, spells)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            background = VALUES(background),
            army_wide_rules = VALUES(army_wide_rules),
            special_rules = VALUES(special_rules),
            aura_rules = VALUES(aura_rules),
            spells = VALUES(spells)
    """
    count = 0
    for row in details:
        army_name = row.get("army_name") or ""
        game_system = row.get("game_system") or "grimdark-future"
        if not army_name:
            continue
        cursor.execute(sql, (
            army_name,
            game_system,
            row.get("background"),
            row.get("army_wide_rules"),
            row.get("special_rules"),
            row.get("aura_rules"),
            row.get("spells"),
        ))
        count += 1
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Upserted {count} army details into opr_army_detail.")
    return 0


if __name__ == "__main__":
    exit(main())
