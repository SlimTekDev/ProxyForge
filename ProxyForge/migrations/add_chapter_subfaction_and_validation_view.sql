-- 1) Add chapter/subfaction for Space Marine lists so validation and UI can allow chapter-specific units.
ALTER TABLE play_armylists ADD COLUMN chapter_subfaction VARCHAR(100) NULL COMMENT 'Selected chapter (e.g. Blood Angels) for Space Marines; used for validation and unit picker';

-- 2) Recreate view_list_validation_40k so faction_status allows the list's chapter_subfaction keyword (Space Marines only).
DROP VIEW IF EXISTS view_list_validation_40k;

CREATE VIEW view_list_validation_40k AS
SELECT
  e.list_id,
  d.name AS unit_name,
  COUNT(e.unit_id) AS times_taken,
  CASE
    WHEN f.name IN ('Imperial Agents','Imperial Knights','Chaos Daemons','Chaos Knights') THEN 'Ally'
    WHEN EXISTS (
      SELECT 1 FROM waha_datasheets_keywords dk
      WHERE dk.datasheet_id = d.waha_datasheet_id
        AND dk.is_faction_keyword = 1
        AND dk.keyword NOT IN (l.faction_primary, 'Adeptus Astartes', 'Imperium', 'Chaos')
        AND (l.chapter_subfaction IS NULL OR dk.keyword <> l.chapter_subfaction)
    ) THEN 'INVALID'
    WHEN f.name = l.faction_primary THEN 'Valid'
    ELSE 'INVALID'
  END AS faction_status,
  CASE
    WHEN EXISTS (SELECT 1 FROM waha_datasheets_keywords dk WHERE dk.datasheet_id = d.waha_datasheet_id AND dk.keyword = 'Epic Hero') THEN 1
    WHEN EXISTS (SELECT 1 FROM waha_datasheets_keywords dk WHERE dk.datasheet_id = d.waha_datasheet_id AND dk.keyword = 'Battleline') THEN 6
    ELSE 3
  END AS max_allowed
FROM play_armylist_entries e
JOIN play_armylists l ON e.list_id = l.list_id
JOIN waha_datasheets d ON e.unit_id = d.waha_datasheet_id
JOIN waha_factions f ON d.faction_id = f.id
GROUP BY e.list_id, e.unit_id, d.name, f.name, l.faction_primary, l.chapter_subfaction;
