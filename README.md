## Runner

### Install
`sudo -E env "PATH=$PATH" scripts/setup_runner.sh "<username>" "<password>"`

### Run in devel mode
`./run.sh -h '<host>' -p <port>`

with given optional `host` (default localhost) and `port` (default 5000).

### Run in deploy mode
`cd scripts && ./redeploy.sh`

---

## Builder
`sudo -E env "PATH=$PATH" scripts/setup_builder.sh`

### Build new Docker image
`scripts/rebuild.sh`

---

### to run tests all tests (including integration tests):
`tests/run_tests.sh`
#### to run a single test case
`tests/run_tests.sh tests.<file name without .py>`

### to migrate database
`migrations/migrate.sh`
