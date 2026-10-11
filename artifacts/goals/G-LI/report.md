# G-LI public-document ingestion and landscape remediation

**Status:** complete as an engineering intake goal; landscape gate remains `LANDSCAPE_INCOMPLETE`.
**Run:** `85bd2035956e0a96`
**Network/model/physical execution:** audited read-only public retrieval / none / prohibited

## Outcome

The intake attempted every audited relevant public-copy route in the G-LR manifest. It retained only hashes, locators, parser/page metadata, and a human review queue in tracked artifacts; raw PDFs remain in ignored `data/raw/gli/`.

`LANDSCAPE_INCOMPLETE` remains the only legal readiness result. Intake improves provenance and access visibility but does not perform scientific field extraction, lineage adjudication, contradiction resolution, or evidence promotion.

## Intake results

| Status | Count |
|---|---:|
| `FETCH_FAILED` | 4 |
| `INGESTED` | 2 |
| `OUT_OF_SCOPE` | 1 |
| `PUBLIC_LANDING_NO_PDF` | 1 |
| `RIGHTS_BLOCKED` | 2 |

## Route outcomes

| Source | Status | Route attempts |
|---|---|---:|
| `S04` | `FETCH_FAILED` | 1 |
| `S06` | `RIGHTS_BLOCKED` | 1 |
| `S11` | `FETCH_FAILED` | 3 |
| `S13` | `RIGHTS_BLOCKED` | 1 |
| `S15` | `INGESTED` | 1 |
| `S16` | `FETCH_FAILED` | 2 |
| `S17` | `FETCH_FAILED` | 2 |
| `S19` | `OUT_OF_SCOPE` | 0 |
| `S20` | `PUBLIC_LANDING_NO_PDF` | 1 |
| `S21` | `INGESTED` | 1 |

## Readiness blockers carried forward

- only 2/9 relevant public-route records have document hashes
- one or more relevant public routes remain failed, rights-blocked, landing-only, or OCR-required
- critical evidence fields still require human source mapping; G-LI does not infer facts
- study-family lineage adjudication remains pending from G-LR
- contradiction ledger remains pending from G-LR
- scientific screening adjudication remains pending from G-LR

## Acceptance evidence

| Criterion | Result | Evidence |
|---|---|---|
| 1. Scope derived from audited ledgers | PASS | scope hash and 10 route rows; 9 relevant rows attempted, 1 low-relevance row explicitly out of scope |
| 2. Exact-host, read-only policy | PASS | frozen policy hash, per-route outcomes, zero credentials/model calls |
| 3. Page-aware PDF intake | PASS for 2 PDFs | content/parser/page hashes and ignored cache keys for S15 and S21; failures remain typed |
| 4. Deduplication and replay | PASS | cache index, content-addressed files, duplicate/cache tests, offline run replay |
| 5. No payload in tracked artifacts | PASS | ledger/queue contain hashes and locators only; raw PDFs remain under ignored `data/raw/gli/` |
| 6. Landscape remediation verdict | PASS | `remediated-landscape.json` preserves `LANDSCAPE_INCOMPLETE` and names blockers |
| 7. Failure and boundary tests | PASS | 19 focused retrieval/ingestion tests |
| 8. G10R boundary | PASS | Phase-B execution remains unrun and its authority is unchanged |

## Authority boundary

No credentials, model calls, unrestricted crawling, OCR, external writes, scientific promotion, laboratory action, or G10R Phase B execution occurred. G10R remains frozen and requires a separate owner activation after this goal.

## Artifacts

- `data/manifests/public-document-ingestion.jsonl`
- `data/processed/public-document-review-queue.json`
- `artifacts/goals/G-LI/remediated-landscape.json`
- `artifacts/goals/G-LI/run.json`
- `data/raw/gli/` (ignored local cache only)
