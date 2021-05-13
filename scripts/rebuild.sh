# requires to be logged in with Docker
git checkout deploy
git pull

docker buildx build --output=type=docker --platform linux/arm/v7 -t devicecontrol:arm .
docker tag devicecontrol:arm bioarineo/devicecontrol:arm
docker push bioarineo/devicecontrol:arm

# notify Neurons, shh IDs must be copied !
declare -a choice=( $( python3 find_neurons.py ) )
for port in "${output[@]}";
do
  ssh 'bioarineo@localhost' -p "$port" 'cd ~/DeviceControl/scripts && ./redeploy.sh &>/dev/null &'
done