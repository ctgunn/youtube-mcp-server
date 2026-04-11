# Research: YT-110 Layer 1 Endpoint `channels.list`

## Decision: Model `channels.list` auth as mixed/conditional based on selector mode

**Rationale**: Local product artifacts already describe `channels.list` as selector-dependent for authorization behavior (`api_key` or mixed). Keeping a mixed/conditional contract matches Layer 1 metadata standards and prevents misleading callers into assuming one global auth mode. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/102-layer1-metadata-standards/contracts/layer1-metadata-standard.md`

**Alternatives considered**:

- `api_key` only for all selectors. Rejected because owner-scoped selectors (for example `mine`) require authorized-user context.
- `oauth_required` only for all selectors. Rejected because public selector paths should remain usable without over-constraining callers.
- Hide selector-auth differences in runtime behavior only. Rejected because maintainers need contract-visible auth rules before implementation inspection.

## Decision: Use mutually exclusive selector validation for `id`, `mine`, `forHandle`, and username-style lookup when supported

**Rationale**: Existing Layer 1 patterns prefer deterministic request-shape validation and reject ambiguous selector combinations. `channels.list` contract clarity improves when exactly one selector mode is active per request. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/103-activities-list/contracts/layer1-activities-auth-filter-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/110-channels-list-wrapper/spec.md`

**Alternatives considered**:

- Allow multiple selectors and let upstream decide precedence. Rejected because caller behavior becomes non-deterministic.
- Accept mixed selectors and silently rewrite to one selector. Rejected because hidden coercion causes debugging and reproducibility issues.
- Restrict to only one or two selectors in this slice. Rejected because YT-110 explicitly includes broader selector coverage expectations.

## Decision: Treat selector-auth mapping as explicit contract behavior

**Rationale**: The wrapper should make selector behavior reviewable and consistent with existing mixed-auth patterns. This slice uses public selector paths for `id`, `forHandle`, and username-style lookup (when supported), and owner-scoped path behavior for `mine`. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/103-activities-list/contracts/layer1-activities-auth-filter-contract.md`

**Alternatives considered**:

- Permit any auth mode for any selector. Rejected because it weakens deterministic contract boundaries.
- Model `mine` as public selector. Rejected because it conflicts with owner-scoped behavior.
- Omit username-style lookup due to ambiguity. Rejected because the seed and feature spec call for username-style handling when supported.

## Decision: Resolve username-style lookup requirement as a documented conditional selector (`forUsername`) with caveat language

**Rationale**: The feature seed requires username-style lookup to be documented if supported, while current tool inventory emphasizes `forHandle`. Documenting username-style lookup as conditional availability resolves ambiguity without forcing unsupported runtime behavior. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/110-channels-list-wrapper/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`

**Alternatives considered**:

- Remove username-style lookup from contracts entirely. Rejected because it leaves a named requirement unresolved.
- Require username-style lookup unconditionally. Rejected because endpoint support may vary and this plan must stay accurate.
- Replace username-style lookup with `managedByMe`. Rejected because it changes feature intent rather than clarifying it.

## Decision: Keep the implementation seam centered on existing integration wrapper and transport modules

**Rationale**: Recent endpoint slices (YT-107/108/109) show a stable extension path through wrapper metadata, shared executor flow, transport request construction, and layered tests. Reusing that seam is the smallest and safest approach. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

**Alternatives considered**:

- Add a new integration submodule for channels immediately. Rejected because one endpoint slice does not justify new architecture.
- Implement runtime behavior first and document later. Rejected because constitution requires contract-first planning.
- Limit validation to unit tests only. Rejected because constitution requires integration and regression coverage.

## Decision: Preserve explicit normalized boundaries between `invalid_request`, `auth`, and no-match successful retrieval

**Rationale**: YT-110 requires downstream callers to distinguish invalid invocation patterns from auth issues and empty-but-valid results. Maintaining these boundaries keeps higher-layer behavior predictable and testable. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/110-channels-list-wrapper/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`

**Alternatives considered**:

- Flatten all failures to one invalid category. Rejected because downstream recovery behavior would degrade.
- Treat no-match retrieval as an error. Rejected because empty result sets are valid for list-style retrieval.
- Merge auth and selector mismatch outcomes. Rejected because caller remediation differs significantly.

## Clarification Closure

All planning-time clarifications for YT-110 are resolved in this research artifact. No `NEEDS CLARIFICATION` markers remain.
