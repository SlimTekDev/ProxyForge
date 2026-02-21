-- view_40k_stratagems: stratagems with clean_det_id for 40K stratagem cheat sheet.
-- Required for: stratagem list in w40k_builder (view_40k_stratagems WHERE clean_det_id = %s).
-- Run on cloud DB after dump/restore. No DEFINER.

DROP VIEW IF EXISTS view_40k_stratagems;

CREATE VIEW view_40k_stratagems AS
SELECT
  faction_id,
  CAST(detachment_id AS UNSIGNED) AS clean_det_id,
  name,
  type,
  cp_cost,
  phase,
  description
FROM waha_stratagems;
