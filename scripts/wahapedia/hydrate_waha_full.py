"""
Full Wahapedia 40K CSV → waha_* pipeline. Loads all CSVs in dependency order.
See docs/Wahapedia-40K-Fetcher-Hydrator-Plan.md for mapping and robustness notes.

Recommended workflow: After fetching/exporting source CSVs, run a cleaner (e.g. CleanAll40K3.py)
so output goes to data/wahapedia/Cleaned_CSVs/; then run this hydrator. The hydrator prefers
Cleaned_CSVs when present, so you load cleaned (HTML-stripped, encoding-fixed) data.

Usage:
  python scripts/wahapedia/hydrate_waha_full.py
  python scripts/wahapedia/hydrate_waha_full.py --data-dir path/to/wahapedia --dry-run
  python scripts/wahapedia/hydrate_waha_full.py --tables factions,detachments,datasheets

Uses .env for DB (MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE).
"""
from __future__ import annotations

import argparse
import csv
import os
import re
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
except ImportError:
    pass

import mysql.connector

REPO = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = REPO / "data" / "wahapedia"
DB_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
    "user": os.environ.get("MYSQL_USER", "hobby_admin"),
    "password": os.environ.get("MYSQL_PASSWORD", ""),
    "database": os.environ.get("MYSQL_DATABASE", "wargaming_erp"),
}

PIPE = "|"
COMMA = ","
ENCODING = "utf-8"
ENCODING_SIG = "utf-8-sig"  # strip BOM so column "id" is recognized
ENCODING_ERRORS = "replace"
CLEANED_SUBDIR = "Cleaned_CSVs"

# Filenames that have a different name in Cleaned_CSVs (e.g. Datasheet_abilities vs Datasheets_abilities)
CLEANED_ALT_NAMES = {
    "Datasheets_abilities.csv": ["Datasheet_abilities.csv"],
}
# Core chain: same id scheme required (root has 000000001; cleaned may have 882). Never prefer cleaned for these.
# Datasheets_abilities: use root so datasheet_id matches waha_datasheets (same export); cleaned often has different column names or id scheme and can yield 0 link rows.
SKIP_CLEANED_FOR = {"Datasheets.csv", "Datasheets_models.csv", "Datasheets_models_cost.csv", "Datasheets_abilities.csv"}


def _cell(v):
    if v is None:
        return None
    s = (v.strip() if isinstance(v, str) else str(v)).strip()
    return s if s else None


def _strip_html(text: str | None) -> str | None:
    """Remove HTML tags and decode common entities for abilities/descriptions at intake."""
    if text is None:
        return None
    s = str(text).strip()
    if not s:
        return None
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"').replace("&#39;", "'").replace("&apos;", "'")
    s = " ".join(s.split())
    return s if s else None


def _int(v):
    if v is None:
        return None
    try:
        return int(v)
    except (ValueError, TypeError):
        return None


def _norm_id(v):
    """Normalize id/datasheet_id to 9-digit string so cleaned (882) matches DB (000000882)."""
    s = _cell(v)
    if not s:
        return s
    if str(s).strip().isdigit():
        return str(int(s)).zfill(9)
    return s


def _resolve_path(data_dir: Path, filename: str, cleaned_dir: Path | None = None) -> Path:
    """Prefer cleaned CSV (Cleaned_CSVs subdir) when present; otherwise use data_dir. Skip cleaned for core id-chain files."""
    if cleaned_dir is None:
        cleaned_dir = data_dir / CLEANED_SUBDIR
    if filename in SKIP_CLEANED_FOR:
        return data_dir / filename
    # Try cleaned with primary name, then cleaned with alternate name(s), then root
    candidates = [cleaned_dir / filename]
    candidates.extend(cleaned_dir / alt for alt in CLEANED_ALT_NAMES.get(filename, []))
    candidates.append(data_dir / filename)
    for p in candidates:
        if p.exists():
            return p
    return data_dir / filename


def _detect_delimiter(path: Path, encoding: str = ENCODING_SIG) -> str:
    """Use pipe if first line contains pipe, else comma (cleaned files often use comma)."""
    with open(path, "r", encoding=encoding, errors=ENCODING_ERRORS) as f:
        first = f.readline()
    return PIPE if PIPE in first else COMMA


def _normalize_row_keys(row: dict) -> dict:
    """Strip BOM from keys so '\\ufeffdatasheet_id' becomes 'datasheet_id' (cleaned CSVs)."""
    return {k.lstrip("\ufeff"): v for k, v in row.items()} if row else row


def read_csv(path: Path, delimiter: str | None = None, encoding: str = ENCODING_SIG) -> list[dict]:
    """Read CSV; use utf-8-sig for BOM. Delimiter auto-detected from first line if None. Keys normalized (BOM stripped)."""
    if not path.exists():
        return []
    if delimiter is None:
        delimiter = _detect_delimiter(path, encoding)
    rows = []
    with open(path, "r", encoding=encoding, errors=ENCODING_ERRORS) as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        for row in reader:
            rows.append(_normalize_row_keys(row))
    return rows


def run_factions(cursor, data_dir: Path, dry_run: bool, verbose: bool) -> int:
    path = _resolve_path(data_dir, "Factions.csv")
    rows = read_csv(path)
    if not rows:
        return 0
    sql = """
        INSERT INTO waha_factions (id, name, link)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE name = VALUES(name), link = VALUES(link)
    """
    n = 0
    for r in rows:
        id_ = _cell(r.get("id"))
        if not id_:
            continue
        name, link = _cell(r.get("name")), _cell(r.get("link"))
        if not dry_run:
            cursor.execute(sql, (id_, name, link))
            n += 1
        else:
            n += 1
    return n


def run_detachments(cursor, data_dir: Path, dry_run: bool, verbose: bool) -> int:
    path = _resolve_path(data_dir, "Detachments.csv")
    rows = read_csv(path)
    if not rows:
        return 0
    sql = """
        INSERT INTO waha_detachments (id, faction_id, name, legend, type)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE faction_id = VALUES(faction_id), name = VALUES(name), legend = VALUES(legend), type = VALUES(type)
    """
    n = 0
    for r in rows:
        id_ = _cell(r.get("id"))
        if not id_:
            continue
        faction_id, name = _cell(r.get("faction_id")), _cell(r.get("name"))
        legend, type_ = _cell(r.get("legend")), _cell(r.get("type"))
        if not dry_run:
            cursor.execute(sql, (id_, faction_id, name, legend, type_))
            n += 1
        else:
            n += 1
    return n


def run_datasheets(cursor, data_dir: Path, dry_run: bool, verbose: bool) -> int:
    path = _resolve_path(data_dir, "Datasheets.csv")
    rows = read_csv(path)
    if not rows:
        return 0
    sql = """
        INSERT INTO waha_datasheets (waha_datasheet_id, name, faction_id)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE name = VALUES(name), faction_id = VALUES(faction_id)
    """
    n = 0
    for r in rows:
        id_ = _norm_id(r.get("id"))
        if not id_:
            continue
        name, faction_id = _cell(r.get("name")), _cell(r.get("faction_id"))
        if not dry_run:
            cursor.execute(sql, (id_, name, faction_id))
            n += 1
        else:
            n += 1
    return n


def run_datasheets_points(cursor, data_dir: Path, dry_run: bool, verbose: bool) -> int:
    path = _resolve_path(data_dir, "Datasheets_models_cost.csv")
    rows = read_csv(path)
    if not rows:
        return 0
    seen = set()
    n = 0
    for r in rows:
        ds_id = _norm_id(r.get("datasheet_id"))
        line = _int(r.get("line") or r.get("Line"))
        if not ds_id or line != 1:
            continue
        if ds_id in seen:
            continue
        seen.add(ds_id)
        cost = _int(r.get("cost"))
        if cost is None:
            continue
        if not dry_run:
            cursor.execute("UPDATE waha_datasheets SET points_cost = %s WHERE waha_datasheet_id = %s", (cost, ds_id))
            if cursor.rowcount:
                n += 1
        else:
            n += 1
    return n


def run_datasheets_models(cursor, data_dir: Path, dry_run: bool, verbose: bool) -> int:
    path = _resolve_path(data_dir, "Datasheets_models.csv")
    rows = read_csv(path)
    if not rows:
        return 0
    if not dry_run:
        cursor.execute("DELETE FROM waha_datasheets_models")
    sql = """
        INSERT INTO waha_datasheets_models
        (datasheet_id, line_id, name, movement, toughness, save_value, inv_sv, inv_sv_descr, wounds, leadership, oc, base_size, base_size_descr)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    n = 0
    for r in rows:
        ds_id = _norm_id(r.get("datasheet_id"))
        line = _int(r.get("line"))
        if not ds_id:
            continue
        name = _cell(r.get("name"))
        movement = _cell(r.get("M"))
        toughness = _int(r.get("T"))
        save_value = _cell(r.get("Sv"))
        inv_sv = _cell(r.get("inv_sv"))
        inv_sv_descr = _cell(r.get("inv_sv_descr"))
        wounds = _int(r.get("W"))
        leadership = _cell(r.get("Ld"))
        oc = _int(r.get("OC"))
        base_size = _cell(r.get("base_size"))
        base_size_descr = _cell(r.get("base_size_descr"))
        if not dry_run:
            cursor.execute(sql, (
                ds_id, line or 1, name, movement, toughness, save_value, inv_sv, inv_sv_descr,
                wounds, leadership, oc, base_size, base_size_descr
            ))
            n += 1
        else:
            n += 1
    return n


def run_datasheet_unit_composition(cursor, data_dir: Path, dry_run: bool, verbose: bool) -> int:
    path = _resolve_path(data_dir, "Datasheets_unit_composition.csv")
    rows = read_csv(path)
    if not rows:
        return 0
    if not dry_run:
        cursor.execute("DELETE FROM waha_datasheet_unit_composition")
    sql = "INSERT INTO waha_datasheet_unit_composition (datasheet_id, line_id, description) VALUES (%s, %s, %s)"
    n = 0
    for r in rows:
        ds_id = _norm_id(r.get("datasheet_id"))
        line = _int(r.get("line"))
        desc = _cell(r.get("description"))
        if not ds_id:
            continue
        if not dry_run:
            cursor.execute(sql, (ds_id, line or 1, desc))
            n += 1
        else:
            n += 1
    return n


def run_datasheets_keywords(cursor, data_dir: Path, dry_run: bool, verbose: bool) -> int:
    path = _resolve_path(data_dir, "Datasheets_keywords.csv")
    rows = read_csv(path)
    if not rows:
        return 0
    if not dry_run:
        cursor.execute("DELETE FROM waha_datasheets_keywords")
    sql = "INSERT INTO waha_datasheets_keywords (datasheet_id, keyword, model, is_faction_keyword) VALUES (%s, %s, %s, %s)"
    n = 0
    for r in rows:
        ds_id = _norm_id(r.get("datasheet_id"))
        keyword = _cell(r.get("keyword"))
        model = _cell(r.get("model"))
        is_fk = r.get("is_faction_keyword", "")
        is_faction = 1 if str(is_fk).strip().lower() in ("true", "1", "yes") else 0
        if not ds_id or not keyword:
            continue
        if not dry_run:
            cursor.execute(sql, (ds_id, keyword, model, is_faction))
            n += 1
        else:
            n += 1
    return n


def run_abilities_from_datasheets_abilities(cursor, data_dir: Path, dry_run: bool, verbose: bool) -> int:
    path = _resolve_path(data_dir, "Datasheets_abilities.csv")
    rows = read_csv(path)
    seen = {}
    for r in rows:
        aid = _cell(r.get("ability_id"))
        if aid and str(aid).strip().replace(".0", "").isdigit():
            aid = str(int(float(aid))).zfill(9) if "." in str(aid) else str(int(aid)).zfill(9)
        if not aid:
            continue
        name = _strip_html(_cell(r.get("name"))) or _cell(r.get("name"))
        desc = _strip_html(_cell(r.get("description"))) or _cell(r.get("description"))
        if aid not in seen or (name or desc):
            seen[aid] = (name, desc)
    if not seen:
        return 0
    if not dry_run:
        cursor.execute("DELETE FROM waha_abilities")
    sql = "INSERT INTO waha_abilities (id, name, description) VALUES (%s, %s, %s)"
    n = 0
    for aid, (name, desc) in seen.items():
        if not dry_run:
            cursor.execute(sql, (aid, name, desc))
            n += 1
        else:
            n += 1
    return n


def run_datasheets_abilities(cursor, data_dir: Path, dry_run: bool, verbose: bool) -> int:
    path = _resolve_path(data_dir, "Datasheets_abilities.csv")
    rows = read_csv(path)
    if not rows and CLEANED_SUBDIR in str(path):
        rows = read_csv(data_dir / "Datasheets_abilities.csv")
    if not rows:
        return 0
    # Prefer datasheet_id; fallback for alternate CSV column names (e.g. "datasheet", "id")
    def _ds_id(r):
        return _norm_id(r.get("datasheet_id") or r.get("datasheet") or r.get("id"))
    if not dry_run:
        cursor.execute("DELETE FROM waha_datasheets_abilities")
    sql = """
        INSERT INTO waha_datasheets_abilities (datasheet_id, line_id, ability_id, model_name, name, description, type)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    n = 0
    for r in rows:
        ds_id = _ds_id(r)
        line = _int(r.get("line"))
        ability_id = _cell(r.get("ability_id"))
        if ability_id and str(ability_id).replace(".0", "").strip().isdigit():
            try:
                ability_id = str(int(float(ability_id))).zfill(9)
            except (ValueError, TypeError):
                pass
        model = _cell(r.get("model"))
        name = _strip_html(_cell(r.get("name"))) or _cell(r.get("name"))
        desc = _strip_html(_cell(r.get("description"))) or _cell(r.get("description"))
        type_ = _cell(r.get("type"))
        if not ds_id:
            continue
        if not dry_run:
            cursor.execute(sql, (ds_id, line or 1, ability_id, model, name, desc, type_))
            n += 1
        else:
            n += 1
    if n == 0 and rows and (verbose or not dry_run):
        first = rows[0]
        keys = list(first.keys())[:8]
        print(f"    [datasheets_abilities] 0 rows inserted; path={path}; first row keys: {keys}; ds_id from first row: {_ds_id(first)!r}")
    return n


def run_datasheets_wargear(cursor, data_dir: Path, dry_run: bool, verbose: bool) -> int:
    path = _resolve_path(data_dir, "Datasheets_wargear.csv")
    rows = read_csv(path)
    if not rows:
        return 0
    if not dry_run:
        cursor.execute("DELETE FROM waha_datasheets_wargear")
    sql = """
        INSERT INTO waha_datasheets_wargear
        (datasheet_id, line_id, line_in_wargear, dice, name, description, range_val, type, attacks, bs_ws, strength, ap, damage)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    n = 0
    for r in rows:
        ds_id = _norm_id(r.get("datasheet_id"))
        line = _int(r.get("line"))
        line_in_w = _int(r.get("line_in_wargear"))
        dice = _cell(r.get("dice"))
        name = _cell(r.get("name"))
        desc = _cell(r.get("description"))
        range_val = _cell(r.get("range"))
        type_ = _cell(r.get("type"))
        attacks = _cell(r.get("A"))
        bs_ws = _cell(r.get("BS_WS"))
        strength = _cell(r.get("S"))
        ap = _cell(r.get("AP"))
        damage = _cell(r.get("D"))
        if not ds_id:
            continue
        if not dry_run:
            cursor.execute(sql, (
                ds_id, line or 1, line_in_w or 1, dice, name, desc, range_val, type_,
                attacks, bs_ws, strength, ap, damage
            ))
            n += 1
        else:
            n += 1
    return n


def run_datasheets_options(cursor, data_dir: Path, dry_run: bool, verbose: bool) -> int:
    path = _resolve_path(data_dir, "Datasheets_options.csv")
    rows = read_csv(path)
    if not rows:
        return 0
    if not dry_run:
        cursor.execute("DELETE FROM waha_datasheets_options")
    sql = "INSERT INTO waha_datasheets_options (datasheet_id, line_id, button_text, description) VALUES (%s, %s, %s, %s)"
    n = 0
    for r in rows:
        ds_id = _norm_id(r.get("datasheet_id"))
        line = _int(r.get("line"))
        button = _cell(r.get("button"))
        desc = _cell(r.get("description"))
        if not ds_id:
            continue
        if not dry_run:
            cursor.execute(sql, (ds_id, line or 1, button, desc))
            n += 1
        else:
            n += 1
    return n


def run_datasheets_leader(cursor, data_dir: Path, dry_run: bool, verbose: bool) -> int:
    path = _resolve_path(data_dir, "Datasheets_leader.csv")
    rows = read_csv(path)
    if not rows:
        return 0
    if not dry_run:
        cursor.execute("DELETE FROM waha_datasheets_leader")
    sql = "INSERT INTO waha_datasheets_leader (leader_id, attached_id) VALUES (%s, %s)"
    n = 0
    for r in rows:
        leader_id = _norm_id(r.get("leader_id"))
        attached_id = _norm_id(r.get("attached_id"))
        if not leader_id or not attached_id:
            continue
        if not dry_run:
            cursor.execute(sql, (leader_id, attached_id))
            n += 1
        else:
            n += 1
    return n


def run_stratagems(cursor, data_dir: Path, dry_run: bool, verbose: bool) -> int:
    path = _resolve_path(data_dir, "Stratagems.csv")
    rows = read_csv(path)
    if not rows:
        return 0
    sql = """
        INSERT INTO waha_stratagems (id, faction_id, name, type, cp_cost, legend, turn, phase, detachment, detachment_id, description)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE faction_id=VALUES(faction_id), name=VALUES(name), type=VALUES(type), cp_cost=VALUES(cp_cost),
        legend=VALUES(legend), turn=VALUES(turn), phase=VALUES(phase), detachment=VALUES(detachment), detachment_id=VALUES(detachment_id), description=VALUES(description)
    """
    n = 0
    for r in rows:
        id_ = _cell(r.get("id"))
        if not id_:
            continue
        faction_id = _cell(r.get("faction_id"))
        name = _cell(r.get("name"))
        type_ = _cell(r.get("type"))
        cp_cost = _int(r.get("cp_cost"))
        legend = _cell(r.get("legend"))
        turn = _cell(r.get("turn"))
        phase = _cell(r.get("phase"))
        detachment = _cell(r.get("detachment"))
        detachment_id = _cell(r.get("detachment_id"))
        desc = _cell(r.get("description"))
        if not dry_run:
            cursor.execute(sql, (id_, faction_id, name, type_, cp_cost, legend, turn, phase, detachment, detachment_id, desc))
            n += 1
        else:
            n += 1
    return n


def run_enhancements(cursor, data_dir: Path, dry_run: bool, verbose: bool) -> int:
    path = _resolve_path(data_dir, "Enhancements.csv")
    rows = read_csv(path)
    if not rows:
        return 0
    sql = """
        INSERT INTO waha_enhancements (id, faction_id, name, cost, detachment, detachment_id, legend, description)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE faction_id=VALUES(faction_id), name=VALUES(name), cost=VALUES(cost), detachment=VALUES(detachment),
        detachment_id=VALUES(detachment_id), legend=VALUES(legend), description=VALUES(description)
    """
    n = 0
    for r in rows:
        id_ = _cell(r.get("id"))
        if not id_:
            continue
        faction_id = _cell(r.get("faction_id"))
        name = _cell(r.get("name"))
        cost = _int(r.get("cost"))
        detachment = _cell(r.get("detachment"))
        detachment_id = _cell(r.get("detachment_id"))
        legend = _cell(r.get("legend"))
        desc = _cell(r.get("description"))
        if not dry_run:
            cursor.execute(sql, (id_, faction_id, name, cost, detachment, detachment_id, legend, desc))
            n += 1
        else:
            n += 1
    return n


def run_datasheets_stratagems(cursor, data_dir: Path, dry_run: bool, verbose: bool) -> int:
    path = _resolve_path(data_dir, "Datasheets_stratagems.csv")
    rows = read_csv(path)
    if not rows:
        return 0
    if not dry_run:
        cursor.execute("DELETE FROM waha_datasheets_stratagems")
    sql = "INSERT INTO waha_datasheets_stratagems (datasheet_id, stratagem_id) VALUES (%s, %s)"
    n = 0
    for r in rows:
        ds_id = _norm_id(r.get("datasheet_id"))
        strat_id = _cell(r.get("stratagem_id"))
        if not ds_id or not strat_id:
            continue
        if not dry_run:
            cursor.execute(sql, (ds_id, strat_id))
            n += 1
        else:
            n += 1
    return n


def run_abilities_csv_merge(cursor, data_dir: Path, dry_run: bool, verbose: bool) -> int:
    """Merge names/descriptions from Abilities.csv into waha_abilities (fixes e.g. FACTION 'Unnamed Ability' -> 'Waaagh!'). Run after abilities + datasheets_abilities."""
    path = data_dir / "Abilities.csv"
    if not path.exists():
        return 0
    rows = read_csv(path)
    if not rows:
        return 0
    # Abilities.csv: id, name, legend, faction_id, description
    n = 0
    for r in rows:
        aid = _cell(r.get("id"))
        if aid and str(aid).replace(".0", "").strip().isdigit():
            try:
                aid = str(int(float(aid))).zfill(9) if "." in str(aid) else str(int(aid)).zfill(9)
            except (ValueError, TypeError):
                pass
        if not aid:
            continue
        name = _cell(r.get("name"))
        desc = _cell(r.get("description"))
        if not dry_run:
            cursor.execute(
                "UPDATE waha_abilities SET name = COALESCE(NULLIF(TRIM(%s), ''), name), description = COALESCE(NULLIF(TRIM(%s), ''), description) WHERE id = %s",
                (name or "", desc or "", aid),
            )
            if cursor.rowcount:
                n += 1
        else:
            n += 1
    return n


def run_datasheets_detachment_abilities(cursor, data_dir: Path, dry_run: bool, verbose: bool) -> int:
    path = _resolve_path(data_dir, "Datasheets_detachment_abilities.csv")
    rows = read_csv(path)
    if not rows:
        return 0
    if not dry_run:
        cursor.execute("DELETE FROM waha_datasheets_detachment_abilities")
    sql = "INSERT INTO waha_datasheets_detachment_abilities (datasheet_id, detachment_ability_id) VALUES (%s, %s)"
    n = 0
    for r in rows:
        ds_id = _norm_id(r.get("datasheet_id"))
        da_id = _cell(r.get("detachment_ability_id"))
        if not ds_id or not da_id:
            continue
        if not dry_run:
            cursor.execute(sql, (ds_id, da_id))
            n += 1
        else:
            n += 1
    return n


STEPS = [
    ("factions", run_factions),
    ("detachments", run_detachments),
    ("datasheets", run_datasheets),
    ("datasheets_points", run_datasheets_points),
    ("datasheets_models", run_datasheets_models),
    ("datasheet_unit_composition", run_datasheet_unit_composition),
    ("datasheets_keywords", run_datasheets_keywords),
    ("abilities", run_abilities_from_datasheets_abilities),
    ("datasheets_abilities", run_datasheets_abilities),
    ("abilities_csv_merge", run_abilities_csv_merge),
    ("datasheets_wargear", run_datasheets_wargear),
    ("datasheets_options", run_datasheets_options),
    ("datasheets_leader", run_datasheets_leader),
    ("stratagems", run_stratagems),
    ("enhancements", run_enhancements),
    ("datasheets_stratagems", run_datasheets_stratagems),
    ("datasheets_detachment_abilities", run_datasheets_detachment_abilities),
]


def main():
    ap = argparse.ArgumentParser(description="Full Wahapedia 40K CSV → waha_* hydration")
    ap.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR, help="Directory containing Wahapedia CSVs")
    ap.add_argument("--dry-run", action="store_true", help="Do not write to DB")
    ap.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    ap.add_argument("--tables", type=str, default="", help="Comma-separated step names to run (default: all)")
    args = ap.parse_args()

    data_dir = args.data_dir.resolve()
    if not data_dir.is_dir():
        cwd_dir = Path.cwd() / "data" / "wahapedia"
        if cwd_dir.is_dir():
            data_dir = cwd_dir.resolve()
            if args.verbose:
                print(f"Using data dir (cwd-relative): {data_dir}")
        else:
            print(f"Data directory not found: {args.data_dir}")
            print(f"  (Also tried cwd-relative: {cwd_dir})")
            return 1
    if args.verbose:
        print(f"Data dir: {data_dir}")

    steps_to_run = [s.strip() for s in args.tables.split(",") if s.strip()] if args.tables else [name for name, _ in STEPS]
    step_map = {name: fn for name, fn in STEPS}

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
    except mysql.connector.Error as e:
        print(f"Database connection failed: {e}")
        return 1

    if args.dry_run:
        print("DRY RUN — no changes will be written.")

    total = 0
    for name in steps_to_run:
        if name not in step_map:
            print(f"Unknown step: {name}")
            continue
        fn = step_map[name]
        try:
            n = fn(cursor, data_dir, args.dry_run, args.verbose)
            total += n
            print(f"  {name}: {n}")
        except Exception as e:
            print(f"  {name}: ERROR — {e}")
            if args.tables:
                conn.rollback()
                cursor.close()
                conn.close()
                return 1
            conn.rollback()
            raise

    if not args.dry_run:
        conn.commit()
    cursor.close()
    conn.close()
    print(f"Done. Total rows processed: {total}")
    return 0


if __name__ == "__main__":
    exit(main())
