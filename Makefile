.PHONY: createsuperuser
createsuperuser:
	 poetry run python -m manage createsuperuser

.PHONY: install
install:
	poetry install

.PHONY: makemigrations
makemigrations:
	 poetry run python -m manage makemigrations

.PHONY: migrate
migrate:
	 poetry run python -m manage migrate

.PHONY: shell
shell:
	 poetry run python -m manage shell