#!/bin/bash

echo "Execute in /home/bioarineo/DeviceControl/setup as sudoer and in tmux only!!!"
echo "Press any key to continue or Ctrl-C to cancel ..."
read -n 1 -s

apt update

echo "Setting up MySQL database..."

apt -y install default-mysql-server
service mysql start

mysql < "database-setup.sql"

echo "Setting up Python environment..."

apt -y install python3-pip

pip3 install importlib
pip3 install numpy
pip3 install mysql-connector
pip3 install JPype1
pip3 install Flask
pip3 install Flask-RESTful
pip3 install pycrypto
pip3 install pyserial
pip3 install mettler_toledo_device
pip3 install requests

apt -y install libatlas3-base

echo "Installing Java dependencies..."

apt -y install default-jre

echo "DeviceControl is ready to run!"
