# Implementation Plan: JSON-RPC / MCP Error Code Alignment

**Branch**: `018-mcp-error-alignment` | **Date**: 2026-03-21 | **Spec**: [~/Projects/youtube-mcp-server/specs/018-mcp-error-alignment/spec.md](~/Projects/youtube-mcp-server/specs/018-mcp-error-alignment/spec.md)
**Input**: Feature specification from `/specs/018-mcp-error-alignment/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Replace the current string-based server error taxonomy with a documented JSON-RPC / MCP-aligned error-code contract across local and hosted MCP flows. The plan keeps the current Python MCP service, FastAPI-hosted runtime, and safe error payload shape intact while introducing one shared mapping layer, updating external contracts, and proving parity for malformed request, unsupported method, invalid argument, authentication or authorization denial, resource lookup failure, and unexpected tool execution scenarios.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: FastAPI, Uvicorn, Pydantic v2, Redis client, Python standard library JSON/HTTP/config/logging modules  
**Storage**: In-memory runtime state only for request handling, tool dispatch, observability state, and hosted session metadata backed by the existing shared session store where already configured  
**Testing**: `pytest` across existing unit, contract, and integration suites plus hosted verification and documentation checks  
**Target Platform**: Local development and Google Cloud Run hosted Linux runtime serving MCP clients  
**Project Type**: Hosted MCP web service  
**Performance Goals**: Preserve the existing foundation latency expectations and hosted response behavior while limiting this slice to error classification, contract updates, and verification coverage  
**Constraints**: Preserve MCP-native success payloads from FND-010, preserve hosted security enforcement and status-code semantics from FND-013, keep client-visible error payloads sanitized, and avoid changing the supported tool set, route footprint, or authentication model  
**Scale/Scope**: One hosted MCP service; shared error handling across local routing, hosted `/mcp` handling, security denials, session failures, and tool dispatch; regression coverage spanning unit, contract, integration, and hosted verification seams

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Contracts defined or updated for all external/MCP-facing behavior changes
- [x] Plan includes explicit Red-Green-Refactor steps for each phase and user story
- [x] Red phase identifies failing tests before implementation tasks begin
- [x] Green phase limits implementation to minimum code required for passing tests
- [x] Refactor phase includes cleanup tasks with full regression test re-run
- [x] Integration and regression coverage strategy is documented
- [x] Observability, security, and simplicity constraints are addressed

## Project Structure

### Documentation (this feature)

```text
specs/018-mcp-error-alignment/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── mcp-error-code-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── mcp_server/
    ├── app.py
    ├── cloud_run_entrypoint.py
    ├── deploy.py
    ├── observability.py
    ├── security.py
    ├── protocol/
    │   ├── envelope.py
    │   └── methods.py
    ├── tools/
    │   ├── dispatcher.py
    │   └── retrieval.py
    └── transport/
        ├── http.py
        ├── session_store.py
        └── streaming.py

tests/
├── contract/
│   ├── test_deep_research_tools_contract.py
│   ├── test_hosted_mcp_security_contract.py
│   ├── test_mcp_transport_contract.py
│   └── test_operational_observability_contract.py
├── integration/
│   ├── test_cloud_run_docs_examples.py
│   ├── test_hosted_http_routes.py
│   ├── test_hosted_mcp_security_flows.py
│   ├── test_mcp_request_flow.py
│   └── test_streamable_http_transport.py
└── unit/
    ├── test_envelope_contract.py
    ├── test_hosted_security_policy.py
    ├── test_invoke_error_mapping.py
    ├── test_method_routing.py
    └── test_retrieval_tools.py

scripts/
└── verify_cloud_run_foundation.py
```

**Structure Decision**: Extend the existing single-package Python service under `src/mcp_server` by centralizing error-code mapping in the current protocol and hosted-entry seams, then update the current unit, contract, integration, deployment-verification, and documentation artifacts that already assert client-visible error behavior. Preserve the existing `tests/unit`, `tests/contract`, and `tests/integration` layout so Red-Green-Refactor coverage remains explicit at the mapper, MCP contract, and hosted parity boundaries.

## Phase 0: Research and Decision Closure

### Research Focus

- Decide the target JSON-RPC / MCP-aligned code strategy for core protocol failures versus project-specific extension cases.
- Decide how hosted security denials, session failures, and resource lookup failures map into numeric protocol-safe codes without losing actionable `category` information.
- Decide the precedence order when one request could be described as malformed, unauthorized, unsupported, or invalid in more than one way.
- Decide the minimum contract and verification surface needed to align local and hosted behavior without redesigning unrelated transport or browser-access features.

### Planned Red-Green-Refactor Flow

- **Red**: Compare the current local router, hosted entrypoint, security decision flow, contracts, and tests against the FND-018 spec to identify where string codes, inconsistent category handling, and local-hosted drift still exist.
- **Green**: Resolve the error-code taxonomy, precedence rules, covered categories, and verification scope in `research.md`, leaving no unresolved clarification points in the technical approach.
- **Refactor**: Collapse overlapping failure classes into one shared mapping strategy that preserves existing safe payload structure and HTTP status semantics while eliminating string-typed client-visible codes for covered paths.

### Research Outputs

- `research.md` with final decisions for numeric code strategy, category precedence, hosted/local parity scope, and contract-update scope.

## Phase 1: Design and Contracts

### Design Focus

- Model the shared error-code contract, mapped failure categories, payload invariants, and parity verification requirements needed by FND-018.
- Define the external MCP contract for local and hosted failure responses, including numeric codes, stable `error.data.category` values, and preserved HTTP status behavior where applicable.
- Provide a quickstart that demonstrates Red-Green-Refactor checks, local verification, and hosted verification for the representative malformed request, unsupported method, invalid argument, auth-denial, resource-missing, and tool-failure scenarios.

### Planned Red-Green-Refactor Flow

- **Red**: Capture the failing design expectations for code-type alignment, category precedence, parity across local and hosted flows, and contract coverage before implementation tasks begin.
- **Green**: Produce `data-model.md`, `contracts/mcp-error-code-contract.md`, and `quickstart.md` with the minimum design detail needed to implement those failing checks.
- **Refactor**: Remove duplicated wording across the plan, contract, and quickstart; confirm that observability and hosted security semantics remain intact; and re-check that the design is the smallest change that satisfies the spec.

### Design Outputs

- `data-model.md`
- `contracts/mcp-error-code-contract.md`
- `quickstart.md`

## Phase 2: Implementation Strategy

### User Story 1 - Receive Protocol-Aligned Error Codes

- **Red**: Add failing unit and contract tests proving covered malformed request, unsupported method, invalid argument, unknown-tool, and unexpected tool-failure cases no longer return string-style server codes in local MCP responses.
- **Green**: Implement the minimum shared mapping changes needed for the local protocol router and tool paths to emit the documented numeric code set while preserving sanitized messages and stable category details.
- **Refactor**: Consolidate local error construction so protocol validation, dispatcher failures, and tool failures all derive from one mapping path, then rerun the targeted plus regression suites.

### User Story 2 - Trust Error Consistency Across Hosted and Local Flows

- **Red**: Add failing integration and contract tests proving equivalent malformed request, invalid argument, authentication or authorization denial, and resource-missing scenarios return matching client-visible error codes across local and hosted flows.
- **Green**: Implement the minimum hosted-entry and security-mapping updates needed so hosted `/mcp` responses reuse the same documented code contract while preserving existing HTTP statuses and access-control behavior.
- **Refactor**: Remove duplicated hosted-versus-local error classification logic, tighten shared helpers, and rerun the contract, integration, and hosted verification suites.

### User Story 3 - Diagnose Failures Through One Documented Mapping

- **Red**: Add failing documentation and verification checks proving the published contract does not yet describe every covered category, precedence rule, or representative failure example required by FND-018.
- **Green**: Implement the minimum contract, deploy-verification, and quickstart updates needed to publish one mapping for transport, protocol, validation, authentication or authorization, resource lookup, and tool execution failures.
- **Refactor**: Consolidate examples and verification helpers, remove stale string-code references from plan-adjacent artifacts, and rerun the full unit, contract, and integration suites.

### Regression Strategy

- Preserve current `initialize`, `tools/list`, `tools/call`, `/health`, `/ready`, hosted auth enforcement, browser-access behavior, and durable-session behavior outside the intentional change from string codes to documented numeric codes.
- Re-run the full unit, contract, and integration suites after targeted error-alignment tests pass to prove no regressions in protocol alignment, hosted security, retrieval behavior, session continuity, or observability.
- Verify that operators can still diagnose failures through sanitized `message` and stable `error.data.category` fields even after the code field changes format.

### Rollback and Mitigation

- Keep the feature scoped to error-code mapping, shared helpers, contracts, tests, and verification artifacts so operators can roll back by redeploying the prior revision if downstream clients are not ready for the aligned code contract.
- Preserve HTTP status behavior, safe messages, and high-level failure categories so rollout issues can be triaged quickly without conflating code alignment regressions with broader transport, auth, or tool-execution faults.

## Post-Design Constitution Check

- [x] Contracts defined or updated for all external/MCP-facing behavior changes
- [x] Plan includes explicit Red-Green-Refactor steps for each phase and user story
- [x] Red phase identifies failing tests before implementation tasks begin
- [x] Green phase limits implementation to minimum code required for passing tests
- [x] Refactor phase includes cleanup tasks with full regression test re-run
- [x] Integration and regression coverage strategy is documented
- [x] Observability, security, and simplicity constraints are addressed

## Complexity Tracking

No constitution violations or justified exceptions are required for this plan.
