# G10R-AG — Separately activated proposal evaluation

**Status:** proposed
**Dependencies:** G10R-AF `PROPOSAL_MACHINERY_READY`; exact committed
G10R-AE Phase-A manifest; explicit owner/provider/network activation
**Authority:** one bounded live evaluation only; no laboratory, safety,
evidence-promotion, subscription, or source-policy expansion authority

## Objective

Run one A1 versus A2-M evaluation of the proposal machinery using the exact
G10R-AE manifest, then determine whether the society produces more useful
reviewable proposals than a single investigator under equal resources. The
comparison measures proposal completeness, source attribution, contradiction
retention, falsifiability, discriminators, uncertainty, and rival preservation;
it does not measure rhetorical persuasiveness or consensus.

## Activation contract

The run may initialize a provider only after an owner record names all of:

- manifest ID `G10R-AE-fresh-phase-a-runner-intake-v1`;
- the exact G10R-AE manifest SHA-256;
- provider and model identity;
- the frozen read-only source policy and exact host permission;
- the hard `$25.00` aggregate cap; and
- the output namespace for this evaluation.

Missing, stale, or mismatched activation fields stop before provider or network
initialization. A cycle invocation or a `PROPOSAL_MACHINERY_READY` result does
not activate this goal.

## In scope

- one preregistered A1/A2-M comparison on the frozen G10R-AF cases;
- live model/provider traces and exact retrieval/action telemetry within the
  frozen source policy and aggregate budget;
- provisional packets, source leads, claim edges, conflict sets, incomplete
  packets, and partial failures retained in the output namespace;
- treatment-blinded deterministic scoring and a case-level comparison; and
- a post-run handoff that routes positive, negative, and inconclusive results
  to the correct offline follow-up.

## Explicit exclusions

No new source host, subscription or paywall access, credentials beyond the
activated provider, budget increase, evidence promotion, scientific or safety
approval, laboratory action, automatic rerun, or G11 approval. Retrieved
sources remain candidates until separately vetted; a proposal is not a material
performance claim.

## Expected implementation surface

- `tools/evaluation/separately_activated_proposal_evaluation.py`;
- `tests/agents/test_separately_activated_proposal_evaluation.py`;
- `schemas/proposal-evaluation-run.schema.json`;
- `artifacts/goals/G10R-AG/{activation,run,score,criterion-ledger,report}.*`;
- an immutable event/budget ledger retaining provider, model, source-policy,
  call, token, query, fetch, and spend telemetry; and
- no mutation of G10R-AE, G10R-AF, or historical paid artifacts.

## Deterministic behavior matrix

| Condition | Required result |
|---|---|
| Exact activation record and matching frozen manifest | provider may initialize within cap |
| Missing or stale activation field | stop before provider/network initialization |
| Valid complete proposal | retain and score typed proposal components |
| Contradictory or pending source | retain both states; no automatic winner or direct evidence promotion |
| Malformed, duplicate, cross-case, or stale packet | typed fail-closed event; preserve prior valid packets |
| Budget exhaustion or provider failure | retain partial trace and terminal state; no automatic retry |
| Rhetorical agreement without proposal content | zero scientific/proposal credit |
| Positive society signal | emit `ESCALATE_PROPOSAL_EVALUATION` only as a recommendation for a later adoption-grade goal |
| Negative or ambiguous signal | emit `DO_NOT_ESCALATE_PROPOSAL_EVALUATION` or `INCONCLUSIVE_PROPOSAL_EVALUATION` and route to offline diagnosis |

## Acceptance criteria

1. The activation record names the exact G10R-AE manifest ID/hash, provider,
   model, source policy, cap, and output namespace; mismatches stop before any
   external call.
2. A1 and A2-M receive the same cases, proposal contract, source policy,
   authority, and aggregate budget; treatment identity is unavailable to the
   deterministic scorer.
3. Every successful, incomplete, contradictory, pending, and failed proposal
   path is retained with case, arm, viewpoint, action, source, and checkpoint
   provenance, or a typed reason for omission.
4. The score ledger reports typed proposal components and zero rhetorical,
   consensus, answer-length, viewpoint-count, and agent-count credit.
5. The event and budget ledger records model/provider identity, calls, tokens,
   queries, fetches, source outcomes, retries, partial failures, and spend;
   total spend never exceeds `$25.00`.
6. Blinded replay of the recorded run is byte-stable and makes no additional
   provider, network, credential, or budget calls.
7. The report emits exactly one legal outcome and does not promote evidence,
   authorize a laboratory, or bypass G11.

## Handoff

Return exactly one of `ESCALATE_PROPOSAL_EVALUATION`,
`DO_NOT_ESCALATE_PROPOSAL_EVALUATION`, or
`INCONCLUSIVE_PROPOSAL_EVALUATION`. A positive result only proposes a later
adoption-grade evaluation; it is not a scientific validation or lab approval.
