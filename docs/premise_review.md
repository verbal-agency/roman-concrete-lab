# Premise review: Roman Concrete AI Discovery System

## Verdict

The source specification has a worthwhile research question and unusually good scientific guardrails, but it is not yet safe to execute as written. It is a maximal architecture built on an untested assumption: that enough comparable, independent, machine-readable experimental evidence exists to support calibrated prediction, model discrimination, and candidate optimization.

The strongest executable program is narrower and conditional:

> Build a provenance-preserving evidence system for modern, terrestrial, Roman-inspired hot-mixed lime-pozzolan mortars; determine whether the published evidence is sufficient to estimate effects on functional crack healing; and, only if a preregistered feasibility gate passes, rank a small set of physical experiments that discriminate explicit rival hypotheses. A well-supported NO-GO finding is a successful pre-lab result.

This is worth executing because it can produce a useful result even if the fashionable premise—AI-guided discovery of a superior “Roman concrete”—does not survive contact with the data.

## Rapid scoping signal: audit before build

A preliminary, non-systematic scan suggests that the direct evidence base is probably too small for immediate predictive modeling, while the adjacent literature is large enough to support a rigorous evidence audit and replication design.

- [Seymour et al., 2023](https://doi.org/10.1126/sciadv.add1602) provides the central modern hot-mixing/quicklime self-healing result, but one originating study cannot establish out-of-study predictability.
- The [RILEM hot-lime review](https://doi.org/10.1617/s11527-023-02157-1) reports substantial variation in materials and process definitions, which weakens automatic pooling.
- [Grosso Giordano et al., 2024](https://doi.org/10.1016/j.conbuildmat.2024.136603) shows that crack closure, water flow, and microstructural observations can disagree and reports limited differences among its tested formulations.
- [Grosso Giordano et al., 2025](https://doi.org/10.1016/j.jobe.2025.113234) describes the lime-based self-healing literature as limited, conflicting, and measurement-variable.

This signal is not itself a systematic-review conclusion. It changes the order of work: G-1 must test literature sufficiency before G00 authorizes a software or modeling program. The anticipated verdict is `REPLICATION_STUDY_REQUIRED`, but the frozen search and screening record—not this expectation—must decide.

## What the source gets right

- It explicitly rejects claims of discovery before physical validation.
- It distinguishes observations, interpretations, hypotheses, and predictions.
- It requires provenance and warns that LLM extraction is not ground truth.
- It separates performance optimization from scientific information gain.
- It calls for retrospective evaluation and an agent-free baseline.
- It permits the conclusion that an agent adds no value.
- It identifies out-of-distribution risk and the physical-lab boundary.

Those principles should be retained.

## Material weaknesses

### 1. “Roman concrete” is still several incompatible domains

The document acknowledges heterogeneity but then reunites terrestrial concrete, marine concrete, ancient samples, modern reconstructions, self-healing materials, and conventional concrete datasets in one pipeline. These domains differ in ingredients, processing, age, exposure, observable outcomes, and causal relevance. They cannot be treated as rows of one supervised-learning problem.

The flagship hot-mixing work itself separates ancient characterization from modern Roman-inspired testing and reports two modern formulations; one self-healing formulation is explicitly a coarse-aggregate-free mortar containing OPC, fly ash, sand, water, and quicklime. That is not a generic empirical basis for optimizing all Roman-inspired concrete. See [Seymour et al., 2023](https://doi.org/10.1126/sciadv.add1602). New archaeological evidence supports hot mixing at a particular Pompeian construction context, but also underscores that practices were not temporally or geographically universal; see [Masic et al., 2025](https://doi.org/10.1038/s41467-025-66634-7).

**Correction:** the first program must select one modern material class, one exposure regime, one intervention family, and one primary functional outcome. Ancient and marine evidence may inform hypotheses but must not silently become performance labels for modern terrestrial mortar.

### 2. The project assumes a model-ready dataset before conducting a data audit

Phases 5–10 presume that extraction will yield enough comparable observations for calibrated surrogates, Bayesian optimization, mechanistic modeling, and multi-fidelity fusion. That may be false. Published Roman-concrete mechanical data are sparse, while modern self-healing studies use nonuniform cracking, curing, imaging, and transport protocols. An interlaboratory study found that methods and laboratory conditions materially affect self-healing assessment; see [Litina et al., 2021](https://doi.org/10.3390/ma14082024). Another study notes the absence of a standardized permeability method and large result variation even at similar crack widths; see [Lee et al., 2021](https://doi.org/10.3390/ma14123202).

**Correction:** put a reproducible evidence-feasibility gate before implementation of predictive modeling. The gate must be able to terminate the modeling branch.

### 3. The proposed objective space is not a research objective

The list of seventeen outcomes includes mechanical performance, transport, healing, durability, carbon, cost, and curing time. “Multi-objective” does not solve the absence of priorities, test budgets, constraints, or a decision-maker's utility. Different outcomes also have different measurement semantics and evidence coverage.

**Correction:** use permeability or water-flow recovery after controlled cracking as the primary endpoint; crack closure as a secondary endpoint; and compressive-strength retention as a safety constraint. Treat carbon, cost, marine durability, freeze/thaw, chloride ingress, and millennial durability as out of scope for the first program.

### 4. Bayesian optimization is mispositioned

Bayesian optimization is normally sequential: a surrogate proposes a query, the real experiment or validated simulator returns an observation, and the model updates. Before lab access, optimizing the predictions of a literature-trained surrogate can simply find its errors. Surrogate misspecification can reduce the usefulness of acquired points; see [Bodin et al., 2020](https://proceedings.mlr.press/v119/bodin20a.html).

**Correction:** call the pre-lab activity **constrained offline experiment ranking**, not closed-loop Bayesian optimization. Permit BO only in synthetic integration tests or after a physical/validated-simulator feedback loop exists.

### 5. “Expected information gain” is not available from a prose hypothesis registry

A claim, evidence list, and confidence label do not define a probability model. Expected information gain for model discrimination requires rival predictive models, parameter/prior uncertainty, an observation model, and a utility over possible outcomes. See [Hainy et al., 2022](https://doi.org/10.1007/s11222-022-10078-2).

**Correction:** begin with auditable qualitative discrimination tables. Compute numeric information gain only where rival models produce explicit predictive distributions and assumptions are recorded.

### 6. The extraction schema has the wrong unit of analysis

The flat record cannot faithfully represent paper → study → material → batch/mix → specimen → intervention → measurement. It omits replicate count, dispersion, specimen geometry, crack-generation method, test standard, censoring, control pairing, data origin, data transformations, and whether values were reported, digitized, derived, imputed, or absent.

**Correction:** adopt normalized entities and typed assertions. Preserve null semantics and prohibit conversion of “not reported” into zero.

### 7. The evidence “fidelity ladder” is false ordering

Historical observations, reconstructions, statistical predictions, and simulations are not points on one scalar fidelity axis. An archaeological observation can be direct evidence of composition but weak evidence of modern performance. A simulation can be precise yet irrelevant outside its validity domain.

**Correction:** assess evidence on separate axes: directness to claim, measurement quality, internal validity, applicability/domain match, independence, and uncertainty. Fusion must preserve disagreement rather than average unlike quantities.

### 8. Retrospective evaluation is under-specified and vulnerable to leakage

A publication-year split is insufficient. Later papers may repeat earlier samples; reviews may contain test outcomes; article versions have different availability dates; transformations may be fit globally; and a general-purpose LLM may already know the held-out paper.

**Correction:** freeze corpus manifests, group by study/material lineage, fit every transformation on training folds only, deduplicate shared specimens, and deny the evaluated agent network access. The LLM may receive only the frozen evidence packet. An LLM “time-travel” benchmark cannot prove historical novelty.

### 9. The agent comparison is confounded

Baseline A has a dataset and optimizer. System B receives literature, hypotheses, mechanistic tools, and an agent. Any difference cannot be attributed to agency.

**Correction:** run a factorial ablation in which deterministic and agentic orchestrators receive identical evidence, tools, budgets, and output schemas. Evaluate repeated runs for task accuracy, unsupported-claim rate, constraint violations, ranking stability, cost, and latency.

### 10. “Lab-ready” requires expertise the software cannot supply

Mixing quicklime is exothermic and materials protocols depend on standards, equipment, specimen geometry, replication, randomization, and safety controls. A generated protocol is a draft until a qualified materials scientist and laboratory safety reviewer approve it.

**Correction:** label all protocols `DRAFT — EXPERT REVIEW REQUIRED`; make expert sign-off an external release gate; include controls, replicate rationale, randomization, measurement standards, equipment assumptions, and stop conditions.

### 11. The architecture is premature

PostgreSQL, pgvector, a graph database, LangGraph, PyTorch, BoTorch, and several classes of physics software are listed before data scale and query patterns are known. This creates a large surface area without improving the scientific claim.

**Correction:** begin with versioned schemas, files, and a small relational store. Add services only when an accepted goal demonstrates the need. LangGraph is conditional on the agent benchmark, not part of the critical path.

### 12. Success criteria are aspirations, not pass/fail criteria

Terms such as “calibrated,” “successful,” “useful,” and “lab-ready” lack thresholds and named evidence. The project has no budget, stop rule, or failure release.

**Correction:** every goal needs binary acceptance criteria and a criterion-to-test/artifact map. Program gates must specify GO, LIMITED, and NO-GO outcomes in advance.

## Questions the owner must answer

These are material product/research choices. The roadmap records recommended defaults so work can start, but G00 must confirm or override them.

1. Is the primary purpose a credible materials-research contribution or a demonstration of an AI research architecture?
   - **Recommended:** materials research first. Software sophistication has no value unless it strengthens a specific claim.
2. Is the initial domain modern terrestrial mortar, marine concrete, or archaeological characterization?
   - **Recommended:** modern terrestrial Roman-inspired hot-mixed lime-pozzolan mortar. Use ancient terrestrial evidence only to motivate hypotheses; exclude marine systems from v1.
3. Which outcome controls the first decision?
   - **Recommended:** functional water-flow/permeability recovery after controlled cracking, with crack closure secondary and compressive strength as a constraint.
4. Who is the scientist of record?
   - **Required before lab handoff:** a cementitious-materials expert who approves ontology, comparability judgments, hypotheses, and draft protocols.
5. What data rights are acceptable?
   - **Recommended:** metadata and openly licensed full text/data by default; store restricted-source metadata and citations but not unauthorized content.
6. Is a NO-GO result acceptable after the evidence audit?
   - **Recommended and required for credibility:** yes.
7. What are the corpus, compute, API, and model-call budgets?
   - **Recommended starting cap:** a 30–60-paper screened seed corpus, deterministic local processing where possible, and recorded model-call budgets.
8. Does the project intend commercial reuse?
   - This changes acceptable source licenses and must be recorded before corpus acquisition.

## Recommended program-level success statement

The program succeeds if it produces one of two reproducible outcomes:

1. **GO:** comparable evidence supports a validated, abstention-aware model that ranks a bounded set of in-domain physical experiments and states exactly what each result would imply; or
2. **NO-GO:** the evidence audit demonstrates why ranking would be unreliable and produces the smallest controlled laboratory program needed to make a future model possible.

Either outcome is stronger than a visually impressive agent that optimizes unsupported predictions.
