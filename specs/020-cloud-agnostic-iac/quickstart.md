# Quickstart: Cloud-Agnostic Infrastructure Module Strategy

## 1. Review the Shared Platform Contract

Use this step to understand the shared platform contract before looking at any provider-specific implementation.

1. Read [shared-platform-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/contracts/shared-platform-contract.md).
2. Confirm the required shared capabilities cover hosted runtime, ingress, identity, secrets, observability, and durable session support.
3. Confirm the shared contract preserves one application deployment model and does not turn provider modules into a prerequisite for local work.

Expected outcome: reviewers understand the portable platform boundary independently of any one provider.

## 2. Map the Current GCP Foundation to the Shared Contract

Use this step to interpret the existing foundation as the primary provider adapter.

1. Review `infrastructure/gcp/README.md` and the FND-019 contract artifacts.
2. Match each GCP-hosted capability and output to the shared platform contract.
3. Confirm the current deployment handoff to `scripts/deploy_cloud_run.sh` remains the application deployment model rather than becoming a provider-specific rewrite.

Expected outcome: the current GCP path is understood as a primary provider adapter, not as the platform model itself.

## 3. Evaluate the Secondary Provider Adapter

Use this step to prove the layout is portable beyond the primary provider.

1. Read [aws-provider-adapter-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/contracts/aws-provider-adapter-contract.md) as the AWS provider adapter.
2. Compare the AWS capability mapping expectations against the shared platform contract.
3. Record any partial or unsupported capabilities before treating the secondary path as production-ready.

Expected outcome: maintainers can reason about a second provider without redefining the application deployment model.

## 4. Confirm Execution Mode Boundaries

Use this step to ensure local-first workflows remain intact across the documented execution modes.

1. Read [execution-mode-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/contracts/execution-mode-contract.md).
2. Compare its mode definitions with `README.md` and `infrastructure/local/README.md`.
3. Confirm the minimal local runtime remains independent of cloud-provider modules and that hosted-like local verification stays a separate path.

Expected outcome: local, hosted-like local, and hosted workflows are all documented as related execution modes of the same shared platform contract.

## 5. Planning-to-Implementation Handoff

Use this step when implementation work begins.

1. Add failing contract and integration tests that lock the shared capability vocabulary and provider-adapter boundaries.
2. Refactor the current GCP documentation and infrastructure assets behind the shared contract without changing the application deployment model.
3. Add the minimum secondary-provider scaffold or planning assets needed to keep portability reviewable.
4. Run the full repository test suite:
   `pytest`

Expected outcome: the feature moves from planning into implementation with explicit Red-Green-Refactor ordering and a preserved full-suite validation gate.
