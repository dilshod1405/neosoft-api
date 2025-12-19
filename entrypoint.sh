#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
until nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 1
done

echo "PostgreSQL is ready."

echo "Applying migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

exec "$@"
