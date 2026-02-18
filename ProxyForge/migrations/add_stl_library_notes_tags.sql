-- Add user notes and tags to STL library (for Digital Library view).
-- PowerShell: Get-Content "ProxyForge\migrations\add_stl_library_notes_tags.sql" -Raw | mysql -u hobby_admin -p wargaming_erp
-- (If columns already exist, you'll get "Duplicate column" and can ignore.)

ALTER TABLE stl_library ADD COLUMN notes TEXT NULL;
ALTER TABLE stl_library ADD COLUMN tags VARCHAR(500) NULL;
