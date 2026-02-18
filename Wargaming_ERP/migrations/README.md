# Database migrations

Run these once against your `wargaming_erp` database when adding new features.

- **add_stl_library_notes_tags.sql** – Adds `notes` (TEXT) and `tags` (VARCHAR 500) to `stl_library` for the Digital Library view. After running, you can add notes and comma-separated tags per STL in the STL Gallery.

  **PowerShell** (from repo root):
  ```powershell
  Get-Content "Wargaming_ERP\migrations\add_stl_library_notes_tags.sql" -Raw | mysql -u hobby_admin -p wargaming_erp
  ```
  Or use `cmd` so `<` works:
  ```powershell
  cmd /c "mysql -u hobby_admin -p wargaming_erp < Wargaming_ERP\migrations\add_stl_library_notes_tags.sql"
  ```

  **Bash / Cmd:**
  ```bash
  mysql -u hobby_admin -p wargaming_erp < Wargaming_ERP/migrations/add_stl_library_notes_tags.sql
  ```
  If you already ran it, you may see "Duplicate column" and can ignore.

- **add_stl_library_mmf_detail.sql** – Adds MMF object detail from the API: `description` (TEXT), `price` (VARCHAR 50), `status` (VARCHAR 50), `has_pdf` (TINYINT). Run the fetcher with **MMF_ENRICH_PREVIEW=1** (or after enrichment) so the JSON has these fields, then run the hydrator. In MySQL Workbench: open the file and execute, or run:
  ```sql
  ALTER TABLE stl_library ADD COLUMN description TEXT NULL;
  ALTER TABLE stl_library ADD COLUMN price VARCHAR(50) NULL;
  ALTER TABLE stl_library ADD COLUMN status VARCHAR(50) NULL;
  ALTER TABLE stl_library ADD COLUMN has_pdf TINYINT(1) NULL;
  ```
