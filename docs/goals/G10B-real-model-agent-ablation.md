# G10B — Capped real-model agent-society signal pilot

**Status:** complete
**Dependencies:** G09 complete; G10 complete; owner-authorized OpenAI API treatment with a hard $25 estimated-cost cap, runtime-only credential, repository-local prompt/output traces, and `store=false`
**Advances:** determines whether a real-model agent society shows enough task-level signal over a strong single-agent control to justify an adoption-grade factorial evaluation

## Why this goal exists

G10 established closed-world authority, memory, replay, and focus contracts, but its deterministic role simulator inherited control outcomes, evaluated a ceilinged control, and produced near-identical proposals. Its recorded fixture result rejects that prototype only. G10B is a new, estimable evaluation; it must not reuse G10's sealed cases or interpret its outcome as evidence about real-model systems.

## Objective

Run a preregistered, closed-world directional pilot on new non-ceiling tasks. Determine whether an independently prompted three-role society plus adjudicator produces at least one blinded, decision-relevant improvement over a strong single-agent treatment under an equal aggregate output-token budget. This goal decides whether a full factorial evaluation is warranted; it cannot adopt an agent layer for production.

The output is a narrowly scoped adoption or rejection by task. It grants no scientific, source-adjudication, safety, laboratory, network, or external-communication authority.

## Two-phase execution contract

### Phase A — no model calls

Freeze the case packets, development/sealed split, rubric, prompts, role contracts, output schema, deterministic C0 baseline, C1/C4-lite orchestrator, de-identification mapping, objective scorer, provider fixtures, API budget estimator, and hard pre-call cost guard. Phase A must pass offline tests before the first live request. Fixture responses validate plumbing only and never count as treatment evidence.

### Phase B — capped OpenAI pilot

Use the Responses API with `gpt-6-luna`, `reasoning.effort=low`, `store=false`, no tools, no retrieval, and the frozen structured-output contract. Run the smallest informative comparison first: four sealed cases, one C1 execution per case, three independent C4-lite role executions per case, and one C4-lite adjudication per case. That is 20 treatment calls. Do not run model judging in the initial pilot; use the frozen deterministic rubric and emit a blinded packet for optional human review.

Before every request, estimate the maximum cumulative cost using current configured input/output rates and declared token ceilings. Stop before a request that could take estimated cumulative cost above $25. Record actual token usage and estimated actual cost from response usage; credentials and key material are never logged.

## Required pilot treatments

All treatments receive byte-identical versioned context cards, frozen evidence packets, schemas, callable tools, budgets, stopping conditions, and output contracts. The only differences are the explicitly named orchestration layers.

| Arm | Treatment | Layer observed |
|---|---|---|
| C0 | G09 deterministic workflow | non-agent floor |
| C1 | one configured model, one bounded analyst role | model reasoning |
| C4-lite | three independently prompted specialist roles plus one bounded adjudicator reading only their typed outputs | role diversity, critique, and selection as one combined signal |

Use the same model, reasoning policy, context, output schema, evidence, tools, and authority for C1 and C4-lite. C1 receives an output-token ceiling equal to the sum of the three role ceilings plus the adjudicator ceiling. No treatment may receive open-web retrieval, a different evidence packet, arbitrary code execution, or different scientific authority. C2, C3, repeated seeds, model judges, and broader cases belong to G10C only if this pilot warrants escalation.

## Evaluation tasks and cases

Before any treatment is run, create a new versioned manifest with at least two development cases and exactly four sealed pilot cases: one each for (a) contradiction triage, (b) rival-hypothesis generation, (c) discriminating-experiment selection, and (d) provenance/unsupported-claim detection. Cases must have deliberate headroom: C0 cannot receive a perfect primary score on every sealed case under the frozen rubric. Offline negative fixtures separately exercise malformed output, provider unavailable, stale context, duplicate call, budget exhaustion, and unsupported authority.

Development cases are isolated from the sealed manifest. The protocol permits a finite, recorded development budget followed by one frozen treatment configuration. Any change to prompts, roles, memory rules, focus policy, provider, rubric, case selection, or budget after sealed scoring begins invalidates the run and requires a new protocol version and sealed case set.

## Roles, memory, and tournament requirements

- Each specialist role has a declared, task-relevant prior and distinct output obligation. For example: evidence skeptic identifies missing support and contradictions; mechanism proposer supplies falsifiable causal accounts; transfer analyst separates direct support from analogy; experimental designer nominates discriminating measurements; safety/provenance reviewer vetoes unsupported promotion.
- Independent-generation rounds precede critique. Critique records the specific claim, evidence locator, predicted observation, and disconfirming observation it challenges.
- Immutable evidence memory is read-only. Derived hypotheses, critiques, episodic traces, and focus decisions are typed, context-scoped, source-located, and append-only. Consensus never promotes a hypothesis; promotion remains `REVIEW_REQUIRED`.
- C4's focus manager records a deterministic next-action rationale from uncertainty, expected information value, feasibility, risk, remaining budget, and the relevant evidence/hypothesis IDs; it must abstain when that contract is unsatisfied.
- The protocol must include conflict, stale-context, duplicate-write, cross-problem-memory-leakage, and resume/replay cases.

## Blind scoring and preregistered decision

Score de-identified outputs using a frozen deterministic rubric, without treatment identity or model/provider metadata. The primary score is required-element coverage constrained by valid evidence locators and absence of prohibited claims. Secondary measures are provenance completeness, unsupported-claim rate, contradiction coverage, distinct prediction count, abstention quality, constraint/safety violations, role-output distinctness, estimated cost, and latency. The report must expose the rubric hits so a human can audit whether the directional result is credible.

The protocol must predefine one of these directional outcomes:

- `ESCALATE_TO_G10C_FULL_EVALUATION` only if C4-lite exceeds C1 on at least one sealed case by at least one rubric point, is noninferior overall, introduces at least one supported distinct prediction or discriminator absent from C1, and has zero critical provenance/safety/authority failures.
- `DO_NOT_ESCALATE_AGENT_SOCIETY` if C4-lite shows no qualifying incremental contribution or commits a critical failure. This is a decision not to fund the larger experiment, not a universal rejection of agent societies.
- `INCONCLUSIVE_G10B_EVALUATION` only for an evaluation failure, such as unavailable configured provider, insufficient blinded scoring reliability, invalidated sealed cases, missing cost trace, or critical policy breach. It is not a performance outcome.

No G10B outcome authorizes production adoption. `ESCALATE` creates G10C for repeated runs and individual C2/C3 layer ablations; every other outcome leaves the non-agent G09 release authoritative.

## In scope

- provider-swappable, least-privilege model adapter with recorded fixtures for tests and credentials only at runtime;
- versioned prompts, model IDs, temperature/seeds, context/token/tool budgets, tool inputs/outputs, cost, latency, and retry policy;
- new sealed/development case manifests and blind scoring ledger;
- C0, C1, and C4-lite implementations, typed memory, role contracts, adjudication trace, checkpoint/resume, and replay artifacts;
- deterministic fixture tests plus a configured-provider execution mode activated only by the owner;
- directional signal report stating whether a full factorial ablation is justified.

## Excluded

Open-web retrieval, Sci-Hub or access-control bypass, source promotion, arbitrary code execution, agent-selected provider/model changes, hidden prompt tuning on sealed cases, external messaging, physical execution, laboratory authorization, and a general-purpose agent framework release.

## Authority boundaries

The configured provider may receive only the explicitly approved frozen case packet and runtime credentials. Prompts must prohibit treating model output as empirical evidence. Agents may write derived records only; they may not modify immutable evidence, safety flags, protocol authorization, source-rights records, or empirical measurements. Network is denied except the configured model endpoint; no retrieved content is accepted through that endpoint.

## Expected implementation surface

- `src/roman_concrete_lab/agents/providers/`, `src/roman_concrete_lab/agents/pilot.py`, and typed pilot state;
- `schemas/agent-run.schema.json`, role/hypothesis/critique/focus schemas, and provider-trace schema;
- `fixtures/agents/g10b/`, `tests/agents/`, and recorded provider fixtures;
- `docs/protocols/g10b-real-model-ablation.md`, blinded rubric, and scoring ledger;
- `artifacts/goals/G10B/run.json`, `artifacts/goals/G10B/report.md`, and cost/latency manifest.

Adding LangGraph or another framework requires a decision record showing that the required checkpoint, state, replay, and authority properties cannot be met by the existing bounded orchestrator.

## Acceptance criteria

1. Phase A freezes and hashes the protocol, prompts, rubric, schema, and new development/sealed manifests before any sealed provider call; C0 has nonzero headroom.
2. C1 and C4-lite receive identical evidence, schemas, aggregate output-token budgets, tools, stopping conditions, and authority.
3. Four sealed cases complete the declared 20-call pilot, or the run fails closed before the $25 estimated-cost cap with an attributable terminal state; every call has fresh context and a replayable trace without credential material.
4. Roles exhibit distinguishable task-relevant behavior: role outputs, predictions, critiques, and disconfirmers cannot all collapse to the same derived assertion without an explicit failure result.
5. Blind deterministic scoring records the de-identification mapping separately, primary/secondary rubric hits, the frozen escalation margin, and an audit-ready packet; no model judges are used in the initial pilot.
6. Memory rejects untyped, unsupported, stale, cross-context, duplicate, and immutable-evidence writes; all accepted derived mutations have role, source, and promotion state.
7. Tests cover provider-unavailable, malformed tool/model output, partial failure, duplicate call, checkpoint/resume, budget exhaustion, unsafe/unsupported request, conflicting write, stale context, and replay.
8. The focus manager either emits a reproducible rationale with bounded inputs or abstains; the tournament cannot promote on consensus alone.
9. The final report emits exactly one preregistered directional decision and distinguishes an evaluation failure from a decision not to fund the larger factorial.
10. No result broadens scientific, source-adjudication, safety, laboratory, or external-communication authority; the report records all model/provider/prompt/policy/case/rubric hashes and runtime cost/latency traces.

## Verification evidence

`artifacts/goals/G10B/run.json`, `artifacts/goals/G10B/report.md`, frozen protocol/case/rubric/prompt hashes, de-identified scoring ledger and arm-map hash, deterministic provider fixtures, recorded configured-provider traces, cost/latency manifest, authority scan, and criterion-mapped tests.

## Stop conditions

Stop and emit `INCONCLUSIVE_G10B_EVALUATION` if the approved provider cannot be called or traced, sealed-case integrity or blind scoring fails, or the next request could exceed the $25 estimated-cost cap. Stop and emit `DO_NOT_ESCALATE_AGENT_SOCIETY` if C4-lite shows no qualifying contribution or commits a critical authority/provenance failure. Do not add repetitions or treatments inside G10B; a positive signal must route to a separately frozen G10C.
