## Runner

Runner is a machine where `DeviceControl` will run in `docker` container. This machine first needs to be prepared for this task. It includes:

1. install `docker` (we recommend [these](https://phoenixnap.com/kb/docker-on-raspberry-pi) instructions)
2. run runner installation script (which prepares local database):

`sudo -E env "PATH=$PATH" scripts/setup_runner.sh "<username>" "<password>"`

3. enable connections to your mySQL database from outside of localhost (might even require to open firewall for port 3306)

---

## Builder
`sudo -E env "PATH=$PATH" scripts/setup_builder.sh`

### Build new Docker image
`scripts/rebuild.sh`

---

## DEVELOPERS only

### Run in devel mode
`./run.sh -h '<host>' -p <port>`

with given optional `host` (default localhost) and `port` (default 5000).

### to run tests all tests (including integration tests):
`tests/run_tests.sh`
#### to run a single test case
`tests/run_tests.sh tests.<file name without .py>`

### to migrate database
`migrations/migrate.sh`
