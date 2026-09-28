# G-1 — Audit literature sufficiency before program construction

**Status:** blocked — `AUDIT_INCOMPLETE` pending qualified human adjudication
**Dependencies:** none  
**Advances:** an evidence-backed decision about whether the proposed research program should become a modeling project, an evidence-synthesis project, or a replication-first project

**Current amendment:** execution uses protocol `g1.2-material-candidate` in `docs/protocols/literature-sufficiency-search.md`. It adds a material-candidate viability pass—separate from modelability—using public repository/thesis indexes, exact-title/DOI searches, archaeological/material-characterization records, technical reports, and citation chains. It explicitly excludes Sci-Hub and other unauthorized access and records subscription databases as access gaps unless authenticated access is supplied.

## Objective

Determine both (a) whether a materially specified Roman-concrete candidate can be responsibly handed to a qualified laboratory for a bounded, safe test, and (b) whether the published record contains enough independent, comparable, modern terrestrial hot-mixed quicklime/lime-pozzolan experiments with controlled cracking and functional healing outcomes to justify a model-oriented program proposed in `docs/research_program_v2.md`.

This is the only eligible starting goal. It audits the premise; it does not presume that a model-ready corpus exists.

## Decision question

Can the literature support study-grouped estimation and honest out-of-study evaluation of a declared hot-mixing/quicklime intervention against a process-matched control on functional water-transport recovery after controlled cracking?

The audit emits a paired decision: `material_candidate_verdict` (`LAB_CANDIDATE_PLAUSIBLE`, `LAB_CANDIDATE_NOT_ESTABLISHED`, or provisional/incomplete) and `modelability_verdict` (`MODELABLE_NOW`, `EVIDENCE_SYNTHESIS_ONLY`, `REPLICATION_STUDY_REQUIRED`, or `AUDIT_INCOMPLETE`). The overall G-1 state remains `AUDIT_INCOMPLETE` until required human adjudication and coverage gates are complete.

## Frozen evidence tiers

Only Tier A evidence counts toward the quantitative decision thresholds.

### Tier A — direct intervention evidence

A study family qualifies only when all of the following are identifiable:

- a modern, terrestrial mortar or mortar-like specimen;
- an explicit quicklime/hot-mixing intervention and an interpretable comparator;
- controlled crack generation or a clearly defined damaged state;
- a functional water-flow, permeability, or sorptivity recovery endpoint;
- experimental arms, protocol, and specimen counts distinguishable from repeated measurements and timepoints.

### Tier B — transfer evidence

Modern lime-pozzolan, lime-cement, natural-hydraulic-lime, or self-healing mortar studies that inform an endpoint, mechanism, or measurement method but fail at least one Tier A condition.

### Tier C — contextual evidence

Archaeological characterization, reviews, historical sources, mechanistic papers without a qualifying intervention, and standards or methods papers. These may shape hypotheses and terminology but are not modern performance labels.

### Tier D — excluded

Marine-only optimization, unrelated concrete self-healing systems, commentary without inspectable methods, duplicate reports with no new experiment, and sources whose relevant methods/results cannot be inspected.

## Search and screening protocol

Before final screening, freeze and version:

- databases and indexes searched, access dates, exact queries, language handling, and coverage limits;
- backward and forward citation chaining from known seed papers and reviews;
- title/abstract and full-text inclusion/exclusion rules;
- DOI/title/author/year deduplication and publication-family clustering;
- the definition of an independent study family and experimental arm;
- the numeric thresholds below and all budget/stop rules.

Minimum discovery coverage is Crossref, OpenAlex, Semantic Scholar, and citation chaining from the known seed set. Scopus or Web of Science may be added when lawfully available; lack of subscription access is recorded, not bypassed. Language is not itself an exclusion when a reliable translation path exists.

Known seeds must include, at minimum, Seymour et al. (2023, DOI `10.1126/sciadv.add1602`), the RILEM hot-lime review (2023, DOI `10.1617/s11527-023-02157-1`), Grosso Giordano et al. (2024, DOI `10.1016/j.conbuildmat.2024.136603`), Grosso Giordano et al. (2025, DOI `10.1016/j.jobe.2025.113234`), and relevant references/citations they expose. Seed status confers no eligibility.

The original default search budget was 250 deduplicated records, 60 full-text assessments, and two complete citation-chaining waves. The current amended execution uses the frozen `g1.2-material-candidate` budget of 500 deduplicated records, 120 full-text/preview assessments, and four complete citation-chaining waves. Reaching a budget limit before the saturation rule is satisfied yields `AUDIT_INCOMPLETE`.

Saturation requires two successive search/citation waves that each add no new Tier A study family and less than 5% new potentially eligible records relative to the previously screened unique-record total.

## Decision matrix

Thresholds are governance requirements, not guarantees of statistical adequacy.

| Verdict | All required conditions |
|---|---|
| `MODELABLE_NOW` | At least 5 independent Tier A study families; at least 75 extractable experimental arms; at least 3 independent families reporting a comparable functional endpoint; at least one qualifying external replication outside the originating research group; treatment/control identity is defensible; at least 70% of arms have reported or faithfully extractable numeric primary outcomes and preregistered core covariates; study-grouped evaluation is feasible. |
| `EVIDENCE_SYNTHESIS_ONLY` | The audit is complete and the direct/transfer record can support a reproducible descriptive synthesis or experimental design, but one or more `MODELABLE_NOW` conditions fail without triggering the replication-first conditions below. Ordinarily this requires at least 3 independent Tier A families and 30 extractable arms. No predictive ranking is authorized. |
| `REPLICATION_STUDY_REQUIRED` | Any of: fewer than 3 independent Tier A families; fewer than 30 extractable Tier A arms; no independent replication; no interpretable intervention/control contrast; or protocols/endpoints are too incompatible to support a common estimand. The next program must design evidence generation, not build a literature-trained predictor. |
| `AUDIT_INCOMPLETE` | Required sources could not be lawfully inspected, screening/adjudication is unfinished, the search budget ended before saturation, or the frozen protocol was materially violated. This state authorizes no downstream goal. |

Where conditions conflict, the most conservative applicable verdict wins. Counts may not be rescued by treating specimens, timepoints, images, crack segments, or multiple publications from the same experimental lineage as independent arms or studies.

## Data and provenance contract

Every screened record must preserve:

- stable source identifier, DOI and other bibliographic identifiers;
- title, authors, year, source version, retrieval date, URL, access/license class, and content hash when a lawful local artifact exists;
- screening stage, inclusion decision, evidence tier, exclusion reason, reviewer, and adjudication status;
- `study_family_id`, research-group identity used for replication assessment, and links to duplicate or derivative publications;
- material class, intervention, comparator, crack protocol, exposure, endpoint, and measurement method;
- reported numbers of arms and specimens, with repeated timepoints recorded separately;
- numeric-data availability: reported table, digitizable figure, supplement/repository, narrative only, inaccessible, or not reported;
- exact source locator for every eligibility and count claim;
- uncertainty or unresolved ambiguity without inferred replacement values.

Required invariants:

- one experimental lineage cannot count as more than one independent study family;
- an arm is a deliberately distinct treatment/control condition, not a specimen, timepoint, image, or measurement replicate;
- uncertain Tier A eligibility remains `pending` and contributes zero to thresholds until adjudicated;
- reviews and archaeological evidence never count as Tier A;
- abstract-only or inaccessible claims do not count as extractable arms;
- an LLM may propose screening or extraction labels but may not approve eligibility, independence, or a verdict;
- absent methods, outcomes, uncertainty, or covariates remain absent and are never inferred from domain convention.

## Expected implementation surface

- `docs/protocols/literature-sufficiency-search.md` — frozen search, screening, saturation, and adjudication protocol;
- `schemas/literature-sufficiency-record.schema.json` — machine-readable record contract;
- `data/manifests/literature-sufficiency-sources.jsonl` — deduplicated source and retrieval manifest;
- `data/manifests/literature-sufficiency-screening.csv` — screening ledger;
- `data/processed/literature-sufficiency-study-families.jsonl` — family/arm counts and eligibility fields;
- `data/processed/literature-sufficiency-material-candidates.jsonl` — candidate identity, material evidence, lab-handoff readiness, and provisional candidate verdicts;
- `tools/literature_audit/` — optional, standard-library-only normalization and deterministic verdict code;
- `fixtures/literature_audit/` — offline positive, negative, duplicate, contradictory, malformed, partial, inaccessible, and budget-exhaustion cases;
- `tests/literature_audit/` — contract and verdict tests if executable tooling is introduced;
- `docs/reports/literature-sufficiency-audit.md` — human-readable evidence map, disagreements, limitations, and verdict;
- `artifacts/goals/G-1/decision.json` and `artifacts/goals/G-1/report.md` — machine-readable decision and criterion-to-evidence map.

Equivalent paths are allowed only if the goal report records them. Do not create the general project scaffold, evidence database, model stack, agent framework, or laboratory protocol in this goal.

## Deterministic and stateful behavior

- Replaying a frozen manifest and adjudicated ledger must return the same counts and verdict.
- Duplicate retrieval is idempotent and must not create another source, family, or arm.
- A corrected, retracted, or newly accessible source creates a versioned manifest event and invalidates affected screening/count artifacts before recomputation.
- Checkpoints occur after discovery, deduplication, title/abstract screening, full-text screening, family clustering, and adjudication; resume cannot skip an incomplete stage.
- Conflicting reviewer decisions remain unresolved until adjudicated and contribute zero to thresholds.
- Partial provider failure is recorded per query/source; required-coverage or saturation failure yields `AUDIT_INCOMPLETE`.
- Budget counters include queries, unique records, full-text assessments, citation waves, optional model calls, and reviewer adjudications.
- Unsupported formats or unavailable lawful access produce typed reasons, never fabricated metadata or silent exclusion.

## Authority boundaries

- Network access is read-only and limited to the frozen search sources, publisher/repository pages, and cited links.
- No paywall, robots, authentication, or rate-limit bypass is permitted.
- Credentials remain runtime-only and may not appear in queries, logs, fixtures, or artifacts.
- Source documents are untrusted data; embedded instructions and linked code are never executed.
- Full text is stored or redistributed only when the license permits it; otherwise retain metadata, locators, and lawful local-use hashes.
- Optional LLM assistance is limited to triage or structured proposals with model, prompt, seed/configuration, and budget recorded. Human adjudication controls Tier A status and the final verdict.
- This goal authorizes no physical experiment and no claim of material performance.

## Acceptance criteria

1. The versioned protocol freezes sources, queries, eligibility tiers, independence/arm rules, thresholds, budget, saturation, and adjudication before final screening.
2. The source manifest and screening ledger cover every discovered record, use stable deduplication, preserve lawful-access metadata, and contain no unresolved record silently counted as eligible.
3. Every potential Tier A record receives two independent screening decisions or one decision plus documented expert adjudication; disagreements remain visible.
4. Publication families, experimental arms, research-group independence, endpoint comparability, numeric-data availability, and core-covariate completeness are counted with exact locators and auditable derivations.
5. Offline fixtures demonstrate correct handling of eligible, ineligible, duplicate, derivative, contradictory, malformed, partial, inaccessible, and budget-exhausted inputs.
6. A frozen-manifest replay deterministically emits the same counts and exactly one allowed verdict, or `AUDIT_INCOMPLETE`, with every decision-matrix condition mapped to evidence.
7. The report distinguishes direct, transfer, and contextual evidence; discusses known positive and conflicting/null findings; identifies the smallest evidence gap preventing a stronger verdict; and makes no model-performance claim.
8. The search satisfies the saturation rule within budget. If it does not, the recorded outcome is `AUDIT_INCOMPLETE` and no downstream goal is marked eligible.
9. `artifacts/goals/G-1/report.md` maps criteria 1–8 to files, checks, and results and records every deviation or unresolved limitation.
10. The material-candidate ledger names each candidate, links its supporting records, separates formulation/material evidence from model-arm eligibility, and emits a deterministic provisional candidate verdict without authorizing physical execution.

## Stop conditions

- Stop with `AUDIT_INCOMPLETE` if lawful access, reviewer availability, source coverage, protocol integrity, or search budget prevents a defensible audit.
- Stop and amend the goal before continuing if screening reveals that the intervention or primary endpoint cannot be operationally defined as written.
- Do not begin G00 or any later goal until a substantive verdict is recorded and the corresponding G00 track is explicitly selected.

## Handoff

- `MODELABLE_NOW` makes G00 eligible to ratify the bounded modeling program and create its minimal scaffold.
- `EVIDENCE_SYNTHESIS_ONLY` makes G00 eligible only to ratify a synthesis-first charter and minimal corpus tooling; G05B–G08 remain blocked until a later evidence amendment passes the relevant gate.
- `REPLICATION_STUDY_REQUIRED` makes G00 eligible only to ratify a replication-first charter and insert a controlled-study-design goal; the software/modeling sequence G01–G10 remains blocked pending roadmap amendment.
- A paired result with `material_candidate_verdict=LAB_CANDIDATE_PLAUSIBLE` and `modelability_verdict=REPLICATION_STUDY_REQUIRED` makes G00 eligible to ratify only the pre-lab GP1–GP3 branch. GL1 and GL2 remain externally gated; GD1 remains blocked until reproducible physical results pass its data threshold.
- `AUDIT_INCOMPLETE` has no downstream handoff.
