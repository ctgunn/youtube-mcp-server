# Data Model: Cloud-Agnostic Infrastructure Module Strategy

## Shared Platform Contract

- **Purpose**: Represents the provider-neutral infrastructure contract required to host the MCP service consistently across deployment targets.
- **Fields**:
  - `contract_name`: stable name for the shared platform model
  - `supported_execution_modes`: list of allowed execution modes
  - `required_capabilities`: ordered set of portable platform capabilities (`hosted_runtime`, `network_ingress`, `runtime_identity`, `secret_backed_configuration`, `observability_integration`, `durable_session_support`)
  - `deployment_model`: shared application deployment expectations that provider adapters must preserve
  - `portability_rules`: rules describing what may vary by provider and what must remain consistent
  - `status`: `draft`, `reviewed`, `approved`, or `superseded`
- **Validation Rules**:
  - Must define hosted runtime, networking and ingress, runtime identity, secret-backed configuration, observability integration, and durable session support.
  - Must distinguish mandatory capabilities from optional provider-specific enhancements.
  - Must preserve a minimum local execution mode that does not require provider adapters.
- **Relationships**:
  - Owns one or more `Platform Capabilities`.
  - Is implemented by one or more `Provider Adapter Modules`.
  - Applies to one or more `Execution Modes`.

## Platform Capability

- **Purpose**: Represents one portable requirement the hosted platform must satisfy regardless of cloud provider.
- **Fields**:
  - `capability_name`: portable capability identifier
  - `category`: `runtime`, `networking`, `identity`, `secret_management`, `observability`, or `session_durability`
  - `required_inputs`: operator-supplied or environment-specific values needed to satisfy the capability
  - `expected_outputs`: values or guarantees produced when the capability is satisfied
  - `operational_guarantees`: expected behavior visible to operators and maintainers
  - `optional_enhancements`: provider-specific features that are useful but not portable requirements
  - `status`: `defined`, `mapped`, `partially_supported`, or `unsupported`
- **Validation Rules**:
  - Every required capability must have at least one provider mapping for the primary hosted provider.
  - Optional enhancements must not be described as baseline portability requirements.
  - Capability outputs must be sufficient to support the shared application deployment model.
- **Relationships**:
  - Belongs to one `Shared Platform Contract`.
  - Is referenced by one or more `Capability Mappings`.

## Provider Adapter Module

- **Purpose**: Represents one provider-specific implementation or planning path that maps provider behavior to the shared platform contract.
- **Fields**:
  - `provider`: provider identifier such as `gcp` or `aws`
  - `adapter_scope`: `complete`, `scaffolded`, or `planned`
  - `supported_capabilities`: capabilities the adapter satisfies fully
  - `partial_capabilities`: capabilities with gaps or constraints
  - `provider_specific_inputs`: provider-only inputs required by the adapter
  - `provider_specific_outputs`: outputs exposed by the adapter for deployment and operations
  - `limitations`: known gaps, constraints, or unsupported features
  - `status`: `draft`, `mapped`, `validated`, or `deferred`
- **Validation Rules**:
  - Must map back to the `Shared Platform Contract` rather than define an independent platform model.
  - Must separate portable guarantees from provider-specific implementation details.
  - Must declare limitations before the adapter is treated as production-ready.
- **Relationships**:
  - Implements one `Shared Platform Contract`.
  - Owns one or more `Capability Mappings`.
  - Supports one or more `Execution Modes` for hosted use.

Known planning examples:

- `gcp`: first complete provider adapter for the current hosted deployment path
- `aws`: planning-grade provider adapter used to prove portability beyond the primary cloud target

## Capability Mapping

- **Purpose**: Documents how one provider adapter satisfies, partially satisfies, or cannot satisfy a shared platform capability.
- **Fields**:
  - `provider`
  - `capability_name`
  - `mapping_type`: `full`, `partial`, or `unsupported`
  - `provider_constructs`: provider-specific resources or concepts used to satisfy the capability
  - `operator_visible_effects`: the outcomes or caveats an operator must understand
  - `escalation_guidance`: what must happen if the capability is only partially supported
  - `status`: `draft`, `reviewed`, or `accepted`
- **Validation Rules**:
  - Must preserve the portable capability intent even when provider constructs differ.
  - Partial mappings must include explicit caveats and must not be misrepresented as complete support.
  - Unsupported mappings must identify whether the adapter is blocked, deferred, or unsuitable for production.
- **Relationships**:
  - Belongs to one `Provider Adapter Module`.
  - References one `Platform Capability`.

## Execution Mode

- **Purpose**: Represents one documented way of running or validating the MCP service against the shared platform contract.
- **Fields**:
  - `mode_name`: `minimal_local`, `hosted_like_local`, or `hosted`
  - `required_prerequisites`: tools, dependencies, and inputs needed for the mode
  - `capability_subset`: which shared capabilities the mode exercises
  - `provider_dependency`: `none`, `local`, or a named provider adapter
  - `expected_evidence`: signals or artifacts that prove the mode is working
  - `status`: `defined`, `documented`, `verified`, or `outdated`
- **Validation Rules**:
  - `minimal_local` must have `provider_dependency=none`.
  - `hosted_like_local` may exercise durable-session behavior but must remain distinct from hosted cloud deployment.
  - `hosted` must declare which provider adapter supplies its hosted capabilities.
- **Relationships**:
  - Belongs to one `Shared Platform Contract`.
  - May depend on one `Provider Adapter Module`.

## State Transitions

- **Shared Platform Contract**: `draft -> reviewed -> approved|superseded`
- **Platform Capability**: `defined -> mapped -> partially_supported|unsupported`
- **Provider Adapter Module**: `draft -> mapped -> validated|deferred`
- **Capability Mapping**: `draft -> reviewed -> accepted`
- **Execution Mode**: `defined -> documented -> verified|outdated`
