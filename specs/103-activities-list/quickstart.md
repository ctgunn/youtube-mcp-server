# Quickstart: YT-103 Layer 1 Endpoint `activities.list`

## Goal

Use this feature to add a reviewable internal `activities.list` wrapper on top of the existing Layer 1 foundation, with clear quota visibility, explicit `channelId` versus `mine` and `home` guidance, and deterministic rejection of unsupported filter combinations.

## 1. Review the feature artifacts

- Read the specification: [/Users/ctgunn/Projects/youtube-mcp-server/specs/103-activities-list/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/103-activities-list/spec.md)
- Read the implementation plan: [/Users/ctgunn/Projects/youtube-mcp-server/specs/103-activities-list/plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/103-activities-list/plan.md)
- Read the wrapper contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/103-activities-list/contracts/layer1-activities-wrapper-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/103-activities-list/contracts/layer1-activities-wrapper-contract.md)
- Read the auth and filter contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/103-activities-list/contracts/layer1-activities-auth-filter-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/103-activities-list/contracts/layer1-activities-auth-filter-contract.md)

## 2. Implement the feature in Red-Green-Refactor order

1. Add failing unit tests for `activities.list` metadata completeness, quota visibility, and endpoint-specific filter validation.
2. Add failing contract tests for maintainer-facing artifacts that must explain supported public-channel and authorized-user filter modes.
3. Add failing integration tests showing the representative wrapper path does not yet make `activities.list` reusable for higher-layer planning.
4. Implement the smallest updates to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and any narrowly necessary supporting integration modules needed to satisfy those failures.
5. Ensure the wrapper review surface exposes endpoint identity, `quotaCost`, mixed-auth guidance, and the supported selector boundary `channelId`/`mine`/`home` clearly enough for YT-203 planning.
6. Refactor for naming clarity, reduced duplication, and complete reStructuredText docstrings on all new or changed Python functions.

Representative implementation modules:

- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/auth.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/executor.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`

## 3. Keep the change scoped

- Keep YT-103 internal-only.
- Do not add a public `activities_list` MCP tool here; that belongs to YT-203.
- Reuse the YT-101 executor and YT-102 metadata standards instead of inventing a second endpoint-wrapper abstraction.
- Focus on filter interpretation, auth visibility, quota visibility, and valid empty results rather than broad activities-resource expansion.

## 4. Verify before review

Run the targeted and full validation steps expected by the constitution:

```bash
cd /Users/ctgunn/Projects/youtube-mcp-server
python3 -m pytest tests/unit/test_layer1_foundation.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_metadata_contract.py tests/contract/test_layer1_consumer_contract.py
python3 -m pytest
ruff check .
```

## 5. Review readiness checklist

- `activities.list` wrapper metadata shows endpoint identity and the quota cost of `1`
- Maintainer-facing artifacts distinguish public-channel usage from authorized-user usage
- Unsupported or ambiguous filter combinations are rejected or clearly flagged before execution
- Empty valid activity responses remain successful outcomes
- No public MCP tool or hosted behavior changes are introduced in this slice
- Existing Layer 1 execution behavior remains intact outside the endpoint-specific additions
- All new or changed Python functions include reStructuredText docstrings
