[![Python Package](https://github.com/SmartBioTech/DeviceControl/actions/workflows/python-flask.yml/badge.svg)](https://github.com/SmartBioTech/DeviceControl/actions/workflows/python-flask.yml)

# DeviceControl

TBA description

## Runner

Runner is a machine where `DeviceControl` will run in `docker` container. This machine first needs to be prepared for this task. It includes:

1.  run runner installation script (which prepares local database):

`sudo -E env "PATH=$PATH" scripts/setup_runner.sh "<username>" "<password>"`

2. enable connections to your mySQL database from outside of localhost (might even require to open firewall for port 3306)

3. start docker image:

`cd scripts/ && ./redeploy.sh`

> Optionally install package `requests` for your local `python` installation to try the API locally. 

---

## Builder

### Install builder
`sudo -E env "PATH=$PATH" scripts/install_docker.sh`

### Build new docker image
`scripts/rebuild.sh`

---

## DEVELOPERS only

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
