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

.PHONY: update
update: install migrate;

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
