# Contract: `videoAbuseReportReasons_list`

## Public Tool Identity

- **Tool name**: `videoAbuseReportReasons_list`
- **Layer**: Layer 2 public MCP endpoint tool
- **Mapped upstream operation**: `videoAbuseReportReasons.list`
- **Resource family**: `video_abuse_report_reasons`
- **Official quota cost**: `1` unit per invocation
- **Auth mode**: `api_key`
- **Availability**: Active unless official endpoint caveats recorded during implementation say otherwise
- **Response boundary**: Near-raw endpoint-backed abuse-report-reason list result

## Purpose

Retrieve the catalog of valid YouTube video abuse report reasons for one requested display-language view using the low-level `videoAbuseReportReasons.list` endpoint behavior. This tool is for direct endpoint access, debugging, power-user workflows, and later composition by separate video-reporting layers.

## Out Of Scope

`videoAbuseReportReasons_list` does not submit video abuse reports, check report status, moderate content, decide whether content violates policy, rank reasons, summarize policy guidance, enrich returned reasons, retrieve video details, infer language preferences, perform bulk lookups, or compose multiple endpoint calls.

## Input Schema

```json
{
  "type": "object",
  "required": ["part", "hl"],
  "properties": {
    "part": {
      "type": "string",
      "minLength": 1,
      "description": "Part selection for the abuse-report-reason resources to return."
    },
    "hl": {
      "type": "string",
      "minLength": 1,
      "description": "Display-language value for localized abuse-report-reason labels and descriptions."
    }
  },
  "additionalProperties": false
}
```

## Input Rules

- `part` is required and must be non-empty text after trimming.
- `hl` is required and must be non-empty text after trimming.
- API-key access is expected before execution.
- Additional fields are rejected before endpoint execution unless explicitly documented as supported.
- Video identifiers, reason identifiers, report text, report-submission payloads, moderation instructions, policy evaluation instructions, selectors, paging controls, ranking flags, summarization flags, and enrichment flags are invalid.
- The request performs one localized reason-catalog lookup and does not imply a report has been submitted.

## Success Result Shape

```json
{
  "endpoint": "videoAbuseReportReasons.list",
  "quotaCost": 1,
  "requestedParts": ["snippet"],
  "localization": {
    "hl": "en"
  },
  "auth": {
    "mode": "api_key"
  },
  "items": [
    {
      "kind": "youtube#videoAbuseReportReason",
      "id": "reason-123",
      "snippet": {
        "label": "Spam or misleading"
      }
    }
  ]
}
```

## Success Result Rules

- `endpoint` is always `videoAbuseReportReasons.list`.
- `quotaCost` is always `1`.
- `requestedParts` preserves the caller's selected parts.
- `localization.hl` preserves the caller's requested display-language value.
- `auth.mode` discloses API-key access expectations and never includes credentials.
- `items` contains returned reason resources and may be empty for valid successful lookups.
- Safe upstream fields such as `kind`, `etag`, or response metadata may be preserved when returned.
- The result must not fabricate labels, descriptions, policy interpretations, moderation outcomes, report status, recommendations, rankings, summaries, or enrichment.

## Empty Result Rules

- A valid request that returns zero reason items remains a successful list result.
- Empty success must preserve endpoint identity, quota cost, requested parts, localization context, and access context.
- Empty success must remain distinguishable from invalid input, access failure, quota failure, endpoint unavailability, and unexpected upstream failure.

## Failure Categories

| Category | Trigger | Required Detail |
|----------|---------|-----------------|
| `invalid_request` | Missing, empty, malformed, unsupported, or extra input fields | Include `field` when one field caused the failure |
| `authentication_failed` | API-key access is missing, invalid, or unavailable | Include `authMode: api_key` |
| `authorization_failed` | Caller or project cannot access the lookup capability | Include safe reason when available |
| `quota_exhausted` | Quota prevents reason lookup | Include safe quota context when available |
| `endpoint_unavailable` | Upstream reason-list endpoint is unavailable | Include safe availability context when available |
| `deprecated_endpoint` | Upstream reason-list endpoint is deprecated or disabled | Include safe caveat when available |
| `upstream_failure` | Unexpected upstream failure | Include only sanitized diagnostic details |

## Required Caller Examples

### Localized Reason Lookup

```json
{
  "name": "localized_reason_lookup",
  "description": "Quota cost: 1. Retrieve video abuse report reasons for one display-language view.",
  "arguments": {
    "part": "snippet",
    "hl": "en"
  },
  "result": {
    "endpoint": "videoAbuseReportReasons.list",
    "quotaCost": 1,
    "requestedParts": ["snippet"],
    "localization": {
      "hl": "en"
    },
    "itemsPath": "items"
  },
  "quotaCost": 1
}
```

### Empty Successful Result

```json
{
  "name": "empty_success",
  "description": "Quota cost: 1. Preserve an empty reason collection as a successful localized lookup.",
  "arguments": {
    "part": "snippet",
    "hl": "zz"
  },
  "result": {
    "endpoint": "videoAbuseReportReasons.list",
    "quotaCost": 1,
    "localization": {
      "hl": "zz"
    },
    "items": []
  }
}
```

### Missing Part

```json
{
  "name": "missing_part",
  "description": "Reject reason-list requests missing required part selection.",
  "arguments": {
    "hl": "en"
  },
  "error": {
    "category": "invalid_request",
    "field": "part"
  }
}
```

### Missing Display Language

```json
{
  "name": "missing_hl",
  "description": "Reject reason-list requests missing required display-language input.",
  "arguments": {
    "part": "snippet"
  },
  "error": {
    "category": "invalid_request",
    "field": "hl"
  }
}
```

### Invalid Localization

```json
{
  "name": "invalid_hl",
  "description": "Reject malformed or unsupported localization input before execution.",
  "arguments": {
    "part": "snippet",
    "hl": ""
  },
  "error": {
    "category": "invalid_request",
    "field": "hl"
  }
}
```

### Access Failure

```json
{
  "name": "access_failure",
  "description": "Map missing or invalid API-key access to a safe access failure.",
  "arguments": {
    "part": "snippet",
    "hl": "en"
  },
  "error": {
    "category": "authentication_failed",
    "authMode": "api_key"
  }
}
```

### Quota Or Upstream Failure

```json
{
  "name": "quota_or_upstream_failure",
  "description": "Map quota and upstream reason-list failures to safe categories.",
  "arguments": {
    "part": "snippet",
    "hl": "en"
  },
  "error": {
    "category": "quota_exhausted"
  }
}
```

### Out-Of-Scope Report Submission

```json
{
  "name": "out_of_scope_report_submission",
  "description": "Reject report submission, moderation, policy evaluation, ranking, summarization, and enrichment inputs.",
  "arguments": {
    "part": "snippet",
    "hl": "en",
    "videoId": "video-123",
    "reasonId": "reason-123"
  },
  "error": {
    "category": "invalid_request",
    "field": "videoId"
  }
}
```

## Metadata Requirements

- Discovery metadata must include public name, upstream resource, upstream method, operation key, quota cost, auth mode, availability state, input contract, response convention, response boundary, error categories, usage notes, caveats, and examples.
- Tool description and examples must visibly include quota cost `1`.
- Usage notes must explain required `part`, required `hl`, API-key access expectations, localization behavior, and empty-success behavior.
- Caveats must state that report submission, moderation, policy adjudication, ranking, summarization, enrichment, and cross-endpoint workflows are outside this tool.

## Safety Requirements

- Results, errors, metadata, examples, and logs must not expose API keys, OAuth tokens, authorization headers, raw upstream diagnostics, stack traces, unsafe request context, or secret-bearing details.
- Empty successful results must not be reported as errors.
- Errors must be machine-readable and deterministic enough for clients to distinguish local validation, access failure, quota failure, endpoint availability, deprecation, and unexpected upstream failure.
