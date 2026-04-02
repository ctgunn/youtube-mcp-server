dev:
	./scripts/dev_local.sh

dev-hosted:
	./scripts/local_compose.sh up -d
	LOCAL_SESSION_MODE=hosted ./scripts/dev_local.sh

dev-down:
	./scripts/local_compose.sh down
