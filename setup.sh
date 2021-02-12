#!/bin/sh

DBuser=$1
PASSWDDB=$2
# store them in a config which will use also the app
echo "USER=\"${DBuser}\"\nPASSWORD=\"${PASSWDDB}\"" > DB_CONFIG

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
python3 -m pip install Flask Flask-Bootstrap Flask-Mail Flask-Migrate Flask-Moment Flask-SQLAlchemy Flask-WTF \
                       alembic blinker click dominate six SQLAlchemy visitor Werkzeug WTForms numpy \
                       JPype1 Flask-RESTful pycrypto pyserial mettler_toledo_device requests

# init DB? then migrate in run script? (resp. upgrade)
export FLASK_APP=main.py
flask db init
