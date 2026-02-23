-- One-off: clamp play_armylist_entries.quantity to valid min/max from view_40k_unit_composition
-- for 40K roster entries. Fixes wrong counts (e.g. Mortarion stored as 2, Rhino as 2) after
-- view_40k_unit_composition was fixed to dedupe composition lines.
--
-- Run after: recreate_view_40k_unit_composition_with_max.sql
-- Safe to re-run (idempotent).

UPDATE play_armylist_entries e
JOIN play_armylists l ON e.list_id = l.list_id AND l.game_system = '40K_10E'
JOIN view_40k_unit_composition v ON v.datasheet_id = e.unit_id
SET e.quantity = LEAST(
  GREATEST(e.quantity, v.min_size),
  COALESCE(NULLIF(v.max_size, 0), v.min_size)
)
WHERE e.quantity < v.min_size
   OR (v.max_size IS NOT NULL AND v.max_size > 0 AND e.quantity > v.max_size);
