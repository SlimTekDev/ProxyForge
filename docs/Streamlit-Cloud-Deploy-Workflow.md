# Streamlit Cloud deployment workflow (alpha testing)

This document describes how to host ProxyForge on **Streamlit Community Cloud** for alpha testing, using an **external MySQL** database and **no data files in the repo** (hydrate the DB from your machine).

---

## 1. Overview

| Component | Where it lives |
|-----------|----------------|
| **App code** | GitHub repo (this repo). No `data/` in repo (see .gitignore). |
| **Database** | External MySQL (PlanetScale, DigitalOcean Managed DB, Railway, etc.). |
| **Secrets** | Streamlit Cloud dashboard (MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE). |
| **Data (40K, OPR)** | Either **dump + restore** from your local DB (one-time clone) or **hydrate** from CSVs/JSON into the external DB. See §3 and §3a. |

Testers only need the app URL; they never see credentials or run scripts.

---

## 2. Prerequisites

- GitHub repo (e.g. SlimTekDev/ProxyForge or WahapediaExport) with ProxyForge app in a subfolder.
- A **MySQL 8**-compatible database reachable from the internet (many managed providers allow "public" or "allowed IPs" access).
- Your local copy of the repo with:
  - All migrations applied to your **local** DB (so you can export schema or run them on the new DB).
  - Data files under `data/wahapedia/` and `data/opr/` (for hydration only; not committed).

---

### 2a. DB hosting provider options

You need a **MySQL 8–compatible** database reachable from the internet (Streamlit Cloud and your machine for dump/restore or hydration). Below are practical options; check each provider’s current docs for pricing, free tiers, and restore support.

**Managed MySQL (easiest “just a DB”)**

- **DigitalOcean Managed Database (MySQL)** – Simple setup, standard MySQL, dump/restore works. No free tier; small instance is a few dollars/month. Good default if you want minimal fuss.
- **PlanetScale** – MySQL-compatible (Vitess), often has a free tier. Import is usually via their UI/CLI rather than raw `mysqldump`/`mysql < file`; use migrations + hydrate or their import flow. Fine if you don’t rely on a single dump/restore.
- **AWS RDS (MySQL)** / **Azure Database for MySQL** – Full MySQL, dump/restore works. More setup; use if you already use that cloud.

**App-platform DBs (often include a free or cheap tier)**

- **Railway** – Can provision MySQL; simple, often has a free or low-cost tier. Confirm “restore from dump” in their docs (usually via `mysql` client to the provided host).
- **Render** – Primarily PostgreSQL; if they offer MySQL, same idea: provision DB, get URL, restore if supported.

**Self-hosted (VPS)**

- **DigitalOcean Droplet, Linode, Vultr** – Install MySQL yourself on a small VM. Full control, dump/restore works. You handle backups and upgrades; typically a few dollars/month.

**Before you sign up, confirm:**

- **Public connectivity** (or how to allow Streamlit Cloud to connect).
- **Restore from dump** (if you plan to use §3a): can you run `mysql -h host ... < dump.sql` or equivalent?
- **Connection limits** (Streamlit can open several connections per user).
- **Data size / free-tier limits** (your dump size).

---

## 3. One-time: External database setup

You need an empty database on an external host, then either **migrations + hydrate** (§4) or **dump + restore** (§3a).

1. **Create the database** (e.g. `wargaming_erp`) on your chosen host (PlanetScale, DigitalOcean Managed Database, Railway, AWS RDS, etc.). Create an empty DB and note: host, port (usually 3306), user, password, database name.
2. **Allow access**: Ensure the instance allows connections from the internet (or at least Streamlit Cloud IPs and your own IP for dump/restore or hydration). Many providers use “Public” or “Allow from anywhere” for development.
3. **Populate it** using one of:
   - **Option A – Migrations + hydrate:** Run all migrations on the empty DB (see `ProxyForge/migrations/README.md`), then run the hydration script (§4). Use this if you prefer not to dump your local DB or you’re setting up from a new machine that has the CSVs/JSON.
   - **Option B – Dump and restore:** Dump your **already-hydrated local** DB (structure + data) and restore it into the external DB (§3a). You can **skip the hydration step** for the initial deploy.

---

### 3a. Alternative: Dump and restore (skip hydration)

If your local MySQL already has all the data you want (Wahapedia, OPR, etc.), you can clone it to the external server and skip hydration entirely for the first deploy.

1. **Dump the local database** (structure + data). From your machine, with MySQL client in PATH:
   ```powershell
   mysqldump -u hobby_admin -p --single-transaction --routines wargaming_erp > wargaming_erp_dump.sql
   ```
   (Use your actual local user/password; `--single-transaction` helps for InnoDB. Omit `--routines` if you have no stored procedures.)
2. **Create the empty database** on the external host (via the provider’s UI or CLI).
3. **Restore the dump** into the external DB. How you do this depends on the provider:
   - **PlanetScale:** Does not support direct `mysqldump` import; use their import flow or connect with `mysql` client if they expose it.
   - **DigitalOcean / Railway / AWS RDS / generic MySQL:** From a machine that can reach the external host:
     ```powershell
     mysql -h your-external-host.com -u your_user -p wargaming_erp < wargaming_erp_dump.sql
     ```
   - Some providers have an “Import” or “Restore from file” in the dashboard; upload the dump or run the above from their console.
4. **Verify:** Connect to the external DB and confirm tables and row counts (e.g. `waha_datasheets`, `opr_units`) match expectations.
5. **Streamlit Cloud:** Point the app’s secrets at this external DB (§6). No hydration step needed for initial data.

**When to use dump + restore:** Easiest when you already have a full local DB and just want a one-time (or occasional) clone to the cloud. No need to have CSVs/JSON on hand or run hydrators for the first deploy.

**When to use hydrate instead (or later):** (a) You don’t have a local dump but you have the Wahapedia CSVs and OPR JSON. (b) You get **new** source data (e.g. a fresh Wahapedia export) and want to update the **external** DB without re-dumping from local: run `scripts/run_hydrators_for_cloud.py` with `.env.cloud` pointing at the external DB; that updates the cloud DB in place. So re-hydrating is useful for “push only new 40K/OPR data to the cloud” without doing a full dump/restore again.

**DigitalOcean Managed Database – quick path**

1. In the DigitalOcean control panel: **Databases** → your cluster → **Connection details**. Note: **host** (e.g. `db-mysql-xxx.db.ondigitalocean.com`), **port** (25060 is common for DO Managed MySQL), **user**, **password**, and **database** (default is often `defaultdb`; you can create a DB named `wargaming_erp` in the same cluster).
2. **Trusted sources:** Either **remove all trusted sources** (allow any IP) or add specific IPs:
   - **Allow all:** Remove every entry from Trusted Sources (DigitalOcean then allows all IPs). Do not use 0.0.0.0/0.
   - **Allow only Streamlit Cloud:** Add each of the [Streamlit Community Cloud outbound IPs](https://docs.streamlit.io/deploy/streamlit-community-cloud/status) as separate trusted sources (see list below). These IPs may change without notice; check the docs if connections fail later.
   - **Allow only your PC:** Add your own IP (e.g. 68.184.89.22) for local restore/hydration only; the Streamlit app will not connect unless you also add Streamlit’s IPs or allow all.

   **Streamlit Community Cloud IPs** (as of docs; verify at [Status and limitations](https://docs.streamlit.io/deploy/streamlit-community-cloud/status)):  
   `35.230.127.150`, `35.203.151.101`, `34.19.100.134`, `34.83.176.217`, `35.230.58.211`, `35.203.187.165`, `35.185.209.55`, `34.127.88.74`, `34.127.0.121`, `35.230.78.192`, `35.247.110.67`, `35.197.92.111`, `34.168.247.159`, `35.230.56.30`, `34.127.33.101`, `35.227.190.87`, `35.199.156.97`, `34.82.135.155`.
3. **Create DB (if needed):** In the DO database UI you can add a new database (e.g. `wargaming_erp`). If you only have `defaultdb`, you can restore into that and use it as `MYSQL_DATABASE` in secrets.
4. **Dump local** (from your PC):  
   `mysqldump -u hobby_admin -p --single-transaction wargaming_erp > wargaming_erp_dump.sql`
5. **Restore to DO:**  
   - **If `mysql` is on your PATH** (e.g. MySQL client installed):  
     `mysql -h your-do-host -P 25060 -u doadmin -p --ssl-mode=REQUIRED defaultdb < wargaming_erp_dump.sql`  
     (On PowerShell, use `cmd /c "mysql ... < wargaming_erp_dump.sql"` or pipe: `Get-Content wargaming_erp_dump.sql -Raw | mysql ...`.)  
   - **If `mysql` is not installed or not on PATH:** use the Python restore script (no CLI needed). From repo root, with `.env.cloud` containing the DO credentials:  
     `python scripts/restore_dump_to_db.py`  
     Optional: `--dump path/to/dump.sql` and `--env-file .env.cloud`. The script uses SSL for non-localhost hosts; if certificate verification fails, set `MYSQL_SSL_VERIFY=0` in `.env.cloud`.
6. **Verify:** Connect with the same credentials (e.g. MySQL Workbench or `mysql -h ... -P ... -u ... -p`) and run `SELECT COUNT(*) FROM waha_datasheets;` (or any table) to confirm data.
7. **Streamlit Cloud:** Deploy the app (§6) and set **Secrets** with the DO connection details. The app reads `MYSQL_PORT` (e.g. `25060` for DigitalOcean); add it to secrets so the connector uses the correct port.

**3b. Validate migration integrity (recommended)**

To confirm that no tables, columns, or rows were dropped or corrupted during dump/restore:

1. **Baseline (before or from source DB):** From repo root, capture your **local** DB state to a JSON file (use `.env` for local):
   ```powershell
   python scripts/validate_db_migration.py --env-file .env --baseline migration_baseline.json
   ```
   Optionally add `--checksum` to include per-table checksums (slower; helps detect data corruption).

2. **Compare (after restore to cloud):** Point the script at the **cloud** DB and compare to the baseline (use `.env.cloud` for DigitalOcean):
   ```powershell
   python scripts/validate_db_migration.py --env-file .env.cloud --compare migration_baseline.json
   ```
   The script reports: missing or extra tables, column differences, row-count mismatches, and (if `--checksum` was used) checksum mismatches. If views are missing, it reminds you to run **docs/Cloud-Post-Restore-Migration-Plan.md**.

3. **Report only:** To list tables and row counts for one DB (e.g. cloud) without a baseline:
   ```powershell
   python scripts/validate_db_migration.py --env-file .env.cloud
   ```

The baseline file (`migration_baseline.json`) is in `.gitignore`; do not commit it. See **docs/Commissioning-Checklist.md** for a checkbox in the post-restore flow.

**3c. Populate a new empty cloud database from scratch**

If you created a **new** database on DigitalOcean (e.g. `wargaming_erp`) and it has no tables yet:

1. **Set `.env.cloud`** so it points at that database:
   ```ini
   MYSQL_DATABASE=wargaming_erp
   ```
   (and keep `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD` as before).

2. **Restore the dump** into that database (from repo root, with a dump created from your local DB):
   ```powershell
   python scripts/restore_dump_to_db.py --dump wargaming_erp_dump.sql --env-file .env.cloud
   ```
   If you don’t have a dump yet, create one first:
   ```powershell
   mysqldump -u root -p --single-transaction wargaming_erp | Out-File -FilePath wargaming_erp_dump.sql -Encoding utf8
   ```
   Then run the restore command above.

3. **Recreate views and procedures** (restore skips DEFINER objects):
   ```powershell
   python scripts/run_cloud_migrations.py --env-file .env.cloud --full
   ```

4. **Streamlit Cloud secrets:** Set `MYSQL_DATABASE = "wargaming_erp"` so the app uses this database. Reboot the app if needed.

5. **Verify:**  
   `python scripts/run_sql_cloud.py "SELECT COUNT(*) AS n FROM view_master_picker WHERE game_system = '40K'"`  
   should return a non-zero count.

---

**3d. Run SQL against cloud DB**

You can run SQL against your DigitalOcean (or other cloud) DB in several ways:

1. **Python script (no mysql CLI or Workbench needed)** — From repo root, with `.env.cloud` set with your cloud DB credentials:
   ```powershell
   python scripts/run_sql_cloud.py "SELECT COUNT(*) FROM waha_datasheets"
   python scripts/run_sql_cloud.py "SELECT DISTINCT faction FROM view_master_picker WHERE game_system = '40K'"
   python scripts/run_sql_cloud.py "SHOW TABLES"
   ```
   Use double quotes around the query; for queries with single quotes inside, escape or use `--file path/to/query.sql`.

2. **DigitalOcean control panel** — In the DO dashboard: **Databases** → your cluster → **Connection details**. Some plans offer a **Console** or **Query** tab where you can run SQL in the browser.

3. **MySQL Workbench** — Download [MySQL Workbench](https://dev.mysql.com/downloads/workbench/). New connection: host = your DO host, port = 25060, user = doadmin, password = your password; use SSL (required for DO). Then open a SQL tab and run queries.

4. **mysql CLI** — If you added the MySQL bin folder to PATH (§3 / Cloud-Post-Restore-Migration-Plan):  
   `mysql -h your-do-host -P 25060 -u doadmin -p defaultdb --ssl-mode=REQUIRED`  
   Then type SQL and press Enter.

---

## 4. Hydrate the external DB (from your machine)

Use this if you did **not** use dump+restore (§3a)—e.g. you ran migrations on an empty external DB and need to populate it from CSVs/JSON. Also use this **later** when you have new Wahapedia or OPR data and want to update the external DB in place (no need to re-dump from local).

1. **Create `.env.cloud`** (do not commit). Set DB variables to the **external** DB:
   ```ini
   MYSQL_HOST=your-external-db-host.com
   MYSQL_PORT=3306
   MYSQL_USER=your_user
   MYSQL_PASSWORD=your_password
   MYSQL_DATABASE=wargaming_erp
   ```
2. **Run all hydrators** in one go (from repo root):
   ```powershell
   python scripts/run_hydrators_for_cloud.py
   ```
   This script loads `.env.cloud` and runs, in order: Wahapedia full pipeline, Wahapedia datasheets extra, OPR units (newest_hydrator), OPR army detail. Ensure `data/wahapedia/` and `data/opr/` exist locally with the required CSVs/JSON; use `--skip-opr` or `--skip-40k` if some data is missing.
   Alternatively set `PROXYFORGE_ENV_FILE` to another file (e.g. `.env.remote`) or run the individual hydrators manually with the same env.
3. **Verify**: Connect to the external DB and confirm `waha_*` and OPR tables have rows.

---

## 5. Repo readiness (no data in repo)

- **.gitignore** must exclude large data so the repo stays small:
  - `data/wahapedia/` (or at least the large CSVs and subfolders)
  - `data/opr/*.json` (or equivalent)
  - Keep `data/.gitkeep` or small placeholders if you want the folder structure.
- **Secrets**: Never commit `.env` or any file containing DB passwords (already in .gitignore).
- **App entry**: Streamlit Cloud runs the app from the **ProxyForge** folder; main file is `app.py`. Put a `requirements.txt` (or use `Requirements.txt` if your Cloud app already recognises it) in **ProxyForge** with: streamlit, pandas, mysql-connector-python, python-dotenv. If the build fails on missing deps, add a lowercase `requirements.txt` with the same content.

---

## 6. Deploy on Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
2. **New app**:
   - **Repository**: `your-org/WahapediaExport` (or the repo that contains ProxyForge).
   - **Branch**: `main`.
   - **Main file path**: `ProxyForge/app.py`.
   - **Advanced settings** → **Root directory of your app**: set to `ProxyForge` (so the working directory is the app folder and imports resolve; `.env` is not used—secrets come from the dashboard).
3. **Secrets** (in the app’s “Secrets” / “Settings”):
   ```toml
   MYSQL_HOST = "your-external-db-host.com"
   MYSQL_PORT = "3306"
   MYSQL_USER = "your_user"
   MYSQL_PASSWORD = "your_password"
   MYSQL_DATABASE = "wargaming_erp"
   ```
   Use the port from your provider (e.g. DigitalOcean Managed MySQL often uses `25060`). Add any other keys (e.g. `PROXYFORGE_ALPHA_LOGGING` if you use alpha logging).
4. **Deploy**. The first run may take a few minutes. If the app fails, check the logs in the Streamlit Cloud dashboard (share.streamlit.io → your app → **Manage app** → **Logs**).
5. **Share the app URL** with alpha testers. Live app: **https://proxyforge.streamlit.app** (or the custom URL you set in the dashboard).

---

## 7. After deployment

- **Re-hydrating**: When you get new Wahapedia CSVs or OPR data, run the same hydrators again from your machine with the **external** DB credentials. The live app will then show updated data (no redeploy needed for data-only changes).
- **Code changes**: Push to the connected branch; Streamlit Cloud will redeploy automatically.
- **OPR Army Book Reference**: That page reads `data/opr/data.json` from disk. In the cloud deploy that file is not present, so the page shows a “data file not found” message. That’s expected unless you later add a DB-backed or URL-backed source for OPR army book data.

---

## 8. Optional: Alpha logging and debugging

- **What’s included:** `ProxyForge/alpha_logging.py` is already wired in: when `PROXYFORGE_ALPHA_LOGGING=1`, the app logs **page views** (which nav page) and **feature events** (e.g. `list_created` with detail OPR/40K) to the `alpha_events` table. No PII by default (anonymous session ID, event type, page, short detail).
- **Enable:** (1) Run `ProxyForge/migrations/add_alpha_events.sql` on the external DB. (2) In Streamlit Cloud secrets, add `PROXYFORGE_ALPHA_LOGGING = "1"`.
- **Use:** Query `alpha_events` (e.g. by `event_type`, `page`, `created_at`) to see how testers move through the app and which features they use. Useful for prioritising fixes and understanding drop-off.

---

## 9. Cloud vs local: different behaviour (troubleshooting)

If the cloud app shows fewer sidebar options, empty library picker, or errors that don’t happen locally, the most likely cause is **missing views and procedures** on the cloud DB. During dump/restore we skipped all `CREATE` statements that use `DEFINER=root@localhost` (managed MySQL doesn’t allow it), so **views** and **stored procedures** were not created on the cloud.

**Investigation**

1. **Streamlit Cloud logs**  
   In **Manage app** → **Logs**, look for Python tracebacks (e.g. `Table 'view_master_picker' doesn't exist`, or `view_list_validation_40k`). That tells you which view/table is missing.

2. **Compare views on cloud vs local**  
   On your **local** DB:  
   `SHOW FULL TABLES WHERE Table_type = 'VIEW';`  
   On **DigitalOcean** (same query): run it and compare. Any view that exists locally but not on cloud must be recreated on cloud.

3. **Recreate views and procedures on the cloud DB**  
   Use the **Cloud post-restore migration plan**, which lists **all** skipped views and procedures in dependency order so you can minimize one-off debugging:
   - **Full plan:** **docs/Cloud-Post-Restore-Migration-Plan.md**  
     It includes: required views (view_master_picker, view_list_validation_40k, view_40k_datasheet_complete, view_40k_unit_composition, view_40k_enhancement_picker, view_40k_army_rules, view_40k_army_rule_registry, view_40k_stratagems, view_opr_master_picker, view_opr_unit_rules_detailed), optional views for full parity, and procedures **AddUnit** (required by OPR builder) and **GetArmyRoster**.
   - **Minimum (required only):** Run the “One-shot required only” list in that doc (11 migration files in order).  
   - **Full parity:** Run the full “Run order” list (all 20 items) so cloud matches local.

   Run the chosen migrations **on the DigitalOcean database** (e.g. MySQL Workbench or `mysql -h ... -P 25060 -u doadmin -p defaultdb`). Use the same method as for other migrations (e.g. `Get-Content ProxyForge\migrations\create_view_master_picker.sql -Raw | mysql -h YOUR_DO_HOST -P 25060 -u doadmin -p defaultdb`, or run each file in MySQL Workbench).

4. **Other differences**  
   - **OPR Army Book Reference** reads `data/opr/data.json` from disk; that file is not in the cloud repo, so that page will show “data file not found” or similar unless you add a DB-backed source later.  
   - **Code** should be the same if you deploy from the same branch; if the sidebar shows different options, confirm the app is deploying from `main` and the latest commit.

After recreating the views and procedures on the cloud DB, reload the Streamlit app (no redeploy needed). The library picker, faction dropdown, 40K/OPR builders, validation, enhancements, and OPR “Add unit” flow should work.

**Streamlit Cloud troubleshooting checklist (in order)**

| Step | What to do |
|------|------------|
| **A. Deploy / code** | [share.streamlit.io](https://share.streamlit.io) → your app → **Manage app** → **Settings**. Confirm **Branch** is `main` (or the branch you push to). Push latest code to that branch; Streamlit redeploys automatically. If the cloud app shows only “Army Builder” and “Digital Library” instead of all 5 nav options, the deployed code is likely old — trigger **Reboot app** or push a small commit to force redeploy. |
| **B. Cloud DB has data** | From repo root, run: `python scripts/run_sql_cloud.py "SELECT COUNT(*) AS n FROM view_master_picker WHERE game_system = '40K'"` and `python scripts/run_sql_cloud.py "SELECT DISTINCT faction FROM view_master_picker WHERE game_system = '40K'"`. If the count is 0 or your faction (e.g. Orks) is missing, the cloud DB has no 40K data — restore a dump or run hydrators with `.env.cloud` (see §4). |
| **C. Views exist** | `python scripts/run_sql_cloud.py "SHOW FULL TABLES WHERE Table_type = 'VIEW'"`. You should see view_master_picker, view_list_validation_40k, etc. If not, run **docs/Cloud-Post-Restore-Migration-Plan.md** (or `python scripts/run_cloud_migrations.py --env-file .env.cloud --full`). |
| **D. Logs** | **Manage app** → **Logs**. Look for tracebacks (e.g. “table doesn’t exist”, “column not found”). That pinpoints the failing query or view. |

**If logs show "inotify instance limit reached" (Errno 24) or "inotify watch limit reached" (Errno 28):** Streamlit's file watcher hits the container's inotify limit. Disable it by adding `ProxyForge/.streamlit/config.toml` with `[server]` and `fileWatcherType = "none"`. Commit and push; the app will run without file watching (no auto-reload on code change, which is fine for cloud).

**If roster/list names show "ΓÇÖ" instead of an apostrophe** (e.g. "GorkΓÇÖs Grin"): the DB stores UTF-8 but the connection wasn't using it. The app sets `charset='utf8mb4'` and `collation='utf8mb4_unicode_ci'` in `database_utils.py`; after pulling that change and redeploying, apostrophes should display correctly.

**If the build fails with "Invalid requirement" or "Couldn't parse requirement" for requirements.txt** (e.g. `s\\x00t\\x00r\\x00e...` in the error): the file is saved as **UTF-16**. Re-save `ProxyForge/requirements.txt` as UTF-8 (no BOM), commit and push, then **Reboot app**.

**If you suspect commits never made it to GitHub** (e.g. cloud app looks like an old wargaming_erp-era build):

1. **Check local git:** From repo root run `git status` and `git log -3 --oneline`. If you have uncommitted changes, commit them. If your branch is ahead of origin, your pushes may have failed.
2. **Push explicitly:** `git push origin main` (or your branch). Fix any errors (auth, branch name, remote).
3. **Confirm on GitHub:** Open the repo on GitHub in the browser. Open `ProxyForge/app.py` and check the Navigation radio: it should list all 5 options (OPR Army Builder, 40K Army Builder, OPR Army Book Reference, 40K Army Book Reference, Digital Library). If GitHub shows only 2 options, the right code was never pushed.
4. **Force Streamlit to use latest:** In Streamlit Cloud → your app → **Manage app** → **Reboot app**. Or push an empty commit: `git commit --allow-empty -m "Trigger redeploy"` then `git push origin main`.

**App still old after push — wrong repo or wrong path**

If you pushed the latest code (e.g. commit f25b353) and GitHub shows the correct `ProxyForge/app.py` (5 nav options) but the live app still shows the old UI (e.g. only “Army Builder” and “Digital Library”), Streamlit is likely deploying from the **wrong repo** or the **wrong file path**.

1. **Push first** (if you haven’t): `git push origin main`.
2. **Streamlit Cloud → your app → Manage app → Settings.** Check:
   - **Repository:** Must be the repo you just pushed to (e.g. `YourGitHubUser/WahapediaExport`). If it still says `wargaming_erp` or a different repo name, the app is building from that repo — change it to the repo that contains the current ProxyForge code (the one with `ProxyForge/app.py` and 5 nav options), or create a **new** app and connect it to the correct repo.
   - **Branch:** `main` (or the branch you push to).
   - **Main file path:** Must be `ProxyForge/app.py`. If it is `app.py` (repo root) or `wargaming_erp/app.py`, Streamlit is running an old or different app — set it to `ProxyForge/app.py`.
   - **Advanced → Root directory of your app:** Set to `ProxyForge` so the working directory is the app folder (imports and `requirements.txt` resolve correctly).
3. **Save** and **Reboot app**. Wait for the build to finish; the sidebar should then show all 5 options (OPR Army Builder, 40K Army Builder, OPR Army Book Reference, 40K Army Book Reference, Digital Library).

**If the cloud DB has no 40K data** (e.g. `SELECT COUNT(*) FROM view_master_picker WHERE game_system = '40K'` returns 0):

- **Cause:** The cloud database has empty `waha_datasheets` / `waha_factions` (or they were never restored). Views exist but return no rows.
- **Fix:** Populate the cloud DB with 40K (and OPR) data using one of:
  1. **Full dump + restore from local:** On your PC, dump the local DB (which has the data):  
     `mysqldump -u your_user -p --single-transaction wargaming_erp > wargaming_erp_dump.sql`  
     Then restore to the cloud DB using **scripts/restore_dump_to_db.py** with `--env-file .env.cloud`. After restore, run **scripts/run_cloud_migrations.py --env-file .env.cloud --full** again (restore skips views/procedures with DEFINER).
  2. **Hydrate from CSVs/JSON:** If you have `data/wahapedia/` and `data/opr/` locally, run **scripts/run_hydrators_for_cloud.py** so that hydrators use `.env.cloud` and populate the cloud DB’s `waha_*` and OPR tables. See §4.

After the cloud DB has data, reload the app; the 40K library picker and faction list should work.

---

## 10. Commissioning checklist

Before inviting testers, run through **docs/Commissioning-Checklist.md** in full. It covers: external DB and migrations, hydration, repo readiness, Streamlit Cloud deploy steps, then a **feature-by-feature checklist** (OPR builder, 40K builder including chapter/custom and wargear options, Army Book refs, Digital Library, export, validation, optional alpha logging). Use it again after major code or data updates.
