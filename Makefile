dev:
	./scripts/dev_local.sh

dev-hosted:
	docker compose -f infrastructure/local/compose.yaml up -d
	LOCAL_SESSION_MODE=hosted ./scripts/dev_local.sh

dev-down:
	docker compose -f infrastructure/local/compose.yaml down
