#!/bin/bash

# python manage.py flush --no-input
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --no-input #--clear

source /usr/src/gmx/bin/GMXRC.bash

exec "$@"

