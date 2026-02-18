-- Add MMF object detail columns (from API: description, price, status, has_pdf).
-- Run once in MySQL Workbench or: see migrations/README.md for PowerShell.
-- (If columns already exist, you'll get "Duplicate column" and can ignore.)

ALTER TABLE stl_library ADD COLUMN description TEXT NULL;
ALTER TABLE stl_library ADD COLUMN price VARCHAR(50) NULL;
ALTER TABLE stl_library ADD COLUMN status VARCHAR(50) NULL;
ALTER TABLE stl_library ADD COLUMN has_pdf TINYINT NULL;
