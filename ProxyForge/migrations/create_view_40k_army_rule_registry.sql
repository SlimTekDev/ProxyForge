-- view_40k_army_rule_registry: faction-level army rules (Faction ability type).
-- Required for: army rule display in w40k_builder editor view.
-- Run on cloud DB after dump/restore. No DEFINER.

DROP VIEW IF EXISTS view_40k_army_rule_registry;

CREATE VIEW view_40k_army_rule_registry AS
SELECT DISTINCT
  f.name AS faction_name,
  f.id AS faction_id,
  a.name AS army_rule_name,
  a.description AS army_rule_desc
FROM waha_factions f
JOIN waha_datasheets d ON d.faction_id = f.id
JOIN waha_datasheets_abilities da ON da.datasheet_id = d.waha_datasheet_id
JOIN waha_abilities a ON da.ability_id = a.id
WHERE da.type = 'Faction';
