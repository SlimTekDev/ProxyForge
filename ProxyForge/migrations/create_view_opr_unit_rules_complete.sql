-- view_opr_unit_rules_complete: OPR unit rules with description (same as view_opr_unit_rules_detailed).
-- Optional for cloud. No DEFINER.

DROP VIEW IF EXISTS view_opr_unit_rules_complete;

CREATE VIEW view_opr_unit_rules_complete AS
SELECT
  ur.unit_id AS unit_id,
  ur.label AS rule_name,
  ur.rating AS rating,
  sr.description AS description
FROM opr_unitrules ur
LEFT JOIN opr_specialrules sr ON ur.label = sr.name;
