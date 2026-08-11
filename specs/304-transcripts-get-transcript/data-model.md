# Data Model: YT-304 Transcript Retrieval

## Transcript Request

Represents one public `transcripts_getTranscript` invocation.

**Fields**:

- `videoId`: required, trimmed, non-empty video identifier.
- `language`: optional, trimmed language tag selected explicitly by the caller.

**Validation Rules**:

- No unknown fields are accepted.
- `videoId` and a supplied `language` must be text and remain non-empty after trimming.
- A supplied language and configured default must be valid BCP-47 language tags after harmless case normalization.

## Resolved Language

Represents the exactly one language used to select a caption track.

**Fields**:

- `language`: normalized selected language tag.
- `languageSource`: one of `explicit`, `configured_default`, or `english_fallback`.

**State Transitions**:

```text
explicit request -> explicit
no explicit request + valid configured default -> configured_default
no explicit request + no configured default -> english_fallback (en)
invalid supplied or configured language -> safe invalid-parameter/configuration outcome
```

## Caption Track Candidate

Represents one authorized caption-track record discovered for the video.

**Fields**:

- `captionTrackId`: source-provided identifier.
- `videoId`: source-provided associated video identifier.
- `language`: source-provided BCP-47 language tag.
- `status`: source track state such as serving, syncing, or failed.
- `trackKind`: source type such as standard, automatic speech recognition, or forced.
- `isDraft`: source draft indicator when available.

**Validation and Selection Rules**:

- Candidates must exactly match Resolved Language case-insensitively after trimming.
- Failed candidates are excluded.
- The selected candidate is ranked serving, then syncing; standard, then automatic speech recognition, then forced; non-draft before draft; then lexical `captionTrackId`.
- The selection yields zero or one selected Caption Track Candidate.

## Transcript Result

Represents a successful normalized public result.

**Fields**:

- `videoId`: requested video identifier.
- `language`: resolved language.
- `languageSource`: source of language resolution.
- `availability`: `available` or `empty`.
- `text`: complete normalized plain transcript text; empty only when a successful selected download contains no text.
- `captionTrackId`: selected source identifier when available.
- `fieldProvenance`: classification of fields as source-provided or normalized.

**Relationships**:

- One Transcript Request creates one Resolved Language.
- One Resolved Language selects zero or one Caption Track Candidate.
- One selected candidate can produce one Transcript Result.

**State Transitions**:

```text
valid request -> language resolved -> matching candidate selected -> download succeeds -> available | empty
valid request -> no matching candidate / stale candidate -> transcript_unavailable
valid request -> access denied -> authorization_sensitive_data
valid request -> quota exhausted -> quota_exhaustion
valid request -> source/decode failure -> upstream_failure
invalid request/configuration -> invalid_parameters
```

## Safe Failure Outcome

Represents a non-success result without transcript content.

**Fields**:

- `category`: stable public error category.
- `message`: safe recovery-oriented explanation.
- `details`: optional sanitized fields; `language` is permitted only for unavailable outcomes.

**Validation Rules**:

- Never contains caption text, raw downloaded bytes, credentials, authorization values, raw source response bodies, signed URLs, or internal traces.
