"""
Export 40K unit data (abilities, wargear, enhancements) for spot-check vs Wahapedia.
Run from repo root: python scripts/spotcheck_export_40k_units.py

Uses .env for DB. Outputs plain text suitable for pasting into a comparison report.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
except ImportError:
    pass

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "ProxyForge"))
from database_utils import get_db_connection

SPOTCHECK_UNITS = [
    "Ork Boyz",
    "Ork Warboss",
    "Space Marine Intercessors",
    "Space Marine Marneus Calgar",
    "Ork Battlewagon",
    "Tau Crisis Suit",
]

# Flexible name matching: also try without faction prefix
NAME_VARIANTS = {
    "Ork Boyz": ["Boyz", "Ork Boyz"],
    "Ork Warboss": ["Warboss", "Ork Warboss"],
    "Space Marine Intercessors": ["Intercessor Squad", "Intercessors"],
    "Space Marine Marneus Calgar": ["Marneus Calgar", "Marneus Calgar, Chapter Master"],
    "Ork Battlewagon": ["Battlewagon", "Ork Battlewagon"],
    "Tau Crisis Suit": ["Crisis Suits", "Crisis Battlesuits", "Crisis Suit"],
}


def main():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    out = []
    for label in SPOTCHECK_UNITS:
        variants = NAME_VARIANTS.get(label, [label])
        ds_id = None
        name_found = None
        for v in variants:
            # Prefer exact match, then prefix match (e.g. "Intercessors" not "Assault Intercessors With Jump Packs")
            cur.execute(
                "SELECT waha_datasheet_id, name FROM waha_datasheets WHERE name = %s LIMIT 1",
                (v,),
            )
            row = cur.fetchone()
            if not row:
                cur.execute(
                    "SELECT waha_datasheet_id, name FROM waha_datasheets WHERE name LIKE %s ORDER BY CASE WHEN name = %s THEN 0 WHEN name LIKE %s THEN 1 ELSE 2 END, name LIMIT 1",
                    (f"%{v}%", v, f"{v}%"),
                )
                row = cur.fetchone()
            if row:
                ds_id = row["waha_datasheet_id"]
                name_found = row["name"]
                break
        if not ds_id:
            out.append(f"## {label}\n  NOT FOUND in waha_datasheets.\n")
            continue
        out.append(f"## {label} (DB name: {name_found}, id: {ds_id})")
        # Abilities
        cur.execute(
            """
            SELECT COALESCE(a.name, da.name) AS ab_name, da.type AS ab_type, COALESCE(a.description, da.description) AS ab_desc
            FROM waha_datasheets_abilities da
            LEFT JOIN waha_abilities a ON da.ability_id = a.id
            WHERE da.datasheet_id = %s
            ORDER BY LOWER(TRIM(COALESCE(da.type,''))), ab_name
            """,
            (ds_id,),
        )
        ab_rows = cur.fetchall()
        if not ab_rows:
            cur.execute(
                """
                SELECT COALESCE(a.name, da.name) AS ab_name, da.type AS ab_type, COALESCE(a.description, da.description) AS ab_desc
                FROM waha_datasheets_abilities da
                LEFT JOIN waha_abilities a ON da.ability_id = a.id
                WHERE CAST(da.datasheet_id AS CHAR) = %s
                ORDER BY LOWER(TRIM(COALESCE(da.type,''))), ab_name
                """,
                (str(ds_id).strip(),),
            )
            ab_rows = cur.fetchall()
        out.append("  Abilities:")
        if ab_rows:
            for r in ab_rows:
                t = (r.get("ab_type") or "").strip()
                n = (r.get("ab_name") or "").strip()
                d = (r.get("ab_desc") or "")[:80].strip()
                out.append(f"    - [{t}] {n}" + (f": {d}..." if d else ""))
        else:
            out.append("    (none)")
        # Wargear (weapon options)
        cur.execute(
            "SELECT name, range_val, attacks, bs_ws, ap, damage FROM waha_datasheets_wargear WHERE datasheet_id = %s ORDER BY name",
            (ds_id,),
        )
        wg = cur.fetchall()
        if not wg and str(ds_id).strip():
            cur.execute(
                "SELECT name, range_val, attacks, bs_ws, ap, damage FROM waha_datasheets_wargear WHERE CAST(datasheet_id AS CHAR) = %s ORDER BY name",
                (str(ds_id).strip(),),
            )
            wg = cur.fetchall()
        out.append("  Wargear/Weapons (count): " + str(len(wg)))
        for r in (wg or [])[:15]:
            out.append(f"    - {r.get('name', '')} (Range {r.get('range_val')}, A{r.get('attacks')}, etc.)")
        if wg and len(wg) > 15:
            out.append(f"    ... and {len(wg) - 15} more")
        out.append("")
    cur.close()
    conn.close()
    text = "\n".join(out)
    print(text)
    return text


if __name__ == "__main__":
    main()
