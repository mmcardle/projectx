
up:
	docker-compose up

manage:
	docker-compose exec projectx /home/user/.venv/bin/python /home/user/backend/app/manage.py ${command}

fast_api:
	uvicorn --app-dir=backend/app/ api.wsgi:application --reload --port 8001

build:
	yarn --cwd frontend install
	yarn --cwd frontend bic
	yarn --cwd tests install
	docker-compose build projectx

lint:
	black --check backend/
	pylint backend/app backend/test_apps/
	isort --check-only --diff backend/
	unify --check-only --recursive --quote \" backend/

fix_lint:
	black backend/
	isort backend/
	unify --in-place --recursive --quote \" backend/
