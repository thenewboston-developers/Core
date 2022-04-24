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
	docker-compose -f docker-compose.dev.yml up --force-recreate db redis

.PHONY: run-server
run-server:
	poetry run python -m core.manage runserver 127.0.0.1:8000

.PHONY: lint
lint:
	poetry run pre-commit run --all-files

.PHONY: test
test:
	poetry run pytest -v -rs -n auto --show-capture=no

.PHONY: test-stepwise
test-stepwise:
	poetry run pytest --reuse-db --sw -vv --show-capture=no

.PHONY: lint-and-test
lint-and-test: lint test ;
