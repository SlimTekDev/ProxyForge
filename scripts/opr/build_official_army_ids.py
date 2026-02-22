#!/usr/bin/env python3
"""
Build data/opr/official_army_ids.txt from army_forge_armies.json using a curated
set of army names that appear under "OPR Official" on Army Forge for
gameSystem 2, 3, 4, 5, 6.

Official = OPR Official tab at:
  https://army-forge.onepagerules.com/armyBookSelection?gameSystem=2 (GDF)
  https://army-forge.onepagerules.com/armyBookSelection?gameSystem=3 (Firefight)
  https://army-forge.onepagerules.com/armyBookSelection?gameSystem=4 (AoF)
  https://army-forge.onepagerules.com/armyBookSelection?gameSystem=5 (AoF Skirmish)
  https://army-forge.onepagerules.com/armyBookSelection?gameSystem=6 (AoF Regiments)

Includes all subfactions under: Prime Brothers, Battle Brothers, Wormhole Daemons,
Havoc Brothers, Havoc Warriors, Rift Daemons, plus Guilds of the Nexus and
Gangs of New Eden when present. Everything else is treated as Creator.

Usage: python scripts/opr/build_official_army_ids.py
"""
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ARMIES_JSON = REPO_ROOT / "data" / "opr" / "army_forge_armies.json"
OUTPUT_FILE = REPO_ROOT / "data" / "opr" / "official_army_ids.txt"

# Curated set of official OPR army names (OPR Official tab on Army Forge).
# Normalized: strip leading/trailing spaces; match case-insensitive in code.
OFFICIAL_ARMY_NAMES = frozenset({
    # Grimdark Future (2) / Firefight (3) core + subfactions
    "Battle Brothers",
    "Alien Hives",
    "Blessed Sisters",
    "Custodian Brothers",
    "DAO Union",
    "Dark Elf Raiders",
    "Dwarf Guilds",
    "Blood Brothers",
    "Dark Brothers",
    "Knight Brothers",
    "Watch Brothers",
    "Wolf Brothers",
    "Elven Jesters",
    "Havoc Brothers",
    "Eternal Dynasty",
    "Goblin Reclaimers",
    "Change Disciples",
    "Lust Disciples",
    "Plague Disciples",
    "War Disciples",
    "High Elf Fleets",
    "Human Defense Force",
    "Human Inquisition",
    "Infected Colonies",
    "Jackals",
    "Machine Cult",
    "Orc Marauders",
    "Prime Brothers",
    "Wormhole Daemons of Change",
    "Dark Prime Brothers",
    "Knight Prime Brothers",
    "Watch Prime Brothers",
    "Wolf Prime Brothers",
    "Ratmen Clans",
    "Rebel Guerrillas",
    "Robot Legions",
    "Saurian Starhost",
    "Soul-Snatcher Cults",
    "Titan Lords",
    "Wormhole Daemons of Lust",
    "Wormhole Daemons of Plague",
    "Wormhole Daemons of War",
    "Galaxy Guardians",
    "Legions of Carnage",
    "Blood Prime Brothers",
    # Age of Fantasy (4) / Skirmish (5) / Regiments (6) core
    "Wood Elves",
    "Volcanic Dwarves",
    "Vampiric Undead",
    "Sky City Dwarves",
    "Shadow Stalkers",
    "Saurians",
    "Rift Daemons of War",
    "Rift Daemons of Plague",
    "Rift Daemons of Lust",
    "Rift Daemons of Change",
    "Ratmen",
    "Ossified Undead",
    "Orcs",
    "Ogres",
    "Mummified Undead",
    "Kingdom of Angels",
    "Human Empire",
    "High Elves",
    "Havoc Warriors",
    "Havoc Dwarves",
    "Halflings",
    "Goblins",
    "Giant Tribes",
    "Ghostly Undead",
    "Eternal Wardens",
    "Dwarves",
    "Duchies of Vinci",
    "Dragon Empire",
    "Deep-Sea Elves",
    "Dark Elves",
    "Chivalrous Kingdoms",
    "Beastmen",
    # When added to Army Forge Official
    "Guilds of the Nexus",
    "Gangs of New Eden",
})


def main():
    with open(ARMIES_JSON, "r", encoding="utf-8") as f:
        armies = json.load(f)

    official_ids = set()
    name_to_id = {}
    for a in armies:
        name = (a.get("armyName") or "").strip()
        aid = a.get("armyId")
        if not aid:
            continue
        if name in OFFICIAL_ARMY_NAMES:
            official_ids.add(aid)
            name_to_id[name] = aid

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    lines = sorted(official_ids)
    OUTPUT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {OUTPUT_FILE}")
    print(f"  Official army IDs: {len(official_ids)}")
    print(f"  Official names matched: {len(name_to_id)}")
    missing = OFFICIAL_ARMY_NAMES - set(name_to_id.keys())
    if missing:
        print(f"  Names in allowlist not found in JSON (will be official when added): {len(missing)}")
        for n in sorted(missing):
            print(f"    - {n!r}")


if __name__ == "__main__":
    main()
