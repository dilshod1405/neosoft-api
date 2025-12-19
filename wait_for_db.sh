#!/bin/sh
until nc -z "$DB_HOST" "$DB_PORT"; do
  echo "Waiting for PostgreSQL to start..."
  sleep 1
done
echo "PostgreSQL is ready — starting the application"
exec "$@"
