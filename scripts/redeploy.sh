#!/bin/bash

docker stop $(docker ps -q --filter "name=devicecontrol")
docker system prune -f
docker pull bioarineo/devicecontrol:arm

DATABASE=$(/sbin/ifconfig eth0 | sed -En -e 's/.*inet ([0-9.]+).*/\1/p')

docker run -d --privileged -v /dev/serial/by-port/:/dev/serial/by-port/ -p 0.0.0.0:5000:5000 --restart unless-stopped \
       --add-host="database:$DATABASE" --env-file ../DB_CONFIG --name "devicecontrol" bioarineo/devicecontrol:arm
