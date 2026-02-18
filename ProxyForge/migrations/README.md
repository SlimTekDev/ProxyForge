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
