# Scrapers and sync design — automated data refresh

**Goal:** Replace the manual “export → move file → run hydrator” workflow with scrapers that build JSON into your `data/` tree, plus a **sync check** so the database is only updated when a source has actually changed.

---

## 1. High-level flow

```
[Source: Wahapedia / OPR / MMF]
        ↓
   Scraper or API client  →  writes JSON to data/<source>/
        ↓
   Sync check: compare new payload to “last known good” (hash, date, or version)
        ↓
   If changed: run existing hydrator → update DB
   If unchanged: skip DB write, optionally log “no update”
```

- **Scrapers** are separate from your current hydrators: they only produce JSON (and optionally a small **manifest** with version/date/hash).
- **Hydrators** stay as they are (mmf_hydrator, OPR_JSON_analyzer / newest_hydrator, and any future Wahapedia importer); they read JSON and write to MySQL.
- A **sync orchestrator** (one script or a small runner) runs scrapers, does the sync check, and only invokes hydrators when needed. It can run on a schedule (Task Scheduler, cron) or on demand.

---

## 2. Per-source snapshot

### OPR (One Page Rules)

- **Current:** You use community JSON (e.g. `data.json`) and OPR_JSON_analyzer / newest_hydrator.
- **Scraping vs API:** OPR often publishes data as JSON (e.g. from their app or community repos). Prefer **fetching a known JSON URL** over scraping HTML.
- **Sync check options:**
  - If the JSON URL returns **Last-Modified** or **ETag**, use that: store `last_etag` or `last_modified` per source; only download and re-hydrate when the header changes.
  - If the URL is static (same file always), use a **content hash** (e.g. SHA-256 of the response body): store `last_hash`; if new fetch has a different hash, run the hydrator.
  - If the community publishes a **version file** or **changelog**, use that as the “version” and only pull full JSON when the version changes.
- **Output:** Scraper writes to `data/opr/data.json` (and optionally `data/opr/manifest.json` with `{ "fetched_at": "ISO8601", "hash": "sha256..." }`). Orchestrator compares manifest to previous run; if changed, runs OPR hydrator.

### MyMiniFactory (MMF)

- **Current:** **fetch_mmf_library.py** pulls your library via MMF API v2 (`GET /users/{username}/objects`); **mmf_hydrator.py** reads `data/mmf/mmf_download.json` and upserts into `stl_library`. See **docs/MMF-Fetcher-Setup.md** for setup and auth.
- **Scraping vs API:** MMF has an **API**; the fetcher uses it and builds the same JSON shape the hydrator expects (`id`, `name`, `creator.name`, `previewUrl`, `url`).
- **Sync check options:**
  - Store **last run timestamp** and ask the API for “objects updated since &lt;timestamp&gt;” if supported.
  - Or store **last known list of object IDs + updated_at**; only re-hydrate when the set or an updated_at changes.
  - Or **hash of the full JSON** you would send to the hydrator: if unchanged, skip DB update.
- **Output:** Scraper/API client writes `data/mmf/mmf_download.json` (and optionally `data/mmf/manifest.json`). Orchestrator runs mmf_hydrator only when manifest or content changed.

### Wahapedia (40K)

- **Current:** Manual export or separate scripts; you have xlsx/csv and `waha_*` tables.
- **Scraping vs API:** Wahapedia is a fan site; there may be **no official API**. Options:
  - **Scrape** (respect robots.txt and rate limits; check ToS).
  - Use **existing exports** if they publish data dumps or you have a semi-automated export (e.g. browser automation that exports and saves to `data/wahapedia/`).
- **Sync check:** Same idea: **hash of exported data** or **Last-Modified** of the page/list you use as the “source of truth”. Only run the 40K importer when something changed.
- **Output:** Scraper (or export step) writes to `data/wahapedia/` in a consistent shape (e.g. one JSON per entity type, or one big export). A Wahapedia-specific hydrator (or existing pipeline) reads that and updates `waha_*` tables. Orchestrator only runs it when sync check says “changed”.

---

## 3. Sync-check implementation options

| Method | Pros | Cons |
|--------|------|------|
| **ETag / Last-Modified** | No need to download full body to decide | Only works if the server sends these headers (OPR URL might; MMF API might). |
| **Content hash (SHA-256)** | Works for any source; no server support needed | You must download the full payload before deciding (OK for JSON; avoid for huge blobs). |
| **Version file** | Very cheap: one small request to see “version” | Only if the source publishes a version (e.g. OPR might have a “data version” somewhere). |
| **Timestamp + incremental API** | Efficient for APIs that support “updated since” | Only for sources that support it (e.g. MMF). |

**Practical combo:** Use **content hash** of the JSON file you’re about to feed to the hydrator. Store, per source, a small state file (e.g. `data/opr/last_sync.json` with `{ "hash": "...", "at": "ISO8601" }`). After the scraper writes new JSON, compute hash; if it equals `last_sync.hash`, skip hydrator; otherwise run hydrator and update `last_sync.json`.

---

## 4. Suggested folder and script layout

```
data/
  opr/
    data.json           # produced by OPR scraper/fetcher
    manifest.json       # optional: fetched_at, hash, source_url
    last_sync.json      # hash + at from last successful DB update
  mmf/
    mmf_download.json   # produced by MMF API client
    last_sync.json
  wahapedia/
    (export or scraped JSON)
    last_sync.json

scripts/
  opr/
    fetch_opr_json.py   # fetches OPR JSON → data/opr/data.json
  mmf/
    fetch_mmf_library.py # API → data/mmf/mmf_download.json
  wahapedia/
    fetch_wahapedia.py  # scrape or export → data/wahapedia/...
  sync_orchestrator.py  # runs fetchers, sync check, then hydrators
```

- **Fetchers/scrapers** only write to `data/<source>/`.
- **sync_orchestrator.py** (or equivalent):
  1. Runs each fetcher (or skips if “fetch on demand” only).
  2. For each source, reads new JSON (or manifest), computes hash (or uses ETag/version).
  3. Compares to `last_sync.json`; if changed, runs the corresponding hydrator and updates `last_sync.json`.
  4. Logs what was updated and what was skipped.

---

## 5. Implementation order

1. **Sync check only (no new scrapers)**  
   Add `last_sync.json` + hash comparison to your **existing** flow: before running a hydrator, hash the JSON it would read; if same as last time, skip. This gives you “update only when changed” with zero new sources.

2. **OPR**  
   Replace manual download with a small script that fetches the known OPR JSON URL (or list of URLs), writes to `data/opr/data.json`, then run existing OPR hydrator (and sync check). Easiest win if the URL is stable.

3. **MMF**  
   Check MMF’s API docs; build a small client that writes `data/mmf/mmf_download.json` in the shape mmf_hydrator expects. Add sync check (hash or “updated since” if API supports it).

4. **Wahapedia**  
   Hardest (ToS, structure, no API). Option A: automate the export you already do (e.g. “run this export, save to data/wahapedia/”). Option B: build a careful scraper (rate limits, caching, respect robots.txt). In both cases, add sync check (hash of export) so DB only updates when data changed.

5. **Orchestrator**  
   One script that runs all fetchers, then for each source does sync check and conditionally runs the right hydrator. Run it on a schedule or from a “Refresh all data” button in a small admin UI.

---

## 6. Legal and etiquette

- **Terms of service:** Check each site’s ToS and API terms (MMF, Wahapedia, any OPR host). Prefer official APIs and documented feeds.
- **Rate limiting:** Throttle requests (e.g. 1–2 per second); use caching and “only when changed” so you don’t hit servers unnecessarily.
- **robots.txt:** If scraping, respect robots.txt and use a clear User-Agent (e.g. “WargamingERP-Sync/1.0”).

---

## 7. References

- **Data sources table:** MySQLDumps README, “Data sources and import/export scripts”.
- **Current hydrators:** `scripts/mmf/mmf_hydrator.py`, `scripts/opr/OPR_JSON_analyzer.py`, `scripts/opr/newest_hydrator.py`; Wahapedia pipeline (when you add it) will read from `data/wahapedia/`.

When you add a fetcher or change the flow, update this doc and the MySQLDumps README table so “how to refresh data” stays in one place.
