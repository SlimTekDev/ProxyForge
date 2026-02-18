import streamlit as st
from database_utils import get_db_connection
from opr_builder import run_opr_builder
from w40k_builder import run_40k_builder

st.set_page_config(layout="wide", page_title="Wargaming ERP")

try:
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    st.sidebar.title("🛡️ Wargaming ERP")

    # List Creation
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

    # List Selection
    cursor.execute("SELECT * FROM play_armylists")
    all_lists = cursor.fetchall()
    if all_lists:
        list_map = {f"{l['list_name']} ({l['game_system']})": l for l in all_lists}
        sel_label = st.sidebar.selectbox("Active List", list_map.keys())
        active_list = list_map[sel_label]
        
        # Navigation
        if active_list['game_system'] == 'OPR':
            run_opr_builder(active_list)
        else:
            run_40k_builder(active_list)
    else:
        st.warning("Please create a list in the sidebar to begin.")

    conn.close()
except Exception as e:
    st.error(f"System Error: {e}")
