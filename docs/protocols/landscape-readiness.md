# Landscape-readiness protocol

**Protocol version:** `glr.1-landscape-map`
**Frozen:** 2026-10-09
**Base protocol:** `g1.3-public-access-audit`

## Decision question

Has the lawful, bounded literature search produced a source-located evidence map that is complete enough within the declared modern-terrestrial Roman-inspired mortar support region to generate discovery-grade hypotheses, or must outputs remain provisional evidence-gap work?

## Search boundary

G-LR inherits the frozen G-1 source boundary and does not silently widen it: Crossref, OpenAlex, Semantic Scholar/indexed results when reachable, Unpaywall or equivalent open-access indexes, CORE/OpenAIRE and institutional repositories, publisher/repository pages, theses and dissertations, preprint servers, technical reports, author/institutional pages, and backward/forward citation chaining. Scopus, Web of Science, ProQuest, and authenticated library systems remain provider-coverage gaps unless separately activated. Paywall bypass, Sci-Hub, credential persistence, and unauthorized retention are prohibited.

The G-1 query families and citation-chain waves are the frozen search basis. Saturation requires two successive waves adding no new Tier-A family and fewer than 5% new potentially eligible records, with the public-access exhaustion pass complete and no `publisher_metadata` record left unaudited.

## Evidence map contract

Each source is joined to its screening row, study family, access/version record, and candidate references when present. The map distinguishes:

- `REPORTED_SCREENING`: a field explicitly present in the frozen screening ledger;
- `DERIVED_LINEAGE`: a deterministic family, derivative, or candidate linkage;
- `UNRESOLVED`: the field is not normalized in the current evidence packet;
- `NOT_REPORTED`: the source was inspected or assessed and the field is absent;
- `EVIDENCE_PENDING`: access or extraction is insufficient for a claim.

Required field dimensions are material/process, intervention, comparator, damage/crack protocol, exposure, timepoint, endpoint, mechanism, null/negative result, contradiction, study lineage, and exact locator. `NOT_REPORTED`, `UNRESOLVED`, and `EVIDENCE_PENDING` are never treated as zero or as evidence of absence.

## Review and authority

The structural second-review sample is selected deterministically from direct, transfer, preprint, and unavailable-source strata. It checks identity joins, access state, exact locators, family references, and missingness semantics; it is not a substitute for qualified scientific adjudication of Tier-A eligibility. Any scientific disagreement remains visible and pending. No model, agent, or replay tool may be the final eligibility authority.

## Readiness rule

`LANDSCAPE_READY` requires: frozen protocol; reconciled source/screening/family IDs; complete access/version state for the declared record set; source-located critical-field extraction with explicit missingness; lineage and contradiction review; second-review sample audit; and a reproducible saturation determination. Otherwise the result is `LANDSCAPE_INCOMPLETE` with named blockers and a permitted-output boundary.
