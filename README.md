[![Python Package](https://github.com/SmartBioTech/DeviceControl/actions/workflows/python-flask.yml/badge.svg)](https://github.com/SmartBioTech/DeviceControl/actions/workflows/python-flask.yml)
[![Docker](https://github.com/SmartBioTech/DeviceControl/actions/workflows/docker.yml/badge.svg)](https://github.com/SmartBioTech/DeviceControl/actions/workflows/docker.yml)
[![docs](https://readthedocs.org/projects/devicecontrol/badge/?version=latest)](https://devicecontrol.readthedocs.io/en/latest/)

# DeviceControl

`DeviceControl` is a tool to provide unified interface to control and measure data in specific cultivation device.
We recommend reading [wiki](https://github.com/SmartBioTech/DeviceControl/wiki) to get started with the tool 
and [documentation](http://devicecontrol.readthedocs.io/) to get more details about the implementation. 

## Installation

`DeviceControl` runs in a [`Docker` container](https://hub.docker.com/r/bioarineo/devicecontrol) with locally installed database.
The reason for installation of database locally is to make data more persistent and prone to unintentional deletion.

1. Before we start, it is necessary to install `mySQL` database and `docker`:

    ```
    sudo scripts/install_dependencies.sh
   ```

2. Then we need to set up the database:

    ```
    sudo scripts/setup_database.sh "<username>" "<password>"
    ```

3. Set environment variable to DATABASE to your local IP address - this is used by `docker` to access the database

   ```
   DATABASE=$(/sbin/ifconfig <interface> | sed -En -e 's/.*inet ([0-9.]+).*/\1/p')
   ```

4. Enable connections to your `mySQL` database from outside of `localhost` (might even require opening firewall for port 3306)

5. Download docker and start the `docker`:

    ```
    docker run -d --privileged -v /dev/serial/by-port/:/dev/serial/by-port/ -p 0.0.0.0:5000:5000 --restart unless-stopped --add-host="database:$DATABASE" --env-file DB_CONFIG --name "devicecontrol" bioarineo/devicecontrol:latest-<platform>
    ```

    where `<platform>` is either `amd` or `arm`. The `by-port` is mapped to `docker` file system to access devices connected to I/O ports.

`DeviceControl` is running and ready to be used.

Inspect and execute `scripts/example_run.py` to see demonstration of tool's usability on a simulated device.

---

## Quick start

Assuming `DeviceControl` is properly installed and running, follow these steps to quickly setup a device and execute a measurement:

```python
import requests

# device configuration
test_PBR_device = {
    'device_id': PBR_id,
    'device_class': 'test',
    'device_type': 'PBR',
    'address': 'null',
}

# register the device
requests.post('http://localhost:5000/device', json=test_PBR_device)

# configuration of a command for measurement of temperature
cmd = {'device_id': PBR_id,
       'command_id': '2',
       'await': True
      }

response = requests.post('http://localhost:5000/command', json=cmd)
print("The current temperature is", response.json()['data']['temp'])
```
