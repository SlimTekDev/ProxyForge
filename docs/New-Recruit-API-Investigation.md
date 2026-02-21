# New Recruit API Investigation

**Date:** 2025-02-17  
**Goal:** See if New Recruit’s API can supply (a) **catalog data** (units, points, rules) for OPR/40K to feed ProxyForge hydrators, and (b) **list import/export** for roster compatibility.

---

## Summary

- **Catalog data:** New Recruit’s **public API does not expose** game catalog data (units, points, rules). It only exposes systems list, tournaments, tournament details (teams/players/lists), and reports (player reports + exported army lists).
- **Data source:** New Recruit uses **BattleScribe data** from BSData (e.g. battlescribedata.appspot.com), not an NR-owned “game data” API. So NR is not a single source for OPR/40K unit catalogs.
- **List import:** The **Reports API** returns `exported_list` per player. That is suitable for “import list from New Recruit” if we support the export format (exact format not documented; likely BattleScribe .ros/.rosz or NR-specific JSON). Tournament API also returns players’ lists.
- **Recommendation:** Use **New Recruit for list import/export only**. Keep **OPR data** from community JSON / Army Forge and **40K data** from Wahapedia (or other) for catalog/hydrator feeds.

---

## Documented API Endpoints

All endpoints require **POST** and auth headers: `NR-Login`, `NR-Password`.  
Base URL: `https://www.newrecruit.eu`

| Endpoint | Purpose | Returns |
|----------|--------|--------|
| **POST /api/systems** | List game systems | `[{ name, id }]` — use `id` as `id_game_system` elsewhere |
| **POST /api/tournaments** | List tournaments | `{ total, tournaments[] }` — filter by date range, `id_game_system`, optional `status`, paginated (50/page) |
| **POST /api/tournament** | Single tournament | Tournament details: `name`, `type`, `visibility`, `showlists`, `teams[]` (each with `players[]` and their `lists`) |
| **POST /api/reports** | Player reports | Array of report objects; each can include **exported army list** in `exported_list` |

No endpoint returns “all units for game system X” or “army book / catalog” data.

---

## Auth and Errors

- **Auth:** Every request needs `NR-Login` and `NR-Password` headers. Failing auth returns:  
  `{ "message": "Wrong username/password, please contact NR if you need to access this API" }`
- **Errors:** Missing/invalid input often returns `{ "error": "Incorrect input" }`. Tournament endpoint can return `{ "error": "unknown error" }`.
- **Access:** Docs say to contact the NR team if you need API access or have auth issues.

---

## Fit for ProxyForge

### 1. Feeding hydrators (OPR / 40K catalog)

- **Not supported by NR API.** We need bulk unit/datasheet/points/rules to fill `opr_units`, `opr_unit_upgrades`, and `waha_*` (or equivalent). NR does not expose that.
- **OPR:** Keep using community JSON + `OPR_JSON_analyzer.py` / `newest_hydrator.py`; consider fetcher from OPR or Army Forge URLs (see Feature #1).
- **40K:** Keep using Wahapedia (or other) export/sync for `waha_datasheets`, etc.

### 2. List import from New Recruit

- **Supported.** Reports API and Tournament API both expose **exported/list data** per player.
- **Next steps:** (1) Obtain API credentials (contact NR). (2) Call `/api/reports` or `/api/tournament` and inspect the **shape of `exported_list`** (and any list payload in tournament `players[].lists`). (3) Implement a parser that maps that format into ProxyForge roster structures (`play_armylists`, `play_armylist_entries`, etc.) for the relevant game system (OPR or 40K). If the format is BattleScribe .ros/.rosz, we may need a BS roster parser or to accept a pre-exported format NR provides.

### 3. Extra game systems (D&D, Frostgrave, etc.)

- **Systems list only.** `/api/systems` gives system names and IDs (e.g. for filtering tournaments), not unit catalogs. Adding new game systems to ProxyForge still requires our own data source and hydrator per system; NR could be a list source for those systems if they support them and expose lists in a parseable format.

---

## References

- New Recruit tutorials: https://www.newrecruit.eu/tutorials/ (Systems, Reports, Tournament, Tournaments)
- New Recruit uses BattleScribe data (BSData); roster import/export .ros/.rosz: e.g. battlescribedata.appspot.com, BSData repos
- ProxyForge: `docs/Scrapers-and-Sync-Design.md`, `docs/Feature-Todo-ProxyForge.md` (#1, #13), `opr_units` / `waha_*` schema
