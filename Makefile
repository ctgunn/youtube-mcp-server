dev:
	./scripts/dev_local.sh

dev-hosted:
	./scripts/local_compose.sh up -d
	LOCAL_SESSION_MODE=hosted ./scripts/dev_local.sh

dev-down:
	./scripts/local_compose.sh down

PYTHON ?= python3

.PHONY: lint typecheck test test-tools test-runtime test-live-smoke quality

lint:
	$(PYTHON) -m ruff check .

typecheck:
	$(PYTHON) -m mypy src/mcp_server

test:
	$(PYTHON) -m pytest

test-tools:
	PYTHONPATH=src $(PYTHON) -m pytest tests/integration/test_mcp_tool_catalog_endpoints.py

test-runtime:
	PYTHONPATH=src $(PYTHON) -m pytest tests/integration/test_mcp_configured_runtime_matrix.py

test-live-smoke:
	@set -a; \
	if [ -f .env.local ]; then . ./.env.local; \
	elif [ -f .env ]; then . ./.env; fi; \
	set +a; \
	PYTHONPATH=src $(PYTHON) scripts/verify_youtube_live.py

quality:
	$(MAKE) lint
	$(MAKE) typecheck
	$(MAKE) test
