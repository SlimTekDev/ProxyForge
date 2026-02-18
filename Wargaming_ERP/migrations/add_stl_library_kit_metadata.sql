-- Digital Library refinements: kit metadata and print info for MMF records.
-- Run once. If columns already exist you'll get "Duplicate column" and can ignore.
-- Suggested UI values:
--   kit_type: Vehicle, Infantry, Monster, Prop, Terrain, Bases, Accessories, Statues, Books_PDF_Docs (single or comma-separated)
--   kit_composition: multiple_units, multiple_models, complete_models, bits, dioramas (single or comma-separated)
--   print_technology: FDM, Resin, Both, Unknown
--   is_supported: 1 = supported, 0 = unsupported, NULL = unknown

ALTER TABLE stl_library ADD COLUMN size_or_scale VARCHAR(100) NULL COMMENT 'e.g. 28mm, 32mm, 1:100';
ALTER TABLE stl_library ADD COLUMN kit_type VARCHAR(255) NULL COMMENT 'Vehicle, Infantry, Monster, Prop, Terrain, Bases, Accessories, Statues, Books_PDF_Docs';
ALTER TABLE stl_library ADD COLUMN kit_composition VARCHAR(500) NULL COMMENT 'multiple_units, multiple_models, complete_models, bits, dioramas, etc.';
ALTER TABLE stl_library ADD COLUMN is_supported TINYINT NULL COMMENT '1=supported, 0=unsupported, NULL=unknown';
ALTER TABLE stl_library ADD COLUMN print_technology VARCHAR(50) NULL COMMENT 'FDM, Resin, Both, Unknown';
ALTER TABLE stl_library ADD COLUMN miniature_rating VARCHAR(50) NULL COMMENT 'e.g. 4.5 or Minirater: 4.5';
ALTER TABLE stl_library ADD COLUMN license_type VARCHAR(100) NULL COMMENT 'e.g. Commercial, Personal, Patreon';
ALTER TABLE stl_library ADD COLUMN part_count INT NULL COMMENT 'Number of parts/pieces in kit';
ALTER TABLE stl_library ADD COLUMN print_time_estimate VARCHAR(100) NULL COMMENT 'e.g. 8h, 2-4h';
