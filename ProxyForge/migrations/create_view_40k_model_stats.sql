-- view_40k_model_stats: per-model stats from waha_datasheets_models. Optional for cloud. No DEFINER.

DROP VIEW IF EXISTS view_40k_model_stats;

CREATE VIEW view_40k_model_stats AS
SELECT
  datasheet_id,
  name AS Model,
  movement AS M,
  toughness AS T,
  save_value AS Sv,
  wounds AS W,
  leadership AS Ld,
  oc AS OC
FROM waha_datasheets_models;
