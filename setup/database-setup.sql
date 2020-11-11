create user if not exists 'DeviceControl'@'localhost' identified by '&Bioarineo1';
create database if not exists device_control;
grant all privileges on device_control.* to 'DeviceControl'@'localhost';


USE device_control;


CREATE TABLE IF NOT EXISTS `devices` (
  `id` varchar(100) NOT NULL,
  `class` varchar(100) NOT NULL,
  `type` varchar(100) NOT NULL,
  `address` varchar(150) DEFAULT NULL,
  PRIMARY KEY (`id`)
);


CREATE TABLE IF NOT EXISTS `experiments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dev_id` varchar(100) NOT NULL,
  `start` TIMESTAMP NOT NULL,
  `end` TIMESTAMP DEFAULT NULL,
  `description` varchar(255),
  PRIMARY KEY (`id`),
  FOREIGN KEY (`dev_id`) REFERENCES `devices`(`id`)
);


CREATE TABLE IF NOT EXISTS `variables` (
  `code` varchar(30) NOT NULL,
  `name` varchar(150) DEFAULT NULL,
  `type` enum('measured','computed','adjusted','aggregate') DEFAULT NULL,
  `unit` int(11) DEFAULT NULL,
  PRIMARY KEY (`code`)
);


CREATE TABLE IF NOT EXISTS `values` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `time` TIMESTAMP NOT NULL,
  `value` double NOT NULL,
  `dev_id` varchar(100) NOT NULL,
  `var_id` varchar(30) NOT NULL,
  `channel` int(11) DEFAULT NULL,
  `note` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`dev_id`) REFERENCES `devices`(`id`),
  FOREIGN KEY (`var_id`) REFERENCES `variables`(`code`)
);


CREATE TABLE IF NOT EXISTS `event_types` (
  `id` int(11) NOT NULL,
  `type` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
);


CREATE TABLE IF NOT EXISTS `events` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dev_id` varchar(100) NOT NULL,
  `event_type` int(11) NOT NULL,
  `time` TIMESTAMP NOT NULL,
  `args` varchar(100) NOT NULL,
  `command` varchar(100) NOT NULL,
  `response` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`dev_id`) REFERENCES `devices`(`id`),
  FOREIGN KEY (`event_type`) REFERENCES `event_types`(`id`)
);

INSERT IGNORE INTO `event_types` (`id`, `type`)
VALUES
    (1, 'command executed'),
    (2, 'measurement not successful'),
    (3, 'pump state changed'),
    (4, 'variable created');

INSERT IGNORE INTO `variables` (`code`, `name`, `type`)
VALUES
    ('temp', 'current temperature', 'measured'),
    ('temp_min', 'max allowed temperature', 'measured'),
    ('temp_max', 'min allowed temperature', 'measured'),
    ('temp_on', 'thermoregulation on', 'measured'),
    ('pH', 'current pH', 'measured'),
    ('od', 'optical density', 'measured'),
    ('pump_direction', 'direction of pump', 'measured'),
    ('pump_on', 'pump turned on', 'measured'),
    ('pump_valves', 'pump valves settings', 'measured'),
    ('pump_flow', 'pump current flow', 'measured'),
    ('pump_min', 'pump min allowed flow', 'measured'),
    ('pump_max', 'pump max allowed flow', 'measured'),
    ('light_intensity', 'current light intensity', 'measured'),
    ('light_max', 'max allowed light intensity', 'measured'),
    ('light_on', 'light turned on', 'measured'),
    ('pwm_pulse', 'current stirring', 'measured'),
    ('pwm_min', 'minimal stirring', 'measured'),
    ('pwm_max', 'maximal stirring', 'measured'),
    ('pwm_on', 'stirring is turned on', 'measured'),
    ('o2', 'concentration of dissociated O2', 'measured'),
    ('ft_flash', 'steady-state terminal fluorescence', 'measured'),
    ('ft_background', 'steady-state terminal fluorescence background signal', 'measured'),
    ('qy', 'quantum yield', 'computed'),
    ('fm-flash', 'steady-state terminal fluorescence', 'measured'),
    ('fm-background', 'maximal fluorescence background signal', 'measured'),
    ('delay-cycles', 'number of cycles before reaching stable signal', 'measured'),
    ('co2', 'dissolved CO2 concentration', 'measured'),
    ('valve_flow_current', 'current valve flow', 'measured'),
    ('valve_flow_set', 'current valve flow target', 'measured'),
    ('warning', 'valve flow warning', 'measured'),
    ('valve_max_flow', 'valve max flow', 'measured'),
    ('valve_gas_type', 'valve gas type', 'measured'),
    ('user_gas_type', '???', 'measured'),
    ('co2-air', 'CO2 in air', 'measured'),
    ('small-valves', 'settings of individual vents', 'measured'),
    ('flow', 'flow from GAS to PBR', 'measured'),
    ('flow-target', 'target flow from GAS to PBR', 'measured'),
    ('flow-max', 'max allowed flow from GAS to PBR', 'measured'),
    ('pressure', 'current pressure', 'measured'),
    ('aux', 'AUX auxiliary input voltage', 'measured'),
    ('HWaddress', 'the MAC address of the PBR', 'measured'),
    ('clusterName', 'name of the bioreactor array', 'measured'),
    ('humidity', 'sensor humidity', 'measured'),
    ('vis', 'sensor illuminance', 'measured'),
    ('weight', 'measured weight', 'measured');