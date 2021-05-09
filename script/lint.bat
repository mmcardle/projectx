black --check backend/
pylint backend/app backend/testing_apps/
isort --check-only --diff backend/
unify --check-only --recursive --quote \" backend/