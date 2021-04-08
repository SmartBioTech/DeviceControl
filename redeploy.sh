#!/bin/bash

git pull
docker build -t devicecontrol:latest .
docker stop $(docker ps -q --filter "name=devicecontrol")
docker system prune -f
docker run -d -p 0.0.0.0:5000:5000 --name "devicecontrol" devicecontrol
