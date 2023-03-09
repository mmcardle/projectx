#!/bin/sh

set -ex

poetry run python -m black --check backend/
poetry run python -m pylint backend/
poetry run python -m isort --check-only --diff backend/
poetry run python -m unify --check-only --recursive --quote \" backend/
# 51358 - The safety library itself
poetry run safety check -i 51358
poetry show --outdated
yarn --cwd frontend lint