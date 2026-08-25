# Layer 4 Tool-Catalog Verification Quickstart

## 1. Prepare the local environment

From the repository root, use the documented local development setup. The focused catalog suite needs no YouTube credential and makes no outbound YouTube request.

```bash
python -m pip install -e '.[dev]'
```

Do not place API keys, OAuth tokens, or other credentials in fixture definitions, command output, or checked-in configuration.

## 2. Run the focused catalog check

After implementation, run:

```bash
make test-tools
```

Expected evidence:

- the suite discovers the current default catalog through the public MCP route;
- every discovered tool has one individually reported route-invocation case;
- no fixture is missing or stale;
- successes contain structured content, and expected no-data failures have their documented safe category;
- no outbound YouTube request or destructive mutation occurs.

For direct focused debugging, run:

```bash
PYTHONPATH=src python3 -m pytest tests/integration/test_mcp_tool_catalog_endpoints.py
```

## 3. Run complete verification

After focused verification passes, run the mandatory repository quality gate:

```bash
make quality
```

This is the completion command. It runs linting, type checking, and the full test suite. Fix every failure before marking the feature complete.

## 4. Keep live verification separate

Catalog verification proves deterministic discovery and route dispatch only. It does not prove real credential configuration, API capability, quota behavior, or live YouTube results.

The existing live smoke test is separately opt-in, read-only, and requires both an explicit enablement flag and a real API credential. Do not include that workflow in `make test-tools`.

## 5. Correct catalog drift safely

If the focused suite reports a missing tool, add one reviewed safe fixture with object arguments and a success or documented safe-error expectation. If it reports a stale fixture, remove or update that fixture after confirming the current public catalog. Never solve either mismatch by adding a hard-coded catalog list or bypassing the public MCP routes.
