# Proposal: Separate 40K and OPR Army List Tables

Separate tables for 40K and OPR lists so each builder has a single, clear data model and no shared `game_system` branching.

---

## 1. Current vs proposed

| Current | Proposed (40K) | Proposed (OPR) |
|--------|-----------------|-----------------|
| `play_armylists` (game_system = '40K_10E' or 'OPR') | `play_40k_lists` | `play_opr_lists` |
| `play_armylist_entries` (unit_id = waha_datasheet_id or opr_unit_id) | `play_40k_entries` (waha_datasheet_id FK) | `play_opr_entries` (opr_unit_id FK) |

Child tables (enhancements, wargear selections, STL choices) today reference `play_armylist_entries.entry_id`. Options:

- **A.** New tables use their own `entry_id`; add `play_40k_entry_id` (or `play_opr_entry_id`) to child tables and migrate 40K/OPR rows to point to the new entry PKs.
- **B.** New table `play_40k_entries` reuses the same `entry_id` space: migrate 40K rows from `play_armylist_entries` into `play_40k_entries` with the same `entry_id` values so existing FKs (enhancements, wargear, STL) still work without schema change. 40K builder then reads/writes only `play_40k_entries` and `play_40k_lists`.

Option B is less disruptive for existing child tables.

---

## 2. Proposed 40K tables (Option B: reuse entry_id)

### 2.1 `play_40k_lists`

```sql
CREATE TABLE play_40k_lists (
  list_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  list_name VARCHAR(100) DEFAULT NULL,
  point_limit INT DEFAULT 2000,
  faction_primary VARCHAR(100) DEFAULT NULL,
  waha_detachment_id VARCHAR(50) DEFAULT NULL,
  chapter_subfaction VARCHAR(100) DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (waha_detachment_id) REFERENCES waha_detachments(id)
);
```

### 2.2 `play_40k_entries`

```sql
CREATE TABLE play_40k_entries (
  entry_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  list_id INT NOT NULL,
  waha_datasheet_id VARCHAR(50) NOT NULL,
  quantity INT DEFAULT 1,
  FOREIGN KEY (list_id) REFERENCES play_40k_lists(list_id) ON DELETE CASCADE,
  FOREIGN KEY (waha_datasheet_id) REFERENCES waha_datasheets(waha_datasheet_id)
);
```

Child tables keep referencing `entry_id`; we migrate 40K data from `play_armylist_entries` into `play_40k_entries` **reusing the same entry_id values** so `play_armylist_enhancements`, `play_armylist_wargear_selections`, `play_armylist_stl_choices` still match (they already reference 40K entries by entry_id). We do **not** change those child tables; we only point the 40K builder at `play_40k_entries` and `play_40k_lists`.

---

## 3. Migration steps (40K)

1. Create `play_40k_lists` and `play_40k_entries` (as above).
2. Migrate list rows:
   - `INSERT INTO play_40k_lists (list_id, list_name, point_limit, faction_primary, waha_detachment_id, chapter_subfaction) SELECT list_id, list_name, point_limit, faction_primary, waha_detachment_id, chapter_subfaction FROM play_armylists WHERE game_system = '40K_10E';`
   - If `play_armylists` has no `chapter_subfaction`, omit or use default NULL.
3. Migrate entry rows (reuse entry_id):
   - `INSERT INTO play_40k_entries (entry_id, list_id, waha_datasheet_id, quantity) SELECT entry_id, list_id, unit_id, quantity FROM play_armylist_entries e JOIN play_armylists l ON e.list_id = l.list_id WHERE l.game_system = '40K_10E';`
   - This only migrates rows where the list is 40K; `unit_id` becomes `waha_datasheet_id`.
4. Update 40K builder code:
   - Roster load: query `play_40k_entries` JOIN `waha_datasheets` (no `play_armylists` / `game_system`).
   - Add unit: INSERT into `play_40k_entries`.
   - Unit details / gameday: resolve `waha_datasheet_id` from `play_40k_entries` by `entry_id`; use it for all waha_* lookups.
5. App sidebar: for “40K” mode, load lists from `play_40k_lists` instead of `play_armylists WHERE game_system = '40K_10E'`.
6. (Optional) Leave `play_armylists` / `play_armylist_entries` as-is for OPR until OPR is migrated; or add a parallel `play_opr_lists` / `play_opr_entries` and migrate OPR the same way later.

---

## 4. OPR separation (later)

- Create `play_opr_lists` and `play_opr_entries(opr_unit_id, ...)`.
- Migrate OPR lists and entries; reuse `entry_id` for entries so existing OPR child tables (e.g. upgrades) still work.
- Point OPR builder at the new tables; then deprecate or drop the 40K/OPR rows from `play_armylists` and `play_armylist_entries`.

---

## 5. Benefits

- **40K roster and details:** One list table, one entry table, one JOIN to `waha_datasheets`. No `game_system` in the middle; no dual meaning of `unit_id`.
- **Easier debugging:** “Roster not displaying” = check `play_40k_entries` and the JOIN to `waha_datasheets` only.
- **Clear ownership:** 40K code touches only 40K tables; OPR code only OPR tables (after OPR migration).

This proposal can be implemented in a single migration script and a focused refactor of the 40K builder to use the new tables only.
