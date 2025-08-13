#!/bin/bash

rm db.sqlite3
rm -rf ./workoutapi/migrations
python3 manage.py migrate
python3 manage.py makemigrations workoutapi
python3 manage.py migrate workoutapi
python3 manage.py loaddata users
python3 manage.py loaddata tokens
python manage.py loaddata workout_types
python3 manage.py loaddata workouts
python3 manage.py loaddata exercises
python3 manage.py loaddata muscle_groups
python3 manage.py loaddata exercise_muscle_groups
python3 manage.py loaddata workout_exercises
