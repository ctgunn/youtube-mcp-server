# Release Procedure and Deployment Guard Contract

## Purpose

Define the supported local, automatic, and fallback release behavior for OPS-401. This contract preserves the existing Cloud Build, Terraform, deploy-script, and hosted-verification paths while preventing quality or provenance failures from reaching a deployment stage.

## Supported Paths

| Path | Owner | Required behavior |
|---|---|---|
| Local quality validation | Maintainer | Installs declared development tooling and runs `make quality` from a clean checkout. |
| Primary automated release | Cloud Build | Runs for the externally configured `main` trigger and remains the primary automatic owner. |
| Manual fallback release | GitHub Actions | Remains explicitly dispatched by an authorized operator and resolves the actual checked-out revision before quality evaluation. |
| Manual operator release/verification | Authorized operator | Uses the existing documented GCP/Terraform, deployment-script, and verification-script procedures with valid non-production inputs. |

## Ordered Release Gate

Every supported automated release uses this order for one resolved source revision:

```text
checkout resolved commit
  -> safe preflight
  -> make quality
  -> build and publish image
  -> resolve immutable image digest and record provenance
  -> infrastructure reconciliation
  -> export infrastructure outputs
  -> deploy through scripts/deploy_cloud_run.sh
  -> verify through scripts/verify_cloud_run_foundation.py
```

Safe preflight and `make quality` must both pass before image build, publication, Terraform reconciliation, or deployment. The existing deployment verification remains a final release gate; a release is not successful until it passes.

## Revision and Evidence Contract

- The workflow determines the source revision from the actual checkout's full commit SHA, not from a mutable user-supplied ref, short SHA, or branch name alone.
- Lint, typecheck, and tests evaluate that resolved SHA.
- The published image is resolved to an immutable digest before the deployment is treated as eligible to continue.
- The deployment uses the image identified by that digest.
- Non-secret release evidence associates the source SHA, image digest, target environment label, per-category quality statuses, preflight result, provider deployment revision, and hosted verification result.
- Existing image-reference, Terraform-output, deployment, and verification artifacts remain reviewable. The evidence format must not include environment dumps, bearer tokens, API keys, or any other credential value.

## Preflight Contract

Preflight validates only safe categories: required non-secret configuration, target/revision resolution, artifact destination, workflow identity/permission, and presence/accessibility of required secret references. It may report a missing name or category, but it must never serialize, print, or request a secret value as evidence.

| Condition | Required result |
|---|---|
| Missing prerequisite or inaccessible required reference | Stop before image build and identify a safe prerequisite category. |
| Failed, cancelled, missing, skipped, pending, or mismatched quality result | Stop before image build and identify the quality category/revision mismatch. |
| Digest unavailable or does not identify the image to deploy | Stop before deployment and identify provenance failure. |
| Infrastructure, deployment, or hosted verification failure | Preserve existing stage-specific failure reporting and do not report release success. |

## Documentation and Reproducibility Contract

The README must provide one supported build procedure and one supported deployment-and-verification procedure. Each includes prerequisites, required non-secret operator inputs, ordered commands, expected evidence, local-versus-hosted scope, and safe missing-input remediation. A clean-checkout maintainer with authorized non-production access must be able to reproduce the specified procedure without an undocumented repository step.

## Verification Obligations

- Workflow and integration tests assert `make quality` and safe preflight happen before every later release stage in both automated paths.
- Negative tests show that a failure in each quality category, a missing/cancelled result, a ref/SHA mismatch, a missing safe prerequisite, and a digest mismatch cannot invoke a later stage.
- A controlled clean-checkout exercise proves the local quality/build procedure; an authorized non-production exercise proves deployment/verification evidence and no secret disclosure.
