# Implementation Plan: Layer 4 Remote MCP Read-Only Live Smoke

**Branch**: `405-remote-live-smoke` | **Date**: 2026-08-26 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/405-remote-live-smoke/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/405-remote-live-smoke/spec.md`

## Summary

Add a manual, credential-gated remote smoke command that uses the public HTTP MCP transport of an already deployed server. The command will initialize the remote session, retain required protocol/session headers, discover the active catalog, and call only the existing reviewed API-key public-read allowlist. A separate standard-library remote client will safely parse JSON and streamed call responses, classify every selected or excluded tool, enforce 12 tool-call and finite timeout bounds, and emit only redacted evidence. The feature adds verification, command, and documentation behavior; it does not add or change a public MCP tool schema, server handler, or normal CI/deployment gate.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Python standard library (`argparse`, `dataclasses`, `json`, `urllib`); existing local live-smoke allowlist; existing hosted MCP transport/protocol conventions; pytest; Make  
**Storage**: N/A — sessions, catalog facts, derived public fixtures, and redacted reports are held only for one process run; no persistence is added  
**Testing**: pytest unit/contract/integration coverage using an injected responder and standard-library loopback HTTP server; `PYTHONPATH=src python3 -m pytest tests/integration/test_remote_mcp_live_smoke.py`; `make test-tools`; `make test-runtime`; `make test`; final completion gate `make quality`  
**Documentation Style**: Markdown feature contracts and README operator guidance; complete reStructuredText docstrings for every new or changed Python function, including CLI, HTTP, parsing, and test-responder helpers  
**Target Platform**: Local operator shell and CI-compatible Python environments; manually initiated connections to approved staging or production remote MCP endpoints  
**Project Type**: Python remote MCP web service with an internal Layer 4 operator-verification CLI  
**Performance Goals**: At most 12 reviewed tool calls plus initialize and discovery per run; no more than 14 remote POSTs; finite 30-second HTTP timeout per request; exactly one terminal report entry for every selected discovered tool  
**Constraints**: Require `RUN_REMOTE_MCP_LIVE_SMOKE=1` and a remote endpoint before any request; include bearer authentication only when supplied/required by the endpoint; make `initialize`, `tools/list`, and `tools/call` only through the remote public transport; retain `MCP-Session-Id` and negotiated protocol version; parse streamed call replies; reuse a reviewed explicit allowlist and public fixtures without inferring eligibility; never print or persist tokens, authorization headers, session IDs, request arguments, full URLs/query strings, raw response bodies, or exception text; exclude the command from `make test`, `make quality`, CI, and automated deployments  
**Scale/Scope**: One operator-run against one remote endpoint; the 12 existing reviewed API-key public-read operations; per-tool success, safe availability, actionable failure, exclusion, and bound-reached evidence; no generic/retrieval/baseline tools, no OAuth/owner-only actions, no mutations, no new persistent data, and no public MCP contract changes

## Constitution Check

*GATE: Passed before Phase 0 research; re-checked and passed after Phase 1 design.*

- [x] Contracts defined or updated for all external/MCP-facing behavior changes — [remote MCP live-smoke contract](/Users/ctgunn/Projects/youtube-mcp-server/specs/405-remote-live-smoke/contracts/remote-mcp-live-smoke-contract.md) records the existing public transport sequence, session/auth handling, compatibility boundary, and safe report without changing client-facing MCP schemas.
- [x] Plan includes explicit Red-Green-Refactor steps for each phase and user story.
- [x] Red phase identifies failing tests before implementation tasks begin.
- [x] Green phase limits implementation to the separately injectable remote client, existing reviewed allowlist reuse, manual command, focused tests, and required documentation.
- [x] Refactor phase includes cleanup tasks with a full repository test-suite re-run.
- [x] Integration and regression coverage strategy is documented — deterministic loopback HTTP tests prove the public remote sequence, session continuity, streamed response handling, redaction, and gate exclusion; existing catalog and configured-runtime suites remain required regression evidence.
- [x] Plan names the command that proves the full repository test suite passes before completion: `make quality` (with `make test` also retained as required specification evidence).
- [x] Plan defines how reStructuredText docstrings will be added or preserved for new and changed Python functions — all changed script and test functions must document purpose, inputs, outputs, raised errors, side effects, and redaction obligations where relevant.
- [x] Observability, security, and simplicity constraints are addressed — fixed safe categories and compact per-tool reports provide actionable evidence; credentials and raw transport data never cross the CLI/report boundary; one small remote client plus the existing explicit allowlist is simpler and safer than a second catalog, application instance, or a generic external client.

## Project Structure

### Documentation (this feature)

```text
specs/405-remote-live-smoke/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── remote-mcp-live-smoke-contract.md
└── tasks.md                    # Created later by /speckit.tasks
```

### Source Code (repository root)

```text
Makefile                                              # Add a manual remote-smoke target outside quality gates
README.md                                             # Document the four verification boundaries and remote safety rules
scripts/
├── verify_youtube_live.py                            # Reuse reviewed live allowlist/fixture and safe-result concepts
└── verify_remote_mcp_live_smoke.py                   # New remote public-transport client and credential-safe CLI
tests/
└── integration/
    ├── test_remote_mcp_live_smoke.py                 # New loopback remote-transport, session, SSE, and redaction coverage
    ├── test_youtube_live_smoke.py                    # Preserve/reuse allowlist and local-smoke regression rules as needed
    └── test_ci_quality_gate_docs.py                  # Assert documentation and gate exclusion remain true
```

**Structure Decision**: Keep the remote client in a dedicated script. The existing local smoke instantiates an in-process application, which is expressly prohibited for this remote-server feature. Reuse only the reviewed allowlist, public fixtures, bounded selection rules, and credential-safe outcome vocabulary from the local smoke. Keep controlled responder state test-private; do not add an application package, server route, data store, or client-visible tool.

## Implementation Phases and TDD Plan

### Phase 0 — Research and design decisions (complete)

- **Red**: Identify unresolved choices for remote authentication, initialization/session continuation, protocol-version handling, streamed response parsing, HTTP timeout/count bounds, allowlist reuse, fixture dependency handling, endpoint-identity agreement, safe error classification, evidence redaction, command placement, and normal-gate exclusion.
- **Green**: Record the resolved decisions in [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/405-remote-live-smoke/research.md): use an injectable standard-library HTTP client; initialize then preserve `MCP-Session-Id` and negotiated version; use the current 12-entry reviewed API-key public-read allowlist; accept direct JSON discovery and JSON-RPC events in streamed call responses; cap the run at 12 calls and 30 seconds per HTTP request; and emit fixed safe reports only.
- **Refactor**: Reuse the hosted verifier's HTTP/session conventions and the local smoke's explicit allowlist/result classification without copying its in-process transport. Avoid a second public catalog, generic schema-derived input generator, raw response capture, or a long-lived remote-client library.

### Phase 1 — Contracts and verification design (complete)

- **Red**: Define rules that fail for missing opt-in/endpoint/auth prerequisites, unauthorized remote requests, malformed initialize/list/session responses, session loss, direct dispatcher or in-process substitution, non-allowlisted selection, unsafe fixture inputs, forbidden operation invocation, malformed streamed responses, endpoint-metadata mismatch, unbounded work, raw diagnostics, or accidental normal-gate inclusion.
- **Green**: Document run, allowlist entry, discovered tool, remote session, and per-tool outcome lifecycle in [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/405-remote-live-smoke/data-model.md). Document the existing MCP HTTP interaction and safe evidence boundary in [remote-mcp-live-smoke-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/405-remote-live-smoke/contracts/remote-mcp-live-smoke-contract.md). Record authorized operator commands, expected evidence, and failure handling in [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/405-remote-live-smoke/quickstart.md).
- **Refactor**: Keep the allowlist reviewable and explicit, use discovery only as the authority for whether an entry is currently active, and isolate the one approved derived comment fixture in memory. Keep the remote contract compatible with the existing hosted server rather than introducing new endpoint headers or MCP methods.

### Phase 2 — Implementation planning (next command: `/speckit.tasks`)

#### Shared remote verification foundation

- **Red**: Add failing tests for preflight before network use; initialize construction with required client information; bearer-auth handling; session and protocol-version retention; discovery through the remote URL; direct JSON and streamed response decoding; fixed request/time bounds; and no copying of credentials, headers, session IDs, arguments, or raw transport data into a report, CLI line, or failing assertion. Add complete reStructuredText docstrings to every new or changed Python function before considering the foundation green.
- **Green**: Implement `scripts/verify_remote_mcp_live_smoke.py` with a small injectable HTTP requester. Send JSON-RPC `initialize`, then `tools/list`, then selected `tools/call` requests to the remote MCP URL; forward only the required safe request headers and the established session/version values. Normalize HTTP, JSON, and streamed protocol responses to fixed safe categories without returning raw bodies or headers.
- **Refactor**: Centralize request construction, session/version state, safe HTTP failure mapping, streamed-event selection, and report serialization. Preserve machine-readable safe output and the canonical local allowlist source; re-check docstrings and run the focused suite before story work.

#### User Story 1 — Run a Remote Read-Only Smoke

- **Red**: Add a controlled loopback responder test that fails unless the observable sequence is `initialize` → session-bearing `tools/list` → one `tools/call` for each discovered reviewed entry. Require the responder to see bearer auth where supplied, require public object arguments, require the session on continuations, and test direct JSON discovery plus streamed call results without using an in-process application or dispatcher.
- **Green**: Select discovered members of the explicit current allowlist, including the one bounded in-memory public comment-parent dependency. Issue at most 12 tool calls, classify each selected response as successful structured content, documented safe availability error, actionable failure, or bound reached, and compare successful endpoint identity to both the reviewed expected endpoint and discovered `metadata.upstream.operationKey` when published.
- **Refactor**: Consolidate sequence, selection, and outcome assertions while keeping case identities readable and deterministic. Keep discovery membership authoritative and do not introduce a hard-coded duplicate of the remote catalog.

#### User Story 2 — Prevent Unsafe Live Calls

- **Red**: Add failing tests for an omitted enablement flag, endpoint, or required token; rejected initialization; absent/invalid session; empty catalog; allowlist entries absent from discovery; discovered mutations/sensitive tools; unsafe/missing reviewed fixtures; timeouts; HTTP failures; unexpected streamed data; endpoint mismatch; and deliberate credential/header/input/body values that must not occur in evidence.
- **Green**: Fail closed before network I/O when prerequisites are absent. Report every non-allowlisted discovered tool as excluded without invocation; never infer safe eligibility from names/metadata. Use 30-second HTTP requests and a fixed maximum of 14 protocol posts (initialize, discovery, and at most 12 calls), then classify remaining work as bound reached rather than retrying. Convert transport failures to actionable safe categories and never expose exception text or transport payloads.
- **Refactor**: Share validation and redaction paths between preflight, response parsing, report generation, and CLI output. Retain an explicit deny/allowlist review boundary and verify that test responder captures stay internal to tests; update all reStructuredText docstrings after cleanup.

#### User Story 3 — Interpret and Reproduce Verification Evidence

- **Red**: Add documentation and Makefile regression tests that fail unless the remote command is manual, opt-in, remote-only, credential-safe, bounded, excluded from `make test`, `make quality`, CI, and automated deployment, and clearly distinguished from catalog, configured-runtime, and local live smoke verification.
- **Green**: Add `make test-remote-live-smoke`, loading ignored local environment files consistently with the local smoke but requiring `RUN_REMOTE_MCP_LIVE_SMOKE=1` and `REMOTE_MCP_URL`; include `MCP_AUTH_TOKEN` only for endpoints requiring bearer authentication. Extend README guidance with prerequisites, approved endpoint boundary, quota/upstream caveats, four-workflow comparison, safe evidence, and recovery actions.
- **Refactor**: Keep the manual target a thin wrapper over the remote CLI and remove duplicated command/security wording. Verify no quality/CI/deploy target transitively invokes it, then re-run focused documentation and remote tests.

### Cross-cutting verification and rollback

- Focused deterministic evidence: `PYTHONPATH=src python3 -m pytest tests/integration/test_remote_mcp_live_smoke.py`, `make test-tools`, and `make test-runtime` pass without real credentials or external service calls. The remote-focused suite uses only a controlled loopback responder; its captured headers and bodies are test-private.
- Authorized manual evidence: `RUN_REMOTE_MCP_LIVE_SMOKE=1 REMOTE_MCP_URL='approved-endpoint' MCP_AUTH_TOKEN='operator-supplied-value' make test-remote-live-smoke` runs only after deployment approval and only when its target requires bearer authentication. Its output is limited to redacted per-tool summaries, counts, and safe categories; it is not normal completion evidence.
- Completion evidence: run `make test` to satisfy the specification's full-suite requirement, then `make quality` after the final code or documentation change. `make quality` is the constitutional completion gate because it runs linting, type checking, and the full test suite; fix every failure before completion.
- Contract evidence: loopback transport tests verify the existing public initialization, discovery, session, and invocation envelope/stream behavior and prove selected outcome and redaction rules. Existing client-facing names, schemas, result envelopes, endpoints, authentication semantics, and server behavior remain unchanged; no migration is required.
- Mitigation/rollback: revert the feature commit or remove the manual remote-smoke target if it unexpectedly blocks operator workflows. Do not weaken preflight checks, explicit allowlisting, session validation, bounds, or safe reporting. Correct discovery drift, fixture review, endpoint configuration, or remote availability outside committed evidence before re-authorizing a run.

## Complexity Tracking

No constitution violations or exceptions are required. A small standard-library remote client plus the existing reviewed allowlist is simpler than an additional service, persistent report store, generic MCP client dependency, or duplicate catalog. The public server continues to own protocol and tool behavior.
