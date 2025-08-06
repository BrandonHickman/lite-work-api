#!/bin/bash

rm db.sqlite3
rm -rf ./workoutapi/migrations
python3 manage.py migrate
python3 manage.py makemigrations workoutapi
python3 manage.py migrate workoutapi
python3 manage.py loaddata users
python3 manage.py loaddata tokens

