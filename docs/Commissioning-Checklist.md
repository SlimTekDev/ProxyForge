# ProxyForge commissioning checklist (alpha / Streamlit Cloud)

Use this checklist before inviting alpha testers and after major code or data updates. It verifies operational integrity of the **deployed app** and the **hydration workflow** that feeds it.

---

## Part A: Pre-deploy (one-time or when changing DB)

### A1. External database

- [ ] MySQL 8–compatible database created (PlanetScale, DigitalOcean, Railway, etc.).
- [ ] Connection details noted: host, port (3306), user, password, database name.
- [ ] Network access allowed from Streamlit Cloud (and from your IP if you hydrate from your machine).

### A2. Schema (migrations)

If you **restored from a dump** (§3a), the external DB already has the full schema—skip this. Otherwise run each migration in `ProxyForge/migrations/` in the order listed in `ProxyForge/migrations/README.md` against the **external** DB. At minimum:

- [ ] Core tables (play_armylists, play_armylist_entries, waha_*, opr_*, view_master_picker, etc.). If you exported schema from your local DB, ensure all views and tables exist.
- [ ] `add_chapter_subfaction_and_validation_view.sql` (40K chapter/subfaction and validation).
- [ ] `add_waha_datasheets_extra.sql` (40K Army Book legend, loadout, transport).
- [ ] `add_opr_army_detail.sql` (OPR Army Book).
- [ ] `add_alpha_events.sql` (only if you will enable alpha logging).

### A3. Populate the external DB

**Option A – Dump and restore (simplest if you have a full local DB):**

- [ ] Dump local DB:  
  `mysqldump -u your_user -p --single-transaction wargaming_erp > wargaming_erp_dump.sql`
- [ ] **(Optional but recommended)** Capture baseline for migration validation:  
  `python scripts/validate_db_migration.py --env-file .env --baseline migration_baseline.json`  
  (Add `--checksum` for per-table checksums to detect data corruption.)
- [ ] Create empty DB on external host, then restore:  
  `mysql -h external-host -u user -p wargaming_erp < wargaming_erp_dump.sql`  
  (Or use `python scripts/restore_dump_to_db.py --env-file .env.cloud` if no mysql CLI.)
- [ ] Confirm tables and row counts (e.g. `waha_datasheets`, `opr_units`).
- [ ] **(Optional but recommended)** Validate migration integrity:  
  `python scripts/validate_db_migration.py --env-file .env.cloud --compare migration_baseline.json`  
  Fix any missing tables/columns/row-count diffs; if views are missing, run **docs/Cloud-Post-Restore-Migration-Plan.md**.  
  **You can skip A3 Option B** for the initial deploy.

**Option B – Hydrate (if you did not dump; or for later updates from new CSVs/JSON):**

- [ ] Create `.env.cloud` (do not commit) with `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE` pointing at the external DB.
- [ ] Run:  
  `python scripts/run_hydrators_for_cloud.py`  
  (with `data/wahapedia/` and `data/opr/` present locally; use `--skip-opr` or `--skip-40k` if needed).
- [ ] Confirm 40K and OPR tables have rows.

### A4. Repo and Streamlit Cloud config

- [ ] `.gitignore` excludes `data/wahapedia/`, `data/opr/*.json`, `.env`, `.env.cloud`.
- [ ] Placeholders exist if needed: `data/opr/.gitkeep`, `data/wahapedia/.gitkeep`.
- [ ] `ProxyForge/Requirements.txt` (or `requirements.txt`) lists: streamlit, pandas, mysql-connector-python, python-dotenv.

---

## Part B: Deploy on Streamlit Community Cloud

- [ ] Signed in at [share.streamlit.io](https://share.streamlit.io) with GitHub.
- [ ] **New app** → Repository: your repo (e.g. SlimTekDev/ProxyForge); Branch: `main`.
- [ ] **Main file path:** `ProxyForge/app.py`.
- [ ] **Advanced** → **Root directory:** `ProxyForge` (so imports and working directory are correct).
- [ ] **Secrets** (TOML) set:
  - `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`
  - Optional: `PROXYFORGE_ALPHA_LOGGING = "1"` if using alpha logging and `alpha_events` exists.
- [ ] Deploy; wait for first build. Note app URL (e.g. `https://proxyforge.streamlit.app`).

---

## Part C: Post-deploy smoke test (in the browser)

Open the app URL (e.g. https://proxyforge.streamlit.app). If any step fails, fix before inviting testers.

### C1. App loads

- [ ] Sidebar shows “ProxyForge” and navigation: OPR Army Builder, 40K Army Builder, OPR Army Book Reference, 40K Army Book Reference, Digital Library.
- [ ] No “System Error” or connection error in the main area.

### C2. OPR Army Builder

- [ ] **Create list:** Sidebar “Create New List” → enter name, select game mode, primary army, points → Save. New list appears in “Active Roster”.
- [ ] **Add units:** “Add from Library” shows factions/units; search works; add at least one unit to the roster.
- [ ] **Roster:** Roster table shows added unit(s) with points.
- [ ] **View unit:** Click 👁️ (or unit) and unit details open (no crash).
- [ ] **Export (if present):** Any export/download button works.

### C3. 40K Army Builder

- [ ] **Create list:** “Create New List” → name, primary army (e.g. Space Marines), points → Save. List appears.
- [ ] **Detachment:** “Select Detachment” shows options and persists selection.
- [ ] **Chapter (Space Marines):** If primary army is Space Marines, “Select Chapter” shows Generic / All, chapter list, and “Custom (mix chapters)”. Selecting a chapter filters the library; “Custom (mix chapters)” shows all faction units.
- [ ] **Add units:** Search and add at least one unit (e.g. Intercessor Squad, Rhino). Roster updates.
- [ ] **Unit details:** Click 👁️ on a roster unit → Unit details dialog opens; **Stats**, **Rules (Abilities)**, **Loadout / Wargear** tabs work; abilities show plain text (no raw HTML); transport section shows if applicable.
- [ ] **Wargear options:** For a unit with options (e.g. “This model can be equipped with 1 hunter-killer missile”), the option is selectable (0/1) and no “Unsupported option type” appears.
- [ ] **Validation:** Sidebar shows list validation (e.g. Battle-Ready or chapter mismatch); with “Custom (mix chapters)” or Proxy Mode, mixed chapters are allowed.
- [ ] **Export:** “Export list (txt)” and “Export for BattleScribe (.ros.xml)” download correctly.

### C4. OPR Army Book Reference

- [ ] Page loads; army selector and unit/rule content appear (or a clear “data not available” if OPR army detail was not hydrated).

### C5. 40K Army Book Reference

- [ ] Page loads; faction/detachment and datasheet content load from DB (no crash).

### C6. Digital Library

- [ ] Page loads. If STL library is empty, a “no data” or empty state is acceptable; if you have MMF data in the DB, gallery/list should display.

---

## Sharing for alpha testing

After Part C passes, you can share the app URL with alpha testers.

- [ ] **Access:** Anyone with the link can use the app (no login). Do not expose secrets or credentials in the UI or in shared text.
- [ ] **Tell testers:**
  - [ ] Alpha disclaimer: app is in alpha; feedback on broken flows, confusing UI, and what they tried to do is valuable.
  - [ ] First load can be slow (Streamlit cold start; ask them to wait or refresh once if stuck).
  - [ ] OPR Army Book Reference tab will show "data file not found" in the cloud deploy (expected).
  - [ ] Digital Library shows content only if the cloud DB has STL/linking data.
- [ ] **Optional:** Enable alpha logging (Part D) to inspect usage (page views, list creation) without PII.
- [ ] **Example one-liner:** *"ProxyForge alpha: build 40K and OPR lists, add units from the library, and export. Link: [your URL]. First load can be slow; OPR Army Book tab may say data file not found. Feedback welcome."*

---

## Part D: Alpha logging (optional)

If you enabled `PROXYFORGE_ALPHA_LOGGING=1` and created `alpha_events`:

- [ ] Use the app (change pages, create a list, add a unit).
- [ ] In the external DB, run:  
  `SELECT * FROM alpha_events ORDER BY created_at DESC LIMIT 10;`  
- [ ] Rows appear with `event_type`, `page`, `session_id`, `created_at` (no PII by default).

---

## Part E: Re-hydration and ongoing

- [ ] When you have new Wahapedia CSVs or OPR data: run `python scripts/run_hydrators_for_cloud.py` (with `.env.cloud` pointing at the external DB). No redeploy needed for data-only updates.
- [ ] After code changes: push to the connected branch; Streamlit Cloud redeploys. Re-run this checklist (at least Part C) after major changes.

---

## Quick reference: Hydration command

```powershell
# From repo root; .env.cloud has remote DB credentials
python scripts/run_hydrators_for_cloud.py
```

See **docs/Streamlit-Cloud-Deploy-Workflow.md** for full workflow and troubleshooting.
