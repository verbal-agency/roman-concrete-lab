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
          |                                                    +-- G07E deterministic tournament -> G09 exploratory release -> G10 contract prototype -> optional G10B closed-world pilot -> G-LI public intake -> G10M mechanism-proponent society -> G10R-R evaluator remediation -> G10P plumbing -> G10D agent design -> optional G10R active-investigation rerun -> G10R-P postmortem -> G10R-I offline runtime integration -> G10R-A offline acquisition redesign -> G10R-C pre-rerun constraint audit -> G10R-F fresh Phase-A freeze -> G10R-B2 post-constraint Phase-B rerun -> G10R-Q post-B2 offline failure experiments -> G10R-S remediation integration -> G10R-T research-loop repair and ablation -> G10R-U fresh Phase-A freeze -> G10R-W live-loop wiring -> G10R-X fresh Phase-A freeze -> G10R-V paid comparison -> G10R-Y offline diagnosis -> G10R-Z offline acquisition/validity repair -> G10R-AA fresh Phase-A freeze -> G10R-AB paid comparison -> G10R-AC provisional-argument/open-world intake
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

G09 accepts the evidence-gap package, the completed modeling branch, a completed physical-feedback discovery loop from GD1, or the model-free G07E tournament. G10 is not eligible until G09 releases a complete non-agent package. G10 is a closed-world contract prototype; its offline fixture outcome does not estimate real-model value. G10B is the optional real-model, non-ceiling signal pilot. G-LI turns the audited public-copy routes into a reviewable, page-located local intake substrate and remediates the landscape before a live retrieval comparison. G10M is the offline design gate that adds mechanism proponents, a null mechanism, an open mechanism slot, and structural auditors to the active-investigation society. G10R-R is now mandatory after an invalid or scorer-contaminated G10R run: it repairs the open-world candidate/evidence/authority separation and replays the existing traces offline. G10P then repairs the society's evidence-bus and attribution handoffs; G10D separately redesigns role incentives, follow-up obligations, and focus/promotion behavior. Both must complete before a fresh G10R Phase-B run. After the post-G10R-S paid comparison exposed a non-iterative fetch loop, reversed focus priority, stale post-sharing dossiers, a placeholder open slot, and replay ambiguity, G10R-T became the mandatory offline repair-and-ablation gate before any further Phase-A freeze. G11 requires external expert review regardless of whether an agent or retrieval evaluation executes.

The agent-society progression is deliberate: G07E defines the exploratory typed hypothesis layer, shared-memory permissions, deterministic tournament, and explicitly freezes the focus and promotion layers without models or agents; G07 remains the model-branch equivalent. G09 releases that loop without agents; G10 tests the contracts with an offline fixture prototype; G10B asks whether several roles improve closed-world analysis of the same packet; G10M adds mechanism proponents and structural auditors with null/open-slot anti-anchoring; G10R-R repairs the evaluator after the first active-investigation run by separating candidate discovery, evidence validation, and authority. G10P is the plumbing gate: it verifies that candidates and contributions survive every society handoff into the score ledger. G10D is the agent-design gate: it replaces a global review panel with viewpoint-centered teams whose structural support agents compile and challenge evidence for their assigned arguments, followed by a cross-viewpoint tournament. G10R-S integrated a controlled remediation but its next paid run showed that record connectivity was not enough: research must be iterative, later evidence must revise dossiers, focus must spend on the highest-value work, and the open slot must actually generate an evidence-conditioned rival. G10R-T repairs those behaviors and ablates shared support, viewpoint diversity, and adaptive discovery under equal actual offline budgets. Only a positive G10R-T handoff may justify proposing another fresh Phase-A freeze. A G10R society must earn credit for reproducible discovery, useful hypotheses, verified evidence, or discriminators—not discourse, consensus, or mechanism advocacy—and unresolved candidates must not be discarded merely because they are not yet validated. G11 reviews any capability adopted by a later evaluation before it appears in a lab handoff.

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
| [G10R-P](goals/G10R-P-society-postmortem-and-target-state.md) | Diagnose the completed G10R result, separate design/integration/acquisition/scoring weaknesses, and define the measurable society target state before another paid test | G10R complete with `DO_NOT_ESCALATE_ACTIVE_SOCIETY`; no new external calls | `TARGET_STATE_READY_FOR_OFFLINE_BUILD`, `POSTMORTEM_NO_GO`, or `INCONCLUSIVE_POSTMORTEM` |
| [G10R-I](goals/G10R-I-offline-runtime-integration.md) | Integrate the G10D viewpoint society and G10P evidence bus into the investigation runner and verify topology, open-slot, acquisition, budget, authority, and replay invariants offline | G10R-P `TARGET_STATE_READY_FOR_OFFLINE_BUILD`; G10D + G10P complete | `RUNTIME_INTEGRATION_READY`, `RUNTIME_INTEGRATION_NO_GO`, or `INCONCLUSIVE_RUNTIME_INTEGRATION` |
| [G10R-A](goals/G10R-A-offline-acquisition-redesign.md) | Test whether explicit viewpoint support obligations and information-seeking focus can convert the integrated society from discourse into attributable evidence acquisition | refreshed G10R-P postmortem; G10R-I `RUNTIME_INTEGRATION_READY` | `ACQUISITION_DESIGN_READY`, `ACQUISITION_DESIGN_NO_GO`, or `INCONCLUSIVE_ACQUISITION_DESIGN` |
| [G10R-C](goals/G10R-C-pre-rerun-constraint-audit.md) | Audit and remediate accidental constraints across prompts, schemas, task/focus policy, locator/retrieval, source policy, joins, runtime, budgets, replay, and scoring before another paid society evaluation | G10R-A complete; refreshed G10R rerun with `DO_NOT_ESCALATE_ACTIVE_SOCIETY`; no new external calls | `PRE_RERUN_CONSTRAINTS_READY`, `PRE_RERUN_CONSTRAINTS_NO_GO`, or `INCONCLUSIVE_CONSTRAINT_AUDIT` |
| [G10R-F](goals/G10R-F-fresh-phase-a-freeze.md) | Freeze a distinct Phase-A manifest after constraint remediation without overwriting historical run artifacts | G10R-C `PRE_RERUN_CONSTRAINTS_READY`; no paid activation | `PHASE_A_READY_FOR_OWNER_ACTIVATION`, `PHASE_A_FREEZE_NO_GO`, or `INCONCLUSIVE_PHASE_A_FREEZE` |
| [G10R-B2](goals/G10R-B2-post-constraint-active-rerun.md) | Run one separately authorized post-remediation A1 versus A2-M Phase-B comparison under the fresh manifest and frozen $25 cap | G10R-F `PHASE_A_READY_FOR_OWNER_ACTIVATION`; explicit owner/provider/network activation | `ESCALATE_ACTIVE_SOCIETY_EVALUATION`, `DO_NOT_ESCALATE_ACTIVE_SOCIETY`, or `INCONCLUSIVE_ACTIVE_INVESTIGATION` |
| [G10R-Q](goals/G10R-Q-post-b2-postmortem.md) | Experiment on the society's evidence-acquisition failures with controlled offline interventions, then retain only fixes that improve attributable acquisition under equal budgets | G10R-B2 `DO_NOT_ESCALATE_ACTIVE_SOCIETY`; no external calls | `SOCIETY_REMEDIATION_READY` or `INCONCLUSIVE_SOCIETY_REMEDIATION` |
| [G10R-S](goals/G10R-S-offline-remediation-integration.md) | Integrate the winning G10R-Q treatment into the actual A2-M runner and verify acquisition, support-task, locator, deduplication, open-slot, budget, authority, and replay behavior offline | G10R-Q `SOCIETY_REMEDIATION_READY`; no external calls | `RUNTIME_REMEDIATION_READY` or `INCONCLUSIVE_RUNTIME_REMEDIATION` |
| [G10R-T](goals/G10R-T-society-research-loop-ablation.md) | Repair the society's iterative research, focus, dossier-revision, open-slot, replay, and typed-scoring behavior, then ablate each society layer under equal actual offline budgets | G10R-S `RUNTIME_REMEDIATION_READY`; post-G10R-S paid comparison `DO_NOT_ESCALATE_ACTIVE_SOCIETY`; no external calls | `SOCIETY_RESEARCH_LOOP_READY`, `SOCIETY_RESEARCH_LOOP_NO_GO`, or `INCONCLUSIVE_SOCIETY_RESEARCH_LOOP` |
| [G10R-U](goals/G10R-U-fresh-phase-a-freeze-after-loop-repair.md) | Freeze a distinct Phase-A manifest containing the G10R-T research loop and record a separately reviewable owner activation request | G10R-T `SOCIETY_RESEARCH_LOOP_READY`; no paid activation | `PHASE_A_READY_FOR_OWNER_ACTIVATION`, `PHASE_A_FREEZE_NO_GO`, or `INCONCLUSIVE_PHASE_A_FREEZE` |
| [G10R-W](goals/G10R-W-live-research-loop-wiring.md) | Wire the G10R-T research-loop contracts into the live A2-M runner and verify selection-gated acquisition, dossier revision, focus, open-slot, checkpoint, and replay behavior offline | G10R-T complete; no external calls | `RUNTIME_RESEARCH_LOOP_WIRED` or `INCONCLUSIVE_RUNTIME_WIRING` |
| [G10R-X](goals/G10R-X-fresh-phase-a-freeze-after-wiring.md) | Freeze a distinct Phase-A manifest after live research-loop wiring without mutating G10R-U | G10R-W `RUNTIME_RESEARCH_LOOP_WIRED`; no paid activation | new owner-activation-ready manifest or freeze no-go |
| [G10R-V](goals/G10R-V-post-freeze-active-rerun.md) | Run the separately authorized A1 versus A2-M comparison using the post-wiring manifest and repaired research loop | G10R-X complete; explicit owner/provider/network activation | `ESCALATE_ACTIVE_SOCIETY_EVALUATION`, `DO_NOT_ESCALATE_ACTIVE_SOCIETY`, or `INCONCLUSIVE_ACTIVE_INVESTIGATION` |
| [G10R-Y](goals/G10R-Y-post-v-paid-run-diagnostic.md) | Diagnose the post-wiring paid comparison and run offline ablations to separate agent-design, acquisition, attribution, scoring, and overhead failures | G10R-V `DO_NOT_ESCALATE_ACTIVE_SOCIETY`; no external calls | `POST_V_DIAGNOSIS_READY`, `POST_V_DIAGNOSIS_NO_GO`, or `INCONCLUSIVE_POST_V_DIAGNOSIS` |
| [G10R-Z](goals/G10R-Z-acquisition-headroom-and-society-validity.md) | Repair shared metadata-to-content acquisition, delayed open-viewpoint admission, need-driven support, and scorer parity, then prove the treatment with arm-neutral offline fixtures | G10R-Y `POST_V_DIAGNOSIS_READY`; no external calls | `ACQUISITION_HEADROOM_READY`, `ACQUISITION_HEADROOM_NO_GO`, or `INCONCLUSIVE_ACQUISITION_HEADROOM` |
| [G10R-AA](goals/G10R-AA-fresh-phase-a-freeze-after-acquisition-headroom.md) | Wire the additive acquisition/headroom and delayed-admission contracts into a live-capable entrypoint, then freeze a distinct Phase-A manifest and record a pending owner activation request | G10R-Z `ACQUISITION_HEADROOM_READY`; no paid activation | `PHASE_A_READY_FOR_OWNER_ACTIVATION`, `PHASE_A_FREEZE_NO_GO`, or `INCONCLUSIVE_PHASE_A_FREEZE` |
| [G10R-AB](goals/G10R-AB-post-acquisition-headroom-active-comparison.md) | Run one separately authorized, instrumented A1 versus A2-M integration pilot using the G10R-AA manifest; collect boundary telemetry and classify infrastructure failures before applying the society decision rule | G10R-AA `PHASE_A_READY_FOR_OWNER_ACTIVATION`; explicit owner/provider/network activation; offline fault-injection matrix and repair/configuration freeze complete | `ESCALATE_ACTIVE_SOCIETY_EVALUATION`, `DO_NOT_ESCALATE_ACTIVE_SOCIETY`, or `INCONCLUSIVE_ACTIVE_INVESTIGATION` |
| [G10R-AC](goals/G10R-AC-provisional-argument-open-world-intake.md) | Implement provisional viewpoint arguments, open-world quarantined source intake, claim-level vetting, append-only revision, and anti-laundering safeguards offline | G10R-AB `INCONCLUSIVE_ACTIVE_INVESTIGATION`; G10R-P target-state amendment v2; no external calls | `PROVISIONAL_EVIDENCE_LOOP_READY`, `PROVISIONAL_EVIDENCE_LOOP_NO_GO`, or `INCONCLUSIVE_PROVISIONAL_INTAKE` |
| [G10R-AD](goals/G10R-AD-runner-provisional-intake-and-conflict-adjudication.md) | Integrate provisional arguments and claim-level conflict adjudication into the actual A1/A2-M runner and prove checkpoint, replay, authority, and contradiction behavior offline | G10R-AC `PROVISIONAL_EVIDENCE_LOOP_READY`; no external calls | `RUNNER_PROVISIONAL_INTAKE_READY`, `RUNNER_PROVISIONAL_INTAKE_NO_GO`, or `INCONCLUSIVE_RUNNER_INTAKE` |
| [G10R-AE](goals/G10R-AE-fresh-phase-a-freeze-after-runner-intake.md) | Freeze a distinct Phase-A manifest containing the runner-facing provisional intake and conflict adjudication integration, with offline fault injection and pending owner activation | G10R-AD `RUNNER_PROVISIONAL_INTAKE_READY`; no external calls | `PHASE_A_READY_FOR_OWNER_ACTIVATION`, `PHASE_A_FREEZE_NO_GO`, or `INCONCLUSIVE_PHASE_A_FREEZE` |
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
- G10R-P must complete after a non-escalating G10R result, and G10R-I must complete before any later paid society evaluation. G10R-I is the offline runtime-fidelity gate: it must wire the G10D viewpoint society and G10P evidence bus, exercise open-slot and support-task paths, and prove checkpoint/score joins, acquisition behavior, budget equality, authority boundaries, and replay. It may not add live calls, widen source policy, increase aggregate budgets, or promote evidence.
- After an integrated G10R run still produces no qualifying society contribution, G10R-A is the only next society goal: it may redesign offline support-task obligations and acquisition focus, but may not add live calls, widen source policy, increase aggregate budgets, or promote evidence. A positive G10R-A handoff may justify a fresh Phase-A manifest; it does not authorize a paid run by itself.
- After G10R-A and a later paid rerun still leave acquisition behavior ambiguous or constrained, G10R-C is the required next goal. It must audit and remediate the full constraint surface before another Phase-A freeze; it may not add live calls, widen source policy, increase aggregate budgets, or promote evidence.
- After G10R-C returns `PRE_RERUN_CONSTRAINTS_READY`, G10R-F is required to freeze a distinct Phase-A manifest before any separately authorized G10R Phase-B rerun. It may not make live calls, widen source policy, increase aggregate budgets, or overwrite historical artifacts.
- After G10R-F returns `PHASE_A_READY_FOR_OWNER_ACTIVATION`, G10R-B2 is the only eligible paid rerun. It requires explicit owner activation and must use the distinct manifest/output namespace; it may not widen source policy, increase budgets, or repeat automatically after a negative result.
- After G10R-B2 returns `DO_NOT_ESCALATE_ACTIVE_SOCIETY`, G10R-Q is the only eligible next goal. It must experimentally compare fixes for the observed acquisition and coordination symptoms offline while preserving the society architecture; it may not authorize another paid run automatically.
- After G10R-Q returns `SOCIETY_REMEDIATION_READY`, G10R-S is the only eligible next goal. It must integrate the winning treatment into the actual runner and verify it offline before any Phase-A freeze or paid test; it may not authorize a paid run by itself.
- After G10R-S and its separately authorized paid comparison return `DO_NOT_ESCALATE_ACTIVE_SOCIETY`, G10R-T is the only eligible next society goal. It must repair the iterative acquisition loop, highest-value focus allocation, post-sharing dossier revision, evidence-conditioned open slot, exactly-once replay, and typed evaluation, then isolate their effects offline. No further Phase-A freeze or paid society run is eligible unless G10R-T returns `SOCIETY_RESEARCH_LOOP_READY`, and that verdict only permits proposing a separate freeze goal.
- After G10R-T returns `SOCIETY_RESEARCH_LOOP_READY`, G10R-U is the only eligible next goal. It must freeze a distinct manifest containing the repaired research loop and record a separate owner activation request; it may not make model or network calls or activate a paid run.
- After G10R-U returns `PHASE_A_READY_FOR_OWNER_ACTIVATION`, G10R-W is required if the live runner has not yet been verified against the frozen research-loop contracts. G10R-W may make no model or network calls and must prove selection-gated acquisition, dossier revision, focus, open-slot, checkpoint, and replay behavior offline.
- After G10R-W returns `RUNTIME_RESEARCH_LOOP_WIRED`, G10R-X must freeze a distinct manifest containing the wiring changes; G10R-U remains historical and cannot be reused for paid execution.
- After G10R-X returns its owner-activation-ready result, G10R-V is the only eligible paid goal. It requires a separate explicit owner/provider/network activation and may not initialize a provider or spend money from a cycle invocation alone.
- After G10R-V returns `DO_NOT_ESCALATE_ACTIVE_SOCIETY`, G10R-Y is the only eligible next goal. It must diagnose and experimentally separate the observed acquisition/conversion and agent-design failures offline; it may not authorize another paid run automatically.
- After G10R-Y returns `POST_V_DIAGNOSIS_READY`, G10R-Z is the only eligible next goal. It must repair arm-neutral locator resolution, headroom validation, delayed open admission, support completion, and score parity offline; it may not freeze a manifest or authorize paid execution.
- After G10R-Z returns `ACQUISITION_HEADROOM_READY`, G10R-AA is the only eligible next goal. It must freeze a distinct Phase-A manifest and record a pending owner activation request without mutating historical artifacts; it may not make live calls, initialize a provider, open the network, or authorize paid execution.
- After G10R-AA returns `PHASE_A_READY_FOR_OWNER_ACTIVATION`, G10R-AB is the only eligible paid goal. It must first freeze the bundled repair/configuration manifest and pass the offline fault-injection matrix, then use the exact G10R-AA manifest and distinct output namespace for an instrumented A1/A2-M integration pilot. It requires explicit owner/provider/network activation, must preserve typed failures for postmortem analysis, and may not widen source policy, increase budgets, or repeat automatically after a negative or inconclusive result.
- After G10R-AB returns `INCONCLUSIVE_ACTIVE_INVESTIGATION` because common content headroom collapses, G10R-AC is the only eligible next goal. It must implement and test provisional arguments, quarantined open-world source leads, claim-level vetting, append-only revisions, and anti-laundering safeguards offline. It may not make live calls, widen source policy, promote evidence, or authorize another paid run.
- G10R-AC completed with `PROVISIONAL_EVIDENCE_LOOP_READY`: the offline provisional-evidence loop is ready for review, but no later live or paid goal is implicitly authorized. A future goal must explicitly define any Phase-A redesign or runner integration before execution.
- After G10R-AC returns `PROVISIONAL_EVIDENCE_LOOP_READY`, G10R-AD is the only eligible platform-continuation goal. It must integrate provisional intake and conflict adjudication into the actual runner offline; it may not make live calls, widen source policy, promote evidence, or authorize another paid run.
- After G10R-AD returns `RUNNER_PROVISIONAL_INTAKE_READY`, G10R-AE is the only eligible platform-continuation goal. It must freeze a distinct Phase-A manifest and record pending owner activation without making live calls or authorizing a paid run.
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
