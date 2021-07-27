#!/bin/sh

sh ./install_docker.sh

DBuser=$1
PASSWDDB=$2
# store them in a config which will use also the app
echo "USERNAME=\"${DBuser}\"\nPASSWORD=\"${PASSWDDB}\"" > DB_CONFIG

apt-get install -y default-mysql-server

# setup all DBs
mysql -u root<<MYSQL_SCRIPT
CREATE USER if not exists ${DBuser}@'%' IDENTIFIED BY '${PASSWDDB}';
CREATE USER if not exists 'TestUser'@'%' IDENTIFIED BY 'pass';

CREATE DATABASE if not exists device_control;
GRANT ALL PRIVILEGES ON device_control.* TO ${DBuser}@'%';
CREATE DATABASE if not exists device_control_devel;
GRANT ALL PRIVILEGES ON device_control_devel.* TO ${DBuser}@'%';
CREATE DATABASE if not exists device_control_test;
GRANT ALL PRIVILEGES ON device_control_test.* TO 'TestUser'@'%';
FLUSH PRIVILEGES;
MYSQL_SCRIPT
