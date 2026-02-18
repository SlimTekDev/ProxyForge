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
-- Dumping data for table `opr_army_settings`
--

LOCK TABLES `opr_army_settings` WRITE;
/*!40000 ALTER TABLE `opr_army_settings` DISABLE KEYS */;
INSERT INTO `opr_army_settings` VALUES ('Alien Hives','Grimdark Future'),('Badland Nomads','Grimdark Future Firefight'),('Battle Brothers','Grimdark Future'),('Beastmen','Age Of Fantasy'),('Berserker Clans','Grimdark Future Firefight'),('Blessed Sisters','Grimdark Future'),('Blood Brothers','Grimdark Future'),('Blood Prime Brothers','Grimdark Future'),('Brute Clans','Age Of Fantasy Skirmish'),('Brute Coalitions','Grimdark Future Firefight'),('Change Disciples','Grimdark Future'),('Chivalrous Kingdoms','Age Of Fantasy'),('City Runners','Grimdark Future Firefight'),('Crazed Zealots','Age Of Fantasy Skirmish'),('Custodian Brothers','Grimdark Future'),('DAO Union','Grimdark Future'),('Dark Brothers','Grimdark Future'),('Dark Elf Raiders','Grimdark Future'),('Dark Elves','Age Of Fantasy'),('Dark Prime Brothers','Grimdark Future'),('Deep-Sea Elves','Age Of Fantasy'),('Dragon Empire','Age Of Fantasy'),('Duchies of Vinci','Age Of Fantasy'),('Dwarf Guilds','Grimdark Future'),('Dwarves','Age Of Fantasy'),('Elven Jesters','Grimdark Future'),('Eternal Dynasty','Grimdark Future'),('Eternal Wardens','Age Of Fantasy'),('Furious Tribes','Age Of Fantasy Skirmish'),('Ghostly Undead','Age Of Fantasy'),('Giant Tribes','Age Of Fantasy'),('Goblin Reclaimers','Grimdark Future'),('Goblins','Age Of Fantasy'),('Halflings','Age Of Fantasy'),('Havoc Brothers','Grimdark Future'),('Havoc Dwarves','Age Of Fantasy'),('Havoc Warriors','Age Of Fantasy'),('Hidden Syndicates','Age Of Fantasy Skirmish'),('High Elf Fleets','Grimdark Future'),('High Elves','Age Of Fantasy'),('Hired Guards','Age Of Fantasy Skirmish'),('Human Defense Force','Grimdark Future'),('Human Empire','Age Of Fantasy'),('Human Inquisition','Grimdark Future'),('Infected Colonies','Grimdark Future'),('Jackals','Grimdark Future'),('Kingdom of Angels','Age Of Fantasy'),('Knight Brothers','Grimdark Future'),('Knight Prime Brothers','Grimdark Future'),('Lust Disciples','Grimdark Future'),('Machine Cult','Grimdark Future'),('Mega-Corps','Grimdark Future Firefight'),('Mercenaries','Grimdark Future Firefight'),('Merchant Unions','Age Of Fantasy Skirmish'),('Mummified Undead','Age Of Fantasy'),('Ogres','Age Of Fantasy'),('Orc Marauders','Grimdark Future'),('Orcs','Age Of Fantasy'),('Ossified Undead','Age Of Fantasy'),('Outskirt Raiders','Age Of Fantasy Skirmish'),('Plague Disciples','Grimdark Future'),('Prime Brothers','Grimdark Future'),('Psycho Cults','Grimdark Future Firefight'),('Ratmen','Age Of Fantasy'),('Ratmen Clans','Grimdark Future'),('Rebel Guerrillas','Grimdark Future'),('Rift Daemons of Change','Age Of Fantasy'),('Rift Daemons of Lust','Age Of Fantasy'),('Rift Daemons of Plague','Age Of Fantasy'),('Rift Daemons of War','Age Of Fantasy'),('Robot Legions','Grimdark Future'),('Saurian Starhost','Grimdark Future'),('Saurians','Age Of Fantasy'),('Security Forces','Grimdark Future Firefight'),('Shadow Leagues','Grimdark Future Firefight'),('Shadow Stalkers','Age Of Fantasy'),('Shortling Alliances','Age Of Fantasy Skirmish'),('Shortling Federations','Grimdark Future Firefight'),('Sky-City Dwarves','Age Of Fantasy'),('Soul-Snatcher Cults','Grimdark Future'),('Titan Lords','Grimdark Future'),('Trade Federations','Age Of Fantasy Skirmish'),('Treasure Hunters','Age Of Fantasy Skirmish'),('Vampiric Undead','Age Of Fantasy'),('Volcanic Dwarves','Age Of Fantasy'),('War Disciples','Grimdark Future'),('Watch Brothers','Grimdark Future'),('Watch Prime Brothers','Grimdark Future'),('Wolf Brothers','Grimdark Future'),('Wolf Prime Brothers','Grimdark Future'),('Wood Elves','Age Of Fantasy'),('Worker Unions','Grimdark Future Firefight'),('Wormhole Daemons of Change','Grimdark Future'),('Wormhole Daemons of Lust','Grimdark Future'),('Wormhole Daemons of Plague','Grimdark Future'),('Wormhole Daemons of War','Grimdark Future');
/*!40000 ALTER TABLE `opr_army_settings` ENABLE KEYS */;
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
