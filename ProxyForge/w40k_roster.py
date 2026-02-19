"""
40K Roster data layer: single source of truth for roster ↔ datasheet association.

All roster rows carry a canonical datasheet_id from the JOIN with waha_datasheets.
Use datasheet_id (not raw unit_id) for any lookups into waha_datasheets_* tables.
"""

from database_utils import get_db_connection


def get_roster_40k(conn, list_id):
    """
    Load roster for a 40K list. Returns list of dicts with canonical datasheet_id.

    Each row includes:
      - entry_id, list_id, quantity (Qty), Unit (name), Total_Pts, wargear_list
      - unit_id: raw value from play_armylist_entries (for DB updates)
      - datasheet_id: from waha_datasheets.waha_datasheet_id (JOIN). Use this for
        all lookups (wargear, composition, abilities, etc.). None if join failed.
    """
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                e.entry_id,
                e.list_id,
                e.unit_id,
                e.quantity AS Qty,
                d.waha_datasheet_id AS datasheet_id,
                COALESCE(d.name, 'Unknown unit') AS Unit,
                COALESCE(
                    (d.points_cost * CEIL(e.quantity / COALESCE(
                        (SELECT min_size FROM view_40k_unit_composition WHERE datasheet_id = d.waha_datasheet_id LIMIT 1),
                        1
                    ))) + (SELECT COALESCE(SUM(enh.cost), 0) FROM play_armylist_enhancements enh WHERE enh.entry_id = e.entry_id),
                    0
                ) AS Total_Pts,
                (SELECT JSON_ARRAYAGG(option_text) FROM play_armylist_wargear_selections WHERE entry_id = e.entry_id AND (option_text NOT LIKE 'w2|%%' OR option_text = '')) AS wargear_list,
                e.attached_to_entry_id
            FROM play_armylist_entries e
            JOIN play_armylists l ON e.list_id = l.list_id AND l.game_system = '40K_10E'
            LEFT JOIN waha_datasheets d ON e.unit_id = d.waha_datasheet_id
            WHERE e.list_id = %s
            ORDER BY e.entry_id
            """,
            (list_id,),
        )
    except Exception:
        cursor.execute(
            """
            SELECT
                e.entry_id,
                e.list_id,
                e.unit_id,
                e.quantity AS Qty,
                d.waha_datasheet_id AS datasheet_id,
                COALESCE(d.name, 'Unknown unit') AS Unit,
                COALESCE(
                    (d.points_cost * CEIL(e.quantity / COALESCE(
                        (SELECT min_size FROM view_40k_unit_composition WHERE datasheet_id = d.waha_datasheet_id LIMIT 1),
                        1
                    ))) + (SELECT COALESCE(SUM(enh.cost), 0) FROM play_armylist_enhancements enh WHERE enh.entry_id = e.entry_id),
                    0
                ) AS Total_Pts,
                (SELECT JSON_ARRAYAGG(option_text) FROM play_armylist_wargear_selections WHERE entry_id = e.entry_id AND (option_text NOT LIKE 'w2|%%' OR option_text = '')) AS wargear_list
            FROM play_armylist_entries e
            JOIN play_armylists l ON e.list_id = l.list_id AND l.game_system = '40K_10E'
            LEFT JOIN waha_datasheets d ON e.unit_id = d.waha_datasheet_id
            WHERE e.list_id = %s
            ORDER BY e.entry_id
            """,
            (list_id,),
        )
    rows = cursor.fetchall()
    for r in rows:
        if r.get("attached_to_entry_id") is None and "attached_to_entry_id" not in r:
            r["attached_to_entry_id"] = None
    cursor.close()
    # Normalize datasheet_id to string (no trailing .0) so lookups match
    for r in rows:
        if r.get("datasheet_id") is not None:
            raw = str(r["datasheet_id"]).strip()
            r["datasheet_id"] = raw[:-2] if raw.endswith(".0") and raw[:-2].isdigit() else raw
    return rows


def add_unit_40k(conn, list_id, waha_datasheet_id, quantity=1):
    """
    Add a unit to the roster. Stores exact waha_datasheet_id so JOINs and lookups work.

    waha_datasheet_id must be the primary key from waha_datasheets (e.g. from picker).
    """
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO play_armylist_entries (list_id, unit_id, quantity) VALUES (%s, %s, %s)",
        (list_id, str(waha_datasheet_id).strip(), int(quantity)),
    )
    conn.commit()
    cursor.close()


def get_datasheet_id_for_entry(conn, entry_id):
    """
    Return canonical waha_datasheet_id for a roster entry (via JOIN).
    Use when you only have entry_id (e.g. in unit details dialog).
    Same ID as view_master_picker.id / library card — use for all template data (stats, weapons, rules, etc.).
    """
    try:
        eid = int(entry_id)
    except (TypeError, ValueError):
        return None
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT d.waha_datasheet_id AS datasheet_id
        FROM play_armylist_entries e
        JOIN play_armylists l ON e.list_id = l.list_id AND l.game_system = '40K_10E'
        LEFT JOIN waha_datasheets d ON e.unit_id = d.waha_datasheet_id
        WHERE e.entry_id = %s
        LIMIT 1
        """,
        (eid,),
    )
    row = cursor.fetchone()
    cursor.close()
    if not row or row.get("datasheet_id") is None:
        return None
    raw = str(row["datasheet_id"]).strip()
    return raw[:-2] if raw.endswith(".0") and raw[:-2].isdigit() else raw


def get_debug_query_results(conn, list_id, datasheet_id=None):
    """
    Run the key queries that drive roster, unit details, and gameday views.
    Returns a list of {"name": str, "rows": list, "error": str|None} for UI or scripts.
    """
    cur = conn.cursor(dictionary=True)
    out = []

    def run(name, query, params=None):
        try:
            cur.execute(query, params or ())
            return {"name": name, "rows": cur.fetchall(), "error": None}
        except Exception as e:
            return {"name": name, "rows": [], "error": str(e)}

    # 1. 40K lists
    out.append(run(
        "1. play_armylists (40K)",
        "SELECT list_id, list_name, game_system, point_limit, faction_primary FROM play_armylists WHERE game_system = '40K_10E' ORDER BY list_id",
    ))

    if list_id is None:
        cur.close()
        return out

    # 2. Raw entries
    out.append(run(
        "2. play_armylist_entries (raw)",
        "SELECT entry_id, list_id, unit_id, quantity FROM play_armylist_entries WHERE list_id = %s ORDER BY entry_id",
        (list_id,),
    ))

    # 3. JOIN entries → waha_datasheets
    out.append(run(
        "3. JOIN entries → waha_datasheets (datasheet_id)",
        """
        SELECT e.entry_id, e.unit_id AS stored_unit_id,
               d.waha_datasheet_id AS datasheet_id, d.name AS unit_name
        FROM play_armylist_entries e
        JOIN play_armylists l ON e.list_id = l.list_id AND l.game_system = '40K_10E'
        LEFT JOIN waha_datasheets d ON e.unit_id = d.waha_datasheet_id
        WHERE e.list_id = %s ORDER BY e.entry_id
        """,
        (list_id,),
    ))

    # 4. get_roster_40k result
    try:
        roster = get_roster_40k(conn, list_id)
        out.append({"name": "4. get_roster_40k (roster view)", "rows": roster, "error": None})
    except Exception as e:
        out.append({"name": "4. get_roster_40k (roster view)", "rows": [], "error": str(e)})

    # 5. view_master_picker (library) — DB may have game_system or system depending on dump
    out.append(run(
        "5. view_master_picker (library sample)",
        "SELECT * FROM view_master_picker WHERE game_system = '40K' LIMIT 5",
    ))

    # Sample datasheet for unit-detail queries
    sample_dsid = datasheet_id
    if sample_dsid is None and out[3]["rows"]:
        sample_dsid = next((r.get("datasheet_id") for r in out[3]["rows"] if r.get("datasheet_id")), None)

    if sample_dsid:
        sid = str(sample_dsid).strip()
        out.append(run(
            f"6. view_40k_datasheet_complete (ID={sample_dsid})",
            "SELECT * FROM view_40k_datasheet_complete WHERE ID = %s",
            (sid,),
        ))
        out.append(run(
            f"7a. waha_datasheets_wargear (ID={sample_dsid})",
            "SELECT name, range_val, attacks, bs_ws, ap, damage FROM waha_datasheets_wargear WHERE datasheet_id = %s",
            (sid,),
        ))
        out.append(run(
            f"7b. waha_datasheet_unit_composition (ID={sample_dsid})",
            "SELECT line_id, description FROM waha_datasheet_unit_composition WHERE datasheet_id = %s ORDER BY line_id",
            (sid,),
        ))
        out.append(run(
            f"7c. waha_datasheets_models (ID={sample_dsid})",
            "SELECT line_id, name, movement, toughness, save_value, wounds, leadership, oc FROM waha_datasheets_models WHERE datasheet_id = %s ORDER BY line_id",
            (sid,),
        ))
        out.append(run(
            "8. view_list_validation_40k",
            "SELECT unit_name, times_taken, max_allowed, faction_status FROM view_list_validation_40k WHERE list_id = %s",
            (list_id,),
        ))
        out.append(run(
            f"9. view_40k_unit_composition (ID={sample_dsid})",
            "SELECT datasheet_id, min_size, max_size FROM view_40k_unit_composition WHERE datasheet_id = %s",
            (str(sample_dsid),),
        ))

    cur.close()
    return out
