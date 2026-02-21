"""
Army Forge-style army book view: display OPR JSON data for a selected army.
Shows army detail (background, rules, spells from opr_army_detail) and all units
and their upgrade options from data/opr/data.json.
"""
import json
from pathlib import Path

import streamlit as st

from database_utils import get_db_connection

# Repo root: ProxyForge/army_book_ui.py -> parent = ProxyForge, parent.parent = repo
_REPO_ROOT = Path(__file__).resolve().parent.parent
OPR_DATA_PATH = _REPO_ROOT / "data" / "opr" / "data.json"

# Display names for game system slugs
SYSTEM_LABELS = {
    "grimdark-future": "Grimdark Future",
    "grimdark-future-firefight": "Grimdark Future: Firefight",
    "age-of-fantasy": "Age of Fantasy",
    "age-of-fantasy-skirmish": "Age of Fantasy: Skirmish",
    "age-of-fantasy-regiments": "Age of Fantasy: Regiments",
}


@st.cache_data(ttl=300)
def load_opr_data():
    """Load and return the OPR units array from data.json. Cached for 5 min."""
    if not OPR_DATA_PATH.exists():
        return None
    with open(OPR_DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_systems_and_armies(data):
    """Return (systems, system_to_armies). systems = sorted list; system_to_armies = {slug: [army1, army2, ...]}."""
    system_to_armies = {}
    for entry in data:
        if not isinstance(entry, dict):
            continue
        sys_slug = entry.get("system") or "grimdark-future"
        army = entry.get("army") or "Unknown"
        if sys_slug not in system_to_armies:
            system_to_armies[sys_slug] = set()
        system_to_armies[sys_slug].add(army)
    # Sort armies per system, and system order by label
    for k in system_to_armies:
        system_to_armies[k] = sorted(system_to_armies[k])
    systems = sorted(system_to_armies.keys(), key=lambda s: SYSTEM_LABELS.get(s, s))
    return systems, system_to_armies


def filter_entries(data, system_slug, army_name):
    """Return entries for the given system and army."""
    return [
        e
        for e in data
        if isinstance(e, dict)
        and (e.get("system") or "grimdark-future") == system_slug
        and (e.get("army") or "") == army_name
    ]


# Display order for unit groups (Army Forge style)
UNIT_GROUP_ORDER = (
    "Heroes",
    "Core",
    "Special",
    "Support",
    "Vehicles & Monsters",
    "Other",
)


def _generic_name_to_group(generic_name):
    """Derive unit group from genericName when unitGroup is missing (e.g. old data)."""
    if not generic_name or not isinstance(generic_name, str):
        return "Other"
    g = generic_name.strip().lower()
    if "hero" in g:
        return "Heroes"
    if "titan" in g or ("great" in g and "monster" in g):
        return "Vehicles & Monsters"
    if any(x in g for x in ("monster", "vehicle", "tank", "walker", "gunship", "speeder", "chariot", "drop pod", "artillery beast", "brute giant")):
        return "Vehicles & Monsters"
    if "artillery" in g or "support " in g or "altar" in g:
        return "Support"
    non_core = ("elite", "heavy", "assault", "support", "veteran", "psychic", "flying", "shield", "brute")
    if any(x in g for x in ("light infantry", "scouts", "fanatics", "swarms")) and not any(x in g for x in non_core):
        return "Core"
    if g == "infantry" or g == "bikers":
        return "Core"
    if ("infantry" in g or "bikers" in g) and not any(x in g for x in non_core):
        return "Core"
    return "Special"


def group_entries_by_unit_group(entries):
    """Return dict: group_label -> list of entries (sorted by cost, name)."""
    groups = {}
    for e in entries:
        grp = e.get("unitGroup")
        if not grp:
            generic = (e.get("unit") or {}).get("genericName") or ""
            grp = _generic_name_to_group(generic)
        if grp not in groups:
            groups[grp] = []
        groups[grp].append(e)
    for grp in groups:
        groups[grp].sort(key=lambda x: (x.get("cost") or 0, (x.get("name") or "")))
    return groups


def render_unit(entry):
    """Render one unit card: stats + upgrade sets."""
    unit = entry.get("unit") or {}
    bases = unit.get("bases") or {}
    round_base = bases.get("round") or bases.get("square") or "—"
    generic = unit.get("genericName") or "—"

    with st.container(border=True):
        # Header row: name, cost, Q, D, wounds, size
        st.subheader(entry.get("name") or "Unnamed")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Cost", f"{entry.get('cost', 0)} pts")
        col2.metric("Quality", f"{entry.get('quality', '-')}+")
        col3.metric("Defense", f"{entry.get('defense', '-')}+")
        col4.metric("Wounds", entry.get("wounds", 1))
        col5.metric("Size", entry.get("size", 1))

        st.caption(f"**Type:** {generic}  ·  **Base:** {round_base} mm round")

        # Upgrade sets
        upgrade_sets = entry.get("upgradeSets") or []
        if upgrade_sets:
            st.markdown("**Upgrades**")
            for section in upgrade_sets:
                label = section.get("label") or "Options"
                options = section.get("options") or []
                with st.expander(label, expanded=False):
                    if not options:
                        st.caption("No options")
                    else:
                        for opt in options:
                            cost = opt.get("cost")
                            cost_str = f"+{cost} pts" if cost else ""
                            st.write(f"• **{opt.get('label', '')}** {cost_str}")
        st.divider()


def fetch_army_detail(army_name: str, game_system: str):
    """Return one row from opr_army_detail or None."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT background, army_wide_rules, special_rules, aura_rules, spells FROM opr_army_detail WHERE army_name = %s AND game_system = %s",
            (army_name, game_system),
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return row
    except Exception:
        return None


def render_army_detail(army_name: str, game_system: str):
    """Render Background, Army-Wide Rules, Special Rules, Aura Rules, Spells from DB."""
    row = fetch_army_detail(army_name, game_system)
    if not row or not any([row.get("background"), row.get("army_wide_rules"), row.get("special_rules"), row.get("aura_rules"), row.get("spells")]):
        return False
    with st.expander("Army detail — Background, rules & spells", expanded=True):
        if row.get("background"):
            st.markdown("**Background**")
            st.markdown(row["background"])
            st.divider()
        if row.get("army_wide_rules"):
            st.markdown("**Army-Wide Special Rules**")
            st.markdown(row["army_wide_rules"])
            st.divider()
        if row.get("special_rules"):
            st.markdown("**Special Rules**")
            st.markdown(row["special_rules"])
            st.divider()
        if row.get("aura_rules"):
            st.markdown("**Aura Special Rules**")
            st.markdown(row["aura_rules"])
            st.divider()
        if row.get("spells"):
            st.markdown("**Spells**")
            st.markdown(row["spells"])
    return True


def run_army_book_ui():
    """Main entry: system/army selectors and unit list."""
    st.title("OPR Army Book Reference")
    st.caption("Browse units and upgrade options from the OPR data. Data source: `data/opr/data.json`.")

    data = load_opr_data()
    if data is None:
        st.error(f"OPR data file not found: {OPR_DATA_PATH}. Run the OPR fetcher first.")
        return

    systems, system_to_armies = get_systems_and_armies(data)
    if not systems:
        st.warning("No systems found in data.")
        return

    # Sidebar or top: system + army selection
    sys_slug = st.selectbox(
        "Game system",
        options=systems,
        format_func=lambda s: SYSTEM_LABELS.get(s, s.replace("-", " ").title()),
        key="army_book_system",
    )
    armies = system_to_armies.get(sys_slug, [])
    if not armies:
        st.warning("No armies for this system.")
        return

    army_name = st.selectbox("Army", options=armies, key="army_book_army")
    entries = filter_entries(data, sys_slug, army_name)
    grouped = group_entries_by_unit_group(entries)

    # Optional: show army cover once (from first unit that has it)
    army_image_url = None
    for e in entries:
        url = (e.get("unit") or {}).get("product") or {}
        if isinstance(url, dict):
            url = url.get("imageUrl")
        if url:
            army_image_url = url
            break
    if army_image_url:
        st.image(army_image_url, use_container_width=False, width=200, caption=f"{army_name} — Army Book")

    # Army detail (background, rules, spells) from opr_army_detail
    render_army_detail(army_name, sys_slug)

    st.divider()
    st.markdown(f"**{army_name}** — {len(entries)} units")
    for group_label in UNIT_GROUP_ORDER:
        group_entries = grouped.get(group_label, [])
        if not group_entries:
            continue
        st.subheader(group_label)
        st.caption(f"{len(group_entries)} unit(s)")
        for entry in group_entries:
            render_unit(entry)
    # Any group not in UNIT_GROUP_ORDER (e.g. from older data)
    for group_label in sorted(grouped.keys()):
        if group_label in UNIT_GROUP_ORDER:
            continue
        group_entries = grouped[group_label]
        st.subheader(group_label)
        st.caption(f"{len(group_entries)} unit(s)")
        for entry in group_entries:
            render_unit(entry)
