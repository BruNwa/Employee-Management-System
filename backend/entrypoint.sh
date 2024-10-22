#!/bin/bash
set -e
echo "Waiting for database..."
while ! nc -z db 3306; do
  sleep 1
done
echo "Database is up and running!"
echo "Running migrations..."
flask db upgrade
echo "Starting Flask application..."
exec gunicorn -w 4 -b 0.0.0.0:8000 "app:app"