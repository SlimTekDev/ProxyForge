"""
Clean HTML tags and mojibake from all 40K (waha_*) text columns in the database.
Strips <div>, <span>, <img>, <table>, etc., decodes entities, fixes ΓÇÖ -> ', etc.
Run from repo root. Uses .env for DB unless --env-file is given.

Usage:
  python scripts/wahapedia/clean_waha_40k_text.py
  python scripts/wahapedia/clean_waha_40k_text.py --dry-run
  python scripts/wahapedia/clean_waha_40k_text.py --env-file .env.cloud   # run against cloud DB
  python scripts/wahapedia/clean_waha_40k_text.py --env-file .env.cloud --batch 200 --progress 500  # commit every 200, print progress every 500
"""
import argparse
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
try:
    from dotenv import load_dotenv
    load_dotenv(_REPO / ".env")
except ImportError:
    load_dotenv = None

sys.path.insert(0, str(_REPO / "ProxyForge"))
from database_utils import get_db_connection
from text_utils import clean_html_and_mojibake

# (table, list of PK column names, list of text column names to clean)
WAHA_TABLES = [
    ("waha_detachments", ["id"], ["name", "legend", "rules_summary"]),
    ("waha_datasheets", ["waha_datasheet_id"], ["name", "loadout", "legend", "transport", "damaged_description"]),
    ("waha_datasheet_unit_composition", ["datasheet_id", "line_id"], ["description"]),
    ("waha_datasheets_models", ["datasheet_id", "line_id"], ["name", "inv_sv_descr", "base_size_descr"]),
    ("waha_datasheets_abilities", ["datasheet_id", "line_id"], ["model_name", "name", "description"]),
    ("waha_datasheets_options", ["datasheet_id", "line_id"], ["button_text", "description"]),
    ("waha_datasheets_wargear", ["datasheet_id", "line_id", "line_in_wargear"], ["name", "description"]),
    ("waha_abilities", ["id"], ["name", "legend", "description"]),
    ("waha_detachment_abilities", ["id"], ["name", "legend", "description"]),
    ("waha_enhancements", ["id"], ["name", "legend", "description"]),
    ("waha_stratagems", ["id"], ["name", "legend", "description"]),
    ("waha_weapons", ["weapon_id"], ["name"]),
]


def get_existing_columns(cursor, table):
    """Return set of column names that exist in table."""
    cursor.execute(f"SHOW COLUMNS FROM `{table}`")
    rows = cursor.fetchall()
    # cursor(dictionary=True): keys are column names (MySQL uses "Field" for first column; driver may lowercase)
    return {row.get("Field") or row.get("field") or next(iter(row.values())) for row in rows}


def main():
    ap = argparse.ArgumentParser(description="Clean HTML and mojibake from waha_* text columns")
    ap.add_argument("--dry-run", action="store_true", help="Do not UPDATE; print changes only")
    ap.add_argument("--env-file", default=os.environ.get("PROXYFORGE_ENV_FILE"), help="Use this env file for DB (e.g. .env.cloud). Default: .env")
    ap.add_argument("--batch", type=int, default=500, help="Commit every N row updates (default 500). Lower = more progress, more commits.")
    ap.add_argument("--progress", type=int, default=1000, help="Print progress every N rows (default 1000). 0 = no progress.")
    args = ap.parse_args()
    if args.env_file:
        if load_dotenv is None:
            print("python-dotenv required for --env-file. pip install python-dotenv", file=sys.stderr)
            sys.exit(1)
        path = _REPO / args.env_file if not Path(args.env_file).is_absolute() else Path(args.env_file)
        if path.exists():
            load_dotenv(path, override=True)
        else:
            print(f"Env file not found: {path}", file=sys.stderr)
            sys.exit(1)
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    total_updated = 0
    batch_size = max(1, args.batch) if not args.dry_run else 0
    progress_every = max(0, args.progress)
    try:
        for table, pk_cols, text_cols in WAHA_TABLES:
            existing = get_existing_columns(cursor, table)
            pk_use = [c for c in pk_cols if c in existing]
            cols_to_clean = [c for c in text_cols if c in existing]
            if not cols_to_clean or not pk_use:
                continue
            select_cols = pk_use + cols_to_clean
            select_sql = f"SELECT {', '.join(f'`{c}`' for c in select_cols)} FROM `{table}`"
            cursor.execute(select_sql)
            rows = cursor.fetchall()
            table_updated = 0
            for i, row in enumerate(rows):
                pk_vals = [row[c] for c in pk_use]
                updates = []
                params = []
                for col in cols_to_clean:
                    raw = row.get(col)
                    if raw is None or not isinstance(raw, str) or not raw.strip():
                        continue
                    cleaned = clean_html_and_mojibake(raw, preserve_newlines=True)
                    if cleaned is None:
                        continue
                    if cleaned != raw:
                        updates.append(f"`{col}` = %s")
                        params.append(cleaned)
                if not updates:
                    continue
                params.extend(pk_vals)
                where_parts = []
                for c in pk_use:
                    if pk_vals[pk_use.index(c)] is None:
                        where_parts.append(f"`{c}` IS NULL")
                    else:
                        where_parts.append(f"`{c}` = %s")
                where_vals = [v for v in pk_vals if v is not None]
                where_clause = " AND ".join(where_parts)
                update_sql = f"UPDATE `{table}` SET {', '.join(updates)} WHERE {where_clause}"
                update_params = params[: len(updates)] + where_vals
                total_updated += 1
                table_updated += 1
                if not args.dry_run:
                    cursor.execute(update_sql, update_params)
                    if batch_size and total_updated % batch_size == 0:
                        conn.commit()
                else:
                    print(f"[DRY-RUN] {table} {dict(zip(pk_use, pk_vals))}: would update {[c for c in cols_to_clean if row.get(c) and clean_html_and_mojibake(row[c]) != row[c]]}")
                if progress_every and total_updated > 0 and total_updated % progress_every == 0:
                    print(f"  ... {total_updated} rows updated (current table: {table})")
            if table_updated and not args.dry_run:
                conn.commit()
            if table_updated:
                print(f"  {table}: {table_updated} rows" + (" (dry-run)" if args.dry_run else ""))
        print(f"Done. Rows updated: {total_updated}")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
