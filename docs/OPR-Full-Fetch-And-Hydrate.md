# OPR full clean fetch and hydrate

One-time **fetch** writes to repo files; **hydrate** pushes that data into a database. Use the same fetch output for both local and cloud.

---

## Design philosophy (adopted)

All army books and lists are kept consistent with these rules:

- **Canonical game system slugs** — We use fixed slugs (e.g. `grimdark-future`, `age-of-fantasy`, `age-of-fantasy-skirmish`) and never rely on the API’s raw slug. The fetcher always receives an explicit `gameSystem` number (2–6) and applies `GAME_SYSTEM_TO_SLUG` so e.g. Age of Fantasy (4) is always `age-of-fantasy`, never `age-of-fantasy-regiments`.
- **Single source list** — `army_forge_armies.json` is the source of truth. It includes every army we support (including Firefight copies for each Grimdark Future army, except Titan Lords). The unified list (`army_forge_armies_unified.json`) is derived from it and is what we pass to the fetcher.
- **No 404s in the list** — Entries that 404 (e.g. Titan Lords Firefight, Silver Moon Daughters Firefight) are removed from the source list so we don’t refetch them.
- **Real army names** — Placeholder `"TBD"` names are replaced with the army name returned by the last successful fetch (`army_details.json`).
- **Source label** — Every entry has a `"source"` field: `"official"` (OPR Official tab on [Army Forge](https://army-forge.onepagerules.com/armyBookSelection?gameSystem=2)) or `"creator"` (Creators/Community). The list is built from `data/opr/official_army_ids.txt` (allowlist from `scripts/opr/build_official_army_ids.py`). The app uses it to show Official vs Creator in the army dropdown.

The steps below include **list hygiene** (pre- and post-fetch) so that after a full run, all army books and the source list meet this design.

---

## 1. List hygiene (pre-fetch)

Run from repo root so the source list is complete and consistent before fetching:

```powershell
# Ensure source list has all unified armies (Blood Prime + Firefight copies; skips Titan Lords)
python scripts/opr/append_armies_from_unified.py

# Build official allowlist from curated names (run once or when OPR add new official books)
python scripts/opr/build_official_army_ids.py
# Apply source: official = in official_army_ids.txt, else creator
python scripts/opr/ensure_army_sources.py

# Build unified list from source (used by fetcher)
# Important: run this after any edit to army_forge_armies.json (e.g. adding creator armies for AOFS/GFF)
python scripts/opr/build_unified_army_list.py
```

---

## 2. Fetch

From repo root (after step 1):

```powershell
# Fetch all armies from Army Forge API -> data/opr/data.json + army_details.json
# Uses unified list so every book gets canonical game system slug (2–6 -> slugs)
python scripts/opr/fetch_opr_json.py --armies data/opr/army_forge_armies_unified.json
```

---

## 3. List hygiene (post-fetch)

Keeps the source list aligned with the design: real names, no 404s, unified list in sync.

```powershell
# Replace TBD names from army_details.json and remove 404 (armyId, gameSystem) entries
python scripts/opr/update_army_list_names_and_remove_404s.py

# If you added new armies or changed creator_army_ids.txt, re-run so every entry has source
python scripts/opr/ensure_army_sources.py

# Rebuild unified list so next fetch uses the updated source list
python scripts/opr/build_unified_army_list.py
```

---

## 4. Optional: clean OPR tables (before hydrate)

To remove all OPR unit and army-detail rows before re-hydrating (so removed armies don’t stay in the DB):

**Local DB** (e.g. MySQL on this machine). Run the migration file so child tables are cleared first (avoids FK errors):

```powershell
# From repo root (adjust mysql path if needed):
Get-Content "ProxyForge\migrations\clean_opr_tables.sql" -Raw | mysql -u hobby_admin -p wargaming_erp

# Or with full path to mysql:
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u hobby_admin -p wargaming_erp < ProxyForge\migrations\clean_opr_tables.sql
```

**Cloud DB** (use `run_sql_cloud.py` with the clean script):

```powershell
python scripts/run_sql_cloud.py --env-file .env.cloud --file ProxyForge/migrations/clean_opr_tables.sql
```

---

## 5. Hydrate local DB

Uses `.env` (local MySQL). From repo root:

```powershell
# OPR units (data/opr/data.json -> opr_units)
python ProxyForge/newest_hydrator.py

# OPR army detail (data/opr/army_details.json -> opr_army_detail)
python scripts/opr/hydrate_opr_army_detail.py
```

If you cleaned local OPR tables in step 4, these repopulate from the same `data.json` and `army_details.json`.

---

## 6. Hydrate cloud DB

Uses `.env.cloud` (or `PROXYFORGE_ENV_FILE`). From repo root:

```powershell
# OPR only (skips 40K Wahapedia hydrators)
python scripts/run_hydrators_for_cloud.py --skip-40k
```

That runs `ProxyForge/newest_hydrator.py` and `scripts/opr/hydrate_opr_army_detail.py` with the env from `.env.cloud`, so the cloud DB gets the same OPR data.

To use a different env file:

```powershell
$env:PROXYFORGE_ENV_FILE = ".env.remote"
python scripts/run_hydrators_for_cloud.py --skip-40k
# or
python scripts/run_hydrators_for_cloud.py --env-file .env.remote --skip-40k
```

If you cleaned cloud OPR tables first (step 4 with cloud), then this step repopulates them.

**If you get "Can't connect to MySQL server" (e.g. 10060 timeout):**  
- **DigitalOcean** managed MySQL uses port **25060** for public connections. In `.env.cloud` set `MYSQL_PORT=25060`.  
- In the DB cluster’s **Trusted Sources**, add your current IP (or allow all for testing).  
- The hydrators use SSL and the port from `.env.cloud` when the host is not localhost.

---

## Troubleshooting: AOFS / GFF creator armies not in dropdown

The Primary Army dropdown only shows factions that exist in `opr_units` (from the last fetch + hydrate). If **creator** armies for Age of Fantasy Skirmish or Grimdark Future Firefight are missing:

1. **Rebuild the unified list** after any change to `army_forge_armies.json` so creator entries are included in the fetch:
   ```powershell
   python scripts/opr/build_unified_army_list.py
   ```
2. **Run fetch** with the unified list. Watch stderr for `FAILED` lines; each shows `armyId` and `gameSystem`. If creator books 404, those armies will not appear until the API accepts them (or you remove stale IDs from the source list).
3. **Clean OPR tables, then hydrate** so the DB is repopulated from the current `data.json` and `army_details.json`.

---

## Quick copy-paste summary

**Full run (design philosophy + fetch + post-fetch hygiene + hydrate local):**

```powershell
cd C:\Users\slimm\Desktop\WahapediaExport
# 1. Pre-fetch list hygiene
python scripts/opr/append_armies_from_unified.py
python scripts/opr/ensure_army_sources.py
python scripts/opr/build_unified_army_list.py
# 2. Fetch
python scripts/opr/fetch_opr_json.py --armies data/opr/army_forge_armies_unified.json
# 3. Post-fetch list hygiene
python scripts/opr/update_army_list_names_and_remove_404s.py
python scripts/opr/ensure_army_sources.py
python scripts/opr/build_unified_army_list.py
# 4. Clean local OPR tables (optional; use migration so child tables cleared first)
Get-Content "ProxyForge\migrations\clean_opr_tables.sql" -Raw | mysql -u hobby_admin -p wargaming_erp
# 5. Hydrate local
python ProxyForge/newest_hydrator.py
python scripts/opr/hydrate_opr_army_detail.py
```

**Hydrate cloud only (after fetch; uses same data/opr/*.json):**

```powershell
cd C:\Users\slimm\Desktop\WahapediaExport
# Optional: clean cloud OPR tables first
python scripts/run_sql_cloud.py --env-file .env.cloud --file ProxyForge/migrations/clean_opr_tables.sql
python scripts/run_hydrators_for_cloud.py --skip-40k
```
