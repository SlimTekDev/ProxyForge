-- Recreate view_40k_unit_composition with both min_size and max_size so the 40K roster builder
-- can offer single/double (min/max) unit size toggle from quantized unit composition data.
-- Run once. Safe to re-run (replaces the view).
-- Uses CREATE OR REPLACE so you don't need DROP privilege (avoids SYSTEM_USER / definer issues).
-- If your view only had min_size (no max_size), the roster editor could not show the Min/Max toggle.

CREATE OR REPLACE SQL SECURITY INVOKER VIEW view_40k_unit_composition AS
WITH cleandata AS (
  SELECT
    datasheet_id,
    line_id,
    CAST(REGEXP_SUBSTR(description, '[0-9]+') AS UNSIGNED) AS line_min,
    COALESCE(NULLIF(CAST(REGEXP_REPLACE(
      REGEXP_SUBSTR(description, '[0-9]+-[0-9]+|[0-9]+'),
      '.*-',
      ''
    ) AS UNSIGNED), 0), CAST(REGEXP_SUBSTR(description, '[0-9]+') AS UNSIGNED)) AS line_max
  FROM waha_datasheet_unit_composition
)
SELECT
  datasheet_id,
  SUM(line_min) AS min_size,
  SUM(line_max) AS max_size
FROM cleandata
GROUP BY datasheet_id;
