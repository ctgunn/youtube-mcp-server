# Contract: YT-103 `activities.list` Reuse Contract

## Purpose

Define the internal review and reuse contract that later Layer 2 and Layer 3 work can depend on when deciding whether and how to compose the `activities.list` wrapper.

## Consumer Expectations

Future maintainers may rely on the wrapper artifacts to determine:

- that the wrapper represents `activities.list`
- that the endpoint carries quota cost `1`
- that channel-based retrieval is a public access path
- that `mine` and `home` are authorized-user paths
- that only one supported activity-selection mode can be chosen per request
- that valid empty responses remain successful outcomes

Future maintainers must not need to rely on:

- raw upstream documentation as the only source of auth rules
- ad hoc transport code to infer valid request combinations
- trial-and-error execution to learn whether an empty result is a failure

## Reuse Rules

Higher-layer consumers must choose a supported request mode first and then align auth accordingly:

- Use the channel mode when the workflow needs public channel activity.
- Use `mine` when the workflow needs the caller's own activity feed.
- Use `home` when the workflow needs the caller's home feed.
- Do not combine more than one selection mode in the same wrapper call.

If a workflow needs broader `activities.list` support than this contract documents, that change requires an explicit endpoint-scope update rather than hidden expansion.

## Comparison Rules

The review surface for the wrapper must keep the following visible together:

- `operationKey`
- `quotaCost`
- `authMode`
- `authConditionNote`

This visibility must be strong enough that a maintainer can compare the `activities.list` wrapper against other Layer 1 wrappers without reopening upstream documentation.

## Invalid Combination Rules

The contract must make the following behaviors explicit:

- missing `part` is invalid
- multiple activity-selection modes in one request are invalid
- selecting an authorized-user mode without an authorized-user auth path is invalid
- selecting fields outside the supported wrapper contract is invalid

These invalid states are part of the wrapper contract and must not be hidden behind generic upstream failures.

## Empty Result Rules

The contract must make it clear that:

- a valid request may return zero items
- zero items means no matching recent activity was found
- zero items does not mean the wrapper contract failed

## Validation Expectations

Representative proof for YT-103 must show:

- contract artifacts explain public versus authorized-user access clearly
- contract artifacts explain the single-mode-per-request rule clearly
- endpoint tests protect the wrapper from silently accepting unsupported combinations
- future higher-layer planning can determine the correct `activities.list` usage path in one review pass

## Non-Goals

- This contract does not define the public Layer 2 tool for `activities.list`.
- This contract does not attempt exhaustive coverage of every upstream option for the endpoint.
- This contract does not change hosted MCP transport behavior.
