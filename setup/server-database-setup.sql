create user if not exists 'DeviceControl'@'localhost' identified by '&Bioarineo1';
create database if not exists bioarineo_local;
grant all privileges on bioarineo_local.* to 'DeviceControl'@'localhost' identified by '&Bioarineo1';


USE bioarineo_local;


CREATE TABLE `device` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `class` varchar(100) NOT NULL,
  `type` varchar(100) NOT NULL,
  `name` varchar(110) NOT NULL,
  `address` varchar(150) DEFAULT NULL,
  PRIMARY KEY (`id`)
);


CREATE TABLE `variable` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) DEFAULT NULL,
  `code` varchar(30) NOT NULL,
  `type` enum('measured','computed','adjusted','aggregate') DEFAULT NULL,
  PRIMARY KEY (`id`)
);


CREATE TABLE `device_to_variable` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dev_id` int(11) NOT NULL,
  `var_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`dev_id`) REFERENCES `device`(`id`),
  FOREIGN KEY (`var_id`) REFERENCES `variable`(`id`)
);


CREATE TABLE `event` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
);


CREATE TABLE `device_event` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dev_id` int(11) NOT NULL,
  `event_id` int(11) NOT NULL,
  `time` double NOT NULL,
  `args` varchar(100) NOT NULL,
  `event` varchar(100) NOT NULL,
  `response` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`dev_id`) REFERENCES `device`(`id`),
  FOREIGN KEY (`event_id`) REFERENCES `event`(`id`)
);