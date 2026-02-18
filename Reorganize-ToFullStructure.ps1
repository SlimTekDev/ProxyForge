# Reorganize WahapediaExport to full target structure (see REORGANIZATION_PLAN.md)
# Run from: PowerShell (as needed, run Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass)
# Prerequisite: Back up the folder (e.g. .zip) before running.

$ErrorActionPreference = "Stop"
$root = "C:\Users\slimm\Desktop\WahapediaExport"

if (-not (Test-Path $root)) {
    Write-Error "Root not found: $root"
}

Write-Host "Root: $root" -ForegroundColor Cyan
Write-Host "Creating folder structure..." -ForegroundColor Yellow

# --- 1. Create new directories ---
$dirs = @(
    "$root\scripts",
    "$root\scripts\mmf",
    "$root\scripts\opr",
    "$root\scripts\opr\archive",
    "$root\data",
    "$root\data\wahapedia",
    "$root\data\wahapedia\Cleaned_CSVs",
    "$root\data\opr",
    "$root\data\mmf",
    "$root\archive",
    "$root\archive\MySQLDumps_snapshot_scripts",
    "$root\docs"
)
foreach ($d in $dirs) {
    if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d -Force | Out-Null }
    Write-Host "  $d"
}

# --- 2. scripts/mmf: move mmf Data import contents ---
$mmfSrc = "$root\mmf Data import"
if (Test-Path $mmfSrc) {
    Write-Host "`nMoving mmf Data import -> scripts\mmf..." -ForegroundColor Yellow
    Get-ChildItem -Path $mmfSrc -File -ErrorAction SilentlyContinue | ForEach-Object {
        Move-Item -LiteralPath $_.FullName -Destination "$root\scripts\mmf\" -Force
        Write-Host "  moved $($_.Name)"
    }
}

# --- 3. scripts/opr: primary OPR scripts; rest to archive; data files to data/opr ---
$oprSrc = "$root\OPR Data Export"
if (Test-Path $oprSrc) {
    Write-Host "`nMoving OPR Data Export -> scripts\opr and scripts\opr\archive, data\opr..." -ForegroundColor Yellow
    $oprPrimary = @("OPR_JSON_analyzer.py", "newest_hydrator.py")
    $oprDataFiles = @("data.json", "data_pretty.json", "data.csv", "OPRArmyForgeData.xlsx")
    Get-ChildItem -Path $oprSrc -File -ErrorAction SilentlyContinue | ForEach-Object {
        if ($oprPrimary -contains $_.Name) {
            Move-Item -LiteralPath $_.FullName -Destination "$root\scripts\opr\" -Force
            Write-Host "  -> scripts\opr\ $($_.Name)"
        } elseif ($oprDataFiles -contains $_.Name) {
            Move-Item -LiteralPath $_.FullName -Destination "$root\data\opr\" -Force
            Write-Host "  -> data\opr\ $($_.Name)"
        } else {
            Move-Item -LiteralPath $_.FullName -Destination "$root\scripts\opr\archive\" -Force
            Write-Host "  -> scripts\opr\archive\ $($_.Name)"
        }
    }
}

# --- 4. data/wahapedia: root xlsx/csv + Source FIles + Source Files + Cleaned_CSVs + Wahapedia CSV ---
Write-Host "`nMoving Wahapedia/root data -> data\wahapedia..." -ForegroundColor Yellow
$wahapediaExt = @(".xlsx", ".csv")
Get-ChildItem -Path $root -File -ErrorAction SilentlyContinue | Where-Object {
    $_.Extension -in $wahapediaExt -and $_.Name -notmatch "^wargaming_erp_schema" -and $_.Name -notlike "Reorganize*"
} | ForEach-Object {
    Move-Item -LiteralPath $_.FullName -Destination "$root\data\wahapedia\" -Force
    Write-Host "  $($_.Name) -> data\wahapedia\"
}

$sourceFolders = @("$root\Source FIles", "$root\Source Files")
foreach ($sf in $sourceFolders) {
    if (Test-Path $sf) {
        Get-ChildItem -Path $sf -File -ErrorAction SilentlyContinue | ForEach-Object {
            Move-Item -LiteralPath $_.FullName -Destination "$root\data\wahapedia\" -Force
            Write-Host "  $sf\$($_.Name) -> data\wahapedia\"
        }
    }
}

$cleanedSrc = "$root\Cleaned_CSVs"
if (Test-Path $cleanedSrc) {
    Get-ChildItem -Path $cleanedSrc -File -ErrorAction SilentlyContinue | ForEach-Object {
        Move-Item -LiteralPath $_.FullName -Destination "$root\data\wahapedia\Cleaned_CSVs\" -Force
        Write-Host "  Cleaned_CSVs\$($_.Name) -> data\wahapedia\Cleaned_CSVs\"
    }
}

$wahapediaCsv = "$root\Wahapedia CSV"
if (Test-Path $wahapediaCsv) {
    Get-ChildItem -Path $wahapediaCsv -File -ErrorAction SilentlyContinue | ForEach-Object {
        Move-Item -LiteralPath $_.FullName -Destination "$root\data\wahapedia\" -Force
        Write-Host "  Wahapedia CSV\$($_.Name) -> data\wahapedia\"
    }
}

# --- 5. archive: MySQLDataDump, Access DBs, old scripts ---
Write-Host "`nMoving archive items..." -ForegroundColor Yellow
if (Test-Path "$root\MySQLDataDump") {
    Move-Item -LiteralPath "$root\MySQLDataDump" -Destination "$root\archive\MySQLDataDump" -Force
    Write-Host "  MySQLDataDump -> archive\"
}
foreach ($acc in @("Wahapedia Clone1.accdb", "Wahapedia Clone11.mdb.accdb")) {
    $p = Join-Path $root $acc
    if (Test-Path $p) {
        Move-Item -LiteralPath $p -Destination "$root\archive\" -Force
        Write-Host "  $acc -> archive\"
    }
}
foreach ($py in @("old_backup.py", "army_builder.py")) {
    $p = Join-Path $root $py
    if (Test-Path $p) {
        Move-Item -LiteralPath $p -Destination "$root\archive\" -Force
        Write-Host "  $py -> archive\"
    }
}

# --- 6. docs: prompts and notes ---
Write-Host "`nMoving docs..." -ForegroundColor Yellow
foreach ($f in @("AI Prompt.txt", "opr_special_rules.txt")) {
    $p = Join-Path $root $f
    if (Test-Path $p) {
        Move-Item -LiteralPath $p -Destination "$root\docs\" -Force
        Write-Host "  $f -> docs\"
    }
}

# --- 7. MySQLDumps: remove snapshot .py copies (move to archive) ---
Write-Host "`nMoving MySQLDumps snapshot scripts -> archive\MySQLDumps_snapshot_scripts..." -ForegroundColor Yellow
foreach ($py in @("app.py", "w40k_builder.py", "opr_builder.py", "database_utils.py")) {
    $p = Join-Path $root "MySQLDumps\$py"
    if (Test-Path $p) {
        Move-Item -LiteralPath $p -Destination "$root\archive\MySQLDumps_snapshot_scripts\" -Force
        Write-Host "  MySQLDumps\$py -> archive\MySQLDumps_snapshot_scripts\"
    }
}

# --- 8. Prune: __pycache__, duplicate schema dump at root ---
Write-Host "`nPruning..." -ForegroundColor Yellow
$pycache = "$root\__pycache__"
if (Test-Path $pycache) {
    Remove-Item -LiteralPath $pycache -Recurse -Force
    Write-Host "  removed __pycache__"
}
$dupSchema = Join-Path $root "wargaming_erp_schema_dump.csv"
if (Test-Path $dupSchema) {
    Remove-Item -LiteralPath $dupSchema -Force
    Write-Host "  removed root wargaming_erp_schema_dump.csv (duplicate of MySQLDumps)"
}

# --- 9. Remove empty source folders ---
Write-Host "`nRemoving empty folders..." -ForegroundColor Yellow
$toRemove = @(
    "$root\mmf Data import",
    "$root\OPR Data Export",
    "$root\Source FIles",
    "$root\Source Files",
    "$root\Cleaned_CSVs",
    "$root\Wahapedia CSV"
)
foreach ($d in $toRemove) {
    if (Test-Path $d) {
        $left = Get-ChildItem -LiteralPath $d -Recurse -File -ErrorAction SilentlyContinue
        if (-not $left) {
            Remove-Item -LiteralPath $d -Recurse -Force
            Write-Host "  removed $d"
        } else {
            Write-Host "  (kept $d - not empty)"
        }
    }
}

# --- 10. scripts/README.md ---
$scriptsReadme = @"
# Scripts

Import/export and hydration scripts for wargaming_erp data. Paths inside scripts may need updating after reorganization (see REORGANIZATION_PLAN.md).

## scripts/mmf
- **mmf_hydrator.py** — Imports MyMiniFactory export JSON into \`stl_library\`. Input: \`mmf_download.json\` (update \`JSON_PATH\` if you moved it to \`data/mmf/\`).

## scripts/opr
- **OPR_JSON_analyzer.py** — Analyzes OPR community JSON; populates \`opr_units\`, \`opr_unit_upgrades\`, etc. Input: \`data/opr/data.json\` (update \`json_path\` in script).
- **newest_hydrator.py** — Hydrates OPR data into DB. Input: \`data/opr/data.json\` (update \`JSON_PATH\` in script).

## scripts/opr/archive
Legacy hydrators, Clean*.py, import*.py. Update \`source_folder\` / \`FILE_PATH\` to \`data/wahapedia\` or \`data/opr\` if you use them.
"@
Set-Content -Path "$root\scripts\README.md" -Value $scriptsReadme -Encoding UTF8
Write-Host "`nCreated scripts\README.md" -ForegroundColor Green

Write-Host "`nDone. Update path constants in scripts (see REORGANIZATION_PLAN.md section 1b) if you use them." -ForegroundColor Cyan
