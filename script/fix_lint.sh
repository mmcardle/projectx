#!/bin/sh

set -ex

poetry run python -m black backend/
poetry run python -m isort backend/
#poetry run python -m unify --in-place --recursive --quote \" backend/
