#!/bin/bash

/usr/sbin/sshd
while ! nc -z db 3306; do
  echo "Waiting for MySQL to be ready..."
  sleep 1
done
echo "MySQL is ready. Applying migrations..."
flask db upgrade  
export FLASK_ENV=development
echo "Starting flask app..."
python3 app.py &
FLASK_PID=$!  #get the app process id 
while true; do
    if ! kill -0 $FLASK_PID >/dev/null 2>&1; then
        echo "the app has crashed, the container is running for debugging."
        break
    fi
    sleep 5
done
tail -f /dev/null