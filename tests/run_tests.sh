export FLASK_CONFIG="testing"
export FLASK_ENV="testing"
export database="localhost"
export USERNAME=" "
export PASSWORD=" "
export FLASK_APP=main.py
flask test "$1"