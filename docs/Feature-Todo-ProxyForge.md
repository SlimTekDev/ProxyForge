# Feature Todo & Feasibility — ProxyForge

A living list of features and options for the project, with brief feasibility notes. Use this to prioritize and plan.

---

## Priorities & roadmap

| When | Items | Notes |
|------|--------|------|
| **Sooner** | **#1, #4, #7, #11** | OPR data updates; link manager refinements; auto hydrators/scrapers; GW retail data (third-party or manual). |
| **Done** | **#3** | Image gallery per MMF unit (images_json, carousel, backfill script). |
| **Dropped** | **#2** | MMF link slash after `.com` — resolved earlier. |
| **Bookmarked** | **#6** | Direct download from app; vision: users log in to MMF (and other sources) for DL options. |
| **2.0 release** | **#8, #9, #10** | User login; hosting/public access; security. Vision: users add MMF object IDs to fetch/hydrate, associate game units and roster units with MMF files, crowdsource proxy suggestions, heat map / rating data for proxy suggestions. |
| **Later** | **#15** | Slicer integration — more research; definitely a later feature. |

---

## 1. Get updated OPR data

**Feasibility: High**

- **Current:** OPR data is loaded from community JSON (e.g. `data/opr/data.json`) via `OPR_JSON_analyzer.py` / `newest_hydrator.py`. Source is often Army Forge or community repos.
- **Options:** (1) Fetch latest JSON from a known URL (e.g. OPR or community GitHub) on a schedule or on demand. (2) Use Army Forge if they expose a public data URL. (3) Manual “download → replace file → run hydrator” until an auto-fetcher exists.
- **Sync design:** See `docs/Scrapers-and-Sync-Design.md`. Use content hash or `Last-Modified`/ETag to only re-hydrate when data actually changed.

*Note: “Kano” may have been a typo or autocorrect; if it refers to a specific source (e.g. a person or tool), add that source here.*

---

## 2. ~~Get MMF links resolving (needs a `/` after `.com`)~~ **DROPPED — resolved earlier**

*(Previously: ensure one slash between `.com` and path when building MMF URLs. Fix was applied.)*

---

## 3. ~~Figure out if entire image list for each unit is available and can be flipped through for each MMF unit~~ **DONE**

**Implemented**

- **DB:** `stl_library.images_json` (TEXT) stores a JSON array of `{url, thumbnailUrl}` per object. Migration: `ProxyForge/migrations/add_stl_library_images_json.sql` (idempotent).
- **Fetcher:** Extracts images from MMF full object (including `original.url` shape); `MMF_ENRICH_IMAGES=1` enriches all items with full image lists. Hydrator writes `images_json` when the column exists.
- **Backfill:** `scripts/mmf/backfill_stl_images.py` updates `images_json` for all (or missing) records from the API without re-fetching the full library.
- **UI:** Digital Library STL Gallery shows a **Gallery** label and, when multiple images exist, a carousel (◀ / ▶, “Image N / M”) on each card; single image or preview fallback otherwise. Bottom pagination strip added.
- **Docs:** `docs/MMF-Fetcher-Setup.md` and `ProxyForge/migrations/README.md` updated.

---

## 4. Refine link manager for MMF to units

**Feasibility: High**

- **Current:** Link Manager ties `stl_library` (MMF) to units via `stl_unit_links` (mmf_id, unit_id, game_system, is_default). OPR Audit and 40K builder use this.
- **Refinements (from README):** Visual confirmation (thumbnail in table), “Filter by army” / “Show only units with no links”, broken link detection (STL removed or unit ID changed), bulk actions (Unlink All, Set designer default per squad). All are UI/UX and query work; no new external APIs.

---

## 5. Add MMF file options from roster / tags (unit–proxy picker)

**Feasibility: Medium–High**

- **Scope:** A tool that surfaces **MMF file options** for the user to add or associate, drawn from:
  - **(a)** MMF records that are **already linked** to units that appear in the current army roster (e.g. “STLs linked to these roster units”).
  - **(b)** MMF records that **share tags** with the roster’s units — by game system (OPR or 40K) — so users can discover and attach proxy STLs by tag overlap (e.g. “Ork”, “Infantry”, faction slug).
- **Implementation:** New view or tab: “Proxy options for this roster”. Query `stl_unit_links` + `stl_library` for (a); for (b), match roster unit tags (or faction/type) to `stl_library.tags` (or a tag table). Let user pick MMF records to link to roster units. Fits current schema; main work is UI and tag-matching logic.

---

## 6. Add download buttons for MMF library — **BOOKMARKED**

**Feasibility: Medium (auth-dependent)**

- **Current:** “Download” in the STL Gallery opens the MMF object page; user downloads there. True “direct download” (file stream) from the app is bookmarked.
- **Vision:** App eventually allows users to **log in to MMF** (and whatever other sources are needed) so that in-app download options (e.g. “Download” button that streams the file) can use the user’s own auth. Direct download would use MMF API `GET /objects/{object_id}/files` and `GET /files/{file_id}` with the user’s session/API key. See **ProxyForge/README.md** → Bookmarked (Digital Library).

---

## 7. Build auto hydrators/scrapers for MMF, Army Forge, Wahapedia

**Feasibility: High (design); Medium (Wahapedia)**

- **Design:** `docs/Scrapers-and-Sync-Design.md` already describes scrapers producing JSON + optional manifest, sync check (hash/ETag), and hydrators running only when data changed.
- **MMF:** Fetcher is the “scraper”; add a small runner that runs fetcher → sync check → hydrator. Can be scheduled (Task Scheduler, cron, or GitHub Actions).
- **Army Forge / OPR:** Prefer fetching a known JSON URL; sync check by hash or Last-Modified; run existing OPR hydrator when changed.
- **Wahapedia:** No official API; scraping or using exports. Respect robots.txt and ToS; consider rate limits and stability. Easiest: semi-automated export to `data/wahapedia/` then hash-triggered hydrator.

---

## 8. Build user sign up and permissions — **2.0**

**Feasibility: Medium**

- **Planned for 2.0.** Users log in; can add MMF object IDs to be fetched and hydrated into the DB; associate game units and army roster units with MMF files. Long-term: **crowdsource proxy suggestions** and **heat map / rating data** for finding and rating proxy suggestions (community-driven “this STL is a good proxy for this unit”).
- **Current:** Streamlit app is typically single-user or shared without auth. Options when ready: Streamlit + OAuth, reverse proxy auth, or backend (Flask/FastAPI) with user table and roles; BaaS (Supabase, Firebase) for auth. Scope (single household vs multi-tenant) drives the choice.

---

## 9. Figure out hosting and front-end access to public — **2.0**

**Feasibility: Medium**

- **Planned for 2.0** alongside #8 and #10. Options: Streamlit Community Cloud, VPS/cloud VM (Streamlit + MySQL), Docker, or static front + API. Public access implies HTTPS, env-based config, and user auth.

---

## 10. Security features / settings — **2.0**

**Feasibility: High (incremental)**

- **Planned for 2.0.** (1) No secrets in repo; `.env` or platform secrets. (2) DB over SSL if hosted. (3) HTTPS only. (4) User auth (see #8). (5) Input validation and parameterized queries (already in place). (6) Rate limiting if public. (7) “Security / settings” page for toggles (require login, session timeout). Long-term: secure storage of user-linked MMF credentials for download and fetch.

---

## 11. Build scraper for Games Workshop website for pulling GW retail data

**Feasibility: Medium–Low (legal and technical)**

- **Reality:** GW does not offer a public retail API. Direct scraping of gw.com may violate ToS. Retailers get pricelists via trade channels, not public scrape.
- **Alternatives:** (1) Use third-party APIs that aggregate retailer/GW pricing (e.g. Retailed.io, price comparison sites), possibly paid. (2) Manual or semi-manual entry of “GW RRP” for comparison. (3) If you have authorized access (e.g. retailer), use their official feeds instead of scraping the public site.

---

## 12. One-button download: roster → select MMF proxies → download files

**Feasibility: Medium**

- **Scope:** (1) User **builds or imports** an army roster. (2) User **selects MMF records** to use as proxies for each unit (from linked STLs or from the unit–proxy picker in #5). (3) User clicks **one button** to start downloading the files from those MMF pages (STLs / supported formats).
- **Flow:** Roster in app → “Choose proxies” (per unit) → “Download all” → app uses MMF file API (see #6) to fetch file list per object and stream or redirect to downloads. Requires user MMF auth (or stored session) and possibly a background job for many files. Depends on direct-download (#6) for in-app file delivery; until then, could generate a “download list” (links to MMF object pages) or open each object page in sequence.

---

## 13. New Recruit game data + extra game systems (D&D, Frostgrave, etc.)

**Feasibility: Worth checking**

- **Vision:** (1) **Download game data from New Recruit** and use it for army builder info, **cross compatibility** (e.g. import/export lists), and as a **source to feed hydrators**. (2) Use that (and similar sources) to **add support for extra game systems** so the **MMF file association scheme** can cover more than 40K/OPR: e.g. **D&D / Pathfinder**, **Frostgrave / Stargrave / Rangers of Shadow Deep**, and other smaller wargames / tabletop games for “populating forces” (unit ↔ STL links, roster building).
- **New Recruit:** Check if they expose **game data** (datasheets, points, rules) in bulk—not just roster exports—so it can feed hydrators. If yes, design a hydrator and extend `view_master_picker` (or equivalent) and unit tables per game system. If they only expose roster exports, that still helps “import list from New Recruit” and cross compatibility.
- **Extra systems:** Schema and UI already support multiple `game_system` values (e.g. 40K_10E, grimdark-future). Adding D&D/Pathfinder, Frostgrave/Stargrave/Rangers, etc. means: new or shared unit/force tables, game-specific hydrators, and MMF links keyed by game_system + unit (or “force slot”). New Recruit (or other data packs) could be the feed for those systems.

---

## 14. Update process: fetchers, hydrators, hash checks, update on login

**Feasibility: High**

- **Answer:** **Fetchers and hydrators** are the update mechanism. Goal: make the process **more automated** — **hash checks** and **update options on login** (or on app start / scheduled run).
- **Data updates:** See #7 (auto hydrators/scrapers). Fetchers write JSON to `data/<source>/`; sync check (content hash or ETag/Last-Modified) decides whether to run hydrators; only re-hydrate when data changed. See `docs/Scrapers-and-Sync-Design.md`.
- **UX:** Optional “Check for updates” or “Update data” on login (or in a settings/data tab): run fetchers, compare hashes to last run, offer “Update now” or auto-update when changed. Scheduler (Task Scheduler, cron, GitHub Actions) can also run fetchers + sync check in the background.
- **App code updates:** Separate (git pull, CI/CD, Docker rebuild); same idea: optional “update available” or auto-restart on deploy.

---

## 15. Can slicer options be integrated? — **Later; more research**

**Feasibility: Open-ended**

- **Definitely a later feature.** More research needed on which slicer (Cura / PrusaSlicer / etc.), what integration (export project file, CLI, API), and whether to store/display print settings per STL in the Library UI. See original feasibility notes above for options (export .curaproject/.ini, slicer CLI/API, or print-settings table).

---

## Summary table

| # | Feature | Feasibility | Priority / notes |
|---|---------|-------------|------------------|
| 1 | Updated OPR data | High | **Sooner** — fetcher + sync check |
| 2 | ~~MMF links `/` after .com~~ | — | **Dropped** — resolved earlier |
| 3 | Full image list / gallery per MMF unit | High | **Sooner** — API has `images[]`; store/show in UI |
| 4 | Refine link manager (MMF ↔ units) | High | **Sooner** — thumbnails, filters, bulk, broken-link check |
| 5 | MMF file options from roster/tags (unit–proxy picker) | Medium–High | (a) linked-to-roster STLs; (b) tag-matched STLs (OPR/40K) |
| 6 | MMF library download buttons | Medium | **Bookmarked** — user MMF login; direct DL later |
| 7 | Auto hydrators/scrapers (MMF, OPR, Wahapedia) | High / Medium | **Sooner** — MMF+OPR straightforward; Wahapedia no API |
| 8 | User sign up and permissions | Medium | **2.0** — login, add MMF IDs, associate units, crowdsource proxies, heat map |
| 9 | Hosting and public front-end | Medium | **2.0** |
| 10 | Security features/settings | High | **2.0** |
| 11 | GW website scraper (retail data) | Medium–Low | **Sooner** — third-party or manual RRP; avoid ToS risk |
| 12 | One-button download: roster → proxies → files | Medium | Roster → select MMF proxies → one click download; depends on #6 |
| 13 | New Recruit game data + extra game systems | Worth checking | Game data for hydrators; D&D/Pathfinder, Frostgrave/Stargrave/Rangers, etc.; MMF association |
| 14 | Update process (hash checks, update on login) | High | Fetchers + hydrators; hash checks; update on login or schedule |
| 15 | Slicer integration | Open | **Later** — more research |

---

## Digital Library schema (kit metadata & faction links)

- **Kit metadata (stl_library):** `size_or_scale`, `kit_type`, `kit_composition`, `is_supported`, `print_technology`, `miniature_rating`, `license_type`, `part_count`, `print_time_estimate`. Suggested values in migration comments. See **ProxyForge/migrations/add_stl_library_kit_metadata.sql**.
- **Faction links (stl_library_faction_links):** `mmf_id`, `game_system`, `faction_key`. Associates MMF records with 40K faction (`waha_factions.id`) or OPR army (`opr_units.army`) for roster-level “this STL fits this faction” and proxy suggestions (Feature #5). See **add_stl_library_faction_links.sql**.

---

*Document added for Digital Library V0.8. Priorities and 2.0 vision updated per product direction. Edit this file as priorities and findings change.*
