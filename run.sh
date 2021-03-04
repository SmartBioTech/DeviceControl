# /bin/bash

FILE=DB_CONFIG
if [ -f "$FILE" ]; then
    # set all environ variables needed (using DB_CONFIG)
    . $FILE
    export USERNAME="$USER"
    export PASSWORD="$PASSWORD"

    if [ "$#" -eq 1 ]; then
      export FLASK_CONFIG="$1"
      export FLASK_ENV="$1"
    fi

    export FLASK_APP=main.py
    flask db upgrade
    flask run
else
    echo "$FILE file does not exist."
fi
