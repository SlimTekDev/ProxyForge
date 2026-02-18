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
-- Dumping data for table `waha_factions`
--

LOCK TABLES `waha_factions` WRITE;
/*!40000 ALTER TABLE `waha_factions` DISABLE KEYS */;
INSERT INTO `waha_factions` VALUES ('0',NULL,NULL,NULL),('AC','Adeptus Custodes','https://wahapedia.ru/wh40k10ed/factions/adeptus-custodes',NULL),('AdM','Adeptus Mechanicus','https://wahapedia.ru/wh40k10ed/factions/adeptus-mechanicus',NULL),('AE','Aeldari','https://wahapedia.ru/wh40k10ed/factions/aeldari',NULL),('AM','Astra Militarum','https://wahapedia.ru/wh40k10ed/factions/astra-militarum',NULL),('AoI','Imperial Agents','https://wahapedia.ru/wh40k10ed/factions/imperial-agents',NULL),('AS','Adepta Sororitas','https://wahapedia.ru/wh40k10ed/factions/adepta-sororitas',NULL),('CD','Chaos Daemons','https://wahapedia.ru/wh40k10ed/factions/chaos-daemons',NULL),('CSM','Chaos Space Marines','https://wahapedia.ru/wh40k10ed/factions/chaos-space-marines',NULL),('DG','Death Guard','https://wahapedia.ru/wh40k10ed/factions/death-guard','CSM'),('DRU','Drukhari','https://wahapedia.ru/wh40k10ed/factions/drukhari',NULL),('EC','Emperors Children','https://wahapedia.ru/wh40k10ed/factions/emperor-s-children',NULL),('GC','Genestealer Cults','https://wahapedia.ru/wh40k10ed/factions/genestealer-cults',NULL),('GK','Grey Knights','https://wahapedia.ru/wh40k10ed/factions/grey-knights',NULL),('LoV','Leagues of Votann','https://wahapedia.ru/wh40k10ed/factions/leagues-of-votann',NULL),('NEC','Necrons','https://wahapedia.ru/wh40k10ed/factions/necrons',NULL),('ORK','Orks','https://wahapedia.ru/wh40k10ed/factions/orks',NULL),('QI','Imperial Knights','https://wahapedia.ru/wh40k10ed/factions/imperial-knights',NULL),('QT','Chaos Knights','https://wahapedia.ru/wh40k10ed/factions/chaos-knights',NULL),('SM','Space Marines','https://wahapedia.ru/wh40k10ed/factions/space-marines',NULL),('TAU','Tau Empire','https://wahapedia.ru/wh40k10ed/factions/t-au-empire',NULL),('TL','Adeptus Titanicus','https://wahapedia.ru/wh40k10ed/factions/adeptus-titanicus',NULL),('TS','Thousand Sons','https://wahapedia.ru/wh40k10ed/factions/thousand-sons','CSM'),('TYR','Tyranids','https://wahapedia.ru/wh40k10ed/factions/tyranids',NULL),('UA','Unbound Adversaries','https://wahapedia.ru/wh40k10ed/factions/unbound-adversaries',NULL),('UN','Unaligned Forces','https://wahapedia.ru/wh40k10ed/factions/unaligned-forces',NULL),('WE','World Eaters','https://wahapedia.ru/wh40k10ed/factions/world-eaters','CSM');
/*!40000 ALTER TABLE `waha_factions` ENABLE KEYS */;
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
