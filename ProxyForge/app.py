import json
from pathlib import Path

import streamlit as st
import pandas as pd
from database_utils import get_db_connection
from text_utils import fix_apostrophe_mojibake
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

# OPR game system number (Army Forge API) -> slug (DB / view_opr_master_picker)
OPR_GAME_SYSTEM_NUM_TO_SLUG = {
    2: "grimdark-future",
    3: "grimdark-future-firefight",
    4: "age-of-fantasy",
    5: "age-of-fantasy-skirmish",
    6: "age-of-fantasy-regiments",
}
SLUG_TO_GAME_SYSTEM_NUM = {v: k for k, v in OPR_GAME_SYSTEM_NUM_TO_SLUG.items()}


def _load_opr_factions_from_source_list(opr_mode_slug):
    """Load faction display options for the Create New List dropdown from army_forge_armies.json.
    This ensures all armies (including creator) show up even if the DB hasn't been hydrated yet."""
    try:
        path = Path(__file__).resolve().parent.parent / "data" / "opr" / "army_forge_armies.json"
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            armies = json.load(f)
    except Exception:
        return None
    game_system_num = SLUG_TO_GAME_SYSTEM_NUM.get(opr_mode_slug)
    if game_system_num is None:
        return None
    # (armyName strip, source) per faction; prefer creator if same name appears twice
    by_name = {}
    for a in armies:
        if a.get("gameSystem") != game_system_num:
            continue
        name = (a.get("armyName") or "").strip()
        if not name:
            continue
        src = a.get("source", "official")
        if name not in by_name or src == "creator":
            by_name[name] = src
    official = sorted(n for n, s in by_name.items() if s == "official")
    creator = sorted(n for n, s in by_name.items() if s == "creator")

    def _opr_faction_display(name, source_label):
        tag = ""
        if opr_mode_slug == "age-of-fantasy-skirmish" and name in GUILDS_OF_THE_NEXUS_FACTIONS:
            tag = " (Guilds)"
        elif opr_mode_slug == "grimdark-future-firefight" and name in GANGS_OF_NEW_EDEN_FACTIONS:
            tag = " (Gangs)"
        return name + tag + " " + source_label

    return (
        [_opr_faction_display(f, "(Official)") for f in official]
        + [_opr_faction_display(f, "(Creator)") for f in creator]
    )


def _load_opr_army_source_lookup():
    """(army_name, game_system_slug) -> 'official' | 'creator'. Uses data/opr/army_forge_armies.json.
    When the same (armyName, slug) appears as both official and creator, prefer 'creator' so creator books are visible."""
    try:
        path = Path(__file__).resolve().parent.parent / "data" / "opr" / "army_forge_armies.json"
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as f:
            armies = json.load(f)
        # Collect all sources per (armyName, slug); then prefer "creator" if any entry is creator
        by_key = {}
        for a in armies:
            gs = a.get("gameSystem")
            slug = OPR_GAME_SYSTEM_NUM_TO_SLUG.get(gs)
            if slug and a.get("armyName"):
                key = (a["armyName"].strip(), slug)
                by_key.setdefault(key, set()).add(a.get("source", "official"))
        return {k: ("creator" if "creator" in v else "official") for k, v in by_key.items()}
    except Exception:
        return {}


# Guilds of the Nexus subfactions (Age of Fantasy Skirmish) — show "(Guilds)" tag in dropdown
GUILDS_OF_THE_NEXUS_FACTIONS = frozenset({
    "Brute Clans", "Crazed Zealots", "Furious Tribes", "Hidden Syndicates",
    "Hired Guards", "Mercenaries", "Merchant Unions", "Outskirt Raiders",
    "Shortling Alliances", "Trade Federations", "Treasure Hunters",
})

# Gangs of New Eden subfactions (Grimdark Future Firefight) — show "(Gangs)" tag in dropdown
GANGS_OF_NEW_EDEN_FACTIONS = frozenset({
    "Badland Nomads", "Berserker Clans", "Brute Coalitions", "City Runners",
    "Mega-Corps", "Mercenaries", "Psycho Cults", "Security Forces",
    "Shadow Leagues", "Shortling Federations", "Worker Unions",
})


def _strip_opr_faction_label(display_value):
    """Remove ' (Official)', ' (Creator)', ' (Guilds)', ' (Gangs)' from dropdown selection to get faction_primary."""
    if not display_value:
        return display_value
    suffixes = (" (Official)", " (Creator)", " (Guilds)", " (Gangs)")
    while True:
        changed = False
        for suffix in suffixes:
            if display_value.endswith(suffix):
                display_value = display_value[: -len(suffix)]
                changed = True
                break
        if not changed:
            break
    return display_value


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

    # Alpha notice: show when PROXYFORGE_ALPHA_BANNER is set (e.g. "1" in Streamlit Cloud secrets), or always if unset (show on cloud)
    import os
    _show_alpha = os.environ.get("PROXYFORGE_ALPHA_BANNER", "1").strip().lower() in ("1", "true", "yes")
    if _show_alpha:
        st.info(
            "**Alpha test** — ProxyForge is under active development. The app may be restarted to fix bugs or add features. "
            "If the app behaves erratically or you don’t see the latest changes, **refresh the page** (F5 or Ctrl+R on Windows/Linux, Cmd+R on Mac) to load the newest version."
        )

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
            # Dropdown from source list so all armies (including creator) show even if DB not hydrated
            fac_options = _load_opr_factions_from_source_list(opr_mode_slug)
            if not fac_options:
                # Fallback: factions from DB (e.g. if army_forge_armies.json missing)
                cursor.execute(
                    "SELECT DISTINCT faction FROM view_opr_master_picker WHERE game_system = %s",
                    (opr_mode_slug,),
                )
                all_factions = sorted([f["faction"] for f in cursor.fetchall()])
                source_lookup = _load_opr_army_source_lookup()
                official_factions = sorted(
                    f for f in all_factions
                    if source_lookup.get((f, opr_mode_slug), "official") == "official"
                )
                creator_factions = sorted(
                    f for f in all_factions
                    if source_lookup.get((f, opr_mode_slug), "official") == "creator"
                )

                def _opr_faction_display(name, source_label):
                    tag = ""
                    if opr_mode_slug == "age-of-fantasy-skirmish" and name in GUILDS_OF_THE_NEXUS_FACTIONS:
                        tag = " (Guilds)"
                    elif opr_mode_slug == "grimdark-future-firefight" and name in GANGS_OF_NEW_EDEN_FACTIONS:
                        tag = " (Gangs)"
                    return name + tag + " " + source_label

                fac_options = (
                    [_opr_faction_display(f, "(Official)") for f in official_factions]
                    + [_opr_faction_display(f, "(Creator)") for f in creator_factions]
                )
            if not fac_options:
                st.caption("No armies found for this game mode. Add armies to data/opr/army_forge_armies.json and run build_unified_army_list.py, or run fetch and hydrator to load OPR data.")
            p_fac_display = st.selectbox("Primary Army", fac_options or ["—"], key="opr_fac")
            p_fac = _strip_opr_faction_label(p_fac_display) if p_fac_display and p_fac_display != "—" else None
            new_pts = st.number_input("Points", value=2000, step=250, key="opr_pts")
            if st.button("Save List", key="opr_save"):
                if not p_fac:
                    st.error("Select a primary army.")
                else:
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
            list_map = {f"{fix_apostrophe_mojibake(l['list_name'])} ({l['point_limit']} pts)": l for l in opr_lists}
            sel_label = st.sidebar.selectbox("Active Roster", list_map.keys(), key="opr_roster")
            active_list = list_map[sel_label]
            st.sidebar.caption(f"Delete roster: **{fix_apostrophe_mojibake(active_list['list_name'])}**")
            opr_pending = st.session_state.get("opr_confirm_delete_list_id") == active_list["list_id"]
            if opr_pending:
                st.sidebar.warning("Permanently delete this roster? This cannot be undone.")
                c1, c2 = st.sidebar.columns(2)
                if c1.button("Confirm delete", key="opr_confirm_delete"):
                    cursor.execute("DELETE FROM play_armylists WHERE list_id = %s AND game_system = %s", (active_list["list_id"], "OPR"))
                    conn.commit()
                    st.session_state.pop("opr_confirm_delete_list_id", None)
                    log_feature("list_deleted", detail="OPR")
                    st.rerun()
                if c2.button("Cancel", key="opr_cancel_delete"):
                    st.session_state.pop("opr_confirm_delete_list_id", None)
                    st.rerun()
            elif st.sidebar.button("🗑️ Delete this roster", key="opr_delete_roster"):
                st.session_state["opr_confirm_delete_list_id"] = active_list["list_id"]
                st.rerun()
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
            list_map = {f"{fix_apostrophe_mojibake(l['list_name'])} ({l['point_limit']} pts)": l for l in w40k_lists}
            sel_label = st.sidebar.selectbox("Active Roster", list_map.keys(), key="40k_roster")
            active_list = list_map[sel_label]
            st.sidebar.caption(f"Delete roster: **{fix_apostrophe_mojibake(active_list['list_name'])}**")
            w40k_pending = st.session_state.get("40k_confirm_delete_list_id") == active_list["list_id"]
            if w40k_pending:
                st.sidebar.warning("Permanently delete this roster? This cannot be undone.")
                c1, c2 = st.sidebar.columns(2)
                if c1.button("Confirm delete", key="40k_confirm_delete"):
                    cursor.execute("DELETE FROM play_armylists WHERE list_id = %s AND game_system = %s", (active_list["list_id"], "40K_10E"))
                    conn.commit()
                    st.session_state.pop("40k_confirm_delete_list_id", None)
                    log_feature("list_deleted", detail="40K")
                    st.rerun()
                if c2.button("Cancel", key="40k_cancel_delete"):
                    st.session_state.pop("40k_confirm_delete_list_id", None)
                    st.rerun()
            elif st.sidebar.button("🗑️ Delete this roster", key="40k_delete_roster"):
                st.session_state["40k_confirm_delete_list_id"] = active_list["list_id"]
                st.rerun()
            run_40k_builder(active_list)
        else:
            st.warning("Create a 40K list in the sidebar to begin.")

    conn.close()
except Exception as e:
    st.error(f"System Error: {e}")
