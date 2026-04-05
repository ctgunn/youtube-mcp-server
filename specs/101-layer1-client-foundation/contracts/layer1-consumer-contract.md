# Contract: YT-101 Layer 1 Consumer Contract

## Purpose

Define the internal contract for any higher-layer workflow that consumes typed Layer 1 methods introduced by the shared client foundation.
The representative implementation for this contract lives at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`.

## Consumer Expectations

Higher-layer consumers may rely on:

- typed Layer 1 methods instead of raw upstream request construction
- stable wrapper metadata that identifies endpoint intent and auth expectations
- normalized upstream failures with clear retryability signals
- shared execution behavior for logging, auth selection, and retry classification

Higher-layer consumers must not rely on:

- raw upstream error payload shapes
- wrapper-specific ad hoc auth logic
- direct construction of upstream request paths or methods

## Composition Rules

Consumers may compose multiple Layer 1 methods if they:

- call typed wrapper methods rather than bypassing the foundation
- handle normalized failures consistently across each dependency
- preserve internal observability and failure diagnosis expectations

## Representative Proof Required for YT-101

The feature must demonstrate one representative higher-layer consumer that:

- depends on a typed Layer 1 wrapper method
- avoids embedding raw upstream request logic
- handles normalized failure results without binding to raw upstream payloads

## Validation Expectations

- Contract or integration tests prove the representative consumer uses typed Layer 1 methods
- Regression coverage protects against later changes that reintroduce raw request logic into higher layers
- All new or changed Python functions involved in the consumer seam include reStructuredText docstrings
- Final feature completion requires `python3 -m pytest` from `/Users/ctgunn/Projects/youtube-mcp-server` and `ruff check .`
