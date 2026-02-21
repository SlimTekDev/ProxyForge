-- view_master_picker_40k: 40K-only subset of master picker (id, name, points, faction, faction_id, parent_id, system).
-- Optional for cloud; app uses view_master_picker with game_system. No DEFINER.

DROP VIEW IF EXISTS view_master_picker_40k;

CREATE VIEW view_master_picker_40k AS
SELECT
  d.waha_datasheet_id AS id,
  d.name AS name,
  d.points_cost AS points,
  f.name AS faction,
  f.id AS faction_id,
  f.parent_id AS parent_id,
  '40K' AS `system`
FROM waha_datasheets d
JOIN waha_factions f ON d.faction_id COLLATE utf8mb4_unicode_ci = f.id COLLATE utf8mb4_unicode_ci;
