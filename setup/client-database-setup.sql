create user if not exists 'DeviceControl'@'localhost' identified by '&Bioarineo1';
create database if not exists device_control;
grant all privileges on device_control.* to 'DeviceControl'@'localhost' identified by '&Bioarineo1';