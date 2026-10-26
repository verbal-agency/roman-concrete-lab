# G10R-Z — Repair acquisition headroom and society validity offline

**Status:** complete — `ACQUISITION_HEADROOM_READY`
**Dependencies:** G10R-Y complete with `POST_V_DIAGNOSIS_READY` and its
diagnosis, ablation, replay, and criterion-ledger artifacts
**Authority:** repository-local code, recorded fixtures, and deterministic
subprocess tests only; no model, network, credential, subscription,
laboratory, external communication, Phase-A freeze, or paid execution

## Objective

Repair and prove the acquisition/headroom and society-validity contracts in an
offline, provider-neutral path so a later goal can wire them into the
live-capable runner without invalidating frozen G10R-X inputs. Both A1 and A2-M
must resolve a discovered metadata record to an exact policy-permitted
public-content route, while the open viewpoint is proposed only after sharing,
support work is created from unresolved needs, and metadata-only contributions
remain useful discovery candidates without earning source-backed credit. Prove
the repairs with an arm-neutral offline headroom matrix before any new freeze
is eligible.

## Project outcomes advanced

- turns lawful discovery into page-located evidence when public content exists;
- preserves lateral candidates and contradictory hypotheses without promoting
  them automatically;
- makes society value separable from source-access headroom and coordination
  overhead; and
- preserves the reusable evidence, provenance, hypothesis, focus, replay, and
  authority contracts of the exploratory platform.

## Architecture constraints

- The product remains a reusable substrate loaded with a versioned
  Roman-concrete problem context; no Roman-specific rule enters the core
  retrieval or society contracts.
- Candidate, evidence, hypothesis, and authority states remain separate.
- A1 and A2-M use the same locator service, source policy, schemas, ceilings,
  stopping rules, and failure semantics.
- Unresolved or contradictory sources remain visible for collective review;
  only proven fabrication or an illegal authority transition fails closed.
- Source documents remain untrusted data and cannot execute instructions.

## In scope

- a typed, arm-neutral metadata-to-public-locator resolution transition;
- a deterministic preflight proving that positive evaluation fixtures contain
  reachable content headroom without exposing hidden answers to either arm;
- delayed, evidence-conditioned open-viewpoint proposal and admission;
- need-driven structural support scheduling instead of the unconditional
  viewpoint × task Cartesian product;
- aligned deterministic/live completion and contribution scoring;
- negative, contradictory, malformed, partial, budget, unsupported, and replay
  fixtures; and
- an offline A1/A2-M comparison under identical declared ceilings.

## Explicit exclusions

- live scholarly lookup, model calls, credentials, subscriptions, or spending;
- widening the G10R-X host allowlist or changing rights classifications;
- tuning prompts or rubrics to the four G10R-V sealed outputs;
- deleting unresolved candidates because they lack a current card;
- treating fixture success as real-model society value;
- evidence promotion, scientific validation, laboratory contact, or physical
  execution; and
- creating or activating another Phase-A freeze.

## Execution contract

### Expected implementation surface

- `src/roman_concrete_lab/agents/investigation.py` for shared locator
  resolution and live A1/A2-M transitions;
- `src/roman_concrete_lab/agents/research_loop.py` for deterministic parity and
  metadata-only behavior;
- `src/roman_concrete_lab/agents/viewpoint_society.py` for delayed admission and
  need-driven support work;
- `src/roman_concrete_lab/retrieval/` only if a provider-neutral locator
  interface is required;
- `schemas/public-locator-resolution.schema.json` and
  `schemas/evaluation-headroom.schema.json`, or explicitly mapped equivalents;
- recorded fixtures under `fixtures/investigation/g10r-z/`;
- `tools/evaluation/acquisition_headroom_repair.py`;
- `tests/agents/test_g10r_z_acquisition_headroom.py` and focused existing
  research-loop/wiring tests;
- `docs/protocols/g10r-z-acquisition-headroom.md`, which records the additive
  repair protocol without mutating frozen G10R-X inputs; and
- `artifacts/goals/G10R-Z/{headroom-matrix.json,run.json,replay.json,criterion-ledger.json,report.md}`.

Equivalent paths are allowed only when the report maps them to this contract.

### Canonical records and invariants

`PublicLocatorResolution` has schema version `1.0` and contains
`resolution_id`, case/problem/version, arm-neutral need ID, candidate ID,
discovery action IDs, original locator, candidate route records, selected
exact HTTPS content locator, source-policy hash, policy decision, status,
failure reason, and provenance. Legal statuses are `RESOLVED_PUBLIC`,
`METADATA_ONLY`, `RIGHTS_BLOCKED`, `NOT_FOUND`, and `INVALID`. A resolution may
select only a recorded exact route; it may never infer a URL from prose, title,
or DOI shape.

`EvaluationHeadroom` has schema version `1.0` and contains case family,
fixture hash, expected discovery IDs, public-content opportunity IDs, policy
hash, hidden-answer isolation proof, arm-neutrality proof, and one status:
`READY`, `NO_PUBLIC_CONTENT`, or `INVALID_FIXTURE`. A positive evaluation case
cannot be `READY` without at least one recorded candidate → public locator →
fetch → page-card path.

`OpenViewpointAdmission` remains post-sharing and adds a typed `basis_kind`:
`CANDIDATE_PENDING`, `PAPER_CARD`, or `TYPED_DISCRIMINATOR`. Candidate-pending
admission may earn discovery/hypothesis credit and receive bounded later work,
but never evidence or unique source-backed credit. `ABSTAINED` or
`REJECTED_REDUNDANT` creates no active viewpoint, support tasks, model-call
slot, dossier, or focus allocation.

Support work originates from a `ResearchNeed`. A report may be `COMPLETE` only
when it binds an observable action, mapped card, identity adjudication, or typed
discriminator. Generic status prose and role instantiation receive no credit.
Source-backed contribution requires an action → candidate → policy-permitted
content/card or eligible typed adapter output → claim → current dossier → final
portfolio chain. Candidate and hypothesis ledgers retain uncredited records.

Illegal cross-case writes, unrecorded locators, policy-hash drift, stale
manifests, conflicting duplicate IDs, backward state transitions, post-terminal
mutation, or evidence promotion fail closed. Rights-blocked and metadata-only
records remain typed nonfatal outcomes.

### Legal transitions, cache, and invalidation

- `PublicLocatorResolution`: `CREATED` transitions exactly once to
  `RESOLVED_PUBLIC`, `METADATA_ONLY`, `RIGHTS_BLOCKED`, `NOT_FOUND`, or
  `INVALID`; each result is terminal and immutable.
- `EvaluationHeadroom`: `CREATED` transitions exactly once to `READY`,
  `NO_PUBLIC_CONTENT`, or `INVALID_FIXTURE`; each result is terminal.
- Open viewpoint: `PROPOSED` may transition after sharing to `ADMITTED`,
  `REJECTED_REDUNDANT`, or `ABSTAINED_NO_DISTINCT_VIEWPOINT`; no transition
  creates evidence authority.
- Goal execution: `in progress` transitions to exactly one declared terminal
  verdict after the criterion ledger is complete.
- Resolution replay keys contain policy hash, candidate ID, candidate-record
  hash, route-record hash, and operation. Identical keys replay without work;
  a changed policy, fixture, candidate, schema, or route hash invalidates the
  cache and requires a new manifest namespace. Conflicting duplicate payloads
  and stale checkpoints fail closed.
- Budget is debited only for an executed adapter action. Replayed,
  metadata-only, invalid, blocked, and not-found resolutions record zero fetch
  debit. Exhaustion preserves the last valid checkpoint and is terminal.

### Deterministic behavior matrix

| condition | required result |
|---|---|
| Metadata search returns a recorded public repository route | resolve the exact route, select it, fetch/map once, and bind the card to the originating need |
| Metadata search returns only DOI/publisher metadata | `METADATA_ONLY`; retain candidate, issue bounded locator need or abstain, and award no evidence credit |
| Two arms encounter the same candidate | identical locator-policy result under the same policy hash |
| Resolver receives a prose URL guess or unrecorded redirect | `INVALID`; no fetch or budget debit |
| Public route is rights-blocked or host-unlisted | `RIGHTS_BLOCKED`; retain provenance and make no request |
| No distinct open candidate exists after sharing | `ABSTAINED_NO_DISTINCT_VIEWPOINT`; no open-viewpoint work is created |
| Distinct metadata-only candidate exists | optional `ADMITTED` with `CANDIDATE_PENDING`; discovery/hypothesis credit only |
| Distinct page-card-backed candidate exists | `ADMITTED` with `PAPER_CARD`; source-backed credit remains contingent on full final lineage |
| Support report has no action, card, adjudication, or discriminator | `ABSTAINED` or `PARTIAL`, never `COMPLETE` |
| Metadata-only R3 fixture is scored | zero evidence and zero unique source-backed contributions |
| Contradictory attributable source is found | preserve `WEAKENS`/contradiction state and current rival; do not reject or promote it |
| Duplicate resolution or completed checkpoint replays | return the recorded result with no new call, mutation, or debit |
| Budget exhausts during resolution/fetch | terminal typed budget state with the last valid checkpoint preserved |
| Malformed, stale, cross-case, or conflicting input arrives | fail closed with an attributable diagnostic |

### Authority and side-effect boundary

- Repository reads/writes: limited to declared code, fixtures, tests, docs, and
  `artifacts/goals/G10R-Z/`.
- Network, credentials, provider/model calls, subscriptions, and external
  messages: prohibited.
- Subprocesses: project verification commands only.
- Scientific validation, source promotion, lab approval, and physical action:
  prohibited.
- No completion verdict may freeze a manifest or authorize spending.

### Required fixture matrix

The recorded matrix must cover public-content success, metadata-only retention,
rights-blocked content, contradictory/weakening evidence, redundant and absent
open candidates, malformed locator output, stale/cross-case context,
partial fetch/map failure, budget exhaustion, unsupported adapter output,
duplicate resolution, checkpoint resume, and completed replay. Each condition
runs through A1 and A2-M where applicable under the same policy and ceilings.

## Deliverables

1. Versioned locator/headroom schemas and provider-neutral implementation.
2. Repaired live-capable A1/A2-M scheduling and scoring contracts.
3. Recorded fixture matrix and deterministic runner.
4. `headroom-matrix.json` with per-arm acquisition, card, attribution, open-slot,
   overhead, authority, and budget results.
5. Byte-stable `run.json`/`replay.json`, criterion ledger, protocol updates, and
   a final report with exactly one legal verdict.

## Goal-level acceptance criteria

1. Both A1 and A2-M resolve the same recorded metadata candidate to the same
   exact public locator and produce a validated page-aware card; the resolver
   never derives a route from free text.
2. Metadata-only, rights-blocked, not-found, malformed, and unsupported routes
   remain attributable typed outcomes with zero evidence credit and no lost
   candidate/hypothesis record.
3. Every positive evaluation fixture passes `EvaluationHeadroom=READY`; hidden
   answers remain unavailable to both arms, and any non-ready positive fixture
   invalidates rather than silently completing the comparison.
4. Open-viewpoint admission occurs only after initial sharing. Abstention or
   redundancy creates no tasks/calls/dossier/focus entry; candidate-pending
   admission cannot earn evidence or unique source-backed credit.
5. Structural support tasks are created only from typed unresolved needs, and
   no report becomes `COMPLETE` without observable work or a typed
   discriminator.
6. Deterministic and live scoring agree that zero-card metadata produces zero
   evidence and zero unique source-backed contribution while preserving raw
   discovery, hypotheses, contradiction, and review queues.
7. The offline A1/A2-M matrix uses identical source policy and hard per-case
   query, fetch, payload, simulation, token, cost, and stopping ceilings;
   actual usage and value-per-cost are reported separately.
8. Duplicate, resume, partial-failure, budget-exhaustion, stale, cross-case,
   malformed, contradictory, and unsupported fixtures satisfy the behavior
   matrix without external calls or historical-artifact mutation.
9. Replay is byte-stable and exactly-once at every state boundary; a completed
   replay performs no adapter/provider work and no budget debit.
10. Focused tests and `python3 -m pytest -q` pass, every criterion maps to a
    named test/artifact, and the report emits exactly one of
    `ACQUISITION_HEADROOM_READY`, `ACQUISITION_HEADROOM_NO_GO`, or
    `INCONCLUSIVE_ACQUISITION_HEADROOM`.

## Criterion-to-test/artifact map

| criterion | expected verification |
|---|---|
| 1 | `test_both_arms_resolve_and_map_same_public_candidate`; `headroom-matrix.json` |
| 2 | metadata/rights/not-found/malformed/unsupported parameterized tests |
| 3 | `test_positive_cases_require_arm_neutral_headroom`; fixture hashes in `run.json` |
| 4 | delayed admission and zero-work abstention/redundancy tests |
| 5 | `test_support_completion_requires_observable_work`; support ledger in matrix |
| 6 | scorer-parity and metadata-only R0/R3 tests |
| 7 | equal-ceiling assertion and per-arm usage ledger |
| 8 | named edge-case fixture tests and `criterion-ledger.json` |
| 9 | per-boundary resume matrix and `replay.json` |
| 10 | focused/full-suite logs and `report.md` |

## Stop conditions and handoff

Emit `ACQUISITION_HEADROOM_NO_GO` if arm-neutral lawful content resolution
cannot be made deterministic, metadata-only output still earns source-backed
credit, delayed open admission cannot be enforced, or the society cannot run
within the same hard ceilings. Emit `INCONCLUSIVE_ACQUISITION_HEADROOM` for an
implementation, fixture, or replay defect. Emit `ACQUISITION_HEADROOM_READY`
only when all ten criteria pass.

A ready result may propose a distinct fresh Phase-A freeze goal. It does not
create that freeze, initialize a provider, open the network, spend money,
promote evidence, or authorize laboratory work.

## Completion evidence

- `artifacts/goals/G10R-Z/headroom-matrix.json` records the same policy hash,
  exact locator resolutions, public-content opportunities, typed no-content
  outcomes, and equal A1/A2-M ceilings for every recorded fixture family.
- `artifacts/goals/G10R-Z/run.json` records one deterministic arm-neutral
  acquisition run per fixture family and shows that metadata-only output earns
  zero evidence and zero source-backed unique contribution.
- `artifacts/goals/G10R-Z/replay.json` is byte-stable, external-free, and
  reports zero duplicate calls and zero replay budget debits.
- `artifacts/goals/G10R-Z/criterion-ledger.json` marks all ten criteria PASS;
  focused G10R-Z tests pass and the repository suite was run after the repair.
- `artifacts/goals/G10R-Z/report.md` emits exactly
  `ACQUISITION_HEADROOM_READY` and preserves the no-freeze/no-paid-run
  boundary.

The next eligible work is a separate fresh Phase-A freeze after owner review;
this goal itself does not create or activate that freeze.
