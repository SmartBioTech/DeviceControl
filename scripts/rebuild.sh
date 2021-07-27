# requires to be logged in with Docker
git checkout master
git pull

docker buildx build --output=type=docker --platform linux/arm/v7 -t devicecontrol:arm .
docker tag devicecontrol:arm bioarineo/devicecontrol:arm
docker push bioarineo/devicecontrol:arm
