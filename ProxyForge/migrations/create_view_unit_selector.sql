-- view_unit_selector: 40K unit id, name, faction, points, image. Optional for cloud. No DEFINER.

DROP VIEW IF EXISTS view_unit_selector;

CREATE VIEW view_unit_selector AS
SELECT
  d.waha_datasheet_id AS unit_id,
  d.name AS unit_name,
  f.name AS faction_name,
  d.faction_id AS faction_id,
  d.points_cost AS points_cost,
  d.image_url AS image_url
FROM waha_datasheets d
JOIN waha_factions f ON d.faction_id COLLATE utf8mb4_unicode_ci = f.id COLLATE utf8mb4_unicode_ci;
