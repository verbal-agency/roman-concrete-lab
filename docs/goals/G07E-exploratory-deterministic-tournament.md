# G07E — Exploratory deterministic hypothesis tournament

**Status:** proposed  
**Dependencies:** GP4 complete; G00 `EXPLORATORY_PLATFORM` track  
**Advances:** turns the validated non-agent substrate into a replayable tournament-style discovery loop without requiring a model, lab, network, or agent runtime

## Objective

Implement the smallest deterministic tournament that proposes, critiques, compares, focuses, and conditionally promotes problem-specific hypotheses and experiment questions using the frozen GP4 cards and offline evidence fixtures.

This is the first true discovery-platform goal. It evaluates whether structured hypothesis competition adds value beyond a flat candidate list. It does not claim that a material works.

## In scope

- append-only typed hypothesis registry with evidence locators, rival links, prediction distinctness, and legal statuses;
- immutable evidence memory, typed hypothesis memory, and untrusted notes with explicit read/write permissions;
- deterministic proposal/critique/adjudication tournament over a frozen context and evidence manifest;
- focus policy for allocating bounded analysis attention across uncertainty, counterevidence, novelty, feasibility, risk, and information value;
- promotion/retraction policy from observation to derived assertion, hypothesis status, and experiment recommendation;
- qualitative discrimination and coverage scoring with separate utility dimensions and Pareto output;
- deterministic abstention for unsupported, contradictory, malformed, unsafe, and out-of-domain inputs;
- replay, duplicate-call, sensitivity, and budget-exhaustion behavior across the Roman, lime-mortar, and battery-cathode fixtures.

## Excluded

LLM calls, agent society, autonomous browsing, predictive performance modeling, numeric expected information gain without validated predictive distributions, physical execution, recipe invention, safety approval, partner contact, and cross-domain performance comparison.

## Canonical contracts

### Hypothesis registry

Each record contains `hypothesis_id`, `problem_id/version`, intervention, comparator, applicable domain, predicted observation, rival hypothesis IDs, evidence memory IDs, claim type, uncertainty, status, and promotion/retraction reason. Legal statuses are `HYPOTHESIS`, `SUPPORTED_WITHIN_CONTEXT`, `NARROW_USE_CASE`, `CONTRADICTED`, `RETIRED`, `REVIEW_REQUIRED`, and `ABSTAIN`.

No hypothesis may be promoted without evidence locators, a distinguishable prediction, a rival or explicit unresolved rival state, and the applicable reviewer authority. Immutable evidence cannot be written by the tournament.

### Tournament stages

1. **Propose:** enumerate hypotheses from the frozen card and evidence memory.
2. **Critique:** require a disconfirming observation, confounder check, and cheapest useful discriminator.
3. **Adjudicate:** score evidence coverage, contradiction handling, prediction distinctness, feasibility, uncertainty, and risk using deterministic rules.
4. **Focus:** allocate the declared local budget to unresolved hypotheses or abstain.
5. **Promote/retract:** emit a conditional hypothesis or experiment recommendation; never convert a note or unsupported claim into evidence.

### Focus and promotion policies

The implementation must freeze the focus and promotion policies before ranking. A focus decision must record its reason, budget consumed, candidates considered, and abstention condition. Promotion requires a legal transition, provenance, reviewer role, contradiction handling, retraction path, and context-amendment rule. Policies are repository contracts, not agent prompts.

## Deterministic behavior matrix

| Input condition | Required output |
|---|---|
| Complete in-domain card and rival predictions | Ranked or Pareto hypothesis/experiment set with evidence and uncertainty |
| No defensible single utility | `PARETO_SET`; no forced winner |
| Missing provenance, comparator, endpoint, or authority | `REVIEW_REQUIRED` or `ABSTAIN` with named reason |
| Contradictory evidence | Preserve both records; emit contradiction status and focus reason |
| Unsupported or out-of-domain candidate | `ABSTAIN`; never score as performance evidence |
| Unsafe or forbidden combination | Reject before scoring |
| No feasible candidate under declared constraints | `NO_FEASIBLE_CANDIDATE` with evidence |
| Repeated identical replay | Byte-equivalent output and policy hash |
| Budget exhaustion | `BUDGET_EXHAUSTED` with partial manifest; no scope widening |

## Expected implementation surface

- `schemas/hypothesis-registry.schema.json`;
- `schemas/tournament-result.schema.json`;
- `docs/protocols/hypothesis-tournament.md`;
- `tools/tournament/replay.py` and deterministic policy module;
- `fixtures/tournament/` covering positive, contradictory, malformed, partial, unsupported, unsafe, no-feasible, and budget-exhaustion cases;
- `tests/tournament/test_replay.py`;
- `artifacts/goals/G07E/run.json` and `artifacts/goals/G07E/report.md`.

Equivalent paths require an amendment before implementation. Do not create `agents/`, add a live LLM dependency, or introduce a database/vector store in this goal.

## Authority and side-effect boundaries

Repository artifacts and sealed fixtures only. No network, credentials, model calls, subprocesses, external messages, partner contact, laboratory execution, safety approval, or mutation of immutable evidence. The tournament may recommend a question or experiment; only a later qualified review can authorize physical work.

## Acceptance criteria

1. Every fixture hypothesis satisfies the typed registry contract and replays from a frozen card/evidence manifest.
2. Evidence, hypothesis, and untrusted-note memory tiers enforce their write permissions and preserve provenance.
3. Focus and promotion policies are versioned, hashed, and tested for legal transitions, abstention, contradiction, retraction, and context amendment.
4. The tournament produces deterministic ranked/Pareto/abstention outputs with separate utility components; no universal best claim is emitted.
5. Unsupported, contradictory, malformed, partial, unsafe, no-feasible, duplicate-replay, and budget-exhaustion fixtures pass their prescribed behavior.
6. Numeric EIG is absent unless predictive and observation distributions are explicitly validated; no performance model is introduced.
7. The report demonstrates that the same tournament contracts run across all three GP4 cards while endpoint semantics and support regions remain card-specific.

## Verification evidence

`artifacts/goals/G07E/run.json`, `artifacts/goals/G07E/report.md`, schema validation, tournament replay, policy-transition tests, fixture matrix, policy hash, and `git diff --check`.

## Criterion-to-evidence map

| Criterion | Required evidence |
|---|---|
| 1 | Registry schema validation plus positive Roman, lime-mortar, and battery-cathode replay records in `artifacts/goals/G07E/run.json` |
| 2 | Memory-tier permission tests and provenance assertions in `tests/tournament/test_replay.py` |
| 3 | Versioned policy manifest/hash and legal-transition tests covering promotion, retraction, contradiction, and context amendment |
| 4 | Tournament result schema plus ranked/Pareto replay outputs with separate utility components and no universal-best field |
| 5 | Fixture-matrix test results for unsupported, contradictory, malformed, partial, unsafe, no-feasible, duplicate, and budget-exhaustion cases |
| 6 | Schema/replay assertion that no EIG field or predictive model is emitted without the explicitly validated distribution contract |
| 7 | Cross-card replay report showing card-specific endpoint/support-region semantics and identical deterministic contracts |

## Stop conditions

Stop if memory tiers cannot prevent derived claims from becoming evidence, if focus/promotion authority remains implicit, if deterministic replay is unstable, or if a useful tournament output requires a predictive model, lab result, agent runtime, or cross-domain score.
