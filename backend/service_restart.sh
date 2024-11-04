#!/bin/bash
PID=$(ps aux | grep "flask" | grep -v grep | awk '{print $2}')
kill $PID
clear
echo "be patient ;=)"
sleep 2 
flask run 