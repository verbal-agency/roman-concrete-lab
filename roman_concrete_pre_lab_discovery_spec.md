# Roman Concrete AI Discovery System

## Pre-Lab Research & Experimental-Design Specification

**Status:** Build specification\
**Goal:** Push an AI-assisted Roman-inspired concrete discovery program
to the maximum scientifically defensible point possible **without access
to a physical materials laboratory**.

------------------------------------------------------------------------

## 1. Core Research Question

Can a literature-grounded, model-driven scientific system identify
promising, mechanistically defensible Roman-inspired concrete
formulations and rank the physical experiments that would provide the
greatest scientific value once laboratory access becomes available?

The system is **not** intended to claim that it has discovered a new
concrete formulation before physical validation.

Its pre-lab deliverable is:

> A ranked, reproducible, provenance-backed set of candidate
> formulations and experiments, together with explicit predictions,
> uncertainties, competing hypotheses, and the evidence required to
> falsify them.

A secondary research question is:

> Does an LLM/agentic layer improve scientific inquiry beyond a
> conventional data pipeline plus statistical optimizer?

This must be evaluated rather than assumed.

------------------------------------------------------------------------

## 2. Scientific Framing

Roman concrete is not a single recipe. The system should distinguish
among:

-   ancient structural concrete;
-   maritime concrete;
-   different volcanic and pozzolanic sources;
-   different lime-processing techniques;
-   environmental exposure histories;
-   modern Roman-inspired reconstructions.

Potential mechanisms to represent include:

-   pozzolanic reactions;
-   hot mixing;
-   reactive lime clasts;
-   crack-triggered dissolution and mineral precipitation;
-   long-term mineral formation;
-   aggregate/binder interfaces;
-   seawater-mediated reactions;
-   permeability reduction over time.

The system must separate:

1.  **observations** --- what was measured;
2.  **interpretations** --- what authors infer;
3.  **mechanistic hypotheses** --- proposed causal explanations;
4.  **predictions** --- what should happen if a hypothesis is true.

------------------------------------------------------------------------

## 3. Objective Functions and Measurable Outcomes

There is no requirement to optimize directly for "lasts 2,000 years."
That is not observable on project timescales.

Instead, model measurable proxies such as:

-   compressive strength;
-   tensile/flexural strength where available;
-   permeability;
-   porosity;
-   water absorption;
-   crack closure percentage;
-   crack-healing rate;
-   strength recovery after cracking;
-   permeability recovery after cracking;
-   resistance to chemical attack;
-   freeze/thaw performance;
-   chloride penetration;
-   mineral-phase formation;
-   dimensional stability;
-   performance after accelerated aging;
-   embodied carbon;
-   material cost;
-   curing time.

These are **proxy objectives**, not equivalent to millennial durability.

The system should support multi-objective optimization rather than
collapsing all outcomes into one arbitrary score.

------------------------------------------------------------------------

## 4. System Architecture

Conceptual flow:

``` text
Scientific Literature / Published Experimental Data
                    |
                    v
        Literature Retrieval Layer
                    |
                    v
     Structured Evidence Extraction
                    |
                    v
       Evidence / Provenance Store
                    |
          +---------+---------+
          |                   |
          v                   v
  Hypothesis Graph      Experimental Dataset
          |                   |
          +---------+---------+
                    |
                    v
          Surrogate Model(s)
                    |
                    v
        Bayesian Optimization
                    |
                    v
       Candidate Experiments
                    |
                    v
 Physics / Chemistry / Materials Modeling
                    |
                    v
      Multi-Fidelity Evaluation
                    |
                    v
 Agentic Scientific Reasoning Layer
                    |
                    v
 Hypothesis Discrimination + Experiment Ranking
                    |
                    v
        PRE-LAB RESEARCH PACKAGE
                    |
             [LAB BOUNDARY]
                    |
                    v
      Physical manufacture/testing
```

------------------------------------------------------------------------

## 5. Literature and Data Layer

### 5.1 Literature Discovery

Gather literature covering:

-   archaeological characterization of Roman concrete;
-   Roman maritime concrete;
-   lime clasts;
-   hot mixing;
-   pozzolanic chemistry;
-   volcanic ash mineralogy;
-   self-healing cementitious materials;
-   modern replication studies;
-   durability studies;
-   accelerated aging;
-   cement thermodynamics;
-   relevant modern concrete datasets.

Potential source interfaces may include:

-   Crossref;
-   OpenAlex;
-   Semantic Scholar;
-   publisher APIs where legally accessible;
-   institutional/open repositories;
-   structured public materials databases.

The implementation must respect licensing and access restrictions.

### 5.2 Evidence Extraction Schema

Convert papers into structured records.

Example:

``` yaml
paper_id:
sample_id:
sample_origin:
sample_age:
material_class:
binder_components:
aggregate_components:
lime_source:
pozzolan_source:
chemical_composition:
particle_size:
water_binder_ratio:
mixing_temperature:
mixing_sequence:
curing_conditions:
environmental_exposure:
test_method:
measurement:
measurement_value:
measurement_unit:
measurement_time:
microstructure_observation:
mineral_phase:
author_interpretation:
proposed_mechanism:
uncertainty:
extraction_method:
source_page:
source_table_or_figure:
doi:
```

Every extracted fact must retain provenance.

### 5.3 Extraction Quality

LLM extraction cannot silently become ground truth.

Implement:

-   schema validation;
-   units normalization;
-   duplicate detection;
-   confidence scores;
-   source-span/page references;
-   human-review flags;
-   contradiction detection;
-   distinction between measured and inferred values.

------------------------------------------------------------------------

## 6. Evidence and Hypothesis Representation

Create a structured hypothesis registry.

Example:

``` yaml
hypothesis_id: H001
claim: >
  Hot mixing produces reactive calcium-rich inclusions that
  promote crack-triggered mineral precipitation.
supporting_evidence:
contradicting_evidence:
predictions:
confounders:
uncertainty:
falsification_conditions:
source_ids:
status:
```

The system should be able to answer:

-   What evidence supports this hypothesis?
-   What evidence contradicts it?
-   Which observations are merely correlated?
-   Which experiment would most strongly discriminate it from an
    alternative?
-   What result would cause us to reduce confidence in it?

A graph representation is useful where relationships among materials,
processes, observations, mechanisms, and papers matter.

------------------------------------------------------------------------

## 7. Experimental Design Space

Represent candidate formulations numerically.

Possible dimensions:

``` text
lime fraction
lime type
pozzolan fraction
pozzolan mineralogy
aggregate fraction
aggregate mineralogy
water/binder ratio
particle-size distribution
mixing temperature
mixing duration
mixing sequence
curing temperature
curing humidity
salt/seawater exposure
initial crack width
aging conditions
```

Separate:

-   controllable variables;
-   environmental variables;
-   measured outputs;
-   latent/unobserved variables.

Do not create false precision for variables missing from historical
studies.

------------------------------------------------------------------------

## 8. Surrogate Modeling

The surrogate model approximates:

``` text
formulation + process + environment
                    ->
           predicted properties
```

Start with interpretable statistical baselines.

Candidate approaches:

-   Gaussian processes;
-   random forests;
-   gradient-boosted trees;
-   hierarchical models;
-   physics-informed regressors where justified;
-   ensembles.

Gaussian processes are particularly attractive for small-data regimes
because they provide uncertainty estimates.

Required outputs:

``` text
predicted outcome
predictive uncertainty
epistemic uncertainty where feasible
distance from training distribution
```

The system should explicitly identify predictions that are
extrapolations.

------------------------------------------------------------------------

## 9. Bayesian Optimization

Do not build Bayesian optimization mathematics from scratch unless
required for research.

Candidate stack:

-   **BoTorch**
-   **Ax**
-   PyTorch

The optimizer receives:

``` text
design space
constraints
surrogate predictions
uncertainty
objective(s)
```

and returns candidate experiments.

Acquisition strategies may include:

-   expected improvement;
-   upper confidence bound;
-   probability of improvement;
-   entropy/information-based acquisition;
-   multi-objective expected hypervolume improvement.

Critically, the system should distinguish:

### Optimization

> Which experiment is most likely to produce a high-performing material?

from:

### Scientific information gain

> Which experiment will tell us the most about which mechanism is
> correct?

Those are different objectives.

------------------------------------------------------------------------

## 10. Simulation Layer

### 10.1 Tier 0 --- Synthetic Simulator

Use synthetic functions only to test plumbing.

Purpose:

-   verify optimizer integration;
-   verify state handling;
-   verify experiment lifecycle;
-   benchmark search behavior.

Synthetic results must never be presented as materials evidence.

### 10.2 Tier 1 --- Data-Driven Surrogate Simulation

Train models on published experimental measurements.

Use them for:

-   interpolation;
-   uncertainty estimation;
-   candidate screening;
-   sensitivity analysis;
-   retrospective experiments.

### 10.3 Tier 2 --- Mechanistic / Physics-Based Modeling

Push beyond statistical interpolation wherever practical.

Potential modeling targets include:

-   hydration/pozzolanic reaction behavior;
-   thermodynamic phase stability;
-   transport/permeability;
-   dissolution/precipitation;
-   crack-related transport;
-   mineral formation.

Candidate scientific tools should be selected during implementation
based on feasibility and validation against the literature.

Possible classes of software include:

-   cement thermodynamic modeling;
-   geochemical equilibrium/reaction modeling;
-   finite-element/transport modeling;
-   molecular/materials simulation where appropriate.

The project should not use expensive physics simulations merely to make
the architecture appear sophisticated. Each model must answer a defined
scientific question.

------------------------------------------------------------------------

## 11. Multi-Fidelity Modeling

Treat evidence as having different fidelity levels.

Example:

``` text
historical observation
        |
published reconstruction
        |
statistical surrogate
        |
thermodynamic simulation
        |
transport simulation
        |
future physical experiment
```

Develop methods for combining these without pretending they are
equivalent.

Candidate formulations should accumulate evidence across modalities.

Example:

``` yaml
candidate: RC-017

literature_support: strong
surrogate_prediction:
  crack_recovery: 0.82
  uncertainty: 0.14

thermodynamic_support: moderate
transport_model_support: strong

OOD_risk: medium

mechanistic_consistency:
  H001: strong
  H004: weak

overall_status:
  high-value physical experiment
```

------------------------------------------------------------------------

## 12. Retrospective Validation

This is one of the strongest experiments available without a lab.

Take historical published datasets and hide later observations.

Example:

``` text
Knowledge available before Study X
            |
            v
      Run discovery system
            |
            v
 Predict promising formulation/region
            |
            v
Reveal Study X results
            |
            v
Compare prediction vs reality
```

Perform this repeatedly where chronological or dataset splits permit.

This tests whether the system can recover genuinely unseen published
outcomes rather than merely summarize literature it has already
ingested.

Avoid information leakage rigorously.

------------------------------------------------------------------------

## 13. Agentic Layer

Use **LangGraph** as the orchestration/state layer if implementing the
agentic version.

The agent does **not** replace the optimizer, surrogate model,
simulator, or scientific database.

Those should be exposed as tools.

Example tools:

``` text
search_literature()
retrieve_paper()
extract_experiment()
query_evidence()
query_hypothesis()
fit_surrogate()
predict_candidate()
run_bayesian_optimizer()
run_mechanistic_model()
calculate_information_gain()
compare_hypotheses()
register_candidate()
generate_experiment_protocol()
```

### Agent responsibilities

The LLM/agent may:

-   formulate queries;
-   synthesize evidence;
-   identify contradictions;
-   propose hypotheses;
-   connect evidence across papers;
-   decide which deterministic/statistical tool to call;
-   interpret model outputs;
-   propose hypothesis-discriminating experiments;
-   maintain research state;
-   explain recommendations;
-   generate lab-ready experimental plans.

It must not invent measurements.

------------------------------------------------------------------------

## 14. LangGraph State

Example:

``` python
ResearchState = {
    "research_question": ...,
    "evidence_ids": [...],
    "active_hypotheses": [...],
    "candidate_formulations": [...],
    "surrogate_version": ...,
    "optimizer_run": ...,
    "simulation_results": [...],
    "contradictions": [...],
    "uncertainties": [...],
    "next_experiments": [...],
    "provenance": [...]
}
```

The graph should support interruption and resumption because the
eventual physical version of the system may wait days or weeks for
experiments.

------------------------------------------------------------------------

## 15. Agent vs Non-Agent Baseline

This is essential.

Build two systems.

### Baseline A

``` text
structured dataset
    ->
surrogate model
    ->
Bayesian optimizer
    ->
ranked experiments
```

### System B

``` text
literature/evidence
      +
hypothesis representation
      +
surrogate model
      +
Bayesian optimizer
      +
mechanistic tools
      +
LLM agent
      ->
ranked experiments
```

Compare them.

Questions:

-   Does the agent identify useful constraints missing from the numeric
    dataset?
-   Does it produce better hypothesis-discriminating experiments?
-   Does it reduce wasted simulations?
-   Does it recognize contradictions?
-   Does it improve retrospective prediction?
-   Does it increase hallucination or instability?
-   Does it provide useful explanations without changing predictive
    performance?

The project should be willing to conclude that the agent adds little
value.

------------------------------------------------------------------------

## 16. Sensitivity and Causal Analysis

For promising candidates determine:

-   which variables drive predictions;
-   which interactions matter;
-   whether conclusions survive reasonable perturbations;
-   whether correlations could reflect confounding;
-   whether recommendations depend heavily on one paper/dataset.

Useful analyses include:

-   global sensitivity analysis;
-   partial dependence;
-   ablation;
-   feature permutation;
-   uncertainty decomposition;
-   leave-one-study-out validation;
-   counterfactual candidate comparisons.

------------------------------------------------------------------------

## 17. Out-of-Distribution Detection

A proposed formulation may lie far outside anything represented in
published data.

The system must flag this.

Example:

``` text
Candidate RC-043

Predicted self-healing: excellent
Model confidence: apparently high

BUT:

nearest literature formulation: distant
pozzolan chemistry: outside training range
mixing temperature: poorly represented

STATUS: speculative / requires physical validation
```

This prevents optimization from exploiting weaknesses in the surrogate
model.

------------------------------------------------------------------------

## 18. Hypothesis Discrimination

The system should optimize not only formulations but **scientific
questions**.

Suppose:

``` text
H1: lime-clast abundance dominates healing
H2: mixing temperature dominates healing
H3: volcanic-glass composition dominates healing
```

Find an experiment where the hypotheses predict substantially different
outcomes.

That experiment may be more scientifically valuable than the formulation
predicted to have the highest immediate performance.

This is one of the most important capabilities of the system.

------------------------------------------------------------------------

## 19. Pre-Lab Final Output

The final product should generate a research package such as:

### Candidate formulation

``` yaml
candidate_id: RC-027

formulation:
  ...

process:
  ...

predicted_properties:
  crack_closure:
  permeability_recovery:
  compressive_strength:

uncertainty:
  ...

supporting_evidence:
  ...

mechanistic_rationale:
  ...

competing_explanations:
  ...

simulation_results:
  ...

OOD_risk:
  ...

falsification_conditions:
  ...
```

### Recommended physical experiment

``` yaml
experiment_id: EXP-001

scientific_question:
hypotheses_discriminated:
candidate_formulations:
control_formulations:
measurements:
timepoints:
expected_outcomes_by_hypothesis:
decision_rule:
estimated_information_gain:
priority:
```

The system should be capable of saying:

> Run EXP-001 first because its expected outcome most strongly separates
> hypotheses H1 and H3. If result X occurs, confidence in H1 should
> increase; if result Y occurs, H3 becomes more plausible.

That is much stronger than simply generating an interesting concrete
recipe.

------------------------------------------------------------------------

## 20. Lab Handoff Package

When a laboratory partner becomes available, deliver:

1.  top candidate formulations;
2.  controls;
3.  mixing protocols;
4.  curing protocols;
5.  required measurements;
6.  measurement timepoints;
7.  predicted ranges;
8.  explicit competing hypotheses;
9.  falsification criteria;
10. uncertainty estimates;
11. safety/material-handling notes requiring expert review;
12. full provenance;
13. raw and transformed datasets;
14. model versions;
15. code/environment required to reproduce rankings.

The lab should be able to run the experiment without reverse-engineering
the AI system.

------------------------------------------------------------------------

## 21. Scientific Boundary

Before physical experimentation, the system may legitimately claim:

-   literature synthesis;
-   dataset construction;
-   model performance;
-   retrospective prediction;
-   simulation results;
-   statistical associations;
-   candidate ranking;
-   sensitivity results;
-   hypothesis generation;
-   expected information gain;
-   proposed experiments.

It must **not** claim:

-   discovery of a new concrete;
-   demonstrated self-healing;
-   demonstrated durability;
-   demonstrated causal mechanism;
-   successful replication of Roman concrete;
-   superior physical performance.

Those claims require empirical evidence.

------------------------------------------------------------------------

## 22. Suggested Technical Stack

### Orchestration

-   Python
-   LangGraph

### LLM layer

Provider/model should remain swappable.

### Scientific/data layer

-   pandas
-   NumPy
-   SciPy
-   scikit-learn
-   PyTorch

### Bayesian optimization

-   BoTorch
-   Ax

### Storage

Initial:

-   PostgreSQL

Potential additions:

-   pgvector for semantic retrieval;
-   graph database only if graph queries justify operational complexity.

### Provenance

Every important artifact should carry:

``` text
source
timestamp
extraction version
model version
transformation history
confidence
```

### Reproducibility

-   Git
-   immutable experiment IDs;
-   deterministic seeds where possible;
-   environment lockfile;
-   model/data versioning;
-   experiment manifests.

------------------------------------------------------------------------

## 23. Build Phases

### Phase 1 --- Scientific Scope

Define:

-   material class;
-   hypotheses;
-   objective variables;
-   design variables;
-   constraints;
-   evidence standards.

### Phase 2 --- Literature Corpus

Build retrieval and provenance pipeline.

### Phase 3 --- Structured Dataset

Extract published formulations, processing conditions, and outcomes.

### Phase 4 --- Evidence/Hypothesis System

Represent claims, contradictions, predictions, and falsification
criteria.

### Phase 5 --- Statistical Baselines

Build predictive baselines before introducing agents.

### Phase 6 --- Surrogate Model

Produce predictions plus calibrated uncertainty.

### Phase 7 --- Bayesian Optimization

Recommend experiments using both performance and information objectives.

### Phase 8 --- Retrospective Evaluation

Test predictions against held-out published experiments.

### Phase 9 --- Mechanistic Modeling

Add feasible thermodynamic/geochemical/transport simulations.

### Phase 10 --- Multi-Fidelity Fusion

Combine empirical, surrogate, and mechanistic evidence.

### Phase 11 --- Agentic System

Wrap scientific capabilities as tools and orchestrate them with
LangGraph.

### Phase 12 --- Agent Ablation

Measure whether the agent improves results relative to the non-agent
baseline.

### Phase 13 --- Pre-Lab Discovery Run

Generate candidate formulations and hypothesis-discriminating
experiments.

### Phase 14 --- Lab Handoff

Produce the physical-validation package.

------------------------------------------------------------------------

## 24. Success Criteria

A successful pre-lab system should demonstrate:

-   a provenance-backed Roman-concrete dataset;
-   reproducible extraction;
-   calibrated predictive models;
-   explicit uncertainty;
-   successful retrospective tests;
-   useful multi-objective optimization;
-   OOD detection;
-   hypothesis tracking;
-   hypothesis-discriminating experimental design;
-   mechanistic simulation where scientifically justified;
-   reproducible candidate ranking;
-   an empirical comparison of agentic vs non-agentic approaches;
-   lab-ready protocols for the highest-value physical experiments.

------------------------------------------------------------------------

## 25. Ultimate Pre-Lab Ceiling

The project reaches its legitimate pre-lab ceiling when it can make a
statement resembling:

> Given the currently available published evidence, statistical models,
> mechanistic simulations, and explicit assumptions, formulation RC-027
> is predicted to occupy a promising region of the design space.
> Experiment EXP-001 has the highest estimated value because it both
> tests RC-027's predicted behavior and strongly discriminates between
> competing mechanisms H1 and H3. These predictions remain unverified
> until physical testing.

At that point, additional agent reasoning is no substitute for new
empirical evidence.

**The next scientific action is to make the material.**

------------------------------------------------------------------------

## 26. Instruction for a Downstream Planning Agent

Given this specification:

1.  Break the system into executable engineering goals.
2.  Decompose each goal into tasks small enough for an implementation
    agent.
3.  Identify dependencies between tasks.
4.  Identify external datasets, papers, APIs, and scientific software
    requiring investigation.
5.  Separate deterministic software tasks from research tasks.
6.  Define acceptance tests for every engineering component.
7.  Define scientific evaluation criteria separately from software
    tests.
8.  Build the non-agent baseline before the agentic implementation.
9.  Prevent information leakage in retrospective evaluations.
10. Preserve provenance from the first ingestion step.
11. Never treat LLM-generated scientific statements as empirical
    observations.
12. Stop at the physical-validation boundary rather than fabricating
    certainty.
