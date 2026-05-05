# Quickstart: YT-143 Layer 1 Endpoint `subscriptions.delete`

## Goal

Add a reviewable internal `subscriptions.delete` wrapper on top of the existing Layer 1 foundation with explicit target-subscription rules, OAuth-required visibility, deterministic delete-target validation, quota visibility, and normalized deletion-acknowledgment outcomes suitable for downstream reuse.

## 1. Review the feature artifacts

- Read the specification: [/Users/ctgunn/Projects/youtube-mcp-server/specs/143-subscriptions-delete/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/143-subscriptions-delete/spec.md)
- Read the implementation plan: [/Users/ctgunn/Projects/youtube-mcp-server/specs/143-subscriptions-delete/plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/143-subscriptions-delete/plan.md)
- Read the research decisions: [/Users/ctgunn/Projects/youtube-mcp-server/specs/143-subscriptions-delete/research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/143-subscriptions-delete/research.md)
- Read the wrapper contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/143-subscriptions-delete/contracts/layer1-subscriptions-delete-wrapper-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/143-subscriptions-delete/contracts/layer1-subscriptions-delete-wrapper-contract.md)
- Read the auth-delete contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/143-subscriptions-delete/contracts/layer1-subscriptions-delete-auth-delete-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/143-subscriptions-delete/contracts/layer1-subscriptions-delete-auth-delete-contract.md)

## 2. Implement in Red-Green-Refactor order

1. Add failing unit tests for `subscriptions.delete` metadata completeness, quota visibility, OAuth enforcement, required target identifier validation, and unsupported-field rejection.
2. Add failing transport tests for request construction and normalized result handling for valid, invalid, unavailable-target, and upstream-rejected delete profiles.
3. Add failing integration and contract tests showing the representative wrapper path does not yet make `subscriptions.delete` reusable for higher-layer planning.
4. Implement the smallest updates to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py` needed to satisfy those failures, including the internal higher-layer review path for subscription deletion.
5. Ensure review surfaces keep operation identity, quota cost, delete preconditions, authorization expectations, and unavailable-target guidance visible without exposing credentials.
6. Refactor for naming clarity and duplication reduction while preserving deterministic delete validation and normalized outcome boundaries.
7. Add or preserve reStructuredText docstrings for every new or changed Python function.

Representative test modules:

- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_subscriptions_contract.py`

## 3. Keep scope constrained

- Keep YT-143 internal-only.
- Do not add a public `subscriptions_delete` MCP tool in this slice.
- Reuse existing Layer 1 executor and metadata abstractions.
- Focus on delete-target rules, quota visibility, OAuth-required behavior, and normalized deletion outcomes.

## 4. Verify before review

Run targeted and full validation expected by the constitution:

```bash
cd /Users/ctgunn/Projects/youtube-mcp-server
python3 -m pytest tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_metadata_contract.py tests/contract/test_layer1_consumer_contract.py tests/contract/test_layer1_subscriptions_contract.py
python3 -m pytest
python3 -m ruff check .
```

## 5. Review readiness checklist

- `subscriptions.delete` wrapper metadata shows endpoint identity and quota cost `50`
- Delete preconditions are clear
- OAuth-required behavior is explicit and public-only delete access is not implied
- Missing authorization and malformed delete requests fail clearly
- Unavailable delete targets remain distinguishable from local validation failures
- Normalized upstream delete failures remain distinguishable from local validation failures
- Deletion acknowledgment keeps the targeted subscription identity visible
- No public MCP or hosted behavior changes are introduced
- All new or changed Python functions include reStructuredText docstrings
