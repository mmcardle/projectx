#!/bin/sh

set -ex

poetry run python -m black --check backend/
poetry run python -m pylint backend/
poetry run python -m isort --check-only --diff backend/
poetry run python -m unify --check-only --recursive --quote \" backend/
poetry run safety check
poetry show --outdated
yarn --cwd frontend lint