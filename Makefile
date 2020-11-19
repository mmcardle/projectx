
up:
	docker-compose up

manage:
	docker-compose exec projectx /home/user/venv/bin/python /home/user/backend/app/manage.py

build:
	cd frontend && yarn install
	cd frontend && yarn build
	cd tests && yarn install
	docker-compose build projectx
