# /bin/bash
export FLASK_APP=main.py
flask db upgrade
# + set all environ variables needed (using CONFIG)
flask run
