# Research: YT-304 Transcript Retrieval

## Decision: Extend the Existing Concrete Transcript Family

Implement `transcripts_getTranscript` in `src/mcp_server/tools/youtube_composed/transcripts.py`, export its public builders through `src/mcp_server/tools/youtube_composed/__init__.py`, and register its descriptor in `src/mcp_server/tools/dispatcher.py`.

**Rationale**: The transcript module is already the Layer 3 family seam, and the planned catalog already contains this tool. The concrete videos family establishes the descriptor, injected lower-layer dependency, safe error, and dispatcher-registration pattern.

**Alternatives considered**:

- Create a generic transcript service: rejected because one bounded workflow does not justify another abstraction boundary.
- Implement in Layer 2: rejected because this feature combines two lower-layer operations and returns a normalized research result.
- Keep only the representative catalog entry: rejected because YT-304 requires an executable public tool.

## Decision: Use the Official Authorized Caption Flow Only

Compose one `captions.list` request using `part=snippet` and the requested video, then download one selected caption through `captions.download`. The normal path consumes 50 plus 200 documented caption quota units before retries. Both operations require eligible OAuth authorization; caption download additionally requires permission for the associated video.

**Rationale**: This is the PRD's official transcript source strategy and preserves the existing lower-layer credential, observability, and normalized-error behavior. It makes lack of permission distinguishable from absence of an accessible matching caption.

**Alternatives considered**:

- Call an integration wrapper or HTTP client directly: rejected because it bypasses the lower-layer contracts and shared auth/error behavior.
- Add a public or third-party transcript fallback: rejected because YT-304 explicitly scopes to official captions and a fallback would require separately disclosed source/provenance policy.
- Return a different-language caption when a match is absent: rejected because it violates predictable language selection.

## Decision: Centralize the Configured Default Language

Add a non-secret normalized `YOUTUBE_TRANSCRIPT_LANG` setting to `YouTubeLiveRuntimeSettings` in `src/mcp_server/config.py` and pass it through the existing configured runtime/dispatcher path into the descriptor. The handler accepts injected configuration and must not read the process environment directly.

**Rationale**: Existing configuration loaders are pure and testable from a supplied environment mapping. This makes local, hosted, and test behavior consistent while preserving safe configuration diagnostics.

**Alternatives considered**:

- Read the environment in the handler: rejected because it hides a deployment dependency, weakens test injection, and diverges from central configuration practice.
- Treat an invalid configured value as English: rejected because it silently changes the caller-visible selection policy.

## Decision: Resolve and Match Language Exactly and Deterministically

Resolve one language in order: explicit request, configured default, then `en`. Normalize harmless surrounding whitespace and casing, validate a BCP-47 language tag, and select only captions whose declared language exactly matches the resolved tag case-insensitively. Exclude failed tracks; rank serving before syncing, standard before automatic speech recognition before forced, non-draft before draft, then caption identifier lexically. Do not request translation.

**Rationale**: Exact matching gives agents predictable language behavior. The documented ordering avoids reliance on upstream response order while preferring ready, standard, non-draft captions.

**Alternatives considered**:

- Match a language's base code (such as accepting `en-GB` for `en`): rejected because it can return a materially different language variant without caller consent.
- Use source-list order: rejected because it is not a public deterministic contract.
- Use `tlang` translation: rejected because it obscures whether returned text came from the selected source language and violates no-substitution semantics.

## Decision: Download VTT and Normalize Complete Plain Text

Request the selected caption in VTT form, decode it safely as UTF-8, remove VTT headers, cue identifiers, timing lines, and markup, and concatenate nonblank cue text in cue order with normalized whitespace. A successfully downloaded caption with no textual cues returns `text: ""` with an empty availability state.

**Rationale**: VTT is a documented caption conversion format with explicit cue structure, so it supports deterministic plain-text normalization. Text rather than segments belongs to this feature; timestamped output is specified separately.

**Alternatives considered**:

- Return raw download bytes: rejected because agents need stable safe text rather than a source-format payload.
- Infer the parser from the source content type: rejected because caption downloads are returned as binary content even when converted.
- Fabricate timing or text from metadata: rejected because it would misrepresent source data.

## Decision: Map Caption Outcomes to a Narrow Safe Layer 3 Taxonomy

Map malformed public inputs to `invalid_parameters`; no exact accessible track or stale selected track to `transcript_unavailable`; authentication or authorization failures to `authorization_sensitive_data`; quota failures to `quota_exhaustion`; and temporary, malformed, or other source failures to `upstream_failure`. Only safe resolved-language context may accompany an unavailable result.

**Rationale**: Agents need stable recovery semantics, while raw caption content, tokens, upstream bodies, and traces must never escape on failure.

**Alternatives considered**:

- Forward lower-layer categories and messages: rejected because they expose implementation detail and may leak unsafe diagnostics.
- Classify every failure as unavailable: rejected because callers must distinguish access, quota, and retryable source failures.

## Decision: Validate With Deterministic Doubles Before Credential-Gated Live Verification

Use injected recording caption list/download handlers for unit, contract, and registration integration coverage; use the existing configured runtime only for credential-gated live verification. Finish with `python3 -m pytest` and `ruff check .`.

**Rationale**: Controlled responses are required to prove ordering, exact matching, empty text, and safe errors deterministically. The constitution requires Red-Green-Refactor, integration coverage, reStructuredText docstrings, and a final full-suite run.

**Alternatives considered**:

- Test only a live account: rejected because results and permissions are not deterministic and may mutate no useful fixture state.
- Run focused tests only: rejected because the constitution requires final full-repository evidence.
