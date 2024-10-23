#!/bin/bash

/usr/sbin/sshd
while ! nc -z db 3306; do
  echo "Waiting for MySQL to be ready..."
  sleep 1
done

echo "MySQL is ready. Applying migrations..."
flask db upgrade  
echo "Starting the App..."
python3 app.py