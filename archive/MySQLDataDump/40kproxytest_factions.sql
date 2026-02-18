-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: localhost    Database: 40kproxytest
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
-- Table structure for table `factions`
--

DROP TABLE IF EXISTS `factions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `factions` (
  `id` text,
  `name` text,
  `link` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `factions`
--

LOCK TABLES `factions` WRITE;
/*!40000 ALTER TABLE `factions` DISABLE KEYS */;
INSERT INTO `factions` VALUES ('AoI','Imperial Agents','https://wahapedia.ru/wh40k10ed/factions/imperial-agents'),('AM','Astra Militarum','https://wahapedia.ru/wh40k10ed/factions/astra-militarum'),('GC','Genestealer Cults','https://wahapedia.ru/wh40k10ed/factions/genestealer-cults'),('NEC','Necrons','https://wahapedia.ru/wh40k10ed/factions/necrons'),('AE','Aeldari','https://wahapedia.ru/wh40k10ed/factions/aeldari'),('TL','Adeptus Titanicus','https://wahapedia.ru/wh40k10ed/factions/adeptus-titanicus'),('ORK','Orks','https://wahapedia.ru/wh40k10ed/factions/orks'),('UN','Unaligned Forces','https://wahapedia.ru/wh40k10ed/factions/unaligned-forces'),('GK','Grey Knights','https://wahapedia.ru/wh40k10ed/factions/grey-knights'),('TAU','Tâ€™au Empire','https://wahapedia.ru/wh40k10ed/factions/t-au-empire'),('LoV','Leagues of Votann','https://wahapedia.ru/wh40k10ed/factions/leagues-of-votann'),('AdM','Adeptus Mechanicus','https://wahapedia.ru/wh40k10ed/factions/adeptus-mechanicus'),('TS','Thousand Sons','https://wahapedia.ru/wh40k10ed/factions/thousand-sons'),('DG','Death Guard','https://wahapedia.ru/wh40k10ed/factions/death-guard'),('EC','Emperorâ€™s Children','https://wahapedia.ru/wh40k10ed/factions/emperor-s-children'),('WE','World Eaters','https://wahapedia.ru/wh40k10ed/factions/world-eaters'),('QT','Chaos Knights','https://wahapedia.ru/wh40k10ed/factions/chaos-knights'),('CD','Chaos Daemons','https://wahapedia.ru/wh40k10ed/factions/chaos-daemons'),('QI','Imperial Knights','https://wahapedia.ru/wh40k10ed/factions/imperial-knights'),('SM','Space Marines','https://wahapedia.ru/wh40k10ed/factions/space-marines'),('TYR','Tyranids','https://wahapedia.ru/wh40k10ed/factions/tyranids'),('AC','Adeptus Custodes','https://wahapedia.ru/wh40k10ed/factions/adeptus-custodes'),('AS','Adepta Sororitas','https://wahapedia.ru/wh40k10ed/factions/adepta-sororitas'),('CSM','Chaos Space Marines','https://wahapedia.ru/wh40k10ed/factions/chaos-space-marines'),('DRU','Drukhari','https://wahapedia.ru/wh40k10ed/factions/drukhari'),('UA','Unbound Adversaries','https://wahapedia.ru/wh40k10ed/factions/unbound-adversaries');
/*!40000 ALTER TABLE `factions` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-01-21 18:17:54
