.PHONY: test lint format check shell migrate makemigrations

test:
	docker compose run --rm backend pytest

lint:
	docker compose run --rm backend ruff check .

format:
	docker compose run --rm backend ruff format .

check:
	make lint
	make test

shell:
	docker compose run --rm backend python manage.py shell

migrate:
	docker compose run --rm backend python manage.py migrate

makemigrations:
	docker compose run --rm backend python manage.py makemigrations