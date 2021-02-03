
up:
	docker-compose up

manage:
	docker-compose exec projectx /home/user/venv/bin/python /home/user/backend/app/manage.py ${command}

build:
	yarn --cwd frontend install
	yarn --cwd frontend bic
	yarn --cwd tests install
	docker-compose build projectx

lint:
	pycodestyle backend/app/ backend/tests/
	pylint backend/app
	isort --check-only --diff backend/app backend/tests
	unify --check-only --recursive --quote \" backend/app backend/tests

fix_lint:
	autopep8 -i -r backend/app/ backend/tests/
	isort backend/app backend/tests
	unify --in-place --recursive --quote \" backend/app backend/tests
