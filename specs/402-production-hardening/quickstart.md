# Production Hardening Quickstart

## 1. Verify the local baseline

From the repository root, install the documented development dependencies and run:

```bash
make quality
```

The command must finish successfully before adding hardening behavior. It runs linting, type checking, and the complete test suite.

## 2. Run deterministic hardening verification

After implementation, run the focused checks before the full suite:

```bash
python3 -m pytest \
  tests/unit/test_production_hardening_config.py \
  tests/unit/test_rate_limit_policy.py \
  tests/unit/test_result_cache_policy.py \
  tests/unit/test_alert_lifecycle.py \
  tests/contract/test_production_hardening_mcp_contract.py \
  tests/contract/test_production_hardening_iac_contract.py \
  tests/integration/test_production_hardening_hosted_flow.py \
  tests/integration/test_production_hardening_observability.py
make quality
```

Expected evidence includes an accepted and rejected tool call, no rejected upstream invocation, an eligible cache hit and expiry refresh, an ineligible sensitive call bypass, one incident opening, no duplicate open notification, and one recovery after 15 normal minutes.

## 3. Configure local hardening behavior

Use non-secret local configuration values only. The defaults are:

```text
MCP_RATE_LIMIT_IDENTIFIED_REQUESTS_PER_MINUTE=60
MCP_RATE_LIMIT_ANONYMOUS_REQUESTS_PER_MINUTE=10
MCP_RATE_LIMIT_WINDOW_SECONDS=60
MCP_RESULT_CACHE_ENABLED=true
MCP_RESULT_CACHE_BACKEND=memory
MCP_RESULT_CACHE_MAX_FRESHNESS_SECONDS=300
MCP_ALERTING_ENABLED=false
```

Local memory-backed behavior is for one process and deterministic tests only. Do not put bearer tokens, Redis URLs with credentials, notification endpoints, or caller identity values in checked-in configuration, log output, or test fixtures.

## 4. Prepare hosted configuration

For staging/production, configure the hardening stores to use the existing approved Redis-compatible shared dependency. Configure a trusted identity source only when the selected gateway removes caller-supplied values and asserts the principal after authentication; otherwise the validated credential represents one shared identified bucket and missing identity uses the anonymous bucket.

Add safe runtime settings and monitoring inputs through the existing Terraform/deployment handoff. In particular, provide pre-verified Monitoring notification-channel resource identifiers to Terraform; do not pass destination secrets to the application.

Run infrastructure validation after provider initialization:

```bash
terraform -chdir=infrastructure/gcp fmt -check
terraform -chdir=infrastructure/gcp validate
```

## 5. Verify a non-production incident lifecycle

1. Deploy the reviewed revision through the supported hosted workflow with alerting enabled and a non-production verified notification channel.
2. Confirm exported monitoring policy identifiers, metric names, and service/environment labels match the target.
3. Use controlled non-production observations to cross the minimum sample and error/latency threshold.
4. Confirm exactly one incident opens with safe diagnostic context and the configured channel is bound.
5. Supply normal eligible observations for 15 consecutive minutes and confirm exactly one recovery/closure event is recorded.
6. Preserve deployment, policy, and verification records; do not capture credentials, request contents, caller identities, or destination secrets.

## 6. Roll back safely

If the hardening release causes an incident, first preserve the safe diagnostic and monitoring evidence. Roll back to the last verified application revision through the supported deployment workflow. Adjust or disable policy behavior only through approved configuration after confirming the impact; never perform broad shared-state deletion or expose cached content/identity data as a troubleshooting shortcut.
