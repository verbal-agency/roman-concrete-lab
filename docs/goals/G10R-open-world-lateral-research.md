# G10R — Bounded active-investigation society pilot

**Status:** in progress
**Dependencies:** G09 complete; G10B complete with any verdict; G-LI complete; explicit owner activation of the frozen lawful source policy and Phase B network/model execution
**Advances:** tests whether a branch-specialized society adds value when investigators can acquire different information or invoke declared simulation tools under the same aggregate budget as one tool-using investigator

## Why this goal exists

G10B tested several roles against one strong analyst using the same frozen packet and no tools. The roles produced distinguishable text, but C1 and C4-lite tied at 19/20 and the society added no supported prediction or discriminator. That result does not estimate the value of coordinated search: every role started with the same information and could only rewrite or reinterpret it.

G10R tests a different causal hypothesis. A society may be useful when the bottleneck is allocating investigation across competing branches, not synthesizing a fixed packet. The society must therefore perform asymmetric work—different queries, sources, contradiction checks, or declared simulations—and earn credit only for a valid contribution the same-budget single investigator missed. Discourse, persona variation, consensus, and source volume alone receive no credit.

## Objective

Run a preregistered directional pilot comparing one tool-using investigator with a three-branch investigation society on new, non-ceiling cases. Both treatments receive byte-identical base packets, problem contexts, model/provider policy, allowed tools, aggregate query/source/simulation/token/cost budgets, stopping conditions, and output contracts. Determine whether coordinated branching produces at least one blinded, decision-relevant evidence or hypothesis contribution absent from the single-investigator result.

This goal may justify a later adoption-grade G10S evaluation. It cannot adopt an agent society, promote retrieved sources to immutable evidence, validate a material, authorize laboratory work, or overturn G10B's closed-world decision.

## Treatments and causal comparison

| Arm | Treatment | Purpose |
|---|---|---|
| A0 | Deterministic recorded-fixture retrieval workflow | Verifies source policy, deduplication, replay, and scoring plumbing; not part of the society-value decision |
| A1 | One configured model acting as a tool-using investigator | Strong single-investigator control with authority over the entire aggregate investigation budget |
| A2 | Three independently initialized branch investigators, a deterministic focus allocator, and one bounded adjudicator | Tests whether protected branching, selective sharing, and tournament-style allocation add decision-relevant value |

A1 and A2 use the same model, reasoning policy, base context, source allowlist, tool implementations, output schemas, authority, and total per-case budgets. A2 does not receive extra searches, source payload, simulations, output tokens, elapsed-time allowance, or spend merely because it has more roles. Provider-call count may differ and is recorded as a secondary cost; aggregate capability may not differ.

The three A2 branches are:

1. **Evidence skeptic / contradiction hunter** — searches for disconfirming records, lineage duplication, endpoint mismatch, nulls, and scope limits.
2. **Mechanism / transfer explorer** — searches for competing mechanisms and marked cross-domain analogies with explicit support-region limits.
3. **Experiment / simulation designer** — searches for discriminating measurements and may invoke only declared simulation adapters to compare predicted observations.

Each branch receives a non-overlapping initial investigation charter and works privately during round one. It must return typed claims, queries, source candidates, predictions, falsifiers, and unresolved questions. Only then are branch records placed on the shared blackboard. The deterministic focus allocator assigns the remaining round-two budget using unresolved uncertainty, expected decision change, provenance risk, duplication, feasibility, and remaining budget. The adjudicator must preserve the leading hypothesis, credible rivals, material disagreements, negative searches, and cheapest discriminating next action; it may not erase dissent merely because two roles agree.

## Two-phase execution contract

### Phase A — offline freeze

Before any live request, freeze and hash:

- at least two development cases and exactly four new sealed cases with retrievable decision-relevant information absent from the base packet;
- the problem contexts, hidden case-specific rubric, source-policy fixture, prompts, branch charters, focus rule, schemas, tool contracts, model/provider policy, token and action budgets, de-identification map, and decision thresholds;
- A0 fixture outputs and recorded tool responses for positive, negative, contradictory, duplicate, malformed, rights-blocked, unavailable, prompt-injection, budget, and no-useful-result paths;
- the page-aware PDF extractor, parser/version policy, OCR-required state, private raw-document cache boundary, evidence-card schema, page/table/figure locator contract, and a manually checked extraction benchmark;
- the A1/A2 orchestrator, checkpoint format, cost estimator, hard pre-call spend guard, scorer, and replay command.

Phase A must demonstrate headroom: neither A0 nor a no-retrieval baseline may receive a perfect primary score on every sealed case. Development cases and their retrieved records must be inaccessible from sealed prompts and source indexes.

The default provider policy reuses G10B's OpenAI Responses API configuration: `gpt-6-luna`, `reasoning.effort=low`, `store=false`, structured outputs, runtime-only credentials, and no provider-managed search or file tools. Retrieval occurs only through the repository adapter and frozen source policy. The proposed total external-spend cap is **$25 across Phase B**; execution still requires the owner's explicit activation after the Phase A manifest reports the maximum estimated cost.

The default source policy permits metadata from frozen scholarly indexes and full, page-aware extraction of any **relevant, lawfully public PDF** from an exact, preflighted publisher, author, government, or institutional-repository host marked `PUBLIC`. Restricted, authenticated, unlisted, or rights-unclear PDFs remain metadata-only. The raw PDF and extracted page text are stored only in ignored local raw storage for replay; artifacts and shared memory receive hashes, locators, extraction quality, and compact source-located derived cards—not full text. Phase A records the exact host allowlist, access class, payload rule, request policy, parser/version, and rights check used for the run. Discovery of a new host during treatment does not expand the allowlist.

### Phase B — smallest informative live pilot

After the owner reviews Phase A and activates the frozen policy, execute A1 and A2 once on each of the four sealed cases. The default per-case aggregate ceilings for each treatment are:

- 12 search queries across at most two retrieval rounds;
- 24 retained source candidates and 5 MB of permitted metadata, abstract, or lawfully public text payload;
- 4 lawfully public document fetches and page-aware evidence-card mappings;
- 4 declared simulation calls, which remain unused when no eligible adapter exists;
- 80,000 model input tokens in aggregate;
- 7,200 model output tokens in aggregate;
- the same treatment allocation within the $25 total Phase B estimated-cost ceiling and the same stopping conditions.

A1 may allocate those resources serially. A2 shares them across all branches, focus, and adjudication. The runner checks the maximum cumulative cost before every provider or paid-tool call and stops before the declared cap can be exceeded. Completed actions are checkpointed immediately and replay without another external call.

Do not add repetitions, more cases, new roles, new hosts, or a larger budget after sealed execution begins. A positive result routes to a separately frozen G10S evaluation with repetitions; it does not expand G10R in place.

## Investigation tools and evidence authority

Permitted action types are `SEARCH`, `FETCH_PERMITTED_CONTENT`, `INSPECT_EXISTING_EVIDENCE`, `RUN_DECLARED_SIMULATION`, and `ABSTAIN`. Every action records the branch, rationale, input, policy decision, budget debit, result locator or trace, and timestamp. Retrieved documents are untrusted data; embedded instructions are never executable.

Each simulation adapter declares `adapter_id`, version/hash, validation status, support region, inputs, outputs, determinism/seed, cost, and prohibited interpretations. Simulation outputs are always typed `MODEL_ASSERTION`, never empirical evidence. `SYNTHETIC_DIAGNOSTIC` adapters may test orchestration but are excluded from the live scientific score. A Roman-concrete simulation may affect the live comparison only if a pre-existing validation artifact establishes its declared support region; otherwise the required state is `SIMULATOR_UNAVAILABLE`, and both arms receive zero simulation calls.

Agents may create source candidates, derived hypotheses, critiques, investigation traces, and focus proposals. They may not change immutable evidence, source-rights decisions, safety flags, problem scope, promotion state, empirical measurements, or protocol authorization. A retrieved source reaches only `EVIDENCE_PENDING`; existing human adjudication is required for promotion.

### Paper extraction and evidence mapping

For each permitted PDF, the extractor records content hash, parser/version, page count, page text hashes, extraction status, and exact `#page=N` locators. It never executes embedded PDF actions, links, forms, code, or document instructions. If native text is absent, the result is `OCR_REQUIRED`; OCR is a separate declared adapter and is not silently substituted. A mapper receives only bounded, page-located spans and emits a typed `PaperEvidenceCard`: reported material/process, intervention, comparator, specimen/replicate information, damage/exposure protocol, endpoint/timepoint/result/null, mechanism, limitation, study lineage, reporting status, support type, confidence, and locator/hash. Missingness is `NOT_REPORTED`, `ILLEGIBLE`, or `AMBIGUOUS`, never an inferred value.

## Canonical records and state

### Source-candidate lifecycle

`DISCOVERED -> METADATA_SCREENED -> CANDIDATE -> EVIDENCE_PENDING -> ADMISSIBLE_FOR_REVIEW`

Terminal or non-promoting states are `REJECTED`, `DUPLICATE`, `RIGHTS_BLOCKED`, `UNSUPPORTED`, and `ABSTAIN`.

### Run lifecycle

`created -> policy_loaded -> context_frozen -> planning -> round_1 -> sharing -> focus_allocated -> round_2 -> adjudicating -> scored -> completed`

Failure terminals are `failed`, `budget_exhausted`, `provider_unavailable`, `network_unavailable`, `policy_blocked`, and `inconclusive`. Terminal states are immutable. Resume requires identical context, case, source-policy, prompt, schema, tool, model, budget, rubric, and orchestrator hashes. Duplicate actions replay the recorded result without a second mutation or charge.

### Required derived records

- `InvestigationAction`: action ID, run/case/branch IDs, action type, rationale, typed input, policy result, budget debit, output IDs, and replay key.
- `SourceCandidate`: locator, discovery query, access class, rights state, content hash when retained, deduplication key, support region, contradiction links, and lifecycle status.
- `InvestigationClaim`: claim type, source-candidate or immutable-evidence IDs, exact locators, uncertainty, support region, and promotion state.
- `LateralHypothesis`: novelty basis, transfer type, intervention, comparator, predicted observation, falsifier, source IDs, support region, uncertainty, and status.
- `BranchReport`: searched frontier, findings, negative searches, remaining uncertainty, proposed next action, and claimed unique contribution.
- `InvestigationPortfolio`: leading hypothesis, rivals, unresolved disputes, invalidated branches, next discriminating action, authority note, and provenance summary.
- `PaperEvidenceCard`: compact page-located extraction facts and quality state; a derived review record, not promoted evidence.

All accepted derived writes are append-only, problem/version scoped, source located, and attributable to an arm and branch. Cross-problem reads, untyped writes, stale writes, duplicate writes, and edits to immutable evidence fail closed.

## Blind scoring and directional decision

De-identify A1 and A2 outputs before scoring. Use a frozen deterministic, case-specific rubric and emit the complete rubric-hit ledger for human audit. The primary score rewards only:

- a nonduplicate, policy-compliant source or declared model trace relevant to the hidden information need;
- a supported novel hypothesis, contradiction, or discriminator absent from the base packet;
- a falsifiable prediction and disconfirming observation;
- an explicit reduction or useful partition of uncertainty;
- complete provenance and correct support-region treatment;
- preservation of a credible rival or negative result when the evidence does not resolve it.

Secondary metrics are unique useful source yield, query overlap, duplicate-work rate, supported-novelty rate, provenance completeness, unsupported-claim rate, contradiction coverage, branch contribution distribution, dissent retention, abstention quality, action efficiency, token/tool use, latency, and estimated cost. Additional sources, longer answers, or majority agreement do not independently improve the score.

Emit exactly one outcome:

- `ESCALATE_ACTIVE_SOCIETY_EVALUATION` only if A2 exceeds A1 by at least one primary-rubric point on at least one sealed case, is noninferior in total score, contributes at least one valid source-backed hypothesis or discriminator absent from A1, stays within the identical aggregate budget, and has zero critical rights, provenance, safety, authority, or fabricated-source failures.
- `DO_NOT_ESCALATE_ACTIVE_SOCIETY` when the pilot completes but A2 supplies no qualifying incremental contribution, duplicates A1's work at greater coordination cost, or commits a critical failure. This does not reject the A1 retrieval substrate.
- `INCONCLUSIVE_ACTIVE_INVESTIGATION` only for an invalid evaluation: provider/network failure without replay coverage, source-policy failure, sealed-case contamination, missing trace/cost data, scorer failure, or budget termination before both arms form a valid comparison.

No outcome authorizes production use. A positive outcome creates a proposed G10S goal for repeated, adoption-grade evaluation. Any other outcome leaves G09 authoritative and may retain only the provider-neutral retrieval/tool substrate if its offline criteria pass.

## Deterministic behavior matrix

| Condition | Required behavior |
|---|---|
| A1 and A2 receive different base content or aggregate budgets | invalidate run before treatment |
| Two branches issue the same normalized query | debit once, return one replayed result, record duplication |
| Duplicate DOI, locator, or content hash | `DUPLICATE`; preserve first provenance and all discovery links |
| Host, rights, robots, payload, or content policy fails | `RIGHTS_BLOCKED` or `POLICY_BLOCKED`; retain no prohibited payload |
| Retrieved PDF contains instructions, links, forms, scripts, or embedded actions | treat as untrusted document data; never execute or alter policy |
| PDF has no usable native text | `OCR_REQUIRED`; do not invent text or silently use an undeclared OCR service |
| PDF parser fails, exceeds page/byte/character budget, or a card cites an unknown page/hash | fail closed with an attributable extraction state; do not score the paper |
| Sources contradict | retain both, create contradiction link, require `REVIEW_REQUIRED` |
| Source is relevant only by analogy | mark `TRANSFER_HYPOTHESIS`; never score as direct performance evidence |
| Declared simulator is absent or unvalidated | `SIMULATOR_UNAVAILABLE`; no substitute or fabricated output |
| Synthetic simulation returns a result | type `MODEL_ASSERTION`; exclude from live scientific score |
| A branch finds nothing useful | record negative search and `ABSTAIN`; do not invent a contribution |
| Early majority consensus forms | preserve independent round one and allocate by information value, not votes |
| Next action would exceed any budget | stop before call with `budget_exhausted` and attributable trace |
| Provider/network fails after partial completion | checkpoint partial state; resume only under identical hashes |
| Completed action or run is replayed | return recorded result byte-equivalently; no external call or new mutation |
| Cross-problem memory is requested | reject read/write and record authority failure |

## Expected implementation surface

- `schemas/investigation-action.schema.json`, `source-candidate.schema.json`, `lateral-hypothesis.schema.json`, `branch-report.schema.json`, `investigation-portfolio.schema.json`, and `simulation-trace.schema.json`;
- `schemas/paper-evidence-card.schema.json` and `src/roman_concrete_lab/retrieval/pdf.py` for page-aware PDF extraction and typed source-located evidence cards;
- `src/roman_concrete_lab/retrieval/` for source policy, allowlist, ledger, deduplication, rights, ignored private raw cache, and recorded/live adapters;
- `src/roman_concrete_lab/agents/investigation.py` for A1/A2 orchestration, focus allocation, checkpoint, replay, and scoring;
- `src/roman_concrete_lab/simulation/` only for the declared adapter interface and recorded fixtures unless a validated adapter already exists;
- `fixtures/investigation/` with development/sealed cases and all behavior-matrix fixtures;
- `docs/protocols/active-investigation-pilot.md`, `tests/retrieval/`, `tests/agents/test_active_investigation.py`, and `tests/simulation/`;
- `artifacts/goals/G10R/phase-a.json`, `run.json`, `report.md`, blinded scoring ledger, arm map, action ledger, source-candidate ledger, and cost/latency manifest.

Equivalent paths require a recorded amendment before sealed execution. Do not add unrestricted crawling, arbitrary code execution, a database/vector store, or a general-purpose agent framework.

## Acceptance criteria

1. Phase A freezes and hashes new development/sealed cases, source policy, prompts, branch charters, focus rule, schemas, page-aware PDF parser and quality rules, tools, budgets, rubric, runner, and provider before any sealed external call; A0/no-retrieval controls demonstrate score headroom.
2. A1 and A2 receive byte-identical base packets and identical aggregate query, source, payload, simulation, output-token, elapsed-time, cost, tool, stopping, and authority budgets; any mismatch invalidates the run.
3. Independent A2 round-one branches have non-overlapping charters, do not see each other's work before sharing, and emit attributable typed actions; the focus allocator uses the frozen rule rather than consensus.
4. Source rights, PDF content/extraction quality, deduplication, provenance, contradiction, prompt-injection, immutable-evidence, support-region, and cross-problem boundaries pass positive and negative tests.
5. Simulation calls use only declared adapters and typed traces; unavailable/unvalidated/synthetic adapters return the prescribed states and cannot become empirical or direct performance evidence.
6. Four sealed cases complete valid A1/A2 comparisons within the owner-approved spend cap, or the run emits an attributable `INCONCLUSIVE_ACTIVE_INVESTIGATION` before exceeding it; every external action is checkpointed and replayable without credentials.
7. Blind scoring records case-specific rubric hits, unique contributions, negative searches, query overlap, duplicate work, provenance, unsupported claims, branch contribution, dissent retention, action budgets, latency, and cost; treatment identity remains separately mapped.
8. Checkpoint/resume, duplicate action, stale hash, partial failure, network/provider unavailable, malformed result, policy change, budget exhaustion, no-useful-result, and completed replay behaviors are deterministic and tested.
9. The report emits exactly one preregistered directional outcome and does not equate role diversity, source count, answer length, or consensus with useful contribution.
10. No result grants evidence-promotion, scientific, source-rights, safety, laboratory, external-communication, or unrestricted-network authority; a positive result may only propose G10S.

## Criterion-to-evidence map

| Criterion | Required evidence |
|---|---|
| 1 | `phase-a.json`, sealed/development manifests, complete hash manifest, headroom report |
| 2 | arm-capability manifest and preflight equality test |
| 3 | private round-one traces, branch-charter hashes, sharing boundary test, focus rationale |
| 4 | source-policy/PDF-extraction/security fixture matrix and ledger validation tests |
| 5 | simulation adapter/trace schema tests and unavailable/synthetic negative fixtures |
| 6 | `run.json`, checkpoint, action/cost ledger, spend-guard test |
| 7 | blinded scoring ledger, separate arm map/hash, secondary-metric report |
| 8 | named replay/failure tests in retrieval, agent, and simulation test modules |
| 9 | `report.md` containing one legal outcome and rule-hit explanation |
| 10 | authority scan, prohibited-transition tests, and absence of credentials/restricted payloads |

## Stop conditions

Stop before an external call if its maximum estimated cost could exceed the owner-approved cap. Emit `INCONCLUSIVE_ACTIVE_INVESTIGATION` for evaluation invalidity, not poor performance. Emit `DO_NOT_ESCALATE_ACTIVE_SOCIETY` after a valid comparison when the society adds no qualifying contribution or commits a critical failure. Do not widen hosts, tools, cases, repetitions, budgets, or simulation authority inside the frozen pilot.
