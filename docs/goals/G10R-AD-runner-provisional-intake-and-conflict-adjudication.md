# G10R-AD — Integrate provisional intake and conflict adjudication into the runner

**Status:** complete — `RUNNER_PROVISIONAL_INTAKE_READY`
**Dependencies:** G10R-AC `PROVISIONAL_EVIDENCE_LOOP_READY`; no live model,
network, subscription, credential, laboratory, or paid execution
**Authority:** offline repository implementation and deterministic replay only;
this goal may wire contracts into the runner, but may not activate a provider,
expand source policy, promote evidence, or authorize a Phase-B run

## Why this goal exists

G10R-AC proves the provisional-argument and open-world intake contracts in a
standalone ledger. The actual investigation path still does not route
viewpoint output through that ledger or produce claim-level conflict records in
its checkpoints. G10R-AD closes that integration boundary and adds a separate
adjudication layer for genuinely conflicting, attributable sources.

## Objective

Wire `ExploratoryArgument`, `CandidateSource`, `ClaimSourceEdge`, vetting, and
append-only revision records into the deterministic runner path used by A1 and
A2-M. Add a conflict-set adjudicator that compares supported and contradicted
edges by claim scope, material/process, comparator, endpoint, method, and study
identity without majority voting or automatic winner promotion. Prove the
complete path with offline fixtures and replay.

## In scope

- runner adapters that convert viewpoint claims and source leads into the
  G10R-AC records and persist them in case/arm checkpoints;
- a versioned `ConflictSet` and `ConflictAdjudication` contract grouping edges
  for the same claim and declaring whether the disagreement is a scope or
  method difference, a weighted conflict requiring review, or unresolved;
- explicit joins from viewpoint, action, candidate, source, claim, edge,
  dossier revision, portfolio, and score records;
- preservation of provisional arguments, nulls, rivals, adversarial reviews,
  misattribution, unretrievable sources, and contradictory edges;
- source-backed credit only for independently identified, admitted sources
  with exact claim locators and valid hashes;
- deterministic duplicate, stale-context, cross-case, malformed, partial,
  budget, and replay behavior; and
- a report separating integration success from scientific usefulness.

## Explicit exclusions

No live provider or network call, unrestricted crawling, subscription or
access-control bypass, new source host, budget increase, prompt optimization
against sealed cases, automatic conflict winner, immutable evidence promotion,
laboratory authorization, Phase-A freeze, or paid rerun.

## Architecture constraints

- The runner remains problem-context driven; no Roman-specific conflict rule
  enters the reusable contracts.
- Exploration, source identity, retrieval, claim support, adjudication,
  evidence credit, and scientific authority remain separate states.
- A contradiction is positive attributable evidence against a scoped claim; a
  missing, blocked, malformed, or unrelated source is not contradiction.
- Conflicting valid edges coexist until their comparability is adjudicated.
  Adjudication may narrow a claim or mark a method/scope difference, but may
  not erase an edge or silently promote a preferred mechanism.
- Checkpoints and revisions are append-only, case/arm bound, and replayable.

## Canonical contracts

`ConflictSet` schema version `1.0` contains `conflict_set_id`, case/problem
identity, `claim_id`, edge IDs, independent source IDs, scope fields, and
status `OPEN`, `SCOPE_DIFFERENCE`, `METHOD_DIFFERENCE`, `WEIGHTED_CONFLICT`, or
`UNRESOLVED`.

`ConflictAdjudication` schema version `1.0` contains an append-only decision,
reviewer role, comparability checks, rationale, unresolved questions,
revision IDs, and `preserves_prior=true`. It cannot write an immutable
evidence record or change a source's identity.

Required invariants:

- supported or contradicted edges require an admitted source, exact locator,
  claim scope, and matching content hash when available;
- a source failure can only produce `UNRETRIEVABLE` or a typed rejection;
- DOI, content hash, citation ancestry, and stable work identity deduplicate
  apparent independent support or conflict;
- consensus, repetition, rhetoric, and agent count contribute zero scientific
  credit; and
- stale manifest, cross-case, duplicate-conflict, or post-terminal writes fail
  closed while preserving prior records.

## Deterministic behavior matrix

| condition | required result |
|---|---|
| viewpoint emits a strong argument with an unaccepted citation | checkpoint stores a `PROVISIONAL` argument and quarantined source lead with zero evidence credit |
| admitted source supports an exact claim | `SUPPORTED` edge and source-backed contribution are recorded |
| admitted source directly conflicts with an exact claim | `CONTRADICTED` edge, open conflict set, and append-only argument revision; original wording remains |
| two valid sources disagree on unlike materials, endpoints, or methods | conflict set resolves to `SCOPE_DIFFERENCE` or `METHOD_DIFFERENCE`; neither source is discarded |
| two comparable valid sources genuinely disagree | `WEIGHTED_CONFLICT` or `UNRESOLVED`; no automatic winner or promotion |
| source is unrelated to the claim | `UNRESOLVED` or `MISATTRIBUTED`; no contradiction credit |
| fetch is blocked, missing, or malformed | `UNRETRIEVABLE`/rejected; never `CONTRADICTED` |
| duplicate paper is cited by several agents | one independent work; repetition earns no corroboration |
| stale, cross-case, or conflicting checkpoint arrives | fail closed and preserve the prior valid checkpoint |
| completed replay is run again | byte-stable output, zero provider/network calls, zero new budget debit |

## Expected implementation surface

- `src/roman_concrete_lab/agents/investigation.py` and
  `src/roman_concrete_lab/agents/investigation_g10r_z.py` for runner adapters
  and checkpoint joins;
- `src/roman_concrete_lab/agents/provisional_intake.py` for the additive
  intake boundary and a new conflict-adjudication module or equivalent;
- `src/roman_concrete_lab/agents/viewpoint_society.py` for viewpoint-to-claim
  mapping without changing agent incentives;
- `schemas/conflict-set.schema.json` and
  `schemas/conflict-adjudication.schema.json`;
- deterministic fixtures under `fixtures/investigation/g10r-ad/`;
- `tools/evaluation/runner_provisional_intake_replay.py`;
- focused tests under `tests/agents/` and `tests/retrieval/`; and
- `artifacts/goals/G10R-AD/{manifest,criterion-ledger,replay,report}.json/md`.

Equivalent paths are allowed only when the report maps them to this contract.

## Goal-level acceptance criteria

1. A1 and A2-M runner checkpoints contain valid provisional arguments and
   quarantined source leads emitted by viewpoint work without requiring corpus
   acceptance.
2. The runner creates valid claim-source edges and preserves the G10R-AC legal
   statuses, exact-locator/hash gates, source identity, and authority boundary.
3. A directly contradictory attributable edge creates an append-only argument
   revision and conflict set while preserving the original argument, source,
   dissent, and rival.
4. Scope, method, endpoint, material, and comparator differences are recorded
   as typed conflict adjudication rather than collapsed into contradiction or
   consensus.
5. Comparable conflicting sources remain jointly visible as
   `WEIGHTED_CONFLICT` or `UNRESOLVED`; no majority, rhetoric, or agent count
   can select a winner or earn evidence credit.
6. Unrelated, duplicate, metadata-only, rights-blocked, malformed, and
   unretrievable sources retain typed outcomes and cannot create contradiction
   or independent corroboration.
7. Case/arm/action/source/claim/edge/revision joins, checkpoint resume,
   duplicate replay, budget exhaustion, stale context, and cross-case writes
   are deterministic and fail closed where required.
8. The offline replay makes zero model, network, credential, subscription, or
   paid calls; all positive, contradictory, scope-different, unresolved,
   partial-failure, and malformed fixtures are represented in the report.
9. Focused tests, the full repository suite, `git diff --check`, and the
   criterion ledger pass; G10R-AC and all historical paid artifacts remain
   unchanged.

## Handoff

Return exactly one of `RUNNER_PROVISIONAL_INTAKE_READY`,
`RUNNER_PROVISIONAL_INTAKE_NO_GO`, or `INCONCLUSIVE_RUNNER_INTAKE`.
`RUNNER_PROVISIONAL_INTAKE_READY` permits proposing a new Phase-A freeze or a
separately authorized live integration evaluation; it does not authorize
either action.

## Completion evidence

The offline replay in `artifacts/goals/G10R-AD/replay.json` passed all nine
criteria with zero model calls, zero network calls, zero credential reads, and
`$0` paid spend. The focused runner/intake tests pass (`5 passed`); the full
repository suite passes (`193 passed`); and `git diff --check` passes. The
historical G10R-AC, G10R-AB, and G10R-X artifacts remain unchanged.
