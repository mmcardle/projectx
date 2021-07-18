#!/usr/bin/bash

echo "Wait for Database"
/home/user/.venv/bin/python /home/user/manage.py check_db_connection

echo "Applying any migrations"
/home/user/.venv/bin/python /home/user/manage.py migrate

if [ -z "${DEBUG}" ]
then
    export UVICORN_ARGS="--uds /tmp/uvicorn.sock"
    export UVICORN_PROCESSES="4"
else
    export UVICORN_ARGS="--port 8002 --reload"
    export UVICORN_PROCESSES="1"
fi

echo "Running Uvicorn ${UVICORN_PROCESSES} processes with args - ${UVICORN_ARGS}"

nginx -g "daemon on;"
circusd /home/user/config/circus.ini