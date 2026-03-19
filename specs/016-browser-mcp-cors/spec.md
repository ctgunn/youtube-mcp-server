# Feature Specification: Browser-Originated MCP Access + CORS Support

**Feature Branch**: `016-browser-mcp-cors`  
**Created**: 2026-03-18  
**Status**: Draft  
**Input**: User description: "Review requirements/PRD.md to get an overview of the project and its goals for context. Then, work on implementing the requirements for FND-016, as outlined in requirements/spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Complete Allowed Browser Requests (Priority: P1)

An approved browser-based MCP client needs to complete browser preflight and then make authenticated hosted MCP requests without being blocked by missing or inconsistent cross-origin behavior.

**Why this priority**: FND-016 exists to make browser-originated hosted access explicit and dependable. If approved browser clients cannot complete preflight and actual requests, the browser-facing access model is incomplete.

**Independent Test**: Can be fully tested by sending browser-style preflight and follow-up hosted requests from an allowed origin and confirming the service returns the documented allow headers and the request proceeds normally.

**Acceptance Scenarios**:

1. **Given** a browser-originated client sends a preflight request from an approved origin to a supported hosted MCP route, **When** the request uses a documented method and headers, **Then** the service returns a successful preflight response with the required cross-origin allow headers for that access model.
2. **Given** a browser-originated client has passed preflight from an approved origin, **When** it sends the corresponding hosted MCP request, **Then** the response includes the documented cross-origin headers and preserves the expected hosted MCP behavior.
3. **Given** an approved browser-originated request includes the required authentication context, **When** it reaches a supported hosted MCP route, **Then** the request is handled according to the documented access model instead of failing due to implicit browser-origin restrictions.

---

### User Story 2 - Deny Unsupported Browser Access Predictably (Priority: P2)

An operator needs denied browser origins and unsupported browser request patterns to fail in a stable, explainable way so browser access can be supported deliberately rather than accidentally.

**Why this priority**: A browser-facing contract is not safe unless unsupported origins and unsupported request shapes are rejected predictably. Stable denial behavior is part of the security and operability requirement.

**Independent Test**: Can be fully tested by issuing browser-style preflight and actual requests from disallowed origins or with unsupported patterns and confirming the service rejects them using the documented response behavior.

**Acceptance Scenarios**:

1. **Given** a browser-originated preflight request comes from a disallowed origin, **When** it targets a hosted MCP route, **Then** the service denies the request using the documented response behavior for unsupported browser access.
2. **Given** a browser-originated request uses an unsupported method, header set, or route, **When** it reaches the service, **Then** the service returns a stable failure that distinguishes unsupported browser usage from a successful cross-origin grant.

---

### User Story 3 - Verify Browser Access Before Release (Priority: P3)

An operator or maintainer needs explicit verification coverage for both approved and denied browser access so cross-origin regressions are caught before deployment.

**Why this priority**: Browser behavior often fails silently or only in deployed environments. Verification coverage turns the access model into a maintainable contract instead of documentation alone.

**Independent Test**: Can be fully tested by running automated and documented verification for approved-origin preflight, approved-origin request handling, denied-origin behavior, and unsupported browser patterns.

**Acceptance Scenarios**:

1. **Given** the feature is under verification, **When** the browser-access checks run, **Then** both approved-origin success cases and denied-origin failure cases produce the documented outcomes.
2. **Given** a regression changes hosted response headers or preflight handling, **When** verification runs, **Then** the regression is detected before release with evidence that identifies whether the failure is in approval or denial behavior.


### Edge Cases

- What happens when a browser sends preflight to a hosted path that exists but does not support browser-originated access?
- How does the service behave when a request comes from an allowed origin but omits required authentication context?
- What happens when a browser reuses cached preflight expectations after the allowed-origin configuration changes?
- How does the service respond when the request origin is absent, malformed, or represented in an unexpected case or format?
- What happens when a browser sends extra requested headers beyond the documented supported set?
- How does the service distinguish denied-origin behavior from other hosted failures such as invalid method, invalid session state, or general authentication failure?

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Add failing checks for approved-origin preflight, approved-origin hosted request headers, denied-origin behavior, unsupported browser request patterns, and browser-facing verification evidence for both success and denial paths.
- **Green**: Implement the minimum hosted browser-access behavior needed for supported routes to answer preflight correctly, return the documented allow headers for approved origins, and reject unsupported browser access using stable responses.
- **Refactor**: Consolidate browser-origin policy handling across hosted routes, remove duplicated header and denial logic, and rerun the broader hosted regression suite to confirm session behavior, authentication expectations, and protocol correctness remain unchanged.
- Required test levels: unit tests for origin-policy decisions and header selection; integration tests for hosted preflight and browser-originated request handling; contract tests for documented allow and deny behavior; end-to-end hosted verification for approved and denied browser-originated scenarios.
- Pull request evidence must include failing-to-passing test results for approved and denied browser flows, captured verification steps for browser preflight and actual requests, and examples showing the documented response behavior for both supported and rejected origins.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The hosted service MUST explicitly handle browser preflight requests for each hosted MCP route and method combination that is documented as browser-accessible.
- **FR-002**: For approved browser origins, the service MUST return the documented cross-origin allow headers on successful preflight responses.
- **FR-003**: For approved browser origins, the service MUST return the documented cross-origin response headers on the corresponding hosted MCP responses so the browser can consume the result.
- **FR-004**: The hosted browser-access contract MUST specify which origins are allowed, which hosted routes are browser-accessible, and which methods and request headers are supported for browser-originated use.
- **FR-005**: Requests from disallowed origins MUST fail with stable documented behavior that does not appear to grant cross-origin access.
- **FR-006**: Browser-originated requests that use unsupported routes, methods, or requested headers MUST fail with stable documented behavior distinct from approved-origin success responses.
- **FR-007**: Approved browser-originated access MUST preserve the existing hosted authentication and authorization requirements rather than bypassing them because the request originates in a browser.
- **FR-008**: Browser-originated failure behavior MUST remain distinguishable from other hosted failures, including authentication failures, invalid session state, malformed protocol requests, and unsupported non-browser routes.
- **FR-009**: The feature documentation MUST describe the supported browser-originated access model, including approval criteria, expected preflight behavior, expected request-response headers, and denied-origin behavior.
- **FR-010**: Verification guidance MUST include at least one approved-origin preflight scenario, one approved-origin hosted request scenario, one denied-origin scenario, and one unsupported browser request-pattern scenario.
- **FR-011**: Automated verification MUST cover both successful and denied browser-originated hosted access paths and fail when response-header behavior drifts from the documented contract.
- **FR-012**: Hosted browser-origin support MUST remain consistent across the supported MCP interaction patterns that are documented as browser-accessible.
- **FR-013**: Operators MUST be able to determine from documentation and verification evidence whether browser-originated hosted MCP access is supported, partially supported, or intentionally denied for a given origin and route.
- **FR-014**: The browser-originated access model MUST avoid implicit behavior; supported access and denied access MUST both be deliberate and documented outcomes.

### Key Entities *(include if feature involves data)*

- **Browser Origin Policy**: The documented rule set that determines which browser origins are allowed to reach which hosted MCP routes and under what request conditions.
- **Preflight Request**: The browser-sent permission check that asks whether a hosted route allows a cross-origin method and header combination before the actual request is sent.
- **Browser Access Contract**: The published behavior for supported browser-originated MCP access, including approved routes, request patterns, required headers, and denial rules.
- **Denied Browser Request**: A browser-originated request whose origin, route, method, or requested headers fall outside the documented browser access contract.
- **Verification Scenario**: A documented or automated check that proves the expected behavior for approved-origin success cases and denied-origin rejection cases.

### Assumptions

- FND-013 already established the remote authentication strategy and origin-aware transport hardening that this feature now makes browser-explicit.
- Browser-originated access is scoped to hosted MCP routes and request patterns that the project intentionally documents as supported; this feature does not imply universal browser support for every endpoint.
- The same business-level authentication and authorization rules apply to browser-originated requests as to other hosted remote requests.
- When browser-originated access is not allowed for a route or origin, explicit denial is preferable to ambiguous transport failures.

### Dependencies

- `FND-013` remote MCP security and transport hardening defines the access-control baseline that browser-origin support must extend without weakening.
- `FND-009` and `FND-010` establish the hosted MCP transport and protocol behavior that must remain intact when browser-specific handling is added.
- `FND-015` hosted session durability may interact with browser-accessible flows and must remain compatible with any browser-supported hosted paths.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In release verification, 100% of approved-origin browser preflight scenarios for documented supported routes complete with the documented allow behavior.
- **SC-002**: In release verification, 100% of approved-origin browser request scenarios for documented supported routes return the documented cross-origin response headers while preserving normal hosted MCP outcomes.
- **SC-003**: In denied-origin and unsupported-pattern verification, 100% of tested rejected browser requests fail with the documented denial behavior rather than silent or ambiguous failures.
- **SC-004**: A maintainer can determine the supported browser-origin access contract, approval rules, and denial rules in under 10 minutes using the published documentation alone.
- **SC-005**: Automated verification detects any regression in approved-origin or denied-origin browser behavior before release by failing at least one contract or integration check when the documented header or preflight contract changes unexpectedly.
