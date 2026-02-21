# 40K Army Builder — Design Phase

This document resets to **design phase**: intended data flow, where things can break, and a proposal to separate 40K and OPR list storage so the 40K builder has a single, clear data path.

---

## 1. Intended behaviour (first principles)

### 1.1 What the user does

1. **Create a 40K list** – Name, point limit, primary faction. Stored as one row in “list” table.
2. **Select active list** – Sidebar shows 40K lists only; user picks one. Builder loads that list’s roster.
3. **Add units** – From a **library** (units that exist in `waha_datasheets` for the chosen faction). Each “Add” creates one **roster entry** (this list + this unit + quantity).
4. **View roster** – Each row: unit name, points, quantity, controls (view details, delete). Optional: min/max size toggle, chapter badge, wargear summary.
5. **View unit details** – From roster row or from library: same **unit datasheet** (stats, weapons, composition, rules, enhancements, stratagems). Must show the same data whether opened from roster or library.
6. **Game-Day view** – Same roster, each unit as an expandable card with stats, composition, weapons, abilities, stratagems.

### 1.2 Single source of truth for “which unit”

- **Unit** = one row in `waha_datasheets` (primary key `waha_datasheet_id`).
- **Roster entry** = “this list contains this unit, with this quantity (and optional wargear/enhancement choices).”
- **Rule:** Every place that needs to show unit data (name, points, weapons, composition, etc.) must use the **same** identifier that `waha_datasheets` and its child tables use: **`waha_datasheet_id`**.

So:

- When we **store** an “add unit” we must store a value that **equals** some `waha_datasheets.waha_datasheet_id`.
- When we **load** the roster we must produce, for each entry, that same `waha_datasheet_id` (e.g. via JOIN) and use **only that** for any lookup into `waha_datasheets_*`.

No mixing of “raw `unit_id` from entries table” with “resolved” id in some places and not others.

---

## 2. Current data model (combined 40K + OPR)

### 2.1 Shared tables

| Table | Role | 40K use | OPR use |
|-------|------|---------|---------|
| `play_armylists` | One row per list | `game_system = '40K_10E'`, `faction_primary`, `waha_detachment_id`, etc. | `game_system = 'OPR'`, `faction_primary` |
| `play_armylist_entries` | One row per unit-in-list | `unit_id` = `waha_datasheet_id` (should be) | `unit_id` = `opr_unit_id` |

So:

- **40K** and **OPR** share the same list and entry tables; `game_system` (on the list) distinguishes them.
- Every 40K path (roster load, add unit, unit details, gameday) depends on:
  - `play_armylists.game_system = '40K_10E'`
  - `play_armylist_entries.unit_id` = `waha_datasheets.waha_datasheet_id` (type and value).

### 2.2 Where the join happens

- **Roster load:** Something must return, for each 40K roster entry, the **canonical** `waha_datasheet_id` (e.g. from `JOIN waha_datasheets d ON e.unit_id = d.waha_datasheet_id`). If the JOIN fails (wrong/missing `unit_id`), that entry has no unit data.
- **Unit details (from roster):** Given `entry_id`, we need that same `waha_datasheet_id` (e.g. same JOIN by `entry_id`) and then use it for all `waha_*` queries.
- **Game-Day:** Same: each row must carry or resolve that same `waha_datasheet_id` and use it for all detail queries.

If any step uses a different key (e.g. raw `e.unit_id` with different type/casing) or a different code path, roster and details can show nothing even when data exists.

### 2.3 Likely failure points (combined model)

1. **Roster not loading at all**
   - `get_roster_40k(conn, list_id)` returns empty: e.g. `list_id` not in `play_armylists`, or `game_system != '40K_10E'`, or no rows in `play_armylist_entries` for that list.
   - Exception in `get_roster_40k` (e.g. missing view/column): caller gets empty roster and maybe no clear error.

2. **Roster loads but unit details / gameday empty**
   - JOIN `e.unit_id = d.waha_datasheet_id` fails (type/collation mismatch, or `e.unit_id` not actually a `waha_datasheet_id`). Then `datasheet_id` is NULL and all lookups by it return nothing.
   - UI uses wrong field (e.g. `unit_id` instead of `datasheet_id`) for wargear/composition/abilities.

3. **Add unit stores wrong value**
   - Picker sends something other than `waha_datasheet_id` (e.g. index, or id from another view). Then `play_armylist_entries.unit_id` never matches `waha_datasheets.waha_datasheet_id`.

4. **view_master_picker column name**
   - Code uses `WHERE game_system = '40K'` but view might expose `system` (value `'40K'`). If the view has no `game_system` column, the library query can fail or return nothing, so “Add” might never store a valid id.

5. **Shared table confusion**
   - 40K and OPR both write to `play_armylist_entries`. Any logic that doesn’t strictly filter by list’s `game_system` (e.g. when resolving “unit for this entry”) could mix systems or mis-handle types (opr_unit_id vs waha_datasheet_id).

---

## 3. Proposed direction: separate 40K and OPR list tables

### 3.1 Why separate

- **Clear ownership:** 40K lists and entries live in 40K-only tables. No `game_system` branch in every query.
- **Correct keys by design:** 40K entry table has a column that is **only** `waha_datasheet_id` (FK to `waha_datasheets`). No dual meaning (40K vs OPR) in one column.
- **Easier to debug:** One list table, one entry table, one JOIN to `waha_datasheets`. Flow is “40K list → 40K entries → waha_datasheets”.
- **Simpler code:** No `game_system = '40K_10E'` in every 40K path; no risk of OPR-specific views or procedures affecting 40K.

### 3.2 Proposed schema (40K-only)

- **`play_40k_lists`** (replaces “40K rows” of `play_armylists`)
  - `list_id` INT PK
  - `list_name`, `point_limit`, `faction_primary`, `waha_detachment_id`, `chapter_subfaction`, etc.
  - No `game_system` column.

- **`play_40k_entries`** (replaces “40K rows” of `play_armylist_entries`)
  - `entry_id` INT PK
  - `list_id` FK → `play_40k_lists.list_id`
  - **`waha_datasheet_id`** VARCHAR(50) NOT NULL FK → `waha_datasheets.waha_datasheet_id`  ← single meaning
  - `quantity` INT
  - No `unit_id` dual-purpose column.

Existing 40K-specific child tables (e.g. enhancements, wargear selections, STL choices) would reference `play_40k_entries.entry_id` (or we keep `entry_id` globally and add a one-to-one from `play_40k_entries` to a shared “entry” id if we want to keep STL/choices shared; see below).

### 3.3 OPR side

- **`play_opr_lists`** and **`play_opr_entries`** with `opr_unit_id` (and OPR-specific columns as needed). Same idea: one system, one set of tables, no `game_system` in the middle.

### 3.4 Migration path (high level)

1. Create new tables: `play_40k_lists`, `play_40k_entries` (and optionally OPR equivalents).
2. Migrate data: `INSERT INTO play_40k_lists SELECT ... FROM play_armylists WHERE game_system = '40K_10E'`; same for entries (with `waha_datasheet_id = unit_id` for 40K entries).
3. Point 40K builder only at new tables (roster load, add unit, unit details, gameday).
4. Keep `play_armylists` / `play_armylist_entries` for OPR until OPR is migrated, then deprecate or drop.
5. Child tables (e.g. `play_armylist_enhancements`, `play_armylist_wargear_selections`, `play_armylist_stl_choices`): either
   - Add `play_40k_entry_id` and migrate 40K data to reference `play_40k_entries`, or
   - Keep a single `entry_id` space and have `play_40k_entries.entry_id` replace the old 40K `play_armylist_entries.entry_id` (so existing FKs still work if we reuse IDs).

A separate migration doc can spell out exact column mapping and FK handling.

---

## 4. 40K builder flow (target, after separation)

### 4.1 Roster load

- **Input:** `list_id` (from `play_40k_lists`).
- **Query:**  
  `SELECT e.entry_id, e.waha_datasheet_id AS datasheet_id, e.quantity AS Qty, d.name AS Unit, (points expression) AS Total_Pts, (wargear JSON) AS wargear_list FROM play_40k_entries e JOIN waha_datasheets d ON e.waha_datasheet_id = d.waha_datasheet_id WHERE e.list_id = %s`
- **Output:** List of dicts (or DataFrame) with **datasheet_id** on every row (no NULL from JOIN, because of FK).
- **Use:** Roster table and Game-Day only use **datasheet_id** for any further lookup (wargear, composition, abilities, etc.).

### 4.2 Add unit

- **Input:** `list_id`, unit chosen from library (picker).
- **Resolve:** Picker must supply `waha_datasheet_id` (e.g. from `waha_datasheets` or a view that exposes it). If picker exposes something else (e.g. `id` from another view), resolve once: `SELECT waha_datasheet_id FROM waha_datasheets WHERE waha_datasheet_id = %s OR name = %s`.
- **Write:** `INSERT INTO play_40k_entries (list_id, waha_datasheet_id, quantity) VALUES (%s, %s, %s)`.

### 4.3 Unit details (from roster)

- **Input:** `entry_id` (and optionally list context).
- **Resolve:** `SELECT e.waha_datasheet_id FROM play_40k_entries e WHERE e.entry_id = %s` → one value.
- **Use:** That `waha_datasheet_id` for every query in the dialog (view_40k_datasheet_complete, waha_datasheets_models, wargear, composition, abilities, stratagems).

### 4.4 Unit details (from library)

- **Input:** `unit_id` = `waha_datasheet_id` from picker (no entry_id).
- **Use:** That value directly for all the same queries. No JOIN needed.

### 4.5 Game-Day

- **Input:** Roster rows from 4.1 (each has **datasheet_id**).
- **Use:** For each row, use **row["datasheet_id"]** for models, composition, wargear, abilities, keywords. No extra resolution.

---

## 5. What to do with the current (combined) builder before splitting

If we **keep** the combined tables for now and only fix the 40K path:

1. **Verify roster query**
   - Run `get_roster_40k(conn, list_id)` in a small script or notebook with a known 40K `list_id` that has entries. Check: do you get rows? Is `datasheet_id` non-NULL? If not, the JOIN is failing (check `e.unit_id` vs `d.waha_datasheet_id` type/value).
2. **Verify view_master_picker**
   - Run `SELECT * FROM view_master_picker WHERE ... LIMIT 1` and inspect column names. If the view has `system` not `game_system`, fix the library query to use `system = '40K'` (or add a `game_system` alias to the view).
3. **Single code path**
   - Ensure every 40K consumer (roster row, unit details when opened from roster, gameday card) uses **only** the `datasheet_id` that comes from the JOIN (or from `get_datasheet_id_for_entry`). Never use raw `unit_id` for waha_* lookups.
4. **Add unit**
   - Ensure the value written to `play_armylist_entries.unit_id` is exactly the string (or value) that appears in `waha_datasheets.waha_datasheet_id` (and that the JOIN uses the same type/collation).

Even with these fixes, the combined model remains brittle (shared table, dual meaning of `unit_id`). Separation gives a clean 40K-only path and makes “roster data not displaying” easier to trace (one list table, one entry table, one JOIN).

---

## 6. Files and next steps

| Item | Location |
|------|----------|
| Design (this doc) | `docs/40K-Army-Builder-Design.md` |
| Overhaul plan | `docs/40K-Army-Builder-Overhaul-Plan.md` |
| Feature parity | `docs/40K-Feature-Parity-Research.md` |
| Current 40K roster layer | `ProxyForge/w40k_roster.py` (uses `play_armylists` + `play_armylist_entries`) |
| Current 40K UI | `ProxyForge/w40k_builder.py` |
| App entry (40K vs OPR) | `ProxyForge/app.py` (branch by game system, single list/entry tables) |

**Recommended next steps**

1. **Short term (done):** A debug script and sidebar panel now show DB outputs for the key queries (see “Seeing DB outputs for all views” above). Use them to confirm list_id, roster rows, datasheet_id, and view_master_picker.
2. **Medium term:** Implement separate tables `play_40k_lists` and `play_40k_entries` with migration and point the 40K builder only at them (roster load, add, details, gameday). Then 40K roster display and unit data have a single, predictable path.
3. **Later:** Migrate OPR to `play_opr_lists` / `play_opr_entries` and deprecate the combined list/entry tables.

---

## 7. Debug checklist (why is roster not displaying?)

Run these in order to see where the pipeline fails.

1. **Is the list 40K?**
   - `SELECT list_id, list_name, game_system FROM play_armylists WHERE list_id = <your_list_id>;`
   - Expect `game_system = '40K_10E'`. If not, the 40K roster query filters it out.

2. **Are there entries?**
   - `SELECT entry_id, list_id, unit_id, quantity FROM play_armylist_entries WHERE list_id = <your_list_id>;`
   - If empty, nothing will display. Add a unit from the library and retry.

3. **Does the JOIN to waha_datasheets succeed?**
   - `SELECT e.entry_id, e.unit_id, d.waha_datasheet_id, d.name FROM play_armylist_entries e LEFT JOIN waha_datasheets d ON e.unit_id = d.waha_datasheet_id WHERE e.list_id = <your_list_id>;`
   - If `d.waha_datasheet_id` or `d.name` is NULL for a row, that entry’s `unit_id` does not match any `waha_datasheets.waha_datasheet_id` (type or value). Fix by re-adding that unit from the library so the correct id is stored, or by updating `e.unit_id` to the correct `waha_datasheet_id`.

4. **Does view_master_picker expose the right column?**
   - `SELECT * FROM view_master_picker LIMIT 1;` (or `WHERE ... faction = 'Orks'`).
   - Check column names. If you see `system` and not `game_system`, the library query in the app may be wrong (e.g. `WHERE game_system = '40K'` returns no rows). Fix: use `system = '40K'` in the query or alter the view to expose `game_system`.

5. **What does get_roster_40k return?**
   - In Python: `from database_utils import get_db_connection; from w40k_roster import get_roster_40k; conn = get_db_connection(); rows = get_roster_40k(conn, <list_id>); print(len(rows)); print(rows[0] if rows else None)`
   - If `len(rows) == 0`, the query in `get_roster_40k` returns no rows (list_id wrong, or JOIN + filter exclude everything). If `rows[0]["datasheet_id"]` is None, the JOIN failed for that entry (see step 3).

6. **view_40k_datasheet_complete returns no rows for a unit (e.g. Boyz)?**
   - The original view filters by `m.line_id = 1`. Some units (e.g. Boyz) have their first model row with a different `line_id`, so they never match. Run the migration **`ProxyForge/migrations/recreate_view_40k_datasheet_complete_first_model.sql`** so the view uses the first model row per datasheet (MIN(line_id)). After that, unit details and Game-Day will show stats for all units.

**Seeing DB outputs for all views**

- **Script (terminal):** From the `ProxyForge` directory run  
  `python debug_40k_db_queries.py [list_id] [datasheet_id]`  
  If `list_id` is omitted, the first 40K list is used. This prints the same queries as below in order (lists, raw entries, JOIN, get_roster_40k, view_master_picker, unit-detail views, validation, unit composition).
- **In the app:** In the 40K Army Builder sidebar, expand **🔧 DB query results**. It shows the same query result sets (as dataframes) so you can confirm what the roster, unit details, and validation logic are using.
