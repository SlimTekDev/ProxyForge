-- Remove all OPR unit and army-detail rows before a full re-hydrate.
-- Run before newest_hydrator.py and hydrate_opr_army_detail.py for a clean load.
-- Safe to run multiple times.
-- Order: delete child rows that reference opr_units first (FK constraints), then
-- null out opr_unit_id in bridge tables if FKs still exist, then delete opr_units.

DELETE FROM opr_unitrules;
DELETE FROM opr_unitweapons;
DELETE FROM opr_unit_upgrades;

UPDATE inv_proxy_bridge SET opr_unit_id = NULL WHERE opr_unit_id IS NOT NULL;
UPDATE retail_comparison SET opr_unit_id = NULL WHERE opr_unit_id IS NOT NULL;

DELETE FROM opr_units;
DELETE FROM opr_army_detail;
