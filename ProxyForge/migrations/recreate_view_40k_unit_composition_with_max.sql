-- Recreate view_40k_unit_composition with both min_size and max_size so the 40K roster builder
-- can offer single/double (min/max) unit size toggle from quantized unit composition data.
-- Run once. Safe to re-run (replaces the view).
-- Uses CREATE OR REPLACE so you don't need DROP privilege (avoids SYSTEM_USER / definer issues).
-- If your view only had min_size (no max_size), the roster editor could not show the Min/Max toggle.
--
-- Dedupe: waha_datasheet_unit_composition may have duplicate rows (same line repeated). We group
-- by (datasheet_id, line_min, line_max) before summing so Mortarion with 4x "1 Mortarion" lines
-- yields min_size=1, max_size=1 instead of 4.

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
),
deduped AS (
  SELECT datasheet_id, line_min, line_max
  FROM cleandata
  GROUP BY datasheet_id, line_min, line_max
)
SELECT
  datasheet_id,
  SUM(line_min) AS min_size,
  SUM(line_max) AS max_size
FROM deduped
GROUP BY datasheet_id;
