-- Recreate view_40k_datasheet_complete so every datasheet with at least one model row appears.
-- The original view required line_id = 1, so units like Boyz (whose first model row has line_id <> 1) were missing.
-- This version joins to the first model row per datasheet (MIN(line_id)) so all units show in Unit Details.
-- Run once. Safe to re-run (replaces the view).

CREATE OR REPLACE SQL SECURITY INVOKER VIEW view_40k_datasheet_complete AS
SELECT
  d.waha_datasheet_id AS ID,
  d.name AS Unit_Name,
  f.name AS Faction,
  d.points_cost AS Points,
  m.movement AS M,
  m.toughness AS T,
  m.save_value AS Sv,
  m.wounds AS W,
  m.leadership AS Ld,
  m.oc AS OC,
  m.base_size AS Base,
  d.image_url AS Image,
  (SELECT GROUP_CONCAT(k.keyword SEPARATOR ', ')
   FROM waha_datasheets_keywords k
   WHERE k.datasheet_id = d.waha_datasheet_id) AS Keywords
FROM waha_datasheets d
JOIN waha_factions f ON d.faction_id = f.id
JOIN waha_datasheets_models m ON d.waha_datasheet_id = m.datasheet_id
JOIN (
  SELECT datasheet_id, MIN(line_id) AS min_line
  FROM waha_datasheets_models
  GROUP BY datasheet_id
) first_row ON m.datasheet_id = first_row.datasheet_id AND m.line_id = first_row.min_line;
