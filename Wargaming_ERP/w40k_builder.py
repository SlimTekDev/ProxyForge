import streamlit as st
import pandas as pd
import re
from database_utils import get_db_connection

# --- 1. HELPER FUNCTIONS ---

def show_40k_validation(list_id, proxy_mode=False):
    """Queries Keyword-Strict SQL View and displays alerts. Filters mismatches if proxy_mode is active."""
    conn = get_db_connection()
    # This query now pulls 'INVALID' for units with mismatched Chapter keywords
    query = "SELECT unit_name, times_taken, max_allowed, faction_status FROM view_list_validation_40k WHERE list_id = %s"
    df_val = pd.read_sql(query, conn, params=(list_id,))
    conn.close()

    if not df_val.empty:
        # 1. Rule of 3/1/6 (Never bypassed by proxy mode)
        violations = df_val[df_val['times_taken'] > df_val['max_allowed']]
        
        # 2. Keyword/Faction Mismatches (e.g., Dante in a non-Blood Angels list)
        # Bypassed only when proxy_mode is True
        mismatches = df_val[df_val['faction_status'] == 'INVALID']
        
        st.sidebar.divider()
        st.sidebar.subheader("⚖️ List Validation")
        
        # Handle Chapter/Faction Errors
        if not mismatches.empty:
            if proxy_mode:
                # User has enabled Proxy/Custom Chapter Mode
                st.sidebar.info("✨ **Proxy Mode Active**: Chapter/Legion restrictions bypassed.")
            else:
                # Standard strict enforcement
                st.sidebar.error("☢️ **Chapter Mismatch Found**")
                for _, row in mismatches.iterrows():
                    st.sidebar.warning(f"{row['unit_name']} (Native Chapter Mismatch)")

        # Handle Rule of 3 Errors
        if not violations.empty:
            st.sidebar.error("🚨 **Rule Violations**")
            for _, row in violations.iterrows():
                st.sidebar.warning(f"**{row['unit_name']}**: {int(row['times_taken'])}/{int(row['max_allowed'])}")
        
        # 3. Final Battle-Ready Calculation
        # Valid if: No Rule of 3 violations AND (No chapter mismatches OR proxy mode is on)
        is_battle_ready = violations.empty and (mismatches.empty or proxy_mode)
        
        if is_battle_ready:
            st.sidebar.success("🛡️ Army is Battle-Ready")



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

def parse_wargear_option(text):
    if not text: return {"type": "none"}
    if "one of the following:" in text.lower():
        parts = re.split(r'one of the following:', text, flags=re.IGNORECASE)
        header = parts[0]
        options_raw = re.split(r'\s1\s|\sone\s', parts[1])
        options_list = [o.strip().strip(',').strip('.') for o in options_raw if len(o.strip()) > 2]
        target_match = re.search(r"(?:model's|unit's)\s+(.*?)\s+can be", header, re.IGNORECASE)
        target = target_match.group(1).strip() if target_match else "Equipment"
        return {"type": "nested", "target": target, "options": options_list}
    swap_match = re.search(r"(?:model's|unit's)\s+(.*?)\s+can be replaced with\s+(?:1\s+)?(.*)", text, re.IGNORECASE)
    if swap_match:
        return {"type": "swap", "target": swap_match.group(1).strip(), "replacement": swap_match.group(2).strip().strip('.')}
    return {"type": "simple", "text": text}
    
    #continued with show_40k_details

@st.dialog("40K Unit Details", width="large")
def show_40k_details(unit_id, entry_id=None, detachment_id=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 1. Fetch Core Stats
    cursor.execute("SELECT * FROM view_40k_datasheet_complete WHERE ID = %s", (unit_id,))
    details = cursor.fetchone()
    
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
                st.image(default_stl['preview_url'], use_container_width=True, caption=f"Proxy: {default_stl['name']}")
            elif details.get('Image'):
                st.image(details['Image'], use_container_width=True, caption="Standard Datasheet Image")
            else:
                st.info("No visual available.")
        # ------------------------------------------

        with col2:
            st.subheader(details['Unit_Name'])
            
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
                
                # 2. Display the table
                st.dataframe(
                    stats_df.drop(columns=['inv_sv_descr']), 
                    hide_index=True, 
                    use_container_width=True,
                    column_config={
                        "Model": st.column_config.TextColumn("Model", width="medium"),
                        "inv_sv": st.column_config.TextColumn("Inv Sv", help="Invulnerable Save")
                    }
                )

                # 3. Special Saves Note
                special_saves = [
                    f"**{m['Model']}**: {m['inv_sv']} ({m['inv_sv_descr'] if m['inv_sv_descr'] else 'No special rules'})" 
                    for m in models if m['inv_sv'] and m['inv_sv'].strip() not in ('', '-', 'None')
                ]
                
                if special_saves:
                    with st.expander("🛡️ Invulnerable Saves & Special Notes", expanded=True):
                        for note in special_saves:
                            st.caption(note)


#  COntinued with tabs pt 2/7
        
        t1, t2, t3, t4, t5 = st.tabs(["⚔️ Weapons", "📜 Rules", "✨ Enhancements", "👥 Composition", "🎯 Stratagems"])

        # Ensure this 'with t1:' block is indented exactly 8 spaces (2 levels)
        with t1:
            # 1. Fetch current selections
            cursor.execute("SELECT option_text FROM play_armylist_wargear_selections WHERE entry_id = %s", (entry_id,))
            active_selections = [r['option_text'] for r in cursor.fetchall()]

            def update_wgear(text, ent_id, is_active):
                conn_cb = get_db_connection(); cur_cb = conn_cb.cursor()
                if is_active: cur_cb.execute("INSERT INTO play_armylist_wargear_selections (entry_id, option_text) VALUES (%s, %s)", (ent_id, text))
                else: cur_cb.execute("DELETE FROM play_armylist_wargear_selections WHERE entry_id = %s AND option_text = %s", (ent_id, text))
                conn_cb.commit(); conn_cb.close()

            # 2. Render Interactive Swaps
            cursor.execute("SELECT description FROM waha_datasheets_options WHERE datasheet_id = %s", (unit_id,))
            options = cursor.fetchall()
            removed_names = []
            added_names = []

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
                            if choice != "Default": 
                                removed_names.append(parsed['target'].lower())
                                added_names.append(choice)
                        else:
                            is_on = desc in active_selections
                            if st.checkbox(desc, value=is_on, key=f"chk_{hash(desc)}_{entry_id}"):
                                if not is_on: update_wgear(desc, entry_id, True); st.rerun()
                                if parsed.get("type") == "swap": 
                                    removed_names.append(parsed["target"].lower())
                                    added_names.append(parsed["replacement"])
                            elif is_on:
                                update_wgear(desc, entry_id, False); st.rerun()

            st.divider()

            # 3. Build Final Table with Strikethrough & Additions
            cursor.execute("SELECT name, range_val, attacks, bs_ws, ap, damage FROM waha_datasheets_wargear WHERE datasheet_id = %s", (unit_id,))
            display_data = []
            
            for w in cursor.fetchall():
                name = w['name']
                rv, att, bs, ap, dmg = w['range_val'], w['attacks'], w['bs_ws'], w['ap'], w['damage']
                
                if any(rem in name.lower() for rem in removed_names):
                    name, rv, att, bs, ap, dmg = f"~~{name}~~ 🚫", f"~~{rv}~~", f"~~{att}~~", f"~~{bs}~~", f"~~{ap}~~", f"~~{dmg}~~"
                
                display_data.append({"Weapon": name, "Range": rv, "A": att, "BS/WS": bs, "AP": ap, "D": dmg})

            if added_names:
                placeholders = ', '.join(['%s'] * len(added_names))
                cursor.execute(f"SELECT name, range_val, attacks_val, ap_val, damage_val FROM waha_weapons WHERE name IN ({placeholders})", tuple(added_names))
                for nw in cursor.fetchall():
                    display_data.append({
                        "Weapon": f"✅ **{nw['name']}**", "Range": nw['range_val'], 
                        "A": nw['attacks_val'], "BS/WS": "---", "AP": nw['ap_val'], "D": nw['damage_val']
                    })

            st.dataframe(pd.DataFrame(display_data), hide_index=True, use_container_width=True)

# tab2-5 part 4/7
        # --- TAB 2: RULES (CLEANED & ROBUST) ---
        with t2:
            # This query handles both 'Linked' abilities and 'Inline' datasheet text
            cursor.execute("""
                SELECT 
                    COALESCE(a.name, da.name) as ab_name, 
                    COALESCE(a.description, da.description) as ab_desc, 
                    da.type 
                FROM waha_datasheets_abilities da 
                LEFT JOIN waha_abilities a ON da.ability_id = a.id 
                WHERE da.datasheet_id = %s 
                AND da.type IN ('Datasheet', 'Wargear', 'Special()')
                ORDER BY da.type DESC, ab_name ASC
            """, (unit_id,))
            
            unit_abilities = cursor.fetchall()
            if unit_abilities:
                for ab in unit_abilities:
                    icon = "🔧" if ab['type'] == 'Wargear' else "📜"
                    # Clean up any potential None values just in case
                    name = ab['ab_name'] or "Unnamed Ability"
                    desc = ab['ab_desc'] or "No description provided."
                    st.markdown(f"**{icon} {name}**: {desc}")
            else:
                st.info("No unique datasheet abilities found for this unit.")


        with t3:
            # ENHANCEMENT LOGIC
            is_character = "Character" in details['Keywords']
            is_epic = "Epic Hero" in details['Keywords']
            if is_character and not is_epic and detachment_id and entry_id:
                st.write("### ✨ Available Enhancements")
                cursor.execute("SELECT enhancement_id FROM play_armylist_enhancements WHERE entry_id = %s", (entry_id,))
                this_model_enh = [r['enhancement_id'] for r in cursor.fetchall()]
                cursor.execute("SELECT e.enhancement_id FROM play_armylist_enhancements e JOIN play_armylist_entries ent ON e.entry_id = ent.entry_id WHERE ent.list_id = (SELECT list_id FROM play_armylist_entries WHERE entry_id = %s)", (entry_id,))
                all_used_enhs = [r['enhancement_id'] for r in cursor.fetchall()]
                cursor.execute("SELECT * FROM view_40k_enhancement_picker WHERE detachment_id = %s", (detachment_id,))
                available_enhs = cursor.fetchall()
                if not available_enhs: st.info("No enhancements found for this detachment.")
                for enh in available_enhs:
                    is_on = enh['enhancement_id'] in this_model_enh
                    is_taken_elsewhere = enh['enhancement_id'] in all_used_enhs and not is_on
                    disabled = is_taken_elsewhere or (len(this_model_enh) > 0 and not is_on)
                    label = f"{enh['enhancement_name']} (+{enh['cost']} pts)"
                    if is_taken_elsewhere: label += " 🚫 (Taken)"
                    if st.checkbox(label, value=is_on, disabled=disabled, key=f"enh_{enh['enhancement_id']}_{entry_id}"):
                        if not is_on: cursor.execute("INSERT INTO play_armylist_enhancements (entry_id, enhancement_id, cost) VALUES (%s, %s, %s)", (entry_id, enh['enhancement_id'], enh['cost']))
                        else: cursor.execute("DELETE FROM play_armylist_enhancements WHERE entry_id = %s AND enhancement_id = %s", (entry_id, enh['enhancement_id']))
                        conn.commit(); st.rerun()
                    st.caption(enh['description'])
            elif is_epic: st.warning("🚫 Epic Heroes cannot take Enhancements.")
            else: st.info("💡 Only non-Epic Hero Characters can take Enhancements.")
        with t4:
            cursor.execute("SELECT description FROM waha_datasheet_unit_composition WHERE datasheet_id = %s ORDER BY line_id ASC", (unit_id,))
            for comp in cursor.fetchall(): st.write(f"• {comp['description']}")
  
        # --- TAB 5: UNIT-SPECIFIC STRATAGEMS (ROLE & KEYWORD AWARE) ---
        with t5:
            # 1. Fetch unit keywords
            cursor.execute("SELECT keyword FROM waha_datasheets_keywords WHERE datasheet_id = %s", (unit_id,))
            unit_keywords = [row['keyword'].upper() for row in cursor.fetchall()]
            
            # Display reference badges
            st.write(f"🏷️ Keywords: `{'`, `'.join(unit_keywords)}`")

            # 2. Phase filter
            phase_filter = st.selectbox("Filter by Phase", 
                                        ["All Phases", "Command phase", "Movement phase", "Shooting phase", "Fight phase", "Any phase"],
                                        key=f"strat_phase_{unit_id}")

            # 3. Fetch detachment stratagems
            cursor.execute("""
                SELECT name, cp_cost, type, phase, description 
                FROM waha_stratagems 
                WHERE detachment_id = %s OR CAST(detachment_id AS UNSIGNED) = %s
            """, (detachment_id, detachment_id))
            all_strats = cursor.fetchall()
            
            found_any = False
            for s in all_strats:
                desc_upper = s['description'].upper()
                name_upper = s['name'].upper()
                phase_match = (phase_filter == "All Phases" or phase_filter.lower() in s['phase'].lower())
                
                # The 'Target' and 'When' sections define eligibility (usually the first 250 chars)
                target_section = desc_upper[:250]
                
                # Baseline Relevance: Match if keyword is in the target text or it's a generic faction strat
                is_relevant = any(k in target_section for k in unit_keywords) or \
                              f"{primary_army.upper()} UNIT" in target_section or \
                              "ANY UNIT" in target_section
                
                # --- SURGICAL ROLE & KEYWORD KILL SWITCHES ---
                
                # A. Vehicle/Infantry/Monster Barriers
                if "VEHICLE" in target_section and "VEHICLE" not in unit_keywords:
                    is_relevant = False
                if "INFANTRY" in target_section and "INFANTRY" not in unit_keywords:
                    is_relevant = False
                if "MONSTER" in target_section and "MONSTER" not in unit_keywords:
                    is_relevant = False

                # B. Transport Logic (e.g. Tank Shock, Emergency Disembark)
                if "TRANSPORT" in target_section and "TRANSPORT" not in unit_keywords:
                    is_relevant = False

                # C. Character & Epic Hero Logic
                if "CHARACTER UNIT" in target_section and "CHARACTER" not in unit_keywords:
                    is_relevant = False
                if "EXCLUDING EPIC HERO" in target_section and "EPIC HERO" in unit_keywords:
                    is_relevant = False
                
                # D. Gated Keywords (Smoke, Grenades, etc.)
                # If the strat explicitly names a keyword requirement, enforce it
                gated_checks = ["SMOKE", "GRENADES", "FLY", "PSYKER", "STEALTH"]
                for gk in gated_checks:
                    if f" {gk} " in target_section and gk not in unit_keywords:
                        is_relevant = False

                # E. Explicit Check for CAREEN! (Requires Vehicle + Deadly Demise)
                if name_upper == "CAREEN!" and "VEHICLE" not in unit_keywords:
                    is_relevant = False

                # 4. Final Render
                if is_relevant and phase_match:
                    found_any = True
                    with st.expander(f"🎯 **{s['name']}** — {s['cp_cost']}CP", expanded=False):
                        st.caption(f"*{s['type']} - {s['phase']}*")
                        st.write(s['description'])
            
            if not found_any:
                st.info(f"No {phase_filter} stratagems found for this unit.")



    conn.close()

#Gameday view pt 5/7
#---- Gameday Printer Friendly View  - Includes expanders for each section ----
def show_gameday_view(active_list, roster_df, total_pts):
    """A fully collapsible tactical sheet with a surgical stacked column layout."""
    st.title(f"📄 Tactical Briefing: {active_list['list_name']}")
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 1. Top Controls
    c1, c2 = st.columns([0.7, 0.3])
    with c1:
        st.write(f"**{active_list['faction_primary']}** | **{total_pts} / {active_list['point_limit']} pts**")
    with c2:
        if st.button("⬅️ Back to Editor", use_container_width=True):
            st.session_state.gameday_mode = False
            st.rerun()

    # 2. Army & Detachment Rules (Expandable)
    cursor.execute("""
        SELECT DISTINCT army_rule_name, army_rule_desc, detachment_rule_name, detachment_rule_desc 
        FROM view_40k_army_rules 
        WHERE (faction_name = %s OR faction_id = (SELECT id FROM waha_factions WHERE name = %s))
        AND detachment_id = %s LIMIT 1
    """, (active_list['faction_primary'], active_list['faction_primary'], active_list.get('waha_detachment_id')))
    rules = cursor.fetchone()
    
    if rules:
        with st.expander(f"📜 Army & Detachment Rules Summary", expanded=False):
            st.markdown(f"### 🛡️ Army Rule: {rules['army_rule_name']}")
            st.write(rules['army_rule_desc'])
            if rules['detachment_rule_name']:
                st.divider()
                st.markdown(f"### 🚩 Detachment Rule: {rules['detachment_rule_name']}")
                st.write(rules['detachment_rule_desc'])

    st.divider()

    # 3. Unit Entries
    for _, row in roster_df.iterrows():
        with st.expander(f"**{row['Qty']}x {row['Unit']}** ({row['Total_Pts']} pts)", expanded=False):
            
            # A. Stats Table
            cursor.execute("SELECT name as Model, movement as M, toughness as T, save_value as Sv, wounds as W, leadership as Ld, oc as OC FROM waha_datasheets_models WHERE datasheet_id = %s", (row['unit_id'],))
            st.dataframe(pd.DataFrame(cursor.fetchall()), hide_index=True, use_container_width=True)

            # B. Unit Composition (Full width under stats)
            with st.expander("👥 Unit Composition", expanded=False):
                cursor.execute("SELECT description FROM waha_datasheet_unit_composition WHERE datasheet_id = %s ORDER BY line_id ASC", (row['unit_id'],))
                for c in cursor.fetchall():
                    st.write(f"• {c['description']}")

            # --- C. The Stacked Column Layout ---
            w_col, ra_col = st.columns([0.45, 0.55]) 
            
            with w_col:
                # Left Column: Weapons
                with st.expander("⚔️ Weapons", expanded=True):
                    cursor.execute("SELECT name, range_val, attacks, bs_ws, ap, damage FROM waha_datasheets_wargear WHERE datasheet_id = %s", (row['unit_id'],))
                    st.dataframe(pd.DataFrame(cursor.fetchall()), hide_index=True, use_container_width=True)

            with ra_col:
                # Right Column Stack: Enhancements -> Abilities -> Stratagems
                
                # 1. SMART ENHANCEMENTS (Only shows if character has one)
                cursor.execute("""
                    SELECT e.name, e.description, ple.cost 
                    FROM play_armylist_enhancements ple
                    JOIN waha_enhancements e ON ple.enhancement_id = e.id
                    WHERE ple.entry_id = %s
                """, (row['entry_id'],))
                equipped_enh = cursor.fetchone()
                
                if equipped_enh:
                    with st.expander(f"✨ Enhancement: {equipped_enh['name']} (+{equipped_enh['cost']} pts)", expanded=True):
                        st.write(equipped_enh['description'])

                # 2. Abilities
                with st.expander("📜 Abilities", expanded=False):
                    cursor.execute("""
                        SELECT COALESCE(a.name, da.name) as ab_name, COALESCE(a.description, da.description) as ab_desc 
                        FROM waha_datasheets_abilities da 
                        LEFT JOIN waha_abilities a ON da.ability_id = a.id 
                        WHERE da.datasheet_id = %s AND da.type IN ('Datasheet', 'Wargear')
                    """, (row['unit_id'],))
                    for ab in cursor.fetchall():
                        st.markdown(f"**{ab['ab_name']}**: {ab['ab_desc']}")
                
                # 3. Stratagems
                with st.expander("🎯 Relevant Stratagems", expanded=False):
                    # ... (Keep your existing Stratagem logic here) ...

                    cursor.execute("SELECT keyword FROM waha_datasheets_keywords WHERE datasheet_id = %s", (row['unit_id'],))
                    unit_keywords = [k['keyword'].upper() for k in cursor.fetchall()]
                    
                    cursor.execute("SELECT name, cp_cost, type, phase, description FROM view_40k_stratagems WHERE clean_det_id = %s", (active_list.get('waha_detachment_id'),))
                    
                    found_any = False
                    for s in cursor.fetchall():
                        desc_upper = s['description'].upper()
                        target_section = desc_upper[:250]
                        is_relevant = any(k in target_section for k in unit_keywords) or f"{active_list['faction_primary'].upper()} UNIT" in target_section or "ANY UNIT" in target_section
                        
                        if "VEHICLE" in target_section and "VEHICLE" not in unit_keywords: is_relevant = False
                        if "INFANTRY" in target_section and "INFANTRY" not in unit_keywords: is_relevant = False
                        
                        if is_relevant:
                            found_any = True
                            st.markdown(f"**{s['name']}** ({s['cp_cost']}CP)")
                            st.caption(s['description'])
                            st.divider()
                    
                    if not found_any:
                        st.caption("No specific tactical options.")

    conn.close()

#part 6/7

# --- 2. MAIN BUILDER ---

def run_40k_builder(active_list):
    list_id = active_list['list_id']
    primary_army = active_list['faction_primary']
    active_det_id = active_list.get('waha_detachment_id')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # A. Silent Points Fetch
    cursor.callproc('GetArmyRoster', (list_id,))
    total_pts = 0
    cached_roster_df = pd.DataFrame() 
    for res in cursor.stored_results():
        roster_data = res.fetchall()
        if roster_data:
            cached_roster_df = pd.DataFrame(roster_data)
            total_pts = int(pd.to_numeric(cached_roster_df['Total_Pts'], errors='coerce').sum())

    # B. Master Sidebar UI
    show_points_summary(active_list, total_pts)
    
    st.sidebar.divider()
    proxy_mode = st.sidebar.toggle("🔓 Proxy / Custom Chapter Mode", value=False, 
                                   help="Bypasses Chapter/Legion restrictions for search and validation.",
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

    # D. Subfaction Logic
    is_space_marine = (primary_army in ["Space Marines", "Adeptus Astartes"])
    library_subfaction = None
    subfactions = []
    if is_space_marine:
        exclude_list = [primary_army, 'Adeptus Astartes', 'Agents of the Imperium', 'Character', 'Infantry', 'Vehicle', 'Epic Hero', 'Battleline', 'Imperium']
        exclude_placeholders = ', '.join(['%s'] * len(exclude_list))
        cursor.execute(f"SELECT DISTINCT keyword FROM waha_datasheets_keywords dk JOIN waha_datasheets d ON dk.datasheet_id = d.waha_datasheet_id JOIN waha_factions f ON d.faction_id = f.id WHERE (f.name = %s OR f.id = 'SM') AND dk.keyword NOT IN ({exclude_placeholders}) AND dk.is_faction_keyword = 1", [primary_army] + exclude_list)
        subfactions = [f['keyword'] for f in cursor.fetchall()]
        if subfactions:
            selected_sub = st.sidebar.selectbox("Select Chapter", ["Generic / All"] + sorted(subfactions), key=f"subfac_{list_id}")
            if selected_sub != "Generic / All": library_subfaction = selected_sub

    # E. Library Search
    st.sidebar.divider()
    allies = ['Imperial Agents', 'Imperial Knights'] if is_space_marine else []
    allow_allies = st.sidebar.toggle("Include Allied Units", value=False, key=f"ally_{list_id}") if allies else False
    search = st.sidebar.text_input("Search Units", key=f"search_{list_id}")
    
    if proxy_mode:
        lib_query = f"SELECT * FROM view_master_picker WHERE game_system = '40K' AND (faction = %s {'OR faction IN (%s, %s)' if allow_allies else ''}) AND name LIKE %s LIMIT 30"
        params = [primary_army] + (allies if allow_allies else []) + [f"%{search}%"]
    elif library_subfaction:
        sub_placeholders = ', '.join(['%s'] * len(subfactions))
        lib_query = f"SELECT DISTINCT m.* FROM view_master_picker m WHERE m.game_system = '40K' AND m.name LIKE %s AND ((m.faction = %s AND (EXISTS (SELECT 1 FROM waha_datasheets_keywords dk WHERE dk.datasheet_id = m.id AND dk.keyword = %s) OR NOT EXISTS (SELECT 1 FROM waha_datasheets_keywords dk WHERE dk.datasheet_id = m.id AND dk.keyword IN ({sub_placeholders})))) {'OR m.faction IN (%s, %s)' if allow_allies else ''}) LIMIT 30"
        params = [f"%{search}%", primary_army, library_subfaction] + subfactions + (allies if allow_allies else [])
    else:
        lib_query = f"SELECT * FROM view_master_picker WHERE game_system = '40K' AND (faction = %s {'OR faction IN (%s, %s)' if allow_allies else ''}) AND name LIKE %s LIMIT 30"
        params = [primary_army] + (allies if allow_allies else []) + [f"%{search}%"]
    
    cursor.execute(lib_query, params)
    for unit in cursor.fetchall():
        c1, c2, c3 = st.sidebar.columns([0.6, 0.2, 0.2])
        display_name = f"⭐ {unit['name']}" if unit['faction'] in allies else unit['name']
        c1.write(f"**{display_name}**\n{unit['points']} pts")
        if c2.button("Add", key=f"add_{unit['id']}_{list_id}"):
            cursor.execute("SELECT min_size FROM view_40k_unit_composition WHERE datasheet_id = %s", (unit['id'],))
            sz = cursor.fetchone(); start_qty = sz['min_size'] if sz else 1
            cursor.callproc('AddUnit', (list_id, str(unit['id']), start_qty))
            conn.commit(); st.rerun()
        if c3.button("👁️", key=f"lib_det_{unit['id']}_{list_id}"): show_40k_details(unit['id'], detachment_id=active_det_id)

    # --- F. Roster Panel ---
    if 'gameday_mode' not in st.session_state:
        st.session_state.gameday_mode = False

    # 1. Header & Mode Toggle
    header_col, toggle_col = st.columns([0.7, 0.3])
    with header_col:
        st.title(f"🛡️ Roster: {active_list['list_name']}")
    with toggle_col:
        if not st.session_state.gameday_mode:
            if st.button("📑 Game-Day View", use_container_width=True):
                st.session_state.gameday_mode = True
                st.rerun()

    # 2. Logic Branch: Game-Day vs. Editor
    if st.session_state.gameday_mode:
        show_gameday_view(active_list, cached_roster_df, total_pts)
    else:
        # --- 1. DYNAMIC ARMY & DETACHMENT RULES ---
        cursor.execute("""
            SELECT army_rule_name, army_rule_desc 
            FROM view_40k_army_rule_registry 
            WHERE faction_name = %s OR faction_id = (SELECT id FROM waha_factions WHERE name = %s)
            LIMIT 1
        """, (primary_army, primary_army))
        found_rule = cursor.fetchone()
        
        cursor.execute("""
            SELECT name, description 
            FROM waha_detachment_abilities 
            WHERE detachment_id = %s
            LIMIT 1
        """, (active_det_id,))
        det_rule = cursor.fetchone()

        if found_rule or det_rule:
            exp_label = f"📜 {primary_army} Army & Detachment Rules"
            with st.expander(exp_label, expanded=False):
                if found_rule:
                    st.subheader(f"🛡️ Army Rule: {found_rule['army_rule_name']}")
                    st.write(found_rule['army_rule_desc'])
                if det_rule:
                    if found_rule: st.divider()
                    st.subheader(f"🚩 Detachment Rule: {det_rule['name']}")
                    st.write(det_rule['description'])

        # --- 2. STRATAGEM CHEAT SHEET ---
        cursor.execute("""
            SELECT name, type, cp_cost, phase, description 
            FROM view_40k_stratagems 
            WHERE clean_det_id = %s
            ORDER BY phase ASC
        """, (active_det_id,))
        strats = cursor.fetchall()
        
        if strats:
            with st.expander(f"🎯 {primary_army} Detachment Stratagems", expanded=False):
                for s in strats:
                    st.markdown(f"**{s['name']}** — {s['cp_cost']}CP")
                    st.caption(f"*{s['type']} - {s['phase']}*")
                    st.write(s['description'])
                    st.divider()
#Roster listing pt 7/7
        # --- 3. ROSTER LISTING (Interactive Editor) ---
        if not cached_roster_df.empty:
            st.metric("Total Points", f"{total_pts} / {active_list['point_limit']}")
            for i, row in cached_roster_df.iterrows():
                r_qty, r_main, r_view, r_del = st.columns([0.15, 0.65, 0.1, 0.1])
                with r_qty:
                    cursor.execute("SELECT min_size, max_size FROM view_40k_unit_composition WHERE datasheet_id = %s", (row['unit_id'],))
                    sizes = cursor.fetchone()
                    if sizes and sizes['max_size'] > sizes['min_size']:
                        is_max = row['Qty'] == sizes['max_size']
                        if st.button(f"{row['Qty']} ({'Max' if is_max else 'Min'})", key=f"sz_{row['entry_id']}"):
                            cursor.execute("UPDATE play_armylist_entries SET quantity = %s WHERE entry_id = %s", (sizes['min_size'] if is_max else sizes['max_size'], row['entry_id']))
                            conn.commit(); st.rerun()
                    else: st.write(f"👤 {row['Qty']}")
                with r_main:
                    st.write(f"**{row['Unit']}**")
                    txt = f"{row['Total_Pts']} pts"
                    if row['wargear_list'] and row['wargear_list'] != '[]':
                        import json
                        txt += f" | 🔧 {', '.join(json.loads(row['wargear_list']))}"
                    st.caption(txt)
                with r_view:
                    if st.button("👁️", key=f"v_{row['entry_id']}"): show_40k_details(row['unit_id'], entry_id=row['entry_id'], detachment_id=active_det_id)
                with r_del:
                    if st.button("❌", key=f"d_{row['entry_id']}"):
                        cursor.execute("DELETE FROM play_armylist_entries WHERE entry_id = %s", (row['entry_id'],))
                        conn.commit(); st.rerun()
        else:
            st.info("Roster is empty. Add units from the sidebar library.")

    conn.close()

