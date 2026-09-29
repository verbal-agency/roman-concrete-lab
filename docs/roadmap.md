# Execution roadmap

## How to use this roadmap

Give one goal file at a time to the implementation agent. The agent must not start a later goal, relax a scientific gate, or silently add infrastructure. Each goal ends with a binary handoff and named evidence.

The roadmap is stage-gated. G-1 is the only eligible starting goal. The amended plan separates bounded, problem-specific exploration from predictive modeling and from work that requires an external qualified facility:

```text
G-1 -> verdict-specific G00
          |
          +-- exploration_seedability=EXPLORATION_SEEDABLE
          |       -> G00 EXPLORATORY_PLATFORM -> GP1 -> GP2 -> GP3 -> GP4
          |                                                    |
          |                                                    +-- exploratory-only stop
          |                                                    +-- qualified partner -> GL1 -> GL2
          |
          +-- material candidate plausible + REPLICATION_STUDY_REQUIRED
          |       -> G00 PRELAB_REPLICATION -> GP1 -> GP2 -> GP3 -> GP4 -> GL1 -> GL2
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
                                                                optional G10
                                                                       |
                                                                      G11
```

The diagram after G00 now has an exploratory branch and a lab-dependent branch. `EXPLORATION_SEEDABLE` permits a problem-specific candidate/hypothesis and experiment-ranking work while the overall G-1 audit remains provisional; it does not authorize physical execution, performance claims, or a generalizable predictive model. The pre-lab branch (`GP1`–`GP4`) may create evidence dossiers, hypotheses, study specifications, partner-readiness material, and a cross-question portfolio checkpoint without a lab. `GL1` is the external facility/safety gate; `GL2` requires returned physical results. The discovery branch (`GD1`) is unavailable until GL2 produces reproducible, comparable data. A `REPLICATION_STUDY_REQUIRED` verdict without a material candidate blocks physical planning. `EVIDENCE_SYNTHESIS_ONLY` may proceed through evidence infrastructure but cannot authorize predictive ranking merely by reaching a later goal.

G09 accepts the evidence-gap package, the completed modeling branch, or a completed physical-feedback discovery loop from GD1. G10 is not eligible until G09 releases a complete non-agent package. G11 requires external expert review regardless of whether G10 executes.

The agent-society progression is deliberate: G07 defines the typed hypothesis layer, shared-memory permissions, deterministic tournament, and explicitly discusses and freezes the focus and promotion layers; G09 releases that loop without agents; G10 tests role-biased agents against it under identical evidence and budgets; G11 reviews any adopted society before it appears in a lab handoff.

## Goals

| Goal | Objective | Depends on | Gate/output |
|---|---|---|---|
| [G-1](goals/G-1-literature-sufficiency-audit.md) | Determine whether the evidence can seed problem-specific exploration, support synthesis, or justify predictive modeling | none | `EXPLORATION_SEEDABLE` plus the conservative modelability/material verdicts |
| [G00](goals/G00-charter-and-scaffold.md) | Ratify the reusable substrate, declared problem context, and selected exploration, replication, synthesis, or modeling charter | G-1 `EXPLORATION_SEEDABLE` or complete substantive verdict | approved decision record, context contract, and selected track |
| [GP1](goals/GP1-candidate-evidence-and-hypothesis-dossier.md) | Convert evidence into a problem-specific candidate dossier and rival-hypothesis matrix | G00 `EXPLORATORY_PLATFORM` or `PRELAB_REPLICATION` | candidate dossier and hypothesis gate |
| [GP2](goals/GP2-prelab-experiment-specification.md) | Produce a provisional candidate/experiment ranking and a draft, non-authorizing study specification | GP1 | conditional ranking plus `DRAFT — EXPERT REVIEW REQUIRED` study package |
| [GP3](goals/GP3-partner-readiness-package.md) | Package a problem-specific experiment portfolio, facility requirements, data contracts, and partner-review questions | GP2 | exploratory portfolio and partner-ready handoff packet |
| [GP4](goals/GP4-cross-question-portfolio-validation.md) | Validate the reusable problem-card and portfolio substrate across the Roman case and two offline cross-domain fixtures | GP3 | cross-question portfolio validation and explicit no-go/continue decision |
| [GL1](goals/GL1-lab-partner-and-safety-gate.md) | Obtain qualified facility feasibility and safety review before any physical execution | GP4 | approved, revised, or blocked lab gate |
| [GL2](goals/GL2-replication-result-ingestion.md) | Ingest partner results and decide whether the candidate is supported, narrow, inconclusive, or rejected | GL1 plus returned lab data | result snapshot and candidate verdict |
| [GD1](goals/GD1-conditional-discovery-loop.md) | Build a discovery loop only if replication produces sufficient comparable data | GL2 `SUPPORTED` with data threshold | conditional discovery GO/NO-GO |
| [G01](goals/G01-domain-and-evidence-contracts.md) | Implement canonical domain, evidence, provenance, and claim contracts | G00 | schema/contract conformance |
| [G02](goals/G02-corpus-protocol.md) | Produce a reproducible seed corpus and blinded screening ledger | G01 | frozen corpus manifest |
| [G03](goals/G03-extraction-benchmark.md) | Prove extraction quality on an expert-adjudicated gold set | G02 | extraction GO/NO-GO |
| [G04](goals/G04-evidence-store-and-feasibility-gate.md) | Build deterministic ingestion and issue the program feasibility verdict | G03 | NO-GO, LIMITED, or GO |
| [G05A](goals/G05A-evidence-gap-package.md) | On NO-GO, publish the evidence-gap synthesis and minimum lab study | G04 NO-GO | terminal non-model package |
| [G05B](goals/G05B-analysis-dataset.md) | On LIMITED/GO, freeze the analysis dataset and split plan | G04 LIMITED/GO | analysis-ready release |
| [G06](goals/G06-baselines-and-validation.md) | Fit honest baselines and validate by held-out study and time | G05B | model-use verdict |
| [G07](goals/G07-hypotheses-and-experiment-ranking.md) | Formalize the hypothesis registry, deterministic tournament, scoped shared memory, and rank bounded experiments | G06 (any verdict) | hypothesis/tournament contract and ranked design set |
| [G08](goals/G08-mechanistic-spike-and-synthesis.md) | Test one justified mechanistic model and synthesize without false fusion | G07 | model card and synthesis |
| [G09](goals/G09-non-agent-prelab-release.md) | Release the reproducible non-agent context, memory, hypothesis, focus, feedback, and pre-lab package | G05A, G08, or GD1 | versioned non-agent release |
| [G10](goals/G10-agent-ablation.md) | Evaluate whether a bounded agent society with shared memory and hypothesis tournament adds value | G09 | task-specific society adoption/rejection decision |
| [G11](goals/G11-expert-handoff.md) | Obtain scientific/safety review and issue the lab handoff | G09; G10 only if adopted | approved or blocked handoff |

## Program stop rules

- Stop all predictive-modeling, physical-lab, and performance-claim work when G-1 returns `AUDIT_INCOMPLETE`. If and only if `exploration_seedability=EXPLORATION_SEEDABLE`, G00 may authorize the bounded exploratory platform branch.
- Exploratory outputs must remain `PROVISIONAL_BEST`, `HYPOTHESIS`, or `EXPERIMENT_CANDIDATE`; they may not be promoted to validated performance, a recipe, or a generalizable model.
- On G-1 `REPLICATION_STUDY_REQUIRED` with a provisional/confirmed material candidate, G00 may authorize only GP1–GP4. No physical work is authorized until GL1 passes.
- On G-1 `REPLICATION_STUDY_REQUIRED` without a material candidate, use G00 only to document the evidence gap; do not execute GP2, GL1, GL2, or G01–G10.
- GL2 must return `SUPPORTED`, `NARROW_USE_CASE`, `INCONCLUSIVE`, or `NOT_REPRODUCED`; only `SUPPORTED` with the ratified data threshold may unlock GD1.
- G07 must establish the deterministic hypothesis registry, shared-memory permissions, tournament, and focus policy before G09 or G10 can claim a complete discovery loop.
- G09 must release and replay the non-agent loop before G10 introduces role-biased agents; agent society is an overlay to evaluate, not the source of scientific truth.
- G10 adoption is task-specific. A society may be adopted for query formulation, contradiction triage, hypothesis critique, or experiment explanation without receiving authority to alter evidence, approve safety, or run a lab.
- A single problem may have a `PROVISIONAL_BEST` candidate under declared constraints, but a global or cross-problem “best material” claim is prohibited unless the utility function, support region, and validation evidence are explicit.
- The reusable platform core should be exercised across multiple problem cards before introducing a general-purpose agent framework; Roman concrete is the first vertical slice, not the whole platform.
- On G-1 `EVIDENCE_SYNTHESIS_ONLY`, prohibit predictive modeling and ranking unless a versioned evidence amendment later satisfies the frozen gate.
- Stop predictive-model work at G04 NO-GO. Execute G05A; do not continue through G05B–G07.
- Stop model-based ranking at G06 if the preregistered baseline/coverage criteria fail. Route to qualitative design mode in G07.
- Stop mechanistic integration if G08 cannot establish input availability, validity, and an observable validation target.
- Stop agent development at G10 if it fails any critical safety/provenance threshold or does not beat deterministic orchestration on the preregistered primary metric.
- Stop release at G11 if qualified reviewers have not approved the protocol. A blocked review is reported; it is not converted into approval.

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
