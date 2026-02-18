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
  `faction_secondary` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`list_id`),
  KEY `waha_detachment_id` (`waha_detachment_id`),
  KEY `primary_recipe_id` (`primary_recipe_id`),
  CONSTRAINT `play_armylists_ibfk_1` FOREIGN KEY (`waha_detachment_id`) REFERENCES `waha_detachments` (`id`),
  CONSTRAINT `play_armylists_ibfk_2` FOREIGN KEY (`primary_recipe_id`) REFERENCES `inv_paint_recipes` (`recipe_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `play_armylists`
--

LOCK TABLES `play_armylists` WRITE;
/*!40000 ALTER TABLE `play_armylists` DISABLE KEYS */;
INSERT INTO `play_armylists` VALUES (1,'Gork’s Grin','40K_10E',2000,'852',NULL,0,'Orks',NULL),(2,'Troll Stomp','OPR',750,NULL,NULL,0,'Alien Hives',NULL),(3,'test Marines','40K_10E',2000,'1092',NULL,0,'Space Marines',NULL),(4,'BattleBros Test','OPR',2000,NULL,NULL,0,'Battle Brothers',NULL);
/*!40000 ALTER TABLE `play_armylists` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-02-12  2:03:34
