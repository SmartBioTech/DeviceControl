#!/bin/bash

# notify RPI4 to rebuild
ssh -p 10909 pi@localhost 'cd ~/Downloads/DeviceControl && scripts/rebuild.sh'

# notify Neurons, ssh IDs must be copied !
declare -a ports=( $( python3 ~/DeviceControl/scripts/find_neurons.py ) )
for port in "${ports[@]}";
do
  ssh 'bioarineo@localhost' -p "$port" 'cd ~/DeviceControl/scripts && ./redeploy.sh &>/dev/null &'
done