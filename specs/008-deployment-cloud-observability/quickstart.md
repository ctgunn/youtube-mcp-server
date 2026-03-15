# Quickstart: FND-008 Deployment Execution + Cloud Run Observability

## Objective

Implement deployment execution, deployment metadata capture, and hosted
structured runtime log emission for the existing Cloud Run foundation service.

## Prerequisites

- Python 3.11+
- Feature branch: `008-deployment-cloud-observability`
- Foundation slices through FND-007 available in the current branch
- Access to the target Cloud Run project and hosted logging view

## Red Phase (write failing tests and checks first)

1. Add failing unit and integration coverage for deployment execution:
   - deployment script executes the deploy action instead of printing only the
     command
   - deployment failures stop the workflow with actionable output
2. Add failing unit, integration, or contract coverage for deployment outcome
   capture:
   - successful runs include revision name and service URL
   - successful runs include runtime identity, environment profile, scaling,
     concurrency, and timeout
   - partial metadata capture is classified as `incomplete`
3. Add failing integration and contract coverage for hosted structured logging:
   - `/health` and `/ready` emit structured log events
   - `/mcp` success and failure paths emit structured log events
   - unsupported paths emit structured log events
   - `toolName` is present only for tool calls
4. Run targeted suites and confirm failures:

```bash
python3 -m unittest discover -s tests/unit -p 'test_*.py'
python3 -m unittest discover -s tests/integration -p 'test_*.py'
python3 -m unittest discover -s tests/contract -p 'test_*.py'
```

## Green Phase (minimal implementation)

1. Update the deployment workflow so it executes the hosted deploy command
   using the validated deployment input set.
2. Capture and return one deployment outcome record containing:
   - outcome classification
   - revision name
   - service URL
   - runtime settings summary
   - failure stage and remediation when applicable
3. Update hosted runtime observability so each handled request emits one
   structured JSON log event to runtime output while preserving current
   in-memory event recording for tests.
4. Re-run targeted suites until all pass:

```bash
python3 -m unittest discover -s tests/unit -p 'test_*.py'
python3 -m unittest discover -s tests/integration -p 'test_*.py'
python3 -m unittest discover -s tests/contract -p 'test_*.py'
```

## Refactor Phase (behavior-preserving cleanup)

1. Consolidate deployment-result shaping and metadata extraction into shared
   helpers.
2. Consolidate hosted log-event shaping so runtime emission and in-memory
   recording use the same canonical event schema.
3. Re-run the full regression suite:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Manual Hosted Validation Flow

1. Prepare deployment inputs for project, region, service, image, runtime
   identity, environment, scaling, concurrency, timeout, and secret references.
2. Execute the deployment workflow and capture the returned deployment outcome
   record.
3. Confirm the deployment record includes:
   - `revisionName`
   - `serviceUrl`
   - runtime settings summary
4. Save the deployment record to `artifacts/cloud-run-deployment.json`.
5. Run hosted verification using the saved deployment record:

```bash
PYTHONPATH=src python3 scripts/verify_cloud_run_foundation.py \
  --deployment-record artifacts/cloud-run-deployment.json \
  --evidence-file artifacts/cloud-run-verification.txt
```

6. Send hosted requests to `/health`, `/ready`, and `/mcp`.
7. Inspect the hosted logging view and confirm each request produced a
   structured log event with:
   - `requestId`
   - `path`
   - `status`
   - `latencyMs`
   - `toolName` for tool calls only
8. If deployment fails or metadata capture is incomplete, use the reported
   failure stage and remediation guidance before retrying.

## Success Evidence

- Deployment workflow executes one hosted deployment path directly.
- Every successful deployment produces a retained deployment outcome record with
  revision and runtime metadata.
- Hosted probe, MCP, and failure traffic produce structured runtime log events
  visible to operators.
- Targeted and full regression test suites pass before feature completion.
