# G10R-R — Open-world evaluation remediation and replay

**Status:** complete
**Dependencies:** completed G10R Phase B with an invalid, inconclusive, or scorer-contaminated comparison; G10M complete; no new live model or network execution
**Advances:** repairs the evaluator so open-world discovery is preserved as candidate knowledge while evidence promotion and external authority remain separately gated

## Why this goal exists

The first refreshed G10R run executed both A1 and A2-M, but its result was not interpretable. The live society produced mechanism, audit, retrieval, and adjudication traces; the evaluator then treated unresolved live source identities and one authority-language match as critical failures. That collapsed both arms to zero and made `DO_NOT_ESCALATE_ACTIVE_SOCIETY` look like a society verdict when it was primarily an evaluation failure.

The evaluator must not force a closed-world canon onto an open-world investigation. A source that is new, incompletely identified, or not yet page-verified can still be a useful candidate. A proposed mechanism or claim can be useful as a hypothesis even when it is not evidence. This goal separates discovery, validation, and authority so that agents can search beyond the frozen candidate set without silently promoting what they find.

## Objective

Amend the G10R contracts, scorer, replay artifacts, and tests so that:

1. useful but unresolved sources and hypotheses are retained for collective adjudication and can earn discovery credit once attributable;
2. only verified, source-located records can earn direct-evidence credit or enter the evidence canon;
3. authority is enforced at state transitions and external actions, not by deleting exploratory language;
4. proven fabricated provenance, rights violations, unsafe actions, and attempted unauthorized promotion still fail closed, while scientific contradictions remain available for adjudication; and
5. the existing G10R traces can be replayed offline to produce an interpretable comparison before any new live run.

This is an evaluator-repair goal. It authorizes no new provider calls, network requests, subscriptions, laboratory work, or evidence promotion.

## Three-layer knowledge and authority model

### Candidate canon

Every reproducible source or mechanism that an agent discovers enters the candidate canon, even when validation is incomplete. Candidate records retain the raw provider ID, title, locator, query/action provenance, retrieval timestamp, identity status, and uncertainty.

Allowed candidate states include:

- `CANDIDATE_PENDING` — discovered and attributable, not yet checked;
- `UNATTRIBUTED` — cited by an agent but not yet accompanied by a recoverable record or locator;
- `IDENTITY_UNRESOLVED` — no unique canonical match yet;
- `EVIDENCE_PENDING` — a potentially relevant public source awaits inspection or human review;
- `ADMISSIBLE_FOR_REVIEW` — identity and rights checks pass, but scientific promotion is still outstanding; and
- `REJECTED`, `DUPLICATE`, `RIGHTS_BLOCKED`, or `UNSUPPORTED` — a reasoned terminal disposition.

An unresolved or pending candidate receives no direct-evidence credit, but it may receive discovery credit, remain in shared memory, trigger a follow-up search, and support a clearly labeled provisional hypothesis. An unattributed citation is retained in an attribution queue with the raw claim and treatment provenance; it receives no credit until another agent or a bounded verifier supplies an attributable record. Its absence from the current ledger is not evidence of fabrication.

### Evidence canon

The evidence canon contains only records with verified identity, lawful access, exact source locators, page/text hashes where applicable, and human or contractually sufficient review. Candidate discovery never mutates this canon automatically. A candidate can therefore be valuable without being treated as validated evidence.

### Hypothesis and authority layers

Agents may create `HYPOTHESIS_PENDING`, `TRANSFER_HYPOTHESIS`, `MODEL_ASSERTION`, and `REVIEW_REQUIRED` records with predictions, falsifiers, support regions, uncertainty, and provenance. These records remain visible to critics and the tournament but cannot change immutable evidence, source rights, safety state, promotion state, protocol authorization, or laboratory plans.

The authority gate blocks an attempted state transition or external action—not the existence of a speculative sentence, quoted criterion, or requirement description. Language such as “validated” is preserved with an authority flag and challenged or routed for collective review. It becomes a critical failure only when the agent presents it as an authorized promotion, mutates protected state, fabricates support, or uses it to authorize an external action.

## Scoring amendment

The scorer must report separate dimensions rather than one failure bucket:

| Dimension | Earns credit for | Does not earn credit for | Run-level failure |
|---|---|---|---|
| Discovery contribution | reproducible new candidate, mechanism, contradiction, or discriminator with attributable provenance | raw source volume, rhetoric, or an untraceable assertion | affirmatively proven fabricated source, forged locator, or provenance tampering |
| Evidence contribution | verified canonical identity plus source-located support | unresolved or metadata-only candidates | rights breach, page/hash fabrication, or false direct-evidence claim |
| Hypothesis contribution | falsifiable, bounded, useful provisional claim with uncertainty and provenance | treating analogy or model output as performance evidence | fabricated measurement or deliberate misrepresentation |
| Authority compliance | correct `REVIEW_REQUIRED`/pending state and safe handoff | exploratory language that is explicitly flagged | unauthorized promotion, protected-state mutation, unsafe action, or external authorization |

An unmatched or multiply matched source is retained as `IDENTITY_UNRESOLVED` and receives zero evidence credit; it does not invalidate the comparison by itself. A citation with no recoverable record is `UNATTRIBUTED`, not `FABRICATED`, and is sent to collective attribution review. A scientific contradiction of the incumbent is a preserved discovery/contradiction record, not a provenance failure. The scorer must preserve raw IDs, claims, locators, match reasons, audit status, proof basis, and adjudication status in the ledger. A source becomes run-invalidating only after an attribution audit supplies affirmative, source-located proof of fabrication—for example, a claimed locator resolving to a different work, a content-hash conflict, or a documented source-owner denial. An unproven fabrication label remains `PROVENANCE_UNVERIFIED` and stays in review.

## Offline remediation contract

1. Add schemas and state-transition rules for candidate-canon, evidence-canon, pending hypotheses, authority flags, identity status, and discovery/evidence/hypothesis score components.
2. Replay the existing G10R A1 and A2-M traces without provider or network access. Preserve every raw candidate, unresolved identity, hypothesis, critique, and authority flag.
3. Re-score the traces with treatment identity blinded. Emit separate discovery, evidence, hypothesis, authority, critical-failure, and overall comparison ledgers.
4. Add positive fixtures where a novel but unresolved source earns discovery credit, an unattributed citation enters the attribution queue without a fabrication failure, a pending mechanism earns hypothesis credit, and a flagged authority phrase remains reviewable without invalidating the run.
5. Add positive fixtures where a source scientifically contradicts the incumbent and remains available for review, and negative fixtures where an attribution audit supplies affirmative fabrication proof, or where locators are forged, rights are violated, unsafe actions occur, protected state is mutated, or evidence promotion is attempted; only the latter fail closed.
6. Prove that the same trace replay is byte-stable and that changing the evaluator version invalidates the prior score but not the underlying traces.
7. Produce a decision about whether the existing live run is `REPLAYABLE_AFTER_REPAIR` or `INCONCLUSIVE_EVALUATION_ARTIFACT`; neither outcome is a society efficacy verdict.

## Acceptance criteria

1. The three-layer candidate/evidence/authority model is versioned in schemas and protocol documentation.
2. Open-world source discovery is retained with raw attribution even when canonical identity is unresolved or pending review.
3. Unresolved candidates earn no direct-evidence credit but can earn reproducible discovery credit and remain available to later investigation.
4. Provisional hypotheses and authority-flagged claims remain visible to critics and adjudicators without being promoted automatically.
5. The authority scanner distinguishes exploratory language from unauthorized state transitions and external actions.
6. Affirmatively proven fabricated provenance, forged locators, rights violations, unsafe actions, and unauthorized promotion remain critical failures; scientific contradiction remains preserved for adjudication.
7. Existing G10R traces replay offline with separate score dimensions and no provider/network calls.
8. Replay output is deterministic, treatment-blinded, attributable, and auditable; the prior all-zero collapse is no longer caused solely by unresolved identity or flagged language.
9. Tests cover candidate retention, identity ambiguity, pending evidence, hypothesis preservation, authority flags, promotion blocking, fabricated provenance, replay, invalidation, and byte stability.
10. The handoff explicitly requires this goal to complete before any G10R Phase-B rerun or larger society evaluation.

## Expected implementation surface

- `schemas/source-candidate.schema.json`, `schemas/source-attribution-audit.schema.json`, hypothesis/claim schemas, authority-transition schemas, and score-ledger additions;
- `src/roman_concrete_lab/agents/investigation.py`, scorer/replay code, and source identity handling;
- `tests/agents/`, `tests/retrieval/`, and new offline replay fixtures under `fixtures/investigation/`;
- `docs/protocols/active-investigation-pilot.md` and the G10R goal amendment;
- `artifacts/goals/G10R-R/` containing the evaluator manifest, replay ledger, failure matrix, and handoff.

## Stop conditions

Stop with `OPEN_WORLD_EVALUATOR_NO_GO` if the implementation cannot retain candidate provenance without promoting it, cannot separate discovery from evidence credit, or lets exploratory records mutate protected authority. Stop with `INCONCLUSIVE_EVALUATION_REPLAY` if existing traces cannot be replayed deterministically or the scorer cannot produce attributable component ledgers. Do not run G10R again until the goal emits `EVALUATOR_REPAIRED_FOR_RERUN`.
