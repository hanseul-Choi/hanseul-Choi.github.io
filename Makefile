.PHONY: install lint format typecheck imports test build verify serve clean

VENV := .venv
PYTHON := $(VENV)/bin/python
UV := uv

install:
	$(UV) venv --python 3.11 --allow-existing
	$(UV) pip install -e ".[dev]"

lint:
	$(UV) run ruff check .
	$(UV) run ruff format --check .

format:
	$(UV) run ruff format .
	$(UV) run ruff check --fix .

typecheck:
	$(UV) run mypy

imports:
	$(UV) run lint-imports

test:
	$(UV) run pytest

build:
	$(UV) run python -m sitebuilder build

# Single verification gate — AGENTS.md rule 13 requires this after every change.
verify: lint typecheck imports test build

serve:
	$(UV) run python -m sitebuilder serve

clean:
	rm -rf dist .pytest_cache .mypy_cache .ruff_cache .coverage
