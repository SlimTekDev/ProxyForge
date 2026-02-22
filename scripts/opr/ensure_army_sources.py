#!/usr/bin/env python3
"""
Ensure every entry in army_forge_armies.json has a "source" field: "official" or "creator".

If data/opr/official_army_ids.txt exists (one armyId per line), it is the allowlist:
  source = "official" if armyId is in the file, else "creator".
This matches Army Forge "OPR Official" tab; build it with scripts/opr/build_official_army_ids.py.

If official_army_ids.txt does not exist but creator_army_ids.txt exists, those IDs are "creator"
and everyone else "official" (legacy behavior).
Run after adding new armies or after rebuilding official_army_ids.txt.
"""
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ARMIES_JSON = REPO_ROOT / "data" / "opr" / "army_forge_armies.json"
OFFICIAL_IDS_FILE = REPO_ROOT / "data" / "opr" / "official_army_ids.txt"
CREATOR_IDS_FILE = REPO_ROOT / "data" / "opr" / "creator_army_ids.txt"


def main():
    with open(ARMIES_JSON, "r", encoding="utf-8") as f:
        armies = json.load(f)

    official_ids = set()
    if OFFICIAL_IDS_FILE.exists():
        for line in OFFICIAL_IDS_FILE.read_text(encoding="utf-8").splitlines():
            aid = line.strip().split("#")[0].strip()
            if aid:
                official_ids.add(aid)

    creator_ids = set()
    if CREATOR_IDS_FILE.exists():
        for line in CREATOR_IDS_FILE.read_text(encoding="utf-8").splitlines():
            aid = line.strip().split("#")[0].strip()
            if aid:
                creator_ids.add(aid)

    use_official_allowlist = bool(official_ids)
    updated = 0
    for a in armies:
        aid = a.get("armyId")
        if use_official_allowlist:
            new_source = "official" if aid in official_ids else "creator"
        else:
            new_source = "creator" if aid in creator_ids else "official"
        if a.get("source") != new_source:
            a["source"] = new_source
            updated += 1
        elif "source" not in a:
            a["source"] = new_source
            updated += 1

    with open(ARMIES_JSON, "w", encoding="utf-8") as f:
        json.dump(armies, f, indent=2, ensure_ascii=False)

    print(f"Updated {ARMIES_JSON} ({updated} entries set/updated for source)")
    if use_official_allowlist:
        print(f"  official_army_ids.txt: {len(official_ids)} IDs -> source=official (allowlist)")
    else:
        print(f"  creator_army_ids.txt: {len(creator_ids)} IDs -> source=creator (legacy)")
    by_source = {}
    for a in armies:
        s = a.get("source", "official")
        by_source[s] = by_source.get(s, 0) + 1
    for s, n in sorted(by_source.items()):
        print(f"  {s}: {n}")


if __name__ == "__main__":
    main()
