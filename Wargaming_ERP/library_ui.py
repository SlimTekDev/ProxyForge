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

        order_clause = {
            "Name A–Z": "ORDER BY name ASC",
            "Name Z–A": "ORDER BY name DESC",
            "Newest first": "ORDER BY date_added DESC",
            "Oldest first": "ORDER BY date_added ASC",
        }[sort_by]

        # Reset to page 1 when filters change
        filter_sig = f"{search_query}|{selected_creator}|{has_preview_only}|{sort_by}"
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
        else:
            st.info("No matching STLs on this page. Try different filters or go to an earlier page.")
        conn.close()




    # --- TAB 2: OPR AUDIT ---
    with tab2:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        st.subheader("🕵️ OPR Coverage Audit")
        c1, c2 = st.columns(2)
        opr_sys = c1.selectbox("Filter by OPR System", 
            ["All", "grimdark-future", "grimdark-future-firefight", "age-of-fantasy", "age-of-fantasy-skirmish", "age-of-fantasy-regiments"])
        cursor.execute("SELECT DISTINCT army FROM opr_units ORDER BY army")
        opr_armies = [r['army'] for r in cursor.fetchall()]
        sel_opr_army = c2.multiselect("Filter by Army Book", opr_armies)

        query = """
            SELECT ul.id, l.name as model_name, u.name as unit_name, u.army, 
                   ul.mmf_id, ul.unit_id, ul.is_default, ul.game_system
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
        conn.close()

    # --- TAB 3: 40K AUDIT ---
    with tab3:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        st.subheader("🔭 40K Coverage Audit")
        cursor.execute("SELECT DISTINCT faction_id FROM waha_datasheets ORDER BY faction_id")
        factions = [r['faction_id'] for r in cursor.fetchall()]
        sel_factions = st.multiselect("Filter by Faction", factions)

        query = """
            SELECT ul.id, l.name as model_name, d.name as unit_name, d.faction_id as army, 
                   ul.mmf_id, ul.unit_id, ul.is_default, ul.game_system
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
        conn.close()

def render_audit_editor(links, key_prefix, conn):
    if links:
        df = pd.DataFrame(links)
        edited_df = st.data_editor(
            df,
            column_config={
                "id": None, "mmf_id": None, "unit_id": None,
                "is_default": st.column_config.CheckboxColumn("Default"),
                "game_system": st.column_config.TextColumn("System", width="small")
            },
            disabled=["model_name", "unit_name", "army", "game_system"],
            hide_index=True, use_container_width=True, key=f"editor_{key_prefix}"
        )

        if st.button(f"💾 Save {key_prefix.upper()} Changes", key=f"save_{key_prefix}"):
            cursor = conn.cursor()
            for idx, row in edited_df.iterrows():
                orig = df.iloc[idx]
                if row['is_default'] != orig['is_default']:
                    if row['is_default']:
                        cursor.execute("UPDATE stl_unit_links SET is_default = 0 WHERE unit_id = %s AND game_system = %s", (row['unit_id'], row['game_system']))
                        cursor.execute("UPDATE stl_unit_links SET is_default = 1 WHERE id = %s", (row['id'],))
                    else:
                        cursor.execute("UPDATE stl_unit_links SET is_default = 0 WHERE id = %s", (row['id'],))
            conn.commit()
            st.success("Audit Persisted!")
            st.rerun()
    else:
        st.info("No links found for these filters.")
