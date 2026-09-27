# G-1 literature sufficiency audit report

**Protocol:** `g1.1-public-expansion`  
**Execution date:** 2026-09-27  
**Decision question:** whether direct literature supports study-grouped estimation of a modern terrestrial hot-mixed quicklime/lime-pozzolan intervention on functional water-transport recovery after controlled cracking.

## Verdict

**Provisional finding:** `REPLICATION_STUDY_REQUIRED`  
**Recorded G-1 state:** `AUDIT_INCOMPLETE` pending qualified human adjudication

The expanded lawful search materially changes the evidence map: it found a second provisional Tier A family, the 2025 Utah State University/Utah Department of Transportation quicklime bridge-deck program. The thesis and final report are one experimental lineage, not two independent replications. The expanded record still contains only two provisional direct families, three conservative direct dose-contrast arms, and zero independent external replications. That remains far below the thresholds for a literature-trained predictive model or experiment ranker.

The new family is a genuine reason to revise the earlier “one direct family” statement, but not a reason to reverse the go/no-go decision. G-1 remains blocked because Tier A eligibility, family independence, and the final verdict require qualified human adjudication; Scopus, Web of Science, and ProQuest were access gaps without an authenticated session. No downstream goal is authorized by this report.

## Coverage and stopping

The amended public/lawful search screened 34 deduplicated records: the original 24 plus 10 records from expanded quicklime/lime-clast, hot-mix, thesis/repository, and exact-title/DOI searches. Twenty-four records received full-text or full-preview assessment. Two expanded citation/search waves were run after the new Utah lineage was found; neither produced another provisional Tier A family. The second wave produced only derivative or adjacent natural-hydraulic-lime, cement-based, process, patent, and contextual records. This satisfies the amended public-search saturation rule for the reachable sources, while the report continues to disclose subscription access gaps.

Crossref and OpenAlex API discovery returned indexed records. Semantic Scholar's API returned HTTP 429; lawful indexed PDFs/search pages were used as alternate discovery. Repository and publisher pages supplied public copies for the Utah thesis/report, Bath and Sheffield records, and other adjacent studies. No Sci-Hub or equivalent unauthorized source was accessed.

## Deterministic counts

| Quantity | Count | Threshold / interpretation |
|---|---:|---|
| Deduplicated screened records | 34 | Within the amended 500-record cap |
| Full-text/full-preview assessments | 24 | Within the amended 120-record cap |
| Provisional independent Tier A study families | 2 | `MODELABLE_NOW` requires 5; replication-first requires at least 3 |
| Provisional Tier A extractable arms | 3 | `MODELABLE_NOW` requires 75; replication-first requires at least 30 |
| Tier A families with functional endpoint | 2 | `MODELABLE_NOW` requires at least 3 comparable families |
| Tier A external replications | 0 | Required for `MODELABLE_NOW`; absence triggers replication-first |
| Tier A families with ≥70% core-covariate completeness | 0 | No predictive release basis |

The first family is Seymour et al. (2023), counted as one conservative quicklime-versus-quicklime-free core contrast. The second is the Utah State/UDOT bridge-deck lineage, counted as two conservative quicklime dose contrasts (2% and 4% versus 0%); crack-width and exposure conditions are not counted as additional arms. The Utah report describes controlled 100–550 µm cracks and a falling-head water-flow/permeability test on selected specimens after surface closure. That selected-specimen design, and whether it is a sufficiently comparable primary endpoint, are explicit human-adjudication questions rather than silently resolved assumptions.

## What the expanded search found

### Provisional Tier A families

- **Seymour et al. (2023), DOI `10.1126/sciadv.add1602`.** Modern Roman-inspired hot-mixed mortar with quicklime-bearing and lime-clast-free control material, controlled re-mated cracking, and a continuous water-flow endpoint. Exact locators in the local ledger: S01 PDF pp. 4, 6, and 9–10.
- **Nazari (2025), DOI `10.26076/80c4-45f6`, and the UDOT report “Developing and Characterizing Self-Healing Concrete for Bridge Decks.”** The public thesis describes C-Q 0%, C-Q 2%, and C-Q 4% mixtures, 100–550 µm precracked ranges, cyclic water/air-dry and deicing-salt/air-dry exposures, and internal healing assessed by water-flow tests, UPV, and SEM-EDS. The UDOT report documents the exothermic quicklime/hot-mixing process and falling-head permeability method (pp. 44–49), controlled crack widths (pp. 51–52), and results (pp. 75–80). The thesis and report are derivative publications from one lineage and cannot be counted as independent replication.

### Tier B: useful but not direct

- **Morris (2025), University of Bath thesis.** Open hot-mix and free-lime work with observed crack healing and pore-structure evidence, but no directly comparable controlled water-flow recovery contrast in the accessible record.
- **Hetherington/Laycock repository paper.** Hot-mixed versus lime-putty mortars with pozzolans and durability/property testing, but no controlled crack-healing functional endpoint.
- **Kamaruzaman and Si (2026), DOI `10.24191/scl.v20i2.10259`.** Quicklime plus silica fume in cement-based materials with crack repair/impermeability claims, but not a process-matched hot-mixed lime-pozzolan mortar.
- **Grosso Giordano et al. (2024/2025), Qureshi et al. (2018), De Nardi et al. (2017), Yildirim et al. (2015), Villa Bayan and Diaz (2025), and other lime/self-healing records.** These provide endpoint, mechanism, or measurement transfer evidence, but use different binders, additives, crack protocols, or outcomes; derivative publications remain clustered rather than counted as independent families.

### Tier C/D: context or excluded

The RILEM hot-lime review (DOI `10.1617/s11527-023-02157-1`) remains important evidence that water/CaO ratio, slaking temperature, mixing, storage, and provenance can materially change hot-lime mortar. Archaeological studies, process-only hot-mix papers, simulations, patents, and unrelated self-healing systems remain contextual or excluded. They do not create modern direct performance arms.

## Why the decision is still replication-first

The new Utah family improves feasibility but does not supply independence. The two direct lineages use different material systems, crack protocols, conditioning regimes, and flow measurements; one is a modern Roman-inspired mortar and the other is quicklime aggregate concrete for bridge-deck conditions. Pooling them as if they identify one stable treatment effect would confound intervention with formulation, specimen geometry, exposure, and measurement selection. The Utah report also tests water flow only on selected specimens with complete surface closure, which limits comparability to a continuously monitored flow endpoint.

The conservative conclusion is therefore unchanged: do not build a literature-trained predictor or ranker. First run an independently batched, process-matched replication that pre-specifies quicklime/hot-mix versus a slaked-lime or quicklime-free control, crack-width band, exposure schedule, continuous water-flow/permeability endpoint, specimen-level replication, and the rule for handling surface closure versus through-depth sealing.

## Limitations and retained uncertainty

- Qualified human adjudication has not been supplied; all potential Tier A records remain `pending` and contribute zero to any final threshold until adjudicated.
- Scopus, Web of Science, and ProQuest were not accessible without an authenticated subscription session. This is an access limitation, not evidence that those databases contain no additional records.
- Semantic Scholar API coverage was rate-limited; indexed lawful results were screened, but complete API recall is not claimed.
- Several adjacent publisher records remain metadata/abstract-only and cannot count as extractable Tier A arms.
- The search is a bounded sufficiency audit, not a meta-analysis and not evidence of material superiority.

## Handoff

G00 is not yet eligible. After a qualified reviewer adjudicates S01 and S25/S26 as a single Utah family, the likely route is the `REPLICATION_STUDY_REQUIRED` track: ratify a replication-first charter, add a controlled-study-design goal, and block G01–G10 until that roadmap amendment is approved. No physical protocol or safety authorization is created by this report.

## Source links

- [Seymour et al. (2023)](https://doi.org/10.1126/sciadv.add1602)
- [Nazari thesis (2025)](https://digitalcommons.usu.edu/etd2023/669/)
- [UDOT final report (2025)](https://rosap.ntl.bts.gov/view/dot/88347/dot_88347_DS1.pdf)
- [Morris thesis (2025)](https://researchportal.bath.ac.uk/en/studentTheses/the-impact-of-lime-mortar-mix-design-on-its-environmental-resilie/)
- [Hot-mixed/lime-putty repository paper](https://shura.shu.ac.uk/25573/)
- [Kamaruzaman and Si (2026)](https://doi.org/10.24191/scl.v20i2.10259)
- [RILEM hot-lime review (2023)](https://doi.org/10.1617/s11527-023-02157-1)
