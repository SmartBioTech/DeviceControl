# /bin/bash
export FLASK_APP=flasky.py

# do in a separate install script?
# create DBs and give rights
flask db init
# + install requirements
# + set all environ variables needed

flask run
