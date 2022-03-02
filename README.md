[![Python Package](https://github.com/SmartBioTech/DeviceControl/actions/workflows/python-flask.yml/badge.svg)](https://github.com/SmartBioTech/DeviceControl/actions/workflows/python-flask.yml)

# DeviceControl

TBA description

see [wiki](https://github.com/SmartBioTech/DeviceControl/wiki)

## Installation

`DeviceControl` runs in a `Docker` container with locally install database.
This decision was made in order to make data more persistent and prone to unintentional deletion.

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
    docker run -d --privileged -v /dev/serial/by-port/:/dev/serial/by-port/ -p 0.0.0.0:5000:5000 --restart unless-stopped --add-host="database:$DATABASE" --env-file DB_CONFIG --name "devicecontrol" bioarineo/devicecontrol:<platform>
    ```

    where `<platform>` is either `amd` or `arm`. The `by-port` is mapped to `docker` file system to access devices connected to I/O ports.

`DeviceControl` is running and ready to be used.

Inspect and execute `scripts/example_run.py` to see demonstration of tool's usability on a simulated device.

---

## Developers only

### Run in devel mode
`./run.sh -h '<host>' -p <port>`

with given optional `host` (default localhost) and `port` (default 5000).
Note that first you need to locally install requirements:

`python3 -m pip install -r requirements.txt`

### to run tests all tests (including integration tests):
`tests/run_tests.sh`
#### to run a single test case
`tests/run_tests.sh tests.<file name without .py>`

### to migrate database
`migrations/migrate.sh`
