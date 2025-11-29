#!/bin/sh
until nc -z db 5432; do
    echo "Waiting for PostgreSQL to start..."
    sleep 1
done
echo "PostgreSQL is ready — starting the application"
exec "$@"
