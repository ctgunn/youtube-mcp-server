# Research: YT-102 Layer 1 Endpoint Metadata, Quota, and Signature Standards

## Decision: Extend the existing `EndpointMetadata` contract instead of introducing a parallel metadata abstraction

**Rationale**: YT-101 already established a metadata-first wrapper contract under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`. YT-102 is a standards-tightening slice, so the simplest and safest approach is to strengthen validation and reviewability rules on that existing model.

**Alternatives considered**:

- Create a second metadata object dedicated only to review artifacts. Rejected because it would duplicate identity, quota, and auth fields and create drift risk.
- Defer stricter metadata semantics to later endpoint-specific slices. Rejected because later YT-1xx work depends on consistent standards before endpoint volume expands.

## Decision: Represent lifecycle and documentation caveats as explicit maintainer-facing metadata through `caveat_note`, not as incidental free-form notes

**Rationale**: The YT-102 spec requires maintainers to distinguish deprecation, limited availability, and official-document inconsistencies during review. A structured caveat expectation is more reliable than optional free-form notes and makes later contract tests meaningful.

**Alternatives considered**:

- Keep a single optional `notes` field with no stronger semantics. Rejected because reviewers cannot reliably distinguish caveat types or know when notes are mandatory.
- Track caveats only in feature documentation. Rejected because wrapper-level reviewability would still be incomplete in code-facing artifacts.

## Decision: Require a maintainer-visible explanation through `auth_condition_note` whenever wrapper metadata is mixed or conditional

**Rationale**: YT-101 already requires a runtime `conditional_reason` in `AuthContext`, but YT-102 is about wrapper reviewability before execution. Mixed or conditional wrapper metadata therefore needs its own declarative `auth_condition_note` describing when auth expectations change.

**Alternatives considered**:

- Reuse only the runtime `conditional_reason` field. Rejected because it explains one execution, not the wrapper contract itself.
- Allow conditional auth with no explanation as long as tests pass. Rejected because higher-layer planning would still depend on tribal knowledge.

## Decision: Validate reviewability through artifact-aware tests, not only dataclass instantiation tests

**Rationale**: The main YT-102 risk is not request execution; it is maintainers being unable to see quota, auth, and caveat implications quickly. Contract and artifact-based checks are needed alongside unit tests so the implementation proves the review outcome the spec describes.

**Alternatives considered**:

- Restrict validation to metadata object construction. Rejected because the spec requires visible review artifacts, not just in-memory field presence.
- Rely on manual code review with no regression coverage. Rejected because later endpoint slices could silently erode metadata visibility.

## Decision: Keep YT-102 internal-only and avoid public MCP contract changes

**Rationale**: The feature affects internal Layer 1 wrapper standards used by maintainers and future higher-layer authors. No public MCP method, schema, or hosted endpoint behavior needs to change to satisfy the spec.

**Alternatives considered**:

- Surface metadata standards through public MCP tool behavior immediately. Rejected because YT-102 is a foundation slice and public exposure belongs to later Layer 2 or Layer 3 work if needed.
- Broaden the feature into endpoint inventory expansion. Rejected because that would mix standards work with multiple endpoint slices.

## Decision: Preserve the current repository testing layers and add YT-102 checks where reviewability risk lives

**Rationale**: The repository already separates `tests/unit`, `tests/contract`, and `tests/integration`, and the constitution requires explicit Red-Green-Refactor coverage plus full-suite validation. YT-102 should add metadata completeness checks in unit tests, reviewability and contract-artifact checks in contract tests, and representative comparison flows in integration tests.

**Alternatives considered**:

- Unit tests only. Rejected because reviewability and consumer-planning outcomes are cross-artifact concerns.
- Hosted end-to-end tests. Rejected because YT-102 does not change hosted MCP behavior directly.

## Decision: Use contract markdown plus reStructuredText docstrings as the primary maintainer-facing surfaces

**Rationale**: The spec explicitly allows visibility through signatures, docstrings, or adjacent implementation comments, and the constitution already requires reStructuredText docstrings for changed Python functions. Pairing docstrings with feature-local contract markdown gives maintainers both code-adjacent and design-level guidance.

**Alternatives considered**:

- Keep all standards only in code comments. Rejected because design review and future planning need a stable artifact outside the implementation.
- Keep all standards only in markdown. Rejected because quota and auth visibility must remain close to the wrapper definition itself.
