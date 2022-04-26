.PHONY: build
build: build-core build-reverse-proxy;

.PHONY: build-core
build-core:
	docker build . --target=core -t core:current

.PHONY: build-reverse-proxy
build-reverse-proxy:
	docker build . --target=core-reverse-proxy -t core-reverse-proxy:current

.PHONY: superuser
superuser:
	 poetry run python -m core.manage createsuperuser

.PHONY: install
install:
	poetry install

.PHONY: migrations
migrations:
	 poetry run python -m core.manage makemigrations

.PHONY: migrate
migrate:
	 poetry run python -m core.manage migrate

.PHONY: install-pre-commit
install-pre-commit:
	poetry run pre-commit uninstall; poetry run pre-commit install

.PHONY: update
update: install migrate install-pre-commit ;

.PHONY: shell
shell:
	poetry run python -m core.manage shell

.PHONY: dbshell
dbshell:
	poetry run python -m core.manage dbshell

.PHONY: up-dependencies-only
up-dependencies-only:
	test -f .env || touch .env
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --force-recreate db redis

.PHONY: run-server
run-server:
	poetry run python -m core.manage runserver 127.0.0.1:8000

.PHONY: run-dockerized
run-dockerized: build
	grep -q -o CORESETTING_SECRET_KEY .env 2> /dev/null || echo "CORESETTING_SECRET_KEY=$$(xxd -c 48 -l 48 -p /dev/urandom)" >> .env
	docker-compose up --no-build --force-recreate

.PHONY: lint
lint:
	poetry run pre-commit run --all-files

.PHONY: test
test:
	poetry run pytest -v -rs -n auto --show-capture=no

.PHONY: test-stepwise
test-stepwise:
	poetry run pytest --reuse-db --sw -vv --show-capture=no

.PHONY: test-with-coverage
test-with-coverage:
	poetry run pytest -vv --cov=core --cov-report=html

.PHONY: lint-and-test
lint-and-test: lint test ;
