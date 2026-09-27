# G10 — Evaluate bounded agentic orchestration

**Status:** proposed and optional  
**Dependencies:** G09 complete  
**Advances:** answers whether an agent improves the frozen workflow rather than assuming it does

## Objective

Build the smallest bounded agent prototype necessary for a fair factorial comparison with deterministic orchestration, then issue an ADOPT or REJECT decision using preregistered metrics.

## In scope

- tasks where orchestration may plausibly help: evidence query formulation, contradiction triage, hypothesis-table completion, or experiment-set explanation;
- identical frozen evidence packets, tools, schemas, budgets, and stopping conditions for both treatments;
- deterministic orchestrator control, optional non-agent heuristic control, and agent treatment;
- repeated agent runs across recorded cases;
- prompt/model/version/temperature/tool-call/cost/latency traces;
- blind scoring rubric and critical safety/provenance thresholds;
- checkpoint/resume, duplicate call, budget exhaustion, invalid tool output, and unsupported-request behavior;
- provider-swappable adapter only if more than one configured provider is actually needed.

## Excluded

Open-web autonomy, arbitrary code execution, changing scientific records without review, giving the agent extra evidence/tools, production LangGraph adoption before the verdict, and tuning on the sealed evaluation cases.

## Required state machine

`created -> running -> awaiting_review | completed | failed | budget_exhausted`

Only a human review action can move `awaiting_review` to `completed`. Terminal states are immutable. Replaying a completed run returns its artifact, not a second mutation.

## Primary metrics

- task accuracy under the blind rubric;
- unsupported-claim rate;
- provenance completeness;
- constraint/safety violations;
- stability across repeated runs;
- cost and latency.

The adoption rule and noninferiority/superiority margins must be frozen before treatment results are inspected.

## Expected implementation surface

`src/roman_concrete_lab/agents/`, `fixtures/agents/`, `tests/agents/`, `docs/protocols/agent-evaluation.md`, `docs/reports/agent-ablation.md`. LangGraph is allowed only if the prototype's state requirements justify it in a decision record.

## Acceptance criteria

1. Controls and agent receive byte-identical evidence, equivalent callable capabilities, and identical budgets.
2. Evaluation cases are sealed before prompt/treatment tuning and replay with recorded tool fixtures.
3. At least the preregistered number of stochastic repetitions is completed without cross-run state contamination.
4. Any fabricated measurement, source, or expert approval is a critical failure and forces REJECT.
5. Metrics include accuracy, unsupported claims, provenance, constraint violations, stability, cost, and latency with uncertainty.
6. Checkpoint, replay, duplicate-call, malformed-tool, partial-failure, budget, and stop behavior have named tests.
7. The report emits `ADOPT_AGENT_FOR_<TASKS>` or `REJECT_AGENT`; adoption is task-specific and cannot broaden authority.

## Verification evidence

`artifacts/goals/G10/report.md`, frozen protocol hash, run manifests, blinded scores, statistical comparison, failure examples, cost/latency report, and adoption decision.

## Stop conditions

Reject rather than iterate indefinitely when the frozen budget is exhausted. A future evaluation requires a versioned protocol and a new sealed case set.

