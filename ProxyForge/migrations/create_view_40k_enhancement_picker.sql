-- view_40k_enhancement_picker: enhancements with detachment info for 40K roster builder.
-- Required for: enhancement picker in w40k_builder (detachment_id filter).
-- Run on cloud DB after dump/restore (views with DEFINER were skipped). No DEFINER.

DROP VIEW IF EXISTS view_40k_enhancement_picker;

CREATE VIEW view_40k_enhancement_picker AS
SELECT
  e.id AS enhancement_id,
  e.name AS enhancement_name,
  e.cost AS cost,
  e.description AS description,
  d.name AS detachment_name,
  d.id AS detachment_id,
  d.faction_id AS faction_id
FROM waha_enhancements e
JOIN waha_detachments d ON e.detachment_id = d.id;
