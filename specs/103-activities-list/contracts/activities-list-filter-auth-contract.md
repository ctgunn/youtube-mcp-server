# Contract: YT-103 `activities.list` Filter and Auth Contract

## Purpose

Define how maintainers and future Layer 2 or Layer 3 authors choose the correct `activities.list` selector profile and auth path without relying on raw upstream endpoint research.

## Supported Selector Profiles

YT-103 supports three selector profiles for `activities.list`:

- `channelId`: public channel activity retrieval
- `mine`: authorized user activity retrieval
- `home`: authorized user home-feed retrieval

Each request must choose exactly one of these profiles.

## Auth Modeling Rules

The wrapper must be reviewable as a mixed or conditional-auth endpoint because supported request profiles do not share one stable auth requirement.

The contract must make these distinctions explicit:

- `channelId` is the public channel profile
- `mine` requires authorized user context
- `home` requires authorized user context
- wrapper-facing documentation must explain why the wrapper is mixed or conditional rather than purely public or purely authorized

Later Layer 2 and Layer 3 authors must be able to determine the correct access path from maintainer-facing artifacts alone.

## Invalid Combination Rules

The following request states are invalid for the YT-103 wrapper contract:

- no supported selector profile is provided
- more than one supported selector profile is provided
- `channelId` is combined with `mine`
- `channelId` is combined with `home`
- `mine` is combined with `home`
- a selector profile is used with an auth path that contradicts the contract's documented expectation

Unsupported or ambiguous selector states must be rejected or clearly flagged before the request is treated as a supported wrapper call.

## Consumer Guidance

Future Layer 2 and Layer 3 work may rely on this contract to answer:

- when to use the wrapper for public channel activity retrieval
- when an authorized-user activity view is required instead
- which selector combinations are unsupported and must not be hidden behind later tools
- how to preserve empty-result semantics without converting normal no-item states into failures

Future consumers must not need to infer:

- selector precedence when multiple profiles are present
- whether a profile can switch between public and authorized behavior silently
- whether empty results represent an error condition

## Validation Expectations

Representative proof for YT-103 must show:

- contract artifacts define the supported selector profiles explicitly
- mixed or conditional auth labeling is visible and justified
- invalid selector combinations are called out clearly enough for testable enforcement
- later-layer consumers can distinguish public and authorized request paths without extra endpoint research

Required coverage:

- contract checks for this feature-local filter and auth contract artifact
- unit checks for invalid selector combinations
- integration checks for representative public and authorized request paths

## Non-Goals

- This contract does not require exhaustive support for every optional `activities.list` parameter.
- This contract does not define the public Layer 2 tool surface for YT-203.
- This contract does not change hosted transport, security policy, or deployment behavior.
