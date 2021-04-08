#!/bin/sh
export FLASK_APP=main.py
flask db upgrade
exec gunicorn -b 0.0.0.0:5000 --access-logfile - --error-logfile - main:app
