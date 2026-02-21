# 40K Army Builder & Rules Display: Feature Parity Research

This document summarizes research on **Wahapedia**, **New Recruit**, and **Army Forge** (plus official **Battle Forge**) for the army builder and rules display side of ProxyForge. It identifies features and recommended implementation approaches.

---

## 1. Reference Platforms Summary

### 1.1 Wahapedia (wahapedia.ru / wahappka.ru)

- **Role**: Rules library + roster builder; community reference for 40K 10th edition.
- **Army builder**: Dedicated roster builder (e.g. wahappka.ru/rosters) with faction browse, unit selection from faction datasheets, automatic point totals, enhancement management for characters.
- **Rules display**: Hierarchical structure: Core Rules → Rules Appendix, Rules Commentary, mission packs (e.g. Tempest of War). Faction pages with filters for **Allegiance** and **Detachment**; each detachment has its own rules/stratagems.
- **List-building enforcement**: 10th edition construction rules: unit duplicate limits (Rule of 3/1/6), detachment requirements, faction keyword consistency.
- **Notable**: Single place for faction rules, stratagems, and roster building; no BattleScribe; data sourced from community/GW publications.

### 1.2 New Recruit (newrecruit.eu)

- **Role**: Modern, free, web-based army builder for multiple systems (40K 10th/9th, AoS, Horus Heresy, Kill Team, The 9th Age, etc.).
- **Army building**: Create lists, auto point counting, **list validity checking** (uses BattleScribe-style data). Detachment selection (e.g. Space Marines: 21 detachments – Gladius, 1st Company Task Force, Anvil Siege Force, etc.).
- **BattleScribe compatibility**: Create, load, and **edit** BattleScribe rosters (.ros / .rosz); one-click sync, no manual file handling.
- **Platform**: Works on phones, tablets, desktops; optional subscription for bonus features.
- **Extras**: Player profiles (game results, stats), tournament organisation (ELO ladders, pairings, list validity checks, Swiss/group/elimination), Warhall integration for 3D sim.
- **Data**: Community-maintained BattleScribe datasets keep rules current.

### 1.3 Army Forge (army-forge.onepagerules.com)

- **Role**: Official list builder for **One Page Rules** games (e.g. Grimdark Future), not 40K. Different game system; useful for UX patterns (list structure, validation, export) but not for 40K rules content.

### 1.4 Battle Forge (Official Warhammer 40K App)

- **Role**: GW’s official 40K app army builder.
- **Features**:
  - Game sizes: Incursion (1,000), Strike Force (2,000), Onslaught (3,000).
  - **Automatic error detection** (incorrect loadouts, illegal choices).
  - **Export** lists to share or submit to events.
  - Reference: Index datasheets, Combat Patrol, Imperial Armour; Core Rules; army rules, Enhancements, Stratagems; codex content via book codes.
- **Availability**: Free app; core rules and Combat Patrol free; other content paywalled over time.

---

## 2. Core 40K 10th Edition List-Building Rules (for parity)

Implementing these gives parity with how Wahapedia, New Recruit, and Battle Forge treat legality:

| Rule | Description | ProxyForge status |
|------|-------------|------------------|
| **Detachment choice** | One detachment per list; defines army rule, stratagems, enhancements. | ✅ Detachment picker; army/detachment rules displayed. |
| **Faction keyword** | All units share at least one Faction keyword. | ✅ Faction filter; chapter/subfaction (SM) and validation view. |
| **Rule of 3 / 1 / 6** | Same datasheet: max 3 (general), 1 (Epic Hero), 6 (Battleline, Dedicated Transport). | ✅ `view_list_validation_40k`; sidebar validation. |
| **One Epic Hero per name** | Only one of each named Epic Hero in the army. | ✅ Validation view / uniqueness implied by datasheet count. |
| **Enhancements** | Max **3 enhancements** in the army; each enhancement **once**; only on **Characters** (not Epic Heroes); one enhancement per character. | ⚠️ Partial: character-only + “taken elsewhere” UI; **no global cap of 3** or “all different” enforced in validation. |
| **Warlord** | At least one Character as Warlord. | ❌ Not enforced. |
| **Point limit** | List total ≤ chosen limit (e.g. 2,000). | ✅ Points summary and over-limit warning. |
| **Unit size** | Min/max model count per datasheet (e.g. 5–10). | ✅ `view_40k_unit_composition` min/max; Min/Max toggle in roster. |

---

## 3. Feature Parity Matrix

### 3.1 Army builder

| Feature | Wahapedia | New Recruit | Battle Forge | ProxyForge | Recommendation |
|--------|-----------|-------------|--------------|------------|----------------|
| Faction + detachment selection | ✅ | ✅ | ✅ | ✅ | Keep; extend to more subfactions (see overhaul plan). |
| Unit picker (faction-filtered) | ✅ | ✅ | ✅ | ✅ | Add detachment-aware filtering when data exists. |
| Point limit (1k/2k/3k) | ✅ | ✅ | ✅ | ✅ | Confirm 2k default; add 1k/3k presets. |
| Auto point total + over-limit warning | ✅ | ✅ | ✅ | ✅ | Done. |
| Rule of 3/1/6 validation | ✅ | ✅ | ✅ | ✅ | Done. |
| Chapter/subfaction (e.g. SM) | ✅ | ✅ | ✅ | ✅ | Done; extend to other factions. |
| Enhancement picker (detachment) | ✅ | ✅ | ✅ | ✅ | Done. |
| Max 3 enhancements, all different | ✅ | ✅ | ✅ | ❌ | Add validation + UI (see below). |
| One enhancement per character | ✅ | ✅ | ✅ | ✅ | Enforced in UI (one per entry). |
| Warlord / “must have character” | Implied | ✅ | ✅ | ❌ | Add validation: at least one Character. |
| Min/max unit size (e.g. 5–10) | ✅ | ✅ | ✅ | ✅ | Done. |
| Wargear/options per roster entry | ✅ | ✅ | ✅ | ✅ | Wargear selections stored. |
| BattleScribe import/export | ❌ | ✅ | ❌ | ❌ | Consider .rosz export (or at least text/PDF) for sharing. |
| List export (PDF/text) | Unclear | ✅ | ✅ | ❌ | Add export (see overhaul plan “Roster UX”). |

### 3.2 Rules display

| Feature | Wahapedia | New Recruit | Battle Forge | ProxyForge | Recommendation |
|--------|-----------|-------------|--------------|------------|----------------|
| Army rule (faction) | ✅ | ✅ | ✅ | ✅ | Done (view_40k_army_rules). |
| Detachment rule | ✅ | ✅ | ✅ | ✅ | Done. |
| Detachment stratagems | ✅ | ✅ | ✅ | ✅ | In unit details + Game-Day. |
| Core rules reference | ✅ | ✅ | ✅ | ❌ | Link to Wahapedia or embed summary if desired. |
| Datasheet (stats, weapons, abilities) | ✅ | ✅ | ✅ | ✅ | Unit details dialog; roster resolve fix. |
| Unit composition text | ✅ | ✅ | ✅ | ✅ | Composition tab. |
| Enhancements list (detachment) | ✅ | ✅ | ✅ | ✅ | Enhancement tab in unit details. |
| “Why this unit is valid” | ✅ | ✅ | ✅ | ❌ | Show faction + detachment (and subfaction) in picker/details. |
| Rules Commentary / Appendix | ✅ | ✅ | ✅ | ❌ | Optional: link or minimal FAQ section. |

### 3.3 UX / platform

| Feature | Wahapedia | New Recruit | Battle Forge | ProxyForge | Recommendation |
|--------|-----------|-------------|--------------|------------|----------------|
| Web-based | ✅ | ✅ | ❌ (app) | ✅ | Keep. |
| Game-Day / print-friendly view | Unclear | ✅ | ✅ | ✅ | Keep; consider PDF export. |
| Validation summary (errors/warnings) | ✅ | ✅ | ✅ | ⚠️ | Centralise: “2 warnings, 0 errors” + per-entry status. |
| Proxy / custom chapter mode | N/A | N/A | N/A | ✅ | Keep. |

---

## 4. Recommended Implementation (by priority)

### 4.1 High priority (core parity)

1. **Enhancement cap (max 3, all different)**  
   - **Where**: Validation (e.g. extend `view_list_validation_40k` or add Python check).  
   - **Logic**: Count distinct enhancements across `play_armylist_enhancements` for the list; if count > 3 or any enhancement appears more than once → validation error.  
   - **UI**: Sidebar validation message; optionally disable adding a fourth enhancement in unit details.

2. **Warlord / “at least one Character”**  
   - **Where**: Validation.  
   - **Logic**: Ensure roster has at least one entry whose unit has the Character keyword (from `waha_datasheets_keywords`).  
   - **UI**: “List must include at least one Character (Warlord).”

3. **Structured validation messages**  
   - **Where**: `show_40k_validation` + roster row display (see `docs/40K-Army-Builder-Overhaul-Plan.md`).  
   - **Logic**: Return per-entry or per-rule status (VALID / INVALID: reason / WARNING: reason); show summary (“2 warnings, 0 errors”) and optional per-row badge.

4. **Point limit presets**  
   - **Where**: List creation or list options.  
   - **Logic**: Allow 1,000 (Incursion), 2,000 (Strike Force), 3,000 (Onslaught) as presets; store in `play_armylists.point_limit` (or equivalent).

### 4.2 Medium priority (better parity + UX)

5. **Detachment-aware unit picker**  
   - **Where**: Unit search/picker (library sidebar).  
   - **Logic**: When detachment is selected, filter or tag units by “allowed in this detachment” if you have detachment–datasheet links (e.g. from Wahapedia hydrator or rules).  
   - **Overhaul plan**: Already listed as “Detachment-aware picker”.

6. **“Why this unit is valid”**  
   - **Where**: Unit picker and/or unit details dialog.  
   - **Logic**: Display “Faction: X | Detachment: Y | Subfaction: Z” (or “Allowed in this detachment”) using existing faction/detachment/subfaction data.

7. **Roster export**  
   - **Where**: Roster / Game-Day view.  
   - **Logic**: Export current roster to **text** (copy-paste) or **PDF** (e.g. reportlab or a simple HTML→PDF). Include list name, point total, validation summary, and per-unit lines (name, qty, points, wargear/enhancements).  
   - **Overhaul plan**: “Consider export (e.g. PDF or text)”.

8. **Subfactions beyond Space Marines**  
   - **Where**: Faction/subfaction model and picker.  
   - **Logic**: Use same pattern as SM chapter: store subfaction (e.g. Craftworld, Hive Fleet) and filter picker + validation by it.  
   - **Overhaul plan**: “Subfaction beyond Space Marines”.

### 4.3 Lower priority / optional

9. **Core rules / Rules Commentary link**  
   - **Where**: Sidebar or a “Rules” tab.  
   - **Logic**: Link to Wahapedia Core Rules / Commentary, or embed a short “quick reference” if you have the text.

10. **BattleScribe-style export**  
    - **Where**: Roster.  
    - **Logic**: Generate .rosz (or at least a structured text format) so lists can be opened in New Recruit or other tools. Requires understanding BattleScribe roster XML structure; lower priority unless users need it.

11. **Tournament / player stats**  
    - **Where**: New module or external.  
    - **Logic**: Like New Recruit’s ELO, ladders, game results. Only if you want ProxyForge to double as a tournament platform; otherwise out of scope for “army builder + rules display” parity.

---

## 5. Methods to implement (technical)

- **Validation**: Prefer **DB views** (e.g. `view_list_validation_40k`) for rule-of-3 and chapter; add **application-level checks** in Python for enhancement cap and “at least one Character” (or add to view if you expose roster entries + keywords).
- **Enhancement cap**: Query `play_armylist_enhancements` for the list; count by `enhancement_id`; enforce in both validation display and in unit details (disable “Add enhancement” when already 3 distinct).
- **Warlord**: Query roster entries + `waha_datasheets_keywords` for keyword `Character`; if no entry has it, set validation status to INVALID with message.
- **Export**: Use Streamlit’s ability to serve a download (e.g. `st.download_button`) with a string (text) or bytes (PDF). Build content from current roster DataFrame + validation result.
- **Detachment-aware picker**: Depends on having detachment–unit links in DB (e.g. `waha_detachment_units` or equivalent from Wahapedia). If missing, add a hydrator step or manual mapping; then filter `view_master_picker` (or unit query) by `detachment_id` when selected.

---

## 6. Files and references

| Area | File / asset |
|------|----------------|
| 40K builder | `ProxyForge/w40k_builder.py` |
| Validation | `show_40k_validation`, `view_list_validation_40k` |
| Overhaul plan | `docs/40K-Army-Builder-Overhaul-Plan.md` |
| Migrations | `ProxyForge/migrations/` (validation view, unit composition, dedupe) |

---

## 7. Summary

- **Wahapedia**: Strong on rules structure (detachments, stratagems, faction filters) and roster building with 10th ed limits; use as reference for “what rules to show” and “what to validate.”  
- **New Recruit**: Strong on validation, BattleScribe compatibility, export, and multi-system UX; use as reference for “validation UX” and “export/share.”  
- **Battle Forge**: Official reference for “must have” legality (enhancement cap, warlord, errors) and export.  
- **Army Forge (OPR)**: Useful for list-builder UX patterns only; not for 40K rules.

Implementing **enhancement cap (3 max, all different)**, **warlord (at least one Character)**, **structured validation messages**, and **roster export (text/PDF)** will bring ProxyForge to strong parity with these sources for the army builder and rules display. Detachment-aware picker and “why valid” are the next step for a Wahapedia/New Recruit–level experience.
