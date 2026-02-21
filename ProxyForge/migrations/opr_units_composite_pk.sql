-- opr_units composite primary key (opr_unit_id, army)
-- Why: OPR reuses the same unit id across sibling armies (e.g. Battle Brothers, Wolf Brothers, Prime Brothers).
-- With a single PK (opr_unit_id), the hydrator's ON DUPLICATE KEY UPDATE overwrote rows so only one army
-- kept each unit; other armies showed missing units (e.g. core infantry). With (opr_unit_id, army) we
-- store one row per unit per army so the library picker shows all units for each army.
-- Run once. No DEFINER.

-- 1. Drop existing primary key and add composite key
ALTER TABLE opr_units
  DROP PRIMARY KEY,
  ADD PRIMARY KEY (opr_unit_id, army);
