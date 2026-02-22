#!/usr/bin/env python3
"""
Build a single unified OPR army list (data/opr/army_forge_armies_unified.json) from
army_forge_armies.json plus Firefight: for each Grimdark Future (gameSystem 2) army,
add the same army with gameSystem 3 (Grimdark Future Firefight). gameSystem 4 = Age of
Fantasy, 5 = Age of Fantasy Skirmish, 6 = Age of Fantasy Regiments. Then you can run:
  python scripts/opr/fetch_opr_json.py --armies data/opr/army_forge_armies_unified.json
to fetch ALL units (GF + GFF + AoF) in one go.
"""
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ARMIES_IN = REPO_ROOT / "data" / "opr" / "army_forge_armies.json"
ARMIES_OUT = REPO_ROOT / "data" / "opr" / "army_forge_armies_unified.json"


def main():
    with open(ARMIES_IN, "r", encoding="utf-8") as f:
        armies = json.load(f)
    unified = list(armies)
    # Ensure Blood Prime Brothers is present (added via URL earlier; not in original list)
    bp_id = "7ex2x15bpkmy1alv"
    if not any(a.get("armyId") == bp_id for a in unified):
        unified.append({"armyId": bp_id, "gameSystem": 2, "armyName": "Blood Prime Brothers"})
    # Add Firefight (gameSystem 3) for every Grimdark Future (2) army (skip Titan Lords - no Firefight book, 404)
    gf_entries = [a for a in unified if a.get("gameSystem") == 2]
    for a in gf_entries:
        if a.get("armyId") == "3j10zage1lddt6sr":
            continue
        unified.append({
            "armyId": a["armyId"],
            "gameSystem": 3,
            "armyName": a["armyName"],
        })
    ARMIES_OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(ARMIES_OUT, "w", encoding="utf-8") as f:
        json.dump(unified, f, indent=2, ensure_ascii=False)
    by_sys = {}
    for a in unified:
        g = a.get("gameSystem")
        by_sys[g] = by_sys.get(g, 0) + 1
    print(f"Wrote {ARMIES_OUT}")
    print(f"  Total: {len(unified)} army entries")
    for g in sorted(by_sys.keys()):
        label = {
            2: "Grimdark Future",
            3: "Grimdark Future Firefight",
            4: "Age of Fantasy",
            5: "Age of Fantasy Skirmish",
            6: "Age of Fantasy Regiments",
        }.get(g, f"gameSystem {g}")
        print(f"  {label}: {by_sys[g]} armies")


if __name__ == "__main__":
    main()
