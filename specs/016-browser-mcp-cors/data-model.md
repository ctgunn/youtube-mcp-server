# Data Model: FND-016 Browser-Originated MCP Access + CORS Support

## Entity: BrowserOriginPolicy
Description: The runtime policy that determines whether a browser origin may access a hosted route and under which request conditions.

Fields:
- `origin` (string, required): The normalized browser origin presented by the client.
- `originType` (string, required): Whether the request is treated as browser-originated or originless non-browser traffic.
- `allowed` (boolean, required): Whether the origin qualifies for documented browser access.
- `supportedRoutes` (list of string, required): Hosted routes that may be reached by this origin through browser flows.
- `supportedMethods` (list of string, required): Browser request methods that may be used on the supported routes.
- `supportedRequestHeaders` (list of string, required): Requested browser headers that may be granted for cross-origin use.
- `denialReason` (string, optional): Stable reason when browser access is denied or unsupported.

Validation rules:
- `origin` MUST be normalized before comparison.
- `originType` MUST distinguish browser-originated requests from originless non-browser requests.
- `allowed` MUST only be true when the origin matches the documented browser policy.
- `denialReason` MUST be populated when `allowed` is false for a browser-originated request.

## Entity: BrowserPreflightRequest
Description: The browser-sent request that asks whether a hosted route may be called cross-origin.

Fields:
- `origin` (string, required): The requesting browser origin.
- `targetRoute` (string, required): Hosted route the browser wants to call.
- `requestedMethod` (string, required): The method the browser intends to use for the actual request.
- `requestedHeaders` (list of string, optional): Headers the browser intends to send with the actual request.
- `requestedAt` (timestamp, required): When the preflight was evaluated.

Validation rules:
- `targetRoute` MUST be one of the known hosted routes before preflight can succeed.
- `requestedMethod` MUST be explicitly supported for the target route.
- Requested headers outside the documented supported set MUST lead to a denied or unsupported outcome.

## Entity: BrowserAccessResponsePolicy
Description: The response-header policy applied when the hosted service answers a browser preflight or actual request.

Fields:
- `allowOriginHeader` (string, optional): The origin value echoed or granted for a supported browser response.
- `allowMethods` (list of string, optional): Methods granted for browser use on the target route.
- `allowHeaders` (list of string, optional): Request headers granted for browser use.
- `exposeHeaders` (list of string, optional): Response headers that browser clients may read.
- `appliesTo` (string, required): Whether the policy applies to preflight, actual response, or both.
- `policyState` (string, required): Applied, denied, or not_applicable.

Validation rules:
- `allowOriginHeader` MUST only be present for approved browser requests.
- `policyState` MUST be `denied` or `not_applicable` when browser access is not granted.
- `exposeHeaders` MUST include any response headers that browser clients need to continue the documented hosted flow.

## Entity: BrowserRequestOutcome
Description: The final hosted outcome of a browser-originated request after origin, route, method, header, and authentication evaluation.

Fields:
- `requestType` (string, required): Preflight or actual.
- `origin` (string, optional): Browser origin when present.
- `targetRoute` (string, required): Hosted route that was requested.
- `statusFamily` (string, required): Success, denied, malformed, unauthenticated, or unsupported.
- `decisionCategory` (string, required): Stable category explaining the outcome.
- `authEvaluated` (boolean, required): Whether authentication checks were part of the outcome.
- `responsePolicy` (object, required): The applied browser response-header policy.
- `requestId` (string, required): Correlatable request identifier for observability and verification.

Validation rules:
- `decisionCategory` MUST distinguish origin denial from unsupported browser request patterns and authentication failures.
- `authEvaluated` MUST remain false for preflight-only decisions when credentials are not part of the flow.
- `responsePolicy` MUST align with the final browser decision and must not indicate success for denied origins.

## Entity: BrowserVerificationEvidence
Description: The release and operator-facing record proving browser-originated hosted access behaves as documented.

Fields:
- `approvedPreflightEvidence` (object, required): Proof that an approved origin received the expected preflight behavior.
- `approvedRequestEvidence` (object, required): Proof that an approved origin received the documented browser response headers on actual hosted MCP responses.
- `deniedOriginEvidence` (object, required): Proof that a disallowed origin failed with the documented denial behavior.
- `unsupportedPatternEvidence` (object, required): Proof that unsupported browser request patterns fail distinctly from approved access.
- `requestIds` (list of string, required): Correlatable request identifiers for the verification run.

Validation rules:
- Evidence MUST cover both success and failure paths.
- Evidence MUST be sufficient to show that browser support is explicit rather than accidental.
- Request identifiers MUST remain safe for operator exposure.

## Relationships

- `BrowserOriginPolicy` governs whether a `BrowserPreflightRequest` may succeed.
- `BrowserAccessResponsePolicy` is derived from `BrowserOriginPolicy` and attached to a `BrowserRequestOutcome`.
- `BrowserRequestOutcome` references one browser request and one applied response policy.
- `BrowserVerificationEvidence` aggregates approved and denied outcomes derived from the other entities.

## State Transitions

1. Browser sends preflight -> `BrowserPreflightRequest` is evaluated against `BrowserOriginPolicy`.
2. Approved preflight -> `BrowserAccessResponsePolicy.policyState` becomes `applied` for preflight and the route is eligible for the actual browser request.
3. Denied origin or unsupported pattern -> `BrowserRequestOutcome.statusFamily` becomes `denied` or `unsupported` with a stable `decisionCategory`.
4. Approved actual browser request -> response policy is applied to the hosted MCP response while normal auth and session rules continue to govern the request.
5. Verification runs -> `BrowserVerificationEvidence` captures approved and denied request outcomes with request IDs for review.
