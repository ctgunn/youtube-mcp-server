# Research: Cloud Run Public Reachability for Remote MCP

## Implementation Targets

- Cloud Run public invocation remains an operator and provider-adapter concern, not an MCP authentication mechanism.
- MCP bearer-token enforcement remains exclusively at the protected `/mcp` application boundary.
- The existing deployment and hosted verification workflow remains the canonical evidence path.
- Public reachability evidence must show one success path plus two distinct failure interpretations: cloud-level denial and MCP-layer denial.

## Decision 1: Keep Cloud Run public reachability separate from MCP bearer-token authentication

- **Decision**: Treat Cloud Run public invocation as the network-level reachability control for the hosted service, while preserving bearer-token checks on protected `/mcp` routes as the application-layer access control.
- **Rationale**: The repository already defines `/health` and `/ready` as unauthenticated hosted routes and `/mcp` as bearer-protected in [hosted-mcp-security.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/013-remote-mcp-security/contracts/hosted-mcp-security.md). That separation lets operators distinguish “the service can be reached” from “the caller is authorized to use MCP.”
- **Alternatives considered**:
  - Use MCP bearer tokens as the only hosted access control. Rejected because a request denied before reaching the application cannot meaningfully participate in the MCP auth contract.
  - Treat Cloud Run IAM as the primary remote-consumer auth layer. Rejected because the existing hosted security contract centers remote MCP access on bearer-token authentication managed by the application.

## Decision 2: Reuse the existing hosted verifier as the canonical evidence path

- **Decision**: Extend the existing deployment-to-verification handoff built around [deploy_cloud_run.sh](/Users/ctgunn/Projects/youtube-mcp-server/scripts/deploy_cloud_run.sh), [verify_cloud_run_foundation.py](/Users/ctgunn/Projects/youtube-mcp-server/scripts/verify_cloud_run_foundation.py), and [deploy.py](/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/deploy.py) instead of introducing a second verification tool.
- **Rationale**: The repository already treats the deployment record and hosted verification evidence as the rollout proof surface. Reusing that path keeps operator behavior deterministic and avoids duplicating verification logic.
- **Alternatives considered**:
  - Add a separate verification CLI just for public reachability. Rejected because it would duplicate the current deployment handoff model.
  - Rely only on manual `curl` examples. Rejected because the repository prefers scripted verification evidence and testable contract artifacts.

## Decision 3: Verify public reachability before authenticated MCP success

- **Decision**: Keep hosted verification as a two-layer flow: prove the hosted service is reachable first, then prove authenticated MCP access second.
- **Rationale**: The existing verifier already checks `/health` and `/ready` before protected MCP flows, which cleanly separates platform availability from authenticated MCP behavior. FND-021 should make that ordering explicit as part of the contract.
- **Alternatives considered**:
  - Verify only authenticated `/mcp` requests. Rejected because a failed protected request would blur platform reachability and application authorization.
  - Treat `/health` or `/ready` as authenticated proof. Rejected because those routes intentionally remain unauthenticated.

## Decision 4: Distinguish cloud-level denial from MCP-layer denial through separate evidence, not only status codes

- **Decision**: Model cloud-level denial as a verification outcome outside the MCP denial taxonomy, and reuse the existing MCP denial categories only once a request has reached the hosted application.
- **Rationale**: The existing hosted security contract and runtime already use stable MCP-layer categories such as `unauthenticated`, `invalid_credential`, and `origin_denied`. A Cloud Run denial happens before that contract applies and therefore needs its own operator-facing evidence rather than a fabricated MCP error.
- **Alternatives considered**:
  - Distinguish failures only by HTTP status. Rejected because platform denial and MCP denial can both appear as 4xx responses without enough diagnostic context.
  - Invent a new MCP error category for platform denial. Rejected because platform denial occurs before MCP processing begins.

## Decision 5: Add a dedicated public-access contract plus a dedicated verification-evidence contract

- **Decision**: Define two explicit contract artifacts for FND-021: one for the Cloud Run public-access workflow and one for hosted reachability-verification evidence.
- **Rationale**: Existing contracts already split provider-adapter deployment concerns from hosted security concerns. FND-021 fits cleanly as a new review surface for public invocation intent and operator-visible proof without overloading either the GCP foundation contract or the hosted security contract.
- **Alternatives considered**:
  - Extend only the hosted security contract. Rejected because FND-021 is also an infrastructure and operator-workflow feature.
  - Extend only the GCP foundation contract. Rejected because public reachability and denial interpretation are a distinct behavior slice with their own verification semantics.

## Decision 6: Keep public-access intent explicit in the provider adapter and review artifacts

- **Decision**: Treat public invocation as an intentional deployment input and review concern in the GCP provider adapter, not as an implicit provider default.
- **Rationale**: The repository already models operator-visible runtime and security settings through `infrastructure/gcp/`, `README.md`, and deployment metadata. FND-021 should extend that pattern so reviewers can see whether an environment is intended for trusted public remote MCP access.
- **Alternatives considered**:
  - Rely on platform defaults or one-time console settings. Rejected because that undermines reproducibility and reviewability.
  - Make every environment public by assumption. Rejected because the spec allows intentionally private environments.

## Decision 7: Preserve local-first execution as a separate concern

- **Decision**: Keep `minimal_local` and `hosted_like_local` execution modes unchanged and outside any requirement to expose a public hosted endpoint.
- **Rationale**: The shared platform contract and local infrastructure docs already preserve a provider-free local path. FND-021 must not turn public Cloud Run access into a prerequisite for development or hosted-like local verification.
- **Alternatives considered**:
  - Require a public hosted endpoint for all verification. Rejected because it would break the project’s local-first development guarantee.
  - Treat hosted-like local verification as evidence of public reachability. Rejected because it exercises application behavior, not public Internet exposure.
