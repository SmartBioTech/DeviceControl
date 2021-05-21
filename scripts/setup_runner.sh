#!/bin/sh

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

# TODO
# allow DB access
# sudo ufw allow 3306 (probably not needed on Neurons)
# but it is necessary to allow users connect from outside of localhost
# maybe /etc/mysql/mariadb.conf.d/50-server.cnf on Neurons