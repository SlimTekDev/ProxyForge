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
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `play_armylist_wargear_selections`
--

LOCK TABLES `play_armylist_wargear_selections` WRITE;
/*!40000 ALTER TABLE `play_armylist_wargear_selections` DISABLE KEYS */;
INSERT INTO `play_armylist_wargear_selections` VALUES (6,16,'Equipment -> close combat weapon',1),(7,16,'The Boss Nobs big choppa can be replaced with 1 power klaw.',1),(8,16,'The Boss Nobs big choppa and slugga can be replaced with 1 kombi-weapon and 1 close combat weapon.',1),(9,16,'Any number of Boyz can each have their slugga and choppa replaced with 1 shoota and 1 close combat weapon.',1),(10,23,'This models big choppa can be replaced with 1 power klaw.',1),(11,24,'This model can be equipped with 1 attack squig.',1),(12,23,'This model can be equipped with 1 attack squig.',1);
/*!40000 ALTER TABLE `play_armylist_wargear_selections` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-02-12  2:03:35
