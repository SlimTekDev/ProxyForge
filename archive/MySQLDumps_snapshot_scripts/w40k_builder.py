import streamlit as st
import pandas as pd
import re
from database_utils import get_db_connection

#This parser for wargear options  still needs refinement
def parse_wargear_option(text):
    """Surgical parser for Wahapedia 10th Ed weapon swaps."""
    if not text: return {"type": "none"}
    
    # 1. Nested Lists (e.g., "replaced with one of the following: 1 big choppa 1 power klaw")
    if "one of the following:" in text.lower():
        # Split into header and the options string
        parts = re.split(r'one of the following:', text, flags=re.IGNORECASE)
        header = parts[0]
        # Use regex to find items preceded by '1 ' or 'one '
        # This handles the lack of commas in some Wahapedia exports
        options_raw = re.split(r'\s1\s|\sone\s', parts[1])
        options_list = [o.strip().strip(',').strip('.') for o in options_raw if len(o.strip()) > 2]
        
        target_match = re.search(r"(?:model's|unit's)\s+(.*?)\s+can be", header, re.IGNORECASE)
        target = target_match.group(1).strip() if target_match else "Equipment"
        
        return {"type": "nested", "target": target, "options": options_list}

    # 2. Simple Replacement
    swap_match = re.search(r"(?:model's|unit's)\s+(.*?)\s+can be replaced with\s+(?:1\s+)?(.*)", text, re.IGNORECASE)
    if swap_match:
        return {
            "type": "swap", 
            "target": swap_match.group(1).strip(), 
            "replacement": swap_match.group(2).strip().strip('.')
        }

    return {"type": "simple", "text": text}

@st.dialog("40K Unit Details", width="large")
def show_40k_details(unit_id, entry_id=None, detachment_id=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM view_40k_datasheet_complete WHERE ID = %s", (unit_id,))
    details = cursor.fetchone()
    if details:
        col1, col2 = st.columns([0.3, 0.7])
        with col1: 
            st.image(details['Image'], use_container_width=True)
        with col2:
            st.subheader(details['Unit_Name'])
            m_cols = st.columns(6)
            m_cols[0].metric("M", details['M'])
            m_cols[1].metric("T", details['T'])
            m_cols[2].metric("Sv", details['Sv'])
            m_cols[3].metric("W", details['W'])
            m_cols[4].metric("Ld", details['Ld'])
            m_cols[5].metric("OC", details['OC'])
            st.write(f"**Keywords:** {details['Keywords']}")
        
 # The Tabs Definition
    t1, t2, t3, t4 = st.tabs(["⚔️ Weapons", "📜 Rules", "✨ Enhancements", "👥 Composition"])

    with t1:
        # 1. Fetch active selections
        cursor.execute("SELECT option_text FROM play_armylist_wargear_selections WHERE entry_id = %s", (entry_id,))
        active_selections = [r['option_text'] for r in cursor.fetchall()]

        # 2. Update Helper
        def update_wgear(text, ent_id, is_active):
            conn_cb = get_db_connection()
            cur_cb = conn_cb.cursor()
            if is_active:
                cur_cb.execute("INSERT INTO play_armylist_wargear_selections (entry_id, option_text) VALUES (%s, %s)", (ent_id, text))
            else:
                cur_cb.execute("DELETE FROM play_armylist_wargear_selections WHERE entry_id = %s AND option_text = %s", (ent_id, text))
            conn_cb.commit()
            conn_cb.close()

        # 3. Render Options logic
        cursor.execute("SELECT description FROM waha_datasheets_options WHERE datasheet_id = %s", (unit_id,))
        options = cursor.fetchall()
        removed_names = []

        if options:
            with st.expander("🔄 Wargear Options", expanded=True):
                for opt in options:
                    desc = opt['description']
                    if not desc: continue
                    parsed = parse_wargear_option(desc)
                    
                    if parsed["type"] == "nested":
                        st.write(f"**Replace {parsed['target']} with:**")
                        current_choice = next((o for o in parsed['options'] if f"{parsed['target']} -> {o}" in active_selections), "Default")
                        
                        choice = st.radio(f"Select for {parsed['target']}", ["Default"] + parsed["options"], 
                                          index=(["Default"] + parsed["options"]).index(current_choice),
                                          key=f"nest_{hash(desc)}_{entry_id}")
                        
                        if choice != current_choice:
                            if current_choice != "Default": update_wgear(f"{parsed['target']} -> {current_choice}", entry_id, False)
                            if choice != "Default": update_wgear(f"{parsed['target']} -> {choice}", entry_id, True)
                            st.rerun()
                        if choice != "Default": removed_names.append(parsed['target'].lower())
                    
                    else:
                        is_on = desc in active_selections
                        if st.checkbox(desc, value=is_on, key=f"chk_{hash(desc)}_{entry_id}"):
                            if not is_on: 
                                update_wgear(desc, entry_id, True)
                                st.rerun()
                            if parsed.get("type") == "swap": removed_names.append(parsed["target"].lower())
                        elif is_on:
                            update_wgear(desc, entry_id, False)
                            st.rerun()

        # 4. Weapons Display
        cursor.execute("SELECT name, range_val, attacks, bs_ws, ap, damage FROM waha_datasheets_wargear WHERE datasheet_id = %s", (unit_id,))
        weapon_rows = cursor.fetchall()
        
        display_data = []
        for w in weapon_rows:
            name = w['name']
            if name.lower() in removed_names:
                name = f"~~{name}~~ 🚫"
            display_data.append({"Weapon": name, "Range": w['range_val'], "A": w['attacks'], "BS/WS": w['bs_ws'], "AP": w['ap'], "D": w['damage']})
        
        st.dataframe(pd.DataFrame(display_data), hide_index=True, use_container_width=True)

    # ... [Keep t2, t3, t4 logic here] ...
        
        # TAB 2: RULES
        with t2:
            cursor.execute("SELECT a.name, a.description FROM waha_datasheets_abilities da JOIN waha_abilities a ON da.ability_id = a.id WHERE da.datasheet_id = %s", (unit_id,))
            for ab in cursor.fetchall(): 
                st.markdown(f"**{ab['name']}**: {ab['description']}")
        
        # TAB 3: ENHANCEMENTS (WITH ARMY-WIDE VALIDATION)
        with t3:
            is_character = "Character" in details['Keywords']
            is_epic = "Epic Hero" in details['Keywords']
            
            if is_character and not is_epic and detachment_id and entry_id:
                st.write("### ✨ Available Enhancements")
                
                # 1. Fetch selection for THIS specific model
                cursor.execute("SELECT enhancement_id FROM play_armylist_enhancements WHERE entry_id = %s", (entry_id,))
                this_model_enh = [r['enhancement_id'] for r in cursor.fetchall()]
                
                # 2. Fetch ALL enhancements in the ENTIRE army for uniqueness check
                cursor.execute("""
                    SELECT e.enhancement_id FROM play_armylist_enhancements e
                    JOIN play_armylist_entries ent ON e.entry_id = ent.entry_id
                    WHERE ent.list_id = (SELECT list_id FROM play_armylist_entries WHERE entry_id = %s)
                """, (entry_id,))
                all_used_enhs = [r['enhancement_id'] for r in cursor.fetchall()]
                
                # 3. Fetch enhancements for the current detachment
                cursor.execute("SELECT * FROM view_40k_enhancement_picker WHERE detachment_id = %s", (detachment_id,))
                available_enhs = cursor.fetchall()
                
                if not available_enhs:
                    st.info("No enhancements found for this detachment.")
                
                for enh in available_enhs:
                    is_on = enh['enhancement_id'] in this_model_enh
                    is_taken_elsewhere = enh['enhancement_id'] in all_used_enhs and not is_on
                    
                    # Rules: 1 per model, unique across army
                    disabled = is_taken_elsewhere or (len(this_model_enh) > 0 and not is_on)
                    
                    label = f"{enh['enhancement_name']} (+{enh['cost']} pts)"
                    if is_taken_elsewhere:
                        label += " 🚫 (Taken by another unit)"

                    if st.checkbox(label, value=is_on, disabled=disabled, key=f"enh_{enh['enhancement_id']}_{entry_id}"):
                        if not is_on:
                            cursor.execute("INSERT INTO play_armylist_enhancements (entry_id, enhancement_id, cost) VALUES (%s, %s, %s)", 
                                           (entry_id, enh['enhancement_id'], enh['cost']))
                            conn.commit()
                            st.rerun()
                    elif is_on:
                        cursor.execute("DELETE FROM play_armylist_enhancements WHERE entry_id = %s AND enhancement_id = %s", 
                                       (entry_id, enh['enhancement_id']))
                        conn.commit()
                        st.rerun()
                    st.caption(enh['description'])
            
            elif is_epic:
                st.warning("🚫 Epic Heroes cannot take Enhancements.")
            elif not entry_id:
                st.info("💡 Add this unit to your list to select Enhancements.")
            else:
                st.info("💡 Only non-Epic Hero Characters can take Enhancements.")
                
    conn.close()

def run_40k_builder(active_list):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    active_id = active_list['list_id']
    active_det_id = active_list.get('waha_detachment_id')
    primary_army = active_list['faction_primary']

    # --- 1. DETACHMENT SELECTOR ---
    cursor.execute("SELECT id FROM waha_factions WHERE name = %s", (primary_army,))
    f_res = cursor.fetchone()
    if f_res:
        try:
            cursor.execute("""
                SELECT id, name FROM waha_detachments 
                WHERE faction_id = %s OR faction_id IN (
                    SELECT id FROM waha_factions WHERE parent_id = %s
                )
            """, (f_res['id'], f_res['id']))
        except:
            cursor.execute("SELECT id, name FROM waha_detachments WHERE faction_id = %s", (f_res['id'],))
        
        dets = cursor.fetchall()
        det_map = {d['name']: d['id'] for d in dets}
        if det_map:
            current_idx = 0
            if active_det_id:
                for i, name in enumerate(det_map.keys()):
                    if det_map[name] == active_det_id:
                        current_idx = i
            
            sel_det = st.sidebar.selectbox("Select Detachment", list(det_map.keys()), index=current_idx)
            
            if det_map[sel_det] != active_det_id:
                cursor.execute("UPDATE play_armylists SET waha_detachment_id = %s WHERE list_id = %s", (det_map[sel_det], active_id))
                conn.commit()
                st.rerun()
            active_det_id = det_map[sel_det]

    # --- 2. LIBRARY SIDEBAR ---
    st.sidebar.divider()
    search = st.sidebar.text_input(f"Search {primary_army} Units")
    
    lib_query = """
        SELECT * FROM view_master_picker 
        WHERE `system` = '40K' 
        AND (faction = %s OR faction = (
            SELECT COALESCE(f.name, %s) FROM waha_factions f 
            JOIN waha_detachments d ON f.id = d.faction_id 
            WHERE d.id = %s LIMIT 1
        ))
        AND name LIKE %s LIMIT 20
    """
    cursor.execute(lib_query, (primary_army, primary_army, active_det_id, f"%{search}%"))
    
    for unit in cursor.fetchall():
        c1, c2, c3 = st.sidebar.columns([0.6, 0.2, 0.2])
        c1.write(f"**{unit['name']}**  \n{unit['points']} pts")
        if c2.button("Add", key=f"add_{unit['id']}"):
            cursor.callproc('AddUnit', (active_id, str(unit['id']), 1))
            conn.commit()
            st.rerun()
        if c3.button("👁️", key=f"lib_det_{unit['id']}"):
            show_40k_details(unit['id'], detachment_id=active_det_id)

    # --- 3. MAIN ROSTER PANEL ---
    st.title(f"Roster: {active_list['list_name']}")
    cursor.callproc('GetArmyRoster', (active_id,))
    
    results = list(cursor.stored_results())
    if results:
        for res in results:
            data = res.fetchall()
            if data:
                df = pd.DataFrame(data)
                total_val = pd.to_numeric(df['Total_Pts'], errors='coerce').sum()
                st.metric("Total Points", f"{int(total_val)} / {active_list['point_limit']}")

                for i, row in df.iterrows():
                    r1, r2, r3 = st.columns([0.8, 0.1, 0.1])
                    with r1:
                        st.write(f"**{row['Qty']}x {row['Unit']}** (M:{row['M']} T:{row['T']}) — {row['Total_Pts']} pts")
                    with r2:
                        if st.button("👁️", key=f"ros_det_{row['entry_id']}"):
                            show_40k_details(row['unit_id'], entry_id=row['entry_id'], detachment_id=active_det_id)
                    with r3:
                        if st.button("❌", key=f"del_{row['entry_id']}"):
                            cursor.execute("DELETE FROM play_armylist_entries WHERE entry_id = %s", (row['entry_id'],))
                            conn.commit()
                            st.rerun()
                
                st.divider()
                if st.button("🗑️ Clear Entire Roster"):
                    cursor.execute("DELETE FROM play_armylist_entries WHERE list_id = %s", (active_id,))
                    conn.commit()
                    st.rerun()
            else:
                st.metric("Total Points", "0")
                st.info("Roster is empty.")
    
    conn.close()
#  Enhancements logic complete