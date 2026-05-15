# Quickstart: YT-152 Layer 1 Endpoint `videos.reportAbuse`

## Goal

Use this feature to add a reviewable internal `videos.reportAbuse` wrapper on top of the existing Layer 1 foundation, with clear quota visibility, visible OAuth-only expectations, deterministic abuse-report body validation, explicit optional payload guidance, and normalized acknowledgement outcomes suitable for downstream reuse.

## 1. Review the feature artifacts

- Read the specification: [/Users/ctgunn/Projects/youtube-mcp-server/specs/152-videos-report-abuse/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/152-videos-report-abuse/spec.md)
- Read the implementation plan: [/Users/ctgunn/Projects/youtube-mcp-server/specs/152-videos-report-abuse/plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/152-videos-report-abuse/plan.md)
- Read the research decisions: [/Users/ctgunn/Projects/youtube-mcp-server/specs/152-videos-report-abuse/research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/152-videos-report-abuse/research.md)
- Read the wrapper contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/152-videos-report-abuse/contracts/layer1-videos-report-abuse-wrapper-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/152-videos-report-abuse/contracts/layer1-videos-report-abuse-wrapper-contract.md)
- Read the auth and payload contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/152-videos-report-abuse/contracts/layer1-videos-report-abuse-auth-payload-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/152-videos-report-abuse/contracts/layer1-videos-report-abuse-auth-payload-contract.md)

## 2. Implement in Red-Green-Refactor order

1. Add failing unit tests for `videos.reportAbuse` metadata completeness, quota visibility, required body validation, optional payload guidance, 204-success acknowledgement guidance, and OAuth-only enforcement.
2. Add failing transport tests for request construction and normalized result handling for valid, invalid, unauthorized, invalid-reason, rate-limited, video-not-found, upstream-failing, and successful abuse-report profiles.
3. Add failing integration and contract tests showing the representative wrapper path does not yet make `videos.reportAbuse` reusable for higher-layer planning.
4. Implement the smallest updates to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py` needed to satisfy those failures.
5. Ensure review surfaces keep operation identity, quota cost, OAuth-only access, required body fields, optional body fields, unsupported delegated content-owner behavior, and no-content success acknowledgement rules visible without exposing credentials or report submitter identity.
6. Refactor for naming clarity and duplication reduction while preserving deterministic request validation and normalized outcome boundaries.
7. Add or preserve reStructuredText docstrings for every new or changed Python function.
8. Confirm failure-path behavior keeps malformed requests on `invalid_request`, missing OAuth access distinct from malformed input, invalid abuse-reason combinations distinct from missing local inputs, upstream refusals distinct from successful acknowledgements, and temporary upstream outages distinguishable as `upstream_unavailable`.

Representative test modules:

- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_videos_contract.py`

## 3. Keep scope constrained

- Keep YT-152 internal-only.
- Do not add a public `videos_reportAbuse` MCP tool in this slice.
- Do not add abuse-reason discovery behavior; use the existing `videoAbuseReportReasons.list` wrapper as the separate reason-inventory source.
- Do not add partner-only delegated content-owner reporting in this slice.
- Reuse existing Layer 1 executor and metadata abstractions.
- Focus on required body validation, optional body field boundaries, quota visibility, OAuth expectations, no-content success acknowledgement, and normalized report outcomes.

## 4. Verify before review

Run targeted and full validation expected by the constitution:

```bash
cd /Users/ctgunn/Projects/youtube-mcp-server
python3 -m pytest tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_metadata_contract.py tests/contract/test_layer1_consumer_contract.py tests/contract/test_layer1_videos_contract.py
python3 -m pytest
python3 -m ruff check .
```

## 5. Review readiness checklist

- `videos.reportAbuse` wrapper metadata shows endpoint identity and the quota cost of `50`
- Required request payload is clear: `body.videoId` and `body.reasonId`
- Supported optional payload fields are clear: `body.secondaryReasonId`, `body.comments`, and `body.language`
- Partner-only delegated content-owner query behavior is explicitly outside the guaranteed boundary for this slice
- Higher-layer abuse-report summaries show submitted report context, successful acknowledgement, and source contract details without exposing credentials or report submitter identity
- OAuth-only access is visible without reading implementation code
- Unsupported request combinations are explicit in wrapper and contract surfaces
- Missing body, missing video identifier, and missing reason fail clearly
- Authorized upstream invalid-reason, rate-limit, video-not-found, and refusal failures remain distinct from local validation failures and successful acknowledgements
- Temporary upstream report outages remain distinguishable as `upstream_unavailable`
- No public MCP or hosted behavior changes are introduced
- All new or changed Python functions include reStructuredText docstrings
