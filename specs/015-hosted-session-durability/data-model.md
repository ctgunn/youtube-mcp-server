# Data Model: FND-015 Hosted MCP Session Durability

## Entity: HostedSessionRecord
Description: The durable shared-state record representing one active hosted MCP session.

Fields:
- `sessionId` (string, required): The client-visible MCP session identifier issued during initialize.
- `protocolVersion` (string, required): The negotiated MCP protocol version associated with the session.
- `state` (string, required): Session lifecycle state such as active, expired, or closed.
- `createdAt` (timestamp, required): When the hosted session was created.
- `lastActivityAt` (timestamp, required): Most recent successful hosted interaction for the session.
- `expiresAt` (timestamp, required): The time after which the session is no longer valid for continuation.
- `clientMetadata` (object, optional): Client identity details captured during initialize.
- `continuityMode` (string, required): The documented strategy used to preserve hosted continuity for this session.

Validation rules:
- `sessionId` MUST be globally unique across active hosted sessions.
- `state` MUST transition only through the documented lifecycle.
- `expiresAt` MUST be later than `lastActivityAt` for active sessions.
- `continuityMode` MUST correspond to the active deployment topology.

## Entity: SessionReplayRecord
Description: Durable replay metadata and recent event history associated with one hosted session stream.

Fields:
- `sessionId` (string, required): The hosted session this replay state belongs to.
- `streamId` (string, required): The logical stream identifier for event delivery.
- `lastEventId` (string, optional): The most recent replayable event identifier.
- `events` (list, required): Ordered recent event records retained for reconnect and replay.
- `replayWindowEndsAt` (timestamp, required): The time after which replay history is no longer guaranteed.
- `state` (string, required): Replay state such as open, completed, expired, or unavailable.

Validation rules:
- `events` MUST remain ordered by delivery sequence.
- `lastEventId`, when present, MUST match the newest replayable event in `events`.
- Replay state MUST become unavailable or expired once `replayWindowEndsAt` has passed.
- Replay data MUST be attributable to exactly one `sessionId`.

## Entity: SessionEvent
Description: One replayable hosted event stored for continuation or reconnect.

Fields:
- `eventId` (string, required): Stable event cursor used by reconnecting clients.
- `eventType` (string, required): Logical event category delivered over the hosted stream.
- `payloadClass` (string, required): Classification of the event payload for transport handling.
- `payload` (object or null, required): The JSON-RPC or primer event body.
- `createdAt` (timestamp, required): When the event was recorded.
- `deliveryState` (string, required): Delivery summary such as queued, sent, or replayed.

Validation rules:
- `eventId` MUST increase monotonically within a stream.
- `payload` MUST remain protocol-safe for hosted replay.
- Events outside the replay window MUST not be returned as if they were still available.

## Entity: SessionTopologyPolicy
Description: Operator-facing configuration that determines whether a deployment is allowed to advertise durable hosted sessions.

Fields:
- `durabilityRequired` (boolean, required): Whether the runtime must block readiness if the shared session backend is unavailable.
- `sharedBackendConfigured` (boolean, required): Whether a shared durable session backend is configured.
- `sharedBackendHealthy` (boolean, required): Whether the configured backend can currently satisfy session reads and writes.
- `supportedTopology` (string, required): The deployment mode the runtime is prepared to support, such as multi-instance-shared-state.
- `unsupportedReason` (string, optional): Human-readable explanation when durable hosted sessions are not supportable.

Validation rules:
- Hosted runtimes advertising durable sessions MUST require both `sharedBackendConfigured` and `sharedBackendHealthy`.
- `unsupportedReason` MUST be populated when the topology is not safe for durable hosted sessions.
- The policy MUST align with readiness and operator documentation.

## Entity: SessionContinuationAttempt
Description: One client attempt to continue or reconnect an existing hosted session.

Fields:
- `sessionId` (string, required): The hosted session being resumed.
- `requestMethod` (string, required): Follow-up hosted method such as `GET` or `POST`.
- `lastEventId` (string, optional): Replay cursor presented by the client.
- `attemptedAt` (timestamp, required): When the continuation attempt occurred.
- `outcome` (string, required): Result such as continued, replayed, expired, invalid, or replay_unavailable.
- `failureCategory` (string, optional): Stable session-state failure category when continuation fails.

Validation rules:
- Successful continuation MUST touch `lastActivityAt` on the associated `HostedSessionRecord`.
- Failed attempts MUST map to stable session-state categories.
- `replay_unavailable` MUST be distinguishable from `invalid` or `expired`.

## Entity: VerificationEvidence
Description: The operator-facing record proving durable hosted session behavior for the supported deployment model.

Fields:
- `initializeEvidence` (object, required): Proof that hosted initialize created a reusable session.
- `continuationEvidence` (object, required): Proof that follow-up `GET` and `POST` requests succeeded through the supported continuity model.
- `reconnectEvidence` (object, required): Proof that replay or reconnect succeeded within the replay window.
- `failureEvidence` (object, required): Proof that expired, invalid, or replay-unavailable sessions fail in the documented way.
- `requestIds` (list of string, required): Correlatable identifiers for the verification run.

Validation rules:
- Evidence MUST cover both success and expected failure paths.
- Evidence MUST be sufficient to distinguish continuity success from fallback-to-local-memory behavior.
- Request identifiers MUST remain safe for operator exposure.

## Relationships

- `HostedSessionRecord` owns zero or more `SessionReplayRecord` values over its lifetime.
- `SessionReplayRecord` contains zero or more ordered `SessionEvent` values.
- `SessionTopologyPolicy` governs whether `HostedSessionRecord` values may be created and treated as durable.
- `SessionContinuationAttempt` references one `HostedSessionRecord` and may consume one `SessionReplayRecord`.
- `VerificationEvidence` references initialize, continuation, reconnect, and failure outcomes derived from the other entities.

## State Transitions

1. Client initializes hosted MCP session -> `HostedSessionRecord.state` becomes `active`.
2. Session emits replayable events -> `SessionReplayRecord.state` remains `open` while events stay within the replay window.
3. Client sends valid follow-up `GET` or `POST` -> `HostedSessionRecord.lastActivityAt` advances and the continuation attempt outcome is `continued` or `replayed`.
4. Replay window passes without renewal -> `SessionReplayRecord.state` becomes `expired` or `unavailable`.
5. Session TTL passes or operator closes the session -> `HostedSessionRecord.state` becomes `expired` or `closed`.
6. Client attempts continuation after expiry or with bad identity -> continuation attempt outcome becomes `expired`, `invalid`, or `replay_unavailable` with the matching stable failure category.
