#!/usr/bin/bash

echo "Applying any migrations"
/home/user/.venv/bin/python /home/user/backend/app/manage.py migrate

if [ -z "${DEBUG}" ]
then
    export UVICORN_ARGS="--uds /tmp/uvicorn\$(circus.wid).sock"
    export UVICORN_PROCESSES="4"
else
    export UVICORN_ARGS="--port 8002 --reload"
    export UVICORN_PROCESSES="1"
fi

echo "Running Uvicorn with - ${UVICORN_ARGS} - ${UVICORN_PROCESSES}"

nginx -g "daemon on;"
circusd /home/user/config/circus.ini