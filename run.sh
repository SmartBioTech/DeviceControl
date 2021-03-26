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

    HOST="localhost"
    PORT=5000
    while getopts ":h:p:" opt; do
      case $opt in
        h) HOST="$OPTARG"
        ;;
        p) PORT=$OPTARG
        ;;
        \?) echo "Invalid option -$OPTARG" >&2
        ;;
      esac
    done

    flask run --host=$HOST --port=$PORT
else
    echo "$FILE file does not exist."
fi
