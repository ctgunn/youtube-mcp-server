# Data Model: CI/CD Quality Gates

OPS-401 adds no database or runtime persistence. These are logical records represented by checked-in workflow metadata and existing file-based release evidence.

## Quality Evaluation

| Field | Description | Validation |
|---|---|---|
| `revision_sha` | Full immutable commit identifier that was evaluated. | Required; must equal the checked-out revision used by the protected PR or release run. |
| `lint_status` | Outcome of the lint check. | One of `pending`, `pass`, `fail`, `cancelled`, or `missing`. |
| `typecheck_status` | Outcome of static type validation. | Same allowed values; evaluates the designated initial source scope. |
| `tests_status` | Outcome of the full automated repository suite. | Same allowed values; `pass` only after the suite completes successfully. |
| `evaluated_at` | Time the evaluation completed. | Required for released evidence; no secret or credential data. |
| `check_source` | Origin of the check result. | For required PR checks, must identify GitHub Actions. |

**Eligibility rule**: A quality evaluation is `eligible` only when all three statuses are `pass` for the current protected revision. `pending`, `fail`, `cancelled`, and `missing` are non-eligible states and block the protected merge/deployment flow.

## Protected Revision

| Field | Description | Validation |
|---|---|---|
| `revision_sha` | The immutable source revision proposed for merge or release. | Required; must match the associated quality evaluation. |
| `base_branch` | Protected branch to which the pull request is directed. | Must be `main` for OPS-401's required ruleset. |
| `merge_eligibility` | Result of repository quality governance. | `blocked` until the associated quality evaluation is eligible; separate review/authorization controls remain outside this feature. |
| `release_eligibility` | Result of the deployment preconditions. | `blocked` unless quality and preflight both pass for this revision. |

**State transitions**:

```text
proposed -> evaluating -> eligible
                      -> blocked
eligible -> evaluating  (when a new revision or current-base requirement invalidates prior evidence)
```

## Release Provenance

| Field | Description | Validation |
|---|---|---|
| `revision_sha` | Full source commit used to build the release. | Required; must equal the quality-evaluation and checkout SHA. |
| `image_digest` | Immutable identifier of the published image bytes. | Required after publication; must be the image deployed. |
| `target_environment` | Non-secret deployment environment label. | Required; must be an approved target such as staging or production. |
| `quality_evaluation` | Reference or embedded safe summary of required check statuses. | Required; all statuses must be `pass` before release continues. |
| `preflight_status` | Result of safe prerequisite validation. | Must be `pass` before build/deploy stages. |

**State transitions**:

```text
requested -> preflight_passed -> quality_passed -> image_published -> deployed -> verified
          -> blocked            -> blocked        -> failed          -> failed    -> failed
```

No transition to `image_published`, `deployed`, or `verified` is allowed from a failed, cancelled, missing, pending, or mismatched quality/preflight result.

## Deployment Verification Record

| Field | Description | Validation |
|---|---|---|
| `deployment_revision` | Provider-visible revision identifier. | Required after a successful deployment attempt. |
| `revision_sha` | Associated source revision. | Must match release provenance. |
| `image_digest` | Associated immutable image. | Must match release provenance and deployed image. |
| `verification_status` | Result of post-deployment verification. | `pass` or `fail`; a failure makes the release unsuccessful. |
| `evidence_paths` | Paths to non-secret image, deployment, and verification artifacts. | Must not contain credential values or raw credential-bearing environment output. |

## Release Procedure

| Field | Description | Validation |
|---|---|---|
| `prerequisites` | Documented local, access, environment, and non-secret configuration requirements. | Complete enough for an authorized operator's clean-checkout run. |
| `quality_command` | Canonical command that executes all three quality categories. | Must be `make quality`. |
| `build_steps` | Ordered source-to-image actions. | Must use the resolved source revision and emit immutable image provenance. |
| `deployment_steps` | Ordered infrastructure, rollout, and verification actions. | Must not begin until preflight and quality pass. |
| `failure_guidance` | Safe remediation instructions. | Identifies category/stage without secret values. |

## Relationships

```text
Protected Revision 1 --- 1 Quality Evaluation
Protected Revision 1 --- 0..1 Release Provenance
Release Provenance 1 --- 1 Deployment Verification Record
Release Procedure 1 --- * Quality Evaluation / Release Provenance executions
```
