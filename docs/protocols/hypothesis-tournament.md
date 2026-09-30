# Deterministic hypothesis tournament protocol

**Protocol version:** `g07e.1`
**Authority:** offline repository fixtures only; no network, model, agent, lab, or external communication authority.

## Purpose

This protocol turns a versioned problem card into a small, replayable competition among typed hypotheses and experiment questions. It is a discovery-platform substrate, not a performance validator. All outputs remain conditional on the card's support region and evidence locators.

## Memory tiers

| Tier | May be written by tournament? | Required provenance | Authority |
|---|---:|---|---|
| `immutable_evidence` | No | source locator and claim type | source record only |
| `typed_hypothesis` | Yes, append-only | evidence IDs, card/candidate, claim type | deterministic policy |
| `untrusted_note` | Yes, append-only | note ID and originating stage | no promotion authority |

Evidence records are loaded from the card and copied into the run manifest. The tournament cannot edit or overwrite them. Hypotheses and notes are derived records; a note can never satisfy an evidence locator requirement.

## Stages

1. **Propose** creates one hypothesis per valid candidate and a process-matched comparator from the card. The predicted observation names the card's primary endpoint and a controlled intervention/control contrast; it does not invent a recipe or result.
2. **Critique** records a disconfirming observation, confounder check, and cheapest useful discriminator. A single hypothesis receives `UNRESOLVED_RIVAL`; multiple hypotheses link explicit rivals.
3. **Adjudicate** assigns ordinal, separate utility components: endpoint fit, information value, feasibility, and risk. No aggregate score, numeric expected information gain, or performance model is emitted.
4. **Focus** applies the frozen local budget. It records candidates considered, reason, budget consumed, and the abstention condition. No budget can widen the evidence or domain.
5. **Promote/retract** applies the legal status-transition table below. A promotion remains a typed conditional assertion; it is never converted into evidence or physical authorization.

## Legal status transitions

| Current | Legal next statuses | Required condition |
|---|---|---|
| `HYPOTHESIS` | `SUPPORTED_WITHIN_CONTEXT`, `NARROW_USE_CASE`, `CONTRADICTED`, `REVIEW_REQUIRED`, `ABSTAIN`, `RETIRED` | evidence/provenance and policy reason are present |
| `SUPPORTED_WITHIN_CONTEXT` | `NARROW_USE_CASE`, `CONTRADICTED`, `REVIEW_REQUIRED`, `RETIRED` | new typed adjudication reason |
| `NARROW_USE_CASE` | `CONTRADICTED`, `REVIEW_REQUIRED`, `RETIRED` | support region or evidence changes |
| `CONTRADICTED` | `REVIEW_REQUIRED`, `RETIRED` | contradiction is preserved; no silent overwrite |
| `REVIEW_REQUIRED` | `HYPOTHESIS`, `ABSTAIN`, `RETIRED` | reviewer reason or explicit abstention |
| `ABSTAIN` | `HYPOTHESIS` | only with a new context version and `CONTEXT_AMENDED` reason |
| `RETIRED` | none | terminal record |

Every transition is appended as an event and retains the previous record. Context amendment must name the new context version; it cannot be smuggled in as a normal promotion.

## Output rules

- `PARETO_SET` is emitted when separate utility dimensions leave no defensible single winner.
- `RANKED_SET` is permitted only for a deterministic total ordering within one card; the MVP deliberately uses `PARETO_SET` for the normal multi-dimensional path.
- `REVIEW_REQUIRED` is emitted for contradictory or incomplete evidence.
- `ABSTAIN` is emitted for unsupported or out-of-domain candidates.
- `UNSAFE_REJECTED` is emitted before scoring for a forbidden combination.
- `NO_FEASIBLE_CANDIDATE` is emitted when every candidate violates declared constraints.
- `BUDGET_EXHAUSTED` is emitted with a partial manifest and no scope widening.

## Replay contract

The canonical JSON serialization is UTF-8, sorted keys, and compact separators. `result_id`, card digest, evidence-manifest digest, and policy hash are derived from that serialization. Replaying the same fixture and policy must produce byte-equivalent output. Fixture inputs are sealed repository data and are never interpreted as executable instructions.
