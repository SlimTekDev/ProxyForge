import streamlit as st
import mysql.connector
import pandas as pd

def get_db_connection():
    return mysql.connector.connect(
        host="localhost", user="root", password="Warhammer40K!", 
        database="wargaming_erp", connect_timeout=60, buffered=True
    )

st.set_page_config(layout="wide", page_title="Wargaming ERP")

@st.dialog("Unit Details", width="large")
def show_unit_details(unit_id, system, entry_id=None, detachment_id=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if system == "40K":
        cursor.execute("SELECT * FROM view_40k_datasheet_complete WHERE ID = %s", (unit_id,))
        details = cursor.fetchone()
        if details:
            col1, col2 = st.columns([0.3, 0.7])
            with col1: st.image(details['Image'], use_container_width=True)
            with col2:
                st.subheader(details['Unit_Name'])
                m_cols = st.columns(6)
                # FIXED: Accessing list elements by index
                m_cols[0].metric("M", details['M']); m_cols[1].metric("T", details['T']); m_cols[2].metric("Sv", details['Sv'])
                m_cols[3].metric("W", details['W']); m_cols[4].metric("Ld", details['Ld']); m_cols[5].metric("OC", details['OC'])
                st.write(f"**Keywords:** {details['Keywords']}")
            t1, t2, t3 = st.tabs(["⚔️ Weapons", "📜 Rules", "✨ Enhancements"])
            with t1:
                cursor.execute("SELECT name, range_val as 'Range', attacks as A, bs_ws as WS, ap as AP, damage as D FROM waha_datasheets_wargear WHERE datasheet_id = %s", (unit_id,))
                st.dataframe(pd.DataFrame(cursor.fetchall()), hide_index=True)
            with t2:
                cursor.execute("SELECT a.name, a.description FROM waha_datasheets_abilities da JOIN waha_abilities a ON da.ability_id = a.id WHERE da.datasheet_id = %s", (unit_id,))
                for ab in cursor.fetchall(): st.markdown(f"**{ab['name']}**: {ab['description']}")
            with t3:
                if detachment_id:
                    cursor.execute("SELECT * FROM view_40k_enhancement_picker WHERE detachment_id = %s", (detachment_id,))
                    enhs = cursor.fetchall()
                    if enhs:
                        for enh in enhs: st.write(f"**{enh['enhancement_name']}** ({enh['cost']} pts)")
                    else: st.info("No enhancements for this detachment.")
    else:
        cursor.execute("SELECT * FROM opr_units WHERE opr_unit_id = %s", (unit_id,))
        d = cursor.fetchone()
        if d: 
            st.subheader(d['name'])
            q_cols = st.columns(3)
            q_cols[0].metric("QUA", f"{d['quality']}+"); q_cols[1].metric("DEF", f"{d['defense']}+"); q_cols[2].metric("W", d['wounds'])
    conn.close()

try:
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    st.sidebar.title("Army Management")
    
    # --- RESTORED: ADD NEW ARMY ---
    with st.sidebar.expander("➕ Create New List"):
        new_name = st.text_input("List Name")
        new_sys_label = st.selectbox("System", ["40K", "OPR"])
        db_sys = "40K_10E" if new_sys_label == "40K" else "OPR"
        cursor.execute("SELECT DISTINCT faction FROM view_master_picker WHERE `system` = %s", (new_sys_label,))
        fac_options = sorted([f['faction'] for f in cursor.fetchall()])
        p_fac = st.selectbox("Primary Army", fac_options)
        new_pts = st.number_input("Points", value=2000, step=250)
        if st.button("Save List"):
            cursor.execute("INSERT INTO play_armylists (list_name, game_system, point_limit, faction_primary) VALUES (%s, %s, %s, %s)", 
                           (new_name, db_sys, new_pts, p_fac))
            conn.commit(); st.rerun()

    cursor.execute("SELECT * FROM play_armylists")
    all_lists = cursor.fetchall()
    
    if all_lists:
        list_map = {f"{l['list_name']} ({l['game_system']})": l for l in all_lists}
        sel_label = st.sidebar.selectbox("Active List", list_map.keys())
        active_list = list_map[sel_label]
        active_id = active_list['list_id']
        picker_sys = "40K" if active_list['game_system'] == "40K_10E" else "OPR"

        # DETACHMENT SELECTOR
        active_det_id = active_list.get('waha_detachment_id')
        if picker_sys == "40K":
            cursor.execute("SELECT id FROM waha_factions WHERE name = %s", (active_list['faction_primary'],))
            f_res = cursor.fetchone()
            if f_res:
                cursor.execute("SELECT id, name FROM waha_detachments WHERE faction_id = %s", (f_res['id'],))
                dets = cursor.fetchall()
                det_map = {d['name']: d['id'] for d in dets}
                sel_det = st.sidebar.selectbox("Detachment", list(det_map.keys()))
                if det_map[sel_det] != active_det_id:
                    cursor.execute("UPDATE play_armylists SET waha_detachment_id = %s WHERE list_id = %s", (det_map[sel_det], active_id))
                    conn.commit(); st.rerun()
                active_det_id = det_map[sel_det]

        st.sidebar.divider()
        search = st.sidebar.text_input("Search Library")
        allowed_armies = [active_list['faction_primary']]
        if active_list['faction_secondary'] and active_list['faction_secondary'] != 'None':
            allowed_armies.append(active_list['faction_secondary'])
            
        placeholders = ', '.join(['%s'] * len(allowed_armies))
        cursor.execute(f"SELECT * FROM view_master_picker WHERE `system` = %s AND faction IN ({placeholders}) AND name LIKE %s LIMIT 20", 
                       (picker_sys, *allowed_armies, f"%{search}%"))
        
        for unit in cursor.fetchall():
            c1, c2, c3 = st.sidebar.columns([0.6, 0.2, 0.2])
            c1.write(f"**{unit['name']}**\n{unit['points']} pts")
            if c2.button("Add", key=f"a_{unit['id']}"):
                cursor.callproc('AddUnit', (active_id, str(unit['id']), 1))
                conn.commit(); st.rerun()
            if c3.button("👁️", key=f"d_{unit['id']}"):
                show_unit_details(unit['id'], picker_sys, detachment_id=active_det_id)

        # --- RESTORED: ROSTER WITH DETAILS & REMOVE ---
        st.title(f"Roster: {active_list['list_name']}")
        cursor.callproc('GetArmyRoster', (active_id,))
        for res in cursor.stored_results():
            df = pd.DataFrame(res.fetchall())
            if not df.empty:
                st.metric("Total Points", f"{int(pd.to_numeric(df['Total_Pts'], errors='coerce').sum())} / {active_list['point_limit']}")
                for i, row in df.iterrows():
                    r1, r2, r3 = st.columns([0.8, 0.1, 0.1])
                    r1.write(f"**{row['Qty']}x {row['Unit']}** — *{row['Total_Pts']} pts*")
                    if r2.button("👁️", key=f"rd_{i}"):
                        show_unit_details(row['unit_id'], picker_sys, row['entry_id'], active_det_id)
                    if r3.button("❌", key=f"del_{i}"):
                        cursor.execute("DELETE FROM play_armylist_entries WHERE entry_id = %s", (row['entry_id'],))
                        conn.commit(); st.rerun()
                
                if st.button("🗑️ Clear Roster"):
                    cursor.execute("DELETE FROM play_armylist_entries WHERE list_id = %s", (active_id,))
                    conn.commit(); st.rerun()

    conn.close()
except Exception as e:
    st.error(f"Application Error: {e}")





