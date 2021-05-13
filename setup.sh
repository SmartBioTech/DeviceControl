#!/bin/sh

DBuser=$1
PASSWDDB=$2
# store them in a config which will use also the app
echo "USERNAME=\"${DBuser}\"\nPASSWORD=\"${PASSWDDB}\"" > DB_CONFIG

# setup all DBs
mysql -u root<<MYSQL_SCRIPT
CREATE USER if not exists ${DBuser}@'localhost' IDENTIFIED BY '${PASSWDDB}';
CREATE USER if not exists 'TestUser'@'localhost' IDENTIFIED BY 'pass';

CREATE DATABASE if not exists device_control;
GRANT ALL PRIVILEGES ON device_control.* TO ${DBuser}@'localhost';
CREATE DATABASE if not exists device_control_devel;
GRANT ALL PRIVILEGES ON device_control_devel.* TO ${DBuser}@'localhost';
CREATE DATABASE if not exists device_control_test;
GRANT ALL PRIVILEGES ON device_control_test.* TO 'TestUser'@'localhost';
FLUSH PRIVILEGES;
MYSQL_SCRIPT


# install all requirements
apt-get install -y default-mysql-server python3-mysqldb python3-dateutil python3-editor libatlas3-base default-jre
python3 -m pip install -r requirements.txt

#- allow port
# sudo ufw allow 3306
# but change to less wide (problem with source IP)
# sudo ufw allow from 172.17.0.1 to any port 3306
