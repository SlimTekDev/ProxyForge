import streamlit as st
import pandas as pd
from database_utils import get_db_connection
from opr_builder import run_opr_builder
from w40k_builder import run_40k_builder
from library_ui import run_library_ui
from army_book_ui import run_army_book_ui
from w40k_army_book_ui import run_w40k_army_book_ui

try:
    from alpha_logging import log_page_view, log_feature
except ImportError:
    def log_page_view(_): pass
    def log_feature(*_, **__): pass

st.set_page_config(layout="wide", page_title="ProxyForge")

try:
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    st.sidebar.title("⚔️ ProxyForge")
    
    # --- 0. NAVIGATION ---
    st.sidebar.divider()
    page = st.sidebar.radio("🎮 Navigation", [
        "OPR Army Builder",
        "40K Army Builder",
        "OPR Army Book Reference",
        "40K Army Book Reference",
        "Digital Library"
    ])
    st.sidebar.divider()
    log_page_view(page)

    if page == "OPR Army Book Reference":
        run_army_book_ui()
    elif page == "40K Army Book Reference":
        run_w40k_army_book_ui()
    elif page == "Digital Library":
        st.title("📂 Digital STL Vault")
        run_library_ui()
    elif page == "OPR Army Builder":
        # --- OPR LIST CREATION ---
        with st.sidebar.expander("➕ Create New List"):
            new_name = st.text_input("List Name", key="opr_new_name")
            opr_mode = st.selectbox("Game Mode", [
                "Grimdark Future",
                "Grimdark Future Firefight",
                "Age of Fantasy",
                "Age of Fantasy Skirmish",
                "Age of Fantasy Regiments"
            ], key="opr_mode")
            mode_map = {
                "Grimdark Future": "grimdark-future",
                "Grimdark Future Firefight": "grimdark-future-firefight",
                "Age of Fantasy": "age-of-fantasy",
                "Age of Fantasy Skirmish": "age-of-fantasy-skirmish",
                "Age of Fantasy Regiments": "age-of-fantasy-regiments"
            }
            opr_mode_slug = mode_map[opr_mode]
            cursor.execute("SELECT DISTINCT faction FROM view_master_picker WHERE `game_system` = %s", ("OPR",))
            fac_options = sorted([f['faction'] for f in cursor.fetchall()])
            p_fac = st.selectbox("Primary Army", fac_options, key="opr_fac")
            new_pts = st.number_input("Points", value=2000, step=250, key="opr_pts")
            if st.button("Save List", key="opr_save"):
                cursor.execute(
                    "INSERT INTO play_armylists (list_name, game_system, point_limit, faction_primary) VALUES (%s, %s, %s, %s)",
                    (new_name, "OPR", new_pts, p_fac)
                )
                cursor.execute("""
                    INSERT INTO opr_army_settings (army_name, setting_name)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE setting_name = VALUES(setting_name)
                """, (p_fac, opr_mode_slug))
                conn.commit()
                log_feature("list_created", detail="OPR")
                st.rerun()

        cursor.execute("SELECT * FROM play_armylists WHERE game_system = %s", ("OPR",))
        opr_lists = cursor.fetchall()
        if opr_lists:
            list_map = {f"{l['list_name']} ({l['point_limit']} pts)": l for l in opr_lists}
            sel_label = st.sidebar.selectbox("Active Roster", list_map.keys(), key="opr_roster")
            active_list = list_map[sel_label]
            run_opr_builder(active_list)
        else:
            st.warning("Create an OPR list in the sidebar to begin.")
    else:
        # --- 40K ARMY BUILDER ---
        with st.sidebar.expander("➕ Create New List"):
            new_name = st.text_input("List Name", key="40k_new_name")
            cursor.execute("SELECT DISTINCT faction FROM view_master_picker WHERE `game_system` = %s", ("40K",))
            fac_options = sorted([f['faction'] for f in cursor.fetchall()])
            p_fac = st.selectbox("Primary Army", fac_options, key="40k_fac")
            new_pts = st.number_input("Points", value=2000, step=250, key="40k_pts")
            if st.button("Save List", key="40k_save"):
                cursor.execute(
                    "INSERT INTO play_armylists (list_name, game_system, point_limit, faction_primary) VALUES (%s, %s, %s, %s)",
                    (new_name, "40K_10E", new_pts, p_fac)
                )
                conn.commit()
                log_feature("list_created", detail="40K")
                st.rerun()

        cursor.execute("SELECT * FROM play_armylists WHERE game_system = %s", ("40K_10E",))
        w40k_lists = cursor.fetchall()
        if w40k_lists:
            list_map = {f"{l['list_name']} ({l['point_limit']} pts)": l for l in w40k_lists}
            sel_label = st.sidebar.selectbox("Active Roster", list_map.keys(), key="40k_roster")
            active_list = list_map[sel_label]
            run_40k_builder(active_list)
        else:
            st.warning("Create a 40K list in the sidebar to begin.")

    conn.close()
except Exception as e:
    st.error(f"System Error: {e}")
