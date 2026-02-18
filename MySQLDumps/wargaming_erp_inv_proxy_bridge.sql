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
-- Dumping data for table `inv_proxy_bridge`
--

LOCK TABLES `inv_proxy_bridge` WRITE;
/*!40000 ALTER TABLE `inv_proxy_bridge` DISABLE KEYS */;
/*!40000 ALTER TABLE `inv_proxy_bridge` ENABLE KEYS */;
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
