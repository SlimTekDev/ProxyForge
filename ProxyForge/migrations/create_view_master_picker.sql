-- view_master_picker: union of 40K datasheets and OPR units for the library picker.
-- Required for: OPR/40K Army Builder faction dropdown and unit search.
-- Run on cloud DB after dump/restore (views with DEFINER were skipped during restore).
-- No DEFINER so it works on managed MySQL (e.g. DigitalOcean).

DROP VIEW IF EXISTS view_master_picker;

CREATE VIEW view_master_picker AS
SELECT
  d.waha_datasheet_id AS id,
  d.name AS name,
  d.points_cost AS points,
  COALESCE(f_id.name, f_name.name, d.faction_id) AS faction,
  COALESCE(f_id.id, f_name.id) AS faction_id,
  COALESCE(f_id.parent_id, f_name.parent_id) AS parent_id,
  '40K' AS game_system
FROM waha_datasheets d
LEFT JOIN waha_factions f_id ON LOWER(TRIM(d.faction_id)) COLLATE utf8mb4_unicode_ci = LOWER(TRIM(f_id.id)) COLLATE utf8mb4_unicode_ci
LEFT JOIN waha_factions f_name ON f_id.id IS NULL AND LOWER(TRIM(d.faction_id)) COLLATE utf8mb4_unicode_ci = LOWER(TRIM(f_name.name)) COLLATE utf8mb4_unicode_ci
UNION ALL
SELECT
  o.opr_unit_id AS id,
  o.name AS name,
  o.base_cost AS points,
  o.army AS faction,
  NULL AS faction_id,
  NULL AS parent_id,
  'OPR' AS game_system
FROM opr_units o;
