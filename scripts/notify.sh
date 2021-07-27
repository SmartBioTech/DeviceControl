#!/bin/bash

# notify RPI4 to rebuild
ssh -p 10909 pi@localhost '~/Downloads/DeviceControl/scripts/rebuild.sh'

# notify Neurons, ssh IDs must be copied !
declare -a choice=( $( python3 find_neurons.py ) )
for port in "${output[@]}";
do
  ssh 'bioarineo@localhost' -p "$port" 'cd ~/DeviceControl/scripts && ./redeploy.sh &>/dev/null &'
done