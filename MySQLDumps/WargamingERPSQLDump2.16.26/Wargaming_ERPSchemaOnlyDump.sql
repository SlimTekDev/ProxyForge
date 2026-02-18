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
-- Table structure for table `inv_creators`
--

DROP TABLE IF EXISTS `inv_creators`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inv_creators` (
  `creator_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `platform` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`creator_id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `inv_paint_inventory`
--

DROP TABLE IF EXISTS `inv_paint_inventory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inv_paint_inventory` (
  `paint_id` int NOT NULL AUTO_INCREMENT,
  `brand` varchar(50) DEFAULT NULL,
  `paint_name` varchar(100) DEFAULT NULL,
  `paint_type` enum('Base','Layer','Wash','Contrast','Technical','Basing') DEFAULT NULL,
  `purchase_price` decimal(10,2) DEFAULT '4.50',
  `estimated_uses` int DEFAULT '50',
  `current_bottles` int DEFAULT '1',
  `min_bottles` int DEFAULT '1',
  `is_in_stock` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`paint_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `inv_paint_recipes`
--

DROP TABLE IF EXISTS `inv_paint_recipes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inv_paint_recipes` (
  `recipe_id` int NOT NULL AUTO_INCREMENT,
  `recipe_name` varchar(100) DEFAULT NULL,
  `notes` text,
  PRIMARY KEY (`recipe_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `inv_physical_models`
--

DROP TABLE IF EXISTS `inv_physical_models`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inv_physical_models` (
  `model_id` int NOT NULL AUTO_INCREMENT,
  `stl_id` int DEFAULT NULL,
  `is_painted` tinyint(1) DEFAULT '0',
  `is_magnetized` tinyint(1) DEFAULT '0',
  `applied_recipe_id` int DEFAULT NULL,
  `material_cost_est` decimal(10,2) DEFAULT '2.50',
  `current_status` enum('Available','Assigned','Broken') DEFAULT 'Available',
  PRIMARY KEY (`model_id`),
  KEY `stl_id` (`stl_id`),
  KEY `applied_recipe_id` (`applied_recipe_id`),
  CONSTRAINT `inv_physical_models_ibfk_1` FOREIGN KEY (`stl_id`) REFERENCES `inv_stl_library` (`stl_id`),
  CONSTRAINT `inv_physical_models_ibfk_2` FOREIGN KEY (`applied_recipe_id`) REFERENCES `inv_paint_recipes` (`recipe_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `inv_proxy_bridge`
--

DROP TABLE IF EXISTS `inv_proxy_bridge`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inv_proxy_bridge` (
  `proxy_id` int NOT NULL AUTO_INCREMENT,
  `stl_id` int DEFAULT NULL,
  `opr_unit_id` varchar(50) DEFAULT NULL,
  `waha_datasheet_id` varchar(50) DEFAULT NULL,
  `is_preferred` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`proxy_id`),
  KEY `stl_id` (`stl_id`),
  KEY `opr_unit_id` (`opr_unit_id`),
  KEY `waha_datasheet_id` (`waha_datasheet_id`),
  CONSTRAINT `inv_proxy_bridge_ibfk_1` FOREIGN KEY (`stl_id`) REFERENCES `inv_stl_library` (`stl_id`),
  CONSTRAINT `inv_proxy_bridge_ibfk_2` FOREIGN KEY (`opr_unit_id`) REFERENCES `opr_units` (`opr_unit_id`),
  CONSTRAINT `inv_proxy_bridge_ibfk_3` FOREIGN KEY (`waha_datasheet_id`) REFERENCES `waha_datasheets` (`waha_datasheet_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `inv_recipe_steps`
--

DROP TABLE IF EXISTS `inv_recipe_steps`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inv_recipe_steps` (
  `step_id` int NOT NULL AUTO_INCREMENT,
  `recipe_id` int DEFAULT NULL,
  `paint_id` int DEFAULT NULL,
  `step_order` int DEFAULT NULL,
  `application_method` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`step_id`),
  KEY `recipe_id` (`recipe_id`),
  KEY `paint_id` (`paint_id`),
  CONSTRAINT `inv_recipe_steps_ibfk_1` FOREIGN KEY (`recipe_id`) REFERENCES `inv_paint_recipes` (`recipe_id`),
  CONSTRAINT `inv_recipe_steps_ibfk_2` FOREIGN KEY (`paint_id`) REFERENCES `inv_paint_inventory` (`paint_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `inv_resin_inventory`
--

DROP TABLE IF EXISTS `inv_resin_inventory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inv_resin_inventory` (
  `resin_id` int NOT NULL AUTO_INCREMENT,
  `brand` varchar(100) DEFAULT NULL,
  `type` varchar(50) DEFAULT NULL,
  `purchase_price_usd` decimal(10,2) DEFAULT NULL,
  `bottle_size_ml` int DEFAULT '1000',
  `current_stock_ml` decimal(10,2) DEFAULT NULL,
  `min_inventory_ml` decimal(10,2) DEFAULT '500.00',
  `is_active` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`resin_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `inv_stl_bits`
--

DROP TABLE IF EXISTS `inv_stl_bits`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inv_stl_bits` (
  `bit_id` int NOT NULL AUTO_INCREMENT,
  `stl_id` int DEFAULT NULL,
  `bit_name` varchar(255) DEFAULT NULL,
  `estimated_resin_ml` decimal(10,2) DEFAULT '1.00',
  PRIMARY KEY (`bit_id`),
  KEY `stl_id` (`stl_id`),
  CONSTRAINT `inv_stl_bits_ibfk_1` FOREIGN KEY (`stl_id`) REFERENCES `inv_stl_library` (`stl_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `inv_stl_library`
--

DROP TABLE IF EXISTS `inv_stl_library`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inv_stl_library` (
  `stl_id` int NOT NULL AUTO_INCREMENT,
  `creator_id` int DEFAULT NULL,
  `product_name` varchar(255) DEFAULT NULL,
  `render_url` varchar(500) DEFAULT NULL,
  `source_url` varchar(500) DEFAULT NULL,
  `model_height_mm` int DEFAULT '32',
  `resin_vol_ml` decimal(10,2) DEFAULT '5.00',
  PRIMARY KEY (`stl_id`),
  KEY `creator_id` (`creator_id`),
  CONSTRAINT `inv_stl_library_ibfk_1` FOREIGN KEY (`creator_id`) REFERENCES `inv_creators` (`creator_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `opr_army_settings`
--

DROP TABLE IF EXISTS `opr_army_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `opr_army_settings` (
  `army_name` varchar(100) NOT NULL,
  `setting_name` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`army_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `opr_specialrules`
--

DROP TABLE IF EXISTS `opr_specialrules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `opr_specialrules` (
  `rule_id` varchar(50) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `description` text,
  PRIMARY KEY (`rule_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `opr_spells`
--

DROP TABLE IF EXISTS `opr_spells`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `opr_spells` (
  `id` int NOT NULL AUTO_INCREMENT,
  `faction` varchar(100) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `threshold` int DEFAULT NULL,
  `description` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `faction` (`faction`,`name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `opr_unit_upgrades`
--

DROP TABLE IF EXISTS `opr_unit_upgrades`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `opr_unit_upgrades` (
  `id` int NOT NULL AUTO_INCREMENT,
  `unit_id` varchar(50) DEFAULT NULL,
  `section_label` varchar(255) DEFAULT NULL,
  `option_label` varchar(255) DEFAULT NULL,
  `cost` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=28545 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `opr_unitrules`
--

DROP TABLE IF EXISTS `opr_unitrules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `opr_unitrules` (
  `unit_id` varchar(50) NOT NULL,
  `rule_id` varchar(50) NOT NULL,
  `rating` int DEFAULT NULL,
  `label` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`unit_id`,`rule_id`),
  KEY `rule_id` (`rule_id`),
  CONSTRAINT `opr_unitrules_ibfk_1` FOREIGN KEY (`unit_id`) REFERENCES `opr_units` (`opr_unit_id`),
  CONSTRAINT `opr_unitrules_ibfk_2` FOREIGN KEY (`rule_id`) REFERENCES `opr_specialrules` (`rule_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `opr_units`
--

DROP TABLE IF EXISTS `opr_units`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `opr_units` (
  `opr_unit_id` varchar(50) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `army` varchar(100) DEFAULT NULL,
  `base_cost` int DEFAULT NULL,
  `round_base_mm` int DEFAULT NULL,
  `is_hero` tinyint(1) DEFAULT '0',
  `is_aircraft` tinyint(1) DEFAULT '0',
  `quality` int DEFAULT NULL,
  `defense` int DEFAULT NULL,
  `wounds` int DEFAULT NULL,
  `image_url` varchar(255) DEFAULT NULL,
  `size` int DEFAULT '1',
  `base_size_round` varchar(50) DEFAULT NULL,
  `game_system` varchar(50) DEFAULT 'grimdark-future',
  `generic_name` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`opr_unit_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `opr_unitweapons`
--

DROP TABLE IF EXISTS `opr_unitweapons`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `opr_unitweapons` (
  `unit_id` varchar(50) NOT NULL,
  `weapon_label` varchar(100) NOT NULL,
  `attacks` int DEFAULT NULL,
  `ap` int DEFAULT NULL,
  `special_rules` varchar(255) DEFAULT NULL,
  `count` int DEFAULT '1',
  PRIMARY KEY (`unit_id`,`weapon_label`),
  CONSTRAINT `opr_unitweapons_ibfk_1` FOREIGN KEY (`unit_id`) REFERENCES `opr_units` (`opr_unit_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `play_armylist_enhancements`
--

DROP TABLE IF EXISTS `play_armylist_enhancements`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `play_armylist_enhancements` (
  `selection_id` int NOT NULL AUTO_INCREMENT,
  `entry_id` int DEFAULT NULL,
  `enhancement_id` varchar(50) DEFAULT NULL,
  `cost` int DEFAULT NULL,
  PRIMARY KEY (`selection_id`),
  KEY `entry_id` (`entry_id`),
  CONSTRAINT `play_armylist_enhancements_ibfk_1` FOREIGN KEY (`entry_id`) REFERENCES `play_armylist_entries` (`entry_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `play_armylist_entries`
--

DROP TABLE IF EXISTS `play_armylist_entries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `play_armylist_entries` (
  `entry_id` int NOT NULL AUTO_INCREMENT,
  `list_id` int DEFAULT NULL,
  `unit_id` varchar(50) DEFAULT NULL,
  `quantity` int DEFAULT '1',
  PRIMARY KEY (`entry_id`),
  KEY `list_id` (`list_id`),
  CONSTRAINT `play_armylist_entries_ibfk_1` FOREIGN KEY (`list_id`) REFERENCES `play_armylists` (`list_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=99 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `play_armylist_opr_upgrades`
--

DROP TABLE IF EXISTS `play_armylist_opr_upgrades`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `play_armylist_opr_upgrades` (
  `entry_id` int NOT NULL,
  `option_label` varchar(255) NOT NULL,
  `cost` int DEFAULT NULL,
  PRIMARY KEY (`entry_id`,`option_label`),
  CONSTRAINT `play_armylist_opr_upgrades_ibfk_1` FOREIGN KEY (`entry_id`) REFERENCES `play_armylist_entries` (`entry_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `play_armylist_upgrades`
--

DROP TABLE IF EXISTS `play_armylist_upgrades`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `play_armylist_upgrades` (
  `id` int NOT NULL AUTO_INCREMENT,
  `entry_id` int DEFAULT NULL,
  `upgrade_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `entry_id` (`entry_id`),
  CONSTRAINT `play_armylist_upgrades_ibfk_1` FOREIGN KEY (`entry_id`) REFERENCES `play_armylist_entries` (`entry_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `play_armylist_wargear_selections`
--

DROP TABLE IF EXISTS `play_armylist_wargear_selections`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `play_armylist_wargear_selections` (
  `selection_id` int NOT NULL AUTO_INCREMENT,
  `entry_id` int NOT NULL,
  `option_text` varchar(500) NOT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`selection_id`),
  KEY `entry_id` (`entry_id`),
  CONSTRAINT `play_armylist_wargear_selections_ibfk_1` FOREIGN KEY (`entry_id`) REFERENCES `play_armylist_entries` (`entry_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `play_armylists`
--

DROP TABLE IF EXISTS `play_armylists`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `play_armylists` (
  `list_id` int NOT NULL AUTO_INCREMENT,
  `list_name` varchar(100) DEFAULT NULL,
  `game_system` enum('OPR','40K_10E') DEFAULT NULL,
  `point_limit` int DEFAULT '2000',
  `waha_detachment_id` varchar(50) DEFAULT NULL,
  `primary_recipe_id` int DEFAULT NULL,
  `is_boarding_action` tinyint(1) DEFAULT '0',
  `faction_primary` varchar(100) DEFAULT NULL,
  `detachment_id` varchar(50) DEFAULT NULL,
  `faction_secondary` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`list_id`),
  KEY `waha_detachment_id` (`waha_detachment_id`),
  KEY `primary_recipe_id` (`primary_recipe_id`),
  CONSTRAINT `play_armylists_ibfk_1` FOREIGN KEY (`waha_detachment_id`) REFERENCES `waha_detachments` (`id`),
  CONSTRAINT `play_armylists_ibfk_2` FOREIGN KEY (`primary_recipe_id`) REFERENCES `inv_paint_recipes` (`recipe_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `play_listunits`
--

DROP TABLE IF EXISTS `play_listunits`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `play_listunits` (
  `instance_id` int NOT NULL AUTO_INCREMENT,
  `list_id` int DEFAULT NULL,
  `opr_unit_id` varchar(50) DEFAULT NULL,
  `waha_datasheet_id` varchar(50) DEFAULT NULL,
  `custom_name` varchar(100) DEFAULT NULL,
  `is_combined` tinyint(1) DEFAULT '0',
  `attached_to_id` int DEFAULT NULL,
  `current_wounds` int DEFAULT NULL,
  `is_destroyed` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`instance_id`),
  KEY `list_id` (`list_id`),
  KEY `attached_to_id` (`attached_to_id`),
  CONSTRAINT `play_listunits_ibfk_1` FOREIGN KEY (`list_id`) REFERENCES `play_armylists` (`list_id`),
  CONSTRAINT `play_listunits_ibfk_2` FOREIGN KEY (`attached_to_id`) REFERENCES `play_listunits` (`instance_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `play_match_tracking`
--

DROP TABLE IF EXISTS `play_match_tracking`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `play_match_tracking` (
  `match_id` int NOT NULL AUTO_INCREMENT,
  `list_id` int DEFAULT NULL,
  `current_round` int DEFAULT '1',
  `current_cp` int DEFAULT '0',
  `primary_vp` int DEFAULT '0',
  `secondary_vp` int DEFAULT '0',
  PRIMARY KEY (`match_id`),
  KEY `list_id` (`list_id`),
  CONSTRAINT `play_match_tracking_ibfk_1` FOREIGN KEY (`list_id`) REFERENCES `play_armylists` (`list_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `play_mission_cards`
--

DROP TABLE IF EXISTS `play_mission_cards`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `play_mission_cards` (
  `card_id` int NOT NULL AUTO_INCREMENT,
  `game_system` enum('OPR','40K_10E') DEFAULT NULL,
  `card_title` varchar(100) DEFAULT NULL,
  `rules_text` text,
  `vp_reward` int DEFAULT NULL,
  `is_fixed_eligible` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`card_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `retail_comparison`
--

DROP TABLE IF EXISTS `retail_comparison`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `retail_comparison` (
  `comparison_id` int NOT NULL AUTO_INCREMENT,
  `opr_unit_id` varchar(50) DEFAULT NULL,
  `waha_datasheet_id` varchar(50) DEFAULT NULL,
  `equivalent_retail_name` varchar(100) DEFAULT NULL,
  `retail_price_usd` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`comparison_id`),
  KEY `opr_unit_id` (`opr_unit_id`),
  KEY `waha_datasheet_id` (`waha_datasheet_id`),
  CONSTRAINT `retail_comparison_ibfk_1` FOREIGN KEY (`opr_unit_id`) REFERENCES `opr_units` (`opr_unit_id`),
  CONSTRAINT `retail_comparison_ibfk_2` FOREIGN KEY (`waha_datasheet_id`) REFERENCES `waha_datasheets` (`waha_datasheet_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `stl_library`
--

DROP TABLE IF EXISTS `stl_library`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stl_library` (
  `mmf_id` varchar(50) NOT NULL,
  `name` varchar(255) NOT NULL,
  `creator_name` varchar(100) DEFAULT NULL,
  `preview_url` text,
  `mmf_url` text,
  `folder_path` text,
  `date_added` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`mmf_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `stl_unit_links`
--

DROP TABLE IF EXISTS `stl_unit_links`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stl_unit_links` (
  `id` int NOT NULL AUTO_INCREMENT,
  `mmf_id` varchar(50) DEFAULT NULL,
  `unit_id` varchar(50) DEFAULT NULL,
  `game_system` varchar(50) DEFAULT NULL,
  `is_default` tinyint(1) DEFAULT '0',
  `notes` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_link` (`mmf_id`,`unit_id`,`game_system`),
  UNIQUE KEY `unique_link_pair` (`mmf_id`,`unit_id`,`game_system`),
  CONSTRAINT `stl_unit_links_ibfk_1` FOREIGN KEY (`mmf_id`) REFERENCES `stl_library` (`mmf_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `system_alerts`
--

DROP TABLE IF EXISTS `system_alerts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `system_alerts` (
  `alert_id` int NOT NULL AUTO_INCREMENT,
  `alert_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `alert_type` varchar(50) DEFAULT NULL,
  `message` text,
  `severity` enum('Low','Medium','High') DEFAULT NULL,
  PRIMARY KEY (`alert_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `view_40k_army_rule_registry`
--

DROP TABLE IF EXISTS `view_40k_army_rule_registry`;
/*!50001 DROP VIEW IF EXISTS `view_40k_army_rule_registry`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `view_40k_army_rule_registry` AS SELECT 
 1 AS `faction_name`,
 1 AS `faction_id`,
 1 AS `army_rule_name`,
 1 AS `army_rule_desc`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `view_40k_army_rules`
--

DROP TABLE IF EXISTS `view_40k_army_rules`;
/*!50001 DROP VIEW IF EXISTS `view_40k_army_rules`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `view_40k_army_rules` AS SELECT 
 1 AS `faction_name`,
 1 AS `faction_id`,
 1 AS `detachment_id`,
 1 AS `detachment_name`,
 1 AS `army_rule_name`,
 1 AS `army_rule_desc`,
 1 AS `detachment_rule_name`,
 1 AS `detachment_rule_desc`*/;
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
 1 AS `detachment_id`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `view_40k_model_stats`
--

DROP TABLE IF EXISTS `view_40k_model_stats`;
/*!50001 DROP VIEW IF EXISTS `view_40k_model_stats`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `view_40k_model_stats` AS SELECT 
 1 AS `datasheet_id`,
 1 AS `Model`,
 1 AS `M`,
 1 AS `T`,
 1 AS `Sv`,
 1 AS `W`,
 1 AS `Ld`,
 1 AS `OC`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `view_40k_stratagems`
--

DROP TABLE IF EXISTS `view_40k_stratagems`;
/*!50001 DROP VIEW IF EXISTS `view_40k_stratagems`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `view_40k_stratagems` AS SELECT 
 1 AS `faction_id`,
 1 AS `clean_det_id`,
 1 AS `name`,
 1 AS `type`,
 1 AS `cp_cost`,
 1 AS `phase`,
 1 AS `description`*/;
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
 1 AS `min_size`,
 1 AS `max_size`*/;
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
-- Temporary view structure for view `view_list_validation_40k`
--

DROP TABLE IF EXISTS `view_list_validation_40k`;
/*!50001 DROP VIEW IF EXISTS `view_list_validation_40k`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `view_list_validation_40k` AS SELECT 
 1 AS `list_id`,
 1 AS `unit_name`,
 1 AS `times_taken`,
 1 AS `faction_status`,
 1 AS `max_allowed`*/;
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
-- Temporary view structure for view `view_master_picker`
--

DROP TABLE IF EXISTS `view_master_picker`;
/*!50001 DROP VIEW IF EXISTS `view_master_picker`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `view_master_picker` AS SELECT 
 1 AS `id`,
 1 AS `name`,
 1 AS `points`,
 1 AS `faction`,
 1 AS `faction_id`,
 1 AS `parent_id`,
 1 AS `game_system`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `view_master_picker_40k`
--

DROP TABLE IF EXISTS `view_master_picker_40k`;
/*!50001 DROP VIEW IF EXISTS `view_master_picker_40k`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `view_master_picker_40k` AS SELECT 
 1 AS `id`,
 1 AS `name`,
 1 AS `points`,
 1 AS `faction`,
 1 AS `faction_id`,
 1 AS `parent_id`,
 1 AS `system`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `view_opr_master_picker`
--

DROP TABLE IF EXISTS `view_opr_master_picker`;
/*!50001 DROP VIEW IF EXISTS `view_opr_master_picker`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `view_opr_master_picker` AS SELECT 
 1 AS `id`,
 1 AS `name`,
 1 AS `faction`,
 1 AS `points`,
 1 AS `QUA`,
 1 AS `DEF`,
 1 AS `size`,
 1 AS `game_system`,
 1 AS `generic_name`*/;
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
-- Temporary view structure for view `view_opr_unit_rules_complete`
--

DROP TABLE IF EXISTS `view_opr_unit_rules_complete`;
/*!50001 DROP VIEW IF EXISTS `view_opr_unit_rules_complete`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `view_opr_unit_rules_complete` AS SELECT 
 1 AS `unit_id`,
 1 AS `rule_name`,
 1 AS `rating`,
 1 AS `description`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `view_opr_unit_rules_detailed`
--

DROP TABLE IF EXISTS `view_opr_unit_rules_detailed`;
/*!50001 DROP VIEW IF EXISTS `view_opr_unit_rules_detailed`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `view_opr_unit_rules_detailed` AS SELECT 
 1 AS `unit_id`,
 1 AS `rule_name`,
 1 AS `rating`,
 1 AS `description`*/;
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
-- Table structure for table `waha_abilities`
--

DROP TABLE IF EXISTS `waha_abilities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `waha_abilities` (
  `id` text,
  `name` text,
  `legend` text,
  `faction_id` text,
  `description` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `waha_datasheet_unit_composition`
--

DROP TABLE IF EXISTS `waha_datasheet_unit_composition`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `waha_datasheet_unit_composition` (
  `datasheet_id` varchar(50) DEFAULT NULL,
  `line_id` int DEFAULT NULL,
  `description` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `waha_datasheets`
--

DROP TABLE IF EXISTS `waha_datasheets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `waha_datasheets` (
  `waha_datasheet_id` varchar(50) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `faction_id` varchar(50) DEFAULT NULL,
  `base_size_text` varchar(100) DEFAULT NULL,
  `points_cost` int DEFAULT NULL,
  `is_character` tinyint(1) DEFAULT '0',
  `is_aircraft` tinyint(1) DEFAULT '0',
  `movement` varchar(20) DEFAULT NULL,
  `toughness` int DEFAULT NULL,
  `save_value` varchar(10) DEFAULT NULL,
  `wounds` int DEFAULT NULL,
  `leadership` int DEFAULT NULL,
  `oc` int DEFAULT NULL,
  `image_url` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`waha_datasheet_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `waha_datasheets_abilities`
--

DROP TABLE IF EXISTS `waha_datasheets_abilities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `waha_datasheets_abilities` (
  `datasheet_id` varchar(50) DEFAULT NULL,
  `line_id` int DEFAULT NULL,
  `ability_id` varchar(50) DEFAULT NULL,
  `model_name` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `description` text,
  `type` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `waha_datasheets_detachment_abilities`
--

DROP TABLE IF EXISTS `waha_datasheets_detachment_abilities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `waha_datasheets_detachment_abilities` (
  `datasheet_id` varchar(50) DEFAULT NULL,
  `detachment_ability_id` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `waha_datasheets_keywords`
--

DROP TABLE IF EXISTS `waha_datasheets_keywords`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `waha_datasheets_keywords` (
  `datasheet_id` varchar(50) DEFAULT NULL,
  `keyword` varchar(100) DEFAULT NULL,
  `model` varchar(100) DEFAULT NULL,
  `is_faction_keyword` tinyint DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `waha_datasheets_leader`
--

DROP TABLE IF EXISTS `waha_datasheets_leader`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `waha_datasheets_leader` (
  `leader_id` varchar(50) DEFAULT NULL,
  `attached_id` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `waha_datasheets_models`
--

DROP TABLE IF EXISTS `waha_datasheets_models`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `waha_datasheets_models` (
  `datasheet_id` varchar(50) DEFAULT NULL,
  `line_id` int DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `movement` varchar(20) DEFAULT NULL,
  `toughness` int DEFAULT NULL,
  `save_value` varchar(10) DEFAULT NULL,
  `inv_sv` varchar(10) DEFAULT NULL,
  `inv_sv_descr` text,
  `wounds` int DEFAULT NULL,
  `leadership` varchar(10) DEFAULT NULL,
  `oc` int DEFAULT NULL,
  `base_size` varchar(100) DEFAULT NULL,
  `base_size_descr` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `waha_datasheets_options`
--

DROP TABLE IF EXISTS `waha_datasheets_options`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `waha_datasheets_options` (
  `datasheet_id` varchar(50) DEFAULT NULL,
  `line_id` int DEFAULT NULL,
  `button_text` varchar(100) DEFAULT NULL,
  `description` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `waha_datasheets_stratagems`
--

DROP TABLE IF EXISTS `waha_datasheets_stratagems`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `waha_datasheets_stratagems` (
  `datasheet_id` varchar(50) DEFAULT NULL,
  `stratagem_id` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `waha_datasheets_wargear`
--

DROP TABLE IF EXISTS `waha_datasheets_wargear`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `waha_datasheets_wargear` (
  `datasheet_id` varchar(50) DEFAULT NULL,
  `line_id` int DEFAULT NULL,
  `line_in_wargear` int DEFAULT NULL,
  `dice` varchar(50) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `description` text,
  `range_val` varchar(50) DEFAULT NULL,
  `type` varchar(100) DEFAULT NULL,
  `attacks` varchar(50) DEFAULT NULL,
  `bs_ws` varchar(50) DEFAULT NULL,
  `strength` varchar(50) DEFAULT NULL,
  `ap` varchar(50) DEFAULT NULL,
  `damage` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `waha_detachment_abilities`
--

DROP TABLE IF EXISTS `waha_detachment_abilities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `waha_detachment_abilities` (
  `id` varchar(50) NOT NULL,
  `faction_id` varchar(50) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `legend` text,
  `description` text,
  `detachment_name` varchar(100) DEFAULT NULL,
  `detachment_id` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `waha_detachments`
--

DROP TABLE IF EXISTS `waha_detachments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `waha_detachments` (
  `id` varchar(50) NOT NULL,
  `faction_id` varchar(50) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `legend` text,
  `type` varchar(100) DEFAULT NULL,
  `rules_summary` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `waha_enhancements`
--

DROP TABLE IF EXISTS `waha_enhancements`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `waha_enhancements` (
  `faction_id` varchar(50) DEFAULT NULL,
  `id` varchar(50) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `cost` int DEFAULT NULL,
  `detachment` varchar(100) DEFAULT NULL,
  `detachment_id` varchar(50) DEFAULT NULL,
  `legend` text,
  `description` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `waha_factions`
--

DROP TABLE IF EXISTS `waha_factions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `waha_factions` (
  `id` varchar(50) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `link` varchar(255) DEFAULT NULL,
  `parent_id` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `waha_keywords`
--

DROP TABLE IF EXISTS `waha_keywords`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `waha_keywords` (
  `id` varchar(50) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `waha_stratagems`
--

DROP TABLE IF EXISTS `waha_stratagems`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `waha_stratagems` (
  `faction_id` varchar(50) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `id` varchar(50) NOT NULL,
  `type` varchar(100) DEFAULT NULL,
  `cp_cost` int DEFAULT NULL,
  `legend` text,
  `turn` varchar(50) DEFAULT NULL,
  `phase` varchar(100) DEFAULT NULL,
  `detachment` varchar(100) DEFAULT NULL,
  `detachment_id` varchar(50) DEFAULT NULL,
  `description` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `waha_weapons`
--

DROP TABLE IF EXISTS `waha_weapons`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `waha_weapons` (
  `weapon_id` varchar(50) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `range_val` varchar(20) DEFAULT NULL,
  `attacks_val` varchar(20) DEFAULT NULL,
  `strength_val` int DEFAULT NULL,
  `ap_val` int DEFAULT NULL,
  `damage_val` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`weapon_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Final view structure for view `view_40k_army_rule_registry`
--

/*!50001 DROP VIEW IF EXISTS `view_40k_army_rule_registry`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `view_40k_army_rule_registry` AS select distinct `f`.`name` AS `faction_name`,`f`.`id` AS `faction_id`,`a`.`name` AS `army_rule_name`,`a`.`description` AS `army_rule_desc` from (((`waha_factions` `f` join `waha_datasheets` `d` on((`d`.`faction_id` = `f`.`id`))) join `waha_datasheets_abilities` `da` on((`da`.`datasheet_id` = `d`.`waha_datasheet_id`))) join `waha_abilities` `a` on((`da`.`ability_id` = `a`.`id`))) where (`da`.`type` = 'Faction') */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `view_40k_army_rules`
--

/*!50001 DROP VIEW IF EXISTS `view_40k_army_rules`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `view_40k_army_rules` AS select `f`.`name` AS `faction_name`,`f`.`id` AS `faction_id`,`d`.`id` AS `detachment_id`,`d`.`name` AS `detachment_name`,`ar`.`name` AS `army_rule_name`,`ar`.`description` AS `army_rule_desc`,`da`.`name` AS `detachment_rule_name`,`da`.`description` AS `detachment_rule_desc` from (((`waha_factions` `f` join `waha_detachments` `d` on((`f`.`id` = `d`.`faction_id`))) left join `waha_abilities` `ar` on(((`ar`.`faction_id` = `f`.`id`) and (`ar`.`name` in ('Oath of Moment','Waaagh!','Dark Pacts','Synapse','Acts of Faith','Nurgle\'s Gift','Blessings of Khorne','Power from Pain'))))) left join `waha_detachment_abilities` `da` on((`da`.`detachment_id` = `d`.`id`))) */;
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
/*!50001 VIEW `view_40k_enhancement_picker` AS select `waha_enhancements`.`id` AS `enhancement_id`,`waha_enhancements`.`name` AS `enhancement_name`,`waha_enhancements`.`cost` AS `cost`,`waha_enhancements`.`description` AS `description`,`waha_enhancements`.`detachment_id` AS `detachment_id` from `waha_enhancements` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `view_40k_model_stats`
--

/*!50001 DROP VIEW IF EXISTS `view_40k_model_stats`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `view_40k_model_stats` AS select `waha_datasheets_models`.`datasheet_id` AS `datasheet_id`,`waha_datasheets_models`.`name` AS `Model`,`waha_datasheets_models`.`movement` AS `M`,`waha_datasheets_models`.`toughness` AS `T`,`waha_datasheets_models`.`save_value` AS `Sv`,`waha_datasheets_models`.`wounds` AS `W`,`waha_datasheets_models`.`leadership` AS `Ld`,`waha_datasheets_models`.`oc` AS `OC` from `waha_datasheets_models` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `view_40k_stratagems`
--

/*!50001 DROP VIEW IF EXISTS `view_40k_stratagems`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `view_40k_stratagems` AS select `waha_stratagems`.`faction_id` AS `faction_id`,cast(`waha_stratagems`.`detachment_id` as unsigned) AS `clean_det_id`,`waha_stratagems`.`name` AS `name`,`waha_stratagems`.`type` AS `type`,`waha_stratagems`.`cp_cost` AS `cp_cost`,`waha_stratagems`.`phase` AS `phase`,`waha_stratagems`.`description` AS `description` from `waha_stratagems` */;
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
/*!50001 VIEW `view_40k_unit_composition` AS with `cleandata` as (select `waha_datasheet_unit_composition`.`datasheet_id` AS `datasheet_id`,`waha_datasheet_unit_composition`.`line_id` AS `line_id`,cast(regexp_substr(`waha_datasheet_unit_composition`.`description`,'[0-9]+') as unsigned) AS `line_min`,cast(regexp_replace(regexp_substr(`waha_datasheet_unit_composition`.`description`,'[0-9]+-[0-9]+|[0-9]+'),'.*-','') as unsigned) AS `line_max` from `waha_datasheet_unit_composition`) select `cleandata`.`datasheet_id` AS `datasheet_id`,sum(`cleandata`.`line_min`) AS `min_size`,sum(`cleandata`.`line_max`) AS `max_size` from `cleandata` group by `cleandata`.`datasheet_id` */;
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
/*!50001 VIEW `view_list_validation_40k` AS select `e`.`list_id` AS `list_id`,`d`.`name` AS `unit_name`,count(`e`.`unit_id`) AS `times_taken`,(case when (`f`.`name` in ('Imperial Agents','Imperial Knights','Chaos Daemons','Chaos Knights')) then 'Ally' when exists(select 1 from `waha_datasheets_keywords` `dk` where ((`dk`.`datasheet_id` = `d`.`waha_datasheet_id`) and (`dk`.`is_faction_keyword` = 1) and (`dk`.`keyword` not in (`l`.`faction_primary`,'Adeptus Astartes','Imperium','Chaos')))) then 'INVALID' when (`f`.`name` = `l`.`faction_primary`) then 'Valid' else 'INVALID' end) AS `faction_status`,(case when exists(select 1 from `waha_datasheets_keywords` `dk` where ((`dk`.`datasheet_id` = `d`.`waha_datasheet_id`) and (`dk`.`keyword` = 'Epic Hero'))) then 1 when exists(select 1 from `waha_datasheets_keywords` `dk` where ((`dk`.`datasheet_id` = `d`.`waha_datasheet_id`) and (`dk`.`keyword` = 'Battleline'))) then 6 else 3 end) AS `max_allowed` from (((`play_armylist_entries` `e` join `play_armylists` `l` on((`e`.`list_id` = `l`.`list_id`))) join `waha_datasheets` `d` on((`e`.`unit_id` = `d`.`waha_datasheet_id`))) join `waha_factions` `f` on((`d`.`faction_id` = `f`.`id`))) group by `e`.`list_id`,`e`.`unit_id`,`d`.`name`,`f`.`name`,`l`.`faction_primary` */;
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
/*!50001 VIEW `view_master_picker` AS select `d`.`waha_datasheet_id` AS `id`,`d`.`name` AS `name`,`d`.`points_cost` AS `points`,`f`.`name` AS `faction`,`f`.`id` AS `faction_id`,`f`.`parent_id` AS `parent_id`,'40K' AS `game_system` from (`waha_datasheets` `d` join `waha_factions` `f` on((`d`.`faction_id` = `f`.`id`))) union all select `o`.`opr_unit_id` AS `id`,`o`.`name` AS `name`,`o`.`base_cost` AS `points`,`o`.`army` AS `faction`,NULL AS `faction_id`,NULL AS `parent_id`,'OPR' AS `game_system` from `opr_units` `o` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `view_master_picker_40k`
--

/*!50001 DROP VIEW IF EXISTS `view_master_picker_40k`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `view_master_picker_40k` AS select `d`.`waha_datasheet_id` AS `id`,`d`.`name` AS `name`,`d`.`points_cost` AS `points`,`f`.`name` AS `faction`,`f`.`id` AS `faction_id`,`f`.`parent_id` AS `parent_id`,'40K' AS `system` from (`waha_datasheets` `d` join `waha_factions` `f` on((`d`.`faction_id` = `f`.`id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `view_opr_master_picker`
--

/*!50001 DROP VIEW IF EXISTS `view_opr_master_picker`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `view_opr_master_picker` AS select `opr_units`.`opr_unit_id` AS `id`,`opr_units`.`name` AS `name`,`opr_units`.`army` AS `faction`,`opr_units`.`base_cost` AS `points`,`opr_units`.`quality` AS `QUA`,`opr_units`.`defense` AS `DEF`,`opr_units`.`size` AS `size`,`opr_units`.`game_system` AS `game_system`,`opr_units`.`generic_name` AS `generic_name` from `opr_units` */;
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
-- Final view structure for view `view_opr_unit_rules_complete`
--

/*!50001 DROP VIEW IF EXISTS `view_opr_unit_rules_complete`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `view_opr_unit_rules_complete` AS select `ur`.`unit_id` AS `unit_id`,`ur`.`label` AS `rule_name`,`ur`.`rating` AS `rating`,`sr`.`description` AS `description` from (`opr_unitrules` `ur` left join `opr_specialrules` `sr` on((`ur`.`label` = `sr`.`name`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `view_opr_unit_rules_detailed`
--

/*!50001 DROP VIEW IF EXISTS `view_opr_unit_rules_detailed`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `view_opr_unit_rules_detailed` AS select `ur`.`unit_id` AS `unit_id`,`ur`.`label` AS `rule_name`,`ur`.`rating` AS `rating`,`sr`.`description` AS `description` from (`opr_unitrules` `ur` left join `opr_specialrules` `sr` on((`ur`.`label` = `sr`.`name`))) */;
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
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-02-16 22:28:53
