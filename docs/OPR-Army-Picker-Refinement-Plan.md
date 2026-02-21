# OPR Army Picker Refinement Plan

Goal: bring the OPR library picker (sidebar “OPR Library”) closer to the 40K picker by adding **sorting**, **grouping**, **pagination**, and **search improvements**.

---

## Current State

### OPR picker (opr_builder.py)

- **Search:** Single text input, filters by `name LIKE %search%`; applied in SQL. Works.
- **Sorting:** Fixed `ORDER BY name ASC` in SQL only.
- **Grouping:** None; flat list of units.
- **Pagination:** Hard `LIMIT 40` in SQL; no Prev/Next. Users only see first 40 matches.
- **Display:** Unit name, [Hero]/[N models], faction — pts, Add + Info buttons.

### 40K picker (w40k_builder.py) — reference

- **Search:** “Search Units” text input; `name LIKE %search%`; higher limit (500).
- **Sorting:** By role order (Epic Hero → Character → Battleline → …) then by name. Role from keywords.
- **Grouping:** By role (Epic Hero, Character, Battleline, Monster, Vehicle, …); section headers in sidebar.
- **Pagination:** Session state `lib_page_{list_id}`, page size 20, “◀ Prev” / “Next ▶”, caption “X units · Page Y of Z”.
- **Display:** Role header, unit name, pts, “In list: N”, Add button.

---

## Proposed Features for OPR

### 1. Search (enhance)

- **Keep:** Current search box and SQL `name LIKE %search%`.
- **Optional:** Placeholder “Search by unit name…” to match 40K.
- **Optional:** If no search term, consider raising the fetch limit (see pagination) so “browse all” is possible.

### 2. Sorting (add)

- **Options (sidebar selectbox or radio):**
  - **Name A–Z** (current behavior).
  - **Name Z–A.**
  - **Points low → high.**
  - **Points high → low.**
  - **Role/type** (Heroes first, then by generic_name group, then name) — aligns with grouping.
- **Implementation:** Fetch more rows (no ORDER BY or ORDER BY name), then sort in Python by chosen option. Or add `ORDER BY` variants in SQL (name ASC/DESC, points ASC/DESC); for “by role” do in-memory sort after assigning group order (see grouping).

### 3. Grouping (add)

- **Source:** `view_opr_master_picker` already exposes `generic_name` (e.g. “Heavy Infantry Hero”, “Core Infantry”).
- **Map generic_name → display group** (reuse logic from `scripts/opr/fetch_opr_json.py` `generic_name_to_group()`):
  - Heroes  
  - Core  
  - Special  
  - Support  
  - Vehicles & Monsters  
  - Other  
- **UI:** Section headers in sidebar (e.g. **Heroes**, **Core**, …) like 40K’s role headers; list units under each group. Groups can be ordered (e.g. Heroes, Core, Special, Support, Vehicles & Monsters, Other).
- **Optional:** Toggle “Group by type” on/off (grouped vs flat list).

### 4. Pagination (add)

- **Remove** hard `LIMIT 40` for the main fetch; use a higher limit (e.g. 200–500) or no limit, constrained by performance.
- **Session state:** e.g. `opr_lib_page_{active_id}`.
- **Page size:** 20 (match 40K).
- **UI:** Caption “X units · Page Y of Z” and “◀ Prev” / “Next ▶” when `total_pages > 1`.
- **Scope:** Apply pagination to the *sorted* (and optionally grouped) list in Python, so each page shows the correct slice. 40K does: sort → paginate → render current page; same pattern for OPR.

### 5. Dedupe (optional)

- If the same unit can appear multiple times (e.g. different `game_system` for same id), dedupe by unit `id` for display and “Add” (e.g. keep first occurrence per id). 40K does this with `_normalize_unit_id` and `seen_nid`. OPR may already have unique ids per faction+system; add dedupe if duplicates appear.

---

## Implementation Order

1. **Pagination** — Raise fetch limit, add session state, Prev/Next, caption. No change to sort/group. Delivers “see more than 40 units” immediately.
2. **Sorting** — Add sort option (name, points, role). Sort in Python after fetch (or add SQL ORDER BY for name/pts). Paginate after sort.
3. **Grouping** — Add `generic_name` → group helper; sort by group order + name; render with section headers. Optional “Group by type” toggle.
4. **Search tweaks** — Placeholder, any UX polish.
5. **Dedupe** — Only if duplicates are observed.

---

## Technical Notes

- **View:** `view_opr_master_picker` already has `generic_name`; no DB change needed for grouping.
- **Fetch:** Current query returns `id, name, faction, points, QUA, DEF, size, game_system, generic_name`. Enough for sort (name, points), group (generic_name), and display.
- **Group order:** Define a fixed order for OPR groups (e.g. Heroes=0, Core=1, Special=2, Support=3, Vehicles & Monsters=4, Other=5) and sort by (group_order, name) before pagination.
- **Session state:** Use `st.session_state[f"opr_lib_page_{active_id}"]` and reset page to 0 when search or sort changes so user doesn’t land on an empty page.

---

## Out of Scope (for later)

- Filter by unit type (e.g. “Heroes only”) — can be added as a filter dropdown once grouping exists.
- “In list: N” for OPR (show how many of each unit are already in the roster) — same pattern as 40K roster_unit_counts.

---

## Summary

| Feature   | 40K Picker      | OPR (current) | OPR (proposed)                    |
|----------|------------------|---------------|-----------------------------------|
| Search   | ✅ name          | ✅ name       | ✅ keep; optional placeholder     |
| Sort     | ✅ role, name     | ❌ name only  | ✅ name, points, role             |
| Grouping | ✅ by role       | ❌            | ✅ by generic_name → group        |
| Pagination | ✅ 20/page, Prev/Next | ❌ LIMIT 40 | ✅ 20/page, Prev/Next, caption   |
| Dedupe   | ✅ by id         | ❌            | ✅ if needed                      |

This plan aligns OPR with 40K patterns so both builders feel consistent and the OPR picker scales to large rosters (e.g. 100+ units per army).

---

## Implementation status (done)

- **OPR picker:** Search placeholder, fetch limit 500, dedupe by id, sort (Name A–Z, Z–A, Points ↑/↓, Role), "Group by type" toggle, pagination (20/page, Prev/Next, caption), section headers (Heroes, Core, Special, Support, Vehicles & Monsters, Other). See `opr_builder.py` and helper `_opr_generic_name_to_group` + `OPR_GROUP_ORDER`.
- **40K picker:** Sort selectbox (By role (default), Name A–Z, Name Z–A, Points ↑, Points ↓), "Group by role" toggle. See `w40k_builder.py` (`sort_choice_40k`, `group_by_role_40k`, `_w40k_sort_key`).
- **OPR composite PK:** `opr_units` uses `(opr_unit_id, army)` so the same unit can exist per army; hydrator and GetArmyRoster/AddUnit join by `faction_primary` where needed.
- **Prime Brothers variants:** For "* Prime Brothers" lists (e.g. Blood Prime Brothers, Wolf Prime Brothers), the library also includes units from the base "Prime Brothers" army; variant row is preferred when the same unit exists in both.
- **Battle Brothers variants:** For "* Brothers" lists that are not Prime (e.g. Blood Brothers, Wolf Brothers, Dark Brothers), the library also includes units from the base "Battle Brothers" army; variant row is preferred when the same unit exists in both.
