-- view_opr_unit_complete: OPR unit with aggregated special rules. Optional for cloud. No DEFINER.

DROP VIEW IF EXISTS view_opr_unit_complete;

CREATE VIEW view_opr_unit_complete AS
SELECT
  u.opr_unit_id AS ID,
  u.name AS Unit_Name,
  u.army AS Army_Book,
  u.base_cost AS Points,
  u.round_base_mm AS Base_Size,
  (SELECT GROUP_CONCAT(CONCAT(sr.name, IF(ur.rating IS NOT NULL, CONCAT('(', ur.rating, ')'), '')) SEPARATOR ', ')
   FROM opr_unitrules ur
   JOIN opr_specialrules sr ON ur.rule_id = sr.rule_id
   WHERE ur.unit_id = u.opr_unit_id
  ) AS Special_Rules
FROM opr_units u;
