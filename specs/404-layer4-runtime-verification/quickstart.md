# Layer 4 Configured-Runtime Verification Quickstart

## 1. Prepare a safe local environment

From the repository root:

```bash
python -m pip install -e '.[dev]'
```

Do not add API keys, OAuth tokens, authorization headers, private IDs, raw upstream results, or request bodies to fixtures, command output, or checked-in files.

## 2. Run deterministic catalog verification

```bash
make test-tools
```

This checks the default catalog with local deterministic fixtures. It does not prove configured YouTube access and makes no outbound YouTube request.

## 3. Run deterministic configured-runtime verification

After implementation, run:

```bash
make test-runtime
```

Expected evidence:

- discovery-derived coverage for every configured YouTube family;
- separately reported API-key, OAuth-required, or unavailable-capability cases;
- public MCP route invocation only;
- controlled request construction for executable cases;
- zero external network activity and zero representative local fallback in configured cases; and
- redacted result, error, and diagnostic evidence.

For focused debugging, run:

```bash
PYTHONPATH=src python3 -m pytest tests/integration/test_mcp_configured_runtime_matrix.py
PYTHONPATH=src python3 -m pytest tests/integration/test_layer1_live_runtime.py
```

## 4. Run the optional local live smoke only with approval

The following command is manual, read-only, credential-gated, quota-consuming, and dependent on upstream availability. Use only an approved credential and never copy its value into shell history, logs, test evidence, or documentation.

```bash
RUN_YOUTUBE_LIVE_SMOKE=1 YOUTUBE_API_KEY='operator-supplied-value' make test-live-smoke
```

Expected evidence:

- preflight failure without the explicit flag or required credential, before any live request;
- only explicit reviewed API-key public-read allowlist entries run;
- excluded operations are reported but not invoked;
- each selected tool has a separate safe result; and
- output contains no credentials, authorization material, headers, full inputs, or upstream response bodies.

Do not run this command as part of `make test`, `make quality`, CI, or automated deployment. It verifies the local configured application boundary only; OPS-405 covers a running remote MCP endpoint.

## 5. Run required completion evidence

After focused checks pass, run:

```bash
make quality
```

This is the required completion command. It runs linting, type checking, and the full repository test suite. Fix every failure before marking the feature complete.

## 6. Handle failures safely

- Missing or stale matrix families: update the reviewed matrix record after confirming current public discovery metadata; do not add a duplicate hard-coded catalog.
- API-key or OAuth classification failure: correct the case's explicit selector/capability expectation or the configured runtime behavior; do not substitute representative local results.
- Any secret-like text in an error or report: treat it as a security defect, stop sharing the output, and correct the relevant reporting/sanitization boundary before rerunning.
- Live smoke failure: record only the safe tool identity and classification; inspect credentials and upstream status outside committed evidence, then retry only when authorized.
