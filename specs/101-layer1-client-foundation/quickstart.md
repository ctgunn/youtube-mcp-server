# Quickstart: YT-101 Layer 1 Shared Client Foundation

## Goal

Use this feature to introduce the internal Layer 1 foundation that later YouTube endpoint slices will extend.

## 1. Review the feature artifacts

- Read the specification: [/Users/ctgunn/Projects/youtube-mcp-server/specs/101-layer1-client-foundation/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/101-layer1-client-foundation/spec.md)
- Read the implementation plan: [/Users/ctgunn/Projects/youtube-mcp-server/specs/101-layer1-client-foundation/plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/101-layer1-client-foundation/plan.md)
- Read the wrapper contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/101-layer1-client-foundation/contracts/layer1-wrapper-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/101-layer1-client-foundation/contracts/layer1-wrapper-contract.md)

## 2. Implement the foundation in Red-Green-Refactor order

1. Add failing unit tests for wrapper metadata, auth modes, retry classification, and normalized failures.
2. Add failing integration tests for the representative wrapper execution path.
3. Add failing contract or integration coverage for one representative higher-layer consumer.
4. Implement the smallest internal integration module and typed wrapper surface needed to pass those tests.
5. Refactor for naming clarity, shared policy reuse, and complete reStructuredText docstrings on all new or changed Python functions.

Representative implementation modules:

- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/auth.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/errors.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/retry.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/executor.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

## 3. Keep the change scoped

- Keep Layer 1 internal-only.
- Do not add new public MCP tools as part of YT-101.
- Prove the design with one representative wrapper and one representative higher-layer consumer rather than broad endpoint coverage.

## 4. Verify before review

Run the targeted and full validation steps expected by the constitution:

```bash
cd /Users/ctgunn/Projects/youtube-mcp-server
python3 -m pytest tests/unit/test_layer1_foundation.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_consumer_contract.py
python3 -m pytest
ruff check .
```

## 5. Review readiness checklist

- Shared request execution exists for representative wrappers
- Auth modes are declared explicitly
- Quota metadata is mandatory and reviewable
- Retry and error behavior flows through shared policy surfaces
- Logging hooks are present at the shared executor boundary
- A representative higher-layer consumer uses typed Layer 1 methods
- All new or changed Python functions include reStructuredText docstrings
