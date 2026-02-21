-- GetArmyRoster: return roster rows for a list (optional; app may use Python get_roster_40k instead).
-- Run on cloud DB after dump/restore. Depends on view_40k_unit_composition. No DEFINER; SQL SECURITY INVOKER.

DROP PROCEDURE IF EXISTS GetArmyRoster;

DELIMITER ;;

CREATE PROCEDURE GetArmyRoster(IN input_list_id INT)
SQL SECURITY INVOKER
BEGIN
    SELECT
        e.entry_id,
        e.unit_id,
        e.quantity AS Qty,
        COALESCE(d.name, o.name) AS Unit,
        (CASE
            WHEN l.game_system = '40K_10E' THEN
                (d.points_cost * CEIL(e.quantity /
                    COALESCE((SELECT min_size FROM view_40k_unit_composition WHERE datasheet_id = e.unit_id), 1)
                )) + COALESCE((SELECT SUM(enh.cost) FROM play_armylist_enhancements enh WHERE enh.entry_id = e.entry_id), 0)
            ELSE
                (o.base_cost + COALESCE((SELECT SUM(up.cost) FROM play_armylist_upgrades sel JOIN opr_unit_upgrades up ON sel.upgrade_id = up.id WHERE sel.entry_id = e.entry_id), 0)) * e.quantity
        END) AS Total_Pts,
        d.movement AS M, d.toughness AS T, d.save_value AS SV, d.wounds AS W_Waha, d.oc AS OC,
        o.quality AS QUA, o.defense AS DEF, o.wounds AS W_OPR,
        (SELECT JSON_ARRAYAGG(option_text) FROM play_armylist_wargear_selections WHERE entry_id = e.entry_id) AS wargear_list
    FROM play_armylist_entries e
    JOIN play_armylists l ON e.list_id = l.list_id
    LEFT JOIN waha_datasheets d ON e.unit_id = d.waha_datasheet_id AND l.game_system = '40K_10E'
    LEFT JOIN opr_units o ON e.unit_id = o.opr_unit_id AND o.army = l.faction_primary AND l.game_system = 'OPR'
    WHERE e.list_id = input_list_id;
END ;;

DELIMITER ;
