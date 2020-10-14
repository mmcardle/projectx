#!/usr/bin/env bash
PYTHONIOENCODING=utf-8

echo "Applying any migrations"
/home/user/venv/bin/python /home/user/backend/app/manage.py migrate

nginx -g "daemon on;"
circusd  /home/user/config/circus.ini