# G10 closed-world agent evaluation protocol

**Protocol version:** `g10.1-closed-world-ablation`
**Frozen:** 2026-10-10
**Base workflow:** G09 `EXPLORATORY_PLATFORM` and G07E deterministic tournament

## Decision question

Does a bounded, role-biased society improve the frozen deterministic workflow on problem-specific hypothesis and experiment-question tasks without weakening provenance, memory authority, constraint handling, stability, or cost discipline?

This goal uses a transparent offline `fixture-agent-v1` provider. It exercises the society architecture and its authority boundaries; it is not a claim about a live language model.

## Treatments and preregistration

- `CONTROL`: frozen G07E deterministic replay.
- `SOCIETY`: five roles—evidence skeptic, mechanism proposer, transfer analyst, experimental designer, and safety/provenance reviewer—with shared immutable evidence and typed derived memory.
- Eight sealed cases cover positive, contradictory, malformed, partial, unsupported, unsafe, no-feasible, and budget-exhaustion behavior.
- Three seeded repetitions per case (`11`, `23`, `47`) are scored after the protocol is frozen.
- One development-only iteration is allowed before sealed scoring. Development cases are never included in the adoption metric.
- Per run: five role calls, two focus slots, and no scope widening.

Adopt only if society task accuracy exceeds control by at least 0.05, unsupported-claim rate is no greater than control + 0.02, critical provenance/constraint failures are zero, and mean cost is no more than 2× control. Otherwise emit `REJECT_AGENT_SOCIETY`.

## Iteration rule

Version `v1.0` uses round-robin role attention. Version `v1.1` is the single permitted revision: it changes only focus ordering to prioritize provenance/constraint risk before mechanism novelty and records a before/after diagnostic on development fixtures. No sealed case, expected status, rubric, budget, or control policy may change.

## Memory and authority

Evidence memory is immutable. Hypothesis memory is typed, append-only, source-located, and `REVIEW_REQUIRED`; episodic notes are run-private and cannot cross problem contexts. Consensus cannot promote evidence. No role may approve safety, write empirical results, contact an external party, retrieve new sources, or authorize laboratory work.

## State and replay

`created -> context_loaded -> evidence_frozen -> proposing -> critiquing -> adjudicating -> selecting -> awaiting_review | failed | budget_exhausted`.

Replaying a completed evaluation returns byte-equivalent artifacts. A changed fixture, protocol, policy, or seed creates a new run identity. Malformed, unsafe, unsupported, and budget-exhausted cases fail closed with their prescribed status and partial trace.
