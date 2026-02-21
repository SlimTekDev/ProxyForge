-- Add Wahapedia CSV fields to waha_datasheets for 40K Army Book Reference (unit lore, role, loadout, transport, damaged).
-- Run once. If a column already exists, you will get "Duplicate column" for that line; safe to ignore.
-- After running, populate via: python scripts/wahapedia/hydrate_waha_datasheets_extra.py

ALTER TABLE waha_datasheets ADD COLUMN legend TEXT NULL COMMENT 'Unit fluff from Wahapedia Datasheets.csv';
ALTER TABLE waha_datasheets ADD COLUMN role VARCHAR(50) NULL COMMENT 'Characters, Battleline, Other';
ALTER TABLE waha_datasheets ADD COLUMN loadout TEXT NULL COMMENT 'Default equipment summary';
ALTER TABLE waha_datasheets ADD COLUMN transport TEXT NULL COMMENT 'Transport capacity/rules';
ALTER TABLE waha_datasheets ADD COLUMN damaged_w VARCHAR(50) NULL COMMENT 'Degraded wounds band e.g. 1-5';
ALTER TABLE waha_datasheets ADD COLUMN damaged_description TEXT NULL COMMENT 'Degraded profile rules';
ALTER TABLE waha_datasheets ADD COLUMN link VARCHAR(500) NULL COMMENT 'Wahapedia URL';
