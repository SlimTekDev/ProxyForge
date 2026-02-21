# Cloud post-restore migration plan (views and procedures)

After restoring a mysqldump to a managed MySQL (e.g. DigitalOcean), all `CREATE VIEW ... DEFINER=...` and `CREATE PROCEDURE ... DEFINER=...` statements are skipped because the provider does not allow DEFINER. This document lists **every** view and stored procedure that must be recreated on the cloud DB, in **dependency order**, so you can run them once and avoid one-off feature debugging.

All migration files live under **ProxyForge/migrations/** and use **no DEFINER** (and procedures use `SQL SECURITY INVOKER`) so they work on managed MySQL.

---

## Run order (dependency-safe)

Run the following **on the cloud database** (e.g. DigitalOcean) in this order. Use MySQL Workbench, `mysql` CLI, or the commands below.

**CLI (from repo root)** — replace `YOUR_DO_HOST`, `25060`, `doadmin`, `defaultdb` with your cloud DB host, port, user, and database. Use `-p` and type the password when prompted.

**Single file (PowerShell):** If `mysql` is not on PATH, add it once (e.g. `$env:Path = "C:\Program Files\MySQL\MySQL Server 8.0\bin;" + $env:Path`) or add that folder in Windows **Environment Variables** → **Path**.
```powershell
Get-Content "ProxyForge\migrations\create_view_master_picker.sql" -Raw | mysql -h YOUR_DO_HOST -P 25060 -u doadmin -p defaultdb
```

**Single file (cmd / bash):**
```bash
mysql -h YOUR_DO_HOST -P 25060 -u doadmin -p defaultdb < ProxyForge/migrations/create_view_master_picker.sql
```

**Required-only migrations (all 11 in order, PowerShell)** — use `$dbHost` (PowerShell reserves `$host`). If `mysql` is not on your PATH, use the Python script below instead.
```powershell
$dbHost = "YOUR_DO_HOST"; $port = "25060"; $user = "doadmin"; $db = "defaultdb"
$files = @(
  "ProxyForge\migrations\create_view_master_picker.sql",
  "ProxyForge\migrations\recreate_view_40k_datasheet_complete_first_model.sql",
  "ProxyForge\migrations\recreate_view_40k_unit_composition_with_max.sql",
  "ProxyForge\migrations\add_chapter_subfaction_and_validation_view.sql",
  "ProxyForge\migrations\create_view_40k_enhancement_picker.sql",
  "ProxyForge\migrations\create_view_40k_army_rules.sql",
  "ProxyForge\migrations\create_view_40k_army_rule_registry.sql",
  "ProxyForge\migrations\create_view_40k_stratagems.sql",
  "ProxyForge\migrations\create_view_opr_master_picker.sql",
  "ProxyForge\migrations\create_view_opr_unit_rules_detailed.sql",
  "ProxyForge\migrations\create_procedure_AddUnit.sql"
)
foreach ($f in $files) { Get-Content $f -Raw | mysql -h $dbHost -P $port -u $user -p $db }
```

**No MySQL CLI? Use Python (from repo root):**
```powershell
python scripts/run_cloud_migrations.py --env-file .env.cloud
```
Runs the 11 required-only migration files in order using mysql-connector-python (same credentials as restore). See `python scripts/run_cloud_migrations.py --help`.

**Required-only (bash, one line per file):**
```bash
H=YOUR_DO_HOST P=25060 U=doadmin D=defaultdb
for f in create_view_master_picker recreate_view_40k_datasheet_complete_first_model recreate_view_40k_unit_composition_with_max add_chapter_subfaction_and_validation_view create_view_40k_enhancement_picker create_view_40k_army_rules create_view_40k_army_rule_registry create_view_40k_stratagems create_view_opr_master_picker create_view_opr_unit_rules_detailed create_procedure_AddUnit; do
  mysql -h $H -P $P -u $U -p $D < "ProxyForge/migrations/${f}.sql"
done
```

### 1. Views (no view-to-view dependencies in this block)

Run these in any order among themselves (they depend only on base tables):

| Order | View | Migration file | Required by app? |
|-------|------|----------------|------------------|
| 1 | view_master_picker | create_view_master_picker.sql | **Yes** – library picker, faction dropdown (app.py, w40k_builder, w40k_army_book_ui) |
| 2 | view_40k_datasheet_complete | recreate_view_40k_datasheet_complete_first_model.sql | **Yes** – unit details (w40k_builder, w40k_army_book_ui, w40k_roster) |
| 3 | view_40k_unit_composition | recreate_view_40k_unit_composition_with_max.sql | **Yes** – min/max unit size (w40k_builder, w40k_roster) |
| 4 | view_list_validation_40k | add_chapter_subfaction_and_validation_view.sql | **Yes** – 40K list validation (w40k_builder, w40k_roster). File also adds `chapter_subfaction` column if missing. |
| 5 | view_40k_enhancement_picker | create_view_40k_enhancement_picker.sql | **Yes** – enhancement picker (w40k_builder) |
| 6 | view_40k_army_rules | create_view_40k_army_rules.sql | **Yes** – army & detachment rules (w40k_builder) |
| 7 | view_40k_army_rule_registry | create_view_40k_army_rule_registry.sql | **Yes** – army rule display (w40k_builder) |
| 8 | view_40k_stratagems | create_view_40k_stratagems.sql | **Yes** – stratagem cheat sheet (w40k_builder) |
| 9 | view_opr_master_picker | create_view_opr_master_picker.sql | **Yes** – OPR unit details (opr_builder) |
| 10 | view_opr_unit_rules_detailed | create_view_opr_unit_rules_detailed.sql | **Yes** – OPR rules display (opr_builder) |
| 11 | view_40k_model_stats | create_view_40k_model_stats.sql | Optional |
| 12 | view_master_picker_40k | create_view_master_picker_40k.sql | Optional |
| 13 | view_opr_unit_complete | create_view_opr_unit_complete.sql | Optional |
| 14 | view_opr_unit_rules_complete | create_view_opr_unit_rules_complete.sql | Optional |
| 15 | view_unit_selector | create_view_unit_selector.sql | Optional |
| 16 | view_active_list_options | create_view_active_list_options.sql | Optional |

### 2. Views that depend on other views

Run **after** the views above (they reference view_40k_datasheet_complete or base tables that might be used by procedures):

| Order | View | Migration file | Depends on |
|-------|------|----------------|------------|
| 17 | view_list_validation | create_view_list_validation.sql | view_40k_datasheet_complete |
| 18 | view_master_army_command | create_view_master_army_command.sql | (inv_* tables; optional if you don’t use inventory) |

### 3. Stored procedures

Run **after** view_40k_unit_composition (GetArmyRoster uses it):

| Order | Procedure | Migration file | Required by app? |
|-------|-----------|----------------|------------------|
| 19 | AddUnit | create_procedure_AddUnit.sql | **Yes** – opr_builder calls `cursor.callproc('AddUnit', ...)` |
| 20 | GetArmyRoster | create_procedure_GetArmyRoster.sql | Optional (app may use Python get_roster_40k instead) |

---

## One-shot “required only” (minimum for app to work)

If you only want the app to behave like local (library picker, 40K/OPR builders, validation, enhancements, rules, stratagems, OPR unit details), run **in this order**:

1. create_view_master_picker.sql  
2. recreate_view_40k_datasheet_complete_first_model.sql  
3. recreate_view_40k_unit_composition_with_max.sql  
4. add_chapter_subfaction_and_validation_view.sql  
5. create_view_40k_enhancement_picker.sql  
6. create_view_40k_army_rules.sql  
7. create_view_40k_army_rule_registry.sql  
8. create_view_40k_stratagems.sql  
9. create_view_opr_master_picker.sql  
10. create_view_opr_unit_rules_detailed.sql  
11. create_procedure_AddUnit.sql  

---

## Full parity (all skipped views and procedures)

To match local DB exactly (including optional views and GetArmyRoster), run **all** files in the “Run order” tables above: 1–16 first, then 17–18, then 19–20.

---

## Verification

After running the migrations:

- **Views:**  
  `SHOW FULL TABLES WHERE Table_type = 'VIEW';`  
  Compare with your local DB; you should see the same view names (e.g. view_master_picker, view_list_validation_40k, view_40k_enhancement_picker, view_opr_master_picker, etc.).

- **Procedures:**  
  `SHOW PROCEDURE STATUS WHERE Db = 'defaultdb';` (or your DB name)  
  You should see AddUnit and GetArmyRoster.

Then reload the Streamlit app (no redeploy needed). Library picker, faction dropdown, 40K/OPR builders, validation, enhancements, army/detachment rules, stratagems, and OPR unit details should all work.
