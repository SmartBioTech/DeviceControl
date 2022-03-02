#!/bin/bash

host="localhost"
test_case=""

while [ $# -gt 0 ]; do

   if [[ $1 == *"--"* ]]; then
        param="${1/--/}"
        declare $param="$2"
   fi

  shift
done

export FLASK_CONFIG="testing"
export FLASK_ENV="testing"
export database="$host"
export USERNAME=" "
export PASSWORD=" "
export FLASK_APP=main.py
flask test "$test_case"
exit $?
