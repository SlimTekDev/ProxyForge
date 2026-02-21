# Army Forge Fetcher / Hydrator Investigation

**Date:** 2025-02-17  
**Goal:** Define how to build fetchers and hydrators so OPR (Army Forge) list data can be updated automatically instead of manual “download → drop file → run hydrator.”

---

## 1. What ProxyForge needs

- **Input:** A single JSON file (or equivalent) that our existing OPR pipeline can consume.
- **Consumers:**  
  - **ProxyForge/newest_hydrator.py** — syncs into `opr_units` (and expects `OPR_JSON_analyzer` to have run for upgrades/army settings).
  - **scripts/opr/OPR_JSON_analyzer.py** — fills `opr_army_settings`, `opr_unit_upgrades` from the same JSON.

**Expected entry shape (per unit):**

- **Top-level (used by hydrator):** `id`, `name`, `army`, `cost`, `quality`, `defense`, `wounds`, `size`, `system`
- **Nested `unit`:** `bases.round`, `genericName`, `product.imageUrl`
- **For analyzer:** `upgradeSets` → array of `{ "label", "options": [ { "label", "cost" } ] }`

If an export only provides nested `unit` (e.g. `unit.id`, `unit.name`, `unit.cost`), the hydrator can be extended to fall back to `unit.*` when top-level keys are missing.

**Output location:** `data/opr/data.json` (and optionally `data/opr/manifest.json`, `data/opr/last_sync.json` for sync check). See **docs/Scrapers-and-Sync-Design.md**.

---

## 2. Current data source

- **Today:** `data/opr/data.json` is a large JSON **array** of unit entries. Each entry in the sample has:
  - A **`unit`** object: `id`, `cost`, `name`, `size`, `bases`, `rules`, `defense`, `quality`, `weapons`, `upgrades`, `genericName`, `product` (with `imageUrl`, sometimes `http://localhost:...` from Army Forge Studio).
  - Top-level `id` / `name` / `army` / `cost` may be present or only inside `unit`, depending on export source.
- **Origin:** This format is consistent with an **Army Forge (or Army Forge Studio) export** or an internal catalog API — not with the raw BattleScribe `.cat` files on OPR’s GitHub.

---

## 3. Army Forge: public data access (armyInfo discovered)

- **App:** https://army-forge.onepagerules.com (list builder; game systems: Grimdark Future, Age of Fantasy, etc.).
- **Discovered endpoint (2025-02):** **GET `https://army-forge.onepagerules.com/api/army-books/{armyId}`**  
  Query params: `gameSystem` (numeric id, e.g. `2` = Grimdark Future), `simpleMode=false`.  
  Example: [Battle Brothers](https://army-forge.onepagerules.com/api/army-books/78qp9l5alslt6yj8?gameSystem=2&simpleMode=false).
- **Response shape:** Single army book object with:
  - **Top level:** `uid`, `name`, `genericName`, `gameSystemId`, `gameSystemSlug`, `units` (array), `upgradePackages` (array), `spells`, `specialRules`, `versionString`, etc.
  - **units[]:** each has `id`, `cost`, `name`, `size`, `bases` (e.g. `{ "round": "40", "square": "40" }`), `rules`, `defense`, `quality`, `weapons`, `upgrades` (array of upgrade package UIDs), `genericName`. No `army` or `system` on unit—those come from the book.
  - **upgradePackages[]:** each has `uid`, `hint`, `sections[]`; each section has `label`, `options[]`; each option has `label`, `cost` (or `costs` array with `{ cost, unitId }`).
- **Mapping to our format:** For each book, set `army = book.name`, `system = book.gameSystemSlug`. For each unit, build one entry with top-level `id`, `name`, `army`, `cost`, `quality`, `defense`, `wounds` (default 1), `size`, `system`; nested `unit` with `bases`, `genericName`, `product` (empty or from book); `upgradeSets` built from the package sections whose package `uid` is in `unit.upgrades`, with each option’s `cost` = option.cost or first of option.costs.
- **Full catalog:** Fetch **every** army book (one request per `armyId` + `gameSystem`). Army list can come from a config file, or from discovering a “list armies” endpoint (e.g. when loading the app).

**Fetcher option A — Army Forge armyInfo (implemented):**

1. **Script:** `scripts/opr/fetch_opr_json.py`. Army list: `data/opr/army_forge_armies.json` (expand with more `armyId` + `gameSystem` + `armyName` as you discover them).
2. **Live fetch:** For each army, GET `armyInfo?armyName=...&gameSystem=...&armyId=...`. If the server returns non-JSON (e.g. when called from a script), use **`--from-file`**: save the armyInfo response from the browser (Network tab → armyInfo → copy response) to a .json file and run `python fetch_opr_json.py --from-file that_file.json --out data/opr/data.json`.
3. Normalize units + upgradePackages to our entry shape, write `data/opr/data.json`. Then run sync check and hydrators when changed.

---

## 4. OPR GitHub: BattleScribe .cat / .gst

- **Repos:** [OnePageRules/GrimdarkFuture](https://github.com/OnePageRules/GrimdarkFuture), AgeOfFantasy, GrimdarkFutureFirefight, etc. Contain:
  - **.gst** — game system file (root).
  - **.cat** — per-army catalog (XML; BattleScribe catalogue format).
- **Format:** BattleScribe XML (see [BSData catalogue-development wiki](https://github.com/BSData/catalogue-development/wiki/Data-structure-overview)). Not the same as our flat “unit row” JSON.
- **Limitations:** Repos may be less frequently updated than Army Forge; some army books might be Army-Forge–only. Still a useful **fallback** or **secondary source**.

**Fetcher option B — GitHub .cat → our JSON:**

1. **Fetch:** Clone or download OPR repos (e.g. GrimdarkFuture, AgeOfFantasy) or use GitHub API/raw URLs to get `.cat` and `.gst` files.
2. **Convert:** Use a BattleScribe → JSON converter (e.g. [battlescribe-to-json](https://github.com/cemderin/battlescribe-to-json) or similar; or parse .cat XML and map to our schema). Map to the expected entry shape (id, name, army, cost, quality, defense, wounds, size, system, unit.bases, unit.genericName, unit.product, upgradeSets).
3. **Write:** Emit `data/opr/data.json` (and manifest). Run sync check + hydrators when changed.

This path requires a **.cat → “our JSON”** mapping layer (and possibly handling multiple game systems / army books in one combined file).

---

## 5. Recommended approach

| Priority | Approach | Action |
|----------|----------|--------|
| **1** | **Discover Army Forge data URL** | Use Army Forge in browser with DevTools → Network; load a game system and army books; note which requests return full unit/catalog JSON. If a stable URL exists, implement **Option A** fetcher. |
| **2** | **Sync check first** | Add `data/opr/last_sync.json` + hash comparison so that even with manual drop-in of `data.json`, we only run hydrators when the file changed. See Scrapers-and-Sync-Design §3. |
| **3** | **GitHub .cat fallback** | If no Army Forge URL is available or stable, implement **Option B**: fetch .cat/.gst from OPR GitHub, convert to our JSON, write to `data/opr/data.json`. |
| **4** | **Hydrator robustness** | If needed, extend newest_hydrator (and analyzer) to accept entries where id/name/army/cost etc. live only under `unit` (fallback: `entry.get('id') or entry.get('unit', {}).get('id')`). |

---

## 6. Implementation checklist

- [ ] **Sync check:** Add `last_sync.json` (hash + timestamp) for `data/opr/data.json`; skip OPR_JSON_analyzer + newest_hydrator when hash unchanged.
- [x] **Discover Army Forge:** **armyInfo** endpoint documented above (GET with armyId, gameSystem, armyName).
- [ ] **Fetcher script:** Implemented in `scripts/opr/fetch_opr_json.py` — fetches each army from config list, normalizes to our entry shape, writes `data/opr/data.json`. Expand `data/opr/army_forge_armies.json` as more army IDs are discovered.
- [ ] **Normalize shape:** Fetcher or a small normalizer ensures each entry has top-level id, name, army, cost, quality, defense, wounds, size, system and nested unit (bases, genericName, product); upgradeSets for analyzer.
- [ ] **Orchestrator:** When adding a full sync runner, call OPR fetcher → sync check → OPR_JSON_analyzer + newest_hydrator when data changed.

---

## 7. References

- **Sync design:** `docs/Scrapers-and-Sync-Design.md` (OPR §2, layout §4, implementation order §5).
- **Feature todo:** `docs/Feature-Todo-ProxyForge.md` (#1 OPR data, #7 auto hydrators).
- **Hydrators:** `ProxyForge/newest_hydrator.py`, `scripts/opr/OPR_JSON_analyzer.py`.
- **OPR:** Army Forge https://army-forge.onepagerules.com ; OPR GitHub org https://github.com/OnePageRules ; BSData catalogue structure https://github.com/BSData/catalogue-development/wiki/Data-structure-overview .
