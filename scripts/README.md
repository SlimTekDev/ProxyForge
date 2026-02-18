# Scripts

Import/export and hydration scripts for wargaming_erp data. Paths inside scripts may need updating after reorganization (see REORGANIZATION_PLAN.md).

## scripts/mmf
- **fetch_mmf_library.py** — Fetches your MMF library via API; writes `data/mmf/mmf_download.json` and `last_sync.json`. Set `MMF_USERNAME` (and `MMF_API_KEY` if required).
- **mmf_hydrator.py** â€” Imports `data/mmf/mmf_download.json` into `stl_library`. Skips DB write when hash unchanged; use `--force` to run anyway.

## scripts/opr
- **OPR_JSON_analyzer.py** â€” Analyzes OPR community JSON; populates \opr_units\, \opr_unit_upgrades\, etc. Input: \data/opr/data.json\ (update \json_path\ in script).
- **newest_hydrator.py** â€” Hydrates OPR data into DB. Input: \data/opr/data.json\ (update \JSON_PATH\ in script).

## scripts/opr/archive
Legacy hydrators, Clean*.py, import*.py. Update \source_folder\ / \FILE_PATH\ to \data/wahapedia\ or \data/opr\ if you use them.
