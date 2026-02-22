#!/usr/bin/env python3
"""
Compare OPR army names: dropdown sources (opr_units/data.json + opr_army_settings + static)
vs canonical army books (army_forge_armies.json). Report mismatches for review/repair.
Run from repo root: python scripts/opr/compare_army_names.py
"""
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ARMY_FORGE = REPO / "data" / "opr" / "army_forge_armies.json"
DATA_JSON = REPO / "data" / "opr" / "data.json"

# Static list in app.py (Age of Fantasy variants)
STATIC_AOF = [
    "Beastmen", "Chivalrous Kingdoms", "Dark Elves", "Deep-Sea Elves", "Duchies of Vinci",
    "Dwarves", "Eternal Wardens", "Ghostly Undead", "Giant Tribes", "Goblins", "Halflings",
    "Havoc Dwarves", "Havoc War Clans", "Havoc Warriors", "High Elves", "Human Empire",
    "Kingdom of Angels", "Mummified Undead", "Ogres", "Orcs", "Ossified Undead", "Ratmen",
    "Rift Daemons", "Saurians", "Shadow Stalkers", "Sky-City Dwarves", "Vampiric Undead",
    "Volcanic Dwarves", "Wood Elves",
]

def main():
    # 1. Canonical army books (what we fetch)
    with open(ARMY_FORGE, encoding="utf-8") as f:
        armies = json.load(f)
    books = {a.get("armyName", "").strip() for a in armies if a.get("armyName")}

    # 2. Armies in data.json (opr_units after hydrate)
    with open(DATA_JSON, encoding="utf-8") as f:
        data = json.load(f)
    in_data = {e.get("army", "").strip() for e in data if e.get("army")}

    # 3. Armies from opr_army_settings dump (could appear in dropdown)
    dump_path = REPO / "MySQLDumps" / "wargaming_erp_opr_army_settings.sql"
    settings_armies = set()
    if dump_path.exists():
        text = dump_path.read_text(encoding="utf-8")
        # INSERT INTO ... VALUES ('Name','Setting'),...
        for m in re.finditer(r"\('([^']+)',\s*'[^']*'\)", text):
            settings_armies.add(m.group(1).strip())

    # 4. All names that can appear in dropdown = data ∪ settings ∪ static
    dropdown_all = in_data | settings_armies | set(STATIC_AOF)

    # --- Reports ---
    print("=" * 60)
    print("OPR army names: dropdown vs army books (army_forge_armies.json)")
    print("=" * 60)
    print(f"Canonical army books (army_forge_armies.json): {len(books)}")
    print(f"In data.json (opr_units): {len(in_data)}")
    print(f"In opr_army_settings (dump): {len(settings_armies)}")
    print(f"Static AoF list (app.py): {len(STATIC_AOF)}")
    print()

    # A. In dropdown (data/settings/static) but NOT in army books → typo / legacy / sub-faction
    not_in_books = dropdown_all - books
    if not_in_books:
        print("--- IN DROPDOWN BUT NOT IN ARMY BOOKS (review/repair) ---")
        print("These can appear in Primary Army but are not in army_forge_armies.json.")
        print("Either add to army_forge_armies.json (if they are real books) or fix/remove in DB or static list.")
        for name in sorted(not_in_books):
            src = []
            if name in in_data:
                src.append("data.json/opr_units")
            if name in settings_armies:
                src.append("opr_army_settings")
            if name in STATIC_AOF:
                src.append("static(app.py)")
            print(f"  {name!r}  [from: {', '.join(src)}]")
        print()
    else:
        print("--- No names in dropdown that are missing from army books. ---")
        print()

    # B. In army books but not in data.json → missing from fetch/hydrate
    not_in_data = books - in_data
    if not_in_data:
        print("--- IN ARMY BOOKS BUT NOT IN data.json ---")
        print("These are in army_forge_armies.json but have no units in data.json.")
        print("Possible cause: fetch failed for that army or army list is stale.")
        for name in sorted(not_in_data):
            print(f"  {name!r}")
        print()
    else:
        print("--- All army books have entries in data.json. ---")
        print()

    # C. Spelling / normalization: same when lower or when hyphens/spaces normalized
    def normalize(s):
        return s.lower().replace("-", " ").replace("  ", " ").strip()
    books_norm = {normalize(b): b for b in books}
    print("--- SPELLING / NORMALIZATION (dropdown vs book differs) ---")
    for name in sorted(not_in_books):
        norm = normalize(name)
        if norm in books_norm:
            print(f"  Dropdown: {name!r}  ->  Army book: {books_norm[norm]!r}")
    # In books but not in data: check if a normalized match exists in data
    for name in sorted(not_in_data):
        norm = normalize(name)
        match = next((d for d in in_data if normalize(d) == norm), None)
        if match:
            print(f"  Army book: {name!r}  ->  data.json has: {match!r} (normalize to match book?)")
    print()
    print("Done.")

if __name__ == "__main__":
    main()
