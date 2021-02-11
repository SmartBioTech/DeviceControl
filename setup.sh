DBuser=$1
PASSWDDB=$2
# store them in a config which will use also the app

# setup all DBs
mysql -u root -p<<MYSQL_SCRIPT
CREATE USER if not exists ${DBuser}@'localhost' IDENTIFIED BY '${PASSWDDB}';

create database if not exists device_control;
grant all privileges on device_control.* to ${DBuser}@'localhost';
create database if not exists device_control_devel;
grant all privileges on device_control_devel.* to ${DBuser}@'localhost';
create database if not exists device_control_test;
grant all privileges on device_control_test.* to ${DBuser}@'localhost';
MYSQL_SCRIPT

# install all requirements
apt-get install python-mysqldb python-dateutil python-editor
python3 -m pip install Flask Flask-Bootstrap Flask-Mail Flask-Migrate Flask-Moment Flask-SQLAlchemy Flask-WTF alembic blinker click dominate six SQLAlchemy visitor Werkzeug WTForms

# init DB? then migrate in run script? (resp. upgrade)
export FLASK_APP=main.py
flask db init
