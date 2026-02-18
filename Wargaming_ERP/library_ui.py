import re
import streamlit as st
import pandas as pd
from database_utils import get_db_connection

# --- 1. Linking Dialog ---
@st.dialog("🔗 Link STL to Game Unit")
def show_link_dialog(mmf_id, model_name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    st.subheader(f"Linking: {model_name}")
    sys_choice = st.selectbox("Game System", ["grimdark-future", "40K_10E"])
    
    # --- FILTERS ---
    f_col, s_col = st.columns(2)
    
    # Fetch Factions based on System for the dropdown
    if sys_choice == "40K_10E":
        cursor.execute("SELECT DISTINCT faction_id as faction FROM waha_datasheets ORDER BY faction_id")
    else:
        cursor.execute("SELECT DISTINCT army as faction FROM opr_units ORDER BY army")
    
    factions = [f['faction'] for f in cursor.fetchall()]
    sel_fac = f_col.selectbox("Filter Faction", ["All"] + factions)
    u_search = s_col.text_input("Search Unit Name")

    # --- AGNOSTIC UNIT FETCH (FIXED FOR COLUMN MISMATCH) ---
    params = []
    if sys_choice == "40K_10E":
        # 40K uses 'faction_id'
        query = "SELECT waha_datasheet_id as id, name, faction_id as army FROM waha_datasheets WHERE 1=1"
        if sel_fac != "All":
            query += " AND faction_id = %s"
            params.append(sel_fac)
    else:
        # OPR uses 'army' and 'game_system'
        query = "SELECT opr_unit_id as id, name, army FROM opr_units WHERE game_system = %s"
        params.append(sys_choice)
        if sel_fac != "All":
            query += " AND army = %s"
            params.append(sel_fac)

    # Global search filter
    if u_search:
        query += " AND name LIKE %s"
        params.append(f"%{u_search}%")
    
    cursor.execute(query + " ORDER BY name LIMIT 100", tuple(params))
    units = cursor.fetchall()
    unit_map = {f"[{u['army']}] {u['name']}": u['id'] for u in units}
    
    target_unit = st.selectbox("Select Target Unit", options=list(unit_map.keys()))
    is_primary = st.checkbox("Set as Default Image?", value=True)
    
    if st.button("Confirm Link", use_container_width=True):
        unit_id = unit_map[target_unit]
        
        # --- EXCLUSIVITY ENFORCEMENT ---
        if is_primary:
            # Wipe any other defaults for this unit in this system
            cursor.execute("UPDATE stl_unit_links SET is_default = 0 WHERE unit_id = %s AND game_system = %s", (unit_id, sys_choice))
        
        # Insert/Update the link
        cursor.execute("""
            INSERT INTO stl_unit_links (mmf_id, unit_id, game_system, is_default) 
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE is_default = VALUES(is_default)
        """, (mmf_id, unit_id, sys_choice, 1 if is_primary else 0))
        
        conn.commit()
        st.success(f"Linked to {target_unit}!")
        st.rerun()
    conn.close()


# --- 2. Link Unit (from Audit / Army Builder: pick STL for a unit) ---
@st.dialog("🔗 Link Unit to STL")
def show_link_unit_dialog(unit_id, unit_name, game_system, army_label=""):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    st.subheader(f"Link unit: {unit_name}" + (f" [{army_label}]" if army_label else ""))
    st.caption(f"Game system: {game_system}")
    search = st.text_input("Search STL by name or MMF ID", placeholder="Type to filter…", key="link_unit_search")
    cursor.execute(
        "SELECT mmf_id, name, creator_name, preview_url FROM stl_library ORDER BY name LIMIT 200"
    )
    rows = cursor.fetchall()
    if search.strip():
        q = f"%{search.strip()}%"
        cursor.execute(
            "SELECT mmf_id, name, creator_name, preview_url FROM stl_library WHERE name LIKE %s OR mmf_id LIKE %s ORDER BY name LIMIT 200",
            (q, q),
        )
        rows = cursor.fetchall()
    if not rows:
        st.info("No STLs found. Add MMF records via the fetcher/hydrator first.")
        conn.close()
        return
    is_default = st.checkbox("Set as default image for this unit", value=True, key="link_unit_default")
    st.caption("Pick an STL below (thumbnail + Link button):")
    cols_per_row = 4
    for i in range(0, len(rows), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, c in enumerate(cols):
            idx = i + j
            if idx >= len(rows):
                break
            r = rows[idx]
            with c:
                if r.get("preview_url"):
                    st.image(r["preview_url"], use_container_width=True)
                else:
                    st.caption("(no preview)")
                st.caption((r["name"] or r["mmf_id"])[:40] + ("…" if len((r["name"] or "") or r["mmf_id"]) > 40 else ""))
                if st.button("Link", key=f"link_btn_{r['mmf_id']}_{unit_id}"):
                    try:
                        if is_default:
                            cursor.execute("UPDATE stl_unit_links SET is_default = 0 WHERE unit_id = %s AND game_system = %s", (unit_id, game_system))
                        cursor.execute(
                            "INSERT IGNORE INTO stl_unit_links (mmf_id, unit_id, game_system, is_default) VALUES (%s, %s, %s, %s)",
                            (r["mmf_id"], unit_id, game_system, 1 if is_default else 0),
                        )
                        conn.commit()
                        st.success(f"Linked to {r['name'][:30]}.")
                        conn.close()
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
    conn.close()


def render_inline_link_unit(unit_id, unit_name, game_system, army_label=""):
    """Inline 'Link unit to STL' UI (no dialog). Use inside unit details dialog to avoid nested dialogs."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    st.caption(f"Link unit: {unit_name}" + (f" [{army_label}]" if army_label else "") + f" — {game_system}")
    search = st.text_input("Search STL by name or MMF ID", placeholder="Type to filter…", key=f"inline_link_search_{unit_id}")
    cursor.execute(
        "SELECT mmf_id, name, creator_name, preview_url FROM stl_library ORDER BY name LIMIT 200"
    )
    rows = cursor.fetchall()
    if search.strip():
        q = f"%{search.strip()}%"
        cursor.execute(
            "SELECT mmf_id, name, creator_name, preview_url FROM stl_library WHERE name LIKE %s OR mmf_id LIKE %s ORDER BY name LIMIT 200",
            (q, q),
        )
        rows = cursor.fetchall()
    if not rows:
        st.info("No STLs found. Add MMF records via the fetcher/hydrator first.")
        conn.close()
        return
    is_default = st.checkbox("Set as default image for this unit", value=True, key=f"inline_link_default_{unit_id}")
    st.caption("Pick an STL below (thumbnail + Link button):")
    cols_per_row = 4
    for i in range(0, len(rows), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, c in enumerate(cols):
            idx = i + j
            if idx >= len(rows):
                break
            r = rows[idx]
            with c:
                if r.get("preview_url"):
                    st.image(r["preview_url"], use_container_width=True)
                else:
                    st.caption("(no preview)")
                st.caption((r["name"] or r["mmf_id"])[:40] + ("…" if len((r["name"] or "") or r["mmf_id"]) > 40 else ""))
                if st.button("Link", key=f"inline_link_btn_{r['mmf_id']}_{unit_id}"):
                    try:
                        if is_default:
                            cursor.execute("UPDATE stl_unit_links SET is_default = 0 WHERE unit_id = %s AND game_system = %s", (unit_id, game_system))
                        cursor.execute(
                            "INSERT IGNORE INTO stl_unit_links (mmf_id, unit_id, game_system, is_default) VALUES (%s, %s, %s, %s)",
                            (r["mmf_id"], unit_id, game_system, 1 if is_default else 0),
                        )
                        conn.commit()
                        st.success(f"Linked to {(r['name'] or '')[:30]}.")
                        conn.close()
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
    conn.close()


# --- 3. Choose STL for Roster (from Army Builder: add STL(s) to a roster entry) ---
@st.dialog("📦 Choose STL for this Roster Slot")
def show_roster_stl_picker_dialog(entry_id, unit_id, unit_name, game_system, army_label=""):
    """Pick one or more STLs to use for this roster entry (kitbashing: add multiple)."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    st.subheader(f"STLs for: {unit_name}" + (f" [{army_label}]" if army_label else ""))
    st.caption("Add STL(s) to use for this slot. You can add multiple (e.g. kitbash from several sources).")
    search = st.text_input("Search STL by name or MMF ID", placeholder="Type to filter…", key="roster_stl_search")
    # Prefer STLs already linked to this unit
    cursor.execute("""
        SELECT l.mmf_id, l.name, l.creator_name, l.preview_url
        FROM stl_library l
        JOIN stl_unit_links ul ON l.mmf_id = ul.mmf_id AND ul.unit_id = %s AND ul.game_system = %s
        ORDER BY ul.is_default DESC, l.name
        LIMIT 50
    """, (unit_id, game_system))
    linked = cursor.fetchall()
    if search.strip():
        q = f"%{search.strip()}%"
        cursor.execute(
            "SELECT mmf_id, name, creator_name, preview_url FROM stl_library WHERE name LIKE %s OR mmf_id LIKE %s ORDER BY name LIMIT 150",
            (q, q),
        )
        rows = cursor.fetchall()
    else:
        cursor.execute("SELECT mmf_id, name, creator_name, preview_url FROM stl_library ORDER BY name LIMIT 150")
        rows = cursor.fetchall()
    if linked and not search.strip():
        st.caption("Suggested (linked to this unit):")
        for r in linked[:8]:
            with st.container(border=True):
                c1, c2 = st.columns([1, 2])
                with c1:
                    if r.get("preview_url"):
                        st.image(r["preview_url"], use_container_width=True)
                    else:
                        st.caption("(no preview)")
                with c2:
                    st.caption(r["name"] or r["mmf_id"])
                    if st.button("Add to roster", key=f"roster_add_{entry_id}_{r['mmf_id']}"):
                        try:
                            cursor.execute("SELECT COALESCE(MAX(sort_order), 0) + 1 FROM play_armylist_stl_choices WHERE entry_id = %s", (entry_id,))
                            next_ord = cursor.fetchone()
                            next_order = (list(next_ord.values())[0] or 0) if next_ord else 0
                            cursor.execute("INSERT IGNORE INTO play_armylist_stl_choices (entry_id, mmf_id, sort_order) VALUES (%s, %s, %s)", (entry_id, r["mmf_id"], next_order))
                            conn.commit()
                            st.success("Added.")
                            conn.close()
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
        st.divider()
    st.caption("All STLs (or search result):")
    cols_per_row = 4
    for i in range(0, len(rows), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, c in enumerate(cols):
            idx = i + j
            if idx >= len(rows):
                break
            r = rows[idx]
            with c:
                if r.get("preview_url"):
                    st.image(r["preview_url"], use_container_width=True)
                else:
                    st.caption("(no preview)")
                st.caption((r["name"] or r["mmf_id"])[:40] + ("…" if len((r["name"] or "") or r["mmf_id"]) > 40 else ""))
                if st.button("Add", key=f"roster_add_all_{entry_id}_{r['mmf_id']}_{idx}"):
                    try:
                        cursor.execute("SELECT COALESCE(MAX(sort_order), 0) + 1 FROM play_armylist_stl_choices WHERE entry_id = %s", (entry_id,))
                        next_ord = cursor.fetchone()
                        next_order = (list(next_ord.values())[0] or 0) if next_ord else 0
                        cursor.execute("INSERT IGNORE INTO play_armylist_stl_choices (entry_id, mmf_id, sort_order) VALUES (%s, %s, %s)", (entry_id, r["mmf_id"], next_order))
                        conn.commit()
                        st.success("Added.")
                        conn.close()
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
    conn.close()


def render_roster_stl_section(entry_id, unit_id, unit_name, game_system, army_label=""):
    """Render 'Choose STL for Roster' block: current choices (thumbnails + Remove) + Add STL button. Call from Army Builder unit details."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT c.id, c.mmf_id, c.sort_order, l.name, l.preview_url
            FROM play_armylist_stl_choices c
            JOIN stl_library l ON c.mmf_id = l.mmf_id
            WHERE c.entry_id = %s
            ORDER BY c.sort_order, c.id
        """, (entry_id,))
        choices = cursor.fetchall()
    except Exception as e:
        choices = []
        if "doesn't exist" in str(e).lower():
            st.caption("Run migration add_play_armylist_stl_choices.sql to use roster STL choices.")
            conn.close()
            return
    st.markdown("**📦 Choose STL for this roster slot**")
    st.caption("STLs to use for this unit in this roster (e.g. kitbash from multiple sources).")
    if choices:
        for ch in choices:
            c1, c2 = st.columns([1, 3])
            with c1:
                if ch.get("preview_url"):
                    st.image(ch["preview_url"], use_container_width=True)
                else:
                    st.caption("(no preview)")
            with c2:
                st.caption(ch["name"] or ch["mmf_id"])
                if st.button("Remove", key=f"roster_rm_{entry_id}_{ch['id']}"):
                    cursor.execute("DELETE FROM play_armylist_stl_choices WHERE id = %s", (ch["id"],))
                    conn.commit()
                    conn.close()
                    st.rerun()
        st.divider()
    # Inline picker (no nested dialog — we may be inside unit details dialog)
    with st.expander("Add STL…", expanded=False):
        _render_inline_roster_stl_picker(conn, entry_id, unit_id, game_system)
    conn.close()


def _render_inline_roster_stl_picker(conn, entry_id, unit_id, game_system):
    """Inline STL picker for roster slot (used inside unit details dialog; no nested dialog)."""
    cursor = conn.cursor(dictionary=True)
    search = st.text_input("Search STL by name or MMF ID", placeholder="Type to filter…", key=f"roster_stl_search_{entry_id}")
    cursor.execute("""
        SELECT l.mmf_id, l.name, l.creator_name, l.preview_url
        FROM stl_library l
        JOIN stl_unit_links ul ON l.mmf_id = ul.mmf_id AND ul.unit_id = %s AND ul.game_system = %s
        ORDER BY ul.is_default DESC, l.name
        LIMIT 50
    """, (unit_id, game_system))
    linked = cursor.fetchall()
    if search.strip():
        q = f"%{search.strip()}%"
        cursor.execute(
            "SELECT mmf_id, name, creator_name, preview_url FROM stl_library WHERE name LIKE %s OR mmf_id LIKE %s ORDER BY name LIMIT 150",
            (q, q),
        )
        rows = cursor.fetchall()
    else:
        cursor.execute("SELECT mmf_id, name, creator_name, preview_url FROM stl_library ORDER BY name LIMIT 150")
        rows = cursor.fetchall()
    if linked and not search.strip():
        st.caption("Suggested (linked to this unit):")
        for r in linked[:8]:
            c1, c2 = st.columns([1, 2])
            with c1:
                if r.get("preview_url"):
                    st.image(r["preview_url"], use_container_width=True)
                else:
                    st.caption("(no preview)")
            with c2:
                st.caption(r["name"] or r["mmf_id"])
                if st.button("Add to roster", key=f"roster_add_{entry_id}_{r['mmf_id']}"):
                    try:
                        cursor.execute("SELECT COALESCE(MAX(sort_order), 0) + 1 FROM play_armylist_stl_choices WHERE entry_id = %s", (entry_id,))
                        next_ord = cursor.fetchone()
                        next_order = (list(next_ord.values())[0] or 0) if next_ord else 0
                        cursor.execute("INSERT IGNORE INTO play_armylist_stl_choices (entry_id, mmf_id, sort_order) VALUES (%s, %s, %s)", (entry_id, r["mmf_id"], next_order))
                        conn.commit()
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
        st.divider()
    st.caption("All STLs (or search result):")
    cols_per_row = 4
    for i in range(0, len(rows), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, c in enumerate(cols):
            idx = i + j
            if idx >= len(rows):
                break
            r = rows[idx]
            with c:
                if r.get("preview_url"):
                    st.image(r["preview_url"], use_container_width=True)
                else:
                    st.caption("(no preview)")
                st.caption((r["name"] or r["mmf_id"])[:40] + ("…" if len((r["name"] or "") or r["mmf_id"]) > 40 else ""))
                if st.button("Add", key=f"roster_add_all_{entry_id}_{r['mmf_id']}_{idx}"):
                    try:
                        cursor.execute("SELECT COALESCE(MAX(sort_order), 0) + 1 FROM play_armylist_stl_choices WHERE entry_id = %s", (entry_id,))
                        next_ord = cursor.fetchone()
                        next_order = (list(next_ord.values())[0] or 0) if next_ord else 0
                        cursor.execute("INSERT IGNORE INTO play_armylist_stl_choices (entry_id, mmf_id, sort_order) VALUES (%s, %s, %s)", (entry_id, r["mmf_id"], next_order))
                        conn.commit()
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))


def run_library_ui():
    tab1, tab2, tab3 = st.tabs(["🖼️ STL Gallery", "🛡️ OPR Audit", "🦅 40K Audit"])

    # --- TAB 1: GALLERY (paginated + filtered) ---
    with tab1:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Session state for pagination and filter signature (reset page when filters change)
        if "stl_gallery_page" not in st.session_state:
            st.session_state.stl_gallery_page = 1
        if "stl_gallery_page_size" not in st.session_state:
            st.session_state.stl_gallery_page_size = 24
        if "stl_gallery_filter_sig" not in st.session_state:
            st.session_state.stl_gallery_filter_sig = ""

        # --- FILTERS ROW ---
        f1, f2, f3, f4 = st.columns([2, 1, 1, 1])
        search_query = f1.text_input("🔍 Search", placeholder="Name or MMF ID...", key="stl_search")

        cursor.execute("SELECT DISTINCT creator_name FROM stl_library WHERE creator_name IS NOT NULL AND creator_name != '' ORDER BY creator_name")
        creators = [r['creator_name'] for r in cursor.fetchall()]
        selected_creator = f2.selectbox("👷 Creator", ["All"] + creators, key="stl_creator")
        has_preview_only = f3.checkbox("Has preview only", value=False, key="stl_has_preview")
        sort_by = f4.selectbox(
            "Sort",
            ["Name A–Z", "Name Z–A", "Newest first", "Oldest first"],
            key="stl_sort"
        )

        # Second row: kit metadata filters (require add_stl_library_kit_metadata.sql)
        KIT_TYPES = ["Vehicle", "Infantry", "Monster", "Prop", "Terrain", "Bases", "Accessories", "Statues", "Books_PDF_Docs"]
        f5, f6, f7, f8 = st.columns(4)
        filter_kit_type = f5.selectbox("Kit type", ["All"] + KIT_TYPES, key="stl_kit_type")
        filter_size = f6.text_input("Size/scale", placeholder="e.g. 28mm", key="stl_size")
        filter_supported = f7.selectbox("Supported", ["All", "Yes", "No", "Unknown"], key="stl_supported")
        filter_print_tech = f8.selectbox("Print tech", ["All", "FDM", "Resin", "Both", "Unknown"], key="stl_print_tech")

        # Build WHERE and ORDER
        base_query = "FROM stl_library WHERE 1=1"
        params = []
        if search_query.strip():
            base_query += " AND (name LIKE %s OR mmf_id LIKE %s)"
            params.extend([f"%{search_query.strip()}%", f"%{search_query.strip()}%"])
        if selected_creator != "All":
            base_query += " AND creator_name = %s"
            params.append(selected_creator)
        if has_preview_only:
            base_query += " AND preview_url IS NOT NULL AND preview_url != ''"
        if filter_kit_type != "All":
            base_query += " AND (kit_type LIKE %s OR kit_type = %s)"
            params.extend([f"%{filter_kit_type}%", filter_kit_type])
        if (filter_size or "").strip():
            base_query += " AND size_or_scale LIKE %s"
            params.append(f"%{filter_size.strip()}%")
        if filter_supported == "Yes":
            base_query += " AND is_supported = 1"
        elif filter_supported == "No":
            base_query += " AND is_supported = 0"
        elif filter_supported == "Unknown":
            base_query += " AND is_supported IS NULL"
        if filter_print_tech != "All":
            base_query += " AND print_technology = %s"
            params.append(filter_print_tech)

        order_clause = {
            "Name A–Z": "ORDER BY name ASC",
            "Name Z–A": "ORDER BY name DESC",
            "Newest first": "ORDER BY date_added DESC",
            "Oldest first": "ORDER BY date_added ASC",
        }[sort_by]

        # Reset to page 1 when filters change
        filter_sig = f"{search_query}|{selected_creator}|{has_preview_only}|{sort_by}|{filter_kit_type}|{filter_size}|{filter_supported}|{filter_print_tech}"
        if filter_sig != st.session_state.stl_gallery_filter_sig:
            st.session_state.stl_gallery_filter_sig = filter_sig
            st.session_state.stl_gallery_page = 1

        # Total count
        cursor.execute(f"SELECT COUNT(*) as n {base_query}", tuple(params))
        total_count = cursor.fetchone()["n"]

        # --- PAGE SIZE + PAGINATION CONTROLS ---
        page_size_options = [12, 24, 48, 96]
        ps_col, nav_col, _ = st.columns([1, 2, 2])
        with ps_col:
            default_ps_idx = page_size_options.index(st.session_state.stl_gallery_page_size) if st.session_state.stl_gallery_page_size in page_size_options else 1
            new_page_size = st.selectbox(
                "Per page",
                options=page_size_options,
                index=default_ps_idx,
                key="stl_per_page"
            )
        if new_page_size != st.session_state.stl_gallery_page_size:
            st.session_state.stl_gallery_page_size = new_page_size
            st.session_state.stl_gallery_page = 1
        page_size = st.session_state.stl_gallery_page_size
        max_page = max(1, (total_count + page_size - 1) // page_size)
        current_page = min(max(1, st.session_state.stl_gallery_page), max_page)
        st.session_state.stl_gallery_page = current_page

        with nav_col:
            prev_disabled = current_page <= 1
            next_disabled = current_page >= max_page
            p1, p2, p3, p4, p5, p6 = st.columns([1, 1, 1, 1, 2, 1])
            with p2:
                if st.button("◀ Prev", key="stl_prev", disabled=prev_disabled):
                    st.session_state.stl_gallery_page = current_page - 1
                    st.rerun()
            with p3:
                st.caption(f"Page **{current_page}** of **{max_page}** · {total_count} total")
            with p4:
                if st.button("Next ▶", key="stl_next", disabled=next_disabled):
                    st.session_state.stl_gallery_page = current_page + 1
                    st.rerun()
            with p5:
                goto = st.number_input("Go to page", min_value=1, max_value=max_page, value=current_page, key="stl_goto_page", label_visibility="collapsed")
            with p6:
                if st.button("Go", key="stl_go_page"):
                    p = int(st.session_state.get("stl_goto_page", current_page))
                    st.session_state.stl_gallery_page = max(1, min(p, max_page))
                    st.rerun()

        # Fetch only current page
        offset = (current_page - 1) * page_size
        cursor.execute(
            f"SELECT * {base_query} {order_clause} LIMIT %s OFFSET %s",
            tuple(params) + (page_size, offset)
        )
        stls = cursor.fetchall()

        if stls:
            cols = st.columns(4)
            for idx, stl in enumerate(stls):
                with cols[idx % 4]:
                    with st.container(border=True):
                        if stl.get('preview_url'):
                            st.image(stl['preview_url'], use_container_width=True)
                        else:
                            st.caption("(no preview)")
                        st.markdown(f"**{stl['name']}**")
                        if stl.get('creator_name'):
                            st.caption(stl['creator_name'])
                        price_str = (stl.get('price') or "").strip()
                        if price_str and price_str not in ("0", "0.00", "0.0"):
                            st.caption(f"💰 {price_str}")
                        desc = (stl.get('description') or "").strip()
                        if desc:
                            plain = re.sub(r"<[^>]+>", " ", desc).strip()
                            plain = " ".join(plain.split())[:120]
                            if len(plain) >= 120:
                                plain = plain + "…"
                            st.caption(plain)
                        notes_val = (stl.get('notes') or "").strip()
                        desc_full = (stl.get('description') or "").strip()
                        tags_val = (stl.get('tags') or "").strip()
                        if notes_val:
                            st.caption("📝 " + (notes_val[:80] + "…" if len(notes_val) > 80 else notes_val))
                        if tags_val:
                            st.caption("🏷️ " + tags_val)
                        # Kit metadata one-liners (if columns exist)
                        size_val = (stl.get("size_or_scale") or "").strip()
                        kit_val = (stl.get("kit_type") or "").strip()
                        sup_val = stl.get("is_supported")
                        tech_val = (stl.get("print_technology") or "").strip()
                        rate_val = (stl.get("miniature_rating") or "").strip()
                        if size_val:
                            st.caption("📐 " + size_val)
                        if kit_val:
                            st.caption("📦 " + kit_val)
                        if sup_val is not None:
                            st.caption("✓ Supported" if sup_val else "✗ Unsupported")
                        if tech_val:
                            st.caption("🖨️ " + tech_val)
                        if rate_val:
                            st.caption("⭐ " + rate_val)

                        raw_val = str(stl['mmf_url']) if stl.get('mmf_url') else ""
                        if ".com" in raw_val:
                            clean_slug = raw_val.split(".com")[-1].lstrip("/")
                        else:
                            clean_slug = raw_val.strip().lstrip("/")
                        if not clean_slug:
                            clean_url = "https://www.myminifactory.com"
                        elif clean_slug.startswith("object/3d-print"):
                            clean_url = f"https://www.myminifactory.com/{clean_slug}"
                        else:
                            clean_url = f"https://www.myminifactory.com/object/3d-print-{clean_slug}"

                        c_a, c_b, c_c = st.columns(3)
                        if c_a.button("🔗 Link", key=f"lk_{stl['mmf_id']}_{current_page}_{idx}", use_container_width=True):
                            show_link_dialog(stl['mmf_id'], stl['name'])
                        c_b.link_button("🌐 MMF", clean_url, use_container_width=True)
                        c_c.link_button("⬇ Download", clean_url, use_container_width=True)

                        if desc_full:
                            with st.expander("📄 Full description", expanded=False):
                                st.text(re.sub(r"<[^>]+>", " ", desc_full).strip())
                        with st.expander("📦 Kit & print", expanded=False):
                            k_size = st.text_input("Size/scale", value=(stl.get("size_or_scale") or "").strip(), key=f"kit_size_{stl['mmf_id']}_{current_page}_{idx}", placeholder="e.g. 28mm")
                            k_type_opt = ["", "Vehicle", "Infantry", "Monster", "Prop", "Terrain", "Bases", "Accessories", "Statues", "Books_PDF_Docs"]
                            k_type_cur = (stl.get("kit_type") or "").strip() or ""
                            k_type = st.selectbox("Kit type", k_type_opt, index=k_type_opt.index(k_type_cur) if k_type_cur in k_type_opt else 0, key=f"kit_type_{stl['mmf_id']}_{current_page}_{idx}")
                            k_comp = st.text_input("Kit composition", value=(stl.get("kit_composition") or "").strip(), key=f"kit_comp_{stl['mmf_id']}_{current_page}_{idx}", placeholder="multiple_units, bits, etc.")
                            k_sup_opt = ["Unknown", "Yes", "No"]
                            k_sup_cur = "Yes" if stl.get("is_supported") == 1 else "No" if stl.get("is_supported") == 0 else "Unknown"
                            k_sup = st.selectbox("Supported", k_sup_opt, index=k_sup_opt.index(k_sup_cur), key=f"kit_sup_{stl['mmf_id']}_{current_page}_{idx}")
                            k_tech_opt = ["", "FDM", "Resin", "Both", "Unknown"]
                            k_tech_cur = (stl.get("print_technology") or "").strip() or ""
                            k_tech = st.selectbox("Print tech", k_tech_opt, index=k_tech_opt.index(k_tech_cur) if k_tech_cur in k_tech_opt else 0, key=f"kit_tech_{stl['mmf_id']}_{current_page}_{idx}")
                            k_rate = st.text_input("Rating", value=(stl.get("miniature_rating") or "").strip(), key=f"kit_rate_{stl['mmf_id']}_{current_page}_{idx}", placeholder="e.g. 4.5")
                            k_lic = st.text_input("License", value=(stl.get("license_type") or "").strip(), key=f"kit_lic_{stl['mmf_id']}_{current_page}_{idx}", placeholder="Commercial, Personal")
                            k_parts_val = stl.get("part_count")
                            k_parts = st.number_input("Part count", min_value=0, value=int(k_parts_val) if k_parts_val is not None else 0, key=f"kit_parts_{stl['mmf_id']}_{current_page}_{idx}")
                            k_time = st.text_input("Print time est.", value=(stl.get("print_time_estimate") or "").strip(), key=f"kit_time_{stl['mmf_id']}_{current_page}_{idx}", placeholder="e.g. 8h")
                            if st.button("Save kit", key=f"save_kit_{stl['mmf_id']}_{current_page}_{idx}"):
                                try:
                                    conn2 = get_db_connection()
                                    cur2 = conn2.cursor()
                                    is_sup_val = None if k_sup == "Unknown" else (1 if k_sup == "Yes" else 0)
                                    cur2.execute("""UPDATE stl_library SET size_or_scale=%s, kit_type=%s, kit_composition=%s, is_supported=%s, print_technology=%s, miniature_rating=%s, license_type=%s, part_count=%s, print_time_estimate=%s WHERE mmf_id=%s""",
                                        (k_size or None, k_type or None, k_comp or None, is_sup_val, k_tech or None, k_rate or None, k_lic or None, k_parts, k_time or None, stl['mmf_id']))
                                    conn2.commit()
                                    conn2.close()
                                    st.success("Kit saved.")
                                    st.rerun()
                                except Exception as e:
                                    st.error("Run migration add_stl_library_kit_metadata.sql" if "Unknown column" in str(e) else str(e))
                        with st.expander("✏️ Notes & tags", expanded=False):
                            new_notes = st.text_area("Notes", value=notes_val, key=f"notes_{stl['mmf_id']}_{current_page}_{idx}", height=60, label_visibility="collapsed", placeholder="Your notes…")
                            new_tags = st.text_input("Tags", value=tags_val, key=f"tags_{stl['mmf_id']}_{current_page}_{idx}", placeholder="comma, separated, tags", label_visibility="collapsed")
                            if st.button("Save", key=f"save_nt_{stl['mmf_id']}_{current_page}_{idx}"):
                                try:
                                    conn2 = get_db_connection()
                                    cur2 = conn2.cursor()
                                    cur2.execute("UPDATE stl_library SET notes = %s, tags = %s WHERE mmf_id = %s", (new_notes or None, (new_tags or "").strip() or None, stl['mmf_id']))
                                    conn2.commit()
                                    conn2.close()
                                    st.success("Saved.")
                                    st.rerun()
                                except Exception as e:
                                    if "Unknown column" in str(e) or "notes" in str(e).lower() or "tags" in str(e).lower():
                                        st.error("Run migration first: Wargaming_ERP/migrations/add_stl_library_notes_tags.sql")
                                    else:
                                        st.error(str(e))
                        with st.expander("🏴 Faction associations", expanded=False):
                            conn_f = get_db_connection()
                            cur_f = conn_f.cursor(dictionary=True)
                            try:
                                cur_f.execute("SELECT id, game_system, faction_key FROM stl_library_faction_links WHERE mmf_id = %s ORDER BY game_system, faction_key", (stl['mmf_id'],))
                                links = cur_f.fetchall()
                                for lnk in links:
                                    lbl = f"{lnk['game_system']}: {lnk['faction_key']}"
                                    if st.button("🗑 " + lbl, key=f"del_faction_{lnk['id']}_{current_page}_{idx}"):
                                        cur_f.execute("DELETE FROM stl_library_faction_links WHERE id = %s", (lnk['id'],))
                                        conn_f.commit()
                                        conn_f.close()
                                        st.rerun()
                                sys_add = st.selectbox("Game system", ["40K_10E", "grimdark-future", "age-of-fantasy"], key=f"fac_sys_{stl['mmf_id']}_{current_page}_{idx}")
                                if sys_add == "40K_10E":
                                    cur_f.execute("SELECT id, name FROM waha_factions WHERE id != '0' ORDER BY name")
                                    factions = cur_f.fetchall()
                                    fac_options = [f"{f['name']} ({f['id']})" for f in factions]
                                    fac_keys = [f['id'] for f in factions]
                                else:
                                    cur_f.execute("SELECT DISTINCT army FROM opr_units WHERE game_system = %s ORDER BY army", (sys_add,))
                                    factions = cur_f.fetchall()
                                    fac_options = [f['army'] for f in factions]
                                    fac_keys = fac_options
                                sel_fac = st.selectbox("Faction / army", ["—"] + fac_options, key=f"fac_sel_{stl['mmf_id']}_{current_page}_{idx}")
                                if sel_fac != "—" and st.button("Add association", key=f"add_faction_{stl['mmf_id']}_{current_page}_{idx}"):
                                    idx_f = fac_options.index(sel_fac)
                                    fk = fac_keys[idx_f]
                                    cur_f.execute("INSERT IGNORE INTO stl_library_faction_links (mmf_id, game_system, faction_key) VALUES (%s, %s, %s)", (stl['mmf_id'], sys_add, fk))
                                    conn_f.commit()
                                    st.success(f"Linked to {sel_fac}.")
                                    conn_f.close()
                                    st.rerun()
                            except Exception as ex:
                                if "doesn't exist" in str(ex).lower():
                                    st.caption("Run migration add_stl_library_faction_links.sql to use faction associations.")
                                else:
                                    st.error(str(ex))
                            finally:
                                try:
                                    conn_f.close()
                                except Exception:
                                    pass
        else:
            st.info("No matching STLs on this page. Try different filters or go to an earlier page.")
        conn.close()




    # --- TAB 2: OPR AUDIT ---
    with tab2:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        st.subheader("🕵️ OPR Coverage Audit")
        view_mode_opr = st.radio("View", ["Linked units", "Units with no links"], key="opr_view", horizontal=True)
        c1, c2 = st.columns(2)
        opr_sys = c1.selectbox("Filter by OPR System",
            ["All", "grimdark-future", "grimdark-future-firefight", "age-of-fantasy", "age-of-fantasy-skirmish", "age-of-fantasy-regiments"], key="opr_sys")
        cursor.execute("SELECT DISTINCT army FROM opr_units ORDER BY army")
        opr_armies = [r['army'] for r in cursor.fetchall()]
        sel_opr_army = c2.multiselect("Filter by Army Book", opr_armies, key="opr_army")

        if view_mode_opr == "Linked units":
            broken_opr = get_broken_links(conn, "opr")
            if broken_opr:
                with st.expander(f"⚠ Broken links ({len(broken_opr)}) — STL or unit no longer in DB", expanded=True):
                    st.caption("These links point to a missing stl_library row or a removed OPR unit.")
                    for b in broken_opr:
                        st.text(f"Link id {b['id']}: mmf_id={b['mmf_id']}, unit_id={b['unit_id']}, game_system={b['game_system']}")
                    if st.button("Remove all broken links (OPR)", key="remove_broken_opr"):
                        cur = conn.cursor()
                        for b in broken_opr:
                            cur.execute("DELETE FROM stl_unit_links WHERE id = %s", (b["id"],))
                        conn.commit()
                        st.success(f"Removed {len(broken_opr)} broken link(s).")
                        st.rerun()
            query = """
                SELECT ul.id, l.name as model_name, u.name as unit_name, u.army,
                       ul.mmf_id, ul.unit_id, ul.is_default, ul.game_system, l.preview_url
                FROM stl_unit_links ul
                JOIN stl_library l ON ul.mmf_id = l.mmf_id
                JOIN opr_units u ON ul.unit_id = u.opr_unit_id AND ul.game_system = u.game_system
                WHERE ul.game_system != '40K_10E'
            """
            params = []
            if opr_sys != "All":
                query += " AND ul.game_system = %s"
                params.append(opr_sys)
            if sel_opr_army:
                query += f" AND u.army IN ({','.join(['%s']*len(sel_opr_army))})"
                params.extend(sel_opr_army)
            cursor.execute(query + " ORDER BY ul.game_system, u.army, u.name", tuple(params))
            render_audit_editor(cursor.fetchall(), "opr", conn)
        else:
            unlinked_query = """
                SELECT u.opr_unit_id as unit_id, u.name as unit_name, u.army, u.game_system
                FROM opr_units u
                WHERE NOT EXISTS (
                    SELECT 1 FROM stl_unit_links ul WHERE ul.unit_id = u.opr_unit_id AND ul.game_system = u.game_system
                ) AND u.game_system != '40K_10E'
            """
            params = []
            if opr_sys != "All":
                unlinked_query += " AND u.game_system = %s"
                params.append(opr_sys)
            if sel_opr_army:
                unlinked_query += f" AND u.army IN ({','.join(['%s']*len(sel_opr_army))})"
                params.extend(sel_opr_army)
            cursor.execute(unlinked_query + " ORDER BY u.game_system, u.army, u.name LIMIT 200", tuple(params))
            unlinked = cursor.fetchall()
            render_unlinked_units(unlinked, "opr")
        conn.close()

    # --- TAB 3: 40K AUDIT ---
    with tab3:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        st.subheader("🔭 40K Coverage Audit")
        view_mode_40k = st.radio("View", ["Linked units", "Units with no links"], key="40k_view", horizontal=True)
        cursor.execute("SELECT DISTINCT faction_id FROM waha_datasheets ORDER BY faction_id")
        factions = [r['faction_id'] for r in cursor.fetchall()]
        sel_factions = st.multiselect("Filter by Faction", factions, key="40k_fac")

        if view_mode_40k == "Linked units":
            broken_40k = get_broken_links(conn, "40K_10E")
            if broken_40k:
                with st.expander(f"⚠ Broken links ({len(broken_40k)}) — STL or unit no longer in DB", expanded=True):
                    st.caption("These links point to a missing stl_library row or a removed 40K datasheet.")
                    for b in broken_40k:
                        st.text(f"Link id {b['id']}: mmf_id={b['mmf_id']}, unit_id={b['unit_id']}")
                    if st.button("Remove all broken links (40K)", key="remove_broken_40k"):
                        cur = conn.cursor()
                        for b in broken_40k:
                            cur.execute("DELETE FROM stl_unit_links WHERE id = %s", (b["id"],))
                        conn.commit()
                        st.success(f"Removed {len(broken_40k)} broken link(s).")
                        st.rerun()
            query = """
                SELECT ul.id, l.name as model_name, d.name as unit_name, d.faction_id as army,
                       ul.mmf_id, ul.unit_id, ul.is_default, ul.game_system, l.preview_url
                FROM stl_unit_links ul
                JOIN stl_library l ON ul.mmf_id = l.mmf_id
                JOIN waha_datasheets d ON ul.unit_id = d.waha_datasheet_id
                WHERE ul.game_system = '40K_10E'
            """
            params = []
            if sel_factions:
                query += f" AND d.faction_id IN ({','.join(['%s']*len(sel_factions))})"
                params.extend(sel_factions)
            cursor.execute(query + " ORDER BY d.faction_id, d.name", tuple(params))
            render_audit_editor(cursor.fetchall(), "waha", conn)
        else:
            unlinked_query = """
                SELECT d.waha_datasheet_id as unit_id, d.name as unit_name, d.faction_id as army, '40K_10E' as game_system
                FROM waha_datasheets d
                WHERE NOT EXISTS (
                    SELECT 1 FROM stl_unit_links ul WHERE ul.unit_id = d.waha_datasheet_id AND ul.game_system = '40K_10E'
                )
            """
            params = []
            if sel_factions:
                unlinked_query += f" AND d.faction_id IN ({','.join(['%s']*len(sel_factions))})"
                params.extend(sel_factions)
            cursor.execute(unlinked_query + " ORDER BY d.faction_id, d.name LIMIT 200", tuple(params))
            unlinked = cursor.fetchall()
            render_unlinked_units(unlinked, "waha")
        conn.close()

def get_broken_links(conn, game_system):
    """Return stl_unit_links where mmf_id not in stl_library or unit_id not in units table."""
    cursor = conn.cursor(dictionary=True)
    if game_system == "40K_10E":
        cursor.execute("""
            SELECT ul.id, ul.mmf_id, ul.unit_id, ul.game_system
            FROM stl_unit_links ul
            WHERE ul.game_system = '40K_10E'
            AND (ul.mmf_id NOT IN (SELECT mmf_id FROM stl_library)
                 OR ul.unit_id NOT IN (SELECT waha_datasheet_id FROM waha_datasheets))
        """)
    else:
        cursor.execute("""
            SELECT ul.id, ul.mmf_id, ul.unit_id, ul.game_system
            FROM stl_unit_links ul
            WHERE ul.game_system != '40K_10E'
            AND (ul.mmf_id NOT IN (SELECT mmf_id FROM stl_library)
                 OR ul.unit_id NOT IN (SELECT opr_unit_id FROM opr_units WHERE opr_units.game_system = ul.game_system))
        """)
    return cursor.fetchall()


def render_unlinked_units(unlinked, key_prefix):
    """Show units that have no STL link; each row has a 'Link…' button that opens the link-unit dialog."""
    if not unlinked:
        st.info("No unlinked units for these filters.")
        return
    st.caption(f"Showing up to 200 units with no STL link. Use filters above to narrow.")
    for row in unlinked:
        c1, c2 = st.columns([3, 1])
        with c1:
            st.text(f"{row['unit_name']} — {row['army']} ({row['game_system']})")
        with c2:
            if st.button("Link…", key=f"link_unit_{key_prefix}_{row['unit_id']}"):
                show_link_unit_dialog(
                    row["unit_id"],
                    row["unit_name"],
                    row["game_system"],
                    army_label=str(row.get("army", "")),
                )


def render_audit_editor(links, key_prefix, conn):
    if links:
        df = pd.DataFrame(links)
        if "preview_url" not in df.columns:
            df["preview_url"] = None
        df["unlink_me"] = False
        column_config = {
            "id": None, "mmf_id": None, "unit_id": None,
            "preview_url": st.column_config.ImageColumn("Preview", width="small"),
            "is_default": st.column_config.CheckboxColumn("Default"),
            "game_system": st.column_config.TextColumn("System", width="small"),
            "unlink_me": st.column_config.CheckboxColumn("Unlink?", width="small"),
        }
        edited_df = st.data_editor(
            df,
            column_config=column_config,
            disabled=["model_name", "unit_name", "army", "game_system"],
            hide_index=True, use_container_width=True, key=f"editor_{key_prefix}"
        )

        col_save, col_unlink = st.columns(2)
        with col_save:
            if st.button(f"💾 Save {key_prefix.upper()} Changes", key=f"save_{key_prefix}"):
                cursor = conn.cursor()
                for idx, row in edited_df.iterrows():
                    orig = df.iloc[idx]
                    if row["is_default"] != orig["is_default"]:
                        if row["is_default"]:
                            cursor.execute("UPDATE stl_unit_links SET is_default = 0 WHERE unit_id = %s AND game_system = %s", (row["unit_id"], row["game_system"]))
                            cursor.execute("UPDATE stl_unit_links SET is_default = 1 WHERE id = %s", (row["id"],))
                        else:
                            cursor.execute("UPDATE stl_unit_links SET is_default = 0 WHERE id = %s", (row["id"],))
                conn.commit()
                st.success("Audit Persisted!")
                st.rerun()
        with col_unlink:
            to_unlink = edited_df[edited_df["unlink_me"] == True]
            if st.button("🗑 Unlink checked", key=f"unlink_{key_prefix}"):
                if len(to_unlink):
                    cursor = conn.cursor()
                    for _, row in to_unlink.iterrows():
                        cursor.execute("DELETE FROM stl_unit_links WHERE id = %s", (row["id"],))
                    conn.commit()
                    st.success(f"Unlinked {len(to_unlink)} link(s).")
                    st.rerun()
                else:
                    st.warning("Check at least one row (Unlink?) to unlink.")
    else:
        st.info("No links found for these filters.")
