# Quickstart: Verify the Layer 1 Live Execution Runtime

## 1. Prepare a development environment

From `/Users/ctgunn/Projects/youtube-mcp-server`:

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -e .
```

Use `.env.local` or another local environment mechanism. Never commit credentials.

## 2. Configure only the credentials needed for the verification path

```bash
export MCP_ENVIRONMENT=dev
export YOUTUBE_API_KEY='replace-with-a-local-secret'
# Required only for an OAuth-required verification path:
export YOUTUBE_OAUTH_TOKEN='replace-with-a-local-secret'
```

Do not paste these values into test fixtures, expected output, issue comments, logs, or documentation. A missing required credential must yield a safe failure, never sample data.

## 3. Run focused Red-Green checks

```bash
python3 -m pytest \
  tests/unit/test_runtime_config_validation.py \
  tests/unit/test_layer1_foundation.py \
  tests/unit/test_youtube_transport.py \
  tests/integration/test_layer1_foundation.py \
  tests/contract/test_layer1_consumer_contract.py \
  tests/contract/test_layer1_resource_modules_contract.py
```

Verify that controlled-openers prove the configured runtime selected the live transport, while making no real external request. Confirm tests cover API-key and OAuth selection, JSON and media request forms, retryable and terminal failures, and redaction.

## 4. Verify the configured public-tool path

Run the focused public descriptor or MCP transport integration test added for this feature. It must inject a controlled opener through normal configured app/dispatcher composition and fail if a representative executor or placeholder credential is selected.

## 5. Verify missing-credential behavior

Unset the credential required by the chosen path and run the focused configuration/failure test. Expected result: a normalized safe configuration or authorization failure with no credential value and no representative successful payload.

## 6. Run final quality gates

```bash
python3 -m pytest
python3 -m ruff check .
```

Both commands must pass after the final code change. Review changed Python functions for complete reStructuredText docstrings covering purpose, inputs, outputs, raised errors where relevant, and side effects, without recording secret values.
