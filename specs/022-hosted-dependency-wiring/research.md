# Research: Hosted Dependency Wiring for Secrets and Durable Sessions

## Implementation Targets

- Runtime secret access remains a provider-adapter and hosted-runtime concern, not a generic configuration placeholder.
- Durable session connectivity remains part of the hosted runtime readiness and verification model, not an undocumented infrastructure side effect.
- The existing deployment handoff and hosted verification workflow remain the canonical operator evidence path.
- Hosted dependency verification must show one healthy path plus two distinct failure interpretations: secret-access failure and session-connectivity failure.

## Decision 1: Treat runtime secret access as an explicit provider-wiring contract

- **Decision**: Model runtime secret access as an explicit contract between the GCP provider adapter, the Cloud Run runtime identity, and the hosted deployment handoff rather than relying only on secret names or generic environment validation.
- **Rationale**: The repository currently creates Secret Manager secret objects and validates that secret-backed values are present at runtime, but it does not yet prove that the deployed runtime identity can actually read those secrets. FND-022 needs reviewable wiring and diagnosable readiness for that gap.
- **Alternatives considered**:
  - Keep secret handling as generic environment validation only. Rejected because it cannot distinguish a missing value from missing runtime permissions or broken secret references.
  - Push secret-read behavior entirely into manual deployment steps. Rejected because FND-019 and FND-020 require reviewable, reproducible infrastructure and provider-adapter behavior.

## Decision 2: Treat durable session connectivity as a provider-specific connectivity path

- **Decision**: Model Cloud Run-to-session-backend access as an explicit provider-specific connectivity path that must be documented, reviewed, and validated by readiness and hosted verification.
- **Rationale**: The repository already provisions a Redis-compatible session backend and exports a store URL, but it does not yet define the actual hosted connectivity model or how operators diagnose missing network plumbing. FND-022 closes that deployment gap.
- **Alternatives considered**:
  - Treat the exported session store URL as sufficient proof of connectivity. Rejected because a URL alone does not prove the hosted runtime can reach the backend.
  - Treat session-backend failures as generic runtime startup errors. Rejected because the spec requires operators to distinguish session-connectivity failures from other causes before clients encounter continuation failures.

## Decision 3: Keep readiness classification separate for secret-access and session-connectivity failures

- **Decision**: Extend hosted readiness and verification to preserve separate failure classes for secret-access problems and session-connectivity problems rather than collapsing both into generic configuration failure.
- **Rationale**: Current readiness already treats durable session health as a distinct concern, but secret health is still coupled to generic config validation. Operators need the first failure diagnosis to point to the right provider-wiring remediation path.
- **Alternatives considered**:
  - Use one shared dependency-failure class. Rejected because the remediation paths differ materially between secret IAM/reference issues and network/backend issues.
  - Report only the first failure without classifying it. Rejected because the spec explicitly requires distinguishable verification and readiness outcomes.

## Decision 4: Reuse the existing deployment and hosted verification workflow as the evidence path

- **Decision**: Extend the current workflow built around `infrastructure/gcp/`, `scripts/deploy_cloud_run.sh`, `src/mcp_server/deploy.py`, and `scripts/verify_cloud_run_foundation.py` instead of introducing a separate dependency-verification workflow.
- **Rationale**: The repository already uses the deployment record and hosted verification flow as the rollout proof surface. Reusing that path keeps operator behavior deterministic and aligns with FND-019 and FND-021.
- **Alternatives considered**:
  - Create a separate dependency-only verifier. Rejected because it would duplicate the current hosted verification surface.
  - Rely only on README examples. Rejected because the repository already expects reviewable contract and integration evidence for hosted workflows.

## Decision 5: Keep FND-022 inside the existing provider-adapter boundary

- **Decision**: Treat FND-022 as a provider-adapter enhancement to the current GCP infrastructure path, not as a new shared-platform model or a new hosting abstraction.
- **Rationale**: FND-020 already established the shared-platform contract and FND-021 already established hosted reachability. FND-022 is the missing provider-specific wiring slice that turns those earlier capabilities into a deployable, diagnosable runtime.
- **Alternatives considered**:
  - Redefine the shared platform contract. Rejected because the problem is not a missing abstraction; it is missing provider-specific wiring detail.
  - Introduce a second hosted deployment mode. Rejected because it would add complexity without helping the primary Cloud Run path.

## Decision 6: Preserve local-first workflows as separate from hosted dependency wiring

- **Decision**: Leave `minimal_local` and `hosted_like_local` workflows conceptually separate from the provider-specific hosted dependency wiring required for Cloud Run.
- **Rationale**: The constitution and earlier infrastructure features require local execution to remain first-class. FND-022 should strengthen hosted deployment without making cloud-specific dependency wiring a prerequisite for local work.
- **Alternatives considered**:
  - Require provider-specific secret and networking setup for all verification. Rejected because it breaks the local-first project requirement.
  - Treat hosted-like local verification as proof of Cloud Run dependency wiring. Rejected because it exercises application behavior, not the Cloud Run provider path.

## Decision 7: Add dedicated contracts for secret access, session connectivity, and dependency verification

- **Decision**: Define three explicit contract artifacts for FND-022: one for runtime secret access, one for runtime session connectivity, and one for hosted dependency verification evidence.
- **Rationale**: The feature changes three distinct review surfaces: how the runtime reads protected configuration, how it reaches the durable session backend, and how operators prove both behaviors are wired correctly. Keeping them separate makes review and testing more precise.
- **Alternatives considered**:
  - Extend only the existing IaC foundation contract. Rejected because the runtime and verification behavior would remain too implicit.
  - Extend only the readiness contract. Rejected because infrastructure and deployment evidence are part of the feature scope, not just runtime health responses.
