"""
Fetch OPR catalog from Army Forge armyInfo API and write data/opr/data.json
in the shape expected by newest_hydrator and OPR_JSON_analyzer. Also writes
data/opr/army_details.json (background, rules, spells) for hydrate_opr_army_detail.

Usage:
  python fetch_opr_json.py [--out path/to/data.json] [--army-details-out path/to/army_details.json]
  python fetch_opr_json.py --from-file path/to/battle_brothers_armyInfo.json --out data/opr/data.json

  --from-file: use when the live API returns non-JSON. Save the army-books API response
  from the browser (DevTools → Network → army-books/{id} → Copy response) to a .json file.

Requires: requests (pip install requests)
Army list: data/opr/army_forge_armies.json (array of { armyId, gameSystem, armyName }).
After running: run ProxyForge/newest_hydrator.py (units), scripts/opr/OPR_JSON_analyzer.py (upgrades),
scripts/opr/hydrate_opr_army_detail.py (army detail for Army Book view).
"""

import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlencode

try:
    import requests
except ImportError:
    print("pip install requests", file=sys.stderr)
    sys.exit(1)

BASE_URL = "https://army-forge.onepagerules.com/api/army-books"
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARMIES = REPO_ROOT / "data" / "opr" / "army_forge_armies.json"
DEFAULT_OUT = REPO_ROOT / "data" / "opr" / "data.json"
DEFAULT_ARMY_DETAILS_OUT = REPO_ROOT / "data" / "opr" / "army_details.json"


def _option_cost(opt):
    if "cost" in opt:
        return int(opt["cost"]) if opt["cost"] is not None else 0
    costs = opt.get("costs") or []
    if not costs:
        return 0
    return int(costs[0].get("cost", 0))


def build_upgrade_sets(unit, upgrade_packages):
    """Build upgradeSets[] from Army Forge upgradePackages for this unit."""
    unit_upgrade_uids = set(unit.get("upgrades") or [])
    upgrade_sets = []
    for pkg in upgrade_packages or []:
        if pkg.get("uid") not in unit_upgrade_uids:
            continue
        for sec in pkg.get("sections") or []:
            options = []
            for o in sec.get("options") or []:
                options.append({
                    "label": o.get("label") or "",
                    "cost": _option_cost(o),
                })
            if options:
                upgrade_sets.append({
                    "label": sec.get("label") or sec.get("uid") or pkg.get("hint") or "",
                    "options": options,
                })
    return upgrade_sets


def generic_name_to_group(generic_name):
    """Map genericName to Army Forge-style group (Heroes, Core, Special, Support, Vehicles & Monsters)."""
    if not generic_name or not isinstance(generic_name, str):
        return "Other"
    g = generic_name.strip().lower()
    if "hero" in g:
        return "Heroes"
    if "titan" in g or ("great" in g and "monster" in g):
        return "Vehicles & Monsters"
    if any(x in g for x in ("monster", "vehicle", "tank", "walker", "gunship", "speeder", "chariot", "drop pod", "artillery beast", "brute giant")):
        return "Vehicles & Monsters"
    if "artillery" in g or "support " in g or "altar" in g:
        return "Support"
    # Core: basic troops (exclude elite/heavy/assault/support/veteran/psychic/flying variants)
    non_core = ("elite", "heavy", "assault", "support", "veteran", "psychic", "flying", "shield", "brute")
    if any(x in g for x in ("light infantry", "scouts", "fanatics", "swarms")):
        if not any(x in g for x in non_core):
            return "Core"
    if g == "infantry" or g == "bikers":
        return "Core"
    if "infantry" in g or "bikers" in g:
        if not any(x in g for x in non_core):
            return "Core"
    return "Special"


def normalize_book(book):
    """Convert one armyInfo response to list of entries for our hydrator/analyzer."""
    army = book.get("name") or ""
    system = book.get("gameSystemSlug") or "grimdark-future"
    packages = book.get("upgradePackages") or []
    entries = []
    for u in book.get("units") or []:
        bases = u.get("bases") or {}
        generic = u.get("genericName") or ""
        entry = {
            "id": u.get("id"),
            "name": u.get("name"),
            "army": army,
            "cost": u.get("cost"),
            "quality": u.get("quality"),
            "defense": u.get("defense"),
            "wounds": 1,
            "size": u.get("size", 1),
            "system": system,
            "unitGroup": generic_name_to_group(generic),
            "unit": {
                "bases": bases,
                "genericName": generic,
                "product": book.get("coverImagePath") and {"imageUrl": book["coverImagePath"]} or {},
            },
            "upgradeSets": build_upgrade_sets(u, packages),
        }
        entries.append(entry)
    return entries


def extract_army_detail(book):
    """Build one army-detail record from a book response for opr_army_detail."""
    army_name = book.get("name") or ""
    game_system = book.get("gameSystemSlug") or "grimdark-future"
    background = book.get("backgroundFull") or book.get("background") or ""
    army_wide_rules = ""  # API has no separate army-wide list; leave for manual or future

    special_rules_lines = []
    aura_rules_lines = []
    for r in book.get("specialRules") or []:
        name = r.get("name") or ""
        desc = r.get("description") or ""
        line = f"**{name}**: {desc}" if name else desc
        if "Aura" in name:
            aura_rules_lines.append(line)
        else:
            special_rules_lines.append(line)
    special_rules = "\n\n".join(special_rules_lines) if special_rules_lines else ""
    aura_rules = "\n\n".join(aura_rules_lines) if aura_rules_lines else ""

    spell_lines = []
    for s in book.get("spells") or []:
        name = s.get("name") or ""
        thresh = s.get("threshold")
        effect = s.get("effect")
        if not isinstance(effect, str) and effect is not None:
            effect = str(effect)
        effect = effect or ""
        thresh_str = f" ({thresh})" if thresh is not None else ""
        spell_lines.append(f"**{name}{thresh_str}**: {effect}")
    spells = "\n\n".join(spell_lines) if spell_lines else ""

    return {
        "army_name": army_name,
        "game_system": game_system,
        "background": background.strip() or None,
        "army_wide_rules": army_wide_rules.strip() or None,
        "special_rules": special_rules.strip() or None,
        "aura_rules": aura_rules.strip() or None,
        "spells": spells.strip() or None,
    }


def fetch_army(army_id, game_system, army_name, session):
    """GET one army book from API and return parsed JSON."""
    params = {"gameSystem": game_system, "simpleMode": "false"}
    url = f"{BASE_URL}/{army_id}?{urlencode(params)}"
    r = session.get(url, timeout=30)
    r.raise_for_status()
    try:
        return r.json()
    except json.JSONDecodeError as e:
        ct = r.headers.get("Content-Type") or ""
        raise ValueError(f"Response is not valid JSON ({e}). Save armyInfo from browser and use --from-file.") from e


def main():
    ap = argparse.ArgumentParser(description="Fetch OPR data from Army Forge armyInfo")
    ap.add_argument("--armies", type=Path, default=DEFAULT_ARMIES, help="JSON array of { armyId, gameSystem, armyName }")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output data.json path")
    ap.add_argument("--army-details-out", type=Path, default=DEFAULT_ARMY_DETAILS_OUT, help="Output army_details.json for opr_army_detail hydrator")
    ap.add_argument("--from-file", type=Path, metavar="PATH", help="Use a single saved armyInfo JSON file instead of fetching (e.g. paste from browser)")
    args = ap.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    all_entries = []
    army_details = []

    if args.from_file:
        if not args.from_file.exists():
            print(f"File not found: {args.from_file}", file=sys.stderr)
            sys.exit(1)
        with open(args.from_file, "r", encoding="utf-8") as f:
            book = json.load(f)
        entries = normalize_book(book)
        all_entries.extend(entries)
        army_details.append(extract_army_detail(book))
        print(f"  From file: {len(entries)} units")
    else:
        if not args.armies.exists():
            print(f"Army list not found: {args.armies}", file=sys.stderr)
            print("Create it with at least one entry, or use --from-file with a saved armyInfo JSON.", file=sys.stderr)
            sys.exit(1)
        with open(args.armies, "r", encoding="utf-8") as f:
            armies = json.load(f)
        if not armies:
            print("No armies in list.", file=sys.stderr)
            sys.exit(1)
        session = requests.Session()
        session.headers.setdefault("Accept", "application/json")
        session.headers.setdefault("User-Agent", "Mozilla/5.0 (compatible; ProxyForge-OPR-Fetcher/1.0)")
        for i, a in enumerate(armies):
            army_id = a.get("armyId")
            game_system = a.get("gameSystem")
            army_name = a.get("armyName") or ""
            if not army_id or game_system is None:
                print(f"Skipping invalid entry at index {i}: {a}", file=sys.stderr)
                continue
            try:
                book = fetch_army(army_id, game_system, army_name, session)
                entries = normalize_book(book)
                all_entries.extend(entries)
                army_details.append(extract_army_detail(book))
                print(f"  {army_name}: {len(entries)} units")
            except Exception as e:
                print(f"  {army_name}: FAILED — {e}", file=sys.stderr)
                print("  Tip: Save the api/army-books response from your browser to a .json file and run with --from-file.", file=sys.stderr)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(all_entries, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(all_entries)} entries to {args.out}")

    if army_details:
        args.army_details_out.parent.mkdir(parents=True, exist_ok=True)
        with open(args.army_details_out, "w", encoding="utf-8") as f:
            json.dump(army_details, f, ensure_ascii=False, indent=2)
        print(f"Wrote {len(army_details)} army details to {args.army_details_out}")


if __name__ == "__main__":
    main()
