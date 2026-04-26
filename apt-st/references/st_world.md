 # ST World Extended Reference

> APT v13 SemanticTwin phase — detailed examples, patterns, and schemas.
> Companion to `/apt-st/SKILL.md`.

---

## 1. Contract Example: CT_UserProfile_Create (Full)

**Task (TASK_UserProfile_Create):**

```yaml
description: "Create a new user profile from registration form data. Validate email
  format, hash password, generate unique user ID, and persist to database.
  Handle duplicate email and invalid input gracefully."
acceptance_criteria:
  - "Returns UserProfile with generated UUID"
  - "Password is hashed (bcrypt)"
  - "Email validated with RFC 5322 regex"
  - "Duplicate email raises ConflictError"
  - "p99 latency < 200ms"
  - "Peak memory < 128MB"
impact_tests:
  - "tests/test_user_profile.py::test_create_returns_uuid"
  - "tests/test_user_profile.py::test_password_hashed"
  - "tests/test_user_profile.py::test_email_validation"
  - "tests/test_user_profile.py::test_duplicate_email"
  - "tests/test_user_profile.py::test_latency_p99"
  - "tests/test_user_profile.py::test_memory_peak"
target_file: "src/auth/user_profile.py"
estimated_lines: 85
```

**Contract (CT_UserProfile_Create):**

```yaml
input_type:    "RegistrationForm{name:str, email:str, password:str}"
output_type:   "UserProfile{id:str, name:str, email:str, created_at:datetime}"
precondition:  "form is not None and len(form.email) > 0 and len(form.password) >= 8
                and '@' in form.email"
postcondition: "result.id is not None and len(result.id) == 36
                and result.email == form.email and result.created_at is not None"
semantic_meaning: "User registration. ID is UUID v4. Password stored as bcrypt hash,
  never in plaintext. Email must be unique across all users."
target_file: "src/auth/user_profile.py"
status: "active"
nfr_latency_p99_ms: 200
nfr_memory_mb: 128
nfr_accuracy: null
nfr_hw: null
nfr_env_dev:  '{"mock": true, "latency_p99_ms": null, "use_in_memory_db": true}'
nfr_env_prod: '{"mock": false, "latency_p99_ms": 200, "db": "postgresql"}'
```

**Cypher:**

```cypher
MERGE (ct:AptContract {name: 'CT_UserProfile_Create'})
SET ct.input_type      = 'RegistrationForm{name:str, email:str, password:str}',
    ct.output_type     = 'UserProfile{id:str, name:str, email:str, created_at:datetime}',
    ct.precondition    = 'form is not None and len(form.email) > 0 and len(form.password) >= 8',
    ct.postcondition   = 'result.id is not None and len(result.id) == 36 and result.email == form.email',
    ct.semantic_meaning = 'User registration, UUID v4 ID, bcrypt password hash, unique email',
    ct.target_file     = 'src/auth/user_profile.py',
    ct.status          = 'active',
    ct.nfr_latency_p99_ms = 200,
    ct.nfr_memory_mb   = 128,
    ct.nfr_env_dev     = '{"mock": true, "latency_p99_ms": null}',
    ct.nfr_env_prod    = '{"mock": false, "latency_p99_ms": 200}',
    ct.created_at      = datetime()
```

---

## 2. Contract Example: CT_SearchIndex_Build

**Task:**

```yaml
description: "Build search index from product catalog. Bulk insert products into
  search engine with proper field mapping, tokenization, and error handling.
  Handle partial failures gracefully."
acceptance_criteria:
  - "Returns IndexResult with counts"
  - "indexed_count + failed_count == input length"
  - "Handles empty product list (raises ValueError)"
  - "Handles missing required fields"
  - "< 5000ms for 1000 products"
  - "Peak memory < 1024MB"
impact_tests:
  - "tests/test_indexer.py::test_bulk_index"
  - "tests/test_indexer.py::test_partial_failure"
  - "tests/test_indexer.py::test_empty_input"
  - "tests/test_indexer.py::test_missing_fields"
  - "tests/test_indexer.py::test_latency"
  - "tests/test_indexer.py::test_memory"
target_file: "src/search/indexer.py"
estimated_lines: 180
```

**Contract:**

```yaml
input_type:    "products: list[Product{id:str, title:str, description:str, price:float, category:str}]"
output_type:   "IndexResult{indexed_count:int, failed_count:int, errors:list[str]}"
precondition:  "len(products) > 0 and all(p.id and p.title for p in products)"
postcondition: "result.indexed_count + result.failed_count == len(products)
                and result.indexed_count > 0"
semantic_meaning: "Bulk product indexing for search. Products with missing required fields
  go to errors list. Partial success is acceptable."
nfr_latency_p99_ms: 5000
nfr_memory_mb: 1024
nfr_accuracy: null
```

**SEQUENCED_WITH (Index -> Search):**

```cypher
MATCH (k1:AptContract {name: 'CT_SearchIndex_Build'})
MATCH (k2:AptContract {name: 'CT_ECommerce_ElasticSearch'})
MERGE (k1)-[:SEQUENCED_WITH {
  entailment: 'k1.postcondition(indexed_count > 0) entails k2.precondition(index exists)',
  condition: null,
  verified_at: datetime()
}]->(k2)
```

---

## 3. Contract Example: CT_HelloAPT_ParseArgs

**Task:**

```yaml
description: "Parse --name (required, str) and --count (optional, int, default 1).
  Print greeting --count times. Raise UsageError for missing --name."
acceptance_criteria:
  - "--name Alice returns name='Alice'"
  - "--count 3 returns count=3"
  - "missing --name raises UsageError"
  - "--count -1 raises ValueError"
impact_tests:
  - "tests/test_parse_args.py::test_name_flag"
  - "tests/test_parse_args.py::test_count_flag"
  - "tests/test_parse_args.py::test_missing_name"
  - "tests/test_parse_args.py::test_count_negative"
target_file: "src/hello_apt/parse_args.py"
estimated_lines: 45
```

**Contract:**

```yaml
input_type:    "list[str] — sys.argv[1:]"
output_type:   "ParsedArgs{name: str, count: int}"
precondition:  "len(argv) >= 2 and '--name' in argv"
postcondition: "result.name is not None and len(result.name)>0 and result.count>=0"
semantic_meaning: "CLI parsing for greeting. name=person to greet. count=repetition
  (non-negative int, default 1). GNU-style long options."
nfr_latency_p99_ms: null
nfr_memory_mb: null
nfr_accuracy: null
nfr_hw: null
```

**tau_check walkthrough:**

| # | Check | Value | Pass? |
|:-:|-------|-------|:-----:|
| 1 | input concrete? | `list[str]` | YES |
| 2 | output concrete? | `ParsedArgs{name:str, count:int}` | YES |
| 3 | precondition boolean? | `len(argv)>=2 and '--name' in argv` | YES |
| 4 | postcondition verifiable? | `result.name is not None and ...` | YES |
| 5 | semantic meaning? | "CLI parsing... GNU-style long options" | YES |

---

## 4. NFR Environment Variant Examples

### 4.1 Database Access — Three Environments

| Field | Dev | Staging | Prod |
|-------|-----|---------|------|
| `nfr_env_dev` | `{"mock": true, "latency_p99_ms": null, "adapter": "MockDBAdapter"}` | — | — |
| `nfr_env_staging` | — | `{"mock": false, "latency_p99_ms": 100, "adapter": "PostgresAdapter"}` | — |
| `nfr_env_prod` | — | — | `{"mock": false, "latency_p99_ms": 50, "pool_size": 20}` |

**Environment selection:**

```python
env = config.nfr.execution_env   # "dev" | "staging" | "prod"
nfr = json.loads(contract[f"nfr_env_{env}"])
adapter = MockDBAdapter() if nfr.get("mock") else PostgresAdapter(pool_size=nfr.get("pool_size", 10))
```

### 4.2 Search Quality — Performance Drift

```yaml
Contract: CT_ECommerce_Search
nfr_accuracy: "nDCG@10 > 0.7"
nfr_env_dev:  '{"test_dataset": "fixtures/search_100.json", "nDCG_threshold": 0.6}'
nfr_env_prod: '{"test_dataset": "/data/search_10k.json", "nDCG_threshold": 0.7,
                "drift_check_interval_hours": 24}'
```

In prod, scheduled nDCG eval every 24h. If below 0.7: `ContractAmended` with reason `performance_drift`.

### 4.3 API Gateway — Latency-Critical

```yaml
Contract: CT_APIGateway_RouteRequest
nfr_latency_p99_ms: 50
nfr_hw: "load_balancer"
nfr_env_dev:  '{"mock": true, "latency_p99_ms": null, "mode": "local"}'
nfr_env_prod: '{"mock": false, "latency_p99_ms": 50, "lb": "nginx", "workers": 8}'
```

Dev relaxes latency. Prod hard-enforces 50ms p99. Load testing required before deploy.

---

## 5. Hardware Context Layer

### 5.1 HardwareContext Node Schema

| Property | Type | Required | Description |
|----------|------|:--------:|-------------|
| `name` | string | Yes | `HW_{manufacturer}_{model_short}` |
| `type` | string | Yes | `camera`, `gpu`, `sensor`, `actuator`, `network` |
| `manufacturer` | string | No | `NVIDIA`, `Intel`, `AWS` |
| `model` | string | Yes | `NVIDIA A100 80GB`, `Intel Xeon 8380` |
| `constraints` | string | No | Known limitations |
| `sdk_version` | string | No | Required SDK/driver version |
| `interface` | string | No | `USB3`, `GigE`, `PCIe`, `EtherCAT` |
| `created_at` | datetime | Yes | Creation timestamp |

### 5.2 HardwareContext Examples

**GPU Server (ML Ranking):**

**NVIDIA GPU:**

```cypher
MERGE (hw:HardwareContext {name: 'HW_NVIDIA_A100'})
SET hw.type = 'gpu', hw.manufacturer = 'NVIDIA',
    hw.model = 'NVIDIA A100 80GB SXM',
    hw.constraints = 'CUDA 12.0+ required. TDP 400W.',
    hw.sdk_version = 'CUDA 12.0, cuDNN 8.9, TensorRT 8.6',
    hw.interface = 'PCIe Gen4 x16', hw.created_at = datetime()
```

**Robot Arm:**

```cypher
MERGE (hw:HardwareContext {name: 'HW_UR10e'})
SET hw.type = 'actuator', hw.manufacturer = 'Universal Robots',
    hw.model = 'UR10e',
    hw.constraints = 'Payload max 12.5kg. Reach 1300mm. RTDE 125Hz.',
    hw.sdk_version = 'ur_rtde 1.5+', hw.interface = 'EtherCAT',
    hw.created_at = datetime()
```

### 5.3 REQUIRES_HARDWARE Patterns

```cypher
// Mandatory (no fallback)
MATCH (ct:AptContract {name: 'CT_Payment_Process'})
MATCH (hw:HardwareContext {name: 'HW_HSM_Thales'})
MERGE (ct)-[:REQUIRES_HARDWARE {criticality:'mandatory', note:'Encryption keys stored in HSM'}]->(hw)

// Multiple hardware dependencies
MATCH (ct:AptContract {name: 'CT_MLPipeline_Train'})
MATCH (hw_gpu:HardwareContext {name: 'HW_NVIDIA_A100'})
MATCH (hw_storage:HardwareContext {name: 'HW_NFS_Storage'})
MERGE (ct)-[:REQUIRES_HARDWARE {criticality:'mandatory', note:'GPU for training'}]->(hw_gpu)
MERGE (ct)-[:REQUIRES_HARDWARE {criticality:'mandatory', note:'NFS for dataset'}]->(hw_storage)

// Optional (GPU accelerates, CPU fallback exists)
MATCH (ct:AptContract {name: 'CT_Search_MLRanking'})
MATCH (hw:HardwareContext {name: 'HW_NVIDIA_A100'})
MERGE (ct)-[:REQUIRES_HARDWARE {criticality:'optional', note:'GPU 10x speedup, CPU fallback'}]->(hw)

// Test-only (production DB for integration tests only)
MATCH (ct:AptContract {name: 'CT_UserProfile_Create'})
MATCH (hw:HardwareContext {name: 'HW_PostgreSQL_Cluster'})
MERGE (ct)-[:REQUIRES_HARDWARE {criticality:'test_only', note:'Unit tests use in-memory DB'}]->(hw)
```

### 5.4 Ports-and-Adapters Mock Strategy

```
+------------------------------------+
| Contract: CT_UserProfile_Create    |
|  +-------------+                   |
|  | DBPort      | <-- abstract      |
|  +------+------+                   |
|    +----+-----+                    |
|    |          |                    |
|  PostgresAdapter  InMemoryAdapter  |
|  (prod)           (dev/test)       |
+------------------------------------+
```

**Rules:**
1. Hardware SDK calls live in Adapter implementing Port interface
2. Business logic depends only on Port, never Adapter directly
3. Dev: MockAdapter returns synthetic data matching Port types
4. Prod: Real Adapter injected, NFR assertions enforced
5. Integration tests use real Adapter. Unit tests use Mock.

**When NOT to mock:** hardware behavior IS the logic (calibration accuracy),
timing-sensitive (real-time control loops, jitter). Use HIL testing.

---

## 6. SEQUENCED_WITH Composition Detail

### 6.1 Hoare Triple Chaining

```
{P1} f1: A->B {Q1},  {P2} f2: B->C {Q2},  Q1 entails P2
=> {P1} f2.f1: A->C {Q2}
```

**Entailment (3 conditions, ALL required):**
1. Type compatibility: `k1.output_type` matches `k2.input_type`
2. Postcondition coverage: `k1.postcondition` implies `k2.precondition`
3. Integration test: run k1->k2 in sequence, verify k2's postcondition

### 6.2 Non-Linear Patterns

**Branching (OK/NG):**
```
k1 --{condition: 'output.status==OK'}--> k2_ok
k1 --{condition: 'output.status==NG'}--> k2_ng
```
Both branches MUST be reachable. Postcondition must include status field.

**Parallel (Fan-out/Fan-in):**
```
k1 --> k2a --+--> k3 (join, input = product type)
k1 --> k2b --+
```

**Feedback Loop:**
```
k1 --> k2 --{converged}--> k3
       k2 --{!converged}--> k1   // MUST have termination guarantee
```

### 6.3 NOT Categorical Composition

| Property | Category Theory | APT |
|----------|----------------|-----|
| Identity | Required | Not required |
| Associativity | Proven | Not proven |
| Verification | Type-level proof | Runtime test + manual entailment |

Practical pipeline verification, not abstract algebra.

### 6.4 Pipeline Examples

**Linear: E-Commerce Order Pipeline**

```
CT_ValidateCart {CartItems -> ValidatedCart}
  |  SEQUENCED_WITH
CT_ProcessPayment {ValidatedCart -> PaymentResult}
  |  SEQUENCED_WITH
CT_CreateOrder {PaymentResult -> Order}
```

**Branching: Payment Check**

```
CT_ProcessPayment {output: PaymentResult}
  +-- {status == 'approved'} --> CT_CreateOrder (OK)
  +-- {status == 'declined'} --> CT_NotifyUser (NG)
```

**Parallel: Data Enrichment**

```
CT_FetchUserProfile {-> UserProfile}     --+
                                             +--> CT_PersonalizeResults {(profile, history) -> Recommendations}
CT_FetchOrderHistory {-> list[Order]}    --+
```

**Feedback: Retry Pattern**

```
CT_SendEmail
  +-- {delivered or attempts>=3} --> CT_LogResult
  +-- {failed and attempts<3} --> CT_SendEmail (retry, max 3 attempts)
```

---

## 7. Contract Sandwich

Multiple Twins MAY share one Contract when they implement the same interface.

**Use when:** same adapter across modules, shared utility, identical typed spec.
**NOT when:** different pre/postconditions, different NFR, different semantic_meaning.

```cypher
MATCH (ct:AptContract {name: $shared_contract})
MATCH (twin1:SemanticTwin {name: $twin1}), (twin2:SemanticTwin {name: $twin2})
MERGE (twin1)-[:HAS_CONTRACT]->(ct)
MERGE (twin2)-[:HAS_CONTRACT]->(ct)
```

Relaxes HAS_CONTRACT from 1:1 to N:1. Document reason in hub notes.

---

## 8. Failure Pattern Detection

| Pattern | Signal | Fix |
|---------|--------|-----|
| **Over-ambition** | estimated_lines > 500 | Return to /apt-sp for decomposition |
| **Over-ambition** | "and also" in description | One Contract = one concern |
| **False completion** | postcondition is prose | Rewrite as testable boolean |
| **False completion** | GREEN without RED | Delete tests, confirm RED, re-implement |
| **Testing gap** | impact_tests empty | Block: every Task needs test paths |
| **Testing gap** | NFR set but no perf tests | Add latency/memory/accuracy assertions |
| **Testing gap** | Only happy-path | Add boundary, null, overflow tests |

---

## 9. Contract Lifecycle FSM — Detail

### 9.1 Full State Diagram

```
+--------+  all fields  +--------+  FulfillGate  +-----------+  +----------+
| Draft  |------------->| Active |-------------->| Fulfilled |->| Archived |
+---+----+              +---+----+               +-----+-----+  +----------+
    |                       |    +---------+           |
    | design wrong          |<---| Amended |<----------+ regression/discovery
    v                       |    +----+----+
+----------+                +---------+  re-activation
| Rejected |
+----------+
```

### 9.2 Transition Table

| From | To | Trigger | Kafka Event |
|------|----|---------|-------------|
| Draft | Active | 7 fields populated + review | `ContractActivated` |
| Draft | Rejected | Design invalidated | `ContractRejected` |
| Active | Fulfilled | FulfillmentGate pass | `ContractMaterialized` |
| Active | Amended | Discovery during impl | `ContractAmended` |
| Fulfilled | Archived | Project complete | `ContractArchived` |
| **Fulfilled** | **Amended** | **Regression / new req** | **`ContractAmended`** |
| Amended | Active | Amendment reviewed | `ContractActivated` |
| Amended | Rejected | Fundamental design flaw | `ContractRejected` |

### 9.3 Fulfilled->Amended Triggers

- Regression detected in downstream Contract
- New FULFILLS_REQUIREMENT edge added
- Accuracy drift below threshold
- Hardware firmware/SDK change

### 9.4 Kafka Flow

detect -> `ContractAmended` -> SET status='Amended' -> find affected SourceCodeNodes
-> regression tests -> work item in queue.

### 9.5 Invariants

- One state at a time. Null = violation.
- Rejected/Archived = terminal.
- Draft->Fulfilled FORBIDDEN (must pass through Active).
- Every transition = Kafka event.

---

## 10. Amendment Scenarios

### 10.1 Regression from Downstream

```
T1: CT_UserProfile fulfilled
T2: CT_UserAuth amended (token format changed)
T3: Integration test fails
T4: CT_UserProfile -> Amended
Kafka: {event: "ContractAmended", contract: "CT_UserProfile_Create",
        reason: "regression_from_CT_UserAuth_Login_v2"}
```

### 10.2 New Requirement

```
T1: CT_ParseArgs fulfilled
T2: New req: "support --verbose flag"
T3: FULFILLS_REQUIREMENT edge added
T4: CT_ParseArgs -> Amended (add acceptance criteria + postcondition field)
```

### 10.3 Hardware Firmware Update

```
T1: CT_Search_ElasticSearch fulfilled (ES 8.10)
T2: ES 8.11 changes query DSL for nested fields
T3: HW_ElasticSearch_Cluster.sdk_version updated
T4: CT_Search_ElasticSearch -> Amended (update precondition for new API)
```

---

## 11. tau_check Extended: Before/After Fix

### Before (5/5 FAIL):

```
input_type:       "data"                  // abstract
output_type:      "result"                // abstract
precondition:     "valid input"           // prose
postcondition:    "works correctly"       // not verifiable
semantic_meaning: "processes stuff"       // no domain context
```

### After (5/5 PASS):

```
input_type:       "DataFrame{columns:['x','y','z'], dtypes:float64}"
output_type:      "ClusterResult{labels:ndarray int32[N], centroids:ndarray float64[K,3]}"
precondition:     "len(df)>0 and set(['x','y','z']).issubset(df.columns)"
postcondition:    "len(result.labels)==len(input) and result.centroids.shape[1]==3"
semantic_meaning: "K-means clustering of 3D points in mm, ROBOT_BASE frame.
  Labels 0..K-1, centroids in same frame."
```

---

## 12. CrystallizationEvent Hub — Extended

### 12.1 Hub-and-Spoke Diagram

```
                    +------------------------+
                    |  CrystallizationEvent   |
                    |  name: CE_Q1_Transfer   |
                    +----------+--------------+
                               |
        +----------+-----------+-----------+----------+
   INVOLVES{  INVOLVES{   INVOLVES{   INVOLVES{  INVOLVES{
    'atom'}    'twin'}     'task'}   'contract'}  'source'}
        |          |           |           |          |
        v          v           v           v          v
   AtomicSpan  Semantic   Semantic    AptContract SourceCode
               Twin       Task                    Node (PH5)
```

### 12.2 Validation Queries

```cypher
// V14: Hub must have at least atom role
MATCH (cx:CrystallizationEvent)
WHERE NOT (cx)-[:INVOLVES {role: 'atom'}]->()
RETURN 'V14_HUB_INCOMPLETE', cx.name

// Extended: Hub should have all 4 roles (before PH5)
MATCH (cx:CrystallizationEvent)
WHERE NOT (cx)-[:INVOLVES {role: 'atom'}]->()
   OR NOT (cx)-[:INVOLVES {role: 'twin'}]->()
   OR NOT (cx)-[:INVOLVES {role: 'task'}]->()
   OR NOT (cx)-[:INVOLVES {role: 'contract'}]->()
RETURN 'V14_HUB_MISSING_ROLE', cx.name

// Consistency: Every CRYSTALLIZES_TO must have a hub
MATCH (a:AtomicSpan)-[:CRYSTALLIZES_TO]->(t:SemanticTwin)
WHERE NOT EXISTS {
  MATCH (cx:CrystallizationEvent)-[:INVOLVES {role: 'atom'}]->(a)
  WHERE (cx)-[:INVOLVES {role: 'twin'}]->(t)
}
RETURN 'CONSISTENCY_VIOLATION', a.name, t.name
```

---

## 13. Boundary Mold (/apt-st) Detail

### 13.1 Role

**Specification authority.** Takes approved AtomicSpans, crystallizes into SemanticTwins
(Contract + Task). Where "soft meaning" hardens into "hard specification."

### 13.2 Tools

| Tool | Purpose |
|------|---------|
| Contract Registry | Create, amend, version AptContracts |
| Twin Registry | Manage lifecycle: draft->crystallized->implemented->validated->stale->broken |
| Hub Manager | Create/validate CrystallizationEvent hubs |
| NFR Configurator | Set environment-specific nfr_* properties |

### 13.3 Boundary Decides / Does NOT Decide

**Decides:** typed interface, pre/postconditions, NFR constraints, composition topology, hardware reqs.

**Does NOT decide:** how to implement (Execution), whether decomposition correct (Intent),
approval/rejection (Governance).

### 13.4 Feedback Into Boundary

Assurance can send: `contract_gap`, `type_mismatch`, `edge_case`, `nfr_violation`.
On feedback: publish `ContractAmended` -> update fields -> re-run tau_check -> re-activate.

### 13.5 The 6 Architectural Molds

| # | Mold | Command | Role |
|---|------|---------|------|
| 1 | Governance | `/apt` | Oversight: approvals, gates, config |
| 2 | Intent | `/apt-sp` | Planning: decompose, explore, link |
| 3 | **Boundary** | **`/apt-st`** | **Specification: crystallize, compose, specify** |
| 4 | Execution | `/apt-scw` | Building: TDD implement, lock/unlock |
| 5 | Assurance | `/apt-scw` | Quality: verify, fulfill, feedback |
| 6 | Memory | cross-cuts | Knowledge: tiers, context, reflection |

---

*End of ST World Extended Reference.*
