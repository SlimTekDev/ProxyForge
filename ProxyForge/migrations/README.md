# Database migrations

Run these once against your `wargaming_erp` database when adding new features.

- **add_stl_library_notes_tags.sql** – Adds `notes` (TEXT) and `tags` (VARCHAR 500) to `stl_library` for the Digital Library view. After running, you can add notes and comma-separated tags per STL in the STL Gallery.

  **PowerShell** (from repo root):
  ```powershell
  Get-Content "ProxyForge\migrations\add_stl_library_notes_tags.sql" -Raw | mysql -u hobby_admin -p wargaming_erp
  ```
  Or use `cmd` so `<` works:
  ```powershell
  cmd /c "mysql -u hobby_admin -p wargaming_erp < ProxyForge\migrations\add_stl_library_notes_tags.sql"
  ```

  **Bash / Cmd:**
  ```bash
  mysql -u hobby_admin -p wargaming_erp < ProxyForge/migrations/add_stl_library_notes_tags.sql
  ```
  If you already ran it, you may see "Duplicate column" and can ignore.

- **add_stl_library_mmf_detail.sql** – Adds MMF object detail from the API: `description` (TEXT), `price` (VARCHAR 50), `status` (VARCHAR 50), `has_pdf` (TINYINT). Run the fetcher with **MMF_ENRICH_PREVIEW=1** (or after enrichment) so the JSON has these fields, then run the hydrator. In MySQL Workbench: open the file and execute, or run:
  ```sql
  ALTER TABLE stl_library ADD COLUMN description TEXT NULL;
  ALTER TABLE stl_library ADD COLUMN price VARCHAR(50) NULL;
  ALTER TABLE stl_library ADD COLUMN status VARCHAR(50) NULL;
  ALTER TABLE stl_library ADD COLUMN has_pdf TINYINT(1) NULL;
  ```

- **add_stl_library_kit_metadata.sql** – Digital Library refinements: `size_or_scale`, `kit_type`, `kit_composition`, `is_supported`, `print_technology`, `miniature_rating`, `license_type`, `part_count`, `print_time_estimate`. Used by the STL Gallery for filtering and per-card “Kit & print” editing.

  **PowerShell** (from repo root). If `mysql` is not on your PATH, use the full path to `mysql.exe` (e.g. MySQL Server 8.0):
  ```powershell
  $mysql = "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
  Get-Content "ProxyForge\migrations\add_stl_library_kit_metadata.sql" -Raw | & $mysql -u hobby_admin -p wargaming_erp
  Get-Content "ProxyForge\migrations\add_stl_library_faction_links.sql" -Raw | & $mysql -u hobby_admin -p wargaming_erp
  ```
  Or run each migration separately; replace `$mysql` with your path if different (e.g. MySQL Server 8.4).

- **add_stl_library_faction_links.sql** – New table `stl_library_faction_links` (mmf_id, game_system, faction_key) to associate MMF records with 40K factions or OPR armies for roster-level proxy suggestions and filtering.

- **add_play_armylist_stl_choices.sql** – New table `play_armylist_stl_choices` (entry_id, mmf_id, sort_order) so each roster entry can have multiple STL choices (e.g. kitbashing). Used by "Choose STL for Roster" in the Army Builder unit details. Run with same PowerShell pattern as above (full path to mysql if needed).

- **add_stl_library_images_json.sql** – Adds `images_json` (TEXT) to `stl_library` to store a JSON array of `{url, thumbnailUrl}` per MMF object. Used by the STL Gallery image carousel (Feature #3). **Idempotent:** safe to run multiple times (no-op if column exists). After running, re-run the MMF fetcher with `MMF_ENRICH_IMAGES=1` and the hydrator to populate; the gallery will show Prev/Next when multiple images exist.

  **PowerShell** (from repo root; use full path to `mysql.exe` if not on PATH):
  ```powershell
  Get-Content "ProxyForge\migrations\add_stl_library_images_json.sql" -Raw | & $mysql -u hobby_admin -p wargaming_erp
  ```

- **add_opr_army_detail.sql** – New table `opr_army_detail` (army_name, game_system, background, army_wide_rules, special_rules, aura_rules, spells) for Army Book view. Used to show army lore, army-wide rules, special rules, aura rules and spells on the Army Book page. **Populate automatically:** run the OPR fetcher (`scripts/opr/fetch_opr_json.py`) to generate `data/opr/army_details.json`, then run `scripts/opr/hydrate_opr_army_detail.py` to upsert into this table. Primary key: (army_name, game_system).

  **PowerShell** (from repo root). If `mysql` is not on your PATH, use the full path to `mysql.exe`:
  ```powershell
  $mysql = "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"   # or 8.4, etc.
  Get-Content "ProxyForge\migrations\add_opr_army_detail.sql" -Raw | & $mysql -u hobby_admin -p wargaming_erp
  ```
  Or open and execute the `.sql` file in MySQL Workbench.

- **Cloud post-restore (views and procedures):** After restoring a dump to managed MySQL (e.g. DigitalOcean), all views and procedures with DEFINER are skipped. Run the migrations listed in **docs/Cloud-Post-Restore-Migration-Plan.md** on the cloud DB in the order given. The following files are for that plan (no DEFINER; procedures use SQL SECURITY INVOKER):
  - **create_view_master_picker.sql** – view_master_picker (library picker, faction dropdown). Required.
  - **create_view_40k_enhancement_picker.sql** – view_40k_enhancement_picker. Required.
  - **create_view_40k_army_rules.sql** – view_40k_army_rules. Required.
  - **create_view_40k_army_rule_registry.sql** – view_40k_army_rule_registry. Required.
  - **create_view_40k_stratagems.sql** – view_40k_stratagems. Required.
  - **create_view_opr_master_picker.sql** – view_opr_master_picker. Required.
  - **create_view_opr_unit_rules_detailed.sql** – view_opr_unit_rules_detailed. Required.
  - **create_procedure_AddUnit.sql** – AddUnit procedure (OPR builder calls it). Required.
  - **create_procedure_GetArmyRoster.sql** – GetArmyRoster procedure. Optional.
  - **create_view_list_validation.sql** – view_list_validation (depends on view_40k_datasheet_complete). Optional.
  - **create_view_master_army_command.sql** – view_master_army_command. Optional.
  - **create_view_opr_unit_complete.sql** – view_opr_unit_complete. Optional.
  - **create_view_active_list_options.sql** – view_active_list_options. Optional.
  - **create_view_40k_model_stats.sql** – view_40k_model_stats. Optional.
  - **create_view_master_picker_40k.sql** – view_master_picker_40k. Optional.
  - **create_view_opr_unit_rules_complete.sql** – view_opr_unit_rules_complete. Optional.
  - **create_view_unit_selector.sql** – view_unit_selector. Optional.
  See docs/Streamlit-Cloud-Deploy-Workflow.md §9 and docs/Cloud-Post-Restore-Migration-Plan.md for run order and required vs optional.

- **add_chapter_subfaction_and_validation_view.sql** – Adds `play_armylists.chapter_subfaction` (VARCHAR 100, nullable) and recreates `view_list_validation_40k` so that when a Space Marine list has a selected chapter (e.g. Blood Angels), validation allows that chapter’s units instead of marking them INVALID. Run once. Required for chapter-aware 40K army picker and rules.

- **recreate_view_40k_datasheet_complete_first_model.sql** – Recreates `view_40k_datasheet_complete` so every datasheet with at least one model row appears. The original view required `line_id = 1`; this version uses the first model row per datasheet (MIN(line_id)). Fixes "Unit not found" for units like Boyz. Run once; safe to re-run.

- **recreate_view_40k_unit_composition_with_max.sql** – Recreates `view_40k_unit_composition` with both `min_size` and `max_size`. Uses `CREATE OR REPLACE VIEW` and `SQL SECURITY INVOKER` so you can run it as your DB user (e.g. hobby_admin) without DROP privilege or SYSTEM_USER errors. (parsed from `waha_datasheet_unit_composition.description`). Required for the 40K roster builder “single/double” (Min/Max) unit size toggle. If your view only has `min_size`, run this migration, then the roster editor will show the toggle for units with a size range (e.g. 5–10 models).

- **add_waha_datasheets_extra.sql** – Adds to `waha_datasheets`: `legend`, `role`, `loadout`, `transport`, `damaged_w`, `damaged_description`, `link` (from Wahapedia Datasheets.csv) for the 40K Army Book Reference. Run once; if a column already exists you may see "Duplicate column" for that line (safe to ignore). Then populate by running:
  ```powershell
  python scripts/wahapedia/hydrate_waha_datasheets_extra.py
  ```
  Optional: `--file path/to/Datasheets.csv` (default: `data/wahapedia/Datasheets.csv`). Uses `.env` for DB (MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE).

- **dedupe_waha_abilities_keywords.sql** – Removes duplicate rows from `waha_datasheets_keywords` (one per datasheet_id + keyword) and `waha_datasheets_abilities` (one per datasheet_id + line_id + ability_id). Run after rehydration if you see double entries in unit pickers or army book special rules. Requires MySQL 8.0+ (uses ROW_NUMBER). Same PowerShell pattern as above.

- **add_alpha_events.sql** – Optional. Creates table `alpha_events` (session_id, event_type, page, detail, created_at) for alpha-testing usage logging. Only needed if you set `PROXYFORGE_ALPHA_LOGGING=1` in the deployed app’s environment (e.g. Streamlit Cloud secrets). See `docs/Streamlit-Cloud-Deploy-Workflow.md` and `ProxyForge/alpha_logging.py`.
