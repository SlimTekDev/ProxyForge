# Security and environment setup

This document describes how to keep secrets out of the repo and set up your environment safely for local use or when sharing code (e.g. publishing on GitHub).

## Do not commit

- **`.env`** – Copy from `.env.example` and fill in your values. `.env` is in `.gitignore`; never add it to version control.
- **Database passwords, API keys, session cookies** – Use environment variables or `.env` only.
- **`data/mmf/mmf_download.json`** and **`data/mmf/last_sync.json`** – Ignored by default; they can contain your library data and sync state.

## Environment variables

All sensitive configuration is read from the environment (or from `.env` if you use `python-dotenv`).

| Variable | Used by | Description |
|----------|---------|-------------|
| `MYSQL_HOST` | App, hydrators, backfill | MySQL host (default: localhost / 127.0.0.1) |
| `MYSQL_USER` | App, hydrators, backfill | MySQL user |
| `MYSQL_PASSWORD` | App, hydrators, backfill | MySQL password (no default; set in `.env`) |
| `MYSQL_DATABASE` | App, hydrators, backfill | Database name (default: wargaming_erp) |
| `MMF_USERNAME` | MMF fetcher | Your MyMiniFactory username |
| `MMF_API_KEY` | MMF fetcher, backfill | OAuth2 access token (from get_mmf_token.py) |
| `MMF_SESSION_COOKIE` | MMF fetcher, backfill | Full Cookie header from browser (alternative to API key) |

Optional: `OPR_DATA_JSON` (path to OPR export JSON for newest_hydrator), `MMF_ENRICH_*`, etc. See `.env.example`.

## Quick setup for a clean clone

1. Copy the example file:  
   `cp .env.example .env` (or on Windows: `copy .env.example .env`)
2. Edit `.env` and set at least `MYSQL_PASSWORD`, and for MMF scripts: `MMF_USERNAME` and one of `MMF_API_KEY` or `MMF_SESSION_COOKIE`.
3. Optional: `pip install python-dotenv` so the app and scripts load `.env` automatically from the repo root.
4. Run the app or scripts as usual; they read from the environment.

## Legacy / archive scripts

Scripts under **archive/** and **scripts/opr/archive/** may still contain old hardcoded DB credentials. Do not run them in production without updating them to use environment variables (see active scripts for examples).

## Reporting security issues

If you find a security vulnerability in this project, please report it responsibly (e.g. via a private channel or GitHub Security Advisories if applicable) rather than opening a public issue.
