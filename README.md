# ProxyForge

Army list builders (OPR, 40K), Digital Library (STL gallery + audits), and MMF sync scripts. Curate and link your 3D-printed proxies to game units.

## Quick start

1. **Clone** and set up Python (see `ProxyForge/Requirements.txt` for the Streamlit app).
2. **Secrets:** Copy `.env.example` to `.env` and set at least `MYSQL_PASSWORD` (and `MMF_*` if using MMF scripts). Never commit `.env`. See **SECURITY.md** for all variables.
3. **Database:** Run MySQL migrations under `ProxyForge/migrations/` (see that folder’s README).
4. **App:** From repo root, `streamlit run ProxyForge/app.py` (or run from `ProxyForge`).

## Repo layout

- **ProxyForge/** – Streamlit app (Digital Library, Army Builder), DB connection, migrations.
- **scripts/mmf/** – MMF library fetcher, hydrator, backfill_stl_images.
- **scripts/opr/** – OPR data/import scripts.
- **docs/** – Setup and feature docs.
- **data/** – Local data (e.g. `data/mmf/`); `mmf_download.json` and `last_sync.json` are gitignored.

## Contributing / feedback

If you publish this for community feedback, keep `.env` and any real credentials out of the repo. Use `.env.example` and **SECURITY.md** as the single source of truth for required env vars.
