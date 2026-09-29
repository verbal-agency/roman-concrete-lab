# G10 — Evaluate bounded agentic orchestration

**Status:** proposed and optional  
**Dependencies:** G09 complete  
**Advances:** answers whether a bounded agent society improves the frozen workflow rather than assuming that multiple agents, shared memory, or hypothesis competition add value

## Objective

Build the smallest bounded agent-society prototype necessary for a fair factorial comparison with deterministic orchestration, then issue task-specific ADOPT or REJECT decisions using preregistered metrics.

## In scope

- tasks where orchestration may plausibly help: evidence query formulation, contradiction triage, hypothesis-table completion, or experiment-set explanation;
- explicit roles with declared priors/biases, such as evidence skeptic, mechanism proposer, transfer analyst, experimental designer, and safety/provenance reviewer;
- MemGPT-inspired tiered memory management, with immutable evidence memory, typed derived hypothesis memory, private episodic traces, and a scoped working context;
- a hypothesis-tournament protocol in which agents propose predictions, critique rivals, identify disconfirming evidence, and nominate discriminating experiments;
- a focus manager that allocates retrieval/analysis/experiment budget using uncertainty, information value, feasibility, and risk;
- context-card loading and validation before any agent action, plus context-scoped memory isolation across problems;
- identical frozen evidence packets, tools, schemas, budgets, and stopping conditions for both treatments;
- deterministic orchestrator control, optional non-agent heuristic control, and agent treatment;
- repeated agent runs across recorded cases;
- prompt/model/version/temperature/tool-call/cost/latency traces;
- blind scoring rubric and critical safety/provenance thresholds;
- checkpoint/resume, duplicate call, budget exhaustion, invalid tool output, and unsupported-request behavior;
- shared-memory concurrency, stale-context detection, conflicting hypothesis writes, promotion/rejection rules, and cross-problem memory-leakage cases;
- provider-swappable adapter only if more than one configured provider is actually needed.

## Excluded

Open-web autonomy, arbitrary code execution, changing scientific records without review, giving the agent extra evidence/tools, production LangGraph adoption before the verdict, and tuning on the sealed evaluation cases.

## Required state machine

`created -> context_loaded -> evidence_frozen -> proposing -> critiquing -> adjudicating -> selecting -> awaiting_review | completed | failed | budget_exhausted`

Only a human review action can move `awaiting_review` to `completed`. Terminal states are immutable. Replaying a completed run returns its artifact, not a second mutation. Agent writes to immutable evidence memory are illegal; derived writes must carry role, hypothesis, source, and promotion status.

## Primary metrics

- task accuracy under the blind rubric;
- unsupported-claim rate;
- provenance completeness;
- constraint/safety violations;
- stability across repeated runs;
- hypothesis diversity, prediction distinctness, contradiction coverage, tournament stability, and experiment-selection value;
- shared-memory provenance, write conflicts, cross-problem contamination, and context-constraint compliance;
- cost and latency.

The adoption rule and noninferiority/superiority margins must be frozen before treatment results are inspected.

## Expected implementation surface

`src/roman_concrete_lab/agents/`, `src/roman_concrete_lab/memory/`, `src/roman_concrete_lab/hypotheses/`, `fixtures/agents/`, `tests/agents/`, `docs/protocols/agent-evaluation.md`, `docs/reports/agent-ablation.md`. LangGraph is allowed only if the prototype's state requirements justify it in a decision record.

## Acceptance criteria

1. Controls and agent society receive byte-identical evidence, equivalent callable capabilities, and identical budgets.
2. Evaluation cases are sealed before prompt/treatment tuning and replay with recorded tool fixtures.
3. At least the preregistered number of stochastic repetitions is completed without cross-run state contamination.
4. Any fabricated measurement, source, or expert approval is a critical failure and forces REJECT.
5. Metrics include accuracy, unsupported claims, provenance, constraint violations, stability, cost, and latency with uncertainty.
6. Checkpoint, replay, duplicate-call, malformed-tool, partial-failure, budget, and stop behavior have named tests.
7. The shared-memory protocol rejects untyped or unsupported writes, preserves immutable evidence, and records all hypothesis/episodic mutations.
8. The hypothesis tournament compares independently biased roles using explicit predictions and disconfirming evidence; consensus alone cannot promote a hypothesis.
9. The focus manager emits a reproducible next-action rationale or abstains when the context, support, or utility contract is insufficient.
10. The report emits task-specific `ADOPT_AGENT_SOCIETY_FOR_<TASKS>` or `REJECT_AGENT_SOCIETY`; adoption cannot broaden scientific or physical authority.
11. The run manifest records the frozen focus/promotion policy version and fails closed if either policy is missing, stale, or contradicted by an agent action.

## Verification evidence

`artifacts/goals/G10/report.md`, frozen protocol hash, run manifests, blinded scores, statistical comparison, failure examples, cost/latency report, and adoption decision.

## Stop conditions

Reject rather than iterate indefinitely when the frozen budget is exhausted. A future evaluation requires a versioned protocol and a new sealed case set.
