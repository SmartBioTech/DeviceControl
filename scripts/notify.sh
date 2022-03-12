#!/bin/bash

# notify Neurons, ssh IDs must be copied !
declare -a ports=( $( python3 ~/DeviceControl/scripts/find_neurons.py ) )
for port in "${ports[@]}";
do
  ssh 'bioarineo@localhost' -p "$port" 'cd ~/DeviceControl/scripts && ./redeploy.sh &>/dev/null &'
done