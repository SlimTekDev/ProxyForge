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
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `play_armylist_entries`
--

LOCK TABLES `play_armylist_entries` WRITE;
/*!40000 ALTER TABLE `play_armylist_entries` DISABLE KEYS */;
INSERT INTO `play_armylist_entries` VALUES (2,2,'__kWeE8',3),(12,2,'aTxCHqz',1),(16,1,'16',1),(17,1,'2494',1),(18,2,'lmZtl0E',1),(19,3,'103',1),(20,3,'1178',1),(21,3,'103',1),(23,1,'1',1),(24,1,'1',1),(25,1,'16',1),(32,1,'10',1),(44,1,'10',1),(45,1,'1',1),(46,1,'1',1),(47,1,'1',1),(48,4,'02PM2Nk',1),(49,4,'y59VWP0',1),(50,4,'Ov5Z8wE',1);
/*!40000 ALTER TABLE `play_armylist_entries` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-02-12  2:03:36
