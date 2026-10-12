# Execution roadmap

## How to use this roadmap

Give one goal file at a time to the implementation agent. The agent must not start a later goal, relax a scientific gate, or silently add infrastructure. Each goal ends with a binary handoff and named evidence.

The roadmap is stage-gated. G-1 is the only eligible starting goal. The amended plan separates bounded, problem-specific exploration from predictive modeling and from work that requires an external qualified facility:

```text
G-1 -> verdict-specific G00
          |
          +-- exploration_seedability=EXPLORATION_SEEDABLE
          |       -> G00 EXPLORATORY_PLATFORM -> G-LR -> GP1 -> GP2 -> GP3 -> GP4
          |                                                    |
          |                                                    +-- G07E deterministic tournament -> G09 exploratory release -> G10 contract prototype -> optional G10B closed-world pilot -> G-LI public intake -> G10M mechanism-proponent society -> G10R-R evaluator remediation -> G10P plumbing -> G10D agent design -> optional G10R active-investigation rerun
          |                                                    +-- exploratory-only stop
          |                                                    +-- qualified partner (owner activated) -> GL1 -> GL2
          |
          +-- material candidate plausible + REPLICATION_STUDY_REQUIRED
          |       -> G00 PRELAB_REPLICATION -> G-LR -> GP1 -> GP2 -> GP3 -> GP4 -> GL1 -> GL2
          |                                      |
          |                                      +-- supported -> GD1 (conditional discovery)
          |                                      +-- narrow / null / inconclusive -> stop or revise
          |
          +-- REPLICATION_STUDY_REQUIRED without a material candidate -> evidence-gap stop
          |
          +-- EVIDENCE_SYNTHESIS_ONLY ----> G01 -> G02 -> G03 -> G04 NO-GO
          |                                                        |
          |                                                       G05A
          |                                                        |
          +-- MODELABLE_NOW -------------> G01 -> G02 -> G03 -> G04
                                                                   |
                                                      +------------+-----------+
                                                      |                        |
                                                    NO-GO                 LIMITED / GO
                                                      |                        |
                                                    G05A            G05B -> G06 -> G07 -> G08
                                                      |                                  |
                                                      +------------> G09 <---------------+
                                                                       ^
                                                                       |
                                                                      GD1
                                                                       |
                                                               G10 contract prototype
                                                                       |
                                                            optional G10B closed-world pilot
                                                                       |
                                                            optional G10R active investigation
                                                                       |
                                                                      G11
```

The diagram after G00 now has an explicit landscape-readiness stage before the exploratory and lab-dependent branches. `EXPLORATION_SEEDABLE` permits bounded candidate work, but discovery-grade hypothesis generation requires G-LR `LANDSCAPE_READY`; `LANDSCAPE_INCOMPLETE` may produce only provisional evidence-gap outputs. The pre-lab branch (`GP1`–`GP4`) may create evidence dossiers, hypotheses, study specifications, partner-readiness material, and a cross-question portfolio checkpoint without a lab, subject to that boundary. `GL1` is the external facility/safety gate; `GL2` requires returned physical results. The discovery branch (`GD1`) is unavailable until GL2 produces reproducible, comparable data. A `REPLICATION_STUDY_REQUIRED` verdict without a material candidate blocks physical planning. `EVIDENCE_SYNTHESIS_ONLY` may proceed through evidence infrastructure but cannot authorize predictive ranking merely by reaching a later goal.

G09 accepts the evidence-gap package, the completed modeling branch, a completed physical-feedback discovery loop from GD1, or the model-free G07E tournament. G10 is not eligible until G09 releases a complete non-agent package. G10 is a closed-world contract prototype; its offline fixture outcome does not estimate real-model value. G10B is the optional real-model, non-ceiling signal pilot. G-LI turns the audited public-copy routes into a reviewable, page-located local intake substrate and remediates the landscape before a live retrieval comparison. G10M is the offline design gate that adds mechanism proponents, a null mechanism, an open mechanism slot, and structural auditors to the active-investigation society. G10R-R is now mandatory after an invalid or scorer-contaminated G10R run: it repairs the open-world candidate/evidence/authority separation and replays the existing traces offline. G10P then repairs the society's evidence-bus and attribution handoffs; G10D separately redesigns role incentives, follow-up obligations, and focus/promotion behavior. Both must complete before a fresh G10R Phase-B run. G11 requires external expert review regardless of whether an agent or retrieval evaluation executes.

The agent-society progression is deliberate: G07E defines the exploratory typed hypothesis layer, shared-memory permissions, deterministic tournament, and explicitly freezes the focus and promotion layers without models or agents; G07 remains the model-branch equivalent. G09 releases that loop without agents; G10 tests the contracts with an offline fixture prototype; G10B asks whether several roles improve closed-world analysis of the same packet; G10M adds mechanism proponents and structural auditors with null/open-slot anti-anchoring; G10R-R repairs the evaluator after the first active-investigation run by separating candidate discovery, evidence validation, and authority. G10P is the plumbing gate: it verifies that candidates and contributions survive every society handoff into the score ledger. G10D is the agent-design gate: it replaces a global review panel with viewpoint-centered teams whose structural support agents compile and challenge evidence for their assigned arguments, followed by a cross-viewpoint tournament. Only then may G10R ask whether this society improves active information acquisition when a same-budget single investigator can use the same lawful tools. A G10R society must earn credit for reproducible discovery, useful hypotheses, verified evidence, or discriminators—not discourse, consensus, or mechanism advocacy—and unresolved candidates must not be discarded merely because they are not yet validated. G11 reviews any capability adopted by a later evaluation before it appears in a lab handoff.

G00 is now a problem-charter gate, not a commercialization, extraction, or agent-provider gate. It ratifies the Roman-concrete context, lawful current-plane data rights, conditional-ranking boundary, no-external-spend rule, and exploration NO-GO semantics. Commercial licensing is deferred to the GP3/G09 release decision; extraction quality thresholds apply only if the G03 branch becomes eligible; LLM/provider choices apply only at G10; and qualified scientist-of-record review is required at GL1/G11 before any physical handoff. Every G-LR and GP1–GP4 run must load the versioned context and contracts in `docs/protocols/exploration-contracts.md`; GP1 must also record the G-LR verdict and landscape manifest hash.

GP4 is the validated substrate checkpoint. G07E/G09 are the optional internal tournament and release path; GL1 is a separate physical-validation branch and is not automatically activated when GP4 completes. GL1 remains `DEFERRED_NOT_REQUESTED` until the owner explicitly authorizes facility coordination or supplies an attributable qualified facility review. Only an activated GL1 with missing external review is `BLOCKED`.

## Goals

| Goal | Objective | Depends on | Gate/output |
|---|---|---|---|
| [G-1](goals/G-1-literature-sufficiency-audit.md) | Determine whether the evidence can seed problem-specific exploration, support synthesis, or justify predictive modeling; exhaust lawful public-copy routes and quantify the value of subscription access | none | `EXPLORATION_SEEDABLE` plus conservative modelability/material verdicts and a public-access/subscription-value register |
| [G00](goals/G00-charter-and-scaffold.md) | Ratify the reusable substrate, declared problem context, and selected exploration, replication, synthesis, or modeling charter | G-1 `EXPLORATION_SEEDABLE` or complete substantive verdict | approved decision record, context contract, and selected track |
| [G-LR](goals/G-LR-landscape-readiness.md) | Establish a bounded, source-located literature landscape and evidence map before discovery-grade hypothesis generation | G00 `EXPLORATORY_PLATFORM` or `PRELAB_REPLICATION` | `LANDSCAPE_READY` or `LANDSCAPE_INCOMPLETE` verdict |
| [G-LI](goals/G-LI-public-document-ingestion.md) | Ingest audited lawfully public PDFs into a page-located review queue and rerun the landscape evidence boundary | G-LR `LANDSCAPE_INCOMPLETE`; G00 `EXPLORATORY_PLATFORM` | replayable public-document ledger and remediated landscape verdict |
| [GP1](goals/GP1-candidate-evidence-and-hypothesis-dossier.md) | Convert landscape-ready evidence into a problem-specific candidate dossier and rival-hypothesis matrix | G-LR complete; `LANDSCAPE_READY` for discovery-grade outputs | candidate dossier and hypothesis gate |
| [GP2](goals/GP2-prelab-experiment-specification.md) | Produce a provisional candidate/experiment ranking and a draft, non-authorizing study specification | GP1 | conditional ranking plus `DRAFT — EXPERT REVIEW REQUIRED` study package |
| [GP3](goals/GP3-partner-readiness-package.md) | Package a problem-specific experiment portfolio, facility requirements, data contracts, and partner-review questions | GP2 | exploratory portfolio and partner-ready handoff packet |
| [GP4](goals/GP4-cross-question-portfolio-validation.md) | Validate the reusable problem-card and portfolio substrate across the Roman case and two offline cross-domain fixtures | GP3 | cross-question portfolio validation and explicit no-go/continue decision |
| [G07E](goals/G07E-exploratory-deterministic-tournament.md) | Implement the model-free deterministic hypothesis tournament, scoped memory, focus, and promotion policies | GP4 | replayable exploratory tournament and policy manifest |
| [GL1](goals/GL1-lab-partner-and-safety-gate.md) | Obtain qualified facility feasibility and safety review before any physical execution | GP4 plus explicit owner activation or qualified facility review | approved, revised, or blocked lab gate |
| [GL2](goals/GL2-replication-result-ingestion.md) | Ingest partner results and decide whether the candidate is supported, narrow, inconclusive, or rejected | GL1 plus returned lab data | result snapshot and candidate verdict |
| [GD1](goals/GD1-conditional-discovery-loop.md) | Build a discovery loop only if replication produces sufficient comparable data | GL2 `SUPPORTED` with data threshold | conditional discovery GO/NO-GO |
| [G01](goals/G01-domain-and-evidence-contracts.md) | Implement canonical domain, evidence, provenance, and claim contracts | G00 | schema/contract conformance |
| [G02](goals/G02-corpus-protocol.md) | Produce a reproducible seed corpus and blinded screening ledger | G01 | frozen corpus manifest |
| [G03](goals/G03-extraction-benchmark.md) | Prove extraction quality on an expert-adjudicated gold set | G02 | extraction GO/NO-GO |
| [G04](goals/G04-evidence-store-and-feasibility-gate.md) | Build deterministic ingestion and issue the program feasibility verdict | G03 | NO-GO, LIMITED, or GO |
| [G05A](goals/G05A-evidence-gap-package.md) | On NO-GO, publish the evidence-gap synthesis and minimum lab study | G04 NO-GO | terminal non-model package |
| [G05B](goals/G05B-analysis-dataset.md) | On LIMITED/GO, freeze the analysis dataset and split plan | G04 LIMITED/GO | analysis-ready release |
| [G06](goals/G06-baselines-and-validation.md) | Fit honest baselines and validate by held-out study and time | G05B | model-use verdict |
| [G07](goals/G07-hypotheses-and-experiment-ranking.md) | Formalize the model-branch hypothesis registry, deterministic tournament, scoped shared memory, and rank bounded experiments | G06 (any verdict) | hypothesis/tournament contract and ranked design set |
| [G08](goals/G08-mechanistic-spike-and-synthesis.md) | Test one justified mechanistic model and synthesize without false fusion | G07 | model card and synthesis |
| [G09](goals/G09-non-agent-prelab-release.md) | Release the reproducible non-agent context, memory, hypothesis, focus, feedback, and pre-lab package | G05A, G08, GD1, or G07E | versioned non-agent release |
| [G10](goals/G10-agent-ablation.md) | Evaluate a bounded closed-world agent society against the frozen deterministic workflow | G09 | task-specific society adoption/rejection decision |
| [G10B](goals/G10B-real-model-agent-ablation.md) | Determine whether a real-model society adds decision-relevant value over one strong analyst on frozen evidence | G09 + G10; explicit owner activation of a configured model provider | directional closed-world escalation decision |
| [G10M](goals/G10M-mechanism-proponent-society.md) | Upgrade the active-investigation society with mechanism proponents, null/open-slot anti-anchoring, structural audits, and a deterministic mechanism tournament | G10R Phase A; G09 + G10B + G-LI complete | offline mechanism-society readiness or no-go handoff |
| [G10R-R](goals/G10R-R-open-world-evaluation-remediation.md) | Repair the open-world evaluator, preserve unresolved candidates and provisional hypotheses, separate discovery/evidence/authority scoring, and replay the prior G10R run offline | completed G10R run with invalid or scorer-contaminated evaluation; G10M complete | `EVALUATOR_REPAIRED_FOR_RERUN`, `OPEN_WORLD_EVALUATOR_NO_GO`, or `INCONCLUSIVE_EVALUATION_REPLAY` |
| [G10P](goals/G10P-society-evidence-plumbing.md) | Repair and verify viewpoint, support-task, candidate, claim, branch, adjudication, portfolio, and score-ledger handoffs so society contributions cannot disappear before scoring | G10R-R complete; completed G10R traces | `SOCIETY_PLUMBING_READY` or `SOCIETY_PLUMBING_NO_GO` |
| [G10D](goals/G10D-society-agent-design.md) | Redesign the society as viewpoint-centered teams with structural support agents, cross-viewpoint challenge, and adaptive focus, then test it offline under equal aggregate budgets | G10M + G10R-R complete; G10P interfaces frozen or complete | `SOCIETY_DESIGN_READY` or `SOCIETY_DESIGN_NO_GO` |
| [G10R](goals/G10R-open-world-lateral-research.md) | Compare one tool-using investigator with the amended two-layer mechanism-proponent society under identical aggregate retrieval, declared-simulation, token, and cost budgets | G10M + G10R-R + G10P + G10D complete for any rerun; G09 + G10B + G-LI; explicit source-policy/model/spend activation | directional active-investigation escalation decision |
| [G11](goals/G11-expert-handoff.md) | Obtain scientific/safety review and issue the lab handoff | G09; G10R retrieval/tool output only if included; society output only after a later adoption-grade evaluation | approved or blocked handoff |

## Program stop rules

- Stop all predictive-modeling, physical-lab, and performance-claim work when G-1 returns `AUDIT_INCOMPLETE`. If and only if `exploration_seedability=EXPLORATION_SEEDABLE`, G00 may authorize the bounded exploratory platform branch.
- G-1 cannot call a paper subscription-blocked until repository, preprint, author-manuscript, thesis/report, open-index, exact-title/DOI, and citation-chain routes are recorded as attempted. Publisher metadata alone is not an access verdict.
- G-1 must produce a named public-access register separating unavailable papers from unsearched providers and ranking any subscription or document-delivery request by expected decision value. A subscription is deferred when the inaccessible records are only contextual or method-adjacent and cannot plausibly change the gate.
- Exploratory outputs must remain `PROVISIONAL_BEST`, `HYPOTHESIS`, or `EXPERIMENT_CANDIDATE`; they may not be promoted to validated performance, a recipe, or a generalizable model.
- G-LR must precede GP1. A `LANDSCAPE_INCOMPLETE` result permits only explicitly provisional evidence-gap and candidate outputs; it cannot authorize discovery-grade hypothesis generation or a claim that the field has been mapped.
- G-LI is the public-document remediation path for a G-LR `LANDSCAPE_INCOMPLETE` exploratory program. It may make lawful public PDFs page-located and reviewable but cannot turn derived cards into immutable evidence or clear scientific-adjudication blockers by itself. G10R Phase B is deferred until G-LI completes, without changing its frozen Phase-A treatment policy.
- On G-1 `REPLICATION_STUDY_REQUIRED` with a provisional/confirmed material candidate, G00 may authorize only GP1–GP4. No physical work is authorized until GL1 passes.
- On G-1 `REPLICATION_STUDY_REQUIRED` without a material candidate, use G00 only to document the evidence gap; do not execute GP2, GL1, GL2, or G01–G10.
- GL2 must return `SUPPORTED`, `NARROW_USE_CASE`, `INCONCLUSIVE`, or `NOT_REPRODUCED`; only `SUPPORTED` with the ratified data threshold may unlock GD1.
- G07E or G07 must establish the deterministic hypothesis registry, shared-memory permissions, tournament, and focus policy before G09, G10, G10B, or G10R can claim a complete discovery loop.
- G09 must release and replay the non-agent loop before G10 introduces role-biased agents; agent society is an overlay to evaluate, not the source of scientific truth.
- G10 is a fixture-contract prototype, not evidence for or against real-model society value. G10B must use a new non-ceiling sealed case set, an actual configured model provider, blind scoring, and a same-budget single-agent control for its directional closed-world escalation decision. G10B cannot adopt a society for production.
- G10B is closed-world. Only G10R may add retrieved source candidates, and only under an activated lawful source policy. G10R must compare a single investigator and a society with the same aggregate tools and budgets; its deterministic retrieval arm verifies plumbing but does not substitute for that causal comparison.
- G10M must complete before G10R Phase B. It may change the society's orchestration and schemas, but it may not widen source policy, budgets, scientific authority, or evidence-promotion authority.
- G10R-R must complete before any G10R Phase-B rerun after an invalid or scorer-contaminated evaluation. It may repair candidate/evidence/authority semantics and scoring, preserve unattributed citations for collective adjudication, and distinguish pending claims from unauthorized transitions, but it may not add live calls, widen source policy, or promote unresolved candidates to immutable evidence.
- G10P must complete before any G10R Phase-B rerun. It is the evidence-bus gate and may repair typed joins, checkpoint serialization, candidate-ledger access, adjudication outputs, and score attribution, but may not change agent incentives, source policy, aggregate budgets, or scientific authority.
- G10D must complete before any G10R Phase-B rerun. It is the agent-design gate and may change role contracts, follow-up obligations, branch isolation, focus allocation, and adjudication preservation rules, but may not add live calls, widen source policy, increase aggregate budgets, or promote evidence.
- G10R may use only declared simulation adapters. Synthetic or unvalidated outputs remain model assertions and cannot count as empirical or direct performance evidence. A G10R result cannot promote a source candidate to immutable evidence, broaden the problem support region, authorize physical work, or bypass G11/GL1 review.
- G10 adoption is task-specific. A society may be adopted for query formulation, contradiction triage, hypothesis critique, or experiment explanation without receiving authority to alter evidence, approve safety, or run a lab.
- A single problem may have a `PROVISIONAL_BEST` candidate under declared constraints, but a global or cross-problem “best material” claim is prohibited unless the utility function, support region, and validation evidence are explicit.
- The reusable platform core should be exercised across multiple problem cards before introducing a general-purpose agent framework; Roman concrete is the first vertical slice, not the whole platform.
- G07E is the model-free exploratory tournament path; it may proceed from GP4 without a lab or predictive model. It must not be treated as physical discovery or a validated performance system.
- On G-1 `EVIDENCE_SYNTHESIS_ONLY`, prohibit predictive modeling and ranking unless a versioned evidence amendment later satisfies the frozen gate.
- Stop predictive-model work at G04 NO-GO. Execute G05A; do not continue through G05B–G07.
- Stop model-based ranking at G06 if the preregistered baseline/coverage criteria fail. Route to qualitative design mode in G07.
- Stop mechanistic integration if G08 cannot establish input availability, validity, and an observable validation target.
- Stop the G10 prototype at its frozen budget if it fails its thresholds; do not generalize its fixture result to real-model agents. A negative G10B result stops a larger closed-world society evaluation but does not answer G10R's separately preregistered active-investigation question. Stop G10M if mechanism advocacy cannot be separated from valid contributions, or if null/open-slot and rival preservation fail. Stop society escalation after G10R unless it produces a unique, source-backed contribution over the same-budget single investigator with no critical authority, rights, safety, or provenance failure.
- Stop release at G11 if qualified reviewers have not approved the protocol. A deferred or blocked review is reported; it is not converted into approval.

## Cross-cutting definition of done

Every completed goal must provide:

- a machine-readable run or decision manifest;
- tests mapped to each acceptance criterion;
- hashes/versions for input artifacts;
- deterministic output or recorded seed/model configuration;
- documentation of exclusions and discovered future work;
- no unsupported promotion of interpretations or model outputs to observations;
- no credentials, unauthorized source content, or executable instructions from documents.

## Suggested repository surface

This is a target contract, not authorization to build all of it in G00.

```text
pyproject.toml
uv.lock
src/roman_concrete_lab/
  domain/
  corpus/
  extraction/
  evidence/
  analysis/
  design/
  agents/
schemas/
data/
  manifests/
  raw/          # ignored when licensing requires
  interim/
  processed/
fixtures/
tests/
docs/
  decisions/
  protocols/
  reports/
  goals/
artifacts/      # generated, mostly ignored; releases include manifests
```

Do not introduce PostgreSQL, pgvector, a graph database, LangGraph, PyTorch, BoTorch, or a mechanistic suite until the goal that needs it demonstrates that need. Do not create a model-driven discovery layer before GL2 returns comparable physical results.
