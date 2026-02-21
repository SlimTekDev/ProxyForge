-- view_list_validation: list-level validation (Epic Hero / Rule of 3). Depends on view_40k_datasheet_complete.
-- Optional for cloud; used by legacy/other code. Run after view_40k_datasheet_complete. No DEFINER.

DROP VIEW IF EXISTS view_list_validation;

CREATE VIEW view_list_validation AS
SELECT
  l.list_name AS list_name,
  v.Unit_Name AS Unit_Name,
  e.quantity AS quantity,
  (CASE
    WHEN (v.Keywords LIKE '%Epic Hero%') AND (e.quantity > 1) THEN 'INVALID: Only 1 Epic Hero allowed'
    WHEN (e.quantity > 3) AND (v.Keywords NOT LIKE '%Battleline%') THEN 'WARNING: Rule of 3 violation'
    ELSE 'VALID'
  END) AS Status
FROM play_armylist_entries e
JOIN play_armylists l ON e.list_id = l.list_id
JOIN view_40k_datasheet_complete v ON e.unit_id = v.ID;
