# G10M — Mechanism-proponent society design

**Status:** complete
**Dependencies:** G10R Phase A complete under `g10r.3-active-investigation-pilot`; G09 complete; G10B complete with any verdict; G-LI complete
**Advances:** upgrades the active-investigation society from structural search branches alone to a two-layer tournament in which competing mechanism proponents are challenged and resourced by structural investigators

## Why this goal exists

The current G10R A2 design tests structural specialization: an evidence skeptic, a mechanism/transfer explorer, and an experiment/simulation designer divide the investigation. That can test whether work allocation helps, but it does not test the intended discovery behavior in which agents champion competing explanations, derive consequences, and try to defeat one another with evidence.

G10M defines that missing layer before any G10R live treatment is activated. It is a design and offline-contract goal, not a model-spend or scientific-result goal. The mechanism layer must create useful competition without turning advocacy, majority agreement, or fluent explanation into evidence.

## Objective

Amend the A2 society into a two-layer mechanism tournament and prove offline that it can represent, investigate, criticize, focus, and adjudicate competing mechanisms under the same aggregate authority and resource envelope as A1. Preserve the non-agent evidence and promotion boundaries. The output is a versioned Phase-A-ready protocol and implementation, not a claim that any mechanism is correct.

## Target architecture

### A1 control

A1 remains one tool-using investigator with the full aggregate query, fetch, simulation, token, payload, time, and cost budget. It produces the same typed evidence, hypothesis, falsifier, uncertainty, and portfolio records used by the society.

### A2-M mechanism tournament

1. **Mechanism roster.** Freeze a case-specific roster from the approved context and evidence landscape: at least two plausible mechanism cards, one explicit null/no-mechanism card, and one open slot for a newly proposed mechanism. A roster entry records its mechanism statement, support region, prior basis, predicted observations, falsifiers, and known alternatives. The roster is a search scaffold, not evidence.
2. **Mechanism proponents.** Initialize one isolated proponent per roster entry. Each proponent owns its mechanism card, searches for support and contradiction, maps evidence to predictions, records negative searches, and must state what would falsify or weaken its mechanism. It may propose a new mechanism only through the open slot and typed admission rule.
3. **Structural investigators.** Run the evidence-skeptic, transfer-boundary, and experiment/simulation-designer roles as cross-cutting auditors. They inspect typed proponent claims after the private round, search for contradictions and domain errors, and propose discriminating actions; they do not vote a mechanism into promotion.
4. **Shared memory.** The first round is private. The shared blackboard contains append-only mechanism cards, source-located evidence cards, typed claims, predictions, falsifiers, critiques, negative searches, and unresolved disputes. Raw private discourse and untyped persuasion do not enter shared memory.
5. **Tournament and focus.** A deterministic allocator spends the remaining common budget on actions with the highest expected discrimination, uncertainty reduction, provenance risk, feasibility, and novelty value. It must preserve a credible rival and the null unless the frozen rule explicitly permits abstention. The final adjudicator selects a leading provisional mechanism, surviving rivals, and the cheapest discriminating next action; it cannot promote evidence or authorize a lab.

## Anti-anchoring and fairness requirements

- Include a null mechanism and an open mechanism slot in every sealed case.
- Keep proponents isolated from competitor traces until all first-round reports are committed.
- Require every proponent claim to include a predicted observation, falsifier, support region, and source/trace provenance.
- Permit a new mechanism only through a typed admission record with a reason, evidence locator or explicit uncertainty basis, and a bounded budget debit.
- Score supported predictions, contradictions, discriminators, uncertainty reduction, and provenance—not advocacy strength, consensus, source count, or answer length.
- Give A1 and A2 byte-identical context, tools, authority, stopping rules, aggregate budgets, and treatment ceilings. Additional roles may divide the budget but may not enlarge it.
- Treat mechanism-model and simulation outputs as derived assertions; no proponent can alter immutable evidence, source rights, safety flags, promotion state, or protocol authorization.

## Offline execution contract

No live model, network, subscription, laboratory, or external spend is authorized. Implement the mechanism-card, proponent-report, structural-critique, admission, tournament-ledger, and adjudication schemas; extend the runner, checkpoint, replay, scorer, and hidden identity handling; and use deterministic providers/fixtures for all tests.

The design must exercise positive and negative paths for: duplicate mechanisms, identical predictions, contradictory evidence, missing falsifiers, unsupported promotion requests, null retention, open-slot admission, stale writes, cross-problem reads, budget exhaustion, provider failure, partial completion, and replay. The Phase-A manifest must hash the roster policy, prompts, schemas, scoring rules, mechanism admission rule, focus rule, and implementation before any later live call.

## Acceptance criteria

1. A versioned protocol defines mechanism cards, proponent reports, structural critiques, new-mechanism admission, typed shared memory, focus allocation, adjudication, scoring, and authority boundaries.
2. The offline A2-M runner executes isolated proponents, delayed sharing, structural audits, deterministic tournament allocation, and bounded adjudication while preserving append-only provenance and replay.
3. Every sealed case has at least two plausible mechanism entries, a null entry, and an open slot, with a recorded basis and no mechanism treated as established fact.
4. A1 and A2-M have identical aggregate resources and authority; any extra provider calls caused by orchestration are recorded as a secondary cost and cannot change the capability ceiling.
5. Blind scoring awards credit only for valid source-backed or declared-trace-backed predictions, falsifiers, contradictions, discriminators, useful uncertainty partitions, and provenance; rhetoric, consensus, and mechanism count earn no credit.
6. Tests cover proponent isolation, structural-audit visibility, open-slot admission, null retention, rival preservation, conflicting claims, duplicate/stale/cross-problem writes, focus determinism, checkpoint/resume, replay, budget guards, and prohibited promotion/authority transitions.
7. Phase A emits a complete hash manifest, mechanism-roster audit, behavior-fixture report, and explicit `MECHANISM_SOCIETY_READY`, `MECHANISM_SOCIETY_NO_GO`, or `INCONCLUSIVE_MECHANISM_DESIGN` handoff.
8. G10R Phase B remains unexecuted until this goal completes; completion does not authorize production adoption, scientific promotion, lab work, or a general-purpose agent framework.

## Expected implementation surface

- `schemas/mechanism-card.schema.json`, `mechanism-proponent-report.schema.json`, `structural-critique.schema.json`, `mechanism-admission.schema.json`, and tournament-ledger additions;
- `src/roman_concrete_lab/agents/investigation.py` or a bounded successor with explicit A1/A2-M treatment identities;
- deterministic fixtures and tests under `fixtures/investigation/` and `tests/agents/`;
- `docs/protocols/active-investigation-pilot.md` amended to a new protocol version only after the offline contract passes;
- `artifacts/goals/G10M/phase-a.json`, behavior matrix, and criterion-mapped report.

## Stop conditions

Stop with `MECHANISM_SOCIETY_NO_GO` if proponents cannot be kept distinct from structural auditors, the null/open slot cannot be preserved, or the tournament rewards advocacy rather than testable contributions. Stop with `INCONCLUSIVE_MECHANISM_DESIGN` for incomplete traces, non-replayable state, failed budget equality, or unresolved authority boundaries. Do not activate G10R Phase B on a partial design.
