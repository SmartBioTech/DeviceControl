# requires to be logged in with Docker
docker buildx build --output=type=docker --platform linux/arm/v7 -t devicecontrol:arm .
docker tag devicecontrol:arm bioarineo/devicecontrol:arm
docker push bioarineo/devicecontrol:arm
