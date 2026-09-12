.PHONY: up down build logs status reset test

up:
	docker compose up -d --build

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f checker

status:
	docker compose ps
	docker compose logs --tail=30 checker

test:
	docker compose run --rm -e CHECK_ONCE=1 -e CHECK_INTERVAL=0 checker

reset:
	docker compose down -v
