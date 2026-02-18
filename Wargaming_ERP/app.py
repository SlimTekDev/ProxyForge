import streamlit as st
import pandas as pd
from database_utils import get_db_connection
from opr_builder import run_opr_builder
from w40k_builder import run_40k_builder
from library_ui import run_library_ui  # We will create this file next

st.set_page_config(layout="wide", page_title="Wargaming ERP")

try:
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    st.sidebar.title("🛡️ Wargaming ERP")
    
    # --- 0. NAVIGATION ---
    st.sidebar.divider()
    page = st.sidebar.radio("🎮 Navigation", ["Army Builder", "Digital Library"])
    st.sidebar.divider()

    if page == "Digital Library":
        # --- DIGITAL LIBRARY PAGE ---
        st.title("📂 Digital STL Vault")
        run_library_ui() # This function handles search & filter
        
    else:
        # --- ARMY BUILDER PAGE ---
        # --- 1. LIST CREATION ---
        with st.sidebar.expander("➕ Create New List"):
            new_name = st.text_input("List Name")
            new_sys_label = st.selectbox("System", ["40K", "OPR"])
            
            opr_mode_slug = "grimdark-future" # Default
            if new_sys_label == "OPR":
                opr_mode = st.selectbox("Game Mode", [
                    "Grimdark Future", 
                    "Grimdark Future Firefight",
                    "Age of Fantasy",
                    "Age of Fantasy Skirmish",
                    "Age of Fantasy Regiments"
                ])
                mode_map = {
                    "Grimdark Future": "grimdark-future",
                    "Grimdark Future Firefight": "grimdark-future-firefight",
                    "Age of Fantasy": "age-of-fantasy",
                    "Age of Fantasy Skirmish": "age-of-fantasy-skirmish",
                    "Age of Fantasy Regiments": "age-of-fantasy-regiments"
                }
                opr_mode_slug = mode_map[opr_mode]

            db_sys = "40K_10E" if new_sys_label == "40K" else "OPR"
            
            cursor.execute("SELECT DISTINCT faction FROM view_master_picker WHERE `game_system` = %s", (new_sys_label,))
            fac_options = sorted([f['faction'] for f in cursor.fetchall()])
            p_fac = st.selectbox("Primary Army", fac_options)
            
            new_pts = st.number_input("Points", value=2000, step=250)
            
            if st.button("Save List"):
                cursor.execute("INSERT INTO play_armylists (list_name, game_system, point_limit, faction_primary) VALUES (%s, %s, %s, %s)", 
                               (new_name, db_sys, new_pts, p_fac))
                
                if new_sys_label == "OPR":
                    cursor.execute("""
                        INSERT INTO opr_army_settings (army_name, setting_name) 
                        VALUES (%s, %s) 
                        ON DUPLICATE KEY UPDATE setting_name = VALUES(setting_name)
                    """, (p_fac, opr_mode_slug))
                
                conn.commit()
                st.rerun()

        # --- 2. LIST SELECTION ---
        cursor.execute("SELECT * FROM play_armylists")
        all_lists = cursor.fetchall()
        if all_lists:
            list_map = {f"{l['list_name']} ({l['game_system']})": l for l in all_lists}
            sel_label = st.sidebar.selectbox("Active Roster", list_map.keys())
            active_list = list_map[sel_label]
            
            if active_list['game_system'] == 'OPR':
                run_opr_builder(active_list)
            else:
                run_40k_builder(active_list)
        else:
            st.warning("Please create a list in the sidebar to begin.")

    conn.close()
except Exception as e:
    st.error(f"System Error: {e}")
