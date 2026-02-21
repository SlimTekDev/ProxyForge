# 40K Spot-Check Recommendations — Implementation Plan

This plan implements the recommendations from [40K-Spotcheck-Wahapedia-Comparison.md](40K-Spotcheck-Wahapedia-Comparison.md), **excluding recommendation #2** (name matching; confirmed correct in DB).

---

## Overview

| # | Recommendation | Plan section |
|---|----------------|--------------|
| 1 | Populate abilities | [1. Populate datasheet abilities](#1-populate-datasheet-abilities) |
| 2 | ~~Name matching~~ | *Excluded per user* |
| 3 | Transport on vehicles | [2. Populate transport on waha_datasheets](#2-populate-transport-on-waha_datasheets) |
| 4 | Enhancements for detachments | [3. Ensure enhancements loaded for detachments](#3-ensure-enhancements-loaded-for-detachments) |

---

## 1. Populate datasheet abilities

**Goal:** Fill `waha_datasheets_abilities` (and `waha_abilities`) so the builder and Game-Day view show CORE, FACTION, and datasheet abilities for units (e.g. Ork Boyz, Warboss, Battlewagon, Intercessors, Marneus Calgar, Crisis Battlesuits).

**Dependencies:** Wahapedia CSVs in `data/wahapedia/`. The abilities pipeline needs:
- `Datasheets_abilities.csv` — links datasheets to abilities (datasheet_id, line, ability_id, model, name, description, type).
- The full hydrator also expects the core id-chain (Factions, Detachments, Datasheets) so datasheet IDs match.

**Steps:**

1. **Ensure CSVs are present** for the factions you use (Orks, Space Marines, Tau):
   - Place pipe-delimited Wahapedia exports in `data/wahapedia/` so that at least these exist:
     - `Factions.csv`, `Detachments.csv`, `Datasheets.csv` (required for id consistency).
     - **`Datasheets_abilities.csv`** (required for abilities).
   - Optional: use `Cleaned_CSVs/` for abilities only; the hydrator prefers cleaned `Datasheets_abilities.csv` when present (see [Wahapedia-40K-Fetcher-Hydrator-Plan.md](Wahapedia-40K-Fetcher-Hydrator-Plan.md)). Core id-chain files should stay in root so IDs match.

2. **Run the full Wahapedia hydrator** (recommended so all IDs and link tables stay in sync):
   ```powershell
   python scripts/wahapedia/hydrate_waha_full.py
   ```
   This runs all steps including `abilities` and `datasheets_abilities`.  
   **Or** run only the abilities-related steps (after a prior full run that already populated factions/datasheets):
   ```powershell
   python scripts/wahapedia/hydrate_waha_full.py --tables abilities,datasheets_abilities
   ```

3. **Optional — dedupe after rehydration:** If you see duplicate abilities in the UI, run:
   ```powershell
   # Run dedupe migration (MySQL 8.0+)
   # See ProxyForge/migrations/dedupe_waha_abilities_keywords.sql
   ```

4. **Verify:** Open a spot-check unit (e.g. Ork Boyz) in the 40K Army Builder; the Rules tab should show abilities (e.g. FACTION: Waaagh!, Get Da Good Bitz). Alternatively run `python scripts/spotcheck_export_40k_units.py` and confirm abilities are listed in the output.

**References:** `scripts/wahapedia/hydrate_waha_full.py` (steps `abilities`, `datasheets_abilities`); `docs/Wahapedia-40K-Fetcher-Hydrator-Plan.md` (steps 8–9).

---

## 2. Populate transport on waha_datasheets

**Goal:** Fill `waha_datasheets.transport` so vehicles (e.g. Battlewagon) show transport capacity in the builder and Game-Day view. The UI already reads this column when present.

**Dependencies:** Column must exist; then `Datasheets.csv` must contain a `transport` column (Wahapedia export).

**Steps:**

1. **Apply migration if not already done:**
   - Run `ProxyForge/migrations/add_waha_datasheets_extra.sql` so that `waha_datasheets` has the `transport` column (and legend, role, loadout, damaged_*, link). If the column already exists, you can ignore “Duplicate column” for that line.

2. **Run the datasheets-extra hydrator** so transport (and other extra fields) are filled from `Datasheets.csv`:
   ```powershell
   python scripts/wahapedia/hydrate_waha_datasheets_extra.py
   ```
   With a custom file:
   ```powershell
   python scripts/wahapedia/hydrate_waha_datasheets_extra.py --file path/to/Datasheets.csv
   ```
   The script prefers root `data/wahapedia/Datasheets.csv` first so datasheet IDs match the DB.

3. **Verify:** Open a transport (e.g. Ork Battlewagon) in the builder; the Rules tab “Led By / Can Lead / Transport” section should show transport capacity text.

**References:** `scripts/wahapedia/hydrate_waha_datasheets_extra.py`; `ProxyForge/migrations/add_waha_datasheets_extra.sql`; `ProxyForge/w40k_builder.py` (`_show_led_by_can_lead_transport`).

---

## 3. Ensure enhancements loaded for detachments

**Goal:** So that the enhancement picker shows options for the selected detachment, ensure `waha_enhancements` is populated and linked to detachments via `detachment_id`. The builder uses `view_40k_enhancement_picker`, which joins `waha_enhancements` and `waha_detachments`.

**Steps:**

1. **Ensure enhancement CSVs are present:**
   - In `data/wahapedia/`, include **`Enhancements.csv`** with columns: id, faction_id, name, cost, detachment, detachment_id, legend, description (see [Wahapedia-40K-Fetcher-Hydrator-Plan.md](Wahapedia-40K-Fetcher-Hydrator-Plan.md) step 14).

2. **Run the full hydrator** (which includes the `enhancements` step), or run enhancements after factions and detachments:
   ```powershell
   python scripts/wahapedia/hydrate_waha_full.py
   ```
   Or only:
   ```powershell
   python scripts/wahapedia/hydrate_waha_full.py --tables factions,detachments,enhancements
   ```
   Ensure `Detachments.csv` is loaded so `waha_detachments` has the `id` values that `Enhancements.csv` references in `detachment_id`.

3. **Verify:** Create or open a 40K list, select a detachment (e.g. Orks), add a Character unit, open unit details; the Enhancements section should list detachment enhancements. If you see “No enhancements found for this detachment”, check that `waha_enhancements` has rows and that `detachment_id` matches `waha_detachments.id` for the chosen detachment.

**References:** `scripts/wahapedia/hydrate_waha_full.py` (step `enhancements`); `ProxyForge/w40k_builder.py` (enhancement picker uses `view_40k_enhancement_picker`).

---

## Execution order (single pass)

If starting from a clean or partial DB and you have all CSVs in `data/wahapedia/`:

1. Run **full hydrator** once (covers abilities + enhancements + base datasheets):
   ```powershell
   python scripts/wahapedia/hydrate_waha_full.py
   ```
2. Run **datasheets extra** (transport, legend, role, loadout, etc.):
   ```powershell
   python scripts/wahapedia/hydrate_waha_datasheets_extra.py
   ```
3. Optional: run **dedupe** if you see duplicate abilities/keywords:
   - `ProxyForge/migrations/dedupe_waha_abilities_keywords.sql`
4. Re-run spot-check export and/or open units in the builder to confirm abilities, transport, and enhancements.

### Using a specific export folder

If you downloaded a Wahapedia export into a subfolder (e.g. `data/wahapedia/WahaExport2.19.26`), point both scripts at that folder so all IDs come from the same source:

1. **Full hydrator** (use `--data-dir`):
   ```powershell
   cd C:\Users\slimm\Desktop\WahapediaExport
   python scripts/wahapedia/hydrate_waha_full.py --data-dir "data\wahapedia\WahaExport2.19.26"
   ```
2. **Datasheets extra** (use `--file` so it reads the same `Datasheets.csv`):
   ```powershell
   python scripts/wahapedia/hydrate_waha_datasheets_extra.py --file "data\wahapedia\WahaExport2.19.26\Datasheets.csv"
   ```
3. Optional: dedupe and verify as above.

### Faction ability names and Core stratagems

- **FACTION "Unnamed Ability"**: The hydrator now has a step **abilities_csv_merge** that runs after `datasheets_abilities` and merges names/descriptions from **Abilities.csv** (when present in the export folder) into `waha_abilities`. That fills in names like "Waaagh!" for faction abilities. The UI also shows "FACTION (army rule)" when the name is still missing.
- **Stratagems on unit details**: The unit-details Stratagems tab shows (1) **detachment** stratagems (for the list’s chosen detachment) and (2) **Core** stratagems (in the export these have empty `detachment_id` or type containing "Core"). Both sets are combined and then filtered by unit keywords (e.g. INFANTRY, GRENADES) so only relevant stratagems are listed. Run the full hydrator with an export that includes **Abilities.csv** and **Stratagems.csv** so ability names and Core stratagems are present.

---

## Checklist

- [ ] **Abilities:** `Datasheets_abilities.csv` in `data/wahapedia/`; run `hydrate_waha_full.py` (or `--tables abilities,datasheets_abilities` after a full run).
- [ ] **Transport:** Migration `add_waha_datasheets_extra.sql` applied; `Datasheets.csv` has `transport`; run `hydrate_waha_datasheets_extra.py`.
- [ ] **Enhancements:** `Enhancements.csv` in `data/wahapedia/`; run full hydrator (or `--tables factions,detachments,enhancements`).
- [ ] **Verify:** Spot-check units show abilities; Battlewagon shows transport; enhancement picker shows options for selected detachment.
