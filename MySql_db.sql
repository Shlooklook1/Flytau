CREATE DATABASE  IF NOT EXISTS `flytau` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `flytau`;
-- MySQL dump 10.13  Distrib 8.0.30, for Win64 (x86_64)
--
-- Host: localhost    Database: flytau
-- ------------------------------------------------------
-- Server version	8.0.30

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
-- Table structure for table `air_crew`
--

DROP TABLE IF EXISTS `air_crew`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `air_crew` (
  `id` varchar(45) NOT NULL,
  `first_name` varchar(45) DEFAULT NULL,
  `last_name` varchar(45) DEFAULT NULL,
  `phone_number` varchar(45) DEFAULT NULL,
  `hire_date` varchar(45) DEFAULT NULL,
  `city` varchar(45) DEFAULT NULL,
  `street` varchar(45) DEFAULT NULL,
  `house_number` varchar(45) DEFAULT NULL,
  `role` enum('Pilot','Flight attendant') NOT NULL,
  `long_flight_certificate` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `air_crew`
--

LOCK TABLES `air_crew` WRITE;
/*!40000 ALTER TABLE `air_crew` DISABLE KEYS */;
INSERT INTO `air_crew` VALUES ('301','Danny','Pilot',NULL,'2019-01-01',NULL,NULL,NULL,'Pilot',1),('302','Ron','Sky',NULL,'2019-01-01',NULL,NULL,NULL,'Pilot',1),('303','Gal','Flyer',NULL,'2019-01-01',NULL,NULL,NULL,'Pilot',1),('304','Tal','Aviv',NULL,'2019-01-01',NULL,NULL,NULL,'Pilot',1),('305','Shai','Rom',NULL,'2019-01-01',NULL,NULL,NULL,'Pilot',1),('306','Miri','Cohen',NULL,'2019-01-01',NULL,NULL,NULL,'Pilot',1),('307','Eli','Levi',NULL,'2019-01-01',NULL,NULL,NULL,'Pilot',1),('308','Noa','Kopter',NULL,'2019-01-01',NULL,NULL,NULL,'Pilot',1),('309','Avi','Bar',NULL,'2019-01-01',NULL,NULL,NULL,'Pilot',1),('310','Yoni','Ron',NULL,'2019-01-01',NULL,NULL,NULL,'Pilot',1),('401','Dalia','Dayal',NULL,'2020-01-01',NULL,NULL,NULL,'Flight attendant',1),('402','Dana','Serve',NULL,'2020-01-01',NULL,NULL,NULL,'Flight attendant',1),('403','Rina','Help',NULL,'2020-01-01',NULL,NULL,NULL,'Flight attendant',1),('404','Yossi','Tray',NULL,'2020-01-01',NULL,NULL,NULL,'Flight attendant',1),('405','Michal','Seat',NULL,'2020-01-01',NULL,NULL,NULL,'Flight attendant',1),('406','Keren','Water',NULL,'2020-01-01',NULL,NULL,NULL,'Flight attendant',1),('407','Omer','Food',NULL,'2020-01-01',NULL,NULL,NULL,'Flight attendant',1),('408','Nir','Safe',NULL,'2020-01-01',NULL,NULL,NULL,'Flight attendant',1),('409','Liat','Exit',NULL,'2020-01-01',NULL,NULL,NULL,'Flight attendant',1),('410','Tomer','Vest',NULL,'2020-01-01',NULL,NULL,NULL,'Flight attendant',1),('411','Shir','Belt',NULL,'2020-01-01',NULL,NULL,NULL,'Flight attendant',1),('412','Mor','Bag',NULL,'2020-01-01',NULL,NULL,NULL,'Flight attendant',1),('413','Chen','Coffee',NULL,'2020-01-01',NULL,NULL,NULL,'Flight attendant',1),('414','Or','Tea',NULL,'2020-01-01',NULL,NULL,NULL,'Flight attendant',1),('415','Ben','Duty',NULL,'2020-01-01',NULL,NULL,NULL,'Flight attendant',1),('416','Dor','Free',NULL,'2020-01-01',NULL,NULL,NULL,'Flight attendant',1),('417','Gal','Cart',NULL,'2020-01-01',NULL,NULL,NULL,'Flight attendant',1),('418','Tal','Smile',NULL,'2020-01-01',NULL,NULL,NULL,'Flight attendant',1),('419','Yam','Cloud',NULL,'2020-01-01',NULL,NULL,NULL,'Flight attendant',1),('420','Ron','Air',NULL,'2020-01-01',NULL,NULL,NULL,'Flight attendant',1);
/*!40000 ALTER TABLE `air_crew` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `air_crew_assignment`
--

DROP TABLE IF EXISTS `air_crew_assignment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `air_crew_assignment` (
  `fk_air_crew_id` varchar(45) NOT NULL,
  `fk_assignment_plane_id` varchar(50) NOT NULL,
  `fk_assignment_departure_time` time NOT NULL,
  `fk_assignment_departure_date` date NOT NULL,
  PRIMARY KEY (`fk_air_crew_id`,`fk_assignment_plane_id`,`fk_assignment_departure_time`,`fk_assignment_departure_date`),
  KEY `fk_assignment_flight` (`fk_assignment_plane_id`,`fk_assignment_departure_time`,`fk_assignment_departure_date`),
  CONSTRAINT `fk_air_crew_id` FOREIGN KEY (`fk_air_crew_id`) REFERENCES `air_crew` (`id`),
  CONSTRAINT `fk_assignment_flight` FOREIGN KEY (`fk_assignment_plane_id`, `fk_assignment_departure_time`, `fk_assignment_departure_date`) REFERENCES `flight` (`fk_flight_plane_id`, `departure_time`, `departure_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `air_crew_assignment`
--

LOCK TABLES `air_crew_assignment` WRITE;
/*!40000 ALTER TABLE `air_crew_assignment` DISABLE KEYS */;
INSERT INTO `air_crew_assignment` VALUES ('301','PLN-L1','15:32:00','2026-03-31'),('302','PLN-L1','15:32:00','2026-03-31'),('303','PLN-L1','15:32:00','2026-03-31'),('401','PLN-L1','15:32:00','2026-03-31'),('402','PLN-L1','15:32:00','2026-03-31'),('403','PLN-L1','15:32:00','2026-03-31'),('404','PLN-L1','15:32:00','2026-03-31'),('405','PLN-L1','15:32:00','2026-03-31'),('406','PLN-L1','15:32:00','2026-03-31'),('301','PLN-L1','21:00:00','2026-02-21'),('302','PLN-L1','21:00:00','2026-02-21'),('303','PLN-L1','21:00:00','2026-02-21'),('401','PLN-L1','21:00:00','2026-02-21'),('402','PLN-L1','21:00:00','2026-02-21'),('403','PLN-L1','21:00:00','2026-02-21'),('404','PLN-L1','21:00:00','2026-02-21'),('405','PLN-L1','21:00:00','2026-02-21'),('406','PLN-L1','21:00:00','2026-02-21'),('304','PLN-L2','02:00:00','2026-04-03'),('305','PLN-L2','02:00:00','2026-04-03'),('306','PLN-L2','02:00:00','2026-04-03'),('407','PLN-L2','02:00:00','2026-04-03'),('408','PLN-L2','02:00:00','2026-04-03'),('409','PLN-L2','02:00:00','2026-04-03'),('415','PLN-L2','02:00:00','2026-04-03'),('416','PLN-L2','02:00:00','2026-04-03'),('417','PLN-L2','02:00:00','2026-04-03'),('304','PLN-L2','02:48:00','2026-04-01'),('305','PLN-L2','02:48:00','2026-04-01'),('306','PLN-L2','02:48:00','2026-04-01'),('407','PLN-L2','02:48:00','2026-04-01'),('408','PLN-L2','02:48:00','2026-04-01'),('409','PLN-L2','02:48:00','2026-04-01'),('415','PLN-L2','02:48:00','2026-04-01'),('416','PLN-L2','02:48:00','2026-04-01'),('417','PLN-L2','02:48:00','2026-04-01'),('301','PLN-S1','17:51:00','2026-01-21'),('309','PLN-S1','17:51:00','2026-01-21'),('401','PLN-S1','17:51:00','2026-01-21'),('408','PLN-S1','17:51:00','2026-01-21'),('417','PLN-S1','17:51:00','2026-01-21');
/*!40000 ALTER TABLE `air_crew_assignment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `class`
--

DROP TABLE IF EXISTS `class`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `class` (
  `fk_plane_id` varchar(50) NOT NULL,
  `type` enum('Economy','Business') NOT NULL,
  `number_of_col` int DEFAULT NULL,
  `number_of_row` int DEFAULT NULL,
  PRIMARY KEY (`fk_plane_id`,`type`),
  KEY `type` (`type`),
  CONSTRAINT `fk_plane_id` FOREIGN KEY (`fk_plane_id`) REFERENCES `plane` (`plane_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `class`
--

LOCK TABLES `class` WRITE;
/*!40000 ALTER TABLE `class` DISABLE KEYS */;
INSERT INTO `class` VALUES ('PLN-L1','Economy',6,30),('PLN-L1','Business',4,10),('PLN-L2','Economy',6,30),('PLN-L2','Business',4,10),('PLN-L3','Economy',6,30),('PLN-L3','Business',4,10),('PLN-S1','Economy',4,20),('PLN-S2','Economy',4,20),('PLN-S3','Economy',4,20);
/*!40000 ALTER TABLE `class` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customer`
--

DROP TABLE IF EXISTS `customer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customer` (
  `email` varchar(50) NOT NULL,
  `first_name` varchar(45) DEFAULT NULL,
  `last_name` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`email`),
  UNIQUE KEY `Email_UNIQUE` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customer`
--

LOCK TABLES `customer` WRITE;
/*!40000 ALTER TABLE `customer` DISABLE KEYS */;
INSERT INTO `customer` VALUES ('guest1@gmail.com','John','Guest'),('guest2@gmail.com','Jane','Visitor'),('reg1@gmail.com','Israel','Israeli'),('reg2@gmail.com','Rivka','Cohen'),('tel@aviv.tau.ac.il','Tel','Bugrashov');
/*!40000 ALTER TABLE `customer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `flight`
--

DROP TABLE IF EXISTS `flight`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `flight` (
  `fk_flight_plane_id` varchar(50) NOT NULL,
  `departure_time` time NOT NULL,
  `departure_date` date NOT NULL,
  `fk_origin` varchar(45) DEFAULT NULL,
  `fk_destination` varchar(45) DEFAULT NULL,
  `status` enum('Active','Full','Cancelled','Landed') DEFAULT NULL,
  PRIMARY KEY (`fk_flight_plane_id`,`departure_time`,`departure_date`),
  KEY `fk_origin_idx` (`fk_origin`),
  KEY `fk_destination_idx` (`fk_destination`),
  KEY `departure_time` (`departure_time`) /*!80000 INVISIBLE */,
  KEY `departure_date` (`departure_date`),
  CONSTRAINT `fk_destination` FOREIGN KEY (`fk_destination`) REFERENCES `route` (`destination`),
  CONSTRAINT `fk_flight_plane_id` FOREIGN KEY (`fk_flight_plane_id`) REFERENCES `plane` (`plane_id`),
  CONSTRAINT `fk_origin` FOREIGN KEY (`fk_origin`) REFERENCES `route` (`origin`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `flight`
--

LOCK TABLES `flight` WRITE;
/*!40000 ALTER TABLE `flight` DISABLE KEYS */;
INSERT INTO `flight` VALUES ('PLN-L1','15:32:00','2026-03-31','USA','Israel','Active'),('PLN-L1','21:00:00','2026-02-21','Israel','USA','Active'),('PLN-L2','02:00:00','2026-04-03','Japan','Israel','Active'),('PLN-L2','02:48:00','2026-04-01','Israel','Japan','Active'),('PLN-S1','17:51:00','2026-01-21','Israel','Italy','Active');
/*!40000 ALTER TABLE `flight` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `flight_price`
--

DROP TABLE IF EXISTS `flight_price`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `flight_price` (
  `fk_price_plane_id` varchar(50) NOT NULL,
  `fk_price_class` enum('Economy','Business') NOT NULL,
  `fk_price_departure_time` time NOT NULL,
  `fk_price_departure_date` date NOT NULL,
  `price` int DEFAULT NULL,
  PRIMARY KEY (`fk_price_plane_id`,`fk_price_class`,`fk_price_departure_time`,`fk_price_departure_date`),
  KEY `fk_price_to_flight` (`fk_price_plane_id`,`fk_price_departure_time`,`fk_price_departure_date`),
  CONSTRAINT `fk_price_to_class` FOREIGN KEY (`fk_price_plane_id`, `fk_price_class`) REFERENCES `class` (`fk_plane_id`, `type`),
  CONSTRAINT `fk_price_to_flight` FOREIGN KEY (`fk_price_plane_id`, `fk_price_departure_time`, `fk_price_departure_date`) REFERENCES `flight` (`fk_flight_plane_id`, `departure_time`, `departure_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `flight_price`
--

LOCK TABLES `flight_price` WRITE;
/*!40000 ALTER TABLE `flight_price` DISABLE KEYS */;
INSERT INTO `flight_price` VALUES ('PLN-L1','Economy','15:32:00','2026-03-31',1200),('PLN-L1','Economy','21:00:00','2026-02-21',900),('PLN-L1','Business','15:32:00','2026-03-31',2200),('PLN-L1','Business','21:00:00','2026-02-21',1700),('PLN-L2','Economy','02:00:00','2026-04-03',700),('PLN-L2','Economy','02:48:00','2026-04-01',400),('PLN-L2','Business','02:00:00','2026-04-03',1400),('PLN-L2','Business','02:48:00','2026-04-01',1000),('PLN-S1','Economy','17:51:00','2026-01-21',340);
/*!40000 ALTER TABLE `flight_price` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `manager`
--

DROP TABLE IF EXISTS `manager`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `manager` (
  `id` varchar(45) NOT NULL,
  `first_name` varchar(45) DEFAULT NULL,
  `last_name` varchar(45) DEFAULT NULL,
  `phone_number` varchar(45) DEFAULT NULL,
  `hire_date` date DEFAULT NULL,
  `city` varchar(45) DEFAULT NULL,
  `street` varchar(45) DEFAULT NULL,
  `house_number` varchar(10) DEFAULT NULL,
  `password` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `manager`
--

LOCK TABLES `manager` WRITE;
/*!40000 ALTER TABLE `manager` DISABLE KEYS */;
INSERT INTO `manager` VALUES ('100000001','Admin','Boss','050-0000001','2020-01-01','Tel Aviv','Herzl','1','admin123'),('100000002','Dana','Manager','050-0000002','2021-05-15','Haifa','Ben Gurion','10','dana123');
/*!40000 ALTER TABLE `manager` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order`
--

DROP TABLE IF EXISTS `order`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order` (
  `order_id` varchar(50) NOT NULL,
  `fk_order_email` varchar(50) NOT NULL,
  `status` enum('Active','Finished','Cancelled by manager','Cancelled by customer') DEFAULT NULL,
  `order_date` date DEFAULT NULL,
  `order_cost` int DEFAULT NULL,
  PRIMARY KEY (`order_id`),
  KEY `fk_order_email_idx` (`fk_order_email`),
  CONSTRAINT `fk_order_email` FOREIGN KEY (`fk_order_email`) REFERENCES `customer` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order`
--

LOCK TABLES `order` WRITE;
/*!40000 ALTER TABLE `order` DISABLE KEYS */;
INSERT INTO `order` VALUES ('CGLOMI','tel@aviv.tau.ac.il','Active','2026-01-21',8100),('CIU0RH','tel@aviv.tau.ac.il','Active','2026-01-21',15400),('CZTNU1','reg1@gmail.com','Active','2026-01-21',5600),('XXGTOK','reg1@gmail.com','Active','2026-01-21',3400);
/*!40000 ALTER TABLE `order` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `phone_number`
--

DROP TABLE IF EXISTS `phone_number`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `phone_number` (
  `phone_number` varchar(20) NOT NULL,
  `fk_phone_email` varchar(50) NOT NULL,
  PRIMARY KEY (`phone_number`,`fk_phone_email`),
  KEY `email_idx` (`fk_phone_email`),
  CONSTRAINT `fk_phone_email` FOREIGN KEY (`fk_phone_email`) REFERENCES `customer` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `phone_number`
--

LOCK TABLES `phone_number` WRITE;
/*!40000 ALTER TABLE `phone_number` DISABLE KEYS */;
/*!40000 ALTER TABLE `phone_number` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `plane`
--

DROP TABLE IF EXISTS `plane`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `plane` (
  `plane_id` varchar(50) NOT NULL,
  `purchase_date` date DEFAULT NULL,
  `size` enum('Small','Large') DEFAULT NULL,
  `manufacturer` enum('Boeing','Airbus','Dassault') DEFAULT NULL,
  PRIMARY KEY (`plane_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `plane`
--

LOCK TABLES `plane` WRITE;
/*!40000 ALTER TABLE `plane` DISABLE KEYS */;
INSERT INTO `plane` VALUES ('PLN-L1','2020-01-01','Large','Boeing'),('PLN-L2','2021-06-15','Large','Airbus'),('PLN-L3','2019-11-20','Large','Boeing'),('PLN-S1','2022-03-10','Small','Dassault'),('PLN-S2','2023-08-05','Small','Airbus'),('PLN-S3','2024-02-28','Small','Boeing');
/*!40000 ALTER TABLE `plane` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `route`
--

DROP TABLE IF EXISTS `route`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `route` (
  `origin` varchar(45) NOT NULL,
  `destination` varchar(45) NOT NULL,
  `duration` int DEFAULT NULL,
  PRIMARY KEY (`origin`,`destination`),
  KEY `idx_destination` (`destination`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `route`
--

LOCK TABLES `route` WRITE;
/*!40000 ALTER TABLE `route` DISABLE KEYS */;
INSERT INTO `route` VALUES ('Israel','Italy',240),('Israel','Japan',750),('Israel','USA',720),('Italy','Israel',240),('Japan','Israel',780),('USA','Israel',660);
/*!40000 ALTER TABLE `route` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `signed_customer`
--

DROP TABLE IF EXISTS `signed_customer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `signed_customer` (
  `fk_signed_email` varchar(50) NOT NULL,
  `passport` varchar(45) DEFAULT NULL,
  `birth_date` date DEFAULT NULL,
  `sign_up_date` date DEFAULT NULL,
  `password` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`fk_signed_email`),
  UNIQUE KEY `email_UNIQUE` (`fk_signed_email`),
  CONSTRAINT `fk_signed_email` FOREIGN KEY (`fk_signed_email`) REFERENCES `customer` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `signed_customer`
--

LOCK TABLES `signed_customer` WRITE;
/*!40000 ALTER TABLE `signed_customer` DISABLE KEYS */;
INSERT INTO `signed_customer` VALUES ('reg1@gmail.com','P12345678','1990-01-01','2026-01-21','pass1'),('reg2@gmail.com','P87654321','1992-05-05','2026-01-21','pass2');
/*!40000 ALTER TABLE `signed_customer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ticket`
--

DROP TABLE IF EXISTS `ticket`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ticket` (
  `row` int NOT NULL,
  `col` int NOT NULL,
  `fk_ticket_order_id` varchar(50) NOT NULL,
  `fk_ticket_plane_id` varchar(50) DEFAULT NULL,
  `fk_ticket_class` enum('Economy','Business') NOT NULL,
  `fk_ticket_departure_time` time DEFAULT NULL,
  `fk_ticket_departure_date` date DEFAULT NULL,
  `price` int DEFAULT NULL,
  PRIMARY KEY (`row`,`col`,`fk_ticket_order_id`,`fk_ticket_class`),
  KEY `fk_ticket_order_id_idx` (`fk_ticket_order_id`),
  KEY `fk_ticket_departure_time_idx` (`fk_ticket_departure_time`),
  KEY `fk_ticket_plane_id_idx` (`fk_ticket_plane_id`),
  KEY `fk_ticket_departure_date_idx` (`fk_ticket_departure_date`),
  KEY `fk_ticket_class_idx` (`fk_ticket_class`),
  CONSTRAINT `fk_ticket_class` FOREIGN KEY (`fk_ticket_class`) REFERENCES `class` (`type`),
  CONSTRAINT `fk_ticket_departure_date` FOREIGN KEY (`fk_ticket_departure_date`) REFERENCES `flight` (`departure_date`),
  CONSTRAINT `fk_ticket_departure_time` FOREIGN KEY (`fk_ticket_departure_time`) REFERENCES `flight` (`departure_time`),
  CONSTRAINT `fk_ticket_order_id` FOREIGN KEY (`fk_ticket_order_id`) REFERENCES `order` (`order_id`),
  CONSTRAINT `fk_ticket_plane_id` FOREIGN KEY (`fk_ticket_plane_id`) REFERENCES `flight` (`fk_flight_plane_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ticket`
--

LOCK TABLES `ticket` WRITE;
/*!40000 ALTER TABLE `ticket` DISABLE KEYS */;
INSERT INTO `ticket` VALUES (1,2,'CIU0RH','PLN-L1','Economy','15:32:00','2026-03-31',1200),(1,3,'CIU0RH','PLN-L1','Economy','15:32:00','2026-03-31',1200),(1,3,'CIU0RH','PLN-L1','Business','15:32:00','2026-03-31',2200),(1,3,'XXGTOK','PLN-L2','Economy','02:48:00','2026-04-01',400),(1,4,'CZTNU1','PLN-L2','Business','02:00:00','2026-04-03',1400),(1,4,'XXGTOK','PLN-L2','Business','02:48:00','2026-04-01',1000),(1,5,'CZTNU1','PLN-L2','Business','02:00:00','2026-04-03',1400),(1,5,'XXGTOK','PLN-L2','Business','02:48:00','2026-04-01',1000),(1,6,'CZTNU1','PLN-L2','Business','02:00:00','2026-04-03',1400),(1,6,'XXGTOK','PLN-L2','Business','02:48:00','2026-04-01',1000),(2,1,'CGLOMI','PLN-L1','Economy','21:00:00','2026-02-21',900),(2,2,'CGLOMI','PLN-L1','Economy','21:00:00','2026-02-21',900),(2,2,'CIU0RH','PLN-L1','Economy','15:32:00','2026-03-31',1200),(2,3,'CIU0RH','PLN-L1','Economy','15:32:00','2026-03-31',1200),(2,4,'CZTNU1','PLN-L2','Business','02:00:00','2026-04-03',1400),(3,1,'CGLOMI','PLN-L1','Economy','21:00:00','2026-02-21',900),(3,2,'CIU0RH','PLN-L1','Economy','15:32:00','2026-03-31',1200),(3,3,'CIU0RH','PLN-L1','Economy','15:32:00','2026-03-31',1200),(4,1,'CGLOMI','PLN-L1','Economy','21:00:00','2026-02-21',900),(4,2,'CIU0RH','PLN-L1','Economy','15:32:00','2026-03-31',1200),(4,3,'CIU0RH','PLN-L1','Economy','15:32:00','2026-03-31',1200),(5,2,'CIU0RH','PLN-L1','Economy','15:32:00','2026-03-31',1200),(5,3,'CGLOMI','PLN-L1','Economy','21:00:00','2026-02-21',900),(5,3,'CIU0RH','PLN-L1','Economy','15:32:00','2026-03-31',1200),(6,3,'CIU0RH','PLN-L1','Economy','15:32:00','2026-03-31',1200),(6,4,'CGLOMI','PLN-L1','Economy','21:00:00','2026-02-21',900),(7,1,'CGLOMI','PLN-L1','Economy','21:00:00','2026-02-21',900),(8,4,'CGLOMI','PLN-L1','Economy','21:00:00','2026-02-21',900),(10,1,'CGLOMI','PLN-L1','Economy','21:00:00','2026-02-21',900);
/*!40000 ALTER TABLE `ticket` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-01-21 21:45:02
