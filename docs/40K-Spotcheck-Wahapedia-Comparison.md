# 40K Spot-Check: Wahapedia vs Our DB

**Date:** 2025-02-17  
**Units checked:** Ork Boyz, Ork Warboss, Ork Battlewagon, Space Marine Intercessors, Space Marine Marneus Calgar, Tau Crisis Suit (Crisis Battlesuits).

**Method:** Fetched Wahapedia unit pages (wh40k10ed) for all six units. Orks pages fetched earlier; Space Marines and Tau pages fetched using: [Marneus Calgar](https://wahapedia.ru/wh40k10ed/factions/space-marines/Marneus-Calgar), [Crisis Battlesuits](https://wahapedia.ru/wh40k10ed/factions/t-au-empire/Crisis-Battlesuits), [Intercessor Squad](https://wahapedia.ru/wh40k10ed/factions/space-marines/Intercessor-Squad). Ran `scripts/spotcheck_export_40k_units.py` for DB abilities and wargear.

---

## Summary

| Unit | Abilities in DB | Abilities on Wahapedia | Wargear match |
|------|-----------------|------------------------|---------------|
| Ork Boyz | **None** | FACTION: Waaagh!; Get Da Good Bitz | Yes (we have 9 weapons) |
| Ork Warboss | **None** | CORE: Leader; FACTION: Waaagh!; Might is Right; Da Biggest and da Best | Yes (5 weapons) |
| Ork Battlewagon | **None** | CORE: Deadly Demise D6, Firing Deck 11; FACTION: Waaagh!; Ramshackle but Rugged; WARGEAR: 'Ard Case; TRANSPORT capacity | Yes (10 weapons) |
| Space Marine Intercessors | **None** | FACTION: Oath of Moment; Objective Secured; Target Elimination | Yes (Intercessor Squad, 12 weapons) |
| Marneus Calgar | **None** | CORE: Leader; FACTION: Oath of Moment; Inspiring Leader; Master Tactician; Honour Guard of Macragge | Yes (3 weapons: Gauntlets of Ultramar x2, Victrix power sword) |
| Tau Crisis Battlesuits | **None** | CORE: Deep Strike; FACTION: For the Greater Good; Turbo-jets; WARGEAR: Battlesuit Support System, Shield Generator, Weapon Support System | Yes (9 weapons) |

**Conclusion:** For all units in the spot-check, **our database has no abilities** for these datasheets (`waha_datasheets_abilities` empty for the resolved datasheet IDs). Wahapedia clearly shows FACTION, CORE, and datasheet abilities for Boyz, Warboss, and Battlewagon. **Recommendation:** Run the Wahapedia hydrator for **Datasheets_abilities** (and ensure CSVs are loaded for Orks, Space Marines, Tau) so that `waha_datasheets_abilities` is populated; then the builder and Game-Day view will show abilities.

---

## Per-unit detail

### Ork Boyz
- **Wahapedia:** ABILITIES → FACTION: Waaagh!; Get Da Good Bitz (objective control). BODYGUARD rule. Unit composition 1 Boss Nob, 9–19 Boyz. Wargear options listed.
- **Our DB:** Boyz (id 000000016). Abilities: **(none)**. Wargear: 9 weapons (Big choppa, Big shoota, Choppa, etc.) — **match**.

### Ork Warboss
- **Wahapedia:** ABILITIES → CORE: Leader; FACTION: Waaagh!; Might is Right (melee +1 Hit while leading); Da Biggest and da Best (+4 A when Waaagh! active). LEADER: can attach to Nobz, Breaka Boyz, Boyz.
- **Our DB:** Warboss (id 000000001). Abilities: **(none)**. Wargear: 5 (Attack squig, Big choppa, Kombi-weapon, Power klaw, Twin slugga) — **match**.

### Ork Battlewagon
- **Wahapedia:** ABILITIES → CORE: Deadly Demise D6, Firing Deck 11; FACTION: Waaagh!; Ramshackle but Rugged (AP -1 to attacks); WARGEAR ABILITIES: 'Ard Case (T+2, no Firing Deck). TRANSPORT: 22 Orks Infantry (12 if killkannon); MEGA ARMOUR/JUMP PACK = 2, Ghaz = 4.
- **Our DB:** Battlewagon (id 000000039). Abilities: **(none)**. Wargear: 10 weapons — **match**. Transport text would come from `waha_datasheets.transport` if populated by `hydrate_waha_datasheets_extra`.

### Space Marine Intercessors (Intercessor Squad)
- **Wahapedia:** ABILITIES → FACTION: Oath of Moment; **Objective Secured** (control objective until opponent takes it); **Target Elimination** (+2 A to bolt rifles when used, single target). Unit composition: 1 Intercessor Sergeant, 4–9 Intercessors; grenade launcher per 5 models. Wargear options for Sergeant (power weapon, plasma pistol, hand flamer, chainsword; thunder hammer, power fist, etc.).
- **Our DB:** Intercessor Squad (id 000001157). Abilities: **(none)**. Wargear: 12 — **match**.

### Space Marine Marneus Calgar
- **Wahapedia:** ABILITIES → CORE: Leader; FACTION: Oath of Moment; **Inspiring Leader** (unit can shoot/charge after Advance or Fall Back while he leads); **Master Tactician** (Warlord on battlefield → +1 CP in Command phase); **Honour Guard of Macragge** (Marneus has FNP 4+ while Victrix Honour Guard in unit). LEADER: can attach to Intercessor Squad, Bladeguard, Aggressors, Tactical Squad, etc. Composition: 1 Marneus Calgar, 2 Victrix Honour Guard. Wargear: Gauntlets of Ultramar, Victrix power sword.
- **Our DB:** Marneus Calgar (id 000002199). Abilities: **(none)**. Wargear: 3 — **match**.

### Tau Crisis Suit (Crisis Battlesuits)
- **Wahapedia:** ABILITIES → CORE: Deep Strike; FACTION: For the Greater Good; **Turbo-jets** (Advance = +6" Move, no roll). WARGEAR ABILITIES: Battlesuit Support System (shoot after Fall Back, only those with system); Shield Generator (4+ invuln); Weapon Support System (ignore Hit modifiers). Composition: 1 Crisis Shas'vre, 2–5 Crisis Shas'ui. Wargear options (support systems, flamer, plasma, missile pod, fusion, CIB, AFP, etc.).
- **Our DB:** Crisis Battlesuits (id 000000418). Abilities: **(none)**. Wargear: 9 — **match**. (Tau faction slug on Wahapedia: `t-au-empire`.)

---

## Recommendations

1. **Populate abilities:** Run the full Wahapedia pipeline (or at least the `datasheets_abilities` step) for the factions you use (Orks, Space Marines, Tau), so that `waha_datasheets_abilities` is filled. The builder and Game-Day already query this table; they will show abilities once data exists.
2. **Name matching:** Use exact or “Intercessor Squad” for Intercessors so the export (and any UI that resolves by name) does not pick Assault Intercessors With Jump Packs. The spot-check script was updated to prefer exact match then prefix match.
3. **Transport:** Battlewagon transport capacity is on Wahapedia; if not in our app, ensure `waha_datasheets.transport` is populated (e.g. via `add_waha_datasheets_extra` + `hydrate_waha_datasheets_extra.py`).
4. **Enhancements:** Enhancements are detachment-specific and listed on detachment pages, not unit pages. This spot-check did not compare enhancements; ensure `waha_enhancements` and detachment–enhancement links are loaded for the detachments you use.

---

## How to re-run the spot-check

1. Export our data:  
   `python scripts/spotcheck_export_40k_units.py`  
   (from repo root; requires .env and DB with waha_* tables.)
2. Manually open Wahapedia unit pages for the same units and compare the ABILITIES and WARGEAR sections to the script output.
3. Update this doc with any new findings.

**Wahapedia URLs used (wh40k10ed):**  
- Orks: `.../factions/orks/` (e.g. Boyz, Warboss, Battlewagon).  
- Space Marines: `.../factions/space-marines/` — [Marneus-Calgar](https://wahapedia.ru/wh40k10ed/factions/space-marines/Marneus-Calgar), [Intercessor-Squad](https://wahapedia.ru/wh40k10ed/factions/space-marines/Intercessor-Squad).  
- Tau: `.../factions/t-au-empire/` — [Crisis-Battlesuits](https://wahapedia.ru/wh40k10ed/factions/t-au-empire/Crisis-Battlesuits).
