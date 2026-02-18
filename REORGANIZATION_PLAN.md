# WahapediaExport — Reorganization Plan

This document maps the current folder structure, identifies prunable or redundant items, and proposes a cleaner layout. **Review before deleting or moving anything;** adjust the plan to match what you still need.

---

## 1. Current state (summary)

### Top-level folders

| Folder | Purpose (inferred) | Notes |
|--------|--------------------|--------|
| **Wargaming_ERP** | Live app + GitHub repo | **Keep.** Core application (app.py, builders, library_ui, database_utils, newest_hydrator). |
| **MySQLDumps** | DB dumps + README + per-table SQL | **Keep.** Dated dump folders (e.g. WargamingERPSQLDump2.16.26) + schema/routines. Also contains *copies* of app.py, w40k_builder.py, opr_builder.py, database_utils.py — likely snapshot with a dump; **prunable** if you don’t need them. |
| **mmf Data import** | MMF → stl_library | **Keep.** mmf_hydrator.py, mmf_download.json. Check for duplicate `mmf_hydrator` (no extension) — **prune** if it’s a copy. |
| **OPR Data Export** | OPR JSON → DB scripts | **Consolidate.** Many scripts (OPR_JSON_analyzer, various hydrators, Clean*.py, import*.py). Keep the one(s) you actually use; archive or remove the rest. |
| **MySQLDataDump** | Older dump / “40kproxytest” SQL + some CSVs | **Prune or archive.** Different naming (40kproxytest_*.sql); overlaps with MySQLDumps. Either merge into MySQLDumps as an “archive” subfolder or delete after confirming no longer needed. |
| **Source FIles** | Source data (typo in name) | **Keep + rename.** e.g. `Source FIles` → `SourceFiles` or `sources`. Contains Datasheets_wargear.csv and possibly other source files. |
| **Wahapedia CSV** | Wahapedia CSV exports | **Keep or merge.** If it’s just CSVs, consider moving into a single **sources** or **data** area. |
| **Cleaned_CSVs** | Cleaned CSV outputs | **Keep or merge.** Same idea — could live under **data** or **sources**. |
| **__pycache__** | Python bytecode | **Prune.** Add to .gitignore if this repo is ever under git; safe to delete. |

### Loose files at root

- **Excel/CSV (Wahapedia-style):** Abilities.xlsx, Datasheets*.xlsx/csv, Detachments.xlsx, Detachment_abilities.xlsx, Enhancements.xlsx, WahapediaData.csv/xlsx, etc.  
  → **Move** into a single **data** or **sources** folder (e.g. `data/wahapedia/` or `sources/40k/`) so the root isn’t a dumping ground.
- **Access DBs:** Wahapedia Clone1.accdb, Wahapedia Clone11.mdb.accdb  
  → **Archive or prune** if you no longer use Access; otherwise move to **data** or **archive**.
- **Scripts:** army_builder.py, old_backup.py  
  → **Prune** if obsolete; or move to **scripts/archive**.
- **Other:** AI Prompt.txt, opr_special_rules.txt, wargaming_erp_schema_dump.csv  
  → **Decide:** keep as-is, or move to **docs** (prompts, notes) and **data** (schema dump). Schema dump duplicates MySQLDumps content — **prune** or keep one place only.

---

scripts are all acceptable.  ## 1b. Path dependencies — scripts that read local files

**If you move folders or files, these scripts will break until their paths are updated.** The app itself (app.py, w40k_builder, opr_builder, library_ui, database_utils) uses **only MySQL** — no local file paths.

| Script | Path(s) it uses | Breaks if you move … |
|--------|------------------|----------------------|
| **mmf Data import/mmf_hydrator.py** | `…\mmf Data import\mmf_download.json` | The `mmf Data import` folder or `mmf_download.json`. |
| **Wargaming_ERP/newest_hydrator.py** | `…\OPR Data Export\data.json` | The `OPR Data Export` folder or `data.json`. |
| **OPR Data Export/comp_hydrator.py** | `…\OPR Data Export\data.json` | Same. |
| **OPR Data Export/newest_hydrator.py** | `…\OPR Data Export\data.json` | Same. |
| **OPR Data Export/surg_hydrator.py** | `…\OPR Data Export\data.json` | Same. |
| **OPR Data Export/hydrate2.py** | `…\OPR Data Export\data.json` | Same. |
| **OPR Data Export/Hydrate_rules.py** | `…\OPR Data Export\data.json` | Same. |
| **OPR Data Export/robust_dive.py** | `…\OPR Data Export\data.json` | Same. |
| **OPR Data Export/OPR_JSON_analyzer.py** | `…\OPR Data Export\data.json` | Same. |
| **OPR Data Export/OPR_data_importer.py** | `…\OPR Data Export\data.json` | Same. |
| **OPR Data Export/import_json2.py** | `…\OPR Data Export\data.json` | Same. |
| **OPR Data Export/importjson.py** | `…\OPR Data Export\data.json` | Same. |
| **OPR Data Export/import_opr2.py** | `…\OPR Data Export\data.json` | Same. |
| **OPR Data Export/PrettyJson1.py** | `…\OPR Data Export\data.json` and `data_pretty.json` | Same folder or those files. |
| **OPR Data Export/CleanAllPipes.py** | `…\Source Files` and `…\Source Files\Cleaned_CSVs` | The folder named **Source Files** (note: scripts use “Source Files”, not “Source FIles”). |
| **OPR Data Export/CleanAll40K.py** | Same | Same. |
| **OPR Data Export/CleanAll40K2.py** | Same | Same. |
| **OPR Data Export/CleanAll40K3.py** | Same | Same. |
| **OPR Data Export/CleanCSV.py** | Same | Same. |
| **OPR Data Export/CleanDatasheets.py** | `…\WahapediaExport\Datasheets.csv` and `Datasheets_Clean.csv` (root) | Those two files at repo root. |

**Summary:**  
- **Safe to move without code changes:** Wargaming_ERP (app + DB only), MySQLDumps contents, loose xlsx/accdb, `old_backup.py`, `army_builder.py` — they don’t open local data files.  
- **Will break if moved:** `mmf Data import` (and its JSON), `OPR Data Export` (and `data.json` / `data_pretty.json`), the folder the Clean* scripts call **Source Files**, and the root **Datasheets.csv** / **Datasheets_Clean.csv** unless you update the paths in the table above.

**If you do move those folders/files:** update the path constants at the top of each listed script (e.g. `JSON_PATH`, `source_folder`, `FILE_PATH`, `input_path`, `output_path`) to the new locations. You can do that after the move in one pass.

---

## 2. Proposed target structure

```
WahapediaExport/
├── Wargaming_ERP/          # App (unchanged; synced to GitHub)
├── MySQLDumps/             # Dumps only: dated folders + README, schema, routines
│   ├── README.md
│   ├── WargamingERPSQLDump2.16.26/
│   ├── wargaming_erp_routines.sql
│   ├── wargaming_erp_schema_dump.csv
│   └── (per-table SQLs if you still want them)
├── scripts/                 # All import/export/hydration scripts in one place
│   ├── mmf/
│   │   ├── mmf_hydrator.py
│   │   └── (mmf_download.json or symlink; or keep path in script)
│   ├── opr/
│   │   ├── OPR_JSON_analyzer.py   # The one you use
│   │   ├── newest_hydrator.py     # if still used
│   │   └── archive/               # old hydrators, Clean*.py, import*.py
│   └── README.md                 # Short note: what each script does, input/output
├── data/                    # All source/export data (or "sources")
│   ├── wahapedia/           # Wahapedia CSVs, xlsx, cleaned
│   │   ├── (Abilities.xlsx, Datasheets*.xlsx, etc.)
│   │   └── Cleaned_CSVs/    # or merge contents here
│   ├── opr/                 # OPR JSON, pretty-printed, etc.
│   │   └── (data_pretty.json, etc.)
│   └── mmf/                 # Optional: mmf_download.json here if script points to it
├── archive/                 # Old dumps, old DB names, obsolete scripts
│   ├── MySQLDataDump/       # 40kproxytest_*.sql, old CSVs
│   └── (Wahapedia Clone*.accdb, old_backup.py, army_builder.py if pruned)
├── docs/                    # Optional: prompts, notes, one-off references
│   ├── AI Prompt.txt
│   └── opr_special_rules.txt
└── REORGANIZATION_PLAN.md   # This file (can move to docs/ later)
```

**Alternative (minimal change):** Keep **mmf Data import** and **OPR Data Export** as-is, but:
- Rename **Source FIles** → **SourceFiles** or **sources**.
- Create **data/** and move all loose xlsx/csv/accdb into **data/wahapedia/** (and optionally **data/opr/**).
- Move **army_builder.py**, **old_backup.py** to **archive/** or delete.
- Remove **__pycache__**, duplicate **wargaming_erp_schema_dump.csv** at root, and (after confirmation) **MySQLDataDump** or fold it into **MySQLDumps/archive/**.
- In **MySQLDumps**, remove the copy of app/w40k_builder/opr_builder/database_utils if you don’t need that snapshot.

---

## 3. Git branches (Wargaming_ERP)

You mentioned “prunable branches.” Inside **Wargaming_ERP** you have (from earlier):

- **main**
- **40KMMFIntegration**
- **40k-unit-composition** (remote)

After merging what you need:

- Delete local branches you no longer need:  
  `git branch -d 40KMMFIntegration` (or `-D` if not merged).
- Delete remote-tracking branches for removed remotes:  
  `git fetch --prune`  
  and optionally delete remote branch:  
  `git push origin --delete 40k-unit-composition` (only if you’re sure).

---

## 4. Checklist (do in order)

1. **Back up** (or ensure MySQLDumps + Wargaming_ERP are safe).
2. **Prune obviously safe:**  
   - Delete **__pycache__**.  
   - Remove duplicate **wargaming_erp_schema_dump.csv** at root (keep the one in MySQLDumps).
3. **Decide on MySQLDataDump:**  
   - If you don’t need “40kproxytest” dumps, move **MySQLDataDump** to **archive/MySQLDataDump** or delete.
4. **MySQLDumps:**  
   - Remove **app.py**, **w40k_builder.py**, **opr_builder.py**, **database_utils.py** from MySQLDumps unless you want them as a snapshot.
5. **Loose files:**  
   - Create **data** (and optionally **docs**).  
   - Move Wahapedia xlsx/csv and Access DBs into **data/wahapedia/** (or **data/**).  
   - Move **AI Prompt.txt**, **opr_special_rules.txt** to **docs/** if you want them kept.
6. **Scripts:**  
   - **Option A:** Create **scripts/mmf** and **scripts/opr**; move **mmf Data import** contents into **scripts/mmf**; move the OPR scripts you use into **scripts/opr**, rest into **scripts/opr/archive**. Update paths in mmf_hydrator (and any OPR script) to point to **data/** or new script location.  
   - **Option B:** Only rename **Source FIles** → **SourceFiles**, move loose data into **data/**, leave **mmf Data import** and **OPR Data Export** in place but delete or archive redundant scripts inside OPR Data Export.
7. **Rename:** **Source FIles** → **SourceFiles** (or **sources**).
8. **Git:** Merge and then prune local/remote branches in Wargaming_ERP as above.
9. **README / docs:** Update **MySQLDumps/README.md** “Data sources and import/export scripts” table with any new script paths (e.g. **scripts/mmf/mmf_hydrator.py** if you move it).

---

## 5. After reorganization

- Keep **Data sources and import/export scripts** in **MySQLDumps/README.md** in sync with actual script locations.
- Prefer a single **data/** (or **sources/**) tree for all CSV/xlsx/JSON so new exports don’t clutter the root again.
- If you add more import scripts (e.g. direct-from-web), put them under **scripts/** with a short note in the README.

You can tick off items in this plan as you go; adjust folder names and what to archive based on what you still use.
