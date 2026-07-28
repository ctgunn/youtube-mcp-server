# Data Model: YT-301 Layer 3 Shared Scaffolding and Contracts

## Layer 3 Tool Contract

Represents the public agreement for one higher-level YouTube MCP tool.

**Fields**:

- `toolName`: grouped public name, such as `videos_getVideo` or `transcripts_searchTranscript`
- `family`: owning family: `videos`, `channels`, `playlists`, or `transcripts`
- `description`: caller-facing summary of what the higher-level tool returns
- `parameters`: shared parameter conventions used by this tool
- `compositionBoundary`: declaration of direct retrieval, normalization, enrichment, filtering, ranking, composition, or fan-out behavior
- `responseFields`: response field provenance declarations
- `rankingAndFiltering`: reusable ranking or filtering rules that apply to this tool
- `heuristics`: heuristic or inferred field disclosures used by this tool
- `lowerLayerDependencies`: lower-level YouTube resources or Layer 2 contracts the tool may depend on
- `authAndQuotaNotes`: user-visible auth, quota, and composed-workflow caveats
- `partialResultPolicy`: behavior when one dependency or enrichment step is unavailable
- `errorCategories`: stable safe caller-facing failure categories
- `reviewEvidence`: examples and checks proving the contract follows YT-301

**Validation Rules**:

- `toolName` must use the owning family prefix and one of the grouped Layer 3 public catalog names.
- `family` must be one of the four Layer 3 public families.
- `parameters`, `compositionBoundary`, `responseFields`, and `errorCategories` are required.
- Heuristic or inferred fields require basis and limitation notes.
- Multi-resource or fan-out tools require auth, quota, bounded-result, and partial-result notes.
- Contracts must not imply concrete tool execution is delivered by YT-301.

**Relationships**:

- Belongs to one Tool Family.
- References zero or more Shared Parameter Conventions.
- Contains one Composition Boundary.
- Contains many Response Field Categories.
- May contain many Heuristic Disclosures and Ranking/Filtering Rules.
- May reference lower-layer contracts for upstream identity, auth, quota, and availability facts.

## Tool Family

Represents a cohesive Layer 3 public catalog group.

**Fields**:

- `familyName`: `videos`, `channels`, `playlists`, or `transcripts`
- `publicPrefix`: grouped public prefix such as `videos_*`
- `plannedTools`: public catalog names owned by the family
- `familyModule`: planned source area for family-specific contracts and helpers
- `testLocations`: contract, unit, and integration-style test locations
- `sharedHelpers`: family-owned reusable composition or normalization helper categories
- `familyCaveats`: caveats or exceptions that apply to the family

**Validation Rules**:

- Every initial Layer 3 tool must belong to exactly one family.
- Family guidance must identify where definitions, schemas, handlers, helpers, examples, and tests belong.
- Shared helpers must not force unrelated families into a single monolithic file.

**Relationships**:

- Owns many Layer 3 Tool Contracts.
- Uses shared Parameter Conventions, Ranking/Filtering Rules, and Response Field Categories.

## Shared Parameter Convention

Represents a reusable caller-facing parameter rule.

**Fields**:

- `name`: stable MCP-facing parameter name
- `valueKind`: expected user-facing value type or shape
- `requiredness`: required, optional, conditional, or family-specific
- `defaultBehavior`: default used when omitted
- `bounds`: minimum, maximum, or accepted value set where applicable
- `validationBehavior`: user-facing behavior for invalid, missing, reversed, or unsupported values
- `applicableFamilies`: families or tool types where the convention applies
- `upstreamMappingNotes`: mapping to lower-layer or upstream concepts where useful

**Validation Rules**:

- Repeated parameters must have one shared convention before later tool slices reuse them.
- `maxResults`, sample limits, transcript match limits, and fan-out settings require bounded behavior.
- Date filters must use ISO 8601 and define invalid or reversed-window behavior.
- Unsupported parameter combinations must produce deterministic safe validation errors.

**Relationships**:

- Referenced by Layer 3 Tool Contracts.
- May be scoped by Tool Family or workflow shape.

## Response Field Category

Represents the provenance of a result field.

**Fields**:

- `fieldName`: public result field name
- `category`: `raw_upstream`, `normalized`, or `heuristic_inferred`
- `source`: upstream, normalization, or inference source description
- `callerGuidance`: how callers should interpret the field
- `limitations`: caveats for missing, hidden, partial, or inferred values

**Validation Rules**:

- Every representative response field must have exactly one provenance category.
- Raw upstream fields must remain traceable to lower-layer data.
- Normalized fields must describe the normalization purpose.
- Heuristic or inferred fields must include basis and limitation notes.

**Relationships**:

- Belongs to one or more Layer 3 Tool Contracts.
- Heuristic categories link to a Heuristic Disclosure.

## Heuristic Disclosure

Represents a required disclosure for an inferred or approximate result.

**Fields**:

- `name`: heuristic field or signal name
- `basis`: signals or evidence used to infer the value
- `limitations`: uncertainty, false-positive, or missing-data risks
- `applicableTools`: tools or families that may expose the heuristic
- `safeUsageGuidance`: how clients should rely on the heuristic

**Validation Rules**:

- Heuristics must not be presented as raw upstream facts.
- Basis and limitations are required before the heuristic appears in a public contract.
- Sensitive private data, credentials, or owner-only context must not appear in heuristic examples.

**Relationships**:

- Used by Layer 3 Tool Contracts and Response Field Categories.
- May be used by Ranking/Filtering Rules.

## Ranking and Filtering Rule

Represents shared semantics for reusable filtering or ordering behavior.

**Fields**:

- `name`: public rule or parameter name, such as `creatorOnly` or `sortBy`
- `semantics`: caller-facing behavior
- `allowedValues`: accepted values where applicable
- `defaultBehavior`: behavior when omitted
- `applicableFamilies`: families or workflows where the rule applies
- `dependencyNotes`: lower-layer data needed to apply the rule
- `partialDataBehavior`: behavior when dependency data is missing

**Validation Rules**:

- Reused rules must be defined once and referenced by later tool contracts.
- Applicability must be explicit so unsupported tools do not silently accept a rule.
- Ranking based on heuristics must disclose the heuristic basis and limitations.

**Relationships**:

- Referenced by Layer 3 Tool Contracts.
- May depend on Response Field Categories and Heuristic Disclosures.

## Composition Boundary

Represents how much higher-level behavior a Layer 3 tool performs.

**Fields**:

- `kind`: direct retrieval, normalized retrieval, multi-resource composition, enrichment, server-side filtering, ranking, or fan-out
- `lowerLayerDependencies`: lower-layer resources or contracts involved
- `quotaBehavior`: how costs are exposed for single-call or composed workflows
- `authSensitivity`: whether OAuth or owner-authorized data may be required
- `partialResultPolicy`: whether partial data is returned, suppressed, or treated as an error
- `boundedness`: result, fan-out, or sample limits
- `callerCaveats`: user-visible caveats

**Validation Rules**:

- Composite and fan-out tools require quota, auth, partial-result, and boundedness notes.
- Direct retrieval tools must not claim ranking or heuristic enrichment unless represented as a different boundary kind.
- Boundary notes must be visible in public contracts before concrete tool implementation.

**Relationships**:

- Required by every Layer 3 Tool Contract.
- References lower-layer contracts and Shared Parameter Conventions.

## Family Scaffolding Contract

Represents maintainer-facing placement and dependency guidance.

**Fields**:

- `family`: owning Tool Family
- `definitionLocation`: planned location for public contract definitions
- `schemaLocation`: planned location for input schema declarations
- `handlerLocation`: planned location for concrete composed handlers in later slices
- `helperLocation`: planned location for reusable family helpers
- `exampleLocation`: planned location for representative examples
- `testLocations`: unit, contract, and integration-style test locations
- `exceptionNotes`: where family-specific caveats and deviations are recorded

**Validation Rules**:

- Every family must have a scaffolding contract.
- Shared cross-cutting rules must remain centralized; family modules should own only family-specific details.
- Later tool slices must be able to identify placement without redefining YT-301 rules.

**Relationships**:

- Belongs to one Tool Family.
- Guides later Layer 3 Tool Contracts and implementation tasks.

## Validation Evidence

Represents proof that a contract or convention satisfies YT-301.

**Fields**:

- `evidenceType`: contract example, unit check, integration-style check, documentation check, full-suite command, or lint command
- `target`: contract, convention, family, or representative tool shape being validated
- `expectedResult`: passing condition
- `command`: command when executable
- `notes`: review-facing assumptions or caveats

**Validation Rules**:

- Phase 2 tasks must start with failing evidence before implementation work.
- Final validation must include full `python3 -m pytest` and `python3 -m ruff check .`.
- Evidence must include docstring coverage expectations for every new or changed Python function.
