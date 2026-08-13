# Data Model: YT-313 Transcript Language Discovery

## Language Discovery Request

Represents one public `transcripts_listLanguages` invocation.

**Fields**:

- `videoId`: required, trimmed, non-empty video identifier.

**Validation Rules**:

- No unknown fields are accepted.
- `videoId` must be text and remain non-empty after trimming.
- Invalid input ends before a caption-listing request is attempted.

## Language Option

Represents one caller-visible caption track returned by authorized language discovery.

**Fields**:

- `language`: source-provided caption language when supplied.
- `availability`: normalized caller-visible state for a returned option.
- `captionTrackId`: source-provided track identifier when supplied; it is absent or null when the source does not provide one.
- `trackMetadata`: an optional collection of approved source-provided distinguishing attributes, such as name, status, track kind, draft state, and automatic-sync state.

**Validation and Presentation Rules**:

- One returned source track creates one Language Option; duplicate languages remain separate options in source order.
- Only supplied, approved source attributes may appear in `trackMetadata`; missing values are not inferred.
- Source language, identifiers, and metadata are marked `raw_upstream`; availability is marked `normalized`.
- Caption text, raw source payloads, authorization context, and unapproved source fields are never part of an option.

## Language Discovery Result

Represents a completed language-discovery response.

**Fields**:

- `videoId`: normalized requested video identifier.
- `languageOptions`: ordered collection of zero or more Language Options.
- `availability`: `available` when at least one option was returned, or `no_accessible_languages` when an authorized listing completed empty.
- `fieldProvenance`: field-category mapping for the result and each option category.

**Relationships**:

- One Language Discovery Request causes exactly one authorized caption-listing operation.
- One completed source listing yields exactly one Language Discovery Result.
- The result contains zero or more Language Options.

**State Transitions**:

```text
valid request -> authorized caption listing -> one or more source tracks -> available
valid request -> authorized completed empty listing -> no_accessible_languages
valid request -> authorization unavailable -> authorization_sensitive_data
valid request -> quota exhausted -> quota_exhaustion
valid request -> caption endpoint unavailable -> source_unavailable
valid request -> other source failure -> upstream_failure
invalid request -> invalid_parameters
```

## Safe Failure Outcome

Represents a non-success outcome without caption options or caption content.

**Fields**:

- `category`: stable safe public failure category.
- `message`: safe recovery-oriented explanation.
- `details`: optional sanitized diagnostic fields.

**Validation Rules**:

- Never includes caption text, source track details that were not authorized for disclosure, credentials, tokens, raw source response bodies, signed URLs, or internal traces.
- `no_accessible_languages` is a successful Language Discovery Result, never a failure category.
