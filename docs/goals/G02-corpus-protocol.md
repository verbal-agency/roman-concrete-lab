# G02 — Build the reproducible seed corpus and screening protocol

**Status:** proposed  
**Dependencies:** G01 complete  
**Advances:** establishes what evidence exists without contaminating later test sets

## Objective

Create a reproducible, rights-aware seed corpus for the ratified v1 scope, with a frozen search protocol, screening ledger, source-family deduplication, and a held-out evaluation partition selected before automated extraction is tuned.

## In scope

- database/search-source query strings, dates, filters, and result manifests;
- seeded primary papers and backward/forward citation-chaining records;
- title/abstract and full-text inclusion/exclusion criteria;
- PRISMA-like flow counts with machine-readable exclusion reasons;
- source/version hashes, DOI and other identifiers, access path, license class, and retrieval status;
- publication-family and shared-sample lineage detection;
- deterministic assignment to development, gold-benchmark, and sealed evaluation sets;
- metadata fixtures for unavailable, duplicate, retracted/corrected, malformed, and restricted sources.

## Excluded

Scientific value judgments beyond the protocol, full extraction, training models, bypassing paywalls, redistributing unauthorized text, and using the sealed set for prompt/schema tuning.

## Authority and side effects

Network retrieval is allowed only for hosts and source classes approved in G00. Rate limits, robots/access rules, and licenses must be respected. Raw restricted content stays outside version control; its manifest remains reproducible. No browser session cookies or credentials are serialized.

## Expected implementation surface

`src/roman_concrete_lab/corpus/`, `data/manifests/`, `fixtures/corpus/`, `tests/corpus/`, `docs/protocols/search-and-screening.md`, `docs/reports/corpus-flow.md`.

## Acceptance criteria

1. Re-running manifest construction from recorded results produces byte-stable normalized metadata and the same split assignments.
2. Every included/excluded record has a protocol version, decision, reason, actor, and timestamp.
3. Publication families and known shared sample lineages cannot cross the development/sealed boundary.
4. Restricted or unavailable sources remain representable without storing unauthorized content.
5. The sealed set is inaccessible to extraction-tuning code by default and a test proves the boundary.
6. Corpus-flow counts reconcile exactly with the screening ledger.
7. A second reviewer audits a preregistered sample and disagreements are adjudicated and reported.

## Verification evidence

`artifacts/goals/G02/report.md`, frozen manifest hash, query protocol, flow reconciliation test, split-leakage test, license summary, and review/adjudication log.

## Stop conditions

Block on an unresolved rights policy. Complete with a sparse-corpus warning if search results are small; corpus sufficiency is decided in G04, not concealed here.

