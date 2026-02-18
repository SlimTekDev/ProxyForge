# MySQL Dumps — Wargaming ERP

This directory contains MySQL exports of the **wargaming_erp** database used by the Wargaming ERP application. Dumps are retained for backup, restore, and schema reference.

---

## Project context

**Wargaming ERP** is a tabletop wargaming management application that supports:

- **Army list building** for Warhammer 40,000 (10th Ed) and One Page Rules (Grimdark Future / Age of Fantasy), using Wahapedia and OPR community data respectively.
- **Data card generation** — list-aware stats, wargear, enhancements, and special rules for use at the table.
- **Collection and inventory tracking** — STL library, paint recipes, physical models, and unit-to-proxy linking (in development).

The application code and repository are located in the **Wargaming_ERP** directory. The **wargaming_erp** database (MySQL 8.0) is the backend for that application; the files in this directory are point-in-time snapshots of that database. **Prerequisites:** MySQL 8.0, utf8mb4. The app (Python 3.x, Streamlit) connects via credentials configured in the Wargaming_ERP project. Game and library data are loaded from external sources; see **Data sources and import/export scripts** below.

---

## Data sources and import/export scripts

This section documents where the data in **wargaming_erp** comes from and how it is loaded. **Keep this section updated** as you add or change import scripts, export formats, or direct-from-source (e.g. API or web) pulls.

| Source | Feeds | Current method | Notes / roadmap |
|--------|--------|----------------|------------------|
| **40K / Wahapedia** | `waha_*` tables (datasheets, detachments, enhancements, weapons, abilities, stratagems, etc.) | Manual or separate sync/export scripts; structure follows Wahapedia. | *Planned:* direct pull from source site(s) where feasible. |
| **OPR (One Page Rules)** | `opr_units`, `opr_unit_upgrades`, `opr_specialrules`, `opr_spells`, `opr_unitweapons`, `opr_unitrules`, `opr_army_settings` | **OPR_JSON_analyzer.py** (and hydration scripts) in or alongside **Wargaming_ERP**; reads OPR community JSON. | See Wargaming_ERP README for analyzer usage. *Planned:* direct fetch from OPR/community JSON URLs if available. |
| **MyMiniFactory (MMF)** | `stl_library` (Digital Library catalog) | **fetch_mmf_library.py** (scripts/mmf) fetches via MMF API v2; writes **data/mmf/mmf_download.json**. **mmf_hydrator.py** reads that file and upserts `stl_library`; skips when content hash unchanged. | See **docs/MMF-Fetcher-Setup.md**. Set `MMF_USERNAME` and optionally `MMF_API_KEY`. |

**Conventions**

- **Script location** — Import scripts may live in **Wargaming_ERP** (e.g. OPR_JSON_analyzer), in sibling folders (e.g. **mmf Data import**), or in a dedicated **import/** or **scripts/** tree; document the path here when you add or move them.
- **Credentials** — Scripts that connect to MySQL should use config or environment (e.g. same pattern as the app); avoid committing passwords.
- **Dumps** — A MySQL dump is a snapshot. Refreshing game or library data is independent of taking a new dump; run the relevant import or pull, then create a new dated dump if you want to archive that state.
- **Automated scrapers and sync** — For a design to automate JSON fetches and DB updates with a sync check (only update when source data changed), see **docs/Scrapers-and-Sync-Design.md**.

---

## Directory contents

| Content | Description |
|--------|-------------|
| **Dated dump folders** (e.g. `WargamingERPSQLDump2.16.26`) | One folder per dump. The numeric suffix is the **dump date** in `YY.MM.DD` format (e.g. 2.16.26 = 16 February 2026). Each folder typically contains a full dump including data (`Wargaming_ERPDump.sql`) and may include a schema-only dump (`Wargaming_ERPSchemaOnlyDump.sql`). |
| **Per-table SQL files** (`wargaming_erp_<table>.sql`) | Exports of individual tables from the same database. |
| **Schema and routines** | `wargaming_erp_schema_dump.csv`, `wargaming_erp_routines.sql` — schema metadata and stored procedure definitions. |

Full dumps include both schema and data unless the filename indicates schema-only.

---

## Usage

**Restore from a full dump**  
Use the main dump file inside a dated folder with the MySQL client or Workbench, e.g.:

```bash
mysql -u <user> -p wargaming_erp < WargamingERPSQLDump2.16.26/Wargaming_ERPDump.sql
```

**Create a new dated backup**  
Add a new folder named `WargamingERPSQLDump<YY.MM.DD>` and place the new full (and optional schema-only) dump inside it so each snapshot is clearly dated.

**Schema reference**  
A full dump reflects the schema and data the Wargaming_ERP application expects. Use it when provisioning a new database or verifying compatibility after schema changes.

**Restoring from schema-only or per-table dumps**  
If you restore only schema or individual tables, also restore **stored procedures and views** (e.g. from `wargaming_erp_routines.sql` or a full dump). The application depends on them for roster calculation and unit search.

---

## Database overview

The **wargaming_erp** schema is organized into logical areas:

- **List management** — `play_armylists`, `play_armylist_entries`, `play_armylist_upgrades`, `play_armylist_enhancements`, `play_armylist_wargear_selections`, and related tables.
- **40K (Wahapedia)** — `waha_datasheets`, `waha_detachments`, `waha_enhancements`, `waha_weapons`, `waha_abilities`, and associated mapping tables.
- **OPR** — `opr_units`, `opr_unit_upgrades`, `opr_specialrules`, `opr_spells`, `opr_unitweapons`, and related tables.
- **Inventory** — `inv_stl_library`, `inv_physical_models`, `inv_paint_inventory`, `inv_paint_recipes`, `inv_proxy_bridge`, and supporting tables.
- **Play tracking** — `play_listunits`, `play_match_tracking`, `play_mission_cards`, and related tables.

Detailed table and column documentation is maintained in **DataDictionary.md** in the Wargaming_ERP project directory.

**Key database objects** — The application expects these to exist; a restore that omits them will break roster and library behavior:

- **Stored procedures:** `GetArmyRoster(list_id)`, `GetOPRArmyRoster(list_id)`, `AddUnit(list_id, unit_id, quantity)`
- **Views (examples):** `view_master_picker`, `view_opr_master_picker`, `view_40k_datasheet_complete`, `view_40k_unit_composition`, `view_list_validation_40k`, `view_40k_army_rule_registry`, `view_40k_stratagems`, `view_opr_unit_rules_detailed`

---

## Design standards

The application (Streamlit, in **Wargaming_ERP**) follows consistent patterns for UI and data presentation.

### Navigation and filters

- **Top-level navigation** — Sidebar radio: Army Builder vs Digital Library.
- **Cascading filters** — A three-tier cascade is used for list creation and library search: **Game system** → **Setting / mode** (e.g. OPR game type or 40K detachment) → **Faction / primary army**. Faction options are driven by the selected system so the unit pool stays consistent.

### Unit detail presentation

- **Trigger** — Unit details are shown in a modal dialog opened via a **👁️ (view)** control next to the unit in the sidebar library or in the roster.
- **40K unit details** — Dialog shows: optional proxy/STL image (from `stl_unit_links` default) or Wahapedia image; 6-column stat bar (M, T, Sv, Inv Sv, W, Ld, OC) from `waha_datasheets_models`; tabs for **Weapons** (with wargear swap toggles and strikethrough for replaced options), **Rules**, **Enhancements**, **Composition**, and **Stratagems**. Special rules and invulnerable saves are sourced from `waha_abilities` and model-level metadata.
- **OPR unit details** — Dialog shows: optional default STL image; core stats (e.g. QUA, DEF, Wounds); **Active Weapons** vs **Upgrades** tabs. Replaced wargear is shown with **strikethrough and 🚫**; newly added weapons from upgrades are highlighted (e.g. ⭐). Upgrade sections use radio groups for “Replace one…” and checkboxes for additive options; selections are stored in `play_armylist_opr_upgrades`. If the unit has Caster (or equivalent), a **Spells** tab shows the faction spell list from `opr_spells`.

### Roster and game-day views

- **Editor view** — Roster is a list of entries with quantity, unit name, total points, and optional wargear/upgrade summary; each row has 👁️ (details) and ❌ (remove). Points and roster content are supplied by the appropriate stored procedure (`GetArmyRoster` for 40K, `GetOPRArmyRoster` for OPR).
- **Game-day view** — A single-page, read-optimized view of the list (tactical briefing). 40K and OPR each have a dedicated layout: condensed unit blocks, active weapons, and (where applicable) stratagems or spells. Replaced gear is again shown with strikethrough/🚫 for consistency with the detail dialogs.

### Visual and data consistency

- **Proxy/default imagery** — Where a unit has a linked STL marked as default in `stl_unit_links`, the detail dialog and game-day view prefer that image over the canonical datasheet image.
- **Points** — Displayed totals always reflect base cost plus upgrades/enhancements, multiplied by quantity, as computed by the roster stored procedures.

---

## Army builder logic

The Army Builder is the primary workflow for creating and editing rosters. Behavior is split by game system but shares common patterns.

### List creation and context

- **New list** — User sets list name, **game system** (40K or OPR), **primary faction**, and **point limit**. For OPR, the **game mode** (e.g. Grimdark Future, Age of Fantasy) is also chosen and stored in `opr_army_settings`; for 40K, the list is tied to a **detachment** (e.g. via `waha_detachment_id` on `play_armylists`) which drives detachment rules and stratagems.
- **Active list** — A single “Active Roster” is selected in the sidebar; all subsequent library search and roster actions apply to that list. The correct builder module (`w40k_builder` or `opr_builder`) is invoked based on `game_system`.

### Unit search and add

- **Unified unit source** — 40K uses `view_master_picker` (and, where applicable, `view_40k_unit_composition` for min/max size). OPR uses `view_opr_master_picker` filtered by the list’s faction and the current OPR system from `opr_army_settings`. Both expose a consistent notion of unit id, name, faction, and points so the sidebar can show “Add” and “👁️” without game-specific UI duplication.
- **Search and filters** — Sidebar search filters by unit name. 40K can optionally restrict by **Chapter** (faction keyword) and **Include allied units** (e.g. Imperial Agents, Imperial Knights); **Proxy / Custom Chapter mode** relaxes keyword checks so any faction unit can be added. OPR filters by faction and current OPR system; “Prime Brothers” / “Battle Brothers” are treated as valid alternatives for Space Marine–style lists.
- **Adding a unit** — The **Add** action calls the `AddUnit` stored procedure with `list_id`, `unit_id` (waha_datasheet_id or opr_unit_id), and starting quantity. For 40K, starting quantity is derived from `view_40k_unit_composition` (e.g. min size). The new row is created in `play_armylist_entries`; upgrades and enhancements are applied later in the detail dialog.

### Roster computation and display

- **Roster data** — For 40K, `GetArmyRoster(list_id)` returns one row per roster entry with unit name, quantity, entry-level total points (base + enhancements + wargear adjustments as implemented), and optional wargear list. For OPR, `GetOPRArmyRoster(list_id)` returns analogous rows with base cost, upgrade cost, quantity, and total points. Both procedures join `play_armylist_entries` with the appropriate unit and upgrade/enhancement tables so that the UI never recomputes points locally.
- **Quantity and options** — In the roster editor, quantity can be toggled (e.g. min/max for 40K) where the datasheet allows. Wargear and enhancements are edited in the unit detail dialog; changes are written to `play_armylist_wargear_selections`, `play_armylist_enhancements` (40K), or `play_armylist_opr_upgrades` (OPR). The next reload re-runs the roster procedure so the main list and points stay in sync.

### Validation (40K)

- **Rule of 3** — A validation view (`view_list_validation_40k`) compares unit counts to allowed maximums (e.g. 3 for most units). Violations are shown in the sidebar.
- **Chapter/faction mismatch** — Units with faction keywords that do not match the list’s primary (and allowed allies) are flagged unless **Proxy / Custom Chapter mode** is enabled, in which case keyword restrictions are bypassed for list building only.

---

## Digital library logic

The Digital Library manages the STL catalog and its links to game units. It supports discovery, linking, and auditing per game system.

### STL gallery (main catalog)

- **Data source** — `stl_library` (e.g. name, `mmf_id`, creator, preview URL). The gallery displays a grid of entries with optional preview image, name, and actions.
- **Filters** — Search by name or MMF ID; optional filter by **Creator** from distinct `creator_name` values. Results are the subset of `stl_library` matching those criteria.
- **Actions** — **Link** opens the link dialog to associate the STL with a game unit. **MMF** opens the MyMiniFactory URL for the model (URL is normalized to a consistent `object/3d-print-...` form).

### Link dialog (STL → unit)

- **Flow** — User chooses **game system** (40K or OPR). Faction options are then loaded from `waha_datasheets` (40K) or `opr_units` (OPR). User may filter by faction and/or search by unit name. Selecting a unit and confirming creates or updates a row in `stl_unit_links` with `mmf_id`, `unit_id`, `game_system`, and an **is_default** flag.
- **Default image** — “Set as Default Image?” allows marking this link as the default proxy for that unit in that system. When set, any existing default for that `(unit_id, game_system)` is cleared so only one default exists per unit per system. The builder and detail dialogs use this default for preview/display when present.

### Audit tabs (OPR and 40K)

- **Purpose** — Audit tabs list existing links between STLs and units for one game system, so users can see coverage (which units have proxies) and change default assignments.
- **OPR audit** — Joins `stl_unit_links`, `stl_library`, and `opr_units` where `game_system != '40K_10E'`. Filters: OPR system (e.g. grimdark-future), army (multiselect). Results are shown in a data editor; **Default** can be toggled per row. Saving persists `is_default` changes (clearing previous default for that unit/system when a new default is set).
- **40K audit** — Same idea with `waha_datasheets` and `game_system = '40K_10E'`; filter by faction(s). Same default-toggle and save behavior.
- **Tables** — `stl_unit_links` is the single bridge table; `stl_library` holds STL metadata. No separate “inv_” inventory table is required for the link dialog or audit; those flows are entirely STL ↔ unit mapping.

---

## Related documentation

- **Wargaming_ERP/README.md** — Application architecture, tech stack, maintenance (e.g. OPR_JSON_analyzer, metadata locks, safe updates), and roadmap.
- **Wargaming_ERP/DataDictionary.md** — Full table and column reference for the `wargaming_erp` schema.
