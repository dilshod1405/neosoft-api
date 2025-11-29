#!/bin/bash

set -e

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Applying database migrations..."
python manage.py migrate

echo "Starting Gunicorn..."
exec gunicorn edu_neosoft_api.wsgi:application --bind 0.0.0.0:8000 --workers 3
