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
-- Dumping data for table `opr_specialrules`
--

LOCK TABLES `opr_specialrules` WRITE;
/*!40000 ALTER TABLE `opr_specialrules` DISABLE KEYS */;
INSERT INTO `opr_specialrules` VALUES ('_e_W3SrBy5Ol','Sever',''),('_Hxx9p4FkvUn','Drakesworn',NULL),('_mrPya5SXSqW','Deadly',''),('_RzAw7HP5Uet','Traversal',NULL),('-7w3e1QuLK47','Destroyer',NULL),('-QJdqJEKjIpE','Flying',NULL),('09_5wJQE8j1s','Vale Formation',NULL),('09SoiR1HuW7u','Precise',''),('0ia0aPl7hE0t','Exotic Gear',NULL),('0TfnG5G4JEv0','Ignores Regeneration',''),('0Z-OGtDpajc3','Grounded Stealth',NULL),('0Za4ptEWX5hx','Rapid Ambush',NULL),('17crjK7P6_w6','AP',''),('1qiGNqpxKb24','Disintegrate',''),('21dbpSjSDeOY','Clan Warrior',NULL),('2atvlmICQSCV','Fearless',NULL),('2naIlnOv22Ls','Safety Gear',NULL),('2Ut-u9mj5a2t','Vinci Tech',NULL),('2xUH_d7T_Zfv','Harassing',NULL),('2Y_Spjz69MSD','Smash',''),('3FeiOe3krHMa','Aircraft',NULL),('47CAqf7ySlfc','Caster',NULL),('4A7GJdKMoa5t','Slam',''),('4mB0rwGnMVgJ','Changebound',NULL),('4rzxsYvWU9Ge','Wild Veil',NULL),('58bWJyFqRsC3','Union Assault',NULL),('5bc5xNmd5M14','Highborn',NULL),('5v6oaGfrdf29','Surge',''),('5vuGWmPx1aUb','Brutal Fighter',NULL),('5Wpo74lRNhqB','Counter-Attack',NULL),('62-mYKVM9MLd','Impact',NULL),('6EBrtUCjjYPT','Bloodthirsty Fighter',NULL),('6eS0HjIE1HvP','Chop',''),('6mJw5IdqSqNC','Ambush',NULL),('6sMud5j7l3M5','Slash',''),('741uN_Qma5mL','Battleborn',NULL),('7F4391rzKx2g','Shatter',''),('8bJGX_UrPh44','Crossing Barrage',NULL),('8Ck9GAwUK824','Indirect',''),('8Hjy54TYtwb7','Takedown',''),('8KujvrTG8k9p','Regeneration',NULL),('9_lez8f1QHeD','Lucky',NULL),('9042COVrLCsI','Limited',''),('99DXMN96LnI8','Surprise Attack',NULL),('9jyvRoBODD-O','Stealth',NULL),('9NrhGurKS7I8','Gloom-Mist',NULL),('9Te72f48wJyw','Versatile Attack',NULL),('9VqfvG_MRyiX','Break',''),('a0YtInGiUDd6','Tough',NULL),('a467r6cU8RF6','Raider',NULL),('AlIZbh-afBYi','Protected',NULL),('aogQZcOOQrDI','Transport',NULL),('B1i8BBWNU3L0','Ferocious Boost',NULL),('B2JtpsnBmE7N','Empyrean Spirit',NULL),('bcByy3kGe34w','Ethereal',NULL),('bjt7_iCtmOK7','Good Shot',NULL),('c45Fw0D2oGOk','Counter',''),('C6MzEy1CnxTs','Repel Ambushers',NULL),('cavWDboL4ubs','Rending',''),('CCShas9-9K4N','Surprise Piercing Shot',NULL),('cgCroTrOmiv-','Hive Bond',NULL),('CGuO0Zpk-mV1','Skewer',''),('cygZBh3MtWs1','Ferocious',NULL),('d-XfZkibjyi-','Crazed',NULL),('D7ChSWl5R2We','Guardian',NULL),('DD6gAWjz801s','Rupture',''),('DEeVIJcfNfS6','Unpredictable Fighter',NULL),('df-9jrAw7ytM','Shadowborn',NULL),('DhLjIDRrWz6-','Piercing Assault',NULL),('dIQ3SGl2J2Ew','Fear',NULL),('djJahpu0Ciut','Infiltrate',NULL),('EgdF_3MSddXR','Melee Evasion',NULL),('eOGs64JpVsP3','Unpredictable Shooter',NULL),('eyMkgYDVrP7C','Takedown Strike',NULL),('F_1wfmpAyYwT','Self-Destruct',NULL),('f1xiOutM7xXQ','Ossified',NULL),('FAMbscK5vhSu','Scout',NULL),('fHg1uKwkuiBP','Breath Attack',NULL),('FuarMsrD8uVi','Perforate',''),('FZLk0-3ci6jI','Martial Prowess',NULL),('gD2_znglqhNw','Sturdy',NULL),('gnpURIvLqjw9','Devout',NULL),('GRuFoZiyjY5f','Artillery',NULL),('gvBWuZ-vGMnJ','Scratch',''),('gVRt_wk8DktW','Hazardous',''),('gzKDP8xc6MCQ','Fanatic',NULL),('h_TEDAiM7Cy-','Buccaneer',NULL),('h-Cj1XrX00JE','Resistance',NULL),('H9E9PIWpGRdw','Relentless',NULL),('h9JsgD38BRjI','Bounding',NULL),('haWppj0rUxS8','Badlands Hunter',NULL),('Hdm9ry6kJvzb','Strafing',''),('hjaNnUHsY3f5','Targeting Visor',NULL),('HmDYt1eQUL2f','Puncture',''),('hnsVQyx3ylMf','Ravage',NULL),('htvMlDrYyL3x','Casting Debuff',NULL),('HWtnPV9LQF1D','Immobile',NULL),('i40cKJoXJ7zm','Unpredictable',NULL),('IEJp3a4vE0CB','Shred',''),('IyLY1212wacW','Fortified',NULL),('iZkU-vhbjhbb','Watchborn',NULL),('J219U0OD6JiN','Unmovable',NULL),('jaDijWTHmVNU','Split',NULL),('jbhpErfecvEY','Warbound',NULL),('jgyVEAzjbDDh','Infected',NULL),('JoOCVPx1xT1G','Furious',NULL),('JSKVyurtWIyW','Strider',NULL),('JSnFcm3SCiMD','Crack',''),('jyVvnNyAKS-8','Ballistic Vest',NULL),('KdgwlPb8LuD2','Fast',NULL),('KEQ9ZE6RPJp7','Bestial',NULL),('Ldhtmr4H8b6G','Slow',NULL),('LtPyHi_-DHf4','Teleport',NULL),('Lz_ncVgCX5R8','Knightborn',NULL),('mCYGI3sU3jKI','Angelic Blessing',NULL),('mxQ1fCGgPccn','Berserker',NULL),('N0JRcI01vSBT','Deathstrike',NULL),('Naqc5mga9Uha','Bane',''),('NEYp25CGvZl3','Scurry',NULL),('nLQCr5OiSlYz','Caster Group',NULL),('NVBNprYibLJn','Demolish',''),('Ny2MXltMVejS','Royal Legion',NULL),('O_sf2rsHA7rD','Evasive',NULL),('O_wrvW7FiJWX','Plaguebound',NULL),('O2Cd7OibBBA5','No Retreat',NULL),('O5Lcg0FfiPi0','Fracture',''),('oHdve7tknk27','Reap',''),('oqBDibATsWC3','Wreck',''),('ozCLWcof36wD','Hit & Run',NULL),('paOPFddMOffa','Crossing Attack',NULL),('PBP94ujaST4y','Primal',NULL),('QjUvdTBYv0Nd','Darkborn',NULL),('qNNjE6aa9YQ2','Bad Shot',NULL),('qskF5Gm5pMV0','Point-Blank Surge',NULL),('QXyt-zV_bjpg','Unstoppable',''),('rblJ2IkYaFon','Mischievous',NULL),('Rjmkg_tuRv7C','Fragment',''),('rMIqZuIjiy1e','Cursed Undead',NULL),('rqBYj1yANC3J','Unique',NULL),('RSVMS71PNbZF','Honor Code',NULL),('s5A-Pvdby0wT','Cyber-Eyes',NULL),('S8IZt-d0Sgwk','Machine-Fog',NULL),('sCmjgdwkLiGT','Predator Fighter',NULL),('Sdcb8VAeTxji','Hold the Line',NULL),('sGmLaPbLpSvT','Inquisitorial Agent',NULL),('SHjROxMxvQFd','Guerrilla',NULL),('SPhAaWwefTmH','Wave-Step',NULL),('SqhSkyNcexeN','Psychotic',NULL),('swmJMClW7ilS','Reinforced',NULL),('sZAknIp66cEU','Thrash',''),('T08VkBuVmNZ_','Hero',NULL),('tidpe1mTXb9W','Scrapper',NULL),('tnQNmp4_8qjK','Decimate',''),('TTL5RNmwotoh','Melee Slayer',NULL),('Uf2ntJ7kbyRW','Royal Warrior',NULL),('UJ6frPcu1X9m','Rapid Blink',NULL),('umbiz4tnEyF8','Thrust',''),('UXo89u7JIIGL','Warden',NULL),('vFppagDdH3Vl','Regenerative Strength',NULL),('vfW0pVMUrKQr','Wolfborn',NULL),('VI54cszY2BuG','Destructive',''),('w_vX0mi58KKt','Blast',''),('W2-YAUebkXqF','Psychotic Boost',NULL),('w7sENXkksVpG','Devout Boost',NULL),('WcOMD7QgPYXZ','Lacerate',''),('wjTOj41tskFD','Havocbound',NULL),('WKjwnFHqzZ5_','Bash',''),('WNMH1ZiQXSz-','Spell Conduit',NULL),('wsqfB0fq69eG','Shielded',NULL),('x0gFQEwammM_','Battle-Hardened',NULL),('x7chGZmjk8Os','Quick Readjustment',NULL),('xbo_cAvhX-AA','Quake',''),('xE_oCeOaFhT0','Pierce',''),('xeJDKejG4QZN','Tear',''),('xgtq7JJUEwfA','Shadow Operative',NULL),('xmFm9FEnT4Ne','Pulverize',''),('xpz_j0Y8jYOq','Savage',NULL),('xsRmviNFV5c0','Good Fighter',NULL),('XUtLjcGZG6Vn','Tenacious',NULL),('Y_WeXWwLtX6z','Self-Repair',NULL),('YGZRhloGzuHL','Purge',''),('YidAUK2jOH-4','Brute Courage',NULL),('yis0utoPMclv','Lustbound',NULL),('ykPufsAeq8Kw','Quick Shot',NULL),('ypbYeykEKH3C','Bloodborn',NULL),('YtzjP0K3sIAh','Mobile Artillery',NULL),('Ywz0UdkamH-k','Runner',NULL),('ZEZvFOGSAw4H','Butcher',''),('zTfg9msVpfJ0','Guarded',NULL),('zVconc6Qb-g9','Heavy Impact',NULL),('Zx4mWN0SbmK8','Reliable','');
/*!40000 ALTER TABLE `opr_specialrules` ENABLE KEYS */;
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
