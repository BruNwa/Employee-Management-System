#!/bin/bash
echo "init service restart..."
pkill -HUP gunicorn || true
exec gunicorn --reload -w 4 -b 0.0.0.0:8000 "app:app" > /dev/null 2>&1