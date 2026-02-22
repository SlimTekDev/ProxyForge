#!/usr/bin/env python3
"""
Append army_forge_armies.json with any armies that are in the "unified" list
but not yet in the source file: Blood Prime Brothers (if missing) and a
Firefight (gameSystem 3) entry for each Grimdark Future (2) army, except Titan Lords.
Same logic as build_unified_army_list; this writes the additions into the source JSON.
"""
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ARMIES_JSON = REPO_ROOT / "data" / "opr" / "army_forge_armies.json"
TITAN_LORDS_ID = "3j10zage1lddt6sr"
BLOOD_PRIME_ID = "7ex2x15bpkmy1alv"


def main():
    with open(ARMIES_JSON, "r", encoding="utf-8") as f:
        armies = json.load(f)

    existing = {(a.get("armyId"), a.get("gameSystem")) for a in armies}
    added = []

    # Blood Prime Brothers (GDF) if missing
    if (BLOOD_PRIME_ID, 2) not in existing:
        armies.append({
            "armyId": BLOOD_PRIME_ID,
            "gameSystem": 2,
            "armyName": "Blood Prime Brothers",
        })
        existing.add((BLOOD_PRIME_ID, 2))
        added.append("Blood Prime Brothers (Grimdark Future)")

    # Firefight (3) for each GF (2) army, skip Titan Lords
    gf_entries = [a for a in armies if a.get("gameSystem") == 2]
    for a in gf_entries:
        aid = a.get("armyId")
        if aid == TITAN_LORDS_ID:
            continue
        if (aid, 3) not in existing:
            armies.append({
                "armyId": aid,
                "gameSystem": 3,
                "armyName": a["armyName"],
            })
            existing.add((aid, 3))
            added.append(f"{a['armyName']} (Firefight)")

    with open(ARMIES_JSON, "w", encoding="utf-8") as f:
        json.dump(armies, f, indent=2, ensure_ascii=False)

    print(f"Updated {ARMIES_JSON}")
    print(f"  Total entries: {len(armies)}")
    print(f"  Appended: {len(added)}")
    for name in added[:20]:
        print(f"    + {name}")
    if len(added) > 20:
        print(f"    ... and {len(added) - 20} more.")


if __name__ == "__main__":
    main()
