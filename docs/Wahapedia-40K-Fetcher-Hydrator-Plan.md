# Wahapedia 40K fetcher/hydrator — plan and robustness

**Goal:** Make the 40K data pipeline complete and robust: clear CSV → DB mapping, correct load order, one-command hydration, and optional sync check so the DB only updates when exports change.

---

## 1. Current state

- **Source:** Wahapedia-style CSVs in `data/wahapedia/` (pipe-delimited; some from manual or semi-automated export).
- **DB:** `waha_*` tables in `wargaming_erp` (factions, detachments, datasheets, models, keywords, abilities, wargear, options, leader, stratagems, enhancements, etc.).
- **Existing scripts:**
  - `scripts/wahapedia/hydrate_waha_datasheets_extra.py` — updates only extra columns on `waha_datasheets` (legend, role, loadout, transport, damaged_*, link) from `Datasheets.csv`. Run after the main pipeline.
  - `scripts/opr/archive/CleanAll40K*.py`, `CleanDatasheets.py` — legacy cleaners (strip HTML, fix encoding); output to `Cleaned_CSVs/` if you want to use cleaned files as input.

There is **no single “load all Wahapedia CSVs into waha_*”** script yet. This doc and `scripts/wahapedia/hydrate_waha_full.py` define and implement that pipeline.

---

## 2. CSV → table mapping and load order

Load order respects foreign keys: parents first, then children and link tables.

| Step | CSV (in `data/wahapedia/`) | DB table(s) | Notes |
|------|----------------------------|-------------|--------|
| 1 | `Factions.csv` | `waha_factions` | id, name, link; parent_id optional if present in CSV. |
| 2 | `Detachments.csv` | `waha_detachments` | id, faction_id, name, legend, type. |
| 3 | `Datasheets.csv` | `waha_datasheets` | id→waha_datasheet_id, name, faction_id; base stats/points from next steps. |
| 4 | `Datasheets_models_cost.csv` | — | First line per datasheet → `waha_datasheets.points_cost`. **Requires same id scheme as Datasheets.csv** (same export); otherwise no rows match and points stay 0. |
| 5 | `Datasheets_models.csv` | `waha_datasheets_models` | datasheet_id, line→line_id, name, M→movement, T→toughness, Sv→save_value, W→wounds, Ld→leadership, OC→oc, base_size, inv_sv, inv_sv_descr, base_size_descr. |
| 6 | `Datasheets_unit_composition.csv` | `waha_datasheet_unit_composition` | datasheet_id, line→line_id, description. |
| 7 | `Datasheets_keywords.csv` | `waha_datasheets_keywords` | datasheet_id, keyword, model, is_faction_keyword (as 0/1). |
| 8 | (from `Datasheets_abilities.csv`) | `waha_abilities` | Distinct ability_id + name, description (faction_id optional). |
| 9 | `Datasheets_abilities.csv` | `waha_datasheets_abilities` | datasheet_id, line→line_id, ability_id, model→model_name, name, description, type. |
| 10 | `Datasheets_wargear.csv` | `waha_datasheets_wargear` | datasheet_id, line, line_in_wargear, name, description, range→range_val, type, A→attacks, BS_WS→bs_ws, S→strength, AP→ap, D→damage; dice optional. |
| 11 | `Datasheets_options.csv` | `waha_datasheets_options` | datasheet_id, line→line_id, button→button_text, description. |
| 12 | `Datasheets_leader.csv` | `waha_datasheets_leader` | leader_id, attached_id. |
| 13 | `Stratagems.csv` | `waha_stratagems` | id, faction_id, name, type, cp_cost, legend, turn, phase, detachment, detachment_id, description. |
| 14 | `Enhancements.csv` | `waha_enhancements` | id, faction_id, name, cost, detachment, detachment_id, legend, description. |
| 15 | `Datasheets_stratagems.csv` | `waha_datasheets_stratagems` | datasheet_id, stratagem_id. |
| 16 | `Datasheets_detachment_abilities.csv` | `waha_datasheets_detachment_abilities` | datasheet_id, detachment_ability_id. |

*Note:* `Datasheets_enhancements.csv` exists in the export but the current schema has no `waha_datasheets_enhancements` table; enhancements are linked to detachments via `waha_enhancements.detachment_id`. Add a junction table and step if you need per-datasheet enhancement availability.

**Tables without a direct CSV in this set (TBD or manual):**

- `waha_detachment_abilities` — needs a source (e.g. Detachment_abilities.csv or scrape). Leave empty or populate from another export.
- `waha_keywords` — lookup table; can be populated from distinct keywords in `Datasheets_keywords.csv` if desired.
- `waha_weapons` — weapon definitions; not required for the Army Book Reference / army builder if wargear lives in `waha_datasheets_wargear`.

After the full hydrator, run **`hydrate_waha_datasheets_extra.py`** to fill legend, role, loadout, transport, damaged_*, link on `waha_datasheets` (and run the migration first if not done).

---

## 3. Cleaned CSVs (preferred) and data update workflow

**Recommended workflow:** Process source CSVs through a cleaner **after fetching/exporting and before hydrating**, so the hydrator always consumes cleaned files and the DB stores text without HTML or bad encoding.

1. **Obtain source CSVs** — Export or copy Wahapedia-style CSVs into `data/wahapedia/` (e.g. manual export, or a future fetcher).
2. **Run cleaner** — Run a cleaner (e.g. `scripts/opr/archive/CleanAll40K3.py` or equivalent) so that cleaned output is written to `data/wahapedia/Cleaned_CSVs/`. The cleaner should strip HTML tags, fix/sanitize encoding, and optionally normalize delimiters. This step ensures abilities, descriptions, and other text fields are readable and consistent.
3. **Run hydration** — Run the full hydrator; it will prefer files in `Cleaned_CSVs/` when present (see below), so you are always loading cleaned data.

Cleaned files have non-UTF characters and HTML markup removed (e.g. via `CleanAll40K3.py` or similar). The hydrators **prefer cleaned sources** when present:

- **Full hydrator:** CSV keys are normalized (BOM stripped) so cleaned files with `\ufeffdatasheet_id` still match. For each CSV, looks in `data/wahapedia/Cleaned_CSVs/` first (same or alternate filename), then in `data/wahapedia/`, **except** for the core id-chain files `Datasheets.csv`, `Datasheets_models.csv`, `Datasheets_models_cost.csv`, and **Datasheets_abilities.csv** (root used so datasheet_id stays in sync). When loading **Datasheets_abilities.csv**, the hydrator **strips HTML** from ability name and description at intake so `waha_abilities` and `waha_datasheets_abilities` store plain text even when the CSV contains markup. Delimiter is auto-detected (pipe vs comma). Numeric ids from cleaned files are normalized to 9-digit form where needed.
- **Datasheets extra:** Tries **root `Datasheets.csv` first** so ids match the DB from the full hydrator, then `Datasheets_Clean.csv`, then `Cleaned_CSVs/Datasheets.csv`. Strips HTML from legend/loadout/transport/damaged_description when writing so root (pipe) content is stored without markup.

## 4. Robustness

- **Encoding:** Read CSVs as UTF-8 with `utf-8-sig` (strip BOM) and `errors="replace"` to avoid crashes on bad characters.
- **Delimiter:** Auto-detected from the first line (pipe `|` or comma `,`) so both raw (pipe) and cleaned (often comma) exports work.
- **Empty / whitespace:** Trim cell values; treat empty string as NULL where appropriate.
- **IDs:** Preserve CSV id format (e.g. leading zeros) so they match across CSVs and `waha_datasheet_id` / `id` in DB.
- **Idempotency:** Use `INSERT ... ON DUPLICATE KEY UPDATE` for tables with a primary key (factions, detachments, datasheets, stratagems, enhancements, abilities). For link tables without a single PK, either (a) delete all rows then insert, or (b) use a composite unique key and REPLACE/ON DUPLICATE. The full hydrator is designed so one full run replaces the waha_* data with the CSV set (full refresh).
- **Dependencies:** If a CSV is missing, log a warning and skip that step (or fail fast with `--strict`). Optionally support `--tables factions,detachments,datasheets` to run only selected steps.
- **Sync check (future):** Hash the set of CSVs (or a manifest); store in `data/wahapedia/last_sync.json`. Only run the hydrator when the hash changes. See `docs/Scrapers-and-Sync-Design.md`.

---

## 5. Fetcher (future)

- **Current:** No automated fetcher; CSVs are assumed to be exported manually or by a separate process into `data/wahapedia/`.
- **Options:** Browser automation, scrape (respect robots.txt and rate limits), or use an official/community export if available. Fetcher output: same CSV set under `data/wahapedia/` so the hydrator stays unchanged. See “Wahapedia” in `docs/Scrapers-and-Sync-Design.md`.

---

## 6. One-command flow (after implementation)

```powershell
# 1. Obtain source CSVs into data/wahapedia/ (export or copy from your source).
# 2. (Recommended) Run cleaner so Cleaned_CSVs/ is populated — ensures HTML and encoding are stripped before load.
#    Example: python scripts/opr/archive/CleanAll40K3.py  (or point it at data/wahapedia and output to data/wahapedia/Cleaned_CSVs)
# 3. Run full hydration (creates/updates all waha_* from CSVs; prefers Cleaned_CSVs/ when present).
python scripts/wahapedia/hydrate_waha_full.py

# 4. Optionally run extra-column update (legend, role, loadout, etc.).
python scripts/wahapedia/hydrate_waha_datasheets_extra.py
```

Use `.env` for DB (MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE). Optional: `--data-dir path/to/wahapedia`, `--dry-run`, `--verbose`.
