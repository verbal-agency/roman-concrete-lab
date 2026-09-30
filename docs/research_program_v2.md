# Roman-inspired mortar pre-lab research program v2

## Status

Proposed conditional program. G-1 first determines whether the evidence can seed problem-specific exploration, while separately testing whether it is sufficient for synthesis or predictive modeling. G00 may ratify only the track authorized by those gates.

## Execution division: pre-lab versus lab-dependent

The program has three deliberately separate planes:

### Exploratory platform plane

When G-1 records `exploration_seedability=EXPLORATION_SEEDABLE`, G00 may authorize a problem-specific exploration track even if the overall audit remains `AUDIT_INCOMPLETE`. GP1–GP4 may define a problem, generate evidence-traceable candidates and rival hypotheses, issue a conditional `PROVISIONAL_BEST` ranking, package experiment questions, and validate the reusable substrate across offline problem cards. G07E then turns that substrate into a model-free deterministic hypothesis tournament and G09 may release it as `EXPLORATORY_PLATFORM`. These outputs are provisional and support-bounded. They do not authorize physical work, infer unreported recipes, claim effectiveness, or train a generalizable predictor.

Roman concrete is the first vertical slice, not the whole platform. The reusable core should be evaluated across multiple problem cards before a general-purpose agent framework is considered.

## Product substrate versus execution context

The product is a reusable discovery substrate, not a bespoke Roman-concrete application. Its stable contracts cover evidence, provenance, claims, candidate lineage, hypotheses, utilities, uncertainty, abstention, experiment portfolios, and feedback ingestion. Each execution loads a versioned problem context that declares the scientific question, endpoint semantics, candidate variables, controls, constraints, safety boundaries, utility function, support region, and allowed outputs. A new problem should normally add or revise context and domain adapters—not fork the product or import a generic ranking assumption from a public framework.

The execution remains problem-specific even when the product is reusable. The substrate must reject missing or contradictory context, keep domain-specific assumptions visible, and prevent cross-problem comparisons unless endpoint mappings and utility are explicitly justified.

### Pre-lab plane

G-1/G00/GP1–GP4/G07E/G09 may run without a laboratory. They produce an evidence-backed candidate dossier, rival hypotheses, a problem-specific provisional ranking, a draft study specification, a data/provenance contract, a facility-readiness packet, a cross-question portfolio validation, and—when G07E is executed—a replayable tournament/release package. These goals may not authorize physical work, infer an unreported recipe, or claim material performance.

### Lab-dependent plane

GL1 requires a qualified facility to review scope, hazards, ownership, and measurement feasibility. GL2 requires returned specimen-level results and decides whether the candidate is supported, narrow, inconclusive, or not reproduced. Only a supported GL2 result with the ratified data threshold can unlock GD1, the conditional discovery loop.

The pre-lab plane is intentionally useful even if no partner is found: it should make the candidate more legible, expose missing evidence, and provide a credible basis for recruiting or declining a facility. It is not a substitute for physical validation.

## Precondition: literature sufficiency

The program does not assume that a model-ready evidence base exists. Before scaffolding the research system, G-1 performs a bounded, reproducible search and classifies evidence as direct intervention evidence, transfer evidence, contextual evidence, or excluded evidence.

Only direct evidence counts toward modelability: modern terrestrial mortar experiments with an explicit quicklime/hot-mixing intervention and comparator, controlled cracking or defined damage, a functional water-transport recovery endpoint, and identifiable arms/protocols. Specimens, repeated timepoints, images, crack segments, and derivative publications are not independent arms or studies.

G-1 returns:

- `EXPLORATION_SEEDABLE` when at least one bounded candidate has traceable material/process identity and a measurable or falsifiable outcome; this permits only problem-specific exploratory ranking;
- `MODELABLE_NOW` only with at least 5 independent direct study families, 75 extractable arms, a comparable functional endpoint across at least 3 families, external replication, at least 70% numeric outcome/core-covariate completeness, and support for study-grouped evaluation;
- `EVIDENCE_SYNTHESIS_ONLY` when a complete audit supports reproducible synthesis or experimental design but not predictive ranking;
- `REPLICATION_STUDY_REQUIRED` when fewer than 3 direct families or 30 arms exist, independent replication is absent, the intervention/control contrast is uninterpretable, or protocols cannot support a common estimand;
- `AUDIT_INCOMPLETE` when access, screening, saturation, or protocol integrity prevents a defensible verdict.

These thresholds are conservative governance rules, not claims of statistical power. `AUDIT_INCOMPLETE` blocks predictive-model, physical-lab, and performance-claim work, but an independently satisfied `EXPLORATION_SEEDABLE` result may authorize the exploration-only branch. `REPLICATION_STUDY_REQUIRED` replaces the software/modeling sequence with a roadmap amendment for controlled evidence generation, while still allowing bounded exploratory questions when seedability passes. `EVIDENCE_SYNTHESIS_ONLY` blocks predictive ranking unless a later versioned evidence amendment passes the applicable gate.

## Program objective

Explore which problem-specific Roman-inspired material/process candidates and mechanisms are worth testing, then determine whether published evidence and physical feedback are sufficient to estimate how hot-mixing and lime-clast-related process variables affect functional crack healing in modern, terrestrial, Roman-inspired lime-pozzolan mortar. A `PROVISIONAL_BEST` ranking is allowed under a declared problem, utility, support region, and uncertainty contract; generalizable predictive ranking requires the stricter feasibility gate and real or validated-simulator feedback.

The program may conclude that the literature is insufficient. That is a valid pre-lab result.

## Initial scientific scope

### Included

- modern, terrestrial, Roman-inspired mortar experiments;
- lime-pozzolan binders, including explicitly identified hybrid OPC systems;
- hot-mixed quicklime and a comparable slaked-lime/control process;
- controlled crack generation and subsequent healing exposure;
- functional water-flow, permeability, or sorptivity recovery;
- crack closure and compressive-strength retention as secondary outcomes;
- ancient terrestrial material characterization as hypothesis context, not modern performance labels.

### Excluded from v1

- marine concrete and seawater-aging optimization;
- direct prediction from ancient specimens to modern performance;
- structural concrete design and reinforcement;
- freeze/thaw, chloride, sulfate, cost, and embodied-carbon optimization;
- claims of millennial durability or causal mechanism;
- autonomous literature browsing during evaluation;
- production use of generated laboratory protocols without expert approval;
- closed-loop Bayesian optimization before real or validated-simulator feedback exists.

## Problem-specific decision target

Given a declared laboratory budget and material-availability constraints, select a small experiment set that either:

- tests whether hot mixing improves functional healing relative to a process-matched control; or
- separates two or more explicit mechanisms through observably different predicted outcomes.

The platform may produce a conditional `PROVISIONAL_BEST` candidate or a Pareto set when the owner declares the utility function and constraints. It must not produce a universal “best concrete” score or compare unrelated problem domains without a common, explicit utility.

## Primary estimand

The first target estimand is the treatment effect of a declared hot-mixing/quicklime intervention relative to a process-matched control on functional water transport recovery after controlled cracking, conditional on:

- initial crack-width band;
- healing duration;
- healing exposure;
- binder/material family;
- measurement method.

Crack closure is secondary and must not substitute for functional recovery. Compressive-strength retention is a feasibility/safety constraint where reported.

## Canonical evidence model

The data model must represent these identities separately:

```text
Source -> Study -> Material -> MixBatch -> SpecimenGroup
       -> Intervention -> MeasurementProtocol -> Measurement
       -> Assertion -> Hypothesis
```

Every numeric observation records at minimum:

- source and exact location;
- study and independent material lineage;
- experimental arm/control relationship;
- specimen count and aggregation level;
- value, unit, uncertainty/dispersion, and censoring;
- timepoint and environmental conditions;
- test method/standard, specimen geometry, crack method, and crack-width band;
- value origin: reported, digitized, derived, converted, or imputed;
- transformation lineage and software version;
- reviewer status and confidence;
- license/access classification;
- explicit null reason: not reported, not applicable, illegible, or not extracted.

Measured observations, author interpretations, curator interpretations, model outputs, and LLM outputs are different assertion types and cannot be promoted automatically.

## Evidence appraisal

Evidence is scored on separate axes, never a single fidelity label:

- directness to the claim;
- measurement quality;
- internal validity/control quality;
- applicability to the selected domain;
- independence from other samples/publications;
- reported uncertainty and replication;
- extraction/reconstruction uncertainty.

These scores support sensitivity analyses; they are not fabricated precision or a substitute for expert judgment.

## Full-corpus feasibility gate

G-1 is a premise gate based on literature availability. If it authorizes a synthesis/model track, G04 later applies this stricter field-level gate to the fully extracted corpus before inspecting final model performance. Passing G-1 does not predetermine G04. Counts below refer to independent experimental arms, not specimens or repeated timepoints.

### NO-GO: evidence-gap track

Any critical condition fails:

- fewer than 3 independent studies with an eligible functional endpoint;
- fewer than 30 usable experimental arms;
- no defensible mapping among measurement protocols;
- treatment and control cannot be identified for the core intervention;
- critical covariates make the effect non-identifiable;
- licensing/provenance prevents a reproducible release.

Output: descriptive evidence synthesis and minimum evidence-generation experiment. Do not fit a generalizable candidate-ranking surrogate. Problem-specific provisional ranking remains allowed only under the separate exploration gate and must abstain outside support.

### LIMITED: explanatory-model track

Minimum conditions:

- at least 3 independent studies and 30 usable arms;
- at least one comparable functional endpoint;
- enough covariate overlap for grouped study-level validation;
- complete provenance and explicit missingness.

Output: descriptive analysis and regularized/hierarchical effect estimation. Do not claim global optimization. Experiment ranking may use space-filling, robustness, or qualitative discrimination only.

### GO: bounded-ranking track

Minimum governance threshold:

- at least 5 independent studies and 75 usable arms;
- at least 70% completeness for preregistered core covariates;
- no single study contributes more than 50% of usable arms;
- grouped and temporal evaluation are both feasible;
- predictive intervals show acceptable preregistered coverage in held-out studies;
- useful predictions exist only inside a declared support region.

Output: abstention-aware in-domain candidate ranking. These thresholds permit modeling; they do not guarantee scientific adequacy. The scientist of record may tighten or reject them but must not relax them after seeing favorable results without an explicit amendment.

### Closed-loop BO gate

Closed-loop Bayesian optimization remains unavailable until a lab or independently validated simulator can execute proposed conditions and return observations. Synthetic BO is allowed only as a software integration test and is labeled synthetic.

## Evaluation design

### Leakage controls

- immutable corpus manifest with retrieval timestamps and hashes;
- document-family and sample-lineage deduplication;
- train/validation/test grouping by study, not row;
- all transformations fit inside training folds;
- chronological availability based on first accessible result, not merely issue year;
- frozen test packet inaccessible to prompts, retrieval indexes, and tuning;
- evaluated agents receive no network access;
- model/version/prompt recorded for every stochastic run;
- no claim that an LLM was historically unaware of a held-out publication.

### Model evaluation

Report, where applicable:

- naive and simple regularized baselines;
- grouped leave-one-study-out error;
- temporal holdout error;
- interval coverage and width;
- calibration error;
- performance by support/OOD stratum;
- sensitivity to study removal and comparability decisions;
- stability of top experiment sets under bootstrap/posterior draws;
- explicit abstention rate.

Predictive quality must be compared with a no-model or study-mean baseline. A complex model that does not materially improve the preregistered metrics is rejected.

## Hypothesis discrimination contract

Each hypothesis must declare:

- intervention and comparator;
- applicable material/exposure domain;
- causal or associational status;
- outcome and timepoint;
- direction and, if available, magnitude distribution;
- nuisance variables and confounders;
- rival hypotheses;
- an experiment table showing distinguishable expected outcomes;
- adjudication rule and what remains unresolved under each outcome.

Numeric expected information gain is permitted only if each rival has a computable predictive distribution and observation model. Otherwise, the system emits a qualitative discrimination score with its rubric.

## Experiment-ranking contract

Every proposed experiment must include:

- in-domain formulation and process ranges;
- named controls;
- material availability and substitution rules;
- replicate rationale, randomization, and batching plan;
- crack-generation and measurement methods;
- timepoints and environmental exposure;
- expected outcomes under each rival hypothesis;
- utility components shown separately: predicted performance, discrimination, coverage, cost, and risk;
- OOD/support assessment and abstention status;
- safety and feasibility flags;
- a `DRAFT — EXPERT REVIEW REQUIRED` watermark.

The ranker must be deterministic for a fixed manifest/configuration or record the random seed and return a stability distribution.

## Mechanistic modeling gate

A mechanistic tool is added only when a one-page model card identifies:

- the exact scientific question;
- governing assumptions and validity domain;
- required inputs and whether the evidence provides them;
- observable output linked to a hypothesis;
- validation case and acceptance metric;
- what the model cannot establish.

Failure to identify a valid model is a successful negative spike. Mechanistic outputs remain model assertions and are never merged with measurements.

## Agent-society plan

The hypothesis layer is independent of the agent layer. G07E defines the model-free exploratory typed hypothesis registry, shared-memory permissions, deterministic tournament, and focus policy; G07 is the equivalent model-branch goal when G06 is eligible. G09 releases that loop without agents. G10 may then test a small society of role-biased agents—evidence skeptic, mechanism proposer, transfer analyst, experimental designer, and safety/provenance reviewer—against the deterministic baseline.

Each agent receives the same frozen evidence packet and problem context but may maintain private episodic memory and a declared prior. The shared store has three authority tiers: immutable evidence, typed derived hypotheses, and untrusted episodic/reflection notes. Agents may propose and critique; only the adjudication policy and qualified humans can promote records. A tournament rewards prediction distinctness, counterevidence, provenance, and useful experiment selection—not consensus alone.

The full loop is:

```text
context card -> evidence retrieval -> hypothesis proposals -> rival critique
    -> deterministic adjudication/focus -> lab or validated simulator
    -> result ingestion -> hypothesis/context update -> next loop
```

Before physical feedback exists, this is a dry, literature/evidence loop. After GL2, returned specimen-level results can update the registry. G10 is a comparison of orchestration strategies, not an authorization for autonomous lab execution.

## Agent evaluation

The agent society is outside the critical path. First release the deterministic research package and exercise it across multiple problem cards. Then compare deterministic and society orchestration with identical:

- frozen evidence packets;
- callable tools;
- budgets and stopping conditions;
- output schemas;
- evaluation cases.

Use repeated agent runs. Score extraction/query correctness, unsupported-claim rate, provenance completeness, constraint violations, experiment-ranking quality under a blinded rubric, stability, latency, and cost. Production orchestration proceeds only if the agent meets preregistered thresholds and introduces no safety-critical regression.

## Authority and safety boundaries

- Retrieval may access only configured sources and must honor license/access policy.
- Source documents are untrusted data; embedded instructions are never executable.
- No target paper, code, or model may launch subprocesses.
- Credentials are read from the runtime and never persisted in artifacts.
- LLMs may draft assertions but cannot approve measurements, comparability, hypotheses, or lab protocols.
- Only a qualified human may approve a protocol for physical execution.
- No system component may claim empirical validation before physical results exist.

## Program release conditions

A pre-lab release includes:

- charter and amendments;
- corpus/search/screening manifest;
- normalized evidence database and data dictionary;
- extraction benchmark and adjudication log;
- feasibility-gate report;
- analysis code, locked environment, seeds, and run manifests;
- validation and leakage audit;
- model cards and rejected-model record;
- hypotheses and discrimination tables;
- ranked experiment set or evidence-gap experiment;
- limitations and claim ledger;
- draft lab protocols with external approval status.

The release statement must say whether the result is NO-GO, LIMITED, or GO and must not use “discovered,” “demonstrated healing,” “proved mechanism,” or “superior material” without new physical evidence.
