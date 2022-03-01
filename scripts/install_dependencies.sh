#!/bin/bash

apt-get update
apt-get install -y curl
curl -fsSL 'https://get.docker.com' -o get-docker.sh
sh get-docker.sh
usermod -aG docker bioarineo

apt-get install -y default-mysql-server libmysqlclient-dev