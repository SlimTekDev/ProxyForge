-- Store full image list per MMF object (JSON array of {url, thumbnailUrl}) for gallery/carousel in STL Gallery.
-- Populated when fetcher includes "images" and hydrator has this column.
-- Idempotent: safe to run multiple times (no-op if column already exists).

DROP PROCEDURE IF EXISTS add_images_json_if_missing;
DELIMITER //
CREATE PROCEDURE add_images_json_if_missing()
BEGIN
  IF (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
      WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'stl_library' AND COLUMN_NAME = 'images_json') = 0 THEN
    ALTER TABLE stl_library ADD COLUMN images_json TEXT NULL COMMENT 'JSON array of {url, thumbnailUrl} for gallery';
  END IF;
END //
DELIMITER ;
CALL add_images_json_if_missing();
DROP PROCEDURE add_images_json_if_missing;
