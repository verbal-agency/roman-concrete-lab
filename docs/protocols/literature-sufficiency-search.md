# G-1 literature sufficiency search protocol

**Protocol version:** `g1.2-material-candidate`
**Amended/frozen:** 2026-09-27  
**Decision questions:** (1) whether inspectable evidence supports handing a materially specified Roman-concrete candidate to a qualified laboratory, and (2) separately, whether direct evidence supports study-grouped estimation of a modern terrestrial hot-mixed quicklime/lime-pozzolan intervention on functional water-transport recovery after controlled cracking.

## Search coverage

The audit uses read-only discovery from Crossref, OpenAlex, Semantic Scholar, CORE/OpenAIRE/repository indexes when available, publisher/repository pages, theses/dissertations that are lawfully accessible, and backward/forward citation chaining. Scopus, Web of Science, ProQuest, and institutional library search are recorded as access-gap sources unless the user supplies lawful authenticated access. No paywall, authentication, robots, rate-limit, or copyright bypass is permitted. Sci-Hub and equivalent unauthorized copies are explicitly excluded.

The amended material-candidate pass searches four evidence streams separately: modern experiments; archaeological/residue/material-characterization evidence; theses, reports, proceedings, and patents that expose material identity or process constraints; and citation/author chains. A paper may establish that a candidate exists without qualifying as a Tier A model arm.

Seed sources are Seymour et al. (2023, DOI `10.1126/sciadv.add1602`), the RILEM hot-lime review (2023, DOI `10.1617/s11527-023-02157-1`), Grosso Giordano et al. (2024, DOI `10.1016/j.conbuildmat.2024.136603`), and Grosso Giordano et al. (2025, DOI `10.1016/j.jobe.2025.113234`). Seed status does not confer eligibility.

Frozen query families:

1. `("hot mixing" OR "hot lime" OR quicklime OR "unslaked lime") AND (mortar OR concrete) AND (self-healing OR crack OR permeability OR "water flow")`
2. `(lime OR lime-pozzolan OR metakaolin) AND (mortar OR concrete) AND (crack healing OR self-healing) AND (permeability OR sorptivity OR "water flow")`
3. `(Roman OR ancient OR Pompeii) AND (mortar OR concrete) AND (quicklime OR "hot mixing" OR lime clast)`
4. Citation chaining from each seed and every candidate Tier A/B record.
5. `("lime clast" OR "blocky quicklime" OR "lump quicklime" OR "unslaked lime") AND (mortar OR concrete) AND (healing OR crack OR permeability)`.
6. `("hot-mixed mortar" OR "hot lime mortar" OR "hot-mixed lime") AND (self-healing OR "water flow" OR permeability OR crack)`.
7. `(thesis OR dissertation OR repository OR preprint) AND (quicklime OR "hot mixing") AND (mortar OR concrete) AND (healing OR permeability)`.
8. Exact-title, DOI, author, and reference-list searches for every record that is direct-adjacent, inaccessible, or potentially derivative.
9. `("Roman concrete" OR "Roman-inspired concrete" OR "lime clast") AND (formulation OR mix OR specimen OR residue OR composition)`.
10. `("quicklime" OR "calcium oxide") AND ("self-healing" OR "crack healing") AND (concrete OR mortar) AND (thesis OR dissertation OR report OR patent)`.
11. `(archaeological OR ancient OR Roman) AND ("lime clast" OR quicklime OR "calcite-filled crack") AND (residue OR mineralogy OR petrography OR spectroscopy)`.
12. Exact-title, DOI, author, and reference-list searches for every material-candidate record, including records that fail the functional-endpoint test.

Language is not an exclusion when a reliable translation path and inspectable methods/results exist. Abstract-only records can remain in the screening ledger but cannot count as extractable Tier A arms.

## Inclusion and counting rules

Tier A requires all directness conditions in the G-1 goal: modern terrestrial mortar/mortar-like specimen; explicit quicklime/hot-mixing intervention and interpretable comparator; controlled cracking or defined damage; functional water-flow, permeability, or sorptivity recovery endpoint; and identifiable arms/protocol/specimen counts.

An independent study family is a distinct experimental material lineage and research team. A publication that reuses specimens, datasets, or an originating experimental lineage is derivative, not independent. An experimental arm is a deliberately distinct treatment/control condition; specimens, crack segments, images, repeated measurements, and timepoints are never arms.

Tier B records can inform methods or hypotheses but do not count toward G-1 thresholds. Tier C contextual records and Tier D exclusions remain in the ledger with reasons.

## Material-candidate gate

The candidate pass is separate from modelability. `LAB_CANDIDATE_PLAUSIBLE` requires all of the following to be inspectable or explicitly bounded: (a) a named material or formulation envelope, artifact class, or process identity; (b) at least one lawful source with methods/results or authenticated material evidence; (c) a comparator, baseline, or artifact rationale that makes a lab question falsifiable; (d) at least one measurable property or functional endpoint; and (e) a qualified-lab handoff path with safety and authority requirements recorded. The gate does not authorize physical execution and does not permit inferring a recipe, proportions, ignition system, or deployment method from incomplete evidence.

`LAB_CANDIDATE_NOT_ESTABLISHED` applies when the evidence is only historical assertion, an uninspectable abstract, an unbounded ingredient list, or a material claim with no falsifiable measurement path. Candidate status remains provisional until qualified human adjudication confirms the evidence and family relationships.

Potential Tier A records require two context-isolated screening passes or one pass plus documented expert adjudication. Any disagreement remains `pending` and contributes zero to thresholds until resolved. No model or LLM may be the final eligibility authority.

## Budget and saturation

Amended expansion limits: 500 deduplicated records, 120 full-text/preview assessments, and four complete citation-chaining waves across the expanded source families. A budget limit reached before saturation produces `AUDIT_INCOMPLETE`. The expansion is a public/lawful-access search, not a claim of subscription-database exhaustiveness.

Saturation requires two successive waves adding no new Tier A family and fewer than 5% new potentially eligible records relative to the prior screened unique-record total. The report must state which public providers were reachable, which subscription sources were access gaps, and whether any early stopping rule was invoked.

## Decision thresholds

`MODELABLE_NOW`: at least 5 independent Tier A families, 75 extractable arms, comparable functional endpoint in at least 3 families, external replication, defensible treatment/control identity, at least 70% numeric primary outcome/core-covariate completeness, and feasible study-grouped evaluation.

`EVIDENCE_SYNTHESIS_ONLY`: complete audit with enough direct evidence for descriptive synthesis or design, normally at least 3 Tier A families and 30 arms, but one or more modelability conditions fail and no replication-first condition is triggered.

`REPLICATION_STUDY_REQUIRED`: fewer than 3 Tier A families, fewer than 30 Tier A arms, no independent replication, uninterpretable intervention/control contrast, or incompatible protocols/endpoints.

`AUDIT_INCOMPLETE`: required coverage, access, adjudication, saturation, or protocol integrity is not achieved. The paired candidate result may still be reported provisionally while the overall goal remains incomplete.

The most conservative applicable verdict wins.
