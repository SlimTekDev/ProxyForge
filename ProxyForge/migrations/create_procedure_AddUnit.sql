-- AddUnit: insert unit into list and return list summary. Used by opr_builder (cursor.callproc('AddUnit', ...)).
-- Run on cloud DB after dump/restore (procedures with DEFINER were skipped). No DEFINER; SQL SECURITY INVOKER.
-- Use unqualified table names so it works in any database (e.g. defaultdb on DigitalOcean).

DROP PROCEDURE IF EXISTS AddUnit;

DELIMITER ;;

CREATE PROCEDURE AddUnit(
    IN target_list_id INT,
    IN target_unit_id VARCHAR(50),
    IN qty INT
)
SQL SECURITY INVOKER
BEGIN
    INSERT INTO play_armylist_entries (list_id, unit_id, quantity)
    VALUES (target_list_id, target_unit_id, qty);

    SELECT
        l.list_name,
        SUM(calc.unit_total) AS current_total,
        l.point_limit
    FROM play_armylists l
    JOIN (
        SELECT list_id, (d.points_cost * e.quantity) AS unit_total
        FROM play_armylist_entries e
        JOIN waha_datasheets d ON e.unit_id = d.waha_datasheet_id
        UNION ALL
        SELECT e.list_id, (o.base_cost * e.quantity) AS unit_total
        FROM play_armylist_entries e
        JOIN play_armylists l ON e.list_id = l.list_id AND l.game_system = 'OPR'
        JOIN opr_units o ON o.opr_unit_id = e.unit_id AND o.army = l.faction_primary
    ) AS calc ON l.list_id = calc.list_id
    WHERE l.list_id = target_list_id
    GROUP BY l.list_id;
END ;;

DELIMITER ;
