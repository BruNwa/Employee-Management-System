#!/bin/bash

/usr/sbin/sshd
while ! nc -z db 3306; do
  echo "Waiting for MySQL to be ready..."
  sleep 1
done

echo "MySQL is ready. Applying migrations..."
flask db upgrade  
echo "Starting Gunicorn..."
exec gunicorn -w 4 -b 0.0.0.0:8000 "app:app"