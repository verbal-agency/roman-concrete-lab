# G10R-AF — Proposal-machinery readiness

**Status:** proposed
**Dependencies:** G10R-AE `PHASE_A_READY_FOR_OWNER_ACTIVATION`; no live model,
network, subscription, credential, laboratory, or paid execution
**Advances:** tests whether the repaired runner can turn viewpoint work into
reviewable, source-attributed, contradiction-aware experiment proposals rather
than rewarding debate volume or rhetorical agreement

## Objective

Build and verify the proposal boundary that sits between the agent society and
human scientific review. A proposal must state a mechanism or process claim as
a provisional argument, identify a process-matched comparator and measurable
endpoint, predict an observation, name a falsifier and discriminator, preserve
uncertainty and rival explanations, and link every supporting or conflicting
claim to its source/action provenance. The goal evaluates proposal structure
and usefulness; it does not decide whether a material works.

## In scope

- a versioned proposal-packet schema and runner adapter for A1 and A2-M;
- typed source-edge, conflict, pending-candidate, and unresolved-rival fields;
- deterministic proposal-quality scoring in which rhetoric, consensus, answer
  length, viewpoint count, and agent count earn zero credit;
- offline fixtures for complete, contradictory, metadata-only, unresolved,
  malformed, duplicate, cross-case, and budget-exhausted proposals;
- a sealed-case replay that compares the single investigator and society on
  proposal completeness, attributable support, contradiction retention,
  discriminator quality, falsifiability, and uncertainty preservation under
  equal declared budgets; and
- an activation-ready handoff for a later, separately authorized live proposal
  evaluation using the exact G10R-AE manifest.

## Explicit exclusions

No model or network calls, credentials, new source hosts, subscription access,
evidence promotion, scientific or safety approval, laboratory work, rhetorical
debate tournament, consensus-based winner selection, budget increase, or
automatic Phase-B activation.

## Expected implementation surface

- `schemas/proposal-packet.schema.json`;
- `src/roman_concrete_lab/agents/proposal_machinery.py`;
- `tools/evaluation/proposal_machinery_replay.py`;
- `fixtures/investigation/g10r-af/` with sealed cases and recorded source
  edges;
- `tests/agents/test_proposal_machinery.py`;
- `artifacts/goals/G10R-AF/{manifest,replay,criterion-ledger,report}.json/md`;
- `docs/protocols/proposal-machinery.md`; and
- a roadmap-ready handoff naming the later live-evaluation dependency.

## Canonical proposal contract

Every packet must include `proposal_id`, `case_id`, `arm`, `viewpoint_id`,
`intervention_or_process`, `comparator`, `primary_endpoint`,
`predicted_observation`, `falsifier`, `discriminator`, `support_region`,
`uncertainty`, `source_edges`, `conflict_set_ids`, `rival_proposal_ids`, and a
typed status. Source edges must retain `SUPPORTED`, `CONTRADICTED`,
`UNRETRIEVABLE`, `METADATA_ONLY`, or `REVIEW_REQUIRED` without collapsing them
into a vote. Pending or contradictory sources remain visible and earn no direct
evidence credit until their stated review conditions are satisfied.

## Deterministic behavior matrix

| Input condition | Required result |
|---|---|
| Complete proposal with attributable support and a falsifier | `PROPOSAL_REVIEWABLE`; typed proposal credit only |
| Contradictory sources with comparable scope | retain both edges and conflict set; no winner by consensus |
| Metadata-only, blocked, or unresolved source | retain as pending; zero direct-evidence credit |
| Missing comparator, endpoint, falsifier, or provenance | `PROPOSAL_INCOMPLETE`; no proposal credit |
| Duplicate proposal with changed content | fail closed with conflict error |
| Cross-case or stale checkpoint | reject before scoring |
| Budget exhaustion or partial failure | preserve successful packets and report the terminal budget state |
| Rhetorical agreement without typed proposal content | zero scientific credit |

## Acceptance criteria

1. The schema and adapter emit valid, case-bound proposal packets for both A1
   and A2-M, and reject missing required fields or illegal statuses.
2. Every retained proposal carries intervention/process, comparator, endpoint,
   prediction, falsifier, discriminator, uncertainty, and source/action
   provenance, or is explicitly marked `PROPOSAL_INCOMPLETE`.
3. Supporting, contradictory, metadata-only, blocked, and unresolved sources
   remain separately typed; no source is silently promoted or discarded.
4. The deterministic scorer awards zero credit for rhetoric, consensus,
   answer length, viewpoint count, or agent count and reports the typed proposal
   components separately.
5. The sealed offline fixtures cover positive, negative, contradictory,
   malformed, duplicate, cross-case, partial-failure, and budget-exhaustion
   paths, with byte-stable replay and no external calls.
6. The A1/A2-M comparison uses the same cases, source policy, authority,
   aggregate budget, and scoring contract; treatment identity is not available
   to the proposal scorer.
7. The criterion ledger and report distinguish proposal usefulness from
   scientific validation, evidence promotion, and laboratory authorization.
8. The handoff names the exact G10R-AE manifest dependency and states that a
   later live evaluation requires separate owner/provider/network activation.

## Handoff

Return exactly one of `PROPOSAL_MACHINERY_READY`,
`PROPOSAL_MACHINERY_NO_GO`, or `INCONCLUSIVE_PROPOSAL_MACHINERY`. A ready
result permits drafting a separate paid-evaluation goal; it does not authorize
provider initialization, network access, or a laboratory handoff.
