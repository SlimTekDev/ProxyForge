import streamlit as st
import pandas as pd
from database_utils import get_db_connection

#  ---- Stable Release 1.0 ----


def show_opr_gameday_view(active_list, roster_df, total_pts):
    """Surgical tactical sheet for OPR match play: Shows active gear and struck-through replaced gear."""
    st.title(f"📑 OPR Tactical Briefing: {active_list['list_name']}")
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    c1, c2 = st.columns([0.7, 0.3])
    with c1:
        st.write(f"**{active_list['faction_primary']}** | **{total_pts} / {active_list['point_limit']} pts**")
    with c2:
        if st.button("⬅️ Back to Editor", use_container_width=True):
            st.session_state.opr_gameday = False
            st.rerun()

    st.divider()

    import re

    # Helper for Unicode Strikethrough (Since st.table doesn't support Markdown ~~text~~)
    def strike(text):
        return ''.join([u'\u0336' + char for char in str(text)])

    for _, row in roster_df.iterrows():
        entry_id = row['entry_id']
        unit_id = row['unit_id']

        with st.container(border=True):
            # 1. HEADER: Tactical Stats
            h1, h2, h3, h4 = st.columns([0.4, 0.2, 0.2, 0.2])
            
            # Logic: [Models Per Unit] Name (Total Models)
            models_per_unit = row.get('size', 1)
            total_models = row['Qty'] * models_per_unit
            
            h1.markdown(f"### {row['Qty']}x {row['Unit']}")
            h1.caption(f"👥 **Squad Size:** {models_per_unit} | **Total Models:** {total_models}")
            
            h2.metric("QUA", f"{row['QUA']}+")
            h3.metric("DEF", f"{row['DEF']}+")
            h4.metric("PTS", row['Total_Pts'])


            # 2. DATA FETCH: Upgrades and Context
            cursor.execute("SELECT option_label FROM play_armylist_opr_upgrades WHERE entry_id = %s", (entry_id,))
            active_upgs = [r['option_label'] for r in cursor.fetchall()]

            cursor.execute("SELECT section_label, option_label FROM opr_unit_upgrades WHERE unit_id = %s", (unit_id,))
            upg_context = cursor.fetchall()

            # 3. WEAPONS: All Gear (Replaced gear gets Strikethrough)
            st.markdown("##### ⚔️ Arsenal")
            cursor.execute("SELECT weapon_label, attacks, ap, special_rules, count FROM opr_unitweapons WHERE unit_id = %s", (unit_id,))
            base_weapons = cursor.fetchall()
            
            final_weapons = []
            
            # Process Base Weapons
            for w in base_weapons:
                raw_name = w['weapon_label'].split('(')[0].strip()
                name_upper = raw_name.upper()
                
                is_replaced = False
                for upg in active_upgs:
                    ctx = next((c['section_label'] for c in upg_context if c['option_label'] == upg), "").upper()
                    if "REPLACE" in ctx and name_upper in ctx:
                        is_replaced = True
                        break
                
                range_match = re.search(r'(\d+")', w['weapon_label'])
                w_range = range_match.group(1) if range_match else "Melee"

                if is_replaced:
                    final_weapons.append({
                        "Weapon": f"{strike(raw_name)} 🚫",
                        "Range": strike(w_range),
                        "A": strike(w['attacks']), 
                        "AP": strike(w['ap'] if w['ap'] > 0 else "-"), 
                        "Rules": strike(w['special_rules'] if w['special_rules'] else "-")
                    })
                else:
                    final_weapons.append({
                        "Weapon": raw_name,
                        "Range": w_range,
                        "A": w['attacks'], 
                        "AP": w['ap'] if w['ap'] > 0 else "-", 
                        "Rules": w['special_rules'] if w['special_rules'] else "-"
                    })

            # Process Added Weapons (from Upgrades)
            for upg in active_upgs:
                if "(" in str(upg) and "A" in str(upg):
                    u_name = str(upg).split('(')[0].strip()
                    r_match = re.search(r'(\d+")', str(upg))
                    a_match = re.search(r'A(\d+)', str(upg))
                    ap_match = re.search(r'AP\((\d+)\)', str(upg))
                    
                    u_rules = "-"
                    inner_match = re.search(r'\((.*)\)', str(upg))
                    if inner_match:
                        guts = inner_match.group(1).split(',')
                        rules_list = [g.strip() for g in guts if not any(c in g for c in ['"', 'A', 'AP'])]
                        if rules_list:
                            u_rules = ", ".join(rules_list)

                    final_weapons.append({
                        "Weapon": f"⭐ {u_name}",
                        "Range": r_match.group(1) if r_match else "Melee",
                        "A": a_match.group(1) if a_match else "1",
                        "AP": ap_match.group(1) if ap_match else "-",
                        "Rules": u_rules
                    })

            if final_weapons:
                st.table(pd.DataFrame(final_weapons))

            # 4. RULES & SPELLS
            st.divider()
            col_r, col_s = st.columns([0.5, 0.5])
            
            with col_r:
                st.markdown("##### 📜 Rules")
                cursor.execute("SELECT rule_name, rating FROM view_opr_unit_rules_detailed WHERE unit_id = %s", (unit_id,))
                rules = cursor.fetchall()
                displayed_rules = set()
                for r in rules:
                    name = f"{r['rule_name']} ({r['rating']})" if r['rating'] else r['rule_name']
                    if name not in displayed_rules:
                        st.write(f"• {name}")
                        displayed_rules.add(name)

            with col_s:
                is_caster = any("Caster" in str(r['rule_name']) for r in rules) or \
                            any(key in str(u) for u in active_upgs for key in ["Archivist", "Psychic", "Caster"])
                
                if is_caster:
                    st.markdown("##### 🔮 Spells")
                    cursor.execute("SELECT name, threshold FROM opr_spells WHERE faction = %s", (active_list['faction_primary'],))
                    spells = cursor.fetchall()
                    if spells:
                        for s in spells:
                            st.write(f"• **{s['name']}** ({s['threshold']}+)")
    conn.close()



@st.dialog("OPR Unit Details", width="large")
def show_opr_details(unit_id, entry_id=None, faction=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 1. Fetch Core Stats (unit_id here must be the 'opr_unit_id')
    cursor.execute("SELECT * FROM view_opr_master_picker WHERE id = %s", (unit_id,))
    unit = cursor.fetchone()
    
    if unit:
        # --- DEFINITIVE STEP 1.5: VISUAL ROSTER UPDATE ---
        # Joining stl_library to stl_unit_links via mmf_id (varchar 50)
        # Filtering by unit_id (the opr_unit_id)
        cursor.execute("""
            SELECT l.preview_url, l.name 
            FROM stl_library l
            JOIN stl_unit_links ul ON l.mmf_id = ul.mmf_id
            WHERE ul.unit_id = %s 
            AND ul.is_default = 1
            LIMIT 1
        """, (unit_id,))
        default_stl = cursor.fetchone()

        if default_stl and default_stl['preview_url']:
            st.image(
                default_stl['preview_url'], 
                use_container_width=True, 
                caption=f"Visual Reference: {default_stl['name']}"
            )
        # -----------------------------------------------

        type_label = unit.get('generic_name') if unit.get('generic_name') else unit.get('faction', 'Unit')
        st.subheader(f"🛡️ {unit['name']} ({type_label})")
        
        # ... (Rest of your stat/tab logic)

        
        # 2. FETCH DATA EARLY
        cursor.execute("""
            SELECT rule_name, rating, description 
            FROM view_opr_unit_rules_detailed 
            WHERE unit_id = %s
        """, (unit_id,))
        all_rules_data = cursor.fetchall()

        active_upgrades = []
        if entry_id:
            cursor.execute("SELECT option_label FROM play_armylist_opr_upgrades WHERE entry_id = %s", (entry_id,))
            active_upgrades = [r['option_label'] for r in cursor.fetchall()]

        # 3. REACTIVE CASTER DETECTION
        is_caster_innate = any("Caster" in str(r['rule_name']) for r in all_rules_data)
        is_caster_upgraded = any("Caster" in str(upg) or "Psychic" in str(upg) for upg in active_upgrades)
        is_caster = is_caster_innate or is_caster_upgraded

        # 4. STAT METRICS
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Quality", f"{unit['QUA']}+")
        c2.metric("Defense", f"{unit['DEF']}+")
        
        cursor.execute("SELECT wounds FROM opr_units WHERE opr_unit_id = %s", (unit_id,))
        w_res = cursor.fetchone()
        wounds_val = w_res['wounds'] if w_res else 1
        c3.metric("Wounds", wounds_val if wounds_val else 1)
        
        c4.metric("Cost", f"{unit['points']}pts")
        
        # 5. UNIT COMPOSITION
        unit_size = unit.get('size', 1) if unit.get('size') else 1
        st.markdown(f"**Composition:** {unit_size} Model{'s' if unit_size > 1 else ''} per unit")
        
        if entry_id:
            cursor.execute("SELECT quantity FROM play_armylist_entries WHERE entry_id = %s", (entry_id,))
            q_res = cursor.fetchone()
            qty = q_res['quantity'] if q_res else 1
            total_models = qty * unit_size
            st.write(f"🔢 **Total Models in Squad:** {total_models}")

        if unit.get('is_hero'):
            st.caption("🛡️ *Hero: May join a multi-model unit (Tough <= 6).*")
            
        st.divider()

        # 6. DYNAMIC TABS
        tab_list = ["⚔️ Weapons", "📜 Special Rules", "🔄 Upgrades"]
        if is_caster:
            tab_list.append("🔮 Spells")
        
        tabs = st.tabs(tab_list)
        
        # --- TAB 0: WEAPONS ---
        with tabs[0]:
            st.write("### ⚔️ Standard Armament")
            def strike(text):
                return ''.join([u'\u0336' + char for char in str(text)])

            import pandas as pd
            import re

            if not entry_id:
                st.info("💡 Add unit to roster to see dynamic weapon swaps.")
                cursor.execute("SELECT weapon_label, attacks, ap, special_rules, count FROM opr_unitweapons WHERE unit_id = %s", (unit_id,))
                base_weapons = cursor.fetchall()
                if base_weapons: 
                    st.table(pd.DataFrame(base_weapons))
            else:
                cursor.execute("SELECT section_label, option_label FROM opr_unit_upgrades WHERE unit_id = %s", (unit_id,))
                upgrade_context = cursor.fetchall()
                cursor.execute("SELECT weapon_label, attacks, ap, special_rules, count FROM opr_unitweapons WHERE unit_id = %s", (unit_id,))
                base_weapons = cursor.fetchall()
                
                display_data = []
                for w in base_weapons:
                    raw_label = w['weapon_label']
                    name_clean = raw_label.split('(')[0].strip()
                    name_upper = name_clean.upper()
                    
                    is_replaced = False
                    for upg in active_upgrades:
                        ctx = next((c['section_label'] for c in upgrade_context if c['option_label'] == upg), "").upper()
                        if "REPLACE" in ctx and name_upper in ctx:
                            is_replaced = True
                            break
                    
                    range_match = re.search(r'(\d+")', raw_label)
                    w_range = range_match.group(1) if range_match else "Melee"
                    
                    display_data.append({
                        "Qty": f"{strike(w['count'])+'x'}" if is_replaced else f"{w['count']}x",
                        "Weapon": f"{strike(name_clean)} 🚫" if is_replaced else name_clean,
                        "Range": strike(w_range) if is_replaced else w_range,
                        "A": strike(w['attacks']) if is_replaced else w['attacks'],
                        "AP": strike(w['ap'] if w['ap'] > 0 else "-") if is_replaced else (w['ap'] if w['ap'] > 0 else "-"),
                        "Special Rules": strike(w['special_rules']) if is_replaced else (w['special_rules'] if w['special_rules'] else "-")
                    })
                
                for upg in active_upgrades:
                    if "(" in str(upg) and "A" in str(upg):
                        u_name = str(upg).split('(')[0].strip()
                        inner_match = re.search(r'\((.*)\)', str(upg))
                        if inner_match:
                            guts = inner_match.group(1)
                            guts_list = [g.strip() for g in guts.split(',')]
                            u_range, u_atk, u_ap = "Melee", "1", "-"
                            u_rules = []
                            for item in guts_list:
                                if '"' in item: u_range = item.replace('"', '') + '"'
                                elif item.startswith('A') and item[1:].isdigit(): u_atk = item[1:]
                                elif item.startswith('AP('): u_ap = item 
                                else: u_rules.append(item)
                            display_data.append({"Qty": "⭐", "Weapon": f"**{u_name}**", "Range": u_range, "A": u_atk, "AP": u_ap, "Special Rules": ", ".join(u_rules) if u_rules else "-"})

                st.dataframe(pd.DataFrame(display_data), hide_index=True, use_container_width=True)

        # --- TAB 1: SPECIAL RULES ---
        with tabs[1]:
            st.write("### 📜 Unit Special Rules")
            if all_rules_data:
                displayed_rules = set()
                for rule in all_rules_data:
                    display_name = rule['rule_name']
                    if rule['rating'] and rule['rating'] > 0:
                        display_name = f"{rule['rule_name']} ({rule['rating']})"
                    
                    if display_name in displayed_rules: continue
                    
                    with st.expander(f"**{display_name}**", expanded=False):
                        st.write(rule.get('description', '📚 Rule definition missing.'))
                    displayed_rules.add(display_name)
        # --- TAB 2: UPGRADES ---
        with tabs[2]:
            if not entry_id:
                st.info("💡 Add unit to roster to select upgrades.")
            else:
                st.write("### 🛠️ Select Upgrades")
                def update_opr_upg(label, cost, ent_id, is_active):
                    conn_cb = get_db_connection(); cur_cb = conn_cb.cursor()
                    if is_active:
                        cur_cb.execute("INSERT IGNORE INTO play_armylist_opr_upgrades (entry_id, option_label, cost) VALUES (%s, %s, %s)", (ent_id, label, cost))
                    else:
                        cur_cb.execute("DELETE FROM play_armylist_opr_upgrades WHERE entry_id = %s AND option_label = %s", (ent_id, label))
                    conn_cb.commit(); conn_cb.close()

                cursor.execute("SELECT section_label, option_label, cost FROM opr_unit_upgrades WHERE unit_id = %s ORDER BY id ASC", (unit_id,))
                available_upgrades = cursor.fetchall()
                if available_upgrades:
                    section_groups = []
                    current_section = None
                    seen_options = set() 
                    for u in available_upgrades:
                        label = u['option_label']
                        if label in seen_options: continue
                        seen_options.add(label)
                        needs_split = (current_section is None or u['section_label'] != current_section['label'])
                        if needs_split:
                            current_section = {"label": u['section_label'], "options": []}
                            section_groups.append(current_section)
                        current_section['options'].append(u)
                    
                    for s_idx, group in enumerate(section_groups):
                        st.markdown(f"**{group['label']}**")
                        is_radio = any(term in group['label'] for term in ["Replace", "Upgrade one", "Upgrade with one", "Take one"])
                        if is_radio:
                            current_val = next((o['option_label'] for o in group['options'] if o['option_label'] in active_upgrades), "Original")
                            radio_options = ["Original"] + [f"{o['option_label']} (+{o['cost']}pts)" for o in group['options']]
                            try: current_idx = radio_options.index(next(f for f in radio_options if current_val in f))
                            except: current_idx = 0
                            choice = st.radio(f"Sel_{s_idx}", radio_options, index=current_idx, key=f"opr_rad_{s_idx}_{entry_id}", label_visibility="collapsed")
                            clean_choice = choice.split(" (+")[0]
                            if clean_choice != current_val:
                                if current_val != "Original": update_opr_upg(current_val, 0, entry_id, False)
                                if clean_choice != "Original":
                                    cost = next(o['cost'] for o in group['options'] if o['option_label'] == clean_choice)
                                    update_opr_upg(clean_choice, cost, entry_id, True)
                                st.rerun()
                        else:
                            for o in group['options']:
                                is_on = o['option_label'] in active_upgrades
                                if st.checkbox(f"{o['option_label']} (+{o['cost']}pts)", value=is_on, key=f"chk_{o['option_label']}_{entry_id}"):
                                    if not is_on: update_opr_upg(o['option_label'], o['cost'], entry_id, True); st.rerun()
                                elif is_on: update_opr_upg(o['option_label'], o['cost'], entry_id, False); st.rerun()

        # --- TAB 3: SPELLS ---
        if is_caster:
            with tabs[3]:
                st.write(f"### 🔮 {unit['faction']} Spellbook")
                cursor.execute("SELECT name, threshold, description FROM opr_spells WHERE faction = %s", (unit['faction'],))
                spells = cursor.fetchall()
                for s in spells:
                    with st.expander(f"**{s['name']}** ({s['threshold']}+)"):
                        st.write(s['description'])

    conn.close()

def run_opr_builder(active_list):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    active_id = active_list['list_id']
    
    # --- 1. DATA PREP ---
    cursor.callproc('GetOPRArmyRoster', (active_id,))
    roster_df = pd.DataFrame()
    for result in cursor.stored_results():
        roster_df = pd.DataFrame(result.fetchall())
    
    total_pts = 0
    if not roster_df.empty:
        total_pts = int(pd.to_numeric(roster_df['Total_Pts'], errors='coerce').sum())

    # --- 2. SYSTEM IDENTIFICATION & TOGGLE ---
    cursor.execute("SELECT setting_name FROM opr_army_settings WHERE army_name = %s LIMIT 1", (active_list['faction_primary'],))
    system_res = cursor.fetchone()
    current_system = system_res['setting_name'] if system_res else 'grimdark-future'

    mode_display = {
        "grimdark-future": "Grimdark Future",
        "grimdark-future-firefight": "Grimdark Future Firefight",
        "age-of-fantasy": "Age of Fantasy",
        "age-of-fantasy-skirmish": "Age of Fantasy Skirmish",
        "age-of-fantasy-regiments": "Age of Fantasy Regiments"
    }

    with st.sidebar.expander("⚙️ OPR System Settings"):
        current_display = mode_display.get(current_system, "Grimdark Future")
        new_mode_name = st.selectbox("Target System", options=list(mode_display.values()), 
                                     index=list(mode_display.values()).index(current_display), key=f"sys_toggle_{active_id}")
        mode_slug = next(k for k, v in mode_display.items() if v == new_mode_name)
        if mode_slug != current_system:
            cursor.execute("UPDATE opr_army_settings SET setting_name = %s WHERE army_name = %s", (mode_slug, active_list['faction_primary']))
            conn.commit(); st.rerun()

    # --- 3. MODE TOGGLE ---
    if 'opr_gameday' not in st.session_state: st.session_state.opr_gameday = False
    if st.session_state.opr_gameday:
        show_opr_gameday_view(active_list, roster_df, total_pts)
        conn.close(); return 

    # --- 4. LIBRARY SIDEBAR (Surgical & Visible) ---
    st.sidebar.header(f"OPR Library ({current_system})")
    
    primary_fac = active_list['faction_primary'].strip()
    search = st.sidebar.text_input("Search (e.g. 'Brother')", key=f"search_opr_{active_id}")
    
    # 1. Fetch Units (Simplified Query)
    lib_query = """
        SELECT * FROM view_opr_master_picker 
        WHERE (faction = %s OR faction = 'Prime Brothers' OR faction = 'Battle Brothers')
        AND game_system = %s
    """
    params = [primary_fac, current_system]
    if search:
        lib_query += " AND name LIKE %s"
        params.append(f"%{search}%")
    
    lib_query += " ORDER BY name ASC LIMIT 40"
    cursor.execute(lib_query, tuple(params))
    lib_results = cursor.fetchall()

    if not lib_results:
        st.sidebar.warning("No units found. Try a broader search.")
    
    # 2. Rendering Loop (Simplified for Sidebar stability)
    for unit in lib_results:
        u_id = unit['id']
        u_size = unit.get('size', 1)
        comp = f"[{u_size} models]" if u_size > 1 else "[Hero]"
        
        # We use a single markdown block for the info to prevent column collapse
        st.sidebar.markdown(f"**{unit['name']}** {comp}")
        st.sidebar.caption(f"{unit['faction']} — **{unit['points']} pts**")
        
        # Small buttons side-by-side
        btn_col1, btn_col2 = st.sidebar.columns(2)
        if btn_col1.button("➕ Add", key=f"add_lib_{u_id}_{active_id}", use_container_width=True):
            cursor.callproc('AddUnit', (active_id, str(u_id), 1))
            conn.commit()
            st.rerun()
            
        if btn_col2.button("👁️ Info", key=f"det_lib_{u_id}_{active_id}", use_container_width=True):
            show_opr_details(u_id, entry_id=None, faction=unit['faction'])
        
        st.sidebar.divider()

    # --- 5. ROSTER MAIN PANEL ---
    col_t, col_b = st.columns([0.7, 0.3])
    col_t.title(f"OPR Roster: {active_list['list_name']}")
    if col_b.button("📑 Game-Day View", use_container_width=True):
        st.session_state.opr_gameday = True; st.rerun()

    if not roster_df.empty:
        st.metric("Total Points", f"{total_pts} / {active_list['point_limit']}")
        for i, row in roster_df.iterrows():
            with st.container(border=True):
                r1, r2, r3 = st.columns([0.8, 0.1, 0.1])
                u_size = row.get('size', 1) if row.get('size') is not None else 1
                total_models = int(row['Qty']) * int(u_size)
                r1.write(f"**{row['Qty']}x {row['Unit']}** ({total_models} models) — {row['Total_Pts']} pts")
                if row['wargear_list'] and row['wargear_list'] != '[]':
                    import json
                    try:
                        upgs = json.loads(row['wargear_list'])
                        r1.caption(f"🔧 {', '.join(upgs)}")
                    except:
                        clean_fallback = str(row['wargear_list']).replace('[', '').replace(']', '').replace('"', '')
                        r1.caption(f"🔧 {clean_fallback}")
                if r2.button("👁️", key=f"rd_opr_{row['entry_id']}"):
                    show_opr_details(row['unit_id'], row['entry_id'], faction=active_list['faction_primary'])
                if r3.button("❌", key=f"del_opr_{row['entry_id']}"):
                    cursor.execute("DELETE FROM play_armylist_entries WHERE entry_id = %s", (row['entry_id'],))
                    conn.commit(); st.rerun()
    else:
        st.info("Roster is empty.")
    conn.close()

