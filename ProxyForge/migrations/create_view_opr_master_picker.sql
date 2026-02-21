-- view_opr_master_picker: OPR units for library picker and unit details (opr_builder).
-- Required for: OPR unit details dialog and picker (SELECT * FROM view_opr_master_picker WHERE id = %s).
-- Run on cloud DB after dump/restore. No DEFINER.

DROP VIEW IF EXISTS view_opr_master_picker;

CREATE VIEW view_opr_master_picker AS
SELECT
  opr_units.opr_unit_id AS id,
  opr_units.name AS name,
  opr_units.army AS faction,
  opr_units.base_cost AS points,
  opr_units.quality AS QUA,
  opr_units.defense AS DEF,
  opr_units.size AS size,
  opr_units.game_system AS game_system,
  opr_units.generic_name AS generic_name
FROM opr_units;
