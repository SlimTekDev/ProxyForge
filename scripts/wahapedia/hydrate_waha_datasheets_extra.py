"""
Hydrate waha_datasheets extra columns (legend, role, loadout, transport, damaged_w, damaged_description, link)
from data/wahapedia Datasheets. Prefers cleaned CSVs (non-UTF chars and HTML removed): Datasheets_Clean.csv
or Cleaned_CSVs/Datasheets.csv, then falls back to Datasheets.csv. Run after ProxyForge/migrations/add_waha_datasheets_extra.sql.

Usage:
  python scripts/wahapedia/hydrate_waha_datasheets_extra.py
  python scripts/wahapedia/hydrate_waha_datasheets_extra.py --file path/to/Datasheets.csv

Uses .env for DB (MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE).
"""
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

_REPO = Path(__file__).resolve().parents[2]
_DATA_DIR = _REPO / "data" / "wahapedia"
_CLEANED_DIR = _DATA_DIR / "Cleaned_CSVs"
# Prefer root Datasheets.csv first so ids (000000001) match DB from full hydrator; then cleaned options.
# Root is pipe-delimited with same id scheme as waha_datasheets; cleaned often has different ids (882).
DEFAULT_CSV_CANDIDATES = [
    _DATA_DIR / "Datasheets.csv",
    _DATA_DIR / "Datasheets_Clean.csv",
    _CLEANED_DIR / "Datasheets.csv",
]
DB_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
    "user": os.environ.get("MYSQL_USER", "hobby_admin"),
    "password": os.environ.get("MYSQL_PASSWORD", ""),
    "database": os.environ.get("MYSQL_DATABASE", "wargaming_erp"),
}


def _norm_id(v):
    """Normalize id to 9-digit string so cleaned (882) matches DB (000000882)."""
    s = (v or "").strip() if isinstance(v, str) else (str(v).strip() if v else "")
    if not s:
        return None
    if s.replace(".0", "").strip().isdigit():
        try:
            return str(int(float(s))).zfill(9)
        except (ValueError, TypeError):
            return s
    return s


def _detect_delimiter(path: Path) -> str:
    with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
        first = f.readline()
    return "|" if "|" in first else ","


def _row_key(row: dict, *keys: str):
    """Get first present value from row; strip BOM from keys so '\ufeffid' works as 'id'."""
    for k in keys:
        v = row.get(k)
        if v is not None and str(v).strip() != "":
            return v
        # Try BOM-prefixed key (some exports have BOM in header)
        bom_k = "\ufeff" + k
        v = row.get(bom_k)
        if v is not None and str(v).strip() != "":
            return v
    return None


def _strip_html(text: str | None) -> str | None:
    """Remove HTML tags so root Datasheets (with <b> etc.) is safe to store."""
    if not text or not isinstance(text, str):
        return text
    return re.sub(r"<[^>]+>", "", text.strip()).strip() or None


def main():
    ap = argparse.ArgumentParser(description="Hydrate waha_datasheets extra columns from Wahapedia Datasheets (prefer cleaned CSVs)")
    ap.add_argument("--file", type=Path, default=None, help="Path to Datasheets CSV (default: prefer Datasheets_Clean.csv, Cleaned_CSVs/Datasheets.csv, then Datasheets.csv)")
    args = ap.parse_args()

    if args.file is not None:
        csv_path = args.file
    else:
        csv_path = None
        for p in DEFAULT_CSV_CANDIDATES:
            if p.exists():
                csv_path = p
                break
    if not csv_path or not csv_path.exists():
        print(f"No Datasheets CSV found. Tried: {[str(p) for p in DEFAULT_CSV_CANDIDATES]}")
        return 1

    delimiter = _detect_delimiter(csv_path)
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        print(f"Connection failed: {err}")
        return 1

    cursor = conn.cursor()
    sql = """
        UPDATE waha_datasheets
        SET legend = %s, role = %s, loadout = %s, transport = %s,
            damaged_w = %s, damaged_description = %s, link = %s
        WHERE waha_datasheet_id = %s
    """
    count = 0
    updated = 0
    with open(csv_path, "r", encoding="utf-8-sig", errors="replace") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        for row in reader:
            # Prefer id; try datasheet_id, ID (BOM-stripped via _row_key)
            raw_id = _row_key(row, "id", "datasheet_id", "ID")
            if raw_id is not None:
                raw_id = str(raw_id).strip()
            if not raw_id:
                continue
            datasheet_id = _norm_id(raw_id)
            if not datasheet_id:
                continue
            count += 1
            def _v(k):
                v = _row_key(row, k, k.lower(), k.capitalize())
                return ((v or "").strip() or None) if v is not None else None
            legend = _strip_html(_v("legend")) or _v("legend")
            role = _v("role")
            loadout = _strip_html(_v("loadout")) or _v("loadout")
            transport = _strip_html(_v("transport")) or _v("transport")
            damaged_w = _v("damaged_w")
            damaged_description = _v("damaged_description")
            link = _v("link")
            cursor.execute(sql, (legend, role, loadout, transport, damaged_w, damaged_description, link, datasheet_id))
            if cursor.rowcount > 0:
                updated += 1
            else:
                # DB may use un-normalized ids (e.g. "882" or "1"); try raw_id then numeric form
                for try_id in (raw_id, str(int(datasheet_id)) if datasheet_id.isdigit() else None):
                    if try_id is None or try_id == datasheet_id:
                        continue
                    cursor.execute(sql, (legend, role, loadout, transport, damaged_w, damaged_description, link, try_id))
                    if cursor.rowcount > 0:
                        updated += 1
                        break
    conn.commit()
    if updated == 0 and count > 0:
        cursor.execute("SELECT waha_datasheet_id FROM waha_datasheets LIMIT 5")
        db_ids = [r[0] for r in cursor.fetchall()]
        print(f"  No rows updated. CSV and DB ids may be from different exports.")
        print(f"  Sample DB waha_datasheet_id: {db_ids}")
        print(f"  Ensure this CSV is the same export used to load waha_datasheets (run hydrate_waha_full.py first with this file in data/wahapedia/).")
    cursor.close()
    conn.close()
    print(f"Processed {count} CSV rows; updated {updated} waha_datasheets rows.")
    return 0


if __name__ == "__main__":
    exit(main())
