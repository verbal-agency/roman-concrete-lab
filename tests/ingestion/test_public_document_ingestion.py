import base64
import json
import tempfile
import unittest
from io import BytesIO
from pathlib import Path

from pypdf import PdfWriter

from src.roman_concrete_lab.ingestion.public_documents import (
    PublicDocumentIngestor,
    build_scope,
    load_schema,
    run_manifest,
    validate_ingestion_record,
)
from src.roman_concrete_lab.retrieval.contracts import PolicyBlocked, SourcePolicy
from src.roman_concrete_lab.retrieval.network import NetworkUnavailable
from tools.tournament.replay import ROOT


class FakeFetcher:
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def fetch_public_payload(self, locator):
        self.calls.append(locator)
        value = self.responses[locator]
        if isinstance(value, Exception):
            raise value
        return {"locator": locator, "payload_bytes": len(value[1]), "content_type": value[0], "payload": value[1]}


def policy():
    return SourcePolicy.load(ROOT / "fixtures/investigation/source-policy.json")


def native_pdf() -> bytes:
    return base64.b64decode((ROOT / "fixtures/investigation/pdf-benchmark.b64").read_text().strip())


def blank_pdf() -> bytes:
    out = BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    writer.write(out)
    return out.getvalue()


def item(record_id="S04", routes=None, in_scope=True):
    return {
        "source_record_id": record_id,
        "source_locator": "https://doi.org/10.1000/example",
        "title": "Quicklime water-transport study",
        "relevance": "candidate",
        "route_ids": routes or ["https://papers.ssrn.com/example.pdf"],
        "in_scope": in_scope,
        "scope_reason": "fixture",
    }


class PublicDocumentIngestionTests(unittest.TestCase):
    def ingestor(self, fetcher, directory):
        return PublicDocumentIngestor(
            policy=policy(), fetcher=fetcher, schema=load_schema(ROOT), raw_cache_dir=directory,
            question="quicklime water transport", max_selected_characters=1000,
        )

    def test_scope_uses_audited_public_routes_and_excludes_low_relevance(self):
        scope = build_scope(
            landscape_sources=ROOT / "data/manifests/landscape-sources.jsonl",
            access_register=ROOT / "data/manifests/literature-sufficiency-access-register.csv",
        )
        by_id = {row["source_record_id"]: row for row in scope}
        self.assertTrue(by_id["S04"]["in_scope"])
        self.assertTrue(by_id["S17"]["in_scope"])
        self.assertFalse(by_id["S19"]["in_scope"])
        self.assertIn("https://papers.ssrn.com", by_id["S04"]["route_ids"][0])

    def test_direct_pdf_creates_page_located_review_record_without_text_artifact(self):
        route = "https://papers.ssrn.com/example.pdf"
        fetcher = FakeFetcher({route: ("application/pdf", native_pdf())})
        with tempfile.TemporaryDirectory() as raw:
            records, output = self.ingestor(fetcher, Path(raw)).ingest([item(routes=[route])])
            record = records[0]
            self.assertEqual(record["ingestion_status"], "INGESTED")
            self.assertEqual(record["review_status"], "PENDING_HUMAN_REVIEW")
            self.assertTrue(record["selected_pages"])
            self.assertEqual(record["route_attempts"][0]["status"], "PDF_RETRIEVED")
            self.assertTrue((Path(raw) / record["raw_cache_key"]).exists())
            self.assertNotIn('"text"', json.dumps(record))
            self.assertEqual(output["review_queue"]["review_items"][0]["required_fields"][0], "material_process")

    def test_declared_landing_pdf_is_resolved_once_and_unknown_anchors_are_ignored(self):
        landing = "https://www.repository.cam.ac.uk/items/example"
        pdf = "https://www.repository.cam.ac.uk/bitstreams/example.pdf"
        html = b'<meta name="citation_pdf_url" content="/bitstreams/example.pdf"><a href="https://elsewhere.invalid/download.pdf">ignore</a>'
        fetcher = FakeFetcher({landing: ("text/html", html), pdf: ("application/pdf", native_pdf())})
        with tempfile.TemporaryDirectory() as raw:
            records, _ = self.ingestor(fetcher, Path(raw)).ingest([item(routes=[landing])])
        self.assertEqual(records[0]["ingestion_status"], "INGESTED")
        self.assertEqual(fetcher.calls, [landing, pdf])
        self.assertEqual(records[0]["route_attempts"][0]["status"], "PDF_RETRIEVED")

    def test_duplicate_content_keeps_one_cache_document_and_route_provenance(self):
        first = "https://papers.ssrn.com/one.pdf"
        second = "https://papers.ssrn.com/two.pdf"
        fetcher = FakeFetcher({first: ("application/pdf", native_pdf()), second: ("application/pdf", native_pdf())})
        with tempfile.TemporaryDirectory() as raw:
            records, _ = self.ingestor(fetcher, Path(raw)).ingest([item("S04", [first]), item("S17", [second])])
            cached = list(Path(raw).glob("*.pdf"))
        self.assertEqual(records[0]["ingestion_status"], "INGESTED")
        self.assertEqual(records[1]["ingestion_status"], "DUPLICATE_CONTENT")
        self.assertEqual(records[1]["canonical_record_id"], "PDI-S04")
        self.assertEqual(len(cached), 1)

    def test_empty_native_text_requires_ocr_and_does_not_enter_review_queue(self):
        route = "https://papers.ssrn.com/blank.pdf"
        fetcher = FakeFetcher({route: ("application/pdf", blank_pdf())})
        with tempfile.TemporaryDirectory() as raw:
            records, output = self.ingestor(fetcher, Path(raw)).ingest([item(routes=[route])])
        self.assertEqual(records[0]["ingestion_status"], "OCR_REQUIRED")
        self.assertEqual(output["review_queue"]["review_items"], [])

    def test_malformed_policy_and_network_failures_are_attributable_without_payload(self):
        malformed = "https://papers.ssrn.com/bad.pdf"
        denied = "https://papers.ssrn.com/denied.pdf"
        offline = "https://papers.ssrn.com/offline.pdf"
        fetcher = FakeFetcher({
            malformed: ("application/pdf", b"not a pdf"),
            denied: PolicyBlocked("rights changed"),
            offline: NetworkUnavailable("offline"),
        })
        with tempfile.TemporaryDirectory() as raw:
            records, _ = self.ingestor(fetcher, Path(raw)).ingest([
                item("S04", [malformed]), item("S06", [denied]), item("S11", [offline]),
            ])
        self.assertEqual([row["ingestion_status"] for row in records], ["MALFORMED_DOCUMENT", "RIGHTS_BLOCKED", "FETCH_FAILED"])
        self.assertTrue(all(row["content_hash"] is None for row in records))
        self.assertTrue(all(row["route_attempts"] for row in records))

    def test_cache_replay_skips_network_and_changed_scope_changes_run_id(self):
        route = "https://papers.ssrn.com/replay.pdf"
        first = FakeFetcher({route: ("application/pdf", native_pdf())})
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            records, output = self.ingestor(first, directory).ingest([item(routes=[route])])
            second = FakeFetcher({})
            replayed, replay_output = self.ingestor(second, directory).ingest([item(routes=[route])])
            self.assertEqual(first.calls, [route])
            self.assertEqual(second.calls, [])
            self.assertEqual(records, replayed)
            before = run_manifest(scope=[item(routes=[route])], policy=policy(), records=records, review_queue=output["review_queue"])
            after = run_manifest(scope=[item("S17", [route])], policy=policy(), records=replayed, review_queue=replay_output["review_queue"])
        self.assertNotEqual(before["run_id"], after["run_id"])

    def test_out_of_scope_and_invalid_state_are_rejected(self):
        with tempfile.TemporaryDirectory() as raw:
            records, _ = self.ingestor(FakeFetcher({}), Path(raw)).ingest([item("S19", in_scope=False)])
        self.assertEqual(records[0]["ingestion_status"], "OUT_OF_SCOPE")
        invalid = dict(records[0])
        invalid["review_status"] = "PENDING_HUMAN_REVIEW"
        with self.assertRaises(ValueError):
            validate_ingestion_record(invalid, schema=load_schema(ROOT))


if __name__ == "__main__":
    unittest.main()
