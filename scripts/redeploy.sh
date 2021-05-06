#!/bin/bash

git pull
docker build -t devicecontrol:latest .
docker stop $(docker ps -q --filter "name=devicecontrol")
docker system prune -f

# TODO
# set local IP to $DATABASE alias
# hostname -I ?

docker run --privileged -v /dev/serial/by-port/:/dev/serial/by-port/ -p 0.0.0.0:5000:5000 \
       --add-host="database:$DATABASE" --env-file ../DB_CONFIG --name "devicecontrol" bioarineo/devicecontrol:arm

# location of DB_CONFIG is crucial, make sure exec path is OK !
