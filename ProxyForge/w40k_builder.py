import streamlit as st
import pandas as pd
import re
from database_utils import get_db_connection
from library_ui import render_inline_link_unit, render_roster_stl_section
from text_utils import fix_apostrophe_mojibake
from w40k_roster import get_roster_40k, add_unit_40k, get_datasheet_id_for_entry, get_debug_query_results

# --- 1. HELPER FUNCTIONS ---

def _strip_html(text):
    """Remove HTML tags and normalize whitespace for plain-text display."""
    if not text:
        return ""
    s = str(text)
    # Remove HTML tags
    s = re.sub(r"<[^>]+>", "", s)
    # Decode common entities
    s = s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
    return " ".join(s.split())


def _loadout_to_display(html_text):
    """Convert loadout HTML to display text, preserving line breaks from <br> so each model line is separate."""
    if not html_text:
        return ""
    s = str(html_text).strip()
    for br in ("<br>", "<br/>", "<br />", "</br>"):
        s = s.replace(br, "\n")
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
    # If no <br> in source, split on period+space before "Every"/"The" so each model line is separate
    if "\n" not in s and re.search(r"\.\s+(Every|The)\s+", s):
        s = re.sub(r"\.\s+(Every\s+)", r".\n\1", s)
        s = re.sub(r"\.\s+(The\s+)", r".\n\1", s)
    lines = [" ".join(ln.split()) for ln in s.split("\n")]
    return "\n".join(ln for ln in lines if ln)


def _parse_loadout_to_model_weapons(loadout_text):
    """
    Parse default loadout text into list of (model_label, weapons_list).
    e.g. 'The Boss Nob is equipped with: slugga; big choppa. Every Boy is equipped with: slugga; choppa.'
    -> [('Boss Nob', ['slugga', 'big choppa']), ('Boy', ['slugga', 'choppa'])]
    """
    if not loadout_text or not str(loadout_text).strip():
        return []
    s = _loadout_to_display(loadout_text)
    out = []
    # Split into sentences (each model line)
    for line in re.split(r"\n|\.\s+(?=Every|The|Each)", s):
        line = line.strip().strip(".")
        if not line:
            continue
        # "The Boss Nob is equipped with: slugga; big choppa" or "Every Boy is equipped with: slugga; choppa"
        m = re.search(r"(?:The\s+)?(.+?)\s+is\s+equipped\s+with\s*:\s*(.+)", line, re.IGNORECASE)
        if m:
            model_label = m.group(1).strip()
            weapons_str = m.group(2).strip()
            weapons = [w.strip() for w in re.split(r"[;,]", weapons_str) if w.strip()]
            if model_label and weapons:
                out.append((model_label, weapons))
    return out


def _strip_option_html(text):
    """Strip HTML from wargear option / description text: lists to bullets, remove tags, decode entities."""
    if not text:
        return ""
    s = str(text).strip()
    # Convert list items to newline + bullet so structure is preserved
    s = re.sub(r"</li>\s*", "\n", s, flags=re.IGNORECASE)
    s = re.sub(r"<li[^>]*>", "• ", s, flags=re.IGNORECASE)
    for br in ("<br>", "<br/>", "<br />", "</br>"):
        s = s.replace(br, "\n")
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"').replace("&#39;", "'").replace("&apos;", "'")
    try:
        import html
        s = html.unescape(s)
    except Exception:
        pass
    lines = [" ".join(ln.split()) for ln in s.split("\n")]
    return fix_apostrophe_mojibake("\n".join(ln for ln in lines if ln))


def _show_led_by_can_lead_transport(cursor, unit_id):
    """Render Led By, Can Lead, and Transport for a unit (Rules tab or Game-Day card)."""
    if unit_id is None:
        return
    uid = unit_id
    uid_str = str(unit_id).strip()
    # LED BY
    try:
        cursor.execute("""
            SELECT d.name FROM waha_datasheets_leader l
            JOIN waha_datasheets d ON d.waha_datasheet_id = l.leader_id
            WHERE l.attached_id = %s ORDER BY d.name
        """, (uid,))
        led_by = cursor.fetchall()
        if not led_by:
            cursor.execute("""
                SELECT d.name FROM waha_datasheets_leader l
                JOIN waha_datasheets d ON d.waha_datasheet_id = l.leader_id
                WHERE CAST(l.attached_id AS CHAR) = %s ORDER BY d.name
            """, (uid_str,))
            led_by = cursor.fetchall()
        if led_by:
            st.markdown("**LED BY**")
            st.caption("This unit can be led by the following units:")
            for r in led_by:
                st.write(f"• {r.get('name', '')}")
    except Exception:
        pass
    # CAN LEAD
    try:
        cursor.execute("""
            SELECT d.name FROM waha_datasheets_leader l
            JOIN waha_datasheets d ON d.waha_datasheet_id = l.attached_id
            WHERE l.leader_id = %s ORDER BY d.name
        """, (uid,))
        can_lead = cursor.fetchall()
        if not can_lead:
            cursor.execute("""
                SELECT d.name FROM waha_datasheets_leader l
                JOIN waha_datasheets d ON d.waha_datasheet_id = l.attached_id
                WHERE CAST(l.leader_id AS CHAR) = %s ORDER BY d.name
            """, (uid_str,))
            can_lead = cursor.fetchall()
        if can_lead:
            st.markdown("**CAN LEAD**")
            st.caption("This unit can lead the following units:")
            for r in can_lead:
                st.write(f"• {r.get('name', '')}")
    except Exception:
        pass
    # Transport
    try:
        cursor.execute("SELECT transport FROM waha_datasheets WHERE waha_datasheet_id = %s", (uid,))
        row = cursor.fetchone()
        if not row and uid_str:
            cursor.execute("SELECT transport FROM waha_datasheets WHERE CAST(waha_datasheet_id AS CHAR) = %s", (uid_str,))
            row = cursor.fetchone()
        if row and row.get("transport") and str(row.get("transport")).strip():
            st.markdown("**TRANSPORT**")
            st.write(_strip_html(row.get("transport") or ""))
    except Exception:
        pass


def _valid_bodyguard_datasheet_ids(cursor, leader_datasheet_id):
    """Return set of datasheet_id (str) that this leader can attach to (from waha_datasheets_leader)."""
    if not leader_datasheet_id or not str(leader_datasheet_id).strip():
        return set()
    try:
        cursor.execute(
            "SELECT attached_id FROM waha_datasheets_leader WHERE leader_id = %s",
            (leader_datasheet_id,),
        )
        rows = cursor.fetchall()
        if not rows:
            cursor.execute(
                "SELECT attached_id FROM waha_datasheets_leader WHERE CAST(leader_id AS CHAR) = %s",
                (str(leader_datasheet_id).strip(),),
            )
            rows = cursor.fetchall()
        out = set()
        for r in rows:
            aid = r.get("attached_id")
            if aid is not None and str(aid).strip():
                s = str(aid).strip()
                if s.endswith(".0") and s[:-2].isdigit():
                    s = s[:-2]
                out.add(s)
        return out
    except Exception:
        return set()


def _is_leader(cursor, datasheet_id):
    """True if this unit can lead others (exists in waha_datasheets_leader as leader_id)."""
    if not datasheet_id or not str(datasheet_id).strip():
        return False
    try:
        cursor.execute("SELECT 1 FROM waha_datasheets_leader WHERE leader_id = %s LIMIT 1", (datasheet_id,))
        if cursor.fetchone():
            return True
        cursor.execute("SELECT 1 FROM waha_datasheets_leader WHERE CAST(leader_id AS CHAR) = %s LIMIT 1", (str(datasheet_id).strip(),))
        return cursor.fetchone() is not None
    except Exception:
        return False


def _format_stratagem_description(desc):
    """Strip HTML; insert line breaks before TARGET, EFFECT, RESTRICTIONS; bold WHEN, TARGET, EFFECT, RESTRICTIONS."""
    text = _strip_html(desc or "")
    if not text:
        return ""
    # Bold WHEN at the start (case-insensitive)
    text = re.sub(r"^\s*(WHEN)\s*:\s*", r"**\1:** ", text, count=1, flags=re.IGNORECASE)
    # Insert newline before TARGET, EFFECT, RESTRICTIONS and bold the label (match even with no space before, e.g. "move.TARGET:")
    text = re.sub(r"(TARGET)\s*:\s*", r"\n\n**\1:** ", text, flags=re.IGNORECASE)
    text = re.sub(r"(EFFECT)\s*:\s*", r"\n\n**\1:** ", text, flags=re.IGNORECASE)
    text = re.sub(r"(RESTRICTIONS?)\s*:\s*", r"\n\n**\1:** ", text, flags=re.IGNORECASE)
    return text.strip()


def _normalize_stratagem_name_for_key(name):
    """Normalize stratagem name for dedupe key: strip, lower, remove apostrophes/punctuation variants, collapse spaces."""
    if not name:
        return ""
    s = str(name).strip().lower()
    # Remove apostrophe-like chars so "One's" / "Ones" and "'ard" / "ard" match
    for c in ("'", "'", "'", "`", "\u2018", "\u2019"):
        s = s.replace(c, "")
    return " ".join(s.split())


def _dedupe_stratagems(strats):
    """Deduplicate stratagem rows by normalized (name, cp_cost). Prefer row without HTML in description for clean display."""
    if not strats:
        return []
    def _norm_key(s):
        name = (s.get("name") or "").strip() or ""
        cp = s.get("cp_cost")
        return (_normalize_stratagem_name_for_key(name), cp)
    by_key = {}
    for s in strats:
        key = _norm_key(s)
        if key not in by_key:
            by_key[key] = s
        else:
            # Prefer the row whose description has NO HTML (cleaner for display)
            prev_desc = (by_key[key].get("description") or "") or ""
            curr_desc = (s.get("description") or "") or ""
            if "<" not in curr_desc and "<" in prev_desc:
                by_key[key] = s
    out = list(by_key.values())
    out.sort(key=lambda s: (str(s.get("phase") or ""), str(s.get("name") or "")))
    return out


# Sentinel for "Custom (mix chapters)" so validation allows mixed chapter units
CHAPTER_CUSTOM = "CUSTOM"


def show_40k_validation(list_id, proxy_mode=False):
    """Queries Keyword-Strict SQL View and displays alerts. Adds enhancement cap (max 3, all different) and warlord (at least one Character). When chapter is CUSTOM, allows mixed chapters (no chapter mismatch errors)."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    allow_custom_chapter = False
    try:
        cursor.execute("SELECT chapter_subfaction FROM play_armylists WHERE list_id = %s", (list_id,))
        row = cursor.fetchone()
        if row and (row.get("chapter_subfaction") or "").strip() == CHAPTER_CUSTOM:
            allow_custom_chapter = True
    except Exception:
        pass
    allow_mixed_chapters = proxy_mode or allow_custom_chapter

    query = "SELECT unit_name, times_taken, max_allowed, faction_status FROM view_list_validation_40k WHERE list_id = %s"
    df_val = pd.read_sql(query, conn, params=(list_id,))

    # Enhancement cap: max 3 in list, all different
    enh_over = False
    enh_dupe = False
    try:
        cursor.execute("""
            SELECT COUNT(*) AS cnt, COUNT(DISTINCT e.enhancement_id) AS distinct_cnt
            FROM play_armylist_enhancements e
            JOIN play_armylist_entries ent ON e.entry_id = ent.entry_id
            WHERE ent.list_id = %s
        """, (list_id,))
        row = cursor.fetchone()
        if row:
            cnt = int(row.get("cnt") or 0)
            distinct_cnt = int(row.get("distinct_cnt") or 0)
            if cnt > 3:
                enh_over = True
            if distinct_cnt < cnt:
                enh_dupe = True
    except Exception:
        pass

    # Warlord: at least one Character in the list
    has_character = False
    try:
        cursor.execute("""
            SELECT 1 FROM play_armylist_entries e
            JOIN waha_datasheets d ON e.unit_id = d.waha_datasheet_id
            JOIN waha_datasheets_keywords k ON d.waha_datasheet_id = k.datasheet_id
            WHERE e.list_id = %s AND LOWER(TRIM(COALESCE(k.keyword,''))) = 'character'
            LIMIT 1
        """, (list_id,))
        if cursor.fetchone():
            has_character = True
    except Exception:
        pass

    cursor.close()
    conn.close()

    if not df_val.empty or enh_over or enh_dupe or not has_character:
        violations = df_val[df_val['times_taken'] > df_val['max_allowed']] if not df_val.empty else pd.DataFrame()
        mismatches = df_val[df_val['faction_status'] == 'INVALID'] if not df_val.empty else pd.DataFrame()

        st.sidebar.divider()
        st.sidebar.subheader("⚖️ List Validation")

        if not mismatches.empty:
            if allow_mixed_chapters:
                if allow_custom_chapter and not proxy_mode:
                    st.sidebar.info("✨ **Custom Chapter**: Mixed chapters allowed.")
                else:
                    st.sidebar.info("✨ **Proxy Mode Active**: Chapter/Legion restrictions bypassed.")
            else:
                st.sidebar.error("☢️ **Chapter Mismatch Found**")
                for _, row in mismatches.iterrows():
                    st.sidebar.warning(f"{row['unit_name']} (Native Chapter Mismatch)")

        if not violations.empty:
            st.sidebar.error("🚨 **Rule Violations**")
            for _, row in violations.iterrows():
                st.sidebar.warning(f"**{row['unit_name']}**: {int(row['times_taken'])}/{int(row['max_allowed'])}")

        if enh_over:
            st.sidebar.error("🚨 **Enhancements**: Max 3 enhancements per army.")
        if enh_dupe:
            st.sidebar.error("🚨 **Enhancements**: Each enhancement can only be taken once.")

        if not has_character:
            st.sidebar.warning("⚠️ **Warlord**: List must include at least one Character.")

        st.sidebar.caption("Wargear: slot/count limits are not validated.")

        is_battle_ready = (
            violations.empty and (mismatches.empty or allow_mixed_chapters)
            and not enh_over and not enh_dupe and has_character
        )
        if is_battle_ready:
            st.sidebar.success("🛡️ Army is Battle-Ready")


def _build_40k_list_export_text(active_list, total_pts, roster_df):
    """Build plain-text export of the roster (list name, points, per-unit lines with wargear)."""
    lines = []
    lines.append(active_list.get("list_name") or "40K List")
    lines.append("")
    lines.append(f"Faction: {active_list.get('faction_primary') or '—'}")
    lines.append(f"Points: {total_pts} / {active_list.get('point_limit') or 2000}")
    lines.append("")
    if roster_df is None or roster_df.empty:
        lines.append("(No units)")
        return "\n".join(lines)
    for _, row in roster_df.iterrows():
        unit = row.get("Unit") or row.get("unit") or "—"
        qty = row.get("Qty") or row.get("quantity") or 1
        pts = row.get("Total_Pts") or row.get("Total_Pts") or 0
        wg = row.get("wargear_list")
        wg_str = ""
        if wg and str(wg).strip() and str(wg) != "[]":
            try:
                import json
                arr = json.loads(wg) if isinstance(wg, str) else wg
                if isinstance(arr, list):
                    wg_str = " | " + ", ".join(str(x) for x in arr if x and str(x).strip() and not str(x).strip().startswith("w2|"))
                else:
                    wg_str = " | " + str(wg)
            except Exception:
                wg_str = " | " + str(wg)
        lines.append(f"  {int(qty)}x {unit} — {pts} pts{wg_str}")
    return "\n".join(lines)


def _build_40k_list_export_ros_xml(active_list, total_pts, roster_df):
    """Build a minimal BattleScribe-style roster XML (for export; full .ros schema can be added later)."""
    import xml.etree.ElementTree as ET
    roster = ET.Element("roster")
    roster.set("name", (active_list.get("list_name") or "40K List").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    roster.set("gameSystemId", "wh40k-10e")
    roster.set("gameSystemName", "Warhammer 40,000 10th Edition")
    cost = ET.SubElement(roster, "costs")
    cost.set("name", "pts")
    cost.set("value", str(total_pts))
    forces = ET.SubElement(roster, "forces")
    force = ET.SubElement(forces, "force")
    force.set("name", (active_list.get("faction_primary") or "Army").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    if roster_df is not None and not roster_df.empty:
        for _, row in roster_df.iterrows():
            sel = ET.SubElement(force, "selection")
            unit = (row.get("Unit") or row.get("unit") or "Unit").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            sel.set("name", unit)
            sel.set("number", str(int(row.get("Qty") or row.get("quantity") or 1)))
            pts = row.get("Total_Pts") or row.get("Total_Pts") or 0
            c = ET.SubElement(sel, "cost")
            c.set("name", "pts")
            c.set("value", str(int(pts)))
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(roster, encoding="unicode", method="xml")


def show_points_summary(active_list, current_points):
    limit = active_list['point_limit']
    percent = min(current_points / limit, 1.0) if limit > 0 else 0
    st.sidebar.divider()
    st.sidebar.subheader("📊 Points Summary")
    st.sidebar.progress(percent, text=f"{current_points} / {limit} pts")
    if current_points > limit:
        st.sidebar.error(f"⚠️ Over limit by {current_points - limit} pts!")
    elif current_points == limit:
        st.sidebar.balloons()
        st.sidebar.success("🎯 Exactly on target!")

def _split_and_list(s):
    """Split '1 big shoota and 1 close combat weapon' or 'slugga and choppa' into list of items (strip leading 1/one)."""
    if not s or not s.strip():
        return []
    s = s.strip().strip('.').strip(',')
    # Split on ' and ' but not inside parentheticals
    parts = re.split(r"\s+and\s+", s, flags=re.IGNORECASE)
    out = []
    for p in parts:
        p = p.strip()
        # Drop leading "1 " or "one " so we get weapon name only
        p = re.sub(r"^(?:1|one)\s+", "", p, flags=re.IGNORECASE).strip()
        if p and len(p) > 1:
            out.append(p)
    return out


def parse_wargear_option(text):
    """
    Parse wargear option text into structured rule for UI and weapon counts.
    Returns: type in swap_1_1 | swap_multi | any_number | per_N_models | equipped_with | nested | simple,
    plus who (model type), removed, added; for per_N_models: every_N, slots_per_N, options;
    for equipped_with: added (list of one item), max (0..N).
    """
    if not text:
        return {"type": "none"}
    t = text.strip()
    # Normalize curly/smart apostrophes so "Boss Nob's" matches regex
    t = t.replace("\u2019", "'").replace("\u2018", "'")
    t_lower = t.lower()

    # --- "For every N models in this unit, 1 model equipped with X can be equipped with Y" (single or "one of the following")
    per_equipped = re.search(
        r"for\s+every\s+(\d+)\s+models\s+in\s+this\s+unit,?\s+1\s+model\s+equipped\s+with\s+(.+?)\s+can\s+be\s+equipped\s+with\s+(.+)",
        t_lower,
        re.IGNORECASE | re.DOTALL,
    )
    if per_equipped:
        every_N = int(per_equipped.group(1))
        removed_str = re.sub(r"^(?:a|an)\s+", "", per_equipped.group(2).strip().strip("."), flags=re.IGNORECASE).strip()
        rest = per_equipped.group(3).strip().strip(".")
        removed = _split_and_list(removed_str)
        if "one of the following" in rest:
            # Parse "one of the following: • 1 X • 1 Y"
            rest = re.split(r"one of the following\s*:\s*", rest, flags=re.IGNORECASE)[-1].strip()
            options_raw = re.split(r"\s+1\s+|\s+one\s+|\s*[•]\s*", rest)
            option_displays = []
            for o in options_raw:
                o = o.strip().strip(',').strip('.').strip()
                if len(o) > 2:
                    option_displays.append(o)
        else:
            # Single option: "1 Astartes grenade launcher"
            added_list = _split_and_list(rest)
            option_displays = [rest.strip()] if rest else []
            if added_list and not option_displays:
                option_displays = [" ".join(added_list)]
        if removed and option_displays:
            return {
                "type": "per_N_models",
                "who": "model",
                "every_N": every_N,
                "slots_per_N": 1,
                "removed": removed,
                "options": option_displays,
                "raw_options": option_displays,
            }

    # --- "For every N models in this unit, M ... can be replaced with one of the following: ..."
    per_match = re.search(
        r"for\s+every\s+(\d+)\s+models\s+in\s+this\s+unit,?\s+(?:1\s+)?(\w+)'s\s+(.+?)\s+can\s+be\s+replaced\s+with\s+one\s+of\s+the\s+following\s*:\s*(.+)",
        t_lower,
        re.IGNORECASE | re.DOTALL,
    )
    if per_match:
        every_N = int(per_match.group(1))
        who = per_match.group(2).strip()
        removed_str = per_match.group(3).strip()
        rest = per_match.group(4).strip()
        removed = _split_and_list(removed_str)
        # Parse options: "1 big shoota and 1 close combat weapon" / "1 rokkit launcha and 1 close combat weapon"
        options_raw = re.split(r"\s+1\s+|\s+one\s+", rest)
        fragments = []
        for o in options_raw:
            o = o.strip().strip(',').strip('.').replace("\n•", "").replace("•", "").strip()
            if len(o) > 2:
                fragments.append(o)
        # Pair consecutive fragments: "big shoota and" + "close combat weapon" -> "big shoota and close combat weapon"
        option_displays = []
        if len(fragments) >= 2:
            for i in range(0, len(fragments) - 1, 2):
                option_displays.append(fragments[i] + " " + fragments[i + 1])
        else:
            option_displays = [re.sub(r"^(?:1|one)\s+", "", o, flags=re.IGNORECASE).strip() for o in fragments if o]
        options_list = list(option_displays)
        return {
            "type": "per_N_models",
            "who": who,
            "every_N": every_N,
            "slots_per_N": 1,
            "removed": removed,
            "options": option_displays,
            "raw_options": options_list,
        }

    # --- "Any number of X can each have their Y and Z replaced with A and B"
    any_match = re.search(
        r"any\s+number\s+of\s+(.+?)\s+can\s+each\s+have\s+(?:their\s+)?(.+?)\s+replaced\s+with\s+(.+)",
        t_lower,
        re.IGNORECASE | re.DOTALL,
    )
    if any_match:
        who = any_match.group(1).strip()
        removed_str = any_match.group(2).strip()
        added_str = any_match.group(3).strip()
        removed = _split_and_list(removed_str)
        added = _split_and_list(added_str)
        return {"type": "any_number", "who": who, "removed": removed, "added": added}

    # --- "The X's A and B can be replaced with 1 C and 1 D" (multi swap); accept straight or curly apostrophe
    multi_swap = re.search(
        r"(?:the\s+)?(.+?)['\u2019]s\s+(.+?)\s+can\s+be\s+replaced\s+with\s+(.+)",
        t_lower,
        re.IGNORECASE | re.DOTALL,
    )
    if multi_swap:
        who = multi_swap.group(1).strip()
        left = multi_swap.group(2).strip()
        right = multi_swap.group(3).strip().strip('.')
        # --- "The X's A can be replaced with one of the following: • 1 B • 1 C" → nested (radio to pick which)
        if "one of the following" in right.lower():
            removed = _split_and_list(left)
            parts = re.split(r"one of the following\s*:\s*", right, flags=re.IGNORECASE)
            rest = (parts[-1].strip() if len(parts) > 1 else "").replace("\n", " ")
            options_list = []
            for frag in re.split(r"\s*[•]\s*", rest):
                frag = frag.strip().strip(',').strip('.').strip()
                if len(frag) > 2:
                    options_list.append(frag)
            if removed and options_list:
                return {"type": "nested", "target": removed[0] if len(removed) == 1 else left, "options": options_list}
        if " and " in left and (" and " in right or re.search(r"1\s+\w+", right)):
            removed = _split_and_list(left)
            added = _split_and_list(right)
            if len(removed) >= 1 and len(added) >= 1:
                return {"type": "swap_multi", "who": who, "removed": removed, "added": added}
        # --- "The X's A can be replaced with 1 B" (1:1 swap)
        removed = _split_and_list(left)
        added = _split_and_list(right)
        if len(removed) == 1 and len(added) == 1:
            return {"type": "swap_1_1", "who": who, "removed": removed[0], "added": added[0]}
        if len(removed) >= 1 and len(added) >= 1:
            return {"type": "swap_multi", "who": who, "removed": removed, "added": added}

    # --- Fallback: "model's X can be replaced with Y" (1:1)
    swap_match = re.search(
        r"(?:model's|unit's|this\s+model's?)\s+(.*?)\s+can\s+be\s+replaced\s+with\s+(?:1\s+)?(.*)",
        t,
        re.IGNORECASE,
    )
    if swap_match:
        target = swap_match.group(1).strip()
        replacement = swap_match.group(2).strip().strip(".")
        removed = _split_and_list(target)
        added = _split_and_list(replacement)
        if len(removed) == 1 and len(added) == 1:
            return {"type": "swap_1_1", "who": "Model", "removed": removed[0], "added": added[0]}
        if removed and added:
            return {"type": "swap_multi", "who": "Model", "removed": removed, "added": added}

    # --- "This model can be equipped with 1 X" / "with one X" / "with up to N X" (add optional wargear, no swap)
    equipped = re.search(
        r"this\s+model\s+can\s+be\s+equipped\s+with\s+(?:up\s+to\s+)?(?:1|one)\s+(.+?)(?:\.|$)",
        t_lower,
        re.IGNORECASE | re.DOTALL,
    )
    if equipped:
        item = equipped.group(1).strip().strip(".").strip()
        if len(item) > 1:
            return {"type": "equipped_with", "added": [item], "max": 1}
    equipped_n = re.search(
        r"this\s+model\s+can\s+be\s+equipped\s+with\s+up\s+to\s+(\d+)\s+(.+?)(?:\.|$)",
        t_lower,
        re.IGNORECASE | re.DOTALL,
    )
    if equipped_n:
        n = int(equipped_n.group(1))
        item = equipped_n.group(2).strip().strip(".").strip()
        if n >= 1 and len(item) > 1:
            return {"type": "equipped_with", "added": [item], "max": min(n, 10)}

    # Legacy: nested "one of the following" without "for every N models"
    if "one of the following:" in t_lower:
        parts = re.split(r"one of the following:", t, flags=re.IGNORECASE)
        header = parts[0]
        options_raw = re.split(r"\s1\s|\sone\s", parts[1])
        options_list = []
        for o in options_raw:
            cleaned = o.strip().strip(',').strip('.').replace("\n•", "").replace("•", "").strip()
            if len(cleaned) > 2:
                options_list.append(cleaned)
        target_match = re.search(r"(?:model's|unit's)\s+(.*?)\s+can be", header, re.IGNORECASE)
        target = target_match.group(1).strip() if target_match else "Equipment"
        return {"type": "nested", "target": target, "options": options_list}

    return {"type": "simple", "text": text}


def _compute_base_weapon_counts(loadout_text, quantity):
    """
    From default loadout text and unit quantity, return dict weapon_name -> count.
    First model line = 1 model (e.g. Boss Nob), rest = quantity - 1 (e.g. Boyz).
    If the only line (or a line) is "Every model" / "Each model" equipped with X, that line counts as quantity.
    """
    model_weapons = _parse_loadout_to_model_weapons(loadout_text)
    if not model_weapons:
        return {}
    counts = {}
    for i, (model_label, weapons) in enumerate(model_weapons):
        label_lower = (model_label or "").strip().lower()
        if label_lower.startswith("every model") or label_lower.startswith("each model") or label_lower == "every model" or label_lower == "each model":
            n = max(0, quantity)
        else:
            n = 1 if i == 0 else max(0, quantity - 1)
        if i == 0 and quantity == 0 and not (label_lower.startswith("every model") or label_lower.startswith("each model")):
            n = 0
        for w in weapons:
            w = w.strip()
            if w:
                counts[w] = counts.get(w, 0) + n
    return counts


def _weapon_name_matches(a, b):
    """True if weapon names match for count updates (normalize and compare)."""
    def norm(x):
        if not x:
            return ""
        return re.sub(r"\s+", " ", str(x).strip().lower())
    return norm(a) == norm(b) or norm(b) in norm(a) or norm(a) in norm(b)


def _apply_wargear_to_counts(base_counts, options_with_parsed, selections, quantity):
    """
    Apply wargear selections to base weapon counts. selections: list of same length as options_with_parsed;
    each element is either an int (count for swap/any_number) or a list of choice strings (per slot for per_N_models).
    Returns new dict weapon_name -> count (copy, not mutate base_counts).
    """
    counts = dict(base_counts)
    for idx, (desc, parsed) in enumerate(options_with_parsed):
        if idx >= len(selections):
            continue
        sel = selections[idx]
        ptype = parsed.get("type")

        def subtract(weapons, n):
            for w in (weapons if isinstance(weapons, list) else [weapons]):
                for k in list(counts.keys()):
                    if _weapon_name_matches(k, w):
                        counts[k] = max(0, (counts.get(k, 0) - n))
                        break

        def add(weapons, n):
            for w in (weapons if isinstance(weapons, list) else [weapons]):
                key = w.strip()
                if key:
                    # Try to match existing key for consistency
                    for k in list(counts.keys()):
                        if _weapon_name_matches(k, w):
                            counts[k] = counts.get(k, 0) + n
                            break
                    else:
                        counts[key] = counts.get(key, 0) + n

        if ptype == "swap_1_1" and isinstance(sel, int) and sel > 0:
            subtract([parsed["removed"]], sel)
            add([parsed["added"]], sel)
        elif ptype == "swap_multi" and isinstance(sel, int) and sel > 0:
            subtract(parsed["removed"], sel)
            add(parsed["added"], sel)
        elif ptype == "any_number" and isinstance(sel, int) and sel > 0:
            subtract(parsed["removed"], sel)
            add(parsed["added"], sel)
        elif ptype == "per_N_models" and isinstance(sel, list):
            every_N = parsed.get("every_N") or 10
            slots = (quantity // every_N) * (parsed.get("slots_per_N") or 1)
            for choice in sel[:slots]:
                if not choice:
                    continue
                # choice is full option string e.g. "big shoota and close combat weapon"
                added_list = _split_and_list(choice)
                subtract(parsed["removed"], 1)
                add(added_list, 1)
        elif ptype == "nested" and isinstance(sel, str) and sel and sel != "Default":
            # Legacy nested: one choice for all slots
            added_list = _split_and_list(sel)
            subtract([parsed.get("target", "")], 1)
            add(added_list, 1)
        elif ptype == "equipped_with" and isinstance(sel, int) and sel > 0:
            add(parsed.get("added", []), sel)
    return counts


@st.dialog("40K Unit Details", width="large")
def show_40k_details(unit_id, entry_id=None, detachment_id=None, faction=None, game_system="40K_10E"):
    try:
        _show_40k_details_impl(unit_id, entry_id, detachment_id, faction, game_system)
    except Exception as e:
        st.error(f"Unit details error: {e}")
        import traceback
        with st.expander("Technical details", expanded=False):
            st.code(traceback.format_exc())


def _unit_role_from_keywords(keywords_str):
    """Derive a role label and sort order from keywords (Character, Epic Hero, Battleline, etc.). Returns (order_int, label)."""
    if not keywords_str:
        return (99, "Other")
    kw = (keywords_str if isinstance(keywords_str, str) else "").upper()
    if "EPIC HERO" in kw:
        return (0, "Epic Hero")
    if "CHARACTER" in kw:
        return (1, "Character")
    if "BATTLELINE" in kw:
        return (2, "Battleline")
    if "MONSTER" in kw:
        return (3, "Monster")
    if "VEHICLE" in kw:
        return (4, "Vehicle")
    if "TRANSPORT" in kw:
        return (5, "Transport")
    if "INFANTRY" in kw:
        return (6, "Infantry")
    if "BEAST" in kw:
        return (7, "Beast")
    return (99, "Other")


def _normalize_unit_id(unit_id):
    """Return a string ID that matches DB (strip 12345.0 -> 12345 so wargear/models queries find rows)."""
    if unit_id is None or (hasattr(unit_id, '__float__') and pd.isna(unit_id)):
        return None
    try:
        if isinstance(unit_id, float) and unit_id == int(unit_id):
            return str(int(unit_id))
        if isinstance(unit_id, (int, float)):
            return str(int(unit_id)) if unit_id == int(unit_id) else str(unit_id)
    except (ValueError, TypeError):
        pass
    s = str(unit_id).strip()
    if s.endswith('.0') and s[:-2].isdigit():
        return s[:-2]
    return s if s else None


def _show_40k_details_impl(unit_id, entry_id=None, detachment_id=None, faction=None, game_system="40K_10E"):
    """
    Use passed unit_id for template data; entry_id for instance data (enhancements, wargear choices).
    When opened from roster (entry_id set), resolve canonical datasheet_id from DB so wargear/options queries match.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # Roster path: resolve canonical id from entry so wargear/options use same id as DB (avoids type/format mismatch)
    if entry_id is not None:
        try:
            eid = int(entry_id)
            resolved = get_datasheet_id_for_entry(conn, eid)
            if resolved is not None:
                unit_id = resolved
        except (TypeError, ValueError):
            pass
    unit_id = _normalize_unit_id(unit_id)
    if unit_id is None:
        st.warning("No unit selected.")
        conn.close()
        return
    unit_id = str(unit_id).strip()
    if unit_id.endswith(".0") and unit_id[:-2].isdigit():
        unit_id = unit_id[:-2]
    details = None
    try:
        cursor.execute("SELECT * FROM view_40k_datasheet_complete WHERE ID = %s", (unit_id,))
        details = cursor.fetchone()
    except Exception as e:
        st.error(f"Could not load unit: {e}")
        try:
            cursor.execute("SELECT name FROM waha_datasheets WHERE waha_datasheet_id = %s", (unit_id,))
            row = cursor.fetchone()
            if row:
                st.write(f"Unit: **{row.get('name', unit_id)}**")
        except Exception:
            st.caption(f"Unit ID: {unit_id}")
        conn.close()
        return
    if not details:
        # Fallback: build from waha_datasheets (no model row required so Boyz etc. still show)
        try:
            cursor.execute("""
                SELECT d.waha_datasheet_id AS ID, d.name AS Unit_Name, d.points_cost AS Points, d.image_url AS Image,
                       f.name AS Faction
                FROM waha_datasheets d
                LEFT JOIN waha_factions f ON d.faction_id = f.id
                WHERE d.waha_datasheet_id = %s
                LIMIT 1
            """, (unit_id,))
            row = cursor.fetchone()
            if row:
                cursor.execute("SELECT movement AS M, toughness AS T, save_value AS Sv, wounds AS W, leadership AS Ld, oc AS OC, base_size AS Base FROM waha_datasheets_models WHERE datasheet_id = %s ORDER BY line_id ASC LIMIT 1", (unit_id,))
                m = cursor.fetchone()
                if m:
                    row.update(m)
                else:
                    for k in ('M', 'T', 'Sv', 'W', 'Ld', 'OC', 'Base'):
                        row.setdefault(k, None)
                cursor.execute("SELECT GROUP_CONCAT(keyword SEPARATOR ', ') AS kw FROM waha_datasheets_keywords WHERE datasheet_id = %s", (unit_id,))
                kw = cursor.fetchone()
                row['Keywords'] = (kw.get('kw') or '') if kw else ''
                # Normalize keys so dialog finds them (MySQL may return lowercase)
                details = {
                    'ID': row.get('ID') or row.get('id'),
                    'Unit_Name': row.get('Unit_Name') or row.get('unit_name') or row.get('name'),
                    'Faction': row.get('Faction') or row.get('faction'),
                    'Points': row.get('Points') if row.get('Points') is not None else row.get('points_cost'),
                    'Image': row.get('Image') or row.get('image'),
                    'Keywords': row.get('Keywords') or row.get('keywords') or '',
                    'M': row.get('M') or row.get('movement'),
                    'T': row.get('T') or row.get('toughness'),
                    'Sv': row.get('Sv') or row.get('save_value'),
                    'W': row.get('W') or row.get('wounds'),
                    'Ld': row.get('Ld') or row.get('leadership'),
                    'OC': row.get('OC') or row.get('oc'),
                    'Base': row.get('Base') or row.get('base_size'),
                }
        except Exception:
            pass
    if not details:
        st.warning("Unit not found in database.")
        try:
            cursor.execute("SELECT name FROM waha_datasheets WHERE waha_datasheet_id = %s", (unit_id,))
            row = cursor.fetchone()
            if row:
                st.write("**" + str(row.get('name', unit_id)) + "** not found. Check that the unit exists in `waha_datasheets` and that the ID matches.")
            else:
                st.caption(f"Unit ID: {unit_id}")
        except Exception:
            st.caption(f"Unit ID: {unit_id}")
        conn.close()
        return
    if details:
        # --- DYNAMIC VISUAL FETCH (V1.1 STABLE) ---
        # We only pull ONE image where is_default = 1 for this specific unit_id
        cursor.execute("""
            SELECT l.preview_url, l.name 
            FROM stl_library l
            JOIN stl_unit_links ul ON l.mmf_id = ul.mmf_id
            WHERE ul.unit_id = %s 
            AND ul.game_system = '40K_10E' 
            AND ul.is_default = 1
            LIMIT 1
        """, (unit_id,))
        default_stl = cursor.fetchone()

        col1, col2 = st.columns([0.3, 0.7])
        
        with col1:
            # Logic: If a default STL proxy exists, show it. Otherwise, fallback to Wahapedia image.
            if default_stl and default_stl['preview_url']:
                proxy_name = default_stl.get('name') or ''
                if str(proxy_name).strip() == '0':
                    proxy_name = ''
                elif str(proxy_name).startswith('0 ') and len(str(proxy_name)) > 2:
                    proxy_name = str(proxy_name)[2:].strip()
                st.image(default_stl['preview_url'], width="stretch", caption=f"Proxy: {proxy_name}" if proxy_name else "Proxy")
            else:
                img_url = details.get('Image') or details.get('image')
                if not img_url:
                    cursor.execute("SELECT image_url FROM waha_datasheets WHERE waha_datasheet_id = %s", (unit_id,))
                    row = cursor.fetchone()
                    if row and row.get('image_url'):
                        img_url = row['image_url']
                    if not img_url and str(unit_id).strip():
                        cursor.execute("SELECT image_url FROM waha_datasheets WHERE CAST(waha_datasheet_id AS CHAR) = %s", (str(unit_id).strip(),))
                        row = cursor.fetchone()
                        if row and row.get('image_url'):
                            img_url = row['image_url']
                if img_url:
                    st.image(img_url, width="stretch", caption="Datasheet image")
                else:
                    st.caption("No image for this unit.")
        # ------------------------------------------
        # Link unit + Choose STL for Roster
        st.divider()
        unit_name = details.get("Unit_Name") or details.get("unit_name") or "Unit"
        if str(unit_name).strip() == "0":
            unit_name = "Unit"
        elif str(unit_name).strip().startswith("0 ") and len(str(unit_name).strip()) > 2:
            unit_name = str(unit_name).strip()[2:].strip()
        with st.expander("🔗 Link unit to STL", expanded=False):
            render_inline_link_unit(unit_id, unit_name, game_system, army_label=str(faction or ""))
        if entry_id:
            render_roster_stl_section(entry_id, unit_id, unit_name, game_system, army_label=str(faction or ""))
        st.divider()

        with col2:
            st.subheader(unit_name)
            pts_val = details.get('Points') or details.get('points_cost')
            faction_val = details.get('Faction') or details.get('faction')
            kw_val = details.get('Keywords') or details.get('keywords')
            summary_parts = []
            if pts_val is not None and str(pts_val).strip() != '':
                summary_parts.append(f"**{pts_val} pts**")
            if faction_val:
                summary_parts.append(str(faction_val))
            if summary_parts:
                st.caption(" | ".join(summary_parts))
            if kw_val and str(kw_val).strip():
                st.caption(f"*Keywords:* {kw_val}")
            # Show chapter/subfaction if unit has a chapter-specific faction keyword (Space Marines)
            cursor.execute("""
                SELECT keyword FROM waha_datasheets_keywords
                WHERE datasheet_id = %s AND is_faction_keyword = 1
                AND keyword NOT IN ('Space Marines','Adeptus Astartes','Imperium','Chaos','Character','Infantry','Vehicle','Epic Hero','Battleline','Agents of the Imperium')
            """, (unit_id,))
            chapter_kw = [r["keyword"] for r in cursor.fetchall()]
            if chapter_kw:
                st.caption(f"**Chapter:** {', '.join(chapter_kw)}")
            
            # 1. Fetch stats using clean keys for Python logic
            cursor.execute("""
                SELECT name as Model, movement as M, toughness as T, 
                       save_value as Sv, inv_sv, inv_sv_descr, wounds as W, 
                       leadership as Ld, oc as OC 
                FROM waha_datasheets_models 
                WHERE datasheet_id = %s
            """, (unit_id,))
            models = cursor.fetchall()
            
            if models:
                stats_df = pd.DataFrame(models)
                # Drop internal/display-noise columns
                for drop in ('inv_sv_descr', 'line_id', 'datasheet_id'):
                    if drop in stats_df.columns:
                        stats_df = stats_df.drop(columns=[drop])
                # Show "—" instead of 0 or blank for stat columns (avoids confusing "0" in table)
                def _fmt(v):
                    if v is None or (isinstance(v, str) and str(v).strip() in ('', '-')): return '—'
                    if v == 0 or str(v) == '0': return '—'
                    return v
                for col in list(stats_df.columns):
                    if col.lower() in ('model', 'name'): continue
                    stats_df[col] = stats_df[col].apply(_fmt)
                # Sanitize Model column: strip stray "0" / "0 " prefix from names; show "—" if name is only "0"
                if "Model" in stats_df.columns:
                    def _model_display(name):
                        if name is None or (isinstance(name, str) and not name.strip()): return '—'
                        s = str(name).strip()
                        if s == '0': return '—'
                        if s.startswith('0 ') and len(s) > 2: return s[2:].strip()
                        return s
                    stats_df["Model"] = stats_df["Model"].apply(_model_display)
                st.dataframe(
                    stats_df,
                    hide_index=True,
                    width="stretch",
                    column_config={
                        "Model": st.column_config.TextColumn("Model", width="medium"),
                        "inv_sv": st.column_config.TextColumn("Inv Sv", help="Invulnerable Save")
                    }
                )

                # 3. Special Saves Note (sanitize model name: no leading "0" or standalone "0")
                def _model_label(m):
                    raw = m.get('Model') or m.get('model') or m.get('name') or ''
                    if not raw or str(raw).strip() == '' or str(raw).strip() == '0': return '—'
                    s = str(raw).strip()
                    if s.startswith('0 ') and len(s) > 2: s = s[2:].strip()
                    return s or '—'
                special_saves = [
                    f"**{_model_label(m)}**: {m.get('inv_sv') or '—'} ({m.get('inv_sv_descr') or 'No special rules'})"
                    for m in models if (m.get('inv_sv') or m.get('Inv Sv')) and str(m.get('inv_sv') or m.get('Inv Sv') or '').strip() not in ('', '-', 'None')
                ]
                
                if special_saves:
                    with st.expander("🛡️ Invulnerable Saves & Special Notes", expanded=True):
                        for note in special_saves:
                            st.caption(note)

            # Tabs inside col2 so all main content (header, stats, tabs) displays together in the dialog
            t1, t2, t3, t4, t5 = st.tabs(["⚔️ Weapons", "📜 Rules", "✨ Enhancements", "👥 Composition", "🎯 Stratagems"])
            with t1:
                # 0. Unit quantity (for "any number" max and "per N models" slots)
                unit_quantity = 10
                if entry_id is not None:
                    try:
                        cursor.execute("SELECT quantity FROM play_armylist_entries WHERE entry_id = %s", (entry_id,))
                        qrow = cursor.fetchone()
                        if qrow and qrow.get("quantity") is not None:
                            unit_quantity = int(qrow["quantity"])
                    except Exception:
                        unit_quantity = 10
                else:
                    try:
                        cursor.execute("SELECT min_size FROM view_40k_unit_composition WHERE datasheet_id = %s", (str(unit_id),))
                        srow = cursor.fetchone()
                        if srow and srow.get("min_size") is not None:
                            unit_quantity = int(srow["min_size"])
                    except Exception:
                        pass

                # 1. Default loadout and base weapon counts
                loadout_text = None
                try:
                    cursor.execute("SELECT loadout FROM waha_datasheets WHERE waha_datasheet_id = %s", (unit_id,))
                    row = cursor.fetchone()
                    if not row and str(unit_id).strip():
                        cursor.execute("SELECT loadout FROM waha_datasheets WHERE CAST(waha_datasheet_id AS CHAR) = %s", (str(unit_id).strip(),))
                        row = cursor.fetchone()
                    if row and row.get("loadout") and str(row.get("loadout")).strip():
                        loadout_text = str(row.get("loadout")).strip()
                        st.markdown("**Default loadout**")
                        st.caption(_loadout_to_display(loadout_text))
                        st.divider()
                except Exception:
                    pass

                base_counts = _compute_base_weapon_counts(loadout_text or "", unit_quantity)

                # 2. Load options and parse; load structured state (w2| or legacy)
                cursor.execute("SELECT description FROM waha_datasheets_options WHERE datasheet_id = %s", (str(unit_id),))
                options = cursor.fetchall()
                if not options and str(unit_id).strip():
                    cursor.execute("SELECT description FROM waha_datasheets_options WHERE CAST(datasheet_id AS CHAR) = %s", (str(unit_id).strip(),))
                    options = cursor.fetchall()

                options_descs = []
                options_parsed = []
                for opt in options:
                    desc = _strip_option_html(opt.get("description") or "")
                    if not desc:
                        continue
                    options_descs.append(desc)
                    options_parsed.append(parse_wargear_option(desc))

                selections = [0] * len(options_descs)
                for i in range(len(options_descs)):
                    p = options_parsed[i]
                    if p.get("type") == "per_N_models":
                        selections[i] = []
                    elif p.get("type") == "nested":
                        selections[i] = "Default"
                    else:
                        selections[i] = 0

                active_selections = []
                if entry_id is not None:
                    try:
                        cursor.execute("SELECT option_text FROM play_armylist_wargear_selections WHERE entry_id = %s", (entry_id,))
                        all_rows = cursor.fetchall()
                        for r in all_rows:
                            txt = (r.get("option_text") or "").strip()
                            if txt and not txt.startswith("w2|"):
                                active_selections.append(txt)
                    except Exception:
                        pass

                if entry_id is not None:
                    try:
                        cursor.execute("SELECT option_text FROM play_armylist_wargear_selections WHERE entry_id = %s AND option_text LIKE 'w2|%%'", (entry_id,))
                        w2_rows = cursor.fetchall()
                        if w2_rows:
                            for r in w2_rows:
                                txt = (r.get("option_text") or "").strip()
                                if not txt.startswith("w2|"):
                                    continue
                                parts = txt.split("|")
                                if len(parts) >= 3:
                                    try:
                                        idx = int(parts[1])
                                        if idx < len(selections):
                                            if len(parts) == 3:
                                                selections[idx] = int(parts[2])
                                            elif len(parts) >= 4:
                                                slot = int(parts[2])
                                                choice = "|".join(parts[3:])
                                                if isinstance(selections[idx], list):
                                                    while len(selections[idx]) <= slot:
                                                        selections[idx].append("")
                                                    selections[idx][slot] = choice
                                                else:
                                                    selections[idx] = [""] * (slot + 1)
                                                    selections[idx][slot] = choice
                                    except (ValueError, IndexError):
                                        pass
                        else:
                            for i, (desc, parsed) in enumerate(zip(options_descs, options_parsed)):
                                if parsed.get("type") == "nested":
                                    for o in (parsed.get("options") or []):
                                        if f"{parsed.get('target', '')} -> {o}" in active_selections:
                                            selections[i] = o
                                            break
                                    else:
                                        selections[i] = "Default"
                                elif parsed.get("type") in ("swap", "swap_1_1", "swap_multi"):
                                    selections[i] = 1 if desc in active_selections else 0
                                elif parsed.get("type") == "any_number":
                                    selections[i] = 1 if desc in active_selections else 0
                                elif parsed.get("type") == "per_N_models":
                                    selections[i] = []
                    except Exception:
                        pass

                def save_wargear_state(ent_id, new_selections, summary_str):
                    conn_cb = get_db_connection()
                    cur_cb = conn_cb.cursor()
                    try:
                        cur_cb.execute("DELETE FROM play_armylist_wargear_selections WHERE entry_id = %s", (ent_id,))
                        for idx, sel in enumerate(new_selections):
                            if isinstance(sel, list):
                                for slot, choice in enumerate(sel):
                                    cur_cb.execute(
                                        "INSERT INTO play_armylist_wargear_selections (entry_id, option_text, is_active) VALUES (%s, %s, 1)",
                                        (ent_id, f"w2|{idx}|{slot}|{choice}"),
                                    )
                            else:
                                cur_cb.execute(
                                    "INSERT INTO play_armylist_wargear_selections (entry_id, option_text, is_active) VALUES (%s, %s, 1)",
                                    (ent_id, f"w2|{idx}|{sel}"),
                                )
                        if summary_str:
                            cur_cb.execute(
                                "INSERT INTO play_armylist_wargear_selections (entry_id, option_text, is_active) VALUES (%s, %s, 1)",
                                (ent_id, summary_str[:500], 1),
                            )
                        conn_cb.commit()
                    finally:
                        cur_cb.close()
                        conn_cb.close()

                # Weapons chart and final count (always show, before wargear options)
                st.divider()
                final_counts = _apply_wargear_to_counts(base_counts, list(zip(options_descs, options_parsed)), selections, unit_quantity)
                st.markdown("**Weapons** (strikethrough = 0 models with this weapon at current loadout)")
                cursor.execute(
                    "SELECT name, range_val, attacks, bs_ws, ap, damage, description FROM waha_datasheets_wargear WHERE datasheet_id = %s ORDER BY name",
                    (str(unit_id),),
                )
                wargear_rows = cursor.fetchall()
                if not wargear_rows and str(unit_id).strip():
                    cursor.execute(
                        "SELECT name, range_val, attacks, bs_ws, ap, damage, description FROM waha_datasheets_wargear WHERE CAST(datasheet_id AS CHAR) = %s ORDER BY name",
                        (str(unit_id).strip(),),
                    )
                    wargear_rows = cursor.fetchall()
                display_data = []
                for w in wargear_rows:
                    name = w.get('name') or '—'
                    rv = w.get('range_val') or '—'
                    att = w.get('attacks') or '—'
                    bs = w.get('bs_ws') or '—'
                    ap = w.get('ap') or '—'
                    dmg = w.get('damage') or '—'
                    special = (w.get('description') or '').strip()
                    if special:
                        special = _strip_html(special)
                    count = 0
                    for wname, c in final_counts.items():
                        if _weapon_name_matches(wname, name):
                            count = c
                            break
                    if count == 0:
                        name, rv, att, bs, ap, dmg = f"~~{name}~~", f"~~{rv}~~", f"~~{att}~~", f"~~{bs}~~", f"~~{ap}~~", f"~~{dmg}~~"
                    else:
                        name = f"{name} (**{count}×**)"
                    display_data.append({"Weapon": name, "Range": rv, "A": att, "BS/WS": bs, "AP": ap, "D": dmg, "Special": special or "—"})
                for wname, c in final_counts.items():
                    if c == 0:
                        continue
                    if any(_weapon_name_matches(wname, w.get("name") or "") for w in wargear_rows):
                        continue
                    cursor.execute("SELECT name, range_val, attacks_val, ap_val, damage_val FROM waha_weapons WHERE LOWER(TRIM(name)) = LOWER(TRIM(%s))", (wname,))
                    nw = cursor.fetchone()
                    if nw:
                        display_data.append({
                            "Weapon": f"{nw.get('name', wname)} (**{c}×**)",
                            "Range": nw.get("range_val", "—"), "A": nw.get("attacks_val", "—"), "BS/WS": "---",
                            "AP": nw.get("ap_val", "—"), "D": nw.get("damage_val", "—"), "Special": "—",
                        })
                if display_data:
                    st.dataframe(pd.DataFrame(display_data), hide_index=True, width="stretch")
                st.markdown("**Final weapon count** (for dice rolls)")
                summary_parts = [f"{c}× {w}" for w, c in sorted(final_counts.items(), key=lambda x: (-x[1], x[0])) if c and c != 0]
                if summary_parts:
                    st.write(", ".join(summary_parts))
                else:
                    st.caption("Default loadout only (no options applied).")
                if not wargear_rows and not summary_parts:
                    st.info("No weapons or wargear in database for this unit. Load Wahapedia **Datasheets_wargear** (and **Datasheets_options**) for the Orks faction.")

                st.divider()
                if options_descs:
                    with st.expander("🔄 Wargear Options", expanded=True):
                        st.caption(f"Unit size: **{unit_quantity}** models. Set counts below.")
                        new_selections = list(selections)
                        for idx, (desc, parsed) in enumerate(zip(options_descs, options_parsed)):
                            ptype = parsed.get("type")
                            st.caption(desc)

                            if ptype == "swap_1_1":
                                current = new_selections[idx] if isinstance(new_selections[idx], int) else 0
                                n = st.number_input("How many have this swap?", min_value=0, max_value=1, value=current, key=f"wopt_{entry_id or unit_id}_{idx}")
                                if n != current and entry_id is not None:
                                    new_selections[idx] = n
                                    final = _apply_wargear_to_counts(base_counts, list(zip(options_descs, options_parsed)), new_selections, unit_quantity)
                                    summary = ", ".join(f"{c}× {w}" for w, c in sorted(final.items(), key=lambda x: (-x[1], x[0])) if c) or "Default"
                                    save_wargear_state(entry_id, new_selections, summary)
                                    st.rerun()

                            elif ptype == "swap_multi":
                                current = new_selections[idx] if isinstance(new_selections[idx], int) else 0
                                n = st.number_input("How many have this swap?", min_value=0, max_value=1, value=current, key=f"wopt_{entry_id or unit_id}_{idx}_m")
                                if n != current and entry_id is not None:
                                    new_selections[idx] = n
                                    final = _apply_wargear_to_counts(base_counts, list(zip(options_descs, options_parsed)), new_selections, unit_quantity)
                                    summary = ", ".join(f"{c}× {w}" for w, c in sorted(final.items(), key=lambda x: (-x[1], x[0])) if c) or "Default"
                                    save_wargear_state(entry_id, new_selections, summary)
                                    st.rerun()

                            elif ptype == "any_number":
                                current = new_selections[idx] if isinstance(new_selections[idx], int) else 0
                                n = st.number_input("How many have this swap?", min_value=0, max_value=unit_quantity, value=min(current, unit_quantity), key=f"wopt_{entry_id or unit_id}_{idx}_a")
                                if n != current and entry_id is not None:
                                    new_selections[idx] = n
                                    final = _apply_wargear_to_counts(base_counts, list(zip(options_descs, options_parsed)), new_selections, unit_quantity)
                                    summary = ", ".join(f"{c}× {w}" for w, c in sorted(final.items(), key=lambda x: (-x[1], x[0])) if c) or "Default"
                                    save_wargear_state(entry_id, new_selections, summary)
                                    st.rerun()

                            elif ptype == "per_N_models":
                                every_N = parsed.get("every_N") or 10
                                slots = (unit_quantity // every_N) * (parsed.get("slots_per_N") or 1)
                                opts = parsed.get("options") or []
                                opts_with_default = ["Default"] + opts
                                current_list = list(new_selections[idx]) if isinstance(new_selections[idx], list) else []
                                while len(current_list) < slots:
                                    current_list.append("")
                                current_list = current_list[:slots]
                                st.caption(f"Slots: **{slots}** (1 per {every_N} models). Choose for each slot (Default = no swap):")
                                for slot in range(slots):
                                    val = current_list[slot] or ""
                                    choice_idx = opts_with_default.index(val) if val in opts_with_default else 0
                                    sel = st.selectbox(f"Slot {slot + 1}", opts_with_default, index=min(choice_idx, len(opts_with_default) - 1), key=f"wopt_{entry_id or unit_id}_{idx}_{slot}")
                                    current_list[slot] = "" if sel == "Default" else sel
                                if entry_id is not None:
                                    prev_list = new_selections[idx] if isinstance(new_selections[idx], list) else []
                                    if current_list != prev_list:
                                        new_selections[idx] = current_list
                                        final = _apply_wargear_to_counts(base_counts, list(zip(options_descs, options_parsed)), new_selections, unit_quantity)
                                        summary = ", ".join(f"{c}× {w}" for w, c in sorted(final.items(), key=lambda x: (-x[1], x[0])) if c) or "Default"
                                        save_wargear_state(entry_id, new_selections, summary)
                                        st.rerun()

                            elif ptype == "nested":
                                opts = parsed.get("options") or []
                                target = parsed.get("target", "Equipment")
                                default_label = f"{target} (Default)"
                                radio_options = [default_label] + opts
                                current = new_selections[idx] if isinstance(new_selections[idx], str) else "Default"
                                current_display = default_label if current == "Default" else (current if current in radio_options else default_label)
                                choice_idx = radio_options.index(current_display) if current_display in radio_options else 0
                                choice = st.radio(f"Replace {target} with", radio_options, index=min(choice_idx, len(radio_options) - 1), key=f"wopt_{entry_id or unit_id}_{idx}_n")
                                new_val = "Default" if choice == default_label else choice
                                if new_val != current and entry_id is not None:
                                    new_selections[idx] = new_val
                                    final = _apply_wargear_to_counts(base_counts, list(zip(options_descs, options_parsed)), new_selections, unit_quantity)
                                    summary = ", ".join(f"{c}× {w}" for w, c in sorted(final.items(), key=lambda x: (-x[1], x[0])) if c) or "Default"
                                    save_wargear_state(entry_id, new_selections, summary)
                                    st.rerun()

                            elif ptype == "equipped_with":
                                max_val = parsed.get("max") or 1
                                current = new_selections[idx] if isinstance(new_selections[idx], int) else 0
                                n = st.number_input("How many equipped?", min_value=0, max_value=max_val, value=min(current, max_val), key=f"wopt_{entry_id or unit_id}_{idx}_eq")
                                if n != current and entry_id is not None:
                                    new_selections[idx] = n
                                    final = _apply_wargear_to_counts(base_counts, list(zip(options_descs, options_parsed)), new_selections, unit_quantity)
                                    summary = ", ".join(f"{c}× {w}" for w, c in sorted(final.items(), key=lambda x: (-x[1], x[0])) if c) or "Default"
                                    save_wargear_state(entry_id, new_selections, summary)
                                    st.rerun()

                            else:
                                st.caption("(Unsupported option type)")

            # --- TAB 2: RULES (ABILITIES) ---
            with t2:
                st.markdown("**ABILITIES**")
                # Show all ability types (Faction, Datasheet, Wargear, Special, etc.); ORDER by type then name. TRIM type so "Special " matches.
                cursor.execute("""
                    SELECT 
                        COALESCE(a.name, da.name) as ab_name, 
                        COALESCE(a.description, da.description) as ab_desc, 
                        da.type 
                    FROM waha_datasheets_abilities da 
                    LEFT JOIN waha_abilities a ON da.ability_id = a.id 
                    WHERE da.datasheet_id = %s 
                    ORDER BY CASE WHEN LOWER(TRIM(COALESCE(da.type,''))) = 'faction' THEN 0 WHEN LOWER(TRIM(COALESCE(da.type,''))) = 'datasheet' THEN 1 WHEN LOWER(TRIM(COALESCE(da.type,''))) = 'wargear' THEN 2 WHEN LOWER(TRIM(COALESCE(da.type,''))) LIKE 'special%' THEN 3 ELSE 4 END, ab_name ASC
                """, (unit_id,))
                unit_abilities = cursor.fetchall()
                if not unit_abilities:
                    cursor.execute("""
                        SELECT COALESCE(a.name, da.name) as ab_name, COALESCE(a.description, da.description) as ab_desc, da.type
                        FROM waha_datasheets_abilities da
                        LEFT JOIN waha_abilities a ON da.ability_id = a.id
                        WHERE CAST(da.datasheet_id AS CHAR) = %s
                        ORDER BY CASE WHEN LOWER(TRIM(COALESCE(da.type,''))) = 'faction' THEN 0 WHEN LOWER(TRIM(COALESCE(da.type,''))) = 'datasheet' THEN 1 WHEN LOWER(TRIM(COALESCE(da.type,''))) = 'wargear' THEN 2 WHEN LOWER(TRIM(COALESCE(da.type,''))) LIKE 'special%' THEN 3 ELSE 4 END, ab_name ASC
                    """, (str(unit_id).strip(),))
                    unit_abilities = cursor.fetchall()
                if unit_abilities:
                    for ab in unit_abilities:
                        ab_type = (ab.get('type') or '').strip()
                        name = _strip_html((ab.get('ab_name') or '').strip())
                        desc = _strip_option_html((ab.get('ab_desc') or "").strip())
                        if ab_type and ab_type.lower() == 'faction':
                            # Avoid "Unnamed Ability" when faction ability name is missing (e.g. not yet loaded from Abilities.csv)
                            label = name if name else "FACTION (army rule)"
                            st.markdown(f"**FACTION:** {label}")
                            if desc:
                                st.markdown(desc)
                        else:
                            display_name = name if name else "Unnamed Ability"
                            icon = "🔧" if ab_type and ab_type.lower() == 'wargear' else "📜"
                            st.markdown(f"**{icon} {display_name}**: {desc}" if desc else f"**{icon} {display_name}**")
                else:
                    st.caption("No abilities found for this unit.")
                    st.caption("Load Wahapedia **Datasheets_abilities** for this faction to see abilities here.")

                _show_led_by_can_lead_transport(cursor, unit_id)

            with t3:
                keywords_str = (details.get("Keywords") or details.get("keywords") or "") if isinstance(details.get("Keywords") or details.get("keywords"), str) else ""
                kw_lower = keywords_str.lower()
                is_character = "character" in kw_lower
                is_epic = "epic hero" in kw_lower
                if is_character and not is_epic and detachment_id and entry_id:
                    MAX_ENHANCEMENTS_PER_ARMY = 3
                    st.write("### ✨ Available Enhancements")
                    cursor.execute("SELECT enhancement_id FROM play_armylist_enhancements WHERE entry_id = %s", (entry_id,))
                    this_model_enh = [r['enhancement_id'] for r in cursor.fetchall()]
                    cursor.execute("SELECT e.enhancement_id FROM play_armylist_enhancements e JOIN play_armylist_entries ent ON e.entry_id = ent.entry_id WHERE ent.list_id = (SELECT list_id FROM play_armylist_entries WHERE entry_id = %s)", (entry_id,))
                    all_used_enhs = [r['enhancement_id'] for r in cursor.fetchall()]
                    army_enhancement_count = len(all_used_enhs)
                    at_army_cap = army_enhancement_count >= MAX_ENHANCEMENTS_PER_ARMY
                    st.caption(f"Enhancements: **{army_enhancement_count} / {MAX_ENHANCEMENTS_PER_ARMY}** (max per army)")
                    cursor.execute("""
                        SELECT * FROM view_40k_enhancement_picker
                        WHERE detachment_id = %s OR CAST(detachment_id AS CHAR) = %s
                    """, (detachment_id, str(detachment_id)))
                    available_enhs = cursor.fetchall()
                    if not available_enhs:
                        st.info("No enhancements found for this detachment. Ensure a detachment is selected and enhancements are loaded in waha_enhancements.")
                    for enh in available_enhs:
                        is_on = enh['enhancement_id'] in this_model_enh
                        is_taken_elsewhere = enh['enhancement_id'] in all_used_enhs and not is_on
                        # Disable if: taken on another model, or (one enhancement per model and this model has one and we're trying to add), or at army cap and adding would exceed it
                        disabled = is_taken_elsewhere or (len(this_model_enh) > 0 and not is_on) or (at_army_cap and not is_on)
                        label = f"{enh['enhancement_name']} (+{enh['cost']} pts)"
                        if is_taken_elsewhere: label += " 🚫 (Taken)"
                        if at_army_cap and not is_on and not is_taken_elsewhere: label += " 🚫 (Army at 3 enhancements)"
                        chosen = st.checkbox(label, value=is_on, disabled=disabled, key=f"enh_{enh['enhancement_id']}_{entry_id}")
                        # Persist on change: write to DB first, then commit and rerun so next run shows correct state
                        if not disabled and chosen != is_on:
                            if chosen:
                                cursor.execute("INSERT INTO play_armylist_enhancements (entry_id, enhancement_id, cost) VALUES (%s, %s, %s)", (entry_id, enh['enhancement_id'], enh['cost']))
                            else:
                                cursor.execute("DELETE FROM play_armylist_enhancements WHERE entry_id = %s AND enhancement_id = %s", (entry_id, enh['enhancement_id']))
                            conn.commit()
                            st.rerun()
                        st.caption(enh['description'])
                elif is_epic:
                    st.warning("🚫 Epic Heroes cannot take Enhancements.")
                else:
                    st.info("💡 Only non-Epic Hero Characters can take Enhancements.")

            with t4:
                cursor.execute("""
                    SELECT c.description, m.base_size, m.base_size_descr
                    FROM waha_datasheet_unit_composition c
                    LEFT JOIN waha_datasheets_models m ON c.datasheet_id = m.datasheet_id AND c.line_id = m.line_id
                    WHERE c.datasheet_id = %s ORDER BY c.line_id ASC
                """, (unit_id,))
                comp_list = cursor.fetchall()
                if not comp_list and str(unit_id).strip():
                    cursor.execute("""
                        SELECT c.description, m.base_size, m.base_size_descr
                        FROM waha_datasheet_unit_composition c
                        LEFT JOIN waha_datasheets_models m ON c.datasheet_id = m.datasheet_id AND c.line_id = m.line_id
                        WHERE CAST(c.datasheet_id AS CHAR) = %s ORDER BY c.line_id ASC
                    """, (str(unit_id).strip(),))
                    comp_list = cursor.fetchall()
                if comp_list:
                    for comp in comp_list:
                        desc = comp.get('description', '') or ''
                        base = (comp.get('base_size') or comp.get('base_size_descr') or '').strip()
                        if base:
                            desc = f"{desc} — {_strip_html(str(base))}"
                        st.write(f"• {desc}")
                else:
                    st.info("No composition data in database. Load Wahapedia **Datasheets_unit_composition** for this unit.")

            with t5:
                cursor.execute("SELECT keyword FROM waha_datasheets_keywords WHERE datasheet_id = %s", (unit_id,))
                unit_keywords = [(row.get('keyword') or '').upper() for row in cursor.fetchall()]
                st.write(f"🏷️ Keywords: `{'`, `'.join(unit_keywords)}`")
                phase_filter = st.selectbox("Filter by Phase", 
                                            ["All Phases", "Command phase", "Movement phase", "Shooting phase", "Fight phase", "Any phase"],
                                            key=f"strat_phase_{unit_id}")
                # Load detachment stratagems + Core stratagems (empty detachment_id or type containing 'Core' in export)
                all_strats = []
                try:
                    if detachment_id is not None:
                        cursor.execute("""
                            SELECT name, cp_cost, type, phase, description 
                            FROM waha_stratagems 
                            WHERE detachment_id = %s OR CAST(detachment_id AS UNSIGNED) = %s
                        """, (detachment_id, detachment_id))
                        all_strats = list(cursor.fetchall())
                    # Add Core stratagems (available to all; in export they have empty faction_id/detachment_id or type like 'Core – ...')
                    cursor.execute("""
                        SELECT name, cp_cost, type, phase, description 
                        FROM waha_stratagems 
                        WHERE (detachment_id IS NULL OR TRIM(COALESCE(detachment_id,'')) = '' OR type LIKE %s)
                    """, ("%Core%",))
                    core_rows = cursor.fetchall()
                    seen_keys = {(_normalize_stratagem_name_for_key(s.get("name") or ""), s.get("cp_cost")) for s in all_strats}
                    for s in core_rows:
                        k = (_normalize_stratagem_name_for_key(s.get("name") or ""), s.get("cp_cost"))
                        if k not in seen_keys:
                            seen_keys.add(k)
                            all_strats.append(s)
                except Exception:
                    pass
                found_any = False
                faction_upper = (faction or '').upper()
                for s in all_strats:
                    desc_upper = (s.get('description') or '').upper()
                    name_upper = (s.get('name') or '').upper()
                    phase_match = (phase_filter == "All Phases" or phase_filter.lower() in (s.get('phase') or '').lower())
                    target_section = desc_upper[:250]
                    is_relevant = any(k in target_section for k in unit_keywords) or \
                                  f"{faction_upper} UNIT" in target_section or \
                                  "ANY UNIT" in target_section
                    if "VEHICLE" in target_section and "VEHICLE" not in unit_keywords:
                        is_relevant = False
                    if "INFANTRY" in target_section and "INFANTRY" not in unit_keywords:
                        is_relevant = False
                    if "MONSTER" in target_section and "MONSTER" not in unit_keywords:
                        is_relevant = False
                    if "TRANSPORT" in target_section and "TRANSPORT" not in unit_keywords:
                        is_relevant = False
                    if "CHARACTER UNIT" in target_section and "CHARACTER" not in unit_keywords:
                        is_relevant = False
                    if "EXCLUDING EPIC HERO" in target_section and "EPIC HERO" in unit_keywords:
                        is_relevant = False
                    gated_checks = ["SMOKE", "GRENADES", "FLY", "PSYKER", "STEALTH"]
                    for gk in gated_checks:
                        if f" {gk} " in target_section and gk not in unit_keywords:
                            is_relevant = False
                    if name_upper == "CAREEN!" and "VEHICLE" not in unit_keywords:
                        is_relevant = False
                    if is_relevant and phase_match:
                        found_any = True
                        with st.expander(f"🎯 **{s.get('name', '')}** — {s.get('cp_cost', 0)}CP", expanded=False):
                            st.caption(f"*{s.get('type', '')} - {s.get('phase', '')}*")
                            st.markdown(_format_stratagem_description(s.get('description') or ''))
                if not found_any:
                    st.info(f"No {phase_filter} stratagems found for this unit.")



    conn.close()

#Gameday view pt 5/7
#---- Gameday Printer Friendly View  - Includes expanders for each section ----

def _gameday_unit_labels(roster_df):
    """Return dict entry_id -> 'UnitName X' (e.g. 'Warboss A', 'Boyz B') by roster order."""
    if roster_df is None or roster_df.empty:
        return {}
    labels = {}
    counts = {}
    col_eid = "entry_id" if "entry_id" in roster_df.columns else "Entry_ID"
    col_unit = "Unit"
    for _, r in roster_df.iterrows():
        eid = r.get(col_eid)
        if eid is None or (hasattr(eid, "__float__") and pd.isna(eid)):
            continue
        try:
            eid_int = int(eid)
        except (TypeError, ValueError):
            continue
        name = (r.get(col_unit) or "Unit").strip() or "Unit"
        counts[name] = counts.get(name, 0) + 1
        letter = chr(ord("A") + counts[name] - 1) if counts[name] <= 26 else str(counts[name])
        labels[eid_int] = f"{name} {letter}"
    return labels


def _gameday_build_groups(roster_df):
    """Build list of (leader_row or None, bodyguard_row). Pairs (leader+bodyguard) first by bodyguard entry_id, then solos by entry_id."""
    if roster_df is None or roster_df.empty:
        return []
    col_eid = "entry_id" if "entry_id" in roster_df.columns else "Entry_ID"
    col_att = "attached_to_entry_id"
    if col_att not in roster_df.columns:
        return [(None, r) for _, r in roster_df.iterrows()]

    def _eid(r):
        v = r.get(col_eid)
        if v is None or (hasattr(v, "__float__") and pd.isna(v)):
            return None
        try:
            return int(v)
        except (TypeError, ValueError):
            return None

    used = set()
    pairs = []
    for _, r in roster_df.iterrows():
        eid = _eid(r)
        if eid is None or eid in used:
            continue
        att = r.get(col_att)
        if att is None or (hasattr(att, "__float__") and pd.isna(att)):
            continue
        try:
            att_int = int(att)
        except (TypeError, ValueError):
            continue
        bodyguard_row = None
        for _, r2 in roster_df.iterrows():
            if _eid(r2) == att_int:
                bodyguard_row = r2
                break
        if bodyguard_row is not None:
            pairs.append((r, bodyguard_row))
            used.add(eid)
            used.add(att_int)
    solos = [(None, r) for _, r in roster_df.iterrows() if _eid(r) not in used]
    return pairs + solos


def _render_gameday_unit_card(conn, cursor, row, active_list, roster_df=None, unit_label=None):
    """Render one unit's data card. Uses canonical datasheet_id for all lookups (from row or resolved from entry_id). roster_df used for leader/bodyguard labels. unit_label e.g. 'Boyz A' for numbering."""
    entry_id = row.get("entry_id") or row.get("Entry_ID")
    qty = row.get("Qty", 1)
    unit_name = row.get("Unit", "Unit")
    if unit_label:
        unit_name = unit_label
    total_pts = row.get("Total_Pts", 0)
    datasheet_id = row.get("datasheet_id")
    if datasheet_id is None or (hasattr(datasheet_id, "__float__") and pd.isna(datasheet_id)):
        datasheet_id = row.get("unit_id") or row.get("Unit_ID")
    # Resolve canonical id from DB when we have entry_id (same as unit details dialog)
    if entry_id is not None:
        try:
            resolved = get_datasheet_id_for_entry(conn, int(entry_id))
            if resolved is not None:
                datasheet_id = resolved
        except (TypeError, ValueError):
            pass
    if datasheet_id is not None:
        datasheet_id = str(datasheet_id).strip()
        if datasheet_id.endswith(".0") and datasheet_id[:-2].isdigit():
            datasheet_id = datasheet_id[:-2]
    sid = (datasheet_id or "").strip()
    leading_unit_name = None
    led_by_leader_name = None
    if roster_df is not None and not roster_df.empty and entry_id is not None:
        try:
            eid_val = int(entry_id) if not (hasattr(entry_id, "__float__") and pd.isna(entry_id)) else None
        except (TypeError, ValueError):
            eid_val = None
        if eid_val is not None:
            attached_to = row.get("attached_to_entry_id")
            if attached_to is not None and not (hasattr(attached_to, "__float__") and pd.isna(attached_to)):
                for _, r in roster_df.iterrows():
                    if (r.get("entry_id") or r.get("Entry_ID")) == attached_to:
                        leading_unit_name = r.get("Unit", "Unit")
                        break
            for _, r in roster_df.iterrows():
                if (r.get("attached_to_entry_id") or None) == eid_val:
                    led_by_leader_name = r.get("Unit", "Leader")
                    break
    with st.expander(f"**{qty}x {unit_name}** ({total_pts} pts)", expanded=False):
        _render_gameday_unit_content(conn, cursor, row, active_list, roster_df, sid, entry_id, led_by_leader_name, leading_unit_name)


def _render_gameday_unit_content(conn, cursor, row, active_list, roster_df, sid, entry_id, led_by_leader_name=None, leading_unit_name=None):
    """Render the inner content of one unit card (stats, loadout, enhancement, weapons, abilities, stratagems). Used for single cards and for each half of a group card."""
    if not sid:
        st.caption("Unit not linked to datasheet. Remove and re-add this unit from the library.")
        return
    if led_by_leader_name:
        st.caption(f"👤 **Led by:** {led_by_leader_name}")
    if leading_unit_name:
        st.caption(f"👤 **Leading:** {leading_unit_name}")
    # Chosen weapon/wargear options (from roster)
    wg_list = row.get("wargear_list")
    if wg_list and str(wg_list).strip() and str(wg_list) != "[]":
        try:
            import json
            opts = json.loads(wg_list)
            if isinstance(opts, list) and opts:
                st.caption(f"🔧 **Chosen loadout:** {', '.join(str(x) for x in opts)}")
        except Exception:
            if isinstance(wg_list, str) and wg_list.strip():
                st.caption(f"🔧 **Chosen loadout:** {wg_list}")
    # Enhancement (from DB for this entry)
    if entry_id is not None:
        try:
            eid = int(entry_id) if not (hasattr(entry_id, "__float__") and pd.isna(entry_id)) else None
            if eid is not None:
                cursor.execute("""
                    SELECT e.name, e.description, ple.cost
                    FROM play_armylist_enhancements ple
                    JOIN waha_enhancements e ON ple.enhancement_id = e.id
                    WHERE ple.entry_id = %s
                """, (eid,))
                equipped_enh = cursor.fetchone()
                if equipped_enh:
                    st.caption(f"✨ **Enhancement:** {equipped_enh.get('name', '')} (+{equipped_enh.get('cost', 0)} pts)")
        except (TypeError, ValueError):
            pass
    def _query_id(q, param):
        cursor.execute(q, (param,))
        out = cursor.fetchall()
        if not out and param and "CAST(" not in q:
            fallback = q.replace(" datasheet_id = %s", " CAST(datasheet_id AS CHAR) = %s").replace("da.datasheet_id = %s", "CAST(da.datasheet_id AS CHAR) = %s")
            if fallback != q:
                cursor.execute(fallback, (str(param).strip(),))
                out = cursor.fetchall()
        return out
    # A. Stats Table
    cursor.execute("SELECT name as Model, movement as M, toughness as T, save_value as Sv, wounds as W, leadership as Ld, oc as OC FROM waha_datasheets_models WHERE datasheet_id = %s", (sid,))
    models = cursor.fetchall()
    if not models:
        cursor.execute("SELECT name as Model, movement as M, toughness as T, save_value as Sv, wounds as W, leadership as Ld, oc as OC FROM waha_datasheets_models WHERE CAST(datasheet_id AS CHAR) = %s", (sid,))
        models = cursor.fetchall()
    if models:
        st.dataframe(pd.DataFrame(models), hide_index=True, width="stretch")
    # B. Unit Composition (with base size per line)
    with st.expander("👥 Unit Composition", expanded=False):
        comp_list = _query_id("""
            SELECT c.description, m.base_size, m.base_size_descr
            FROM waha_datasheet_unit_composition c
            LEFT JOIN waha_datasheets_models m ON c.datasheet_id = m.datasheet_id AND c.line_id = m.line_id
            WHERE c.datasheet_id = %s ORDER BY c.line_id ASC
        """, sid)
        if comp_list:
            for c in comp_list:
                desc = (c.get('description') or '').strip()
                base = (c.get('base_size') or c.get('base_size_descr') or '').strip()
                if base:
                    desc = f"{desc} — {_strip_html(str(base))}"
                st.write(f"• {desc}")
        else:
            st.caption("No composition data for this unit.")
    w_col, ra_col = st.columns([0.45, 0.55])
    with w_col:
        with st.expander("⚔️ Weapons", expanded=True):
            loadout = _query_id("SELECT loadout FROM waha_datasheets WHERE waha_datasheet_id = %s", sid)
            if loadout and loadout[0].get("loadout") and str(loadout[0].get("loadout")).strip():
                st.caption("**Default loadout:**\n\n" + _loadout_to_display(str(loadout[0].get("loadout")).strip()))
            wargear = _query_id("SELECT name, range_val, attacks, bs_ws, ap, damage, description FROM waha_datasheets_wargear WHERE datasheet_id = %s ORDER BY name", sid)
            if wargear:
                rows = []
                for w in wargear:
                    special = (w.get("description") or "").strip()
                    if special:
                        special = _strip_html(special)
                    rows.append({
                        **{k: w.get(k) or "—" for k in ("name", "range_val", "attacks", "bs_ws", "ap", "damage")},
                        "Special": special or "—",
                    })
                st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
            else:
                st.caption("No weapons/wargear data for this unit.")
    with ra_col:
        if entry_id is not None:
            try:
                eid = int(entry_id)
                cursor.execute("""
                    SELECT e.name, e.description, ple.cost 
                    FROM play_armylist_enhancements ple
                    JOIN waha_enhancements e ON ple.enhancement_id = e.id
                    WHERE ple.entry_id = %s
                """, (eid,))
                equipped_enh = cursor.fetchone()
            except (TypeError, ValueError):
                equipped_enh = None
            if equipped_enh:
                with st.expander(f"✨ Enhancement: {equipped_enh.get('name', '')} (+{equipped_enh.get('cost', 0)} pts)", expanded=True):
                    st.write(equipped_enh.get('description') or '')
        with st.expander("📜 Abilities", expanded=False):
            ab_list = _query_id(
                "SELECT COALESCE(a.name, da.name) as ab_name, COALESCE(a.description, da.description) as ab_desc, da.type FROM waha_datasheets_abilities da LEFT JOIN waha_abilities a ON da.ability_id = a.id WHERE da.datasheet_id = %s ORDER BY CASE WHEN LOWER(TRIM(COALESCE(da.type,''))) = 'faction' THEN 0 WHEN LOWER(TRIM(COALESCE(da.type,''))) = 'datasheet' THEN 1 WHEN LOWER(TRIM(COALESCE(da.type,''))) = 'wargear' THEN 2 WHEN LOWER(TRIM(COALESCE(da.type,''))) LIKE 'special%' THEN 3 ELSE 4 END, ab_name",
                sid,
            )
            if ab_list:
                for ab in ab_list:
                    ab_type = (ab.get('type') or '').strip()
                    name = _strip_html(ab.get('ab_name') or '')
                    desc = _strip_option_html((ab.get('ab_desc') or '').strip())
                    if ab_type and ab_type.lower() == 'faction':
                        st.markdown(f"**FACTION:** {name}")
                        if desc:
                            st.markdown(desc)
                    else:
                        st.markdown(f"**{name}**: {desc}" if desc else f"**{name}**")
            else:
                st.caption("No abilities data for this unit.")
        with st.expander("👥 Led By / Can Lead / Transport", expanded=False):
            _show_led_by_can_lead_transport(cursor, sid)
        with st.expander("🎯 Relevant Stratagems", expanded=False):
            try:
                kw_rows = _query_id("SELECT keyword FROM waha_datasheets_keywords WHERE datasheet_id = %s", sid)
                unit_keywords = [str(k.get('keyword', '')).upper() for k in (kw_rows or [])]
                det_id = active_list.get('waha_detachment_id')
                strats = []
                if det_id is not None:
                    cursor.execute("""
                        SELECT name, cp_cost, type, phase, description FROM waha_stratagems
                        WHERE detachment_id = %s OR CAST(detachment_id AS UNSIGNED) = %s
                    """, (det_id, det_id))
                    strats = list(cursor.fetchall())
                cursor.execute("""
                    SELECT name, cp_cost, type, phase, description FROM waha_stratagems
                    WHERE (detachment_id IS NULL OR TRIM(COALESCE(detachment_id,'')) = '' OR type LIKE %s)
                """, ("%Core%",))
                core_rows = cursor.fetchall()
                seen_keys = {(_normalize_stratagem_name_for_key(s.get("name") or ""), s.get("cp_cost")) for s in strats}
                for s in core_rows:
                    k = (_normalize_stratagem_name_for_key(s.get("name") or ""), s.get("cp_cost"))
                    if k not in seen_keys:
                        seen_keys.add(k)
                        strats.append(s)
                strats = _dedupe_stratagems(strats)
                found_any = False
                faction_upper = (active_list.get('faction_primary') or '').upper()
                for s in strats:
                    desc = s.get('description') or ''
                    desc_upper = (desc or '').upper()[:250]
                    is_relevant = any(k in desc_upper for k in unit_keywords) or f"{faction_upper} UNIT" in desc_upper or "ANY UNIT" in desc_upper
                    if "VEHICLE" in desc_upper and "VEHICLE" not in unit_keywords:
                        is_relevant = False
                    if "INFANTRY" in desc_upper and "INFANTRY" not in unit_keywords:
                        is_relevant = False
                    if is_relevant:
                        found_any = True
                        st.markdown(f"**{s.get('name', '')}** ({s.get('cp_cost', 0)}CP)")
                        st.markdown(_format_stratagem_description(desc))
                        st.divider()
                if not found_any and strats:
                    st.caption("No stratagems filtered by unit keywords. Showing all detachment and Core stratagems:")
                    for s in strats:
                        st.markdown(f"**{s.get('name', '')}** ({s.get('cp_cost', 0)}CP)")
                        st.markdown(_format_stratagem_description(s.get('description') or ''))
                        st.divider()
                elif not strats:
                    st.caption("No stratagems loaded. Select a detachment for this list to see detachment and Core stratagems.")
            except Exception:
                st.caption("Could not load stratagems.")


def _resolve_row_datasheet_and_attachment(conn, row, roster_df):
    """Return (sid, entry_id, led_by_name, leading_name) for a roster row."""
    entry_id = row.get("entry_id") or row.get("Entry_ID")
    datasheet_id = row.get("datasheet_id")
    if datasheet_id is None or (hasattr(datasheet_id, "__float__") and pd.isna(datasheet_id)):
        datasheet_id = row.get("unit_id") or row.get("Unit_ID")
    if entry_id is not None:
        try:
            resolved = get_datasheet_id_for_entry(conn, int(entry_id))
            if resolved is not None:
                datasheet_id = resolved
        except (TypeError, ValueError):
            pass
    if datasheet_id is not None:
        datasheet_id = str(datasheet_id).strip()
        if datasheet_id.endswith(".0") and datasheet_id[:-2].isdigit():
            datasheet_id = datasheet_id[:-2]
    sid = (datasheet_id or "").strip()
    led_by_leader_name = None
    leading_unit_name = None
    if roster_df is not None and not roster_df.empty and entry_id is not None:
        try:
            eid_val = int(entry_id) if not (hasattr(entry_id, "__float__") and pd.isna(entry_id)) else None
        except (TypeError, ValueError):
            eid_val = None
        if eid_val is not None:
            attached_to = row.get("attached_to_entry_id")
            if attached_to is not None and not (hasattr(attached_to, "__float__") and pd.isna(attached_to)):
                for _, r in roster_df.iterrows():
                    if (r.get("entry_id") or r.get("Entry_ID")) == attached_to:
                        leading_unit_name = r.get("Unit", "Unit")
                        break
            for _, r in roster_df.iterrows():
                if (r.get("attached_to_entry_id") or None) == eid_val:
                    led_by_leader_name = r.get("Unit", "Leader")
                    break
    return sid, entry_id, led_by_leader_name, leading_unit_name


def _render_gameday_group_card(conn, cursor, leader_row, bodyguard_row, active_list, roster_df, labels_map):
    """Render one expander for a leader+bodyguard pair with both units' content."""
    col_eid = "entry_id" if "entry_id" in leader_row else "Entry_ID"
    leader_eid = leader_row.get(col_eid)
    body_eid = bodyguard_row.get(col_eid)
    leader_label = labels_map.get(int(leader_eid) if leader_eid is not None else None) or leader_row.get("Unit", "Leader")
    body_label = labels_map.get(int(body_eid) if body_eid is not None else None) or bodyguard_row.get("Unit", "Unit")
    qty_l = leader_row.get("Qty", 1)
    qty_b = bodyguard_row.get("Qty", 1)
    pts_l = leader_row.get("Total_Pts", 0) or 0
    pts_b = bodyguard_row.get("Total_Pts", 0) or 0
    try:
        total_pts = int(float(pts_l)) + int(float(pts_b))
    except (TypeError, ValueError):
        total_pts = pts_l + pts_b
    title = f"**{qty_l}x {leader_label}** → **{qty_b}x {body_label}** ({total_pts} pts)"
    with st.expander(title, expanded=False):
        st.markdown(f"— **Leader:** {leader_label} —")
        sid_l, eid_l, led_by_l, leading_l = _resolve_row_datasheet_and_attachment(conn, leader_row, roster_df)
        _render_gameday_unit_content(conn, cursor, leader_row, active_list, roster_df, sid_l, eid_l, led_by_l, leading_l)
        st.divider()
        st.markdown(f"— **Unit:** {body_label} —")
        sid_b, eid_b, led_by_b, leading_b = _resolve_row_datasheet_and_attachment(conn, bodyguard_row, roster_df)
        _render_gameday_unit_content(conn, cursor, bodyguard_row, active_list, roster_df, sid_b, eid_b, led_by_b, leading_b)


def show_gameday_view(active_list, roster_df, total_pts):
    """A fully collapsible tactical sheet with a surgical stacked column layout."""
    st.title(f"📄 Tactical Briefing: {fix_apostrophe_mojibake(active_list['list_name'])}")
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 1. Top Controls
    c1, c2 = st.columns([0.7, 0.3])
    with c1:
        st.write(f"**{active_list['faction_primary']}** | **{total_pts} / {active_list['point_limit']} pts**")
    with c2:
        if st.button("⬅️ Back to Editor", width="stretch"):
            st.session_state.gameday_mode = False
            st.rerun()

    # 2. Army & Detachment Rules (Expandable)
    try:
        det_id = active_list.get('waha_detachment_id')
        if det_id is not None:
            cursor.execute("""
                SELECT DISTINCT army_rule_name, army_rule_desc, detachment_rule_name, detachment_rule_desc 
                FROM view_40k_army_rules 
                WHERE (faction_name = %s OR faction_id = (SELECT id FROM waha_factions WHERE name = %s))
                AND detachment_id = %s LIMIT 1
            """, (active_list['faction_primary'], active_list['faction_primary'], det_id))
            rules = cursor.fetchone()
        else:
            rules = None
    except Exception:
        rules = None

    if rules:
        with st.expander(f"📜 Army & Detachment Rules Summary", expanded=False):
            st.markdown(f"### 🛡️ Army Rule: {rules.get('army_rule_name', '')}")
            st.write(rules.get('army_rule_desc') or '')
            if rules.get('detachment_rule_name'):
                st.divider()
                st.markdown(f"### 🚩 Detachment Rule: {rules.get('detachment_rule_name', '')}")
                st.write(rules.get('detachment_rule_desc') or '')

    st.divider()

    # 3. Unit Entries (grouped: leader+bodyguard pairs, then solos; with unit labels A/B/C)
    if roster_df.empty:
        st.info("No units in list. Add units in the editor, then open Game-Day view again.")
    else:
        labels_map = _gameday_unit_labels(roster_df)
        groups = _gameday_build_groups(roster_df)
        for leader_row, bodyguard_row in groups:
            try:
                if leader_row is not None and bodyguard_row is not None:
                    _render_gameday_group_card(conn, cursor, leader_row, bodyguard_row, active_list, roster_df, labels_map)
                else:
                    row = bodyguard_row
                    col_eid = "entry_id" if "entry_id" in row else "Entry_ID"
                    eid = row.get(col_eid)
                    unit_label = labels_map.get(int(eid) if eid is not None else None) if eid is not None else None
                    _render_gameday_unit_card(conn, cursor, row, active_list, roster_df, unit_label=unit_label)
            except Exception as err:
                st.warning(f"Could not render unit card: {err}")
                row = bodyguard_row or leader_row
                qty = row.get('Qty', 1)
                unit = row.get('Unit', 'Unit')
                pts = row.get('Total_Pts', 0)
                with st.expander(f"**{qty}x {unit}** ({pts} pts)", expanded=True):
                    st.write(f"Error loading details for this unit.")

    conn.close()

#part 6/7

def _render_roster_row(row, list_id, active_list, active_det_id, cursor, conn, unit_chapter, is_space_marine, subfactions, roster_df=None, labels_map=None):
    """Render one roster row. Uses datasheet_id (from roster JOIN) for all lookups. roster_df for leader/bodyguard; labels_map for unit A/B/C labels."""
    entry_id = row.get("entry_id") or row.get("Entry_ID")
    unit_id = row.get("unit_id") or row.get("Unit_ID")
    datasheet_id = row.get("datasheet_id")  # canonical id from get_roster_40k JOIN
    if entry_id is None or (hasattr(entry_id, "__float__") and pd.isna(entry_id)):
        entry_id = None
    if unit_id is None or (hasattr(unit_id, "__float__") and pd.isna(unit_id)):
        unit_id = None
    lookup_id = datasheet_id if (datasheet_id is not None and str(datasheet_id).strip()) else (unit_id if unit_id is not None else None)
    try:
        eid_int = int(entry_id) if entry_id is not None and not (hasattr(entry_id, "__float__") and pd.isna(entry_id)) else None
    except (TypeError, ValueError):
        eid_int = None

    # Leader/bodyguard: who is leading this unit? (bodyguard -> leader row); for leaders, which unit they're attached to
    led_by_leader_row = None
    leading_unit_row = None  # for leader rows: the bodyguard unit they're attached to
    if roster_df is not None and not roster_df.empty and eid_int is not None and "attached_to_entry_id" in roster_df.columns:
        for _, r in roster_df.iterrows():
            aid = r.get("attached_to_entry_id")
            if aid is not None and not (hasattr(aid, "__float__") and pd.isna(aid)):
                try:
                    if int(aid) == eid_int:
                        led_by_leader_row = r  # this row (bodyguard) is led by leader row r
                except (TypeError, ValueError):
                    pass
        # This row is a leader with attached_to_entry_id set — find that bodyguard row for display
        cur_attached = row.get("attached_to_entry_id")
        if cur_attached is not None and not (hasattr(cur_attached, "__float__") and pd.isna(cur_attached)):
            try:
                want_eid = int(cur_attached)
                for _, r in roster_df.iterrows():
                    reid = r.get("entry_id") or r.get("Entry_ID")
                    if reid is not None and not (hasattr(reid, "__float__") and pd.isna(reid)) and int(reid) == want_eid:
                        leading_unit_row = r
                        break
            except (TypeError, ValueError):
                pass

    r_qty, r_main, r_view, r_del = st.columns([0.15, 0.65, 0.1, 0.1])
    with r_qty:
        min_sz, max_sz = 1, None
        if lookup_id is not None:
            try:
                cursor.execute("SELECT min_size, max_size FROM view_40k_unit_composition WHERE datasheet_id = %s", (str(lookup_id),))
                sizes = cursor.fetchone()
                if sizes:
                    min_sz = int(sizes['min_size']) if sizes.get('min_size') is not None else 1
                    raw_max = sizes.get('max_size')
                    max_sz = int(raw_max) if raw_max is not None and raw_max != '' else None
                    if max_sz is not None and max_sz == 0:
                        max_sz = min_sz
            except Exception:
                min_sz, max_sz = 1, None
        try:
            qty_val = row.get('Qty')
            if qty_val is not None and not (hasattr(qty_val, '__float__') and pd.isna(qty_val)):
                qty = int(float(qty_val))
            else:
                qty = min_sz
        except (ValueError, TypeError):
            qty = min_sz
        if max_sz is not None and max_sz > min_sz and entry_id is not None:
            is_max = (qty == max_sz)
            new_qty = max_sz if not is_max else min_sz
            if st.button(f"{qty} ({'Max' if is_max else 'Min'})", key=f"sz_{entry_id}_{list_id}"):
                cursor.execute("UPDATE play_armylist_entries SET quantity = %s WHERE entry_id = %s", (new_qty, entry_id))
                conn.commit()
                st.rerun()
        else:
            st.write(f"👤 {qty}")
    with r_main:
        chapter_badge = unit_chapter.get(lookup_id or unit_id) if (lookup_id or unit_id) is not None else None
        unit_display = (labels_map.get(eid_int) if (labels_map and eid_int is not None) else None) or row.get("Unit", "")
        st.write(f"**{unit_display}**" + (f" *({chapter_badge})*" if chapter_badge else ""))
        txt = f"{row.get('Total_Pts', 0)} pts"
        wg = row.get('wargear_list')
        if wg and str(wg).strip() != '' and str(wg) != '[]':
            try:
                import json
                txt += f" | 🔧 {', '.join(json.loads(wg))}"
            except Exception:
                pass
        st.caption(txt)
        if led_by_leader_row is not None:
            leader_name = led_by_leader_row.get("Unit", "Leader")
            st.caption(f"👤 **Led by:** {leader_name}")
        if leading_unit_row is not None:
            unit_name_leading = leading_unit_row.get("Unit", "Unit")
            st.caption(f"👤 **Attached to:** {unit_name_leading}")
        # Leader attach dropdown: valid bodyguard units in this list
        if lookup_id is not None and _is_leader(cursor, lookup_id) and roster_df is not None and not roster_df.empty and eid_int is not None:
            valid_ids = _valid_bodyguard_datasheet_ids(cursor, lookup_id)
            def _norm_dsid(v):
                if v is None or (hasattr(v, "__float__") and pd.isna(v)):
                    return ""
                s = str(v).strip()
                if s.endswith(".0") and s[:-2].isdigit():
                    s = s[:-2]
                return s
            options_entry_ids = [None]
            options_labels = ["— None —"]
            for _, r in roster_df.iterrows():
                try:
                    o_eid_raw = r.get("entry_id") or r.get("Entry_ID")
                    if o_eid_raw is not None and not (hasattr(o_eid_raw, "__float__") and pd.isna(o_eid_raw)) and int(o_eid_raw) == eid_int:
                        continue
                except (TypeError, ValueError):
                    pass
                other_dsid = _norm_dsid(r.get("datasheet_id") or r.get("unit_id"))
                if other_dsid and other_dsid in valid_ids:
                    o_eid = r.get("entry_id") or r.get("Entry_ID")
                    try:
                        o_eid_int = int(o_eid) if o_eid is not None and not (hasattr(o_eid, "__float__") and pd.isna(o_eid)) else None
                    except (TypeError, ValueError):
                        o_eid_int = None
                    if o_eid_int is not None:
                        o_qty = r.get("Qty", 1)
                        o_unit = r.get("Unit", "Unit")
                        try:
                            o_qty = int(float(o_qty)) if o_qty is not None else 1
                        except (TypeError, ValueError):
                            o_qty = 1
                        options_entry_ids.append(o_eid_int)
                        options_labels.append(f"{o_qty}x {o_unit}")
            current_attached = row.get("attached_to_entry_id")
            if current_attached is None or (hasattr(current_attached, "__float__") and pd.isna(current_attached)):
                current_attached = None
            else:
                try:
                    current_attached = int(current_attached)
                except (TypeError, ValueError):
                    current_attached = None
            try:
                current_idx = options_entry_ids.index(current_attached) if current_attached is not None else 0
            except ValueError:
                current_idx = 0
            sel = st.selectbox(
                "Attach to unit",
                range(len(options_labels)),
                index=current_idx,
                format_func=lambda i: options_labels[i],
                key=f"attach_{eid_int}_{list_id}",
            )
            new_attached = options_entry_ids[sel]
            if new_attached != current_attached:
                try:
                    cursor.execute(
                        "UPDATE play_armylist_entries SET attached_to_entry_id = %s WHERE entry_id = %s",
                        (new_attached, eid_int),
                    )
                    conn.commit()
                    st.rerun()
                except Exception:
                    pass
    with r_view:
        # Same pattern as OPR: pass (unit_id from row, entry_id from row). Row's datasheet_id = same id as library picker.
        if (lookup_id or unit_id) is not None and st.button("👁️", key=f"v_roster_{entry_id}_{list_id}"):
            uid = _normalize_unit_id(lookup_id or unit_id) or str(lookup_id or unit_id)
            try:
                eid = int(entry_id) if entry_id is not None and not (hasattr(entry_id, "__float__") and pd.isna(entry_id)) else None
            except (TypeError, ValueError):
                eid = None
            show_40k_details(uid, entry_id=eid, detachment_id=active_det_id, faction=active_list.get("faction_primary"), game_system="40K_10E")
    with r_del:
        if entry_id is not None and st.button("❌", key=f"d_{entry_id}"):
            cursor.execute("DELETE FROM play_armylist_entries WHERE entry_id = %s", (entry_id,))
            conn.commit()
            st.rerun()


# --- 2. MAIN BUILDER ---

def run_40k_builder(active_list):
    list_id = active_list['list_id']
    primary_army = active_list['faction_primary']
    active_det_id = active_list.get('waha_detachment_id')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # A. Roster fetch via JOIN so every row has canonical datasheet_id for lookups
    total_pts = 0
    cached_roster_df = pd.DataFrame()
    try:
        roster_rows = get_roster_40k(conn, list_id)
        if roster_rows:
            cached_roster_df = pd.DataFrame(roster_rows)
            total_pts = int(pd.to_numeric(cached_roster_df.get("Total_Pts", 0), errors="coerce").fillna(0).sum())
    except Exception as e:
        st.error(f"Could not load roster: {e}")
        cached_roster_df = pd.DataFrame()

    # B. Master Sidebar UI
    show_points_summary(active_list, total_pts)
    
    st.sidebar.divider()
    proxy_mode = st.sidebar.toggle("🔓 Proxy Mode (bypass all restrictions)", value=False,
                                   help="Bypass chapter and validation restrictions (e.g. narrative/proxy lists). For mixed chapters only, use 'Custom (mix chapters)' in Chapter instead.",
                                   key=f"proxy_master_{list_id}")

    show_40k_validation(list_id, proxy_mode=proxy_mode)
    
    st.sidebar.divider()
    
    # C. Detachment Selector
    cursor.execute("SELECT id FROM waha_factions WHERE name = %s", (primary_army,))
    f_res = cursor.fetchone()
    if f_res:
        cursor.execute("SELECT id, name FROM waha_detachments WHERE faction_id = %s", (f_res['id'],))
        dets = cursor.fetchall(); det_map = {d['name']: d['id'] for d in dets}
        if det_map:
            current_idx = 0
            if active_det_id:
                for i, name in enumerate(det_map.keys()):
                    if det_map[name] == active_det_id: current_idx = i
            sel_det = st.sidebar.selectbox("Select Detachment", list(det_map.keys()), index=current_idx, key=f"det_sel_{list_id}")
            if det_map[sel_det] != active_det_id:
                cursor.execute("UPDATE play_armylists SET waha_detachment_id = %s WHERE list_id = %s", (det_map[sel_det], list_id))
                conn.commit(); st.rerun()
            active_det_id = det_map[sel_det]

    # D. Subfaction Logic (Space Marine chapters: persist so validation and rules are chapter-aware)
    is_space_marine = (primary_army in ["Space Marines", "Adeptus Astartes"])
    library_subfaction = None
    subfactions = []
    saved_chapter = active_list.get("chapter_subfaction")  # from DB after migration
    if is_space_marine:
        exclude_list = [primary_army, 'Adeptus Astartes', 'Agents of the Imperium', 'Character', 'Infantry', 'Vehicle', 'Epic Hero', 'Battleline', 'Imperium']
        exclude_placeholders = ', '.join(['%s'] * len(exclude_list))
        cursor.execute(f"SELECT DISTINCT keyword FROM waha_datasheets_keywords dk JOIN waha_datasheets d ON dk.datasheet_id = d.waha_datasheet_id JOIN waha_factions f ON d.faction_id = f.id WHERE (f.name = %s OR f.id = 'SM') AND dk.keyword NOT IN ({exclude_placeholders}) AND dk.is_faction_keyword = 1", [primary_army] + exclude_list)
        subfactions = [f['keyword'] for f in cursor.fetchall()]
        if subfactions:
            options = ["Generic / All"] + sorted(subfactions) + ["Custom (mix chapters)"]
            try:
                if saved_chapter == CHAPTER_CUSTOM:
                    default_idx = options.index("Custom (mix chapters)")
                elif saved_chapter and saved_chapter in options:
                    default_idx = options.index(saved_chapter)
                else:
                    default_idx = 0
            except (ValueError, TypeError):
                default_idx = 0
            selected_sub = st.sidebar.selectbox("Select Chapter", options, index=min(default_idx, len(options) - 1), key=f"subfac_{list_id}", help="Generic = all faction units. Pick a chapter to filter. Custom = mix units from any chapter (e.g. successor/homebrew).")
            if selected_sub not in ("Generic / All", "Custom (mix chapters)"):
                library_subfaction = selected_sub
            # Persist so view_list_validation_40k and reloads use it; CUSTOM = allow mixed chapters
            new_chapter = CHAPTER_CUSTOM if selected_sub == "Custom (mix chapters)" else (selected_sub if selected_sub != "Generic / All" else None)
            if new_chapter != saved_chapter:
                try:
                    cursor.execute("UPDATE play_armylists SET chapter_subfaction = %s WHERE list_id = %s", (new_chapter, list_id))
                    conn.commit()
                    st.rerun()
                except Exception:
                    pass  # column may not exist until migration is run

    # E. Library Picker (deduped, grouped by role, paginated)
    st.sidebar.divider()
    st.sidebar.subheader("📚 Add from Library")
    allies = ['Imperial Agents', 'Imperial Knights'] if is_space_marine else []
    allow_allies = st.sidebar.toggle("Include Allied Units", value=False, key=f"ally_{list_id}") if allies else False
    search = st.sidebar.text_input("Search Units", key=f"search_{list_id}", placeholder="Search by unit name...")
    lib_limit = 500
    # view_master_picker: some DBs have game_system, others have system; try game_system first
    if proxy_mode:
        lib_query = f"SELECT * FROM view_master_picker WHERE game_system = '40K' AND (faction = %s {'OR faction IN (%s, %s)' if allow_allies else ''}) AND name LIKE %s ORDER BY name LIMIT {lib_limit}"
        params = [primary_army] + (allies if allow_allies else []) + [f"%{search}%"]
    elif library_subfaction:
        sub_placeholders = ', '.join(['%s'] * len(subfactions))
        lib_query = f"SELECT DISTINCT m.* FROM view_master_picker m WHERE m.game_system = '40K' AND m.name LIKE %s AND ((m.faction = %s AND (EXISTS (SELECT 1 FROM waha_datasheets_keywords dk WHERE dk.datasheet_id = m.id AND dk.keyword = %s) OR NOT EXISTS (SELECT 1 FROM waha_datasheets_keywords dk WHERE dk.datasheet_id = m.id AND dk.keyword IN ({sub_placeholders})))) {'OR m.faction IN (%s, %s)' if allow_allies else ''}) ORDER BY m.name LIMIT {lib_limit}"
        params = [f"%{search}%", primary_army, library_subfaction] + subfactions + (allies if allow_allies else [])
    else:
        lib_query = f"SELECT * FROM view_master_picker WHERE game_system = '40K' AND (faction = %s {'OR faction IN (%s, %s)' if allow_allies else ''}) AND name LIKE %s ORDER BY name LIMIT {lib_limit}"
        params = [primary_army] + (allies if allow_allies else []) + [f"%{search}%"]
    cursor.execute(lib_query, params)
    raw_units = cursor.fetchall()
    # Strict dedupe by normalized id (avoids duplicate entries from view/joins)
    unique_units = []
    seen_nid = set()
    for u in raw_units:
        nid = _normalize_unit_id(u.get("id")) or str(u.get("id") or "")
        if nid and nid in seen_nid:
            continue
        seen_nid.add(nid)
        unique_units.append(u)
    # Batch-fetch keywords for all unique unit ids (for role/type grouping)
    unit_keywords = {}
    if unique_units:
        ids = [_normalize_unit_id(u.get("id")) or str(u.get("id") or "") for u in unique_units]
        ids = [i for i in ids if i]
        if ids:
            placeholders = ", ".join(["%s"] * len(ids))
            try:
                cursor.execute(
                    f"SELECT datasheet_id, GROUP_CONCAT(keyword SEPARATOR ', ') AS kw FROM waha_datasheets_keywords WHERE datasheet_id IN ({placeholders}) GROUP BY datasheet_id",
                    ids,
                )
                for row in cursor.fetchall():
                    did = row.get("datasheet_id")
                    if did is not None:
                        did = str(did).strip()
                        if did.endswith(".0") and did[:-2].isdigit():
                            did = did[:-2]
                        unit_keywords[did] = row.get("kw") or ""
            except Exception:
                pass
    # Attach role and sort: by role order, then by name
    for u in unique_units:
        nid = _normalize_unit_id(u.get("id")) or str(u.get("id") or "")
        kw = unit_keywords.get(nid, "")
        order, label = _unit_role_from_keywords(kw)
        u["_role_order"] = order
        u["_role_label"] = label
    unique_units.sort(key=lambda u: (u.get("_role_order", 99), (u.get("name") or u.get("id") or "").lower()))
    # Roster counts for "in list" hint
    roster_unit_counts = {}
    if not cached_roster_df.empty:
        col = "datasheet_id" if "datasheet_id" in cached_roster_df.columns else "unit_id"
        if col in cached_roster_df.columns:
            for _, r in cached_roster_df.iterrows():
                vid = r.get(col)
                if vid is not None and not (hasattr(vid, "__float__") and pd.isna(vid)):
                    vid = str(vid).strip()
                    if vid.endswith(".0") and vid[:-2].isdigit():
                        vid = vid[:-2]
                    roster_unit_counts[vid] = roster_unit_counts.get(vid, 0) + 1
    # Pagination
    lib_page_key = f"lib_page_{list_id}"
    if lib_page_key not in st.session_state:
        st.session_state[lib_page_key] = 0
    page_size = 20
    total_pages = max(1, (len(unique_units) + page_size - 1) // page_size)
    current_page = min(max(0, st.session_state[lib_page_key]), total_pages - 1)
    st.session_state[lib_page_key] = current_page
    start_idx = current_page * page_size
    page_units = unique_units[start_idx : start_idx + page_size]
    if not unique_units:
        st.sidebar.info("No units match. Try a different search or check faction/detachment.")
    else:
        st.sidebar.caption(f"{len(unique_units)} units · Page {current_page + 1} of {total_pages}")
        if total_pages > 1:
            prev_disabled = current_page <= 0
            next_disabled = current_page >= total_pages - 1
            p1, p2, p3 = st.sidebar.columns([1, 1, 1])
            with p1:
                if st.button("◀ Prev", key=f"lib_prev_{list_id}", disabled=prev_disabled):
                    st.session_state[lib_page_key] = current_page - 1
                    st.rerun()
            with p3:
                if st.button("Next ▶", key=f"lib_next_{list_id}", disabled=next_disabled):
                    st.session_state[lib_page_key] = current_page + 1
                    st.rerun()
    # Group by role and render current page
    current_role = None
    for unit in page_units:
        role_label = unit.get("_role_label") or "Other"
        if role_label != current_role:
            current_role = role_label
            st.sidebar.markdown(f"**{role_label}**")
        uid = unit.get("id")
        nid = _normalize_unit_id(uid) or str(uid or "")
        in_list_count = roster_unit_counts.get(nid, 0) if nid else 0
        c1, c2, c3 = st.sidebar.columns([0.6, 0.2, 0.2])
        display_name = f"⭐ {unit.get('name')}" if unit.get('faction') in allies else (unit.get('name') or unit.get('id') or "—")
        pts = unit.get('points') or unit.get('Points') or 0
        line2 = f"{pts} pts"
        if in_list_count > 0:
            line2 += f" · In list: {in_list_count}"
        c1.write(f"**{display_name}**\n{line2}")
        if c2.button("Add", key=f"add_{unit.get('id')}_{list_id}"):
            candidate_id = _normalize_unit_id(unit.get("id")) or str(unit.get("id", ""))
            resolved_id = None
            try:
                cursor.execute("SELECT waha_datasheet_id FROM waha_datasheets WHERE waha_datasheet_id = %s LIMIT 1", (candidate_id,))
                row = cursor.fetchone()
                if row and row.get("waha_datasheet_id") is not None:
                    resolved_id = str(row["waha_datasheet_id"]).strip()
                    if resolved_id.endswith(".0") and resolved_id[:-2].isdigit():
                        resolved_id = resolved_id[:-2]
                if not resolved_id and unit.get("name"):
                    cursor.execute("SELECT waha_datasheet_id FROM waha_datasheets WHERE name = %s LIMIT 1", (unit["name"],))
                    row = cursor.fetchone()
                    if row and row.get("waha_datasheet_id") is not None:
                        resolved_id = str(row["waha_datasheet_id"]).strip()
            except Exception:
                pass
            unit_id_to_store = resolved_id if resolved_id else candidate_id
            start_qty = 1
            try:
                cursor.execute("SELECT min_size FROM view_40k_unit_composition WHERE datasheet_id = %s", (unit_id_to_store,))
                sz = cursor.fetchone()
                if sz and sz.get("min_size") is not None:
                    start_qty = int(sz["min_size"])
            except Exception:
                pass
            try:
                add_unit_40k(conn, list_id, unit_id_to_store, start_qty)
                st.rerun()
            except Exception as ex:
                st.error(str(ex))
        if c3.button("👁️", key=f"lib_det_{unit.get('id')}_{list_id}", help="Preview unit"):
            uid = _normalize_unit_id(unit.get('id')) or str(unit.get('id', ''))
            show_40k_details(uid, detachment_id=active_det_id)

    # --- DB query results (debug) ---
    with st.sidebar.expander("🔧 DB query results", expanded=False):
        st.caption("Queries that drive roster, unit details, and validation. Use to verify joins.")
        try:
            debug_sections = get_debug_query_results(conn, list_id)
            for sec in debug_sections:
                st.caption(sec["name"])
                if sec["error"]:
                    st.error(sec["error"])
                elif sec["rows"]:
                    st.dataframe(sec["rows"], width="stretch", hide_index=True)
                else:
                    st.caption("(no rows)")
                st.divider()
        except Exception as e:
            st.error(str(e))

    # --- F. Roster Panel ---
    if 'gameday_mode' not in st.session_state:
        st.session_state.gameday_mode = False

    # 1. Header & Mode Toggle
    header_col, toggle_col = st.columns([0.7, 0.3])
    with header_col:
        _ch_display = "Custom chapter" if saved_chapter == CHAPTER_CUSTOM else saved_chapter
        chapter_label = f" ({_ch_display})" if is_space_marine and saved_chapter else ""
        st.title(f"🛡️ Roster: {fix_apostrophe_mojibake(active_list['list_name'])}{chapter_label}")
    with toggle_col:
        if not st.session_state.gameday_mode:
            if st.button("📑 Game-Day View", width="stretch"):
                st.session_state.gameday_mode = True
                st.rerun()
            export_text = _build_40k_list_export_text(active_list, total_pts, cached_roster_df)
            list_name_safe = re.sub(r"[^\w\-]", "_", (active_list.get("list_name") or "40k_list")[:60])
            st.download_button(
                "📥 Export list (txt)",
                data=export_text,
                file_name=f"{list_name_safe}.txt",
                mime="text/plain",
                width="stretch",
                key=f"export_40k_{list_id}",
            )
            export_xml = _build_40k_list_export_ros_xml(active_list, total_pts, cached_roster_df)
            st.download_button(
                "📥 Export for BattleScribe (.ros.xml)",
                data=export_xml,
                file_name=f"{list_name_safe}.ros",
                mime="application/xml",
                width="stretch",
                key=f"export_40k_ros_{list_id}",
            )

    # 2. Logic Branch: Game-Day vs. Editor
    if st.session_state.gameday_mode:
        show_gameday_view(active_list, cached_roster_df, total_pts)
    else:
        try:
            # --- 1. DYNAMIC ARMY & DETACHMENT RULES ---
            cursor.execute("""
                SELECT army_rule_name, army_rule_desc 
                FROM view_40k_army_rule_registry 
                WHERE faction_name = %s OR faction_id = (SELECT id FROM waha_factions WHERE name = %s)
                LIMIT 1
            """, (primary_army, primary_army))
            found_rule = cursor.fetchone()
        except Exception:
            found_rule = None
        try:
            if active_det_id is not None:
                cursor.execute("""
                    SELECT name, description 
                    FROM waha_detachment_abilities 
                    WHERE detachment_id = %s
                    LIMIT 1
                """, (active_det_id,))
                det_rule = cursor.fetchone()
            else:
                det_rule = None
        except Exception:
            det_rule = None

        if found_rule or det_rule:
            _ch_display = "Custom chapter" if saved_chapter == CHAPTER_CUSTOM else saved_chapter
            exp_label = f"📜 {primary_army}" + (f" ({_ch_display})" if is_space_marine and saved_chapter else "") + " Army & Detachment Rules"
            with st.expander(exp_label, expanded=False):
                if found_rule:
                    st.subheader(f"🛡️ Army Rule: {found_rule.get('army_rule_name', '')}")
                    st.write(found_rule.get('army_rule_desc') or '')
                if det_rule:
                    if found_rule: st.divider()
                    st.subheader(f"🚩 Detachment Rule: {det_rule.get('name', '')}")
                    st.write(det_rule.get('description') or '')

        # --- 2. STRATAGEM CHEAT SHEET ---
        try:
            if active_det_id is not None:
                cursor.execute("""
                    SELECT name, type, cp_cost, phase, description 
                    FROM view_40k_stratagems 
                    WHERE clean_det_id = %s
                    ORDER BY phase ASC
                """, (active_det_id,))
                strats = cursor.fetchall()
                strats = _dedupe_stratagems(strats)
            else:
                strats = []
        except Exception:
            strats = []

        if strats:
            with st.expander(f"🎯 {primary_army} Detachment Stratagems", expanded=False):
                for s in strats:
                    st.markdown(f"**{s.get('name', '')}** — {s.get('cp_cost', 0)}CP")
                    st.caption(f"*{s.get('type', '')} - {s.get('phase', '')}*")
                    st.markdown(_format_stratagem_description(s.get('description') or ''))
                    st.divider()
        # --- 3. ROSTER LISTING (Interactive Editor) ---
        if not cached_roster_df.empty:
            st.metric("Total Points", f"{total_pts} / {active_list['point_limit']}")
            unit_chapter = {}
            try:
                if is_space_marine and subfactions:
                    col = "datasheet_id" if "datasheet_id" in cached_roster_df.columns else "unit_id"
                    if col in cached_roster_df.columns:
                        uids = cached_roster_df[col].dropna().unique().tolist()
                        uids = [str(u).strip() for u in uids if u is not None and not (hasattr(u, "__float__") and pd.isna(u))]
                        if uids:
                            ph = ",".join(["%s"] * len(uids))
                            sub_ph = ",".join(["%s"] * len(subfactions))
                            cursor.execute(f"SELECT datasheet_id, keyword FROM waha_datasheets_keywords WHERE datasheet_id IN ({ph}) AND is_faction_keyword = 1 AND keyword IN ({sub_ph})", uids + subfactions)
                            for r in cursor.fetchall():
                                unit_chapter[str(r["datasheet_id"]).strip()] = r["keyword"]
            except Exception:
                pass
            # Re-open unit details after STL add/remove so the dialog stays in context (library_ui sets reopen_unit_details before st.rerun())
            reopen = st.session_state.pop("reopen_unit_details", None)
            if isinstance(reopen, dict) and reopen.get("game_system") == "40K_10E":
                eid = reopen.get("entry_id")
                if eid is not None and not cached_roster_df.empty:
                    ecol = "entry_id" if "entry_id" in cached_roster_df.columns else "Entry_ID"
                    if ecol in cached_roster_df.columns:
                        match = cached_roster_df[cached_roster_df[ecol] == eid]
                        if not match.empty:
                            r = match.iloc[0]
                            uid = _normalize_unit_id(r.get("datasheet_id") or r.get("unit_id")) or str(r.get("datasheet_id") or r.get("unit_id") or "")
                            try:
                                eid_int = int(eid) if eid is not None and not (hasattr(eid, "__float__") and pd.isna(eid)) else None
                            except (TypeError, ValueError):
                                eid_int = None
                            show_40k_details(uid, entry_id=eid_int, detachment_id=active_det_id, faction=active_list.get("faction_primary"), game_system="40K_10E")
            labels_map = _gameday_unit_labels(cached_roster_df)
            for i, row in cached_roster_df.iterrows():
                try:
                    _render_roster_row(row, list_id, active_list, active_det_id, cursor, conn, unit_chapter, is_space_marine, subfactions, cached_roster_df, labels_map)
                except Exception as err:
                    st.warning(f"Could not render one row: {err}")
                    st.write(f"**{row.get('Unit', 'Unit')}** — {row.get('Total_Pts', 0)} pts")
        else:
            st.info("Roster is empty. Add units from the sidebar library.")

    conn.close()

