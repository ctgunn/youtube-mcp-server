# Data Model: Config + Secrets + Startup Validation (FND-004)

## Entity: RuntimeConfigProfile
Description: Named runtime environment profile that controls required settings and validation behavior.

Fields:
- `name` (string, required): One of `dev`, `staging`, `prod`.
- `description` (string, required): Human-readable purpose of the profile.
- `requiredConfigKeys` (array[string], required): Non-secret settings required for this profile.
- `requiredSecretKeys` (array[string], required): Secret-backed settings required for this profile.

Validation rules:
- `name` MUST be one of the supported profiles.
- `requiredConfigKeys` and `requiredSecretKeys` MUST be deterministic for each profile.

## Entity: ConfigRequirement
Description: Validation rule for a non-secret runtime setting.

Fields:
- `key` (string, required): Environment/config key identifier.
- `required` (boolean, required): Whether the setting must be present.
- `allowBlank` (boolean, required): Whether blank values are allowed.
- `allowedValues` (array[string], optional): Enumerated valid values where applicable.
- `formatHint` (string, optional): Validation hint for numeric/string formatting.

Validation rules:
- Required keys MUST be present and non-blank unless `allowBlank=true`.
- If `allowedValues` is provided, value MUST match one of them.
- Validation failures MUST identify the key and rule violated without exposing secret data.

## Entity: SecretRequirement
Description: Validation rule for a secret-backed runtime setting.

Fields:
- `key` (string, required): Secret key identifier.
- `required` (boolean, required): Whether the secret is mandatory for the selected profile.
- `injectionSource` (string, required): Expected injection path (deployment environment).
- `availabilityState` (string, required): `available` or `unavailable`.

Validation rules:
- Required secrets MUST be marked `available` before readiness can pass.
- Secret failures MUST never include raw secret values in error output.

## Entity: StartupValidationResult
Description: Aggregated startup validation outcome used to decide whether process boot continues.

Fields:
- `isValid` (boolean, required): Overall startup validation pass/fail.
- `profile` (string, required): Active runtime profile.
- `failedRequirements` (array[object], optional): Requirement failures with non-sensitive details.
- `timestamp` (string, required): Validation completion timestamp.

Validation rules:
- `isValid=false` MUST block startup completion.
- Each failed requirement MUST include key and rule violation reason.

## Entity: ReadinessState
Description: Readiness status derived from config and secret validation outcomes.

Fields:
- `status` (string, required): `ready` or `not_ready`.
- `reasonCode` (string, optional): Machine-readable non-sensitive reason when not ready.
- `checkedAt` (string, required): Timestamp of readiness evaluation.

Validation rules:
- `status=ready` only when all required config and secret checks pass.
- `status=not_ready` when any required validation fails or has not completed.

## Relationships

- `RuntimeConfigProfile` determines which `ConfigRequirement` and `SecretRequirement` sets apply.
- `ConfigRequirement` and `SecretRequirement` evaluations produce `StartupValidationResult`.
- `StartupValidationResult` feeds `ReadinessState` for readiness endpoint responses.

## State Transitions

- Process start -> load selected profile -> evaluate config requirements.
- Evaluate secret requirements -> compute startup validation result.
- If startup validation invalid -> fail startup and prevent traffic acceptance.
- If startup validation valid -> process becomes eligible for readiness.
- Readiness check -> return `ready` only when latest validation remains valid; otherwise `not_ready`.
