🛡️ Wargaming ERP Technical Documentation
Version: 1.0.0 (Modular Release)
Game Systems: Warhammer 40,000 (10th Ed), OPR (Grimdark Future/Age of Fantasy)
🏗️ 1. Architecture Overview
The application follows a Modular Streamlit Architecture. Logic is separated by game system to prevent cross-contamination of rules and data structures.
app.py: The Traffic Controller. Handles list creation and routes the user to the correct builder module based on the game_system flag.
database_utils.py: The Foundation. Centralizes the mysql-connector logic and reads DB config from environment (see repo **.env.example** and **SECURITY.md**).
w40k_builder.py: The 10th Edition sandbox. Handles Detachments, 6-metric stat bars, and Enhancement logic.
opr_builder.py: The OPR engine. Handles "Replace" wargear logic, strikethrough rendering, and upgrade sets.
🗄️ 2. Database Schema (Standardized)
The database is hosted on MySQL 8.0. It bridges flat Wahapedia data with hierarchical OPR JSON data.
Core Management Tables
play_armylists: The header. Stores list_name, point_limit, faction_primary, faction_secondary, and waha_detachment_id.
play_armylist_entries: The junction. Links a list_id to a unit_id.
play_armylist_upgrades: Tracks OPR-specific upgrade selections.
play_armylist_enhancements: Tracks 40K-specific Character enhancements.
System Mapping Views
view_master_picker: The "Search Engine." A UNION ALL view that standardizes Unit Name, Faction, and Points across all games so the UI search bar works universally.
view_40k_datasheet_complete: Flattens 40K stats (M, T, Sv, W, etc.) into a single row for the UI Stat Bar.
⚙️ 3. Core Logic & Stored Procedures
We use Stored Procedures to handle heavy logic inside the database, keeping the Python code lean.
GetArmyRoster(list_id)
The "Brain" of the Roster. It calculates:
Base Cost of the unit.
Upgrade Cost (OPR) by joining play_armylist_upgrades.
Enhancement Cost (40K) by joining play_armylist_enhancements.
Multiplication of (Base + Upgrades) * Quantity.
Stats: Conditionally returns 40K stats or OPR stats based on the list's game_system.
🎨 4. UI Design Standards
Unit Detail Pop-ups (@st.dialog): Triggered via the 👁️ icon.
OPR: Features "Active Weapons" vs "Upgrades" tabs with strikethrough logic (🚫) for replaced gear.
40K: Features a 6-column metric bar and "Special Rules" pulled from the waha_abilities table.
Cascading Filters: List creation and Library search use a 3-tier cascade: System -> Setting -> Faction.
🔐 Environment setup (secrets)
Do not commit passwords or API keys. Copy the repo root **.env.example** to **.env**, fill in `MYSQL_PASSWORD` (and optionally `MMF_*` for MMF scripts), and optionally `pip install python-dotenv` so the app and scripts load `.env`. See repo **SECURITY.md** for full list of variables.

🛠️ 5. Maintenance & Troubleshooting
Adding New OPR Data: Use the OPR_JSON_analyzer.py script. It automatically populates opr_units, opr_unit_upgrades, and maps the opr_army_settings.
Metadata Locks: If the app hangs, use SHOW PROCESSLIST and KILL [ID] in Workbench to clear stuck metadata locks on Stored Procedures.
Safe Updates: Run SET SQL_SAFE_UPDATES = 0 when performing mass updates on play_armylists or waha_factions.
🚀 6. Future Roadmap
40K Enhancement Toggle: Adding the checkbox logic to the 40K Details tab.
40K Wargear Swaps: Implementing the replacement/strikethrough logic for 40K weapon options.
Validation Engine: "Rule of 3" checks and OPR "1 Hero per 500pts" enforcement.

🏗️ 40K Wargear Logic Strategy
In 40K 10th Edition, wargear is mostly free, but the logic is "Replace A with B."
Storage: We’ll use a new bridge table play_armylist_wargear_selections.
UI: Inside the "Weapons" tab, we'll list the options.
Visuals: If you select "Replace Bolt Pistol with Plasma Pistol," we’ll strike through the Bolt Pistol in the weapon table, just like we did for OPR.

Update v0.3

# 🛡️ Wargaming ERP: Surgical Roster Builder

A high-precision Enterprise Resource Planning (ERP) tool for tabletop wargamers. Supports **Warhammer 40,000 (10th Ed)** and **One Page Rules (Grimdark Future)** with live data card generation and rules-aware list building.

## 🚀 Current Features
- **Dual-System Engine**: Seamlessly switch between 40K (Wahapedia-powered) and OPR (JSON-sync) roster building.
- **Surgical Data Cards**: 
    - **40K**: Dynamic Wargear filtering and Enhancement tracking.
    - **OPR**: Reactive "Caster" tabs, de-duplicated Special Rules glossary, and fuzzy-match weapon replacements.
- **Dynamic Weapons View**: Weapon tables update in real-time. Replaced gear is struck through (~~Strikethrough~~ 🚫) and new gear is highlighted.
- **Rules Hydration**: Automated sync scripts to pull official OPR rule definitions directly from source data into the DB.
- **Tactical Game-Day View**: A minimalist, "One-Page" summary of your list for use during matches.

## 🛠️ Tech Stack
- **Frontend**: Streamlit
- **Backend**: Python 3.14+
- **Database**: MySQL 8.0
- **Data Sources**: Wahapedia (40K) & OPR Community JSONs (OPR)

## 🔜 Phase 4: Inventory & Collection
Current development is moving toward **Physical Collection Tracking**, allowing users to sync their "Pile of Shame" with their active army lists.


🛠️ The Refinement Roadmap:
Visual Confirmation: Adding a small image thumbnail directly into the Link Manager table so you can see which STL you are toggling.
Smart Filtering: Adding a "Filter by Army" or "Show Only Units with No Links" toggle to help you find the gaps in your collection.
Broken Link Detection: A tool to flag if an STL in the library has been deleted or if a unit ID has changed.
Bulk Actions: Allowing you to "Unlink All" or "Set Designer Default" for entire squads at once.

📌 Bookmarked (Digital Library):
Direct download from STL Gallery: Backend proxy that uses MMF cookie/API key to call GET /objects/{id}/files and GET /files/{file_id}, then stream the file to the browser (e.g. st.download_button). Requires storing MMF auth in app config/env.

## 📋 Feature Todo & Feasibility
A full list of features and options with feasibility notes lives in **docs/Feature-Todo-Wargaming-ERP.md**. It covers: updated OPR data, MMF link fixes, image gallery per STL, link manager refinements, download buttons, auto hydrators/scrapers, user sign-up & permissions, hosting, security, GW retail data, New Recruit data, update process, and slicer integration. Use it to prioritize and plan.
