"""Replayable public-PDF intake without evidence promotion or raw-text artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Protocol
from urllib.parse import urljoin

from jsonschema import validate

from src.roman_concrete_lab.retrieval.contracts import PolicyBlocked, SourcePolicy, canonical, digest
from src.roman_concrete_lab.retrieval.network import NetworkUnavailable
from src.roman_concrete_lab.retrieval.pdf import DocumentExtractionError, PARSER_ID, extract_pdf, select_relevant_page_spans


SCHEMA_VERSION = "1.0"
INGESTION_VERSION = "gli.1-public-document-intake"
REVIEW_FIELDS = [
    "material_process", "intervention", "comparator", "damage_crack_protocol",
    "exposure", "timepoint", "endpoint", "mechanism", "null_negative_result",
    "contradiction", "study_lineage",
]
IN_SCOPE_RELEVANCE = {"candidate", "transfer_method", "context_only"}


class PayloadFetcher(Protocol):
    def fetch_public_payload(self, locator: str) -> dict[str, Any]: ...


class _DeclaredPdfParser(HTMLParser):
    """Accept only explicit publisher/repository PDF declarations, never arbitrary anchors."""

    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value for key, value in attrs if value is not None}
        if tag == "meta" and values.get("name", "").lower() in {"citation_pdf_url", "pdf_url"}:
            if values.get("content"):
                self.hrefs.append(values["content"])
        if tag == "link" and values.get("type", "").lower() == "application/pdf" and values.get("href"):
            self.hrefs.append(values["href"])


def _sha256(payload: bytes | str) -> str:
    value = payload if isinstance(payload, bytes) else payload.encode("utf-8")
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_schema(root: Path) -> dict[str, Any]:
    return _json(root / "schemas/public-document-ingestion.schema.json")


def validate_ingestion_record(record: dict[str, Any], *, schema: dict[str, Any]) -> None:
    validate(record, schema)
    status = record["ingestion_status"]
    successful = status in {"INGESTED", "DUPLICATE_CONTENT", "OCR_REQUIRED"}
    if successful and not record["content_hash"]:
        raise ValueError(f"{status} requires content_hash")
    if status == "INGESTED":
        if not record["raw_cache_key"] or not record["selected_pages"]:
            raise ValueError("INGESTED requires raw cache and selected page locators")
        if record["review_status"] != "PENDING_HUMAN_REVIEW":
            raise ValueError("INGESTED must enter the human review queue")
    if status == "DUPLICATE_CONTENT" and not record.get("canonical_record_id"):
        raise ValueError("DUPLICATE_CONTENT requires canonical_record_id")
    if status == "OCR_REQUIRED" and record["review_status"] != "NOT_READY_FOR_REVIEW":
        raise ValueError("OCR_REQUIRED cannot enter the native-text review queue")
    if status == "OUT_OF_SCOPE" and record["review_status"] != "OUT_OF_SCOPE":
        raise ValueError("OUT_OF_SCOPE requires OUT_OF_SCOPE review state")


def build_scope(*, landscape_sources: Path, access_register: Path) -> list[dict[str, Any]]:
    """Join source records to audited access routes without making new relevance judgments."""
    access: dict[str, dict[str, str]] = {}
    with access_register.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            access[row["record_id"]] = row
    sources = [json.loads(line) for line in landscape_sources.read_text(encoding="utf-8").splitlines() if line.strip()]
    scope = []
    for source in sources:
        record_id = source["record_id"]
        row = access.get(record_id, {})
        urls = source.get("access", {}).get("public_copy_urls") or []
        if not urls:
            continue
        relevance = row.get("decision_relevance", "unclassified")
        in_scope = relevance in IN_SCOPE_RELEVANCE
        scope.append({
            "source_record_id": record_id,
            "source_locator": source["canonical_citation"]["locator"],
            "title": source["canonical_citation"]["title"],
            "relevance": relevance,
            "route_ids": urls,
            "in_scope": in_scope,
            "scope_reason": "audited relevant public-copy route" if in_scope else f"relevance={relevance} is outside G-LI scope",
        })
    return sorted(scope, key=lambda item: item["source_record_id"])


class PublicDocumentIngestor:
    """Intake documents through a policy-bound fetcher; raw bytes stay in ignored storage."""

    def __init__(
        self,
        *,
        policy: SourcePolicy,
        fetcher: PayloadFetcher,
        schema: dict[str, Any],
        raw_cache_dir: Path,
        question: str,
        max_selected_characters: int = 12_000,
    ) -> None:
        self.policy = policy
        self.fetcher = fetcher
        self.schema = schema
        self.raw_cache_dir = raw_cache_dir
        self.question = question
        self.max_selected_characters = max_selected_characters
        self.raw_cache_dir.mkdir(parents=True, exist_ok=True)
        self._index_path = self.raw_cache_dir / "index.json"
        self._index = self._load_index()

    def _load_index(self) -> dict[str, Any]:
        if not self._index_path.exists():
            return {"documents": {}, "sources": {}}
        value = _json(self._index_path)
        if not isinstance(value.get("documents"), dict) or not isinstance(value.get("sources"), dict):
            raise ValueError("malformed ignored public-document cache index")
        return value

    def _save_index(self) -> None:
        self._index_path.write_text(canonical(self._index) + "\n", encoding="utf-8")

    def _empty_record(self, item: dict[str, Any], *, status: str, detail: str | None, document_locator: str | None = None, route_attempts: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "record_id": f"PDI-{item['source_record_id']}",
            "source_record_id": item["source_record_id"],
            "source_locator": item["source_locator"],
            "document_locator": document_locator,
            "access_class": "PUBLIC",
            "rights_state": "BLOCKED" if status == "RIGHTS_BLOCKED" else "PERMITTED",
            "content_hash": None,
            "parser": None,
            "page_count": 0,
            "extraction_status": "NOT_ATTEMPTED",
            "raw_cache_key": None,
            "route_ids": item["route_ids"],
            "route_attempts": route_attempts or [],
            "ingestion_status": status,
            "review_status": "OUT_OF_SCOPE" if status == "OUT_OF_SCOPE" else "NOT_READY_FOR_REVIEW",
            "selected_pages": [],
            "failure_detail": detail,
            "canonical_record_id": None,
        }

    def _cached_payload(self, source_id: str) -> tuple[str, bytes] | None:
        entry = self._index["sources"].get(source_id)
        if not entry:
            return None
        path = self.raw_cache_dir / entry["raw_cache_key"]
        if not path.exists():
            return None
        return entry["document_locator"], path.read_bytes()

    def _declared_pdf(self, *, landing_locator: str, payload: bytes) -> tuple[str | None, str | None]:
        parser = _DeclaredPdfParser()
        parser.feed(payload.decode("utf-8", errors="replace"))
        candidates = sorted({urljoin(landing_locator, href) for href in parser.hrefs})
        permitted = []
        for candidate in candidates:
            try:
                self.policy.decide(candidate, fetch_content=True)
            except PolicyBlocked:
                continue
            permitted.append(candidate)
        if not permitted:
            return None, "PUBLIC_LANDING_NO_PDF"
        if len(permitted) != 1:
            return None, "PUBLIC_LANDING_AMBIGUOUS"
        return permitted[0], None

    def _fetch_payload(self, locator: str) -> dict[str, Any]:
        budget = getattr(self.fetcher, "budget", None)
        if budget is not None:
            budget.debit(document_fetches=1)
        return self.fetcher.fetch_public_payload(locator)

    def _fetch_pdf(self, route: str) -> tuple[str, bytes] | tuple[None, str]:
        response = self._fetch_payload(route)
        locator = str(response["locator"])
        content_type = str(response["content_type"]).split(";", 1)[0].lower()
        payload = response["payload"]
        if content_type == "application/pdf":
            return locator, payload
        if content_type not in {"text/html", "application/xhtml+xml"}:
            return None, "RIGHTS_BLOCKED"
        declared, landing_status = self._declared_pdf(landing_locator=locator, payload=payload)
        if landing_status:
            return None, landing_status
        resolved = self._fetch_payload(declared)
        resolved_type = str(resolved["content_type"]).split(";", 1)[0].lower()
        if resolved_type != "application/pdf":
            return None, "RIGHTS_BLOCKED"
        return str(resolved["locator"]), resolved["payload"]

    def _cache_pdf(self, *, source_id: str, locator: str, payload: bytes, content_hash: str) -> str:
        key = f"{content_hash[7:]}.pdf"
        path = self.raw_cache_dir / key
        if not path.exists():
            path.write_bytes(payload)
        self._index["sources"][source_id] = {"document_locator": locator, "raw_cache_key": key, "content_hash": content_hash}
        self._index["documents"].setdefault(content_hash, {"raw_cache_key": key, "canonical_record_id": f"PDI-{source_id}"})
        self._save_index()
        return key

    def ingest(self, scope: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        records: list[dict[str, Any]] = []
        canonical_by_hash: dict[str, str] = {}
        for item in scope:
            if not item["in_scope"]:
                record = self._empty_record(item, status="OUT_OF_SCOPE", detail=item["scope_reason"])
                validate_ingestion_record(record, schema=self.schema)
                records.append(record)
                continue
            try:
                route_attempts: list[dict[str, Any]] = []
                cached = self._cached_payload(item["source_record_id"])
                if cached:
                    document_locator, payload = cached
                    route_attempts = [{"locator": document_locator, "status": "PDF_RETRIEVED", "detail": None}]
                else:
                    document_locator = None
                    payload = None
                    last_status = "FETCH_FAILED"
                    last_detail = "no permitted route returned a PDF"
                    for route in item["route_ids"]:
                        try:
                            outcome = self._fetch_pdf(route)
                            if outcome[0] is not None:
                                route_attempts.append({"locator": route, "status": "PDF_RETRIEVED", "detail": None})
                                document_locator, payload = outcome
                                break
                            last_status = outcome[1]
                            last_detail = f"route {route}: {outcome[1]}"
                            route_attempts.append({"locator": route, "status": outcome[1], "detail": last_detail})
                        except PolicyBlocked as exc:
                            last_status, last_detail = "RIGHTS_BLOCKED", str(exc)
                            route_attempts.append({"locator": route, "status": last_status, "detail": last_detail})
                        except NetworkUnavailable as exc:
                            last_status, last_detail = "FETCH_FAILED", str(exc)
                            route_attempts.append({"locator": route, "status": last_status, "detail": last_detail})
                    if payload is None or document_locator is None:
                        record = self._empty_record(item, status=last_status, detail=last_detail, route_attempts=route_attempts)
                        validate_ingestion_record(record, schema=self.schema)
                        records.append(record)
                        continue
                content_hash = _sha256(payload)
                try:
                    document = extract_pdf(
                        payload,
                        locator=document_locator,
                        max_pages=int(self.policy.record["request_policy"]["max_pdf_pages"]),
                        max_characters=int(self.policy.record["request_policy"]["max_extracted_characters"]),
                    )
                except DocumentExtractionError as exc:
                    record = self._empty_record(item, status="MALFORMED_DOCUMENT", detail=str(exc), document_locator=document_locator, route_attempts=route_attempts)
                    validate_ingestion_record(record, schema=self.schema)
                    records.append(record)
                    continue
                raw_cache_key = self._cache_pdf(
                    source_id=item["source_record_id"], locator=document_locator, payload=payload, content_hash=content_hash
                )
                record_id = f"PDI-{item['source_record_id']}"
                canonical_record_id = canonical_by_hash.get(content_hash) or self._index["documents"][content_hash]["canonical_record_id"]
                if content_hash not in canonical_by_hash:
                    canonical_by_hash[content_hash] = canonical_record_id
                if canonical_record_id != record_id:
                    status, review, selected = "DUPLICATE_CONTENT", "NOT_READY_FOR_REVIEW", []
                elif document["extraction_status"] == "OCR_REQUIRED":
                    status, review, selected = "OCR_REQUIRED", "NOT_READY_FOR_REVIEW", []
                else:
                    status, review = "INGESTED", "PENDING_HUMAN_REVIEW"
                    selected = [
                        {key: page[key] for key in ("page_number", "locator", "text_hash", "excerpt_text_hash")}
                        for page in select_relevant_page_spans(
                            document, question=self.question, title=item["title"], max_characters=self.max_selected_characters
                        )
                    ]
                    if not selected:
                        status, review = "OCR_REQUIRED", "NOT_READY_FOR_REVIEW"
                record = {
                    "schema_version": SCHEMA_VERSION,
                    "record_id": record_id,
                    "source_record_id": item["source_record_id"],
                    "source_locator": item["source_locator"],
                    "document_locator": document_locator,
                    "access_class": "PUBLIC",
                    "rights_state": "PERMITTED",
                    "content_hash": content_hash,
                    "parser": PARSER_ID,
                    "page_count": document["page_count"],
                    "extraction_status": document["extraction_status"],
                    "raw_cache_key": raw_cache_key,
                    "route_ids": item["route_ids"],
                    "route_attempts": route_attempts,
                    "ingestion_status": status,
                    "review_status": review,
                    "selected_pages": selected,
                    "failure_detail": None,
                    "canonical_record_id": canonical_record_id if status == "DUPLICATE_CONTENT" else None,
                }
            except Exception as exc:  # Enforce an attributable row for unanticipated source failures.
                record = self._empty_record(item, status="FETCH_FAILED", detail=f"{type(exc).__name__}: {exc}", route_attempts=locals().get("route_attempts", []))
            validate_ingestion_record(record, schema=self.schema)
            records.append(record)
        records.sort(key=lambda row: row["record_id"])
        counts: dict[str, int] = {}
        for row in records:
            counts[row["ingestion_status"]] = counts.get(row["ingestion_status"], 0) + 1
        review_queue = {
            "schema_version": SCHEMA_VERSION,
            "intake_version": INGESTION_VERSION,
            "review_items": [
                {
                    "record_id": row["record_id"],
                    "source_record_id": row["source_record_id"],
                    "content_hash": row["content_hash"],
                    "document_locator": row["document_locator"],
                    "selected_pages": row["selected_pages"],
                    "required_fields": REVIEW_FIELDS,
                    "review_status": row["review_status"],
                }
                for row in records if row["review_status"] == "PENDING_HUMAN_REVIEW"
            ],
        }
        return records, {"counts": counts, "review_queue": review_queue}


def build_remediated_readiness(*, scope: list[dict[str, Any]], records: list[dict[str, Any]], corpus_source_count: int) -> dict[str, Any]:
    """Re-evaluate only the landscape checks this intake can change."""
    relevant = [item for item in scope if item["in_scope"]]
    by_id = {row["source_record_id"]: row for row in records}
    ingested = [row for row in records if row["ingestion_status"] in {"INGESTED", "DUPLICATE_CONTENT"}]
    checks = {
        "audited_public_routes_attempted": all(item["source_record_id"] in by_id for item in relevant),
        "public_document_hashes_complete": bool(relevant) and all(by_id[item["source_record_id"]]["content_hash"] for item in relevant),
        "page_located_native_extraction_complete": bool(relevant) and all(
            by_id[item["source_record_id"]]["ingestion_status"] == "INGESTED" for item in relevant
        ),
        "critical_field_review_complete": False,
        "lineage_adjudication_complete": False,
        "contradiction_map_complete": False,
        "scientific_adjudication_complete": False,
        "full_corpus_route_audit_complete": len(scope) == corpus_source_count,
    }
    blockers = []
    if not checks["audited_public_routes_attempted"]:
        blockers.append("one or more audited public-copy routes were not attempted")
    if not checks["public_document_hashes_complete"]:
        blockers.append(f"only {len(ingested)}/{len(relevant)} relevant public-route records have document hashes")
    if not checks["page_located_native_extraction_complete"]:
        blockers.append("one or more relevant public routes remain failed, rights-blocked, landing-only, or OCR-required")
    blockers.extend([
        "critical evidence fields still require human source mapping; G-LI does not infer facts",
        "study-family lineage adjudication remains pending from G-LR",
        "contradiction ledger remains pending from G-LR",
        "scientific screening adjudication remains pending from G-LR",
    ])
    return {
        "protocol_version": "glr.1-landscape-map+gli.1-public-document-intake",
        "readiness": "LANDSCAPE_INCOMPLETE",
        "checks": checks,
        "counts": {
            "corpus_source_count": corpus_source_count,
            "public_route_rows": len(scope),
            "relevant_public_route_rows": len(relevant),
            "ingested_or_duplicate": len(ingested),
            "review_queue_items": sum(row["review_status"] == "PENDING_HUMAN_REVIEW" for row in records),
            "fetch_failed": sum(row["ingestion_status"] == "FETCH_FAILED" for row in records),
            "rights_blocked": sum(row["ingestion_status"] == "RIGHTS_BLOCKED" for row in records),
            "landing_without_declared_pdf": sum(row["ingestion_status"] == "PUBLIC_LANDING_NO_PDF" for row in records),
            "out_of_scope": sum(row["ingestion_status"] == "OUT_OF_SCOPE" for row in records),
        },
        "blockers": blockers,
        "permitted_outputs": [
            "page-located public-document review queue",
            "provisional evidence-gap and candidate updates",
            "explicitly provisional hypothesis seeds with uncertainty",
        ],
        "prohibited_outputs": [
            "discovery-grade hypothesis generation",
            "validated performance claim",
            "recipe or physical execution authorization",
            "immutable evidence promotion",
        ],
    }


def run_manifest(*, scope: list[dict[str, Any]], policy: SourcePolicy, records: list[dict[str, Any]], review_queue: dict[str, Any], readiness: dict[str, Any] | None = None) -> dict[str, Any]:
    scope_hash = digest(scope)
    inputs = {"scope_hash": scope_hash, "policy_hash": policy.sha256, "ingestion_version": INGESTION_VERSION, "parser": PARSER_ID}
    output = {
        "goal": "G-LI",
        "protocol_version": INGESTION_VERSION,
        "run_id": digest(inputs)[7:23],
        "inputs": inputs,
        "outputs": {
            "ingestion_ledger_hash": digest(records),
            "review_queue_hash": digest(review_queue),
            "counts": {status: sum(1 for row in records if row["ingestion_status"] == status) for status in sorted({row["ingestion_status"] for row in records})},
        },
        "authority": {
            "network": "read-only exact audited PUBLIC hosts only",
            "credentials": "none",
            "model_calls": "none",
            "raw_payloads": "ignored data/raw/gli only",
            "evidence_promotion": "prohibited",
            "g10r_phase_b": "unexecuted",
        },
    }
    if readiness is not None:
        output["outputs"]["readiness_hash"] = digest(readiness)
    return output
