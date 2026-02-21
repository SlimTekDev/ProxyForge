-- view_master_army_command: list summary with unit count, points, physical ready (inventory).
-- Optional for cloud; uses inv_physical_models, inv_proxy_bridge. No DEFINER.

DROP VIEW IF EXISTS view_master_army_command;

CREATE VIEW view_master_army_command AS
SELECT
  al.list_name AS Project,
  al.game_system AS `System`,
  COUNT(lu.instance_id) AS `Unit Count`,
  SUM(COALESCE(w.points_cost, u.base_cost)) AS `Points Total`,
  (SELECT COUNT(*)
   FROM inv_physical_models pm
   JOIN inv_proxy_bridge pb ON pm.stl_id = pb.stl_id
   WHERE (pb.opr_unit_id = lu.opr_unit_id OR pb.waha_datasheet_id = lu.waha_datasheet_id)
  ) AS `Physical Ready`
FROM play_armylists al
LEFT JOIN play_listunits lu ON al.list_id = lu.list_id
LEFT JOIN waha_datasheets w ON lu.waha_datasheet_id = w.waha_datasheet_id
LEFT JOIN opr_units u ON lu.opr_unit_id = u.opr_unit_id
GROUP BY al.list_id, al.list_name, al.game_system;
