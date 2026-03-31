# Quickstart: FND-026 Local Runtime Ergonomics and Environment Entry Point

## Objective

Verify that the repository exposes one canonical local startup path for day-to-day development, keeps `.env.local` as the dedicated local defaults source, and preserves hosted-like local verification as a clear companion workflow for durable-session checks.

## Prerequisites

- Python 3.11+
- Feature branch: `026-local-runtime-entrypoint`
- Repository dependencies installed with `python3 -m pip install -e .`
- Local container runtime available when exercising the hosted-like local verification path

## Execution Baseline

- Treat `scripts/dev_local.sh` as the canonical local startup entry point.
- Treat `.env.local` as the dedicated local defaults file for minimal local runtime.
- Treat hosted-like local verification as an opt-in path layered on the same startup entry point.
- Keep hosted deployment inputs out of the default local workflow.

## Implementation Targets

- Minimal local runtime uses one documented startup command from the repository workspace.
- Local defaults are loaded automatically from the dedicated local environment file.
- Hosted-like local verification clearly documents dependency bootstrap, startup, shutdown, and failure recovery.
- Documentation distinguishes local baseline variables from hosted-like local overrides and hosted deployment-only inputs.

## Red Phase (write failing tests and checks first)

1. Add failing integration or documentation tests showing the root README still leads with manual inline runtime commands instead of one canonical local entry point.
2. Add failing contract or integration tests showing the local workflow does not yet clearly state the role of `.env.local`, hosted-like mode selection, or Redis dependency failure guidance.
3. Add failing checks proving the local and hosted-like variable boundaries remain implicit or duplicated across docs.
4. Run the targeted suites and confirm failures:

```bash
python3 -m pytest \
  tests/contract/test_iac_foundation_contract.py \
  tests/integration/test_cloud_run_docs_examples.py \
  tests/integration/test_cloud_agnostic_infrastructure_workflows.py \
  tests/integration/test_iac_foundation_workflows.py
```

## Green Phase (minimal implementation)

1. Update the root local-runtime guidance to point to `scripts/dev_local.sh` as the canonical startup entry point.
2. Keep `.env.local` as the documented baseline source for local defaults and clarify what it covers.
3. Keep `infrastructure/local/README.md` and `infrastructure/local/.env.example` scoped to the hosted-like companion workflow.
4. Add the smallest documentation, script, or test changes needed to prove the minimal local and hosted-like local flows are distinct and complete.
5. Re-run the targeted suites until they pass:

```bash
python3 -m pytest \
  tests/contract/test_iac_foundation_contract.py \
  tests/integration/test_cloud_run_docs_examples.py \
  tests/integration/test_cloud_agnostic_infrastructure_workflows.py \
  tests/integration/test_iac_foundation_workflows.py
```

## Refactor Phase (behavior-preserving cleanup)

1. Remove duplicated local startup instructions and variable lists between the root README, local infrastructure docs, and startup script guidance.
2. Keep one consistent naming model for `minimal local runtime` and `hosted-like local verification`.
3. Re-run the full repository verification flow:

```bash
python3 -m pytest
ruff check .
```

## Minimal Local Runtime

Start the server through the canonical local entry point:

```bash
bash scripts/dev_local.sh
```

Expected logical evidence:

- `.env.local` is loaded automatically
- the server starts with the baseline local runtime profile
- no cloud deployment configuration is required

## Hosted-Like Local Verification

1. Start the local durable-session dependency:

```bash
docker compose -f infrastructure/local/compose.yaml up -d
```

2. Start the same local entry point in hosted-like mode:

```bash
LOCAL_SESSION_MODE=hosted bash scripts/dev_local.sh
```

Expected logical evidence:

- the local dependency is running
- the same startup entry point launches the app with hosted-like session settings
- durable-session checks can be exercised locally without cloud provisioning

3. Stop the local dependency when finished:

```bash
docker compose -f infrastructure/local/compose.yaml down
```

## Failure Validation

1. Remove or rename `.env.local`, then start the local entry point and verify the failure explains that the local defaults file is missing.
2. Skip the Redis bootstrap, start hosted-like local mode, and verify the failure or readiness guidance points back to the dependency bootstrap path.
3. Restore the baseline local workflow and verify that minimal local runtime remains available even when hosted-like prerequisites are absent.

## Success Evidence

- Developers can identify one canonical local startup command.
- `.env.local` is clearly documented as the baseline local defaults file.
- Hosted-like local verification remains a companion path rather than the default local mode.
- Failure guidance is explicit for missing local defaults and missing hosted-like dependency prerequisites.
