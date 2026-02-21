-- view_active_list_options: wargear swap options for units in a list. Optional for cloud. No DEFINER.

DROP VIEW IF EXISTS view_active_list_options;

CREATE VIEW view_active_list_options AS
SELECT
  l.list_name AS list_name,
  d.name AS unit_name,
  opt.description AS swap_option
FROM play_armylist_entries e
JOIN play_armylists l ON e.list_id = l.list_id
JOIN waha_datasheets d ON e.unit_id = d.waha_datasheet_id
JOIN waha_datasheets_options opt ON d.waha_datasheet_id = opt.datasheet_id;
