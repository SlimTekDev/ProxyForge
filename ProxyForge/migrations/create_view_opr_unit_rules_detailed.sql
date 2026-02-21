-- view_opr_unit_rules_detailed: OPR unit rules with description for unit details.
-- Required for: rules display in opr_builder (view_opr_unit_rules_detailed WHERE unit_id = %s).
-- Run on cloud DB after dump/restore. No DEFINER.

DROP VIEW IF EXISTS view_opr_unit_rules_detailed;

CREATE VIEW view_opr_unit_rules_detailed AS
SELECT
  ur.unit_id AS unit_id,
  ur.label AS rule_name,
  ur.rating AS rating,
  sr.description AS description
FROM opr_unitrules ur
LEFT JOIN opr_specialrules sr ON ur.label = sr.name;
