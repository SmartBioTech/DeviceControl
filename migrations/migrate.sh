# /bin/bash

FILE=DB_CONFIG
if [ -f "$FILE" ]; then
    # set all environ variables needed (using DB_CONFIG)
    . $FILE
    export USERNAME="$USER"
    export PASSWORD="$PASSWORD"

    export FLASK_APP=main.py
    flask db migrate
else
    echo "$FILE file does not exist."
fi
