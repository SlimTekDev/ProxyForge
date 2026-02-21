# 40K Army Builder Overhaul Plan

This doc outlines refinements for the 40K army builder: unit selector, rules/detachment awareness, list validation, single/double unit selection, and deduplication.

---

## 1. Unit selector & rules awareness



**Current state**

- Unit picker is filtered by faction (and optionally chapter for Space Marines).
- Chapter selection is persisted in `play_armylists.chapter_subfaction` and used by `view_list_validation_40k`.
- Allied units (Imperial Agents, Imperial Knights) can be toggled for Space Marines.

**Planned / suggested refinements**

- **Detachment-aware picker**: Restrict or highlight units that are explicitly allowed by the selected detachment (e.g. from Wahapedia detachment–datasheet links or rules). Today we only filter by faction/chapter; detachment rules could further limit or tag units.
- **Subfaction beyond Space Marines**: Extend the “chapter/subfaction” pattern to other factions that have subfaction keywords (e.g. Craftworlds, Hive Fleets) so the picker and validation respect them.
- **Clear “why this unit”**: In the unit picker or unit details, show why a unit is valid (faction + chapter/detachment) so list-building rules are transparent.

---

## 2. List validation

**Current state**

- `view_list_validation_40k` uses `play_armylists.chapter_subfaction` (and proxy mode) to mark entries valid/invalid by chapter keyword.
- Validation is shown in the roster (e.g. badges / status).

**Planned / suggested refinements**

- **Structured validation messages**: Return validation result per entry (e.g. `VALID`, `INVALID: wrong chapter`, `WARNING: Rule of 3`) and display them consistently in the roster and in a summary (e.g. “2 warnings, 0 errors”).
- **Detachment rules**: When detachment data is available, validate that units are allowed in the selected detachment and surface detachment-specific errors.
- **Point limits and compulsory slots**: Validate total points vs list limit and, if we have slot data (e.g. required HQ), validate those too.

---

## 3. Single / double (min–max) unit size

**Current state**

- `view_40k_unit_composition` exposes `min_size` and `max_size` (see migration `recreate_view_40k_unit_composition_with_max.sql`).
- Roster editor shows a “Min/Max” toggle for units that have a size range (`max_size > min_size`); otherwise it shows a fixed quantity.

**If Min/Max doesn’t appear**

- Ensure the migration has been run so the view includes `max_size`.
- Check that `waha_datasheet_unit_composition.description` is populated (e.g. “1–6” or “3–6”) so the view can derive `max_size`.

---

## 4. Double entries (deduplication)

**Likely causes**

- **Join multiplicity**: Views like `view_40k_army_rules` join detachments and detachment abilities; one detachment can have multiple abilities, so the view can return multiple rows per faction+detachment. UIs that iterate over “all rows” without collapsing can show the same army rule or detachment rule multiple times.
- **Duplicate rows in base tables**: After rehydration, tables such as `waha_datasheets_abilities` or `waha_datasheets_keywords` may contain duplicate rows (same logical entity) if:
  - CSV or source data has duplicate lines, or
  - Inserts run multiple times without a unique constraint or “replace” semantics.

**Fixes applied**

- **UI deduplication**: When displaying lists that can have duplicate rows (abilities, stratagems, options), we deduplicate in Python by a stable key (e.g. name + description) before rendering. See `w40k_army_book_ui.py` (abilities, options) and `w40k_builder.py` (stratagems).
- **DB cleanup**: A migration/script `dedupe_waha_abilities_keywords.sql` (or equivalent) removes duplicate rows from `waha_datasheets_abilities` and `waha_datasheets_keywords` while keeping one row per logical key. Running it after rehydration prevents duplicate entries in unit pickers and army book special rules.
- **Hydrators**: Prefer “replace” or “delete + insert” for the affected tables and, where possible, add unique constraints so re-runs do not create duplicates.

---

## 5. Other refinements

- **Roster UX**: Keep Game-Day view; consider export (e.g. PDF or text) of the current roster with validation summary.
- **Performance**: Batch DB calls (e.g. unit composition, chapter keywords) as already done; avoid N+1 queries when loading large rosters.
- **Proxy mode**: Keep current behavior (relax validation when enabled) and document it in the UI (e.g. “Proxy mode: list is not strictly validated”).

---

## 6. Files touched

| Area              | File / asset |
|-------------------|--------------|
| 40K builder       | `ProxyForge/w40k_builder.py` |
| **40K roster (data layer)** | `ProxyForge/w40k_roster.py` – single source of truth: roster rows carry canonical `datasheet_id` from JOIN with `waha_datasheets`; use for all unit-detail lookups (roster view, unit details dialog, Game-Day view). |
| 40K army book     | `ProxyForge/w40k_army_book_ui.py` |
| Validation view   | `ProxyForge/migrations/add_chapter_subfaction_and_validation_view.sql` |
| Unit composition | `ProxyForge/migrations/recreate_view_40k_unit_composition_with_max.sql` |
| Dedupe            | `ProxyForge/migrations/dedupe_waha_abilities_keywords.sql` (see migrations folder) |
