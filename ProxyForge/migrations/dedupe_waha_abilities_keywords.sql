-- Deduplicate waha_datasheets_abilities and waha_datasheets_keywords.
-- Run after rehydration if you see double entries in unit pickers or army book special rules.
-- These tables have no primary key, so repeated inserts can create duplicate rows.
-- Safe update mode is disabled for the DELETEs (no KEY column); restored at the end.

SET @prev_safe = @@SQL_SAFE_UPDATES;
SET SQL_SAFE_UPDATES = 0;

-- 1. waha_datasheets_keywords: keep one row per (datasheet_id, keyword).
--    If model/is_faction_keyword differ for same (datasheet_id, keyword), one row is kept (arbitrary).
DROP TEMPORARY TABLE IF EXISTS _kw_dedup;
CREATE TEMPORARY TABLE _kw_dedup AS
SELECT datasheet_id, keyword, model, is_faction_keyword
FROM (
  SELECT datasheet_id, keyword, model, is_faction_keyword,
         ROW_NUMBER() OVER (PARTITION BY datasheet_id, keyword ORDER BY model, is_faction_keyword) AS rn
  FROM waha_datasheets_keywords
) t
WHERE rn = 1;

DELETE FROM waha_datasheets_keywords;
INSERT INTO waha_datasheets_keywords (datasheet_id, keyword, model, is_faction_keyword)
SELECT datasheet_id, keyword, model, is_faction_keyword FROM _kw_dedup;
DROP TEMPORARY TABLE _kw_dedup;

-- 2. waha_datasheets_abilities: keep one row per (datasheet_id, line_id, ability_id).
DROP TEMPORARY TABLE IF EXISTS _ab_dedup;
CREATE TEMPORARY TABLE _ab_dedup AS
SELECT datasheet_id, line_id, ability_id, model_name, name, description, type
FROM (
  SELECT datasheet_id, line_id, ability_id, model_name, name, description, type,
         ROW_NUMBER() OVER (PARTITION BY datasheet_id, line_id, ability_id ORDER BY line_id) AS rn
  FROM waha_datasheets_abilities
) t
WHERE rn = 1;

DELETE FROM waha_datasheets_abilities;
INSERT INTO waha_datasheets_abilities (datasheet_id, line_id, ability_id, model_name, name, description, type)
SELECT datasheet_id, line_id, ability_id, model_name, name, description, type FROM _ab_dedup;
DROP TEMPORARY TABLE _ab_dedup;

SET SQL_SAFE_UPDATES = IFNULL(@prev_safe, 1);
