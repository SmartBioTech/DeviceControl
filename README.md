### to install the tool:
`sudo -E env "PATH=$PATH" ./setup.sh "<username>" "<password>"`

### to run the tool
`./run.sh -h '<host>' -p <port>`

with given optional `host` (default localhost) and `port` (default 5000). 

### to run tests all tests (including integration tests):
`tests/run_tests.sh`
#### to run a single test case
`tests/run_tests.sh tests.<file name without .py>`

### to migrate database
`migrations/migrate.sh`
