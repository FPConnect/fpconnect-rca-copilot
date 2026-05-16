.PHONY: up down build test lint migrate dev-mobile install-mobile test-mobile

up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build

logs:
	docker-compose logs -f

test-api:
	cd apps/api && python -m pytest tests/ -v

test-web:
	cd apps/web && npm test

test-mobile:
	cd apps/mobile && npm test

lint-api:
	cd apps/api && ruff check app/ tests/

lint-web:
	cd apps/web && npm run lint

migrate:
	cd apps/api && alembic upgrade head

install-api:
	cd apps/api && pip install -r requirements.txt

install-web:
	cd apps/web && npm install

install-mobile:
	cd apps/mobile && npm install

dev-api:
	cd apps/api && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-web:
	cd apps/web && npm run dev

dev-mobile:
	cd apps/mobile && npm run start

format-api:
	cd apps/api && ruff format app/ tests/

seed-api:
	cd apps/api && python scripts/seed_clinical.py
