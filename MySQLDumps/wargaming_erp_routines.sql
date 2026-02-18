CREATE DATABASE  IF NOT EXISTS `wargaming_erp` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `wargaming_erp`;
-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: localhost    Database: wargaming_erp
-- ------------------------------------------------------
-- Server version	8.0.44

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Temporary view structure for view `view_list_validation_40k`
--

DROP TABLE IF EXISTS `view_list_validation_40k`;
/*!50001 DROP VIEW IF EXISTS `view_list_validation_40k`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `view_list_validation_40k` AS SELECT 
 1 AS `list_id`,
 1 AS `waha_datasheet_id`,
 1 AS `unit_name`,
 1 AS `times_taken`,
 1 AS `max_allowed`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `view_unit_selector`
--

DROP TABLE IF EXISTS `view_unit_selector`;
/*!50001 DROP VIEW IF EXISTS `view_unit_selector`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `view_unit_selector` AS SELECT 
 1 AS `unit_id`,
 1 AS `unit_name`,
 1 AS `faction_name`,
 1 AS `faction_id`,
 1 AS `points_cost`,
 1 AS `image_url`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `view_40k_enhancement_picker`
--

DROP TABLE IF EXISTS `view_40k_enhancement_picker`;
/*!50001 DROP VIEW IF EXISTS `view_40k_enhancement_picker`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `view_40k_enhancement_picker` AS SELECT 
 1 AS `enhancement_id`,
 1 AS `enhancement_name`,
 1 AS `cost`,
 1 AS `description`,
 1 AS `detachment_name`,
 1 AS `detachment_id`,
 1 AS `faction_id`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `view_list_validation`
--

DROP TABLE IF EXISTS `view_list_validation`;
/*!50001 DROP VIEW IF EXISTS `view_list_validation`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `view_list_validation` AS SELECT 
 1 AS `list_name`,
 1 AS `Unit_Name`,
 1 AS `quantity`,
 1 AS `Status`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `view_master_army_command`
--

DROP TABLE IF EXISTS `view_master_army_command`;
/*!50001 DROP VIEW IF EXISTS `view_master_army_command`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `view_master_army_command` AS SELECT 
 1 AS `Project`,
 1 AS `System`,
 1 AS `Unit Count`,
 1 AS `Points Total`,
 1 AS `Physical Ready`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `view_opr_unit_complete`
--

DROP TABLE IF EXISTS `view_opr_unit_complete`;
/*!50001 DROP VIEW IF EXISTS `view_opr_unit_complete`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `view_opr_unit_complete` AS SELECT 
 1 AS `ID`,
 1 AS `Unit_Name`,
 1 AS `Army_Book`,
 1 AS `Points`,
 1 AS `Base_Size`,
 1 AS `Special_Rules`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `view_active_list_options`
--

DROP TABLE IF EXISTS `view_active_list_options`;
/*!50001 DROP VIEW IF EXISTS `view_active_list_options`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `view_active_list_options` AS SELECT 
 1 AS `list_name`,
 1 AS `unit_name`,
 1 AS `swap_option`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `view_40k_datasheet_complete`
--

DROP TABLE IF EXISTS `view_40k_datasheet_complete`;
/*!50001 DROP VIEW IF EXISTS `view_40k_datasheet_complete`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `view_40k_datasheet_complete` AS SELECT 
 1 AS `ID`,
 1 AS `Unit_Name`,
 1 AS `Faction`,
 1 AS `Points`,
 1 AS `M`,
 1 AS `T`,
 1 AS `Sv`,
 1 AS `W`,
 1 AS `Ld`,
 1 AS `OC`,
 1 AS `Base`,
 1 AS `Image`,
 1 AS `Keywords`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `view_40k_unit_composition`
--

DROP TABLE IF EXISTS `view_40k_unit_composition`;
/*!50001 DROP VIEW IF EXISTS `view_40k_unit_composition`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `view_40k_unit_composition` AS SELECT 
 1 AS `datasheet_id`,
 1 AS `full_composition`,
 1 AS `min_size`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `view_master_picker`
--

DROP TABLE IF EXISTS `view_master_picker`;
/*!50001 DROP VIEW IF EXISTS `view_master_picker`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `view_master_picker` AS SELECT 
 1 AS `system`,
 1 AS `setting`,
 1 AS `faction`,
 1 AS `id`,
 1 AS `name`,
 1 AS `points`*/;
SET character_set_client = @saved_cs_client;

--
-- Final view structure for view `view_list_validation_40k`
--

/*!50001 DROP VIEW IF EXISTS `view_list_validation_40k`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `view_list_validation_40k` AS select `e`.`list_id` AS `list_id`,`d`.`waha_datasheet_id` AS `waha_datasheet_id`,`d`.`name` AS `unit_name`,count(`e`.`unit_id`) AS `times_taken`,(case when exists(select 1 from `waha_datasheets_keywords` `dk` where ((`dk`.`datasheet_id` = `d`.`waha_datasheet_id`) and (`dk`.`keyword` = 'Epic Hero'))) then 1 when exists(select 1 from `waha_datasheets_keywords` `dk` where ((`dk`.`datasheet_id` = `d`.`waha_datasheet_id`) and (`dk`.`keyword` = 'Battleline'))) then 6 when ((`d`.`name` like '%Rhino%') or (`d`.`name` like '%Drop Pod%')) then 6 else 3 end) AS `max_allowed` from (`play_armylist_entries` `e` join `waha_datasheets` `d` on((`e`.`unit_id` = `d`.`waha_datasheet_id`))) group by `e`.`list_id`,`e`.`unit_id`,`d`.`name` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `view_unit_selector`
--

/*!50001 DROP VIEW IF EXISTS `view_unit_selector`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `view_unit_selector` AS select `d`.`waha_datasheet_id` AS `unit_id`,`d`.`name` AS `unit_name`,`f`.`name` AS `faction_name`,`d`.`faction_id` AS `faction_id`,`d`.`points_cost` AS `points_cost`,`d`.`image_url` AS `image_url` from (`waha_datasheets` `d` join `waha_factions` `f` on((`d`.`faction_id` = `f`.`id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `view_40k_enhancement_picker`
--

/*!50001 DROP VIEW IF EXISTS `view_40k_enhancement_picker`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `view_40k_enhancement_picker` AS select `e`.`id` AS `enhancement_id`,`e`.`name` AS `enhancement_name`,`e`.`cost` AS `cost`,`e`.`description` AS `description`,`d`.`name` AS `detachment_name`,`d`.`id` AS `detachment_id`,`d`.`faction_id` AS `faction_id` from (`waha_enhancements` `e` join `waha_detachments` `d` on((`e`.`detachment_id` = `d`.`id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `view_list_validation`
--

/*!50001 DROP VIEW IF EXISTS `view_list_validation`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `view_list_validation` AS select `l`.`list_name` AS `list_name`,`v`.`Unit_Name` AS `Unit_Name`,`e`.`quantity` AS `quantity`,(case when ((`v`.`Keywords` like '%Epic Hero%') and (`e`.`quantity` > 1)) then 'INVALID: Only 1 Epic Hero allowed' when ((`e`.`quantity` > 3) and (not((`v`.`Keywords` like '%Battleline%')))) then 'WARNING: Rule of 3 violation' else 'VALID' end) AS `Status` from ((`play_armylist_entries` `e` join `play_armylists` `l` on((`e`.`list_id` = `l`.`list_id`))) join `view_40k_datasheet_complete` `v` on((`e`.`unit_id` = `v`.`ID`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `view_master_army_command`
--

/*!50001 DROP VIEW IF EXISTS `view_master_army_command`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `view_master_army_command` AS select `al`.`list_name` AS `Project`,`al`.`game_system` AS `System`,count(`lu`.`instance_id`) AS `Unit Count`,sum(coalesce(`w`.`points_cost`,`u`.`base_cost`)) AS `Points Total`,(select count(0) from (`inv_physical_models` `pm` join `inv_proxy_bridge` `pb` on((`pm`.`stl_id` = `pb`.`stl_id`))) where ((`pb`.`opr_unit_id` = `lu`.`opr_unit_id`) or (`pb`.`waha_datasheet_id` = `lu`.`waha_datasheet_id`))) AS `Physical Ready` from (((`play_armylists` `al` left join `play_listunits` `lu` on((`al`.`list_id` = `lu`.`list_id`))) left join `waha_datasheets` `w` on((`lu`.`waha_datasheet_id` = `w`.`waha_datasheet_id`))) left join `opr_units` `u` on((`lu`.`opr_unit_id` = `u`.`opr_unit_id`))) group by `al`.`list_id`,`al`.`list_name`,`al`.`game_system` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `view_opr_unit_complete`
--

/*!50001 DROP VIEW IF EXISTS `view_opr_unit_complete`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `view_opr_unit_complete` AS select `u`.`opr_unit_id` AS `ID`,`u`.`name` AS `Unit_Name`,`u`.`army` AS `Army_Book`,`u`.`base_cost` AS `Points`,`u`.`round_base_mm` AS `Base_Size`,(select group_concat(concat(`sr`.`name`,if((`ur`.`rating` is not null),concat('(',`ur`.`rating`,')'),'')) separator ', ') from (`opr_unitrules` `ur` join `opr_specialrules` `sr` on((`ur`.`rule_id` = `sr`.`rule_id`))) where (`ur`.`unit_id` = `u`.`opr_unit_id`)) AS `Special_Rules` from `opr_units` `u` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `view_active_list_options`
--

/*!50001 DROP VIEW IF EXISTS `view_active_list_options`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `view_active_list_options` AS select `l`.`list_name` AS `list_name`,`d`.`name` AS `unit_name`,`opt`.`description` AS `swap_option` from (((`play_armylist_entries` `e` join `play_armylists` `l` on((`e`.`list_id` = `l`.`list_id`))) join `waha_datasheets` `d` on((`e`.`unit_id` = `d`.`waha_datasheet_id`))) join `waha_datasheets_options` `opt` on((`d`.`waha_datasheet_id` = `opt`.`datasheet_id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `view_40k_datasheet_complete`
--

/*!50001 DROP VIEW IF EXISTS `view_40k_datasheet_complete`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `view_40k_datasheet_complete` AS select `d`.`waha_datasheet_id` AS `ID`,`d`.`name` AS `Unit_Name`,`f`.`name` AS `Faction`,`d`.`points_cost` AS `Points`,`m`.`movement` AS `M`,`m`.`toughness` AS `T`,`m`.`save_value` AS `Sv`,`m`.`wounds` AS `W`,`m`.`leadership` AS `Ld`,`m`.`oc` AS `OC`,`m`.`base_size` AS `Base`,`d`.`image_url` AS `Image`,(select group_concat(`waha_datasheets_keywords`.`keyword` separator ', ') from `waha_datasheets_keywords` where (`waha_datasheets_keywords`.`datasheet_id` = `d`.`waha_datasheet_id`)) AS `Keywords` from ((`waha_datasheets` `d` join `waha_factions` `f` on((`d`.`faction_id` = `f`.`id`))) join `waha_datasheets_models` `m` on((`d`.`waha_datasheet_id` = `m`.`datasheet_id`))) where (`m`.`line_id` = 1) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `view_40k_unit_composition`
--

/*!50001 DROP VIEW IF EXISTS `view_40k_unit_composition`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `view_40k_unit_composition` AS select `waha_datasheet_unit_composition`.`datasheet_id` AS `datasheet_id`,group_concat(`waha_datasheet_unit_composition`.`description` order by `waha_datasheet_unit_composition`.`line_id` ASC separator ' | ') AS `full_composition`,cast(regexp_substr(group_concat(`waha_datasheet_unit_composition`.`description` separator ','),'[0-9]+') as unsigned) AS `min_size` from `waha_datasheet_unit_composition` group by `waha_datasheet_unit_composition`.`datasheet_id` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `view_master_picker`
--

/*!50001 DROP VIEW IF EXISTS `view_master_picker`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `view_master_picker` AS select '40K' AS `system`,'40K 10th Edition' AS `setting`,coalesce(`f`.`name`,`d`.`faction_id`) AS `faction`,`d`.`waha_datasheet_id` AS `id`,`d`.`name` AS `name`,`d`.`points_cost` AS `points` from (`waha_datasheets` `d` left join `waha_factions` `f` on((`d`.`faction_id` = `f`.`id`))) union all select 'OPR' AS `system`,`s`.`setting_name` AS `setting`,`u`.`army` AS `faction`,`u`.`opr_unit_id` AS `id`,`u`.`name` AS `name`,`u`.`base_cost` AS `points` from (`opr_units` `u` left join `opr_army_settings` `s` on((`u`.`army` = `s`.`army_name`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Dumping events for database 'wargaming_erp'
--

--
-- Dumping routines for database 'wargaming_erp'
--
/*!50003 DROP PROCEDURE IF EXISTS `AddUnit` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `AddUnit`(
    IN target_list_id INT, 
    IN target_unit_id VARCHAR(50), 
    IN qty INT
)
BEGIN
    -- Insert the unit into the list
    INSERT INTO wargaming_erp.play_armylist_entries (list_id, unit_id, quantity)
    VALUES (target_list_id, target_unit_id, qty);
    
    -- Immediately return the new list summary so the UI can update
    SELECT 
        l.list_name, 
        SUM(calc.unit_total) AS current_total,
        l.point_limit
    FROM wargaming_erp.play_armylists l
    JOIN (
        SELECT list_id, (d.points_cost * e.quantity) AS unit_total
        FROM wargaming_erp.play_armylist_entries e
        JOIN wargaming_erp.waha_datasheets d ON e.unit_id = d.waha_datasheet_id
        UNION ALL
        SELECT list_id, (o.base_cost * e.quantity) AS unit_total
        FROM wargaming_erp.opr_units o
        JOIN wargaming_erp.play_armylist_entries e ON o.opr_unit_id = e.unit_id
    ) AS calc ON l.list_id = calc.list_id
    WHERE l.list_id = target_list_id
    GROUP BY l.list_id;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `GetArmyRoster` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `GetArmyRoster`(IN input_list_id INT)
BEGIN
    SELECT 
        e.entry_id, 
        e.unit_id, 
        e.quantity AS Qty,
        COALESCE(d.name, o.name) AS Unit,
        -- Corrected Point Math for 10th Edition Blocks
        (CASE 
            WHEN l.game_system = '40K_10E' THEN
                (d.points_cost * CEIL(e.quantity / 
                    COALESCE((SELECT min_size FROM view_40k_unit_composition WHERE datasheet_id = e.unit_id), 1)
                )) + COALESCE((SELECT SUM(enh.cost) FROM play_armylist_enhancements enh WHERE enh.entry_id = e.entry_id), 0)
            ELSE 
                (o.base_cost + COALESCE((SELECT SUM(up.cost) FROM play_armylist_upgrades sel JOIN opr_unit_upgrades up ON sel.upgrade_id = up.id WHERE sel.entry_id = e.entry_id), 0)) * e.quantity
        END) AS 'Total_Pts',
        -- Stats: Using your verified column names
        d.movement AS M, d.toughness AS T, d.save_value AS SV, d.wounds AS W_Waha, d.oc AS OC,
        o.quality AS QUA, o.defense AS DEF, o.wounds AS W_OPR,
        -- Aggregated Wargear
        (SELECT JSON_ARRAYAGG(option_text) FROM play_armylist_wargear_selections WHERE entry_id = e.entry_id) AS wargear_list
    FROM play_armylist_entries e
    JOIN play_armylists l ON e.list_id = l.list_id
    LEFT JOIN waha_datasheets d ON e.unit_id = d.waha_datasheet_id AND l.game_system = '40K_10E'
    LEFT JOIN opr_units o ON e.unit_id = o.opr_unit_id AND l.game_system = 'OPR'
    WHERE e.list_id = input_list_id;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-02-12  2:03:37
