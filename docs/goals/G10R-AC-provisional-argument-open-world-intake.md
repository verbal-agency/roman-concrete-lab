# G10R-AC — Build the provisional-argument and open-world intake loop

**Status:** complete — `PROVISIONAL_EVIDENCE_LOOP_READY`
**Dependencies:** G10R-AB `INCONCLUSIVE_ACTIVE_INVESTIGATION`; G10R-P target-state amendment v2; no live model, network, subscription, or laboratory execution
**Authority:** offline implementation only; agents may propose arguments and source leads, but may not self-admit sources, promote evidence, authorize experiments, or widen the live source policy

## Objective

Implement and replay the target capability in which biased viewpoint agents can
make strong provisional arguments and cite unaccepted or newly discovered
sources, while separate acquisition and vetting layers determine whether each
claim–source edge is supported, contradicted, unresolved, misattributed, or
unretrievable. Preserve every argument and revision; do not treat source
failure as contradiction or consensus as corroboration.

## In scope

- versioned `ExploratoryArgument`, `CandidateSource`, `ClaimSourceEdge`,
  `VettingDecision`, and append-only revision schemas;
- a quarantine intake path for newly discovered public locators, including
  unknown-host, metadata-only, rights-blocked, malformed, duplicate, and
  fetch-positive records;
- deterministic identity, content-hash, citation-ancestry, and independent-work
  deduplication;
- claim-level vetting with page/figure/table/locator and content-hash
  requirements for support or contradiction;
- adversarial vetting, null/rival preservation, and zero credit for consensus,
  repetition, rhetoric, or agent count;
- revision and rescue behavior when a later source supports, weakens,
  contradicts, or fails to resolve an earlier provisional argument; and
- replay, budget, authority, and illegal-transition tests.

## Explicit exclusions

No live provider or network call, unrestricted crawling, subscription or
access-control bypass, automatic corpus admission from an agent claim,
immutable evidence promotion, laboratory authorization, or paid rerun.

## Deterministic behavior matrix

| condition | required result |
|---|---|
| strong argument with unaccepted citation | argument remains `PROVISIONAL`; source lead is quarantined; zero evidence credit |
| fetched source with exact identity and claim locator | source may become `ADMITTED_CORPUS`; edge becomes `SUPPORTED` only after vetting |
| real source unrelated to cited claim | edge `UNRESOLVED` or `MISATTRIBUTED`; argument remains reviewable |
| source directly conflicts with claim | edge `CONTRADICTED`; incumbent argument is revised, not deleted |
| fetch denied, missing, or malformed | source `UNRETRIEVABLE`/rejected typed outcome; never `CONTRADICTED` |
| repeated DOI/content hash/citation ancestor | one independent work; repetition earns no corroboration |
| agent consensus without independent source edges | zero scientific credit; null/rival retained |
| unknown public host | quarantined lead; no direct evidence credit until policy/vetting review |
| conflicting duplicate or cross-case write | fail closed and preserve prior valid records |

## Acceptance criteria

1. A biased viewpoint can create a valid provisional argument with unaccepted
   source references, predictions, uncertainty, and requested discriminators.
2. Acquisition can record a newly discovered locator in quarantine without
   requiring prior corpus acceptance; unknown-host and rights-blocked routes
   earn zero evidence credit and remain reviewable.
3. Every claim–source edge has exactly one legal status from
   `SUPPORTED`, `CONTRADICTED`, `UNRESOLVED`, `MISATTRIBUTED`, or
   `UNRETRIEVABLE`, with illegal transitions rejected.
4. `SUPPORTED` and `CONTRADICTED` require exact claim scope plus a page,
   figure, table, or locator and content hash when available; failed retrieval
   cannot produce contradiction.
5. Identity, content hash, and citation ancestry prevent one work from being
   counted as independent corroboration more than once.
6. Later vetting produces append-only argument and edge revisions; it can
   weaken, rescue, or contradict an argument without erasing its original
   wording, provenance, or dissent.
7. An adversarial vetter, null, and credible rival are preserved; consensus,
   repetition, rhetoric, and agent count receive zero scientific credit.
8. Positive, contradictory, malformed, partial-failure, duplicate,
   metadata-only, rights-blocked, unknown-host, and budget-exhaustion fixtures
   replay deterministically with no provider or network calls.
9. The target-state artifact, protocol, roadmap, schemas, tests, and report
   agree on the capability, legal statuses, authority boundary, and next
   handoff; full tests and `git diff --check` pass.

## Expected implementation surface

- schemas under `schemas/` for arguments, candidate sources, claim–source
  edges, vetting decisions, and revisions;
- additive intake/vetting modules under
  `src/roman_concrete_lab/agents/` and `src/roman_concrete_lab/retrieval/`;
- deterministic fixtures under `fixtures/investigation/g10r-ac/`;
- focused tests under `tests/agents/` and `tests/retrieval/`;
- `tools/evaluation/provisional_argument_open_world_intake.py`; and
- `artifacts/goals/G10R-AC/manifest.json`, `criterion-ledger.json`,
  `replay.json`, and `report.md`.

## Handoff

Return exactly one of `PROVISIONAL_EVIDENCE_LOOP_READY`,
`PROVISIONAL_EVIDENCE_LOOP_NO_GO`, or `INCONCLUSIVE_PROVISIONAL_INTAKE`.
Only the first permits a later Phase-A redesign proposal; it does not authorize
live calls, source-policy expansion, evidence promotion, or another paid run.

## Completion evidence

The offline replay in `artifacts/goals/G10R-AC/replay.json` passed all eight
behavior criteria with zero model calls, zero network calls, zero credential
reads, and `$0` paid spend. Focused tests pass (`5 passed`); the full suite
passes (`189 passed`); and `git diff --check` passes. A stale historical
G10R-X manifest hash was refreshed for the already-amended viewpoint protocol
so the repository-wide integrity test remains valid.
