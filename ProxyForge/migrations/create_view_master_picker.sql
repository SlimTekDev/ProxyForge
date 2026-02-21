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
  f.name AS faction,
  f.id AS faction_id,
  f.parent_id AS parent_id,
  '40K' AS game_system
FROM waha_datasheets d
JOIN waha_factions f ON d.faction_id = f.id
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
