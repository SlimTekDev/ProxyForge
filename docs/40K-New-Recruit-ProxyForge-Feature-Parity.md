# 40K Feature Parity: New Recruit vs ProxyForge

**Date:** 2025-02-17  
**Purpose:** Same kind of feature parity check as Wahapedia (see `40K-Spotcheck-Wahapedia-Comparison.md`), focused on **New Recruit** as the reference. Covers army builder, wargear/options logic, rules display, validation, export, and optional paid features so ProxyForge can aim for full New Recruit–level functionality.

**Reference:** New Recruit — https://newrecruit.eu | App: https://www.newrecruit.eu/app | 40K 10th: https://www.newrecruit.eu/wiki/wh40k-10e/warhammer-40%2C000-10th-edition/

---

## 1. Summary

| Area | New Recruit | ProxyForge | Parity |
|------|-------------|------------|--------|
| **Data source** | BattleScribe (BSData) | Wahapedia (waha_*) | Different; both valid |
| **Faction + detachment** | ✅ Catalogs per faction; detachment picker | ✅ | ✅ |
| **Unit picker** | ✅ Faction-filtered; min/max size | ✅ | ✅ |
| **Wargear / loadout** | ✅ Grouped options; **split stack** per model group | ⚠️ Options from DB; counts/slots in progress | ⚠️ |
| **List validation** | ✅ Automatic (BS constraints) | ⚠️ Rule of 3, points; enhancement cap partial | ⚠️ |
| **Points** | ✅ Auto count | ✅ | ✅ |
| **BattleScribe import/export** | ✅ .ros / .rosz; edit in-app | ❌ | ❌ |
| **Export list** | ✅ Share / submit | ❌ | ❌ |
| **Game-Day / print view** | ✅ | ✅ | ✅ |
| **Tournaments / ELO** | ✅ Optional (subscription) | ❌ | ❌ |
| **Warhall integration** | ✅ Deploy armies to 3D sim | ❌ | N/A |
| **Paid (subscription)** | Ad-free, bonus features | N/A | — |

**Conclusion:** ProxyForge matches New Recruit on core list-building (faction, detachment, units, points, composition) and Game-Day view. Gaps: **wargear logic** (split stack, per-model-group options), **BattleScribe compatibility**, **list export**, **full validation**, and **tournament/ELO** (optional). Below we detail New Recruit’s wargear behaviour and list concrete recommendations.

---

## 2. New Recruit Wargear / Options Logic (for suggestions)

New Recruit uses **BattleScribe-style data**: catalogues, entries, and **option groups** with constraints. Understanding this helps design ProxyForge’s wargear UI and storage.

### 2.1 How New Recruit handles options

- **Grouped options:** Wargear is organized into **groups** (e.g. “Acastus Autocannons”, “Missile Drones”). Each group has:
  - **Choices** (e.g. “1 Acastus autocannon + 1 lascannon” vs “2 Acastus autocannons” vs “2 Lascannons”).
  - **Constraints** (min/max selections, “per N models”, etc.).
- **Entry types:** Entries can be **upgrades** (e.g. “Show/Hide Options” for Crusade, Boarding Actions, Legends) or **wargear** attached to units. Options have:
  - **min(force)** / **max(force)** (e.g. `min(force): 1` = at least one choice in the force).
  - **Modifiers** (e.g. “set hidden true”, “set min(force) 0” when Crusade Force is in roster).
- **Per-model customization:** For units where **individual models** can have different loadouts:
  - **“Split the stack”** — use the **two overlapping squares with a plus icon** to split one unit into multiple **model groups** (e.g. “5 Boyz with shootas” + “5 Boyz with big shoota/rokkit”).
  - Each group can then have its own wargear choices within the rules (e.g. “for every 10 models, 1 can have big shoota or rokkit” → one slot per 10, chosen per group if split).

### 2.2 Takeaways for ProxyForge

1. **Option groups with constraints** — Map “for every 10 models, 1 can have A or B” to **slots** (1 slot per 10 models) and **choices per slot** (A or B). ProxyForge’s `per_N_models` + slot selectors align with this.
2. **Split stack / model groups** — New Recruit allows **multiple “sub-units”** (same datasheet, same roster entry) with different wargear. ProxyForge currently has one wargear state per roster entry; to mirror “split stack”, we’d need **per–model-group** selections (e.g. entry 1 = “Boyz”, groups: [10 with loadout A], [10 with loadout B]).
3. **1:1 and multi-weapon swaps** — “Model’s X can be replaced with Y” (one choice per model) and “X and Y can be replaced with A and B” (both required for the swap). ProxyForge’s `swap_1_1` / `swap_multi` + **count** (how many models have this swap) match this.
4. **“Any number can have”** — Counter from 0 to unit size. ProxyForge’s `any_number` + number_input 0..N matches.
5. **Validation** — New Recruit validates against BS constraints (min/max, mutual exclusions, etc.). ProxyForge can add **wargear validity** (e.g. total “per 10” slots ≤ floor(quantity/10), swap counts ≤ model counts).

---

## 3. Feature Parity Matrix

### 3.1 Army builder

| Feature | New Recruit | ProxyForge | Note |
|--------|-------------|------------|------|
| Faction + detachment selection | ✅ | ✅ | |
| Unit picker (faction-filtered) | ✅ | ✅ | |
| Point limit (1k/2k/3k) | ✅ | ✅ | |
| Auto points + over-limit warning | ✅ | ✅ | |
| Min/max unit size | ✅ | ✅ | |
| Wargear options per entry | ✅ Grouped; constraints | ⚠️ From waha_datasheets_options; structured parser | |
| **Split stack (model groups)** | ✅ | ❌ | Per-model-group loadouts |
| Counts per option (e.g. “8 with shoota”) | ✅ Via split / choices | ⚠️ In progress (number_input, slots) | |
| Enhancement picker (detachment) | ✅ | ✅ | |
| Max 3 enhancements, all different | ✅ | ⚠️ Partial | |
| Rule of 3/1/6 | ✅ | ✅ | |
| Warlord / at least one Character | ✅ | ❌ | |
| List validity (errors/warnings) | ✅ | ⚠️ | |
| BattleScribe .ros/.rosz import/export | ✅ | ❌ | |
| List export (share/submit) | ✅ | ❌ | |

### 3.2 Rules display

| Feature | New Recruit | ProxyForge | Note |
|--------|-------------|------------|------|
| Army rule (faction) | ✅ | ✅ | |
| Detachment rule + stratagems | ✅ | ✅ | |
| Datasheet (stats, weapons, abilities) | ✅ | ✅ | |
| Unit composition text | ✅ | ✅ | |
| Default loadout + options | ✅ | ✅ | |
| Weapon count / “dice roll” summary | Via list display | ✅ Final weapon count | |
| Core rules / Commentary | ✅ | ❌ | Link or embed |

### 3.3 UX / platform

| Feature | New Recruit | ProxyForge | Note |
|--------|-------------|------------|------|
| Web-based | ✅ | ✅ | |
| Mobile-friendly | ✅ | ⚠️ Streamlit | |
| Game-Day / print-friendly | ✅ | ✅ | |
| Validation summary (errors/warnings) | ✅ | ⚠️ | |
| Proxy / custom chapter | N/A | ✅ | ProxyForge differentiator |

### 3.4 Optional / paid (New Recruit)

| Feature | New Recruit | ProxyForge | Note |
|--------|-------------|------------|------|
| Ad-free | Subscription | N/A | |
| Player profiles (game results, stats) | ✅ | ❌ | |
| Tournaments (create, join, pairings) | ✅ | ❌ | |
| ELO ladders | ✅ | ❌ | |
| Warhall integration (deploy to 3D) | ✅ | ❌ | |

---

## 4. Recommendations (priority order)

### 4.1 Wargear / options (align with New Recruit logic)

1. **Finish interactive wargear UI** (see `40K-Spotcheck-Recommendations-Implementation-Plan.md` and Weapons tab work): ✅ **Done.**
   - **swap_1_1 / swap_multi:** number_input 0 or 1 (“How many have this swap?”).
   - **any_number:** number_input 0 to unit_quantity.
   - **per_N_models:** Slots = floor(quantity / N); one select per slot (e.g. big shoota vs rokkit).
   - Persist state as `w2|idx|count` or `w2|idx|slot|choice`; roster display row (summary string) written on save.
2. **Weapon count and strikethrough:** ✅ Done. Final weapon count from base + selections; strikethrough weapons with 0 count; summary line for dice rolls.
3. **Optional — “split stack”:** Deferred (out of scope for current pass). To mirror New Recruit’s “split the stack”: allow one roster entry to have multiple model groups; store per-group wargear; UI “Split unit”. Do after single-group wargear is solid.

### 4.2 Validation

4. **Enhancement cap:** ✅ Done. Max 3 enhancements in list; all different. Enforced in `show_40k_validation`; unit details already disables fourth (at army cap).
5. **Warlord:** ✅ Done. At least one Character in list. Validation rule + message in sidebar.
6. **Wargear validity:** ✅ Done (informational). Sidebar caption: “Wargear: slot/count limits are not validated.” Full per-entry slot/count checks can be added later.

### 4.3 Export and compatibility

7. **List export:** ✅ Done. Export current roster to **text** via `st.download_button` (“Export list (txt)”): list name, faction, points, per-unit lines with wargear.
8. **BattleScribe import/export:** ✅ Done (minimal). “Export for BattleScribe (.ros.xml)” downloads a minimal roster XML (roster name, points, force, selections). File extension `.ros`; full .rosz schema can be added later.

### 4.4 Lower priority (optional / paid-style)

9. **Tournaments / ELO:** Out of scope.
10. **Warhall:** Out of scope.

---

## 5. References

| Item | Link / location |
|------|------------------|
| New Recruit home | https://newrecruit.eu |
| New Recruit app | https://www.newrecruit.eu/app |
| 40K 10th wiki | https://www.newrecruit.eu/wiki/wh40k-10e/warhammer-40%2C000-10th-edition/ |
| Wahapedia comparison | `docs/40K-Spotcheck-Wahapedia-Comparison.md` |
| Feature parity research | `docs/40K-Feature-Parity-Research.md` |
| New Recruit API | `docs/New-Recruit-API-Investigation.md` |
| Wargear implementation | `ProxyForge/w40k_builder.py` (parse_wargear_option, Weapons tab) |

---

## 6. Summary

- **New Recruit** is the reference for: BattleScribe-style **grouped wargear options**, **split stack** (per-model-group loadouts), **automatic list validation**, **BattleScribe import/export**, and **list export**. Optional: tournaments, ELO, Warhall, subscription (ad-free, bonus features).
- **ProxyForge** already matches on: faction/detachment, unit picker, points, composition, enhancements (picker), Game-Day view, and final weapon count direction. Gaps: full **interactive wargear counts/slots**, **split stack**, **enhancement cap + warlord** validation, **list export**, and **BattleScribe** compatibility.
- **Recommendation:** Implement the wargear UI (counts + per-N slots), validation (enhancement cap, warlord, wargear rules), and list export first. Consider “split stack” and BattleScribe later for closer parity with New Recruit.
