import streamlit as st
import pandas as pd
from database_utils import get_db_connection

@st.dialog("OPR Unit Details", width="large")
def show_opr_details(unit_id, entry_id=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT name, army, quality, defense, wounds, image_url FROM opr_units WHERE opr_unit_id = %s", (unit_id,))
    details = cursor.fetchone()
    if details:
        col1, col2 = st.columns([0.3, 0.7])
        with col1: 
            if details['image_url']: st.image(details['image_url'], use_container_width=True)
        with col2:
            st.subheader(details['name'])
            q1, q2, q3 = st.columns(3)
            q1.metric("QUA", f"{details['quality']}+"); q2.metric("DEF", f"{details['defense']}+"); q3.metric("W", details['wounds'])
        
        tab1, tab2 = st.tabs(["⚔️ Active Weapons", "✨ Upgrades"])
        
        bought_upgrades = []
        if entry_id:
            cursor.execute("SELECT upgrade_id FROM play_armylist_upgrades WHERE entry_id = %s", (entry_id,))
            bought_upgrades = [r['upgrade_id'] for r in cursor.fetchall()]

        with tab2:
            if entry_id:
                st.success(f"⚙️ Customizing Unit #{entry_id}")
                cursor.execute("SELECT id, section_label, option_label, cost FROM opr_unit_upgrades WHERE unit_id = %s ORDER BY section_label", (unit_id,))
                upgrades = cursor.fetchall()
                current_sec = ""
                for up in upgrades:
                    if up['section_label'] != current_sec:
                        current_sec = up['section_label']; st.markdown(f"--- \n**{current_sec}**")
                    is_on = up['id'] in bought_upgrades
                    if st.checkbox(f"{up['option_label']} (+{up['cost']} pts)", value=is_on, key=f"up_{up['id']}_{entry_id}"):
                        if not is_on:
                            cursor.execute("INSERT INTO play_armylist_upgrades (entry_id, upgrade_id) VALUES (%s, %s)", (entry_id, up['id']))
                            conn.commit(); st.rerun()
                    elif is_on:
                        cursor.execute("DELETE FROM play_armylist_upgrades WHERE entry_id = %s AND upgrade_id = %s", (entry_id, up['id']))
                        conn.commit(); st.rerun()

        with tab1:
            cursor.execute("SELECT weapon_label, attacks, ap, special_rules FROM opr_unitweapons WHERE unit_id = %s", (unit_id,))
            base_weapons = cursor.fetchall()
            replaced_keywords = []
            upgrade_weapons = []
            if bought_upgrades:
                cursor.execute(f"SELECT option_label, section_label FROM opr_unit_upgrades WHERE id IN ({','.join(['%s']*len(bought_upgrades))})", tuple(bought_upgrades))
                for active_up in cursor.fetchall():
                    if "Replace" in active_up['section_label']:
                        replaced_keywords.append(active_up['section_label'].replace("Replace ", "").replace("any ", "").strip())
                    if "(" in active_up['option_label']:
                        upgrade_weapons.append({"Weapon": f"✨ **{active_up['option_label']}**", "A": "-", "AP": "-", "Rules": "Active"})
            
            final_display = []
            for w in base_weapons:
                is_replaced = any(k.lower() in w['weapon_label'].lower() for k in replaced_keywords)
                if is_replaced:
                    final_display.append({"Weapon": f"~~🚫 {w['weapon_label']}~~", "A": f"~~{w['attacks']}~~", "AP": f"~~{w['ap']}~~", "Rules": f"~~{w['special_rules']}~~"})
                else:
                    final_display.append({"Weapon": w['weapon_label'], "A": w['attacks'], "AP": w['ap'], "Rules": w['special_rules']})
            final_display.extend(upgrade_weapons)
            st.table(final_display)
    conn.close()

def run_opr_builder(active_list):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    active_id = active_list['list_id']
    
    # Library Sidebar
    st.sidebar.header("OPR Library")
    allowed_armies = [active_list['faction_primary']]
    if active_list['faction_secondary'] and active_list['faction_secondary'] != 'None':
        allowed_armies.append(active_list['faction_secondary'])
    
    search = st.sidebar.text_input("Search OPR Units")
    placeholders = ', '.join(['%s'] * len(allowed_armies))
    cursor.execute(f"SELECT * FROM view_master_picker WHERE `system` = 'OPR' AND faction IN ({placeholders}) AND name LIKE %s LIMIT 20", (*allowed_armies, f"%{search}%"))
    
    for unit in cursor.fetchall():
        c1, c2, c3 = st.sidebar.columns([0.6, 0.2, 0.2])
        c1.write(f"**{unit['name']}**\n{unit['points']} pts")
        if c2.button("Add", key=f"add_opr_{unit['id']}"):
            cursor.callproc('AddUnit', (active_id, str(unit['id']), 1))
            conn.commit(); st.rerun()
        if c3.button("👁️", key=f"det_opr_{unit['id']}"):
            show_opr_details(unit['id'])

    # Roster Main Panel
    st.title(f"OPR Roster: {active_list['list_name']}")
    cursor.callproc('GetArmyRoster', (active_id,))
    for result in cursor.stored_results():
        df = pd.DataFrame(result.fetchall())
        if not df.empty:
            st.metric("Total Points", f"{int(pd.to_numeric(df['Total_Pts'], errors='coerce').sum())}")
            for i, row in df.iterrows():
                r1, r2, r3 = st.columns([0.8, 0.1, 0.1])
                r1.write(f"**{row['Qty']}x {row['Unit']}** (Q:{row['QUA']} D:{row['DEF']}) — {row['Total_Pts']} pts")
                if r2.button("👁️", key=f"rd_opr_{row['entry_id']}"):
                    show_opr_details(row['unit_id'], row['entry_id'])
                if r3.button("❌", key=f"del_opr_{row['entry_id']}"):
                    cursor.execute("DELETE FROM play_armylist_entries WHERE entry_id = %s", (row['entry_id'],))
                    conn.commit(); st.rerun()
    conn.close()
