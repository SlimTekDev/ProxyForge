# Wargaming ERP — Data Dictionary

**Database:** `wargaming_erp`  
**Engine:** InnoDB  
**Charset:** utf8mb4  
**Source:** Consolidated from MySQL dump (schema as of dump).

---

## 1. List management

Tables that store army lists and the units in them.

### `play_armylists`

| Column | Type | Description |
|--------|------|-------------|
| `list_id` | INT, PK, AI | Unique ID for each army list. |
| `list_name` | VARCHAR(100) | User-defined roster name. |
| `game_system` | ENUM('OPR','40K_10E') | Controls which builder and data source apply. |
| `point_limit` | INT | Points ceiling (default 2000). |
| `waha_detachment_id` | VARCHAR(50), FK → waha_detachments.id | 40K detachment ruleset. |
| `primary_recipe_id` | INT, FK → inv_paint_recipes.recipe_id | Optional paint recipe for the list. |
| `is_boarding_action` | TINYINT(1) | Boarding action flag. |
| `faction_primary` | VARCHAR(100) | Main army/faction name. |
| `detachment_id` | VARCHAR(50) | Alternate detachment reference. |
| `faction_secondary` | VARCHAR(100) | Allied faction (optional). |

### `play_armylist_entries`

| Column | Type | Description |
|--------|------|-------------|
| `entry_id` | INT, PK, AI | One row per unit “instance” in a list. |
| `list_id` | INT, FK → play_armylists.list_id | Parent list. |
| `unit_id` | VARCHAR(50) | waha_datasheet_id (40K) or opr_unit_id (OPR). |
| `quantity` | INT | Number of models/units in this entry. |

### `play_armylist_upgrades`

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT, PK, AI | Unique selection ID. |
| `entry_id` | INT, FK → play_armylist_entries.entry_id | Unit entry (CASCADE delete). |
| `upgrade_id` | INT, FK → opr_unit_upgrades.id | OPR upgrade option. |

Legacy/alternate OPR upgrade link by upgrade ID.

### `play_armylist_opr_upgrades`

| Column | Type | Description |
|--------|------|-------------|
| `entry_id` | INT, PK, FK → play_armylist_entries.entry_id | Unit entry (CASCADE delete). |
| `option_label` | VARCHAR(255), PK | Selected upgrade text (e.g. weapon swap). |
| `cost` | INT | Points paid for this option. |

Primary table for OPR upgrade selections; used by roster logic.

### `play_armylist_enhancements`

| Column | Type | Description |
|--------|------|-------------|
| `selection_id` | INT, PK, AI | Unique selection ID. |
| `entry_id` | INT, FK → play_armylist_entries.entry_id | Unit entry. |
| `enhancement_id` | VARCHAR(50), FK → waha_enhancements.id | 40K enhancement. |
| `cost` | INT | Enhancement cost in points. |

### `play_armylist_wargear_selections`

| Column | Type | Description |
|--------|------|-------------|
| `selection_id` | INT, PK, AI | Unique selection ID. |
| `entry_id` | INT, FK → play_armylist_entries.entry_id | Unit entry (CASCADE delete). |
| `option_text` | VARCHAR(500) | Wargear option text (e.g. “Replace X with Y”). |
| `is_active` | TINYINT(1) | Whether this selection is active (default 1). |

40K wargear swap choices for roster entries.

---

## 2. OPR data

Populated from OPR JSON (e.g. OPR_JSON_analyzer, hydration scripts).

### `opr_army_settings`

| Column | Type | Description |
|--------|------|-------------|
| `army_name` | VARCHAR(100), PK | Army book name (e.g. Battle Brothers). |
| `setting_name` | VARCHAR(100) | Game mode slug (e.g. grimdark-future, age-of-fantasy). |

Maps each army to its selected OPR game system.

### `opr_units`

| Column | Type | Description |
|--------|------|-------------|
| `opr_unit_id` | VARCHAR(50), PK | Unique ID from OPR JSON. |
| `name` | VARCHAR(100) | Unit name. |
| `army` | VARCHAR(100) | Army book name. |
| `base_cost` | INT | Points before upgrades. |
| `round_base_mm` | INT | Base size in mm. |
| `is_hero` | TINYINT(1) | Hero unit flag. |
| `is_aircraft` | TINYINT(1) | Aircraft flag. |
| `quality` | INT | Quality stat (e.g. 3 = 3+). |
| `defense` | INT | Defense stat (e.g. 2 = 2+). |
| `wounds` | INT | Wounds per model. |
| `image_url` | VARCHAR(255) | Optional image URL. |
| `size` | INT | Models per unit (default 1). |
| `base_size_round` | VARCHAR(50) | Base size description. |
| `game_system` | VARCHAR(50) | OPR system (e.g. grimdark-future). |
| `generic_name` | VARCHAR(100) | Generic/display name. |

### `opr_unit_upgrades`

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT, PK, AI | Unique upgrade option ID. |
| `unit_id` | VARCHAR(50), FK → opr_units.opr_unit_id | Unit this option belongs to. |
| `section_label` | VARCHAR(255) | Category (e.g. “Replace Shredder Cannon”). |
| `option_label` | VARCHAR(255) | Option text and stats. |
| `cost` | INT | Point cost. |

### `opr_unitrules`

| Column | Type | Description |
|--------|------|-------------|
| `unit_id` | VARCHAR(50), PK, FK → opr_units | Unit. |
| `rule_id` | VARCHAR(50), PK, FK → opr_specialrules | Rule. |
| `rating` | INT | Optional rating (e.g. Tough(X)). |
| `label` | VARCHAR(100) | Optional display label. |

### `opr_unitweapons`

| Column | Type | Description |
|--------|------|-------------|
| `unit_id` | VARCHAR(50), FK → opr_units | Unit. |
| `weapon_label` | VARCHAR(100) | Weapon name and stats text. |
| `attacks` | INT | Attacks value. |
| `ap` | INT | AP value. |
| `special_rules` | VARCHAR(255) | Special rules text. |
| `count` | INT | Count (e.g. number of that weapon). |

### `opr_specialrules`

| Column | Type | Description |
|--------|------|-------------|
| `rule_id` | VARCHAR(50), PK | Unique slug (e.g. core_tough). |
| `name` | VARCHAR(100) | Human-readable name. |
| `description` | TEXT | Rule text (from JSON). |

### `opr_spells`

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT, PK, AI | Unique ID. |
| `faction` | VARCHAR(100) | Army name (e.g. Battle Brothers). |
| `name` | VARCHAR(100) | Spell name. |
| `threshold` | INT | Casting value (e.g. 4+). |
| `description` | TEXT | Spell effect. |
| UNIQUE | (faction, name) | One spell name per faction. |

---

## 3. 40K / Wahapedia data

Standardized structure for 10th Ed data (Wahapedia-sourced).

### `waha_factions`

| Column | Type | Description |
|--------|------|-------------|
| `id` | VARCHAR(50), PK | Faction ID (e.g. ORK, SM). |
| `name` | VARCHAR(100) | Faction name. |
| `link` | VARCHAR(255) | Optional URL. |
| `parent_id` | VARCHAR(50) | Parent faction if applicable. |

### `waha_detachments`

| Column | Type | Description |
|--------|------|-------------|
| `id` | VARCHAR(50), PK | Detachment ID. |
| `faction_id` | VARCHAR(50), FK → waha_factions | Faction. |
| `name` | VARCHAR(255) | Detachment name. |
| `legend` | TEXT | Optional flavour text. |
| `type` | VARCHAR(100) | Type. |
| `rules_summary` | TEXT | Rules summary. |

### `waha_datasheets`

| Column | Type | Description |
|--------|------|-------------|
| `waha_datasheet_id` | VARCHAR(50), PK | Unique Wahapedia datasheet ID. |
| `name` | VARCHAR(255) | Unit name. |
| `faction_id` | VARCHAR(50), FK → waha_factions | Faction. |
| `base_size_text` | VARCHAR(100) | Base size. |
| `points_cost` | INT | Points per model/unit. |
| `is_character` | TINYINT(1) | Character flag. |
| `is_aircraft` | TINYINT(1) | Aircraft flag. |
| `movement` | VARCHAR(20) | M stat. |
| `toughness` | INT | T stat. |
| `save_value` | VARCHAR(10) | Sv stat. |
| `wounds` | INT | W stat. |
| `leadership` | INT | Ld stat. |
| `oc` | INT | OC stat. |
| `image_url` | VARCHAR(500) | Datasheet image URL. |

### `waha_datasheet_unit_composition`

| Column | Type | Description |
|--------|------|-------------|
| `datasheet_id` | VARCHAR(50), FK → waha_datasheets | Datasheet. |
| `line_id` | INT | Line ordering. |
| `description` | TEXT | Composition line text. |

### `waha_datasheets_models`

| Column | Type | Description |
|--------|------|-------------|
| `datasheet_id` | VARCHAR(50), FK → waha_datasheets | Datasheet. |
| `line_id` | INT | Model row ordering. |
| `name` | VARCHAR(255) | Model name. |
| `movement` | VARCHAR(20) | M. |
| `toughness` | INT | T. |
| `save_value` | VARCHAR(10) | Sv. |
| `inv_sv` | VARCHAR(10) | Invulnerable save. |
| `inv_sv_descr` | TEXT | Inv save description. |
| `wounds` | INT | W. |
| `leadership` | VARCHAR(10) | Ld. |
| `oc` | INT | OC. |
| `base_size` | VARCHAR(100) | Base size. |
| `base_size_descr` | TEXT | Base size description. |

Used for 40K stat bar (per-model stats).

### `waha_datasheets_abilities`

| Column | Type | Description |
|--------|------|-------------|
| `datasheet_id` | VARCHAR(50), FK → waha_datasheets | Datasheet. |
| `line_id` | INT | Ordering. |
| `ability_id` | VARCHAR(50) | Ability reference. |
| `model_name` | VARCHAR(255) | Model name. |
| `name` | VARCHAR(255) | Ability name. |
| `description` | TEXT | Ability text. |
| `type` | VARCHAR(50) | Type. |

### `waha_datasheets_detachment_abilities`

| Column | Type | Description |
|--------|------|-------------|
| `datasheet_id` | VARCHAR(50), FK → waha_datasheets | Datasheet. |
| `detachment_ability_id` | VARCHAR(50) | Detachment ability ID. |

### `waha_datasheets_keywords`

| Column | Type | Description |
|--------|------|-------------|
| `datasheet_id` | VARCHAR(50), FK → waha_datasheets | Datasheet. |
| `keyword` | VARCHAR(100) | Keyword (e.g. Infantry, Chapter). |
| `model` | VARCHAR(100) | Model scope. |
| `is_faction_keyword` | TINYINT | Whether this is a faction keyword. |

### `waha_datasheets_leader`

| Column | Type | Description |
|--------|------|-------------|
| `leader_id` | VARCHAR(50) | Leader unit ID. |
| `attached_id` | VARCHAR(50) | Unit this leader can attach to. |

### `waha_datasheets_options`

| Column | Type | Description |
|--------|------|-------------|
| `datasheet_id` | VARCHAR(50), FK → waha_datasheets | Datasheet. |
| `line_id` | INT | Ordering. |
| `button_text` | VARCHAR(100) | Option label. |
| `description` | TEXT | Wargear option text (e.g. “Replace A with B”). |

### `waha_datasheets_stratagems`

| Column | Type | Description |
|--------|------|-------------|
| `datasheet_id` | VARCHAR(50), FK → waha_datasheets | Datasheet. |
| `stratagem_id` | VARCHAR(50) | Stratagem ID. |

### `waha_datasheets_wargear`

| Column | Type | Description |
|--------|------|-------------|
| `datasheet_id` | VARCHAR(50), FK → waha_datasheets | Datasheet. |
| `line_id` | INT | Ordering. |
| `line_in_wargear` | INT | Position in wargear block. |
| `dice` | VARCHAR(50) | Dice (e.g. for attacks). |
| `name` | VARCHAR(255) | Weapon/equipment name. |
| `description` | TEXT | Description. |
| `range_val` | VARCHAR(50) | Range. |
| `type` | VARCHAR(100) | Type. |
| `attacks` | VARCHAR(50) | Attacks. |
| `bs_ws` | VARCHAR(50) | BS/WS. |
| `strength` | VARCHAR(50) | S. |
| `ap` | VARCHAR(50) | AP. |
| `damage` | VARCHAR(50) | Damage. |

### `waha_abilities`

| Column | Type | Description |
|--------|------|-------------|
| `id` | TEXT | Ability ID. |
| `name` | TEXT | Name. |
| `legend` | TEXT | Legend. |
| `faction_id` | TEXT | Faction. |
| `description` | TEXT | Description. |

### `waha_detachment_abilities`

| Column | Type | Description |
|--------|------|-------------|
| `id` | VARCHAR(50), PK | Ability ID. |
| `faction_id` | VARCHAR(50) | Faction. |
| `name` | VARCHAR(100) | Name. |
| `legend` | TEXT | Legend. |
| `description` | TEXT | Description. |
| `detachment_name` | VARCHAR(100) | Detachment name. |
| `detachment_id` | VARCHAR(50) | Detachment ID. |

### `waha_enhancements`

| Column | Type | Description |
|--------|------|-------------|
| `faction_id` | VARCHAR(50) | Faction. |
| `id` | VARCHAR(50), PK | Enhancement ID. |
| `name` | VARCHAR(100) | Name. |
| `cost` | INT | Points cost. |
| `detachment` | VARCHAR(100) | Detachment name. |
| `detachment_id` | VARCHAR(50) | Detachment ID. |
| `legend` | TEXT | Legend. |
| `description` | TEXT | Description. |

### `waha_keywords`

| Column | Type | Description |
|--------|------|-------------|
| `id` | VARCHAR(50), PK | Keyword ID. |
| `name` | VARCHAR(255) | Keyword name. |

### `waha_stratagems`

| Column | Type | Description |
|--------|------|-------------|
| `faction_id` | VARCHAR(50) | Faction. |
| `name` | VARCHAR(100) | Stratagem name. |
| `id` | VARCHAR(50), PK | Stratagem ID. |
| `type` | VARCHAR(100) | Type. |
| `cp_cost` | INT | CP cost. |
| `legend` | TEXT | Legend. |
| `turn` | VARCHAR(50) | Turn. |
| `phase` | VARCHAR(100) | Phase. |
| `detachment` | VARCHAR(100) | Detachment. |
| `detachment_id` | VARCHAR(50) | Detachment ID. |
| `description` | TEXT | Description. |

### `waha_weapons`

| Column | Type | Description |
|--------|------|-------------|
| `weapon_id` | VARCHAR(50), PK | Weapon ID. |
| `name` | VARCHAR(255) | Weapon name. |
| `range_val` | VARCHAR(20) | Range. |
| `attacks_val` | VARCHAR(20) | Attacks. |
| `strength_val` | INT | Strength. |
| `ap_val` | INT | AP. |
| `damage_val` | VARCHAR(20) | Damage. |

---

## 4. STL library (digital library)

Used by the Digital Library UI for STL catalog and unit linking.

### `stl_library`

| Column | Type | Description |
|--------|------|-------------|
| `mmf_id` | VARCHAR(50), PK | MyMiniFactory object ID (e.g. object-735880). |
| `name` | VARCHAR(255) | Display name. |
| `creator_name` | VARCHAR(100) | Creator/designer. |
| `preview_url` | TEXT | Preview image URL. |
| `mmf_url` | TEXT | MyMiniFactory page URL. |
| `folder_path` | TEXT | Local path (optional). |
| `date_added` | TIMESTAMP | When added (default CURRENT_TIMESTAMP). |

### `stl_unit_links`

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT, PK, AI | Unique link ID. |
| `mmf_id` | VARCHAR(50), FK → stl_library.mmf_id | STL entry. |
| `unit_id` | VARCHAR(50) | waha_datasheet_id or opr_unit_id. |
| `game_system` | VARCHAR(50) | e.g. 40K_10E, grimdark-future. |
| `is_default` | TINYINT(1) | Default proxy image for this unit in this system. |
| `notes` | VARCHAR(255) | Optional notes. |
| UNIQUE | (mmf_id, unit_id, game_system) | One link per STL–unit–system. |

---

## 5. Inventory (inv_*)

Physical inventory: creators, STL library (inv), paint, resin, models, proxy bridge.

### `inv_creators`

| Column | Type | Description |
|--------|------|-------------|
| `creator_id` | INT, PK, AI | Unique ID. |
| `name` | VARCHAR(100), UNIQUE | Creator name. |
| `platform` | VARCHAR(50) | Platform (e.g. MMF, Patreon). |

### `inv_stl_library`

| Column | Type | Description |
|--------|------|-------------|
| `stl_id` | INT, PK, AI | Unique ID. |
| `creator_id` | INT, FK → inv_creators | Creator. |
| `product_name` | VARCHAR(255) | Product name. |
| `render_url` | VARCHAR(500) | Render image URL. |
| `source_url` | VARCHAR(500) | Source URL. |
| `model_height_mm` | INT | Height in mm (default 32). |
| `resin_vol_ml` | DECIMAL(10,2) | Estimated resin volume (default 5.00). |

### `inv_stl_bits`

| Column | Type | Description |
|--------|------|-------------|
| `bit_id` | INT, PK, AI | Unique ID. |
| `stl_id` | INT, FK → inv_stl_library | STL entry. |
| `bit_name` | VARCHAR(255) | Bit/option name. |
| `estimated_resin_ml` | DECIMAL(10,2) | Resin estimate (default 1.00). |

### `inv_physical_models`

| Column | Type | Description |
|--------|------|-------------|
| `model_id` | INT, PK, AI | Unique ID. |
| `stl_id` | INT, FK → inv_stl_library | STL printed. |
| `is_painted` | TINYINT(1) | Painted flag. |
| `is_magnetized` | TINYINT(1) | Magnetized flag. |
| `applied_recipe_id` | INT, FK → inv_paint_recipes | Paint recipe used. |
| `material_cost_est` | DECIMAL(10,2) | Estimated material cost (default 2.50). |
| `current_status` | ENUM('Available','Assigned','Broken') | Status. |

### `inv_paint_inventory`

| Column | Type | Description |
|--------|------|-------------|
| `paint_id` | INT, PK, AI | Unique ID. |
| `brand` | VARCHAR(50) | Brand. |
| `paint_name` | VARCHAR(100) | Paint name. |
| `paint_type` | ENUM('Base','Layer','Wash','Contrast','Technical','Basing') | Type. |
| `purchase_price` | DECIMAL(10,2) | Price (default 4.50). |
| `estimated_uses` | INT | Uses per bottle (default 50). |
| `current_bottles` | INT | Current stock (default 1). |
| `min_bottles` | INT | Min stock (default 1). |
| `is_in_stock` | TINYINT(1) | In-stock flag (default 1). |

### `inv_paint_recipes`

| Column | Type | Description |
|--------|------|-------------|
| `recipe_id` | INT, PK, AI | Unique ID. |
| `recipe_name` | VARCHAR(100) | Recipe name. |
| `notes` | TEXT | Notes. |

### `inv_recipe_steps`

| Column | Type | Description |
|--------|------|-------------|
| `step_id` | INT, PK, AI | Unique ID. |
| `recipe_id` | INT, FK → inv_paint_recipes | Recipe. |
| `paint_id` | INT, FK → inv_paint_inventory | Paint. |
| `step_order` | INT | Step order. |
| `application_method` | VARCHAR(50) | Method. |

### `inv_resin_inventory`

| Column | Type | Description |
|--------|------|-------------|
| `resin_id` | INT, PK, AI | Unique ID. |
| `brand` | VARCHAR(100) | Brand. |
| `type` | VARCHAR(50) | Type. |
| `purchase_price_usd` | DECIMAL(10,2) | Price. |
| `bottle_size_ml` | INT | Bottle size (default 1000). |
| `current_stock_ml` | DECIMAL(10,2) | Current stock in ml. |
| `min_inventory_ml` | DECIMAL(10,2) | Min stock (default 500.00). |
| `is_active` | TINYINT(1) | Active flag (default 1). |

### `inv_proxy_bridge`

| Column | Type | Description |
|--------|------|-------------|
| `proxy_id` | INT, PK, AI | Unique ID. |
| `stl_id` | INT, FK → inv_stl_library | STL. |
| `opr_unit_id` | VARCHAR(50), FK → opr_units | OPR unit. |
| `waha_datasheet_id` | VARCHAR(50), FK → waha_datasheets | 40K datasheet. |
| `is_preferred` | TINYINT(1) | Preferred proxy flag. |

Links inventory STLs to game units (OPR and/or 40K).

---

## 6. Play tracking and misc

### `play_listunits`

| Column | Type | Description |
|--------|------|-------------|
| `instance_id` | INT, PK, AI | Unique instance ID. |
| `list_id` | INT, FK → play_armylists | List. |
| `opr_unit_id` | VARCHAR(50) | OPR unit (if OPR). |
| `waha_datasheet_id` | VARCHAR(50) | 40K datasheet (if 40K). |
| `custom_name` | VARCHAR(100) | Custom name. |
| `is_combined` | TINYINT(1) | Combined unit flag. |
| `attached_to_id` | INT, FK → play_listunits.instance_id | Parent instance (e.g. attached leader). |
| `current_wounds` | INT | Current wounds in play. |
| `is_destroyed` | TINYINT(1) | Destroyed flag. |

### `play_match_tracking`

| Column | Type | Description |
|--------|------|-------------|
| `match_id` | INT, PK, AI | Unique match ID. |
| `list_id` | INT, FK → play_armylists | List used. |
| `current_round` | INT | Current round (default 1). |
| `current_cp` | INT | Command points (default 0). |
| `primary_vp` | INT | Primary VP (default 0). |
| `secondary_vp` | INT | Secondary VP (default 0). |

### `play_mission_cards`

| Column | Type | Description |
|--------|------|-------------|
| `card_id` | INT, PK, AI | Unique ID. |
| `game_system` | ENUM('OPR','40K_10E') | Game system. |
| `card_title` | VARCHAR(100) | Card title. |
| `rules_text` | TEXT | Rules text. |
| `vp_reward` | INT | VP reward. |
| `is_fixed_eligible` | TINYINT(1) | Fixed objective eligible. |

### `retail_comparison`

| Column | Type | Description |
|--------|------|-------------|
| `comparison_id` | INT, PK, AI | Unique ID. |
| `opr_unit_id` | VARCHAR(50), FK → opr_units | OPR unit. |
| `waha_datasheet_id` | VARCHAR(50), FK → waha_datasheets | 40K datasheet. |
| `equivalent_retail_name` | VARCHAR(100) | Retail product name. |
| `retail_price_usd` | DECIMAL(10,2) | Price in USD. |

### `system_alerts`

| Column | Type | Description |
|--------|------|-------------|
| `alert_id` | INT, PK, AI | Unique ID. |
| `alert_date` | TIMESTAMP | When raised (default CURRENT_TIMESTAMP). |
| `alert_type` | VARCHAR(50) | Alert type. |
| `message` | TEXT | Message. |
| `severity` | ENUM('Low','Medium','High') | Severity. |

---

## Keeping this document up to date

To refresh column metadata from the live database, run:

```sql
SELECT
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT
FROM
    INFORMATION_SCHEMA.COLUMNS
WHERE
    TABLE_SCHEMA = 'wargaming_erp'
ORDER BY
    TABLE_NAME,
    ORDINAL_POSITION;
```

Use the results to update the tables and columns above after schema changes.
