"""
40K Army Book Reference: browse factions, detachments, and datasheets from the DB.
Uses existing waha_* tables and views. Unit grouping uses waha_datasheets.role when
present (from Wahapedia CSV), otherwise inferred from Keywords (Characters, Battleline, Other).
Unit legend, loadout, transport, and damaged profile come from waha_datasheets after
running scripts/wahapedia/hydrate_waha_datasheets_extra.py.
"""
import re
import streamlit as st
from database_utils import get_db_connection

# Display order for role-based grouping (inferred from Keywords)
ROLE_ORDER = ("Characters", "Battleline", "Other")


def _infer_role(keywords_str):
    """Infer 40K role from Keywords string for grouping."""
    if not keywords_str or not isinstance(keywords_str, str):
        return "Other"
    k = keywords_str.upper()
    if "EPIC HERO" in k or "CHARACTER" in k:
        return "Characters"
    if "BATTLELINE" in k:
        return "Battleline"
    return "Other"


def _strip_html(text):
    """Remove simple HTML tags for display."""
    if not text:
        return ""
    return re.sub(r"<[^>]+>", "", str(text))


def _dedupe_by_key(rows, key_fields):
    """Return rows deduplicated by the given key fields (first occurrence kept)."""
    if not rows or not key_fields:
        return list(rows)
    seen = set()
    out = []
    for r in rows:
        key = tuple(r.get(f) for f in key_fields)
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def run_w40k_army_book_ui():
    """Main entry: faction/detachment selectors and datasheet list."""
    st.title("40K Army Book Reference")
    st.caption("Browse factions, detachments, and datasheets from Wahapedia data in the database.")

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return

    # Factions that have 40K datasheets (from view_master_picker)
    cursor.execute("SELECT DISTINCT faction FROM view_master_picker WHERE game_system = %s ORDER BY faction", ("40K",))
    factions = [r["faction"] for r in cursor.fetchall()]
    if not factions:
        st.warning("No 40K factions found. Load Wahapedia data into waha_* tables first.")
        conn.close()
        return

    faction_name = st.selectbox("Faction", options=factions, key="w40k_ab_faction")
    if not faction_name:
        conn.close()
        return

    # Resolve faction id for detachments
    cursor.execute("SELECT id FROM waha_factions WHERE name = %s", (faction_name,))
    fac_row = cursor.fetchone()
    faction_id = fac_row["id"] if fac_row else None

    # Detachments for this faction (optional)
    detachments = []
    if faction_id:
        cursor.execute("SELECT id, name, legend, type FROM waha_detachments WHERE faction_id = %s ORDER BY name", (faction_id,))
        detachments = cursor.fetchall()
    detachment_id = None
    detachment_legend = None
    if detachments:
        det_options = ["— No detachment selected"] + [d["name"] for d in detachments]
        det_sel = st.selectbox("Detachment (optional)", options=det_options, key="w40k_ab_detachment")
        if det_sel and det_sel != "— No detachment selected":
            for d in detachments:
                if d["name"] == det_sel:
                    detachment_id = d["id"]
                    detachment_legend = d.get("legend")
                    break

    # Show detachment legend if selected
    if detachment_legend:
        with st.expander("Detachment lore & rules", expanded=True):
            st.markdown(_strip_html(detachment_legend))

    # Army rules (faction + optional detachment)
    if detachment_id:
        cursor.execute("""
            SELECT DISTINCT army_rule_name, army_rule_desc, detachment_rule_name, detachment_rule_desc
            FROM view_40k_army_rules
            WHERE (faction_name = %s OR faction_id = %s) AND detachment_id = %s
            LIMIT 1
        """, (faction_name, faction_id, detachment_id))
    else:
        cursor.execute("""
            SELECT DISTINCT army_rule_name, army_rule_desc, NULL as detachment_rule_name, NULL as detachment_rule_desc
            FROM view_40k_army_rules
            WHERE faction_name = %s OR faction_id = %s
            LIMIT 1
        """, (faction_name, faction_id))
    army_rules = cursor.fetchone()
    if army_rules and (army_rules.get("army_rule_desc") or army_rules.get("detachment_rule_desc")):
        with st.expander("Army & detachment rules", expanded=False):
            if army_rules.get("army_rule_name"):
                st.markdown(f"**{army_rules['army_rule_name']}**")
                st.write(army_rules.get("army_rule_desc") or "")
            if army_rules.get("detachment_rule_name") and army_rules.get("detachment_rule_desc"):
                st.divider()
                st.markdown(f"**{army_rules['detachment_rule_name']}**")
                st.write(army_rules["detachment_rule_desc"])

    st.divider()

    # Datasheets for this faction (view_40k_datasheet_complete uses Faction name)
    cursor.execute("SELECT * FROM view_40k_datasheet_complete WHERE Faction = %s ORDER BY Points, Unit_Name", (faction_name,))
    units = cursor.fetchall()
    if not units:
        st.info(f"No datasheets found for {faction_name}.")
        conn.close()
        return

    # Extra fields from waha_datasheets (legend, role, loadout, transport, damaged_*) when migration + hydrator have run
    ids = [u.get("ID") for u in units if u.get("ID")]
    extra_by_id = {}
    if ids:
        placeholders = ",".join(["%s"] * len(ids))
        try:
            cursor.execute(f"""
                SELECT waha_datasheet_id, legend, role, loadout, transport, damaged_w, damaged_description
                FROM waha_datasheets WHERE waha_datasheet_id IN ({placeholders})
            """, ids)
            for r in cursor.fetchall():
                extra_by_id[r["waha_datasheet_id"]] = r
        except Exception:
            pass  # columns may not exist yet

    # Group by DB role when present, else inferred from Keywords
    by_role = {}
    for u in units:
        uid = u.get("ID")
        extra = extra_by_id.get(uid) or {}
        role = (extra.get("role") or "").strip() or _infer_role(u.get("Keywords"))
        if role not in by_role:
            by_role[role] = []
        by_role[role].append(u)

    st.markdown(f"**{faction_name}** — {len(units)} units")
    for role in ROLE_ORDER:
        group = by_role.get(role, [])
        if not group:
            continue
        st.subheader(role)
        st.caption(f"{len(group)} unit(s)")
        for u in group:
            with st.container(border=True):
                uid = u.get("ID")
                extra = extra_by_id.get(uid) or {}
                st.subheader(u.get("Unit_Name") or "Unnamed")
                if extra.get("legend"):
                    with st.expander("Unit lore", expanded=False):
                        st.markdown(_strip_html(extra["legend"]))
                c1, c2, c3, c4, c5, c6 = st.columns(6)
                c1.metric("Pts", u.get("Points") or 0)
                c2.metric("M", u.get("M") or "—")
                c3.metric("T", u.get("T") or "—")
                c4.metric("Sv", u.get("Sv") or "—")
                c5.metric("W", u.get("W") or "—")
                c6.metric("OC", u.get("OC") or "—")
                if extra.get("loadout"):
                    st.caption(f"**Loadout:** {_strip_html(extra['loadout'])}")
                if extra.get("transport"):
                    st.caption(f"**Transport:** {_strip_html(extra['transport'])}")
                if extra.get("damaged_w") or extra.get("damaged_description"):
                    st.caption(f"**Damaged ({extra.get('damaged_w') or '—'}):** {_strip_html(extra.get('damaged_description') or '')}")
                if u.get("Keywords"):
                    st.caption(f"**Keywords:** {u['Keywords']}")
                if u.get("Base"):
                    st.caption(f"**Base:** {u['Base']}")
                if u.get("Image"):
                    st.image(u["Image"], width=150, caption="Datasheet")
                # Abilities
                cursor.execute("""
                    SELECT COALESCE(a.name, da.name) as ab_name, COALESCE(a.description, da.description) as ab_desc
                    FROM waha_datasheets_abilities da
                    LEFT JOIN waha_abilities a ON da.ability_id = a.id
                    WHERE da.datasheet_id = %s AND (da.type IN ('Datasheet', 'Wargear') OR da.type IS NULL)
                    ORDER BY da.line_id
                """, (uid,))
                ab_list = cursor.fetchall()
                ab_list = _dedupe_by_key(ab_list, ("ab_name", "ab_desc"))
                if ab_list:
                    with st.expander("Abilities", expanded=False):
                        for ab in ab_list:
                            st.markdown(f"**{ab['ab_name'] or 'Ability'}**: {ab['ab_desc'] or ''}")
                # Wargear
                cursor.execute("""
                    SELECT name, range_val, type, attacks, bs_ws, strength, ap, damage, description
                    FROM waha_datasheets_wargear WHERE datasheet_id = %s ORDER BY line_id, line_in_wargear
                """, (uid,))
                wg_list = cursor.fetchall()
                wg_list = _dedupe_by_key(wg_list, ("name", "range_val", "type", "attacks", "bs_ws", "strength", "ap", "damage"))
                if wg_list:
                    with st.expander("Wargear / weapons", expanded=False):
                        for w in wg_list:
                            name = w.get("name") or "—"
                            rng = w.get("range_val") or "—"
                            a = w.get("attacks") or "—"
                            bs = w.get("bs_ws") or "—"
                            s = w.get("strength") or "—"
                            ap = w.get("ap") or "—"
                            d = w.get("damage") or "—"
                            st.write(f"**{name}** — Range {rng} | A {a} | BS/WS {bs} | S {s} | AP {ap} | D {d}")
                            if w.get("description"):
                                st.caption(w["description"])
                # Options (wargear options / loadout)
                cursor.execute("SELECT button_text, description FROM waha_datasheets_options WHERE datasheet_id = %s ORDER BY line_id", (uid,))
                opt_list = cursor.fetchall()
                opt_list = _dedupe_by_key(opt_list, ("button_text", "description"))
                if opt_list:
                    with st.expander("Options", expanded=False):
                        for o in opt_list:
                            st.markdown(f"**{o.get('button_text') or 'Option'}**")
                            st.write(o.get("description") or "")
                st.divider()

    conn.close()
