# G-LI — Public-document ingestion and landscape remediation

**Status:** complete
**Dependencies:** G-LR complete with `LANDSCAPE_INCOMPLETE`; G00 `EXPLORATORY_PLATFORM`; the G-1 public-access register
**Advances:** converts lawfully public, relevant documents from the audited corpus into a replayable, reviewable evidence-intake substrate before any live active-investigation evaluation

## Objective

Build and run the bounded public-document intake layer. It must retrieve only already-audited lawfully public copies, retain raw payloads solely in ignored local storage, extract page-located native text without executing document content, and create a persistent review queue plus a provenance snapshot. It remediates the access/hash/extraction blockers in G-LR; it does not claim to complete scientific adjudication or create an immutable evidence store.

## Scope

- derive the intake scope from `data/manifests/landscape-sources.jsonl` and `data/manifests/literature-sufficiency-access-register.csv`;
- include every source with a recorded public-copy route whose relevance is `candidate`, `transfer_method`, or `context_only`; retain excluded low-relevance records as out of scope with a reason;
- fetch only exact hosts already marked `PUBLIC` in `fixtures/investigation/source-policy.json`, rechecking redirects and payload limits;
- resolve a declared PDF link from an audited public landing page only when it remains on an exact permitted host; never crawl, search, or follow arbitrary links;
- cache permitted raw PDFs and native extracted text only under ignored `data/raw/gli/`; commit hashes, page counts, extraction status, locators, and bounded page-selection metadata, never full text;
- deduplicate by content hash while preserving every source-to-document route; issue `OCR_REQUIRED`, `FETCH_FAILED`, `RIGHTS_BLOCKED`, `MALFORMED_DOCUMENT`, `PUBLIC_LANDING_NO_PDF`, or `REVIEW_REQUIRED` rather than fabricating text;
- create a deterministic review queue that has one source/document mapping and source-located critical-field obligations for every successfully extracted document;
- rerun the landscape readiness calculation with the new intake snapshot, preserving `LANDSCAPE_INCOMPLETE` until its existing scientific, lineage, contradiction, and review blockers actually clear.

## Exclusions

LLM or agent extraction, paywall bypass, Sci-Hub, credential use, unrestricted crawling, OCR, automatic fact promotion, scientific adjudication, predictive modeling, laboratory work, and G10R Phase B execution are excluded. A source-located intake record or review card is not immutable evidence.

## Contracts and legal states

The canonical `PublicDocumentIngestionRecord` has `schema_version`, `record_id`, `source_record_id`, `source_locator`, `document_locator`, `access_class`, `rights_state`, `content_hash`, `parser`, `page_count`, `extraction_status`, `raw_cache_key`, `route_ids`, per-route `route_attempts`, `review_status`, and `failure_detail`. Legal `ingestion_status` values are `INGESTED`, `DUPLICATE_CONTENT`, `OCR_REQUIRED`, `FETCH_FAILED`, `RIGHTS_BLOCKED`, `MALFORMED_DOCUMENT`, `PUBLIC_LANDING_NO_PDF`, `PUBLIC_LANDING_AMBIGUOUS`, and `OUT_OF_SCOPE`. Legal review states are `PENDING_HUMAN_REVIEW`, `NOT_READY_FOR_REVIEW`, and `OUT_OF_SCOPE`.

A successful row requires a content hash, permitted document locator, parser, positive page count, ignored-cache key, and source-located page selection. A duplicate must reference the canonical ingested record. A failure row must retain its route and precise failure state but no unauthorized payload. A row may never become `ImmutableEvidence`, `ADMISSIBLE_FOR_REVIEW`, or a performance claim through this goal.

| Condition | Required result |
|---|---|
| direct permitted PDF | hash, raw-cache key, page-located extraction, `INGESTED`, and human-review queue entry |
| permitted landing page with one declared permitted PDF | resolve once, then apply the direct-PDF behavior |
| landing page with no declared permitted PDF | `PUBLIC_LANDING_NO_PDF`; no broad link crawling |
| redirect, host, rights, byte, or content-type policy failure | `RIGHTS_BLOCKED` with no retained prohibited payload |
| malformed or encrypted PDF | `MALFORMED_DOCUMENT` with no fallback parser/OCR |
| native text absent | `OCR_REQUIRED`, no invented text, and no review-ready field claim |
| equal document hash from two sources | one canonical raw cache entry; route links retained; later row `DUPLICATE_CONTENT` |
| rerun with same manifest/policy and cached raw documents | byte-stable ledger/snapshot; no network request |
| source/policy/route hash changes | invalidate the prior run and require a new run ID |

## Expected implementation surface

- `schemas/public-document-ingestion.schema.json`;
- `src/roman_concrete_lab/ingestion/` for policy-bound intake, cache, deduplication, page selection, and replay validation;
- `tools/ingestion/replay.py`;
- `data/manifests/public-document-ingestion.jsonl` and `data/processed/public-document-review-queue.json` (hashes/locators only);
- `artifacts/goals/G-LI/run.json` and `report.md`, plus `docs/reports/public-document-ingestion.md`;
- `fixtures/ingestion/` and `tests/ingestion/test_public_document_ingestion.py`.

## Acceptance criteria

1. The intake scope is mechanically derived from the G-LR source manifest and G-1 access register; every public-route record is either attempted or explicitly `OUT_OF_SCOPE` with a recorded relevance reason.
2. Every attempted route is governed by the frozen exact-host policy, uses read-only GET with no credentials, rechecks redirects, and records a deterministic status without retaining unauthorized content.
3. Every successful PDF has content/page hashes, parser/version, exact page locators, an ignored raw-cache key, and a review queue entry; empty native text, malformed/encrypted files, and landing-page ambiguity use the prescribed non-success states.
4. Content duplicates create one canonical cache/document identity while retaining each discovered route; reruns reuse cached content without a second fetch.
5. The committed ledger, queue, and run manifest contain no PDF payload or full extracted text, are schema-valid, and replay byte-stably from the cache/fixtures.
6. The remediated landscape report reconciles attempted, ingested, duplicate, pending-review, and failed counts; it states the remaining G-LR blockers and emits only `LANDSCAPE_READY` or `LANDSCAPE_INCOMPLETE` under the existing rule.
7. Focused tests cover direct PDF, landing resolution, duplicate, empty native text, malformed PDF, policy failure, cache replay, changed-input invalidation, and no-payload artifact boundaries.
8. G10R Phase B remains unexecuted and cannot use G-LI output to widen its frozen hosts, cases, source policy, or evidence-promotion authority.

## Authority and stop conditions

Network access is read-only and permitted only for the exact audited public hosts and direct or declared-PDF routes above. No credentials, provider calls, external writes, or laboratory action are authorized. Stop an individual route before retaining data if rights, host, redirect, byte, or parser policy fails; record the failure and continue with other routes. Complete the goal with `LANDSCAPE_INCOMPLETE` when remaining scientific-review, source-route, lineage, contradiction, or saturation requirements remain unmet. Only a later explicit G10R activation can authorize its Phase B network/model treatment.

## Criterion-to-evidence map

| Criterion | Evidence |
|---|---|
| 1–2 | intake manifest, source-policy hash, scope/relevance report, policy tests |
| 3–4 | ingestion ledger, review queue, cache/dedup/replay tests |
| 5 | schema validation, no-payload scan, byte-stable replay manifest |
| 6 | `docs/reports/public-document-ingestion.md` and `artifacts/goals/G-LI/run.json` |
| 7 | `tests/ingestion/test_public_document_ingestion.py` |
| 8 | G10R phase-A manifest comparison and authority scan |
