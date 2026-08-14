# Data Model: YT-315 Transcript Search

## Transcript Search Request

| Field | Type | Required | Validation and meaning |
|---|---|---:|---|
| `videoId` | string | Yes | Non-empty after trimming; identifies exactly one video. |
| `query` | string | Yes | Non-empty after trimming; searched literally and case-insensitively. |
| `language` | string | No | Non-empty valid language tag when present; passed to timed retrieval for exact language selection. |
| `maxMatches` | integer | No | Inclusive range 1–50; defaults to 10. |

The request rejects unknown fields and wrong value types before retrieving transcript segments.

## Retrieved Transcript Segment

| Field | Type | Source | Rules |
|---|---|---|---|
| `text` | string | Normalized caption cue | Search only this segment's text; do not join it to adjacent segments. |
| `startTimeSeconds` | number | Normalized caption timing | Non-negative elapsed seconds from video start. |
| `endTimeSeconds` | number | Normalized caption timing | Never earlier than `startTimeSeconds`. |

Segments are supplied by the existing timestamped-caption retrieval capability. This feature neither selects caption tracks nor changes timing boundaries.

## Transcript Match

| Field | Type | Meaning |
|---|---|---|
| `matchedText` | string | The first source-preserving substring in the segment that matches the case-insensitive query. |
| `snippet` | string | Up to 160 characters of context from the same segment, centered on the first match where context exists. Ellipses appear only for omitted segment text. |
| `startTimeSeconds` | number | Start time of the complete matching source segment. |
| `endTimeSeconds` | number | End time of the complete matching source segment. |

A segment produces at most one match. Matches sort by start time ascending, preserving source segment order where start times are equal.

## Transcript Search Result

| Field | Type | Meaning |
|---|---|---|
| `videoId` | string | Normalized requested video identifier. |
| `language` | string | Selected source caption language when a track was searched. |
| `languageSelectionSource` | string | Existing timed-retrieval selection context. |
| `captionTrackId` | string | Source identifier for the selected caption track when provided. |
| `availability` | string | `available` when matches exist; `no_matches` when retrieval completed but no segment matches. |
| `matches` | array of Transcript Match | Chronologically ordered matches after the requested cap. |
| `fieldProvenance` | object | Declares normalized request, selected-source, and local-search fields. |

## State Transitions

```text
valid request
  -> retrieve timestamped segments
  -> no accessible captions / language unavailable / safe source failure
     OR
  -> selected segments
  -> literal segment search
  -> available matches OR no_matches
```

Only `no_matches` is a successful empty-search state. Caption unavailability and source failures are errors, not result states.
