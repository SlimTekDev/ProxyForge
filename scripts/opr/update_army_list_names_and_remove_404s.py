#!/usr/bin/env python3
"""
Update army_forge_armies.json: (1) Replace "TBD" army names with real names from
the last fetch (army_details.json), (2) Remove the two 404 (armyId, gameSystem)
entries so they are not refetched.

Run after a full fetch so army_details.json order matches the unified list order.
Usage: python scripts/opr/update_army_list_names_and_remove_404s.py
"""
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ARMIES_JSON = REPO_ROOT / "data" / "opr" / "army_forge_armies.json"
ARMY_DETAILS_JSON = REPO_ROOT / "data" / "opr" / "army_details.json"

# (armyId, gameSystem) that 404'd - remove from list so we don't refetch
REMOVE_404 = {
    ("3j10zage1lddt6sr", 3),   # Titan Lords Firefight - no such book
    ("13UQcqEOM9ufwm2k", 3),  # TBD army Firefight - 404
}


def build_unified_order(armies: list) -> list:
    """Same order as build_unified_army_list (full order including 404s so indices match army_details)."""
    unified = list(armies)
    bp_id = "7ex2x15bpkmy1alv"
    if not any(a.get("armyId") == bp_id for a in unified):
        unified.append({"armyId": bp_id, "gameSystem": 2, "armyName": "Blood Prime Brothers"})
    gf_entries = [a for a in unified if a.get("gameSystem") == 2]
    for a in gf_entries:
        unified.append({
            "armyId": a["armyId"],
            "gameSystem": 3,
            "armyName": a["armyName"],
        })
    return unified


def main():
    with open(ARMIES_JSON, "r", encoding="utf-8") as f:
        armies = json.load(f)
    with open(ARMY_DETAILS_JSON, "r", encoding="utf-8") as f:
        details = json.load(f)

    # Build unified in same order as fetcher (before removing 404s), then drop 404s so indices match army_details
    unified = build_unified_order(armies)
    unified_success = [u for u in unified if (u.get("armyId"), u.get("gameSystem")) not in REMOVE_404]

    # Remove 404 entries from the list we keep
    armies_cleaned = [
        a for a in armies
        if (a.get("armyId"), a.get("gameSystem")) not in REMOVE_404
    ]
    removed_count = len(armies) - len(armies_cleaned)
    for (aid, gs) in REMOVE_404:
        if any(a.get("armyId") == aid and a.get("gameSystem") == gs for a in armies):
            print(f"Removed: armyId={aid!r}, gameSystem={gs}")

    if len(unified_success) != len(details):
        print(f"Warning: unified_success length {len(unified_success)} != army_details length {len(details)}. TBD mapping may be wrong.")
    else:
        mapping = {}
        for i in range(len(details)):
            key = (unified_success[i]["armyId"], unified_success[i]["gameSystem"])
            mapping[key] = details[i]["army_name"]

        updated = 0
        for a in armies_cleaned:
            key = (a.get("armyId"), a.get("gameSystem"))
            if a.get("armyName") == "TBD" and key in mapping:
                a["armyName"] = mapping[key]
                # Safe for Windows console (cp1252)
                disp = a["armyName"].encode("ascii", "replace").decode()
                print(f"  TBD -> {disp!r}  (armyId={a['armyId']!r}, gameSystem={a['gameSystem']})")
                updated += 1
        print(f"Updated {updated} TBD names to real army names.")

    with open(ARMIES_JSON, "w", encoding="utf-8") as f:
        json.dump(armies_cleaned, f, indent=2, ensure_ascii=False)
    print(f"Wrote {ARMIES_JSON}  (removed {removed_count} 404 entries, {len(armies_cleaned)} total).")


if __name__ == "__main__":
    main()
