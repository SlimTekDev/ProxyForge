# OPR Army Name Mismatches (Dropdown vs Army Books)

**Dropdown is now 1:1 with data.json:** The Create New List → Primary Army list comes only from `view_opr_master_picker` (i.e. `opr_units` populated by `data.json`). The static list and `opr_army_settings` merge were removed. To add an army (e.g. Blood Prime Brothers), add it to `army_forge_armies.json` and run the fetcher so it appears in `data.json`, then re-run the hydrator.

This report compares army names in **data.json** and (for legacy reference) **opr_army_settings** against the canonical **army books** in `data/opr/army_forge_armies.json`.

Regenerate the report: `python scripts/opr/compare_army_names.py`

---

## 1. In dropdown but NOT in army books (review/repair)

These can appear in the Primary Army list but are **not** in `army_forge_armies.json`. Either add them to the army list (if they are real OPR books we should fetch) or treat as legacy/alias and leave as-is (dropdown still works via `opr_army_settings`).

| Army name | Source | Suggested action |
|-----------|--------|------------------|
| Badland Nomads | opr_army_settings | Likely Firefight/Skirmish; add to army_forge_armies if we have armyId. |
| Berserker Clans | opr_army_settings | Same. |
| **Blood Prime Brothers** | (was opr_army_settings) | Add to `army_forge_armies.json` and fetcher output so it appears in data.json; then it will show in the dropdown. Library fallback still shows Prime Brothers units for "* Prime Brothers" lists. |
| Brute Clans | opr_army_settings | AoF Skirmish. |
| Brute Coalitions | opr_army_settings | Firefight. |
| City Runners | opr_army_settings | Firefight. |
| Crazed Zealots | opr_army_settings | AoF Skirmish. |
| Dragon Empire | opr_army_settings | May be AoF; add if we have book. |
| Furious Tribes | opr_army_settings | AoF Skirmish. |
| Havoc War Clans | static (app.py) | Static AoF list; if not in army_forge, consider removing or adding to army list. |
| Hidden Syndicates | opr_army_settings | Skirmish. |
| Hired Guards | opr_army_settings | Skirmish. |
| Mega-Corps | opr_army_settings | Firefight. |
| Mercenaries | opr_army_settings | Firefight. |
| Merchant Unions | opr_army_settings | Skirmish. |
| Outskirt Raiders | opr_army_settings | Skirmish. |
| Psycho Cults | opr_army_settings | Firefight. |
| Rift Daemons | static (app.py) | Static list uses "Rift Daemons"; books use "Rift Daemons of Change/Lust/Plague/War". Alias OK or narrow. |
| Security Forces | opr_army_settings | Firefight. |
| Shadow Leagues | opr_army_settings | Firefight. |
| Shortling Alliances | opr_army_settings | Skirmish. |
| Shortling Federations | opr_army_settings | Firefight. |
| **Sky-City Dwarves** | data.json, opr_army_settings, static | **Repair:** Use "Sky City Dwarves" (no hyphen) to match army book. See §3. |
| Trade Federations | opr_army_settings | Skirmish. |
| Treasure Hunters | opr_army_settings | Skirmish. |
| Worker Unions | opr_army_settings | Firefight. |

---

## 2. In army books but NOT in data.json

| Army name | Note |
|-----------|------|
| Sky City Dwarves | Same as §3: data.json has "Sky-City Dwarves" (hyphen). After normalization/fix, this row disappears. |

---

## 3. Spelling / normalization (one concrete fix)

| Location | Current | Should be (match army book) |
|----------|---------|----------------------------|
| app.py static list (OPR_ARMIES_BY_SYSTEM) | Sky-City Dwarves | **Sky City Dwarves** |
| data.json / opr_units | Set by API when fetching; API may return "Sky City Dwarves". If fetcher or an old export wrote "Sky-City Dwarves", re-fetch that army so `book.get("name")` gives the canonical form. | — |
| opr_army_settings (DB) | Manual or migration: `UPDATE opr_army_settings SET army_name = 'Sky City Dwarves' WHERE army_name = 'Sky-City Dwarves';` | — |

---

## 4. Repair checklist

- [ ] **Static list:** In `app.py`, change `"Sky-City Dwarves"` to `"Sky City Dwarves"` in OPR_ARMIES_BY_SYSTEM (all three AoF keys).
- [ ] **DB (optional):** Run `UPDATE opr_army_settings SET army_name = 'Sky City Dwarves' WHERE army_name = 'Sky-City Dwarves';` on local and cloud if you want dropdown and settings to use the canonical name.
- [ ] **data.json:** Re-run `fetch_opr_json.py` and then `newest_hydrator.py`; the API may already return "Sky City Dwarves" for that book, which will fix opr_units.
- [ ] **Blood Prime Brothers / other variants:** No change needed; they are valid dropdown options (opr_army_settings) and the library fallback shows Prime Brothers units.
- [ ] **Firefight/Skirmish-only names:** Add to `army_forge_armies.json` if you have their armyId and want them in the fetcher; otherwise leave as-is (they still appear from opr_army_settings).
