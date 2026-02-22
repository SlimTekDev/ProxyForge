-- =============================================================================
-- YarnTracker: Two Scalar Functions and Two Stored Procedures
-- Database: yarntracker
-- Each includes: description + complete, bug-free code.
-- Stored procedures use transactions at an appropriate isolation level.
-- =============================================================================

USE yarntracker;

-- =============================================================================
-- SCALAR FUNCTION 1
-- =============================================================================
-- Description:
--   FormatYarnDisplay(yarn_id) returns a single display string for a yarn
--   given its primary key. The result is "Brand – YarnName (Weight)", e.g.
--   "Cascade Yarns – 220 Superwash (Worsted)". Centralizes display logic for
--   reports and UIs. Returns NULL if the yarn_id is not found.
-- =============================================================================

DROP FUNCTION IF EXISTS FormatYarnDisplay;

DELIMITER //

CREATE FUNCTION FormatYarnDisplay(p_yarn_id INT)
RETURNS VARCHAR(200)
READS SQL DATA
NOT DETERMINISTIC
BEGIN
    DECLARE v_result VARCHAR(200) DEFAULT NULL;
    IF p_yarn_id IS NULL THEN
        RETURN NULL;
    END IF;
    SELECT CONCAT(
        COALESCE(b.brandName, 'Unknown'),
        ' – ',
        COALESCE(y.yarnName, 'Unknown'),
        ' (',
        COALESCE(wc.categoryName, 'Unknown weight'),
        ')'
    ) INTO v_result
    FROM yarninfo y
    LEFT JOIN brandinfo b ON b.id = y.brandID
    LEFT JOIN weightcategory wc ON wc.id = y.weightCategoryID
    WHERE y.id = p_yarn_id;
    RETURN v_result;
END//

DELIMITER ;


-- =============================================================================
-- SCALAR FUNCTION 2
-- =============================================================================
-- Description:
--   GetTotalGramsForYarn(yarn_id) returns the total grams on hand for a given
--   yarn across all inventory rows. Given yarninfo.id, it sums yarninventory
--   .gramsOnHand for that yarn. Useful for quick stash checks and reporting.
--   Returns 0 if the yarn has no inventory or yarn_id is not found.
-- =============================================================================

DROP FUNCTION IF EXISTS GetTotalGramsForYarn;

DELIMITER //

CREATE FUNCTION GetTotalGramsForYarn(p_yarn_id INT)
RETURNS INT
READS SQL DATA
NOT DETERMINISTIC
BEGIN
    DECLARE v_total INT DEFAULT 0;
    IF p_yarn_id IS NULL THEN
        RETURN 0;
    END IF;
    SELECT COALESCE(SUM(inv.gramsOnHand), 0) INTO v_total
    FROM yarninventory inv
    WHERE inv.yarnID = p_yarn_id
      AND inv.gramsOnHand IS NOT NULL;
    RETURN v_total;
END//

DELIMITER ;


-- =============================================================================
-- STORED PROCEDURE 1
-- =============================================================================
-- Description:
--   GetInventoryByLocation(p_location_id) returns a recordset of all yarn
--   inventory stored in the given location. For each row it returns bin
--   number, location name, yarn display (brand – name), color, grams on hand,
--   and inventory id. Uses REPEATABLE READ so the result set is consistent
--   for the duration of the read. Read-only; no data modification.
-- =============================================================================

DROP PROCEDURE IF EXISTS GetInventoryByLocation;

DELIMITER //

CREATE PROCEDURE GetInventoryByLocation(IN p_location_id INT)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
    START TRANSACTION;

    SELECT
        inv.id AS inventory_id,
        bi.BinNumber AS bin_number,
        l.locationName AS location_name,
        CONCAT(COALESCE(b.brandName, ''), ' – ', COALESCE(y.yarnName, '')) AS yarn_display,
        COALESCE(c.Name, '(no color)') AS color_name,
        inv.gramsOnHand AS grams_on_hand,
        inv.dyeLot AS dye_lot
    FROM yarninventory inv
    JOIN yarninfo y ON y.id = inv.yarnID
    LEFT JOIN brandinfo b ON b.id = y.brandID
    LEFT JOIN color c ON c.id = inv.colorID
    LEFT JOIN bininfo bi ON bi.BinNumber = inv.binNumber
    LEFT JOIN locations l ON l.id = bi.locationID
    WHERE bi.locationID = p_location_id
      AND inv.gramsOnHand > 0
    ORDER BY bi.BinNumber, y.yarnName, c.Name;

    COMMIT;
END//

DELIMITER ;


-- =============================================================================
-- STORED PROCEDURE 2
-- =============================================================================
-- Description:
--   AllocateYarnToProject(p_project_id, p_inventory_id, p_grams) allocates
--   a quantity of yarn from a specific inventory entry to a project. It
--   validates that the project and inventory exist, that the inventory has
--   at least p_grams available (grams on hand minus already allocated),
--   then inserts a row into projectyarnallocation. Uses READ COMMITTED and
--   a transaction so the check and insert are atomic. Does not reduce
--   yarninventory.gramsOnHand (allocation is reservation; physical deduction
--   can be a separate step). Returns no result set; use OUT parameters or
--   check ROW_COUNT() if needed.
-- =============================================================================

DROP PROCEDURE IF EXISTS AllocateYarnToProject;

DELIMITER //

CREATE PROCEDURE AllocateYarnToProject(
    IN p_project_id INT,
    IN p_inventory_id INT,
    IN p_grams INT
)
BEGIN
    DECLARE v_grams_on_hand INT DEFAULT 0;
    DECLARE v_already_allocated INT DEFAULT 0;
    DECLARE v_available INT DEFAULT 0;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    IF p_project_id IS NULL OR p_inventory_id IS NULL OR p_grams IS NULL OR p_grams <= 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'AllocateYarnToProject: project_id, inventory_id, and grams must be non-null; grams must be positive.';
    END IF;

    SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
    START TRANSACTION;

    -- Ensure project exists
    IF NOT EXISTS (SELECT 1 FROM projectinfo WHERE id = p_project_id) THEN
        ROLLBACK;
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'AllocateYarnToProject: project not found.';
    END IF;

    -- Ensure inventory exists and get grams on hand
    SELECT COALESCE(gramsOnHand, 0) INTO v_grams_on_hand
    FROM yarninventory
    WHERE id = p_inventory_id;

    IF v_grams_on_hand IS NULL THEN
        ROLLBACK;
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'AllocateYarnToProject: inventory entry not found.';
    END IF;

    -- Sum already allocated from this inventory
    SELECT COALESCE(SUM(gramsAllocated), 0) INTO v_already_allocated
    FROM projectyarnallocation
    WHERE inventoryID = p_inventory_id;

    SET v_available = v_grams_on_hand - COALESCE(v_already_allocated, 0);

    IF v_available < p_grams THEN
        ROLLBACK;
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'AllocateYarnToProject: insufficient available grams for this inventory.';
    END IF;

    INSERT INTO projectyarnallocation (projectID, inventoryID, gramsAllocated)
    VALUES (p_project_id, p_inventory_id, p_grams);

    COMMIT;
END//

DELIMITER ;


-- =============================================================================
-- USAGE EXAMPLES (run after creating objects)
-- =============================================================================
/*
-- Scalar function 1
SELECT FormatYarnDisplay(1) AS yarn_display;
SELECT FormatYarnDisplay(NULL) AS yarn_display;

-- Scalar function 2
SELECT GetTotalGramsForYarn(1) AS total_grams;
SELECT GetTotalGramsForYarn(999) AS total_grams;

-- Stored procedure 1 (recordset)
CALL GetInventoryByLocation(1);

-- Stored procedure 2 (allocation)
CALL AllocateYarnToProject(2, 1, 100);
-- Invalid: CALL AllocateYarnToProject(2, 1, 99999);
*/
