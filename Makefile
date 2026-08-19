dev:
	./scripts/dev_local.sh

dev-hosted:
	./scripts/local_compose.sh up -d
	LOCAL_SESSION_MODE=hosted ./scripts/dev_local.sh

dev-down:
	./scripts/local_compose.sh down

PYTHON ?= python3

.PHONY: lint typecheck test quality

lint:
	$(PYTHON) -m ruff check .

typecheck:
	$(PYTHON) -m mypy src/mcp_server

test:
	$(PYTHON) -m pytest

quality:
	$(MAKE) lint
	$(MAKE) typecheck
	$(MAKE) test
