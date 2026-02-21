-- view_40k_army_rules: faction + detachment rules for 40K Game-Day / editor.
-- Required for: army & detachment rules summary in w40k_builder (view_40k_army_rules).
-- Run on cloud DB after dump/restore. No DEFINER.

DROP VIEW IF EXISTS view_40k_army_rules;

CREATE VIEW view_40k_army_rules AS
SELECT
  f.name AS faction_name,
  f.id AS faction_id,
  d.id AS detachment_id,
  d.name AS detachment_name,
  ar.name AS army_rule_name,
  ar.description AS army_rule_desc,
  da.name AS detachment_rule_name,
  da.description AS detachment_rule_desc
FROM waha_factions f
JOIN waha_detachments d ON f.id = d.faction_id
LEFT JOIN waha_abilities ar ON ar.faction_id = f.id
  AND ar.name IN ('Oath of Moment','Waaagh!','Dark Pacts','Synapse','Acts of Faith','Nurgle''s Gift','Blessings of Khorne','Power from Pain')
LEFT JOIN waha_detachment_abilities da ON da.detachment_id = d.id;
