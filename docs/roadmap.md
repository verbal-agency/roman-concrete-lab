# Execution roadmap

## How to use this roadmap

Give one goal file at a time to the implementation agent. The agent must not start a later goal, relax a scientific gate, or silently add infrastructure. Each goal ends with a binary handoff and named evidence.

The roadmap is stage-gated. G-1 is the only eligible starting goal:

```text
G-1 -> verdict-specific G00
          |
          +-- REPLICATION_STUDY_REQUIRED -> amend roadmap; G01-G10 blocked
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
                                                                       |
                                                                optional G10
                                                                       |
                                                                      G11
```

The diagram after G00 describes the synthesis/model track only. A `REPLICATION_STUDY_REQUIRED` verdict blocks G01–G10 until G00 ratifies a replication-first charter and the roadmap is amended with a controlled-study-design goal. `EVIDENCE_SYNTHESIS_ONLY` may proceed through evidence infrastructure but cannot authorize predictive ranking merely by reaching a later goal.

G09 accepts either the evidence-gap package or the completed modeling branch. G10 is not eligible until G09 releases a complete non-agent package. G11 requires external expert review regardless of whether G10 executes.

## Goals

| Goal | Objective | Depends on | Gate/output |
|---|---|---|---|
| [G-1](goals/G-1-literature-sufficiency-audit.md) | Determine whether enough direct, independent literature exists to justify this program | none | `MODELABLE_NOW`, `EVIDENCE_SYNTHESIS_ONLY`, `REPLICATION_STUDY_REQUIRED`, or `AUDIT_INCOMPLETE` |
| [G00](goals/G00-charter-and-scaffold.md) | Ratify the verdict-specific scientific charter and create only its authorized scaffold | substantive G-1 verdict | approved decision record and selected track |
| [G01](goals/G01-domain-and-evidence-contracts.md) | Implement canonical domain, evidence, provenance, and claim contracts | G00 | schema/contract conformance |
| [G02](goals/G02-corpus-protocol.md) | Produce a reproducible seed corpus and blinded screening ledger | G01 | frozen corpus manifest |
| [G03](goals/G03-extraction-benchmark.md) | Prove extraction quality on an expert-adjudicated gold set | G02 | extraction GO/NO-GO |
| [G04](goals/G04-evidence-store-and-feasibility-gate.md) | Build deterministic ingestion and issue the program feasibility verdict | G03 | NO-GO, LIMITED, or GO |
| [G05A](goals/G05A-evidence-gap-package.md) | On NO-GO, publish the evidence-gap synthesis and minimum lab study | G04 NO-GO | terminal non-model package |
| [G05B](goals/G05B-analysis-dataset.md) | On LIMITED/GO, freeze the analysis dataset and split plan | G04 LIMITED/GO | analysis-ready release |
| [G06](goals/G06-baselines-and-validation.md) | Fit honest baselines and validate by held-out study and time | G05B | model-use verdict |
| [G07](goals/G07-hypotheses-and-experiment-ranking.md) | Formalize rival hypotheses and rank bounded experiments | G06 (any verdict) | ranked design set |
| [G08](goals/G08-mechanistic-spike-and-synthesis.md) | Test one justified mechanistic model and synthesize without false fusion | G07 | model card and synthesis |
| [G09](goals/G09-non-agent-prelab-release.md) | Release the reproducible non-agent pre-lab package | G05A or G08 | versioned pre-lab release |
| [G10](goals/G10-agent-ablation.md) | Determine whether bounded agentic orchestration adds value | G09 | adopt/reject agent decision |
| [G11](goals/G11-expert-handoff.md) | Obtain scientific/safety review and issue the lab handoff | G09; G10 only if adopted | approved or blocked handoff |

## Program stop rules

- Stop all downstream work when G-1 returns `AUDIT_INCOMPLETE`.
- On G-1 `REPLICATION_STUDY_REQUIRED`, use G00 only to ratify a replication-first program and amend this roadmap; do not execute G01–G10.
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

Do not introduce PostgreSQL, pgvector, a graph database, LangGraph, PyTorch, BoTorch, or a mechanistic suite until the goal that needs it demonstrates that need.
