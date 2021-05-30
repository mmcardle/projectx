
up:
	docker-compose up

manage:
	docker-compose exec projectx pipenv run ./manage.py ${command}

fast_api:
	uvicorn --app-dir=backend/ projectx.api.asgi:application --reload --port 8001

build:
	yarn --cwd frontend install
	yarn --cwd frontend bic
	yarn --cwd tests install
	docker-compose build projectx

lint:
	black --check backend/
	pylint backend/
	isort --check-only --diff backend/
	unify --check-only --recursive --quote \" backend/

fix_lint:
	black backend/
	isort backend/
	unify --in-place --recursive --quote \" backend/
