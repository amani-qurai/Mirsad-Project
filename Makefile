# Mirsad — shared commands for both halves of the repo (ADR-0001 §8).
# Run `make help` for the list.

PYTHON ?= .venv/bin/python

.DEFAULT_GOAL := help
.PHONY: help up down logs ps install test test-api test-web check-locales typecheck build ci

help: ## List the targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-14s %s\n", $$1, $$2}'

up: ## Build and start db, api and web
	docker compose up --build -d --wait

down: ## Stop the stack (the database volume is kept)
	docker compose down

logs: ## Follow the stack's logs
	docker compose logs -f

ps: ## Show the stack's containers
	docker compose ps

install: ## Install backend and web dependencies locally
	$(PYTHON) -m pip install -e 'backend[dev]'
	cd frontend && npm ci

test: test-api test-web check-locales ## Run every test

test-api: ## Backend tests
	cd backend && ../$(PYTHON) -m pytest -q

test-web: ## Web tests
	cd frontend && npm test

check-locales: ## ar.json and en.json carry the same keys (NN-1)
	$(PYTHON) scripts/check_locale_parity.py

typecheck: ## TypeScript check
	cd frontend && npm run -s typecheck

build: ## Build the web app
	cd frontend && npm run -s build

ci: test typecheck build ## What CI runs, minus the Docker job
