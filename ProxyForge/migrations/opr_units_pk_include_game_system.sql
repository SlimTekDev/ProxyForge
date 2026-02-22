-- opr_units: add game_system to primary key so the same (opr_unit_id, army) can exist in multiple systems (GF vs Firefight).
-- Why: Firefight upload (1339 units) was overwriting GF rows because PK was (opr_unit_id, army). With (opr_unit_id, army, game_system)
-- we keep ~1737 GF/AoF rows and add ~1339 Firefight rows (~3076 total). Run after opr_units_composite_pk.sql. No DEFINER.
-- FKs that reference opr_units(opr_unit_id) must be dropped first (opr_unit_id is no longer unique); they are not re-added.

ALTER TABLE inv_proxy_bridge DROP FOREIGN KEY inv_proxy_bridge_ibfk_2;
ALTER TABLE opr_unitrules DROP FOREIGN KEY opr_unitrules_ibfk_1;
ALTER TABLE opr_unitweapons DROP FOREIGN KEY opr_unitweapons_ibfk_1;
ALTER TABLE retail_comparison DROP FOREIGN KEY retail_comparison_ibfk_1;

ALTER TABLE opr_units
  DROP PRIMARY KEY,
  ADD PRIMARY KEY (opr_unit_id, army, game_system);
