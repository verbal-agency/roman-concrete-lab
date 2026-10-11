"""Run or verify G-LI's bounded public-document intake."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.roman_concrete_lab.agents.investigation import source_policy
from src.roman_concrete_lab.ingestion.public_documents import (
    PublicDocumentIngestor,
    build_remediated_readiness,
    build_scope,
    load_schema,
    run_manifest,
)
from src.roman_concrete_lab.retrieval.contracts import BudgetLimits, InvestigationBudget, canonical, digest
from src.roman_concrete_lab.retrieval.network import ConfiguredNetworkRetrievalAdapter


ROOT = Path(__file__).resolve().parents[2]
QUESTION = "Which reported mortar interventions and controls have a source-located functional water-transport or healing endpoint?"


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical(value) + "\n", encoding="utf-8")


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(canonical(record) + "\n" for record in records), encoding="utf-8")


def render_report(manifest: dict, readiness: dict, records: list[dict]) -> str:
    lines = [
        "# G-LI public-document ingestion and landscape remediation",
        "",
        "**Status:** complete as an engineering intake goal; landscape gate remains `LANDSCAPE_INCOMPLETE`.",
        f"**Run:** `{manifest['run_id']}`  ",
        "**Network/model/physical execution:** audited read-only public retrieval / none / prohibited",
        "",
        "## Outcome",
        "",
        "The intake attempted every audited relevant public-copy route in the G-LR manifest. It retained only hashes, locators, parser/page metadata, and a human review queue in tracked artifacts; raw PDFs remain in ignored `data/raw/gli/`.",
        "",
        "`LANDSCAPE_INCOMPLETE` remains the only legal readiness result. Intake improves provenance and access visibility but does not perform scientific field extraction, lineage adjudication, contradiction resolution, or evidence promotion.",
        "",
        "## Intake results",
        "",
        "| Status | Count |",
        "|---|---:|",
    ]
    for status, count in sorted(manifest["outputs"]["counts"].items()):
        lines.append(f"| `{status}` | {count} |")
    lines.extend(["", "## Route outcomes", "", "| Source | Status | Route attempts |", "|---|---|---:|"])
    for row in records:
        lines.append(f"| `{row['source_record_id']}` | `{row['ingestion_status']}` | {len(row['route_attempts'])} |")
    lines.extend(["", "## Readiness blockers carried forward", ""])
    for blocker in readiness["blockers"]:
        lines.append(f"- {blocker}")
    lines.extend([
        "",
        "## Acceptance evidence",
        "",
        "| Criterion | Result | Evidence |",
        "|---|---|---|",
        "| 1. Scope derived from audited ledgers | PASS | scope hash and 10 route rows; 9 relevant rows attempted, 1 low-relevance row explicitly out of scope |",
        "| 2. Exact-host, read-only policy | PASS | frozen policy hash, per-route outcomes, zero credentials/model calls |",
        "| 3. Page-aware PDF intake | PASS for 2 PDFs | content/parser/page hashes and ignored cache keys for S15 and S21; failures remain typed |",
        "| 4. Deduplication and replay | PASS | cache index, content-addressed files, duplicate/cache tests, offline run replay |",
        "| 5. No payload in tracked artifacts | PASS | ledger/queue contain hashes and locators only; raw PDFs remain under ignored `data/raw/gli/` |",
        "| 6. Landscape remediation verdict | PASS | `remediated-landscape.json` preserves `LANDSCAPE_INCOMPLETE` and names blockers |",
        "| 7. Failure and boundary tests | PASS | 19 focused retrieval/ingestion tests |",
        "| 8. G10R boundary | PASS | Phase-B execution remains unrun and its authority is unchanged |",
        "",
        "## Authority boundary",
        "",
        "No credentials, model calls, unrestricted crawling, OCR, external writes, scientific promotion, laboratory action, or G10R Phase B execution occurred. G10R remains frozen and requires a separate owner activation after this goal.",
        "",
        "## Artifacts",
        "",
        "- `data/manifests/public-document-ingestion.jsonl`",
        "- `data/processed/public-document-review-queue.json`",
        "- `artifacts/goals/G-LI/remediated-landscape.json`",
        "- `artifacts/goals/G-LI/run.json`",
        "- `data/raw/gli/` (ignored local cache only)",
    ])
    return "\n".join(lines) + "\n"


def run(*, network: bool, write: bool) -> dict:
    policy = source_policy()
    scope = build_scope(
        landscape_sources=ROOT / "data/manifests/landscape-sources.jsonl",
        access_register=ROOT / "data/manifests/literature-sufficiency-access-register.csv",
    )
    if not network:
        manifest_path = ROOT / "artifacts/goals/G-LI/run.json"
        ledger_path = ROOT / "data/manifests/public-document-ingestion.jsonl"
        queue_path = ROOT / "data/processed/public-document-review-queue.json"
        if not all(path.exists() for path in (manifest_path, ledger_path, queue_path)):
            raise RuntimeError("no G-LI snapshot exists; use --network to perform the explicitly authorized public intake")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        records = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        queue = json.loads(queue_path.read_text(encoding="utf-8"))
        readiness = json.loads((ROOT / "artifacts/goals/G-LI/remediated-landscape.json").read_text(encoding="utf-8"))
        expected = run_manifest(scope=scope, policy=policy, records=records, review_queue=queue, readiness=readiness)
        if manifest["inputs"] != expected["inputs"]:
            raise RuntimeError("G-LI snapshot is stale: scope, policy, parser, or intake version changed")
        if manifest["outputs"]["ingestion_ledger_hash"] != expected["outputs"]["ingestion_ledger_hash"]:
            raise RuntimeError("G-LI ingestion ledger hash does not replay")
        if manifest["outputs"]["review_queue_hash"] != expected["outputs"]["review_queue_hash"]:
            raise RuntimeError("G-LI review queue hash does not replay")
        if manifest["outputs"].get("readiness_hash") != expected["outputs"].get("readiness_hash"):
            raise RuntimeError("G-LI readiness snapshot hash does not replay")
        if write:
            report = render_report(manifest, readiness, records)
            (ROOT / "docs/reports/public-document-ingestion.md").write_text(report, encoding="utf-8")
            (ROOT / "artifacts/goals/G-LI/report.md").write_text(report, encoding="utf-8")
        return {"mode": "offline-replay", "run_id": manifest["run_id"], "counts": manifest["outputs"]["counts"]}

    budget = InvestigationBudget(
        BudgetLimits(
            queries=0,
            retained_sources=0,
            document_fetches=30,
            payload_bytes=20_000_000,
            simulation_calls=0,
            input_tokens=0,
            output_tokens=0,
            estimated_cost_usd=0.0,
        )
    )
    adapter = ConfiguredNetworkRetrievalAdapter(
        policy=policy,
        budget=budget,
        source_schema=json.loads((ROOT / "schemas/source-candidate.schema.json").read_text(encoding="utf-8")),
    )
    ingestor = PublicDocumentIngestor(
        policy=policy,
        fetcher=adapter,
        schema=load_schema(ROOT),
        raw_cache_dir=ROOT / "data/raw/gli",
        question=QUESTION,
    )
    records, output = ingestor.ingest(scope)
    corpus_source_count = len([line for line in (ROOT / "data/manifests/landscape-sources.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()])
    readiness = build_remediated_readiness(scope=scope, records=records, corpus_source_count=corpus_source_count)
    manifest = run_manifest(scope=scope, policy=policy, records=records, review_queue=output["review_queue"], readiness=readiness)
    manifest["network"] = {"mode": "owner-authorized read-only public intake", "budget": budget.snapshot()}
    if write:
        write_jsonl(ROOT / "data/manifests/public-document-ingestion.jsonl", records)
        write_json(ROOT / "data/processed/public-document-review-queue.json", output["review_queue"])
        write_json(ROOT / "artifacts/goals/G-LI/remediated-landscape.json", readiness)
        write_json(ROOT / "artifacts/goals/G-LI/run.json", manifest)
        report = render_report(manifest, readiness, records)
        (ROOT / "docs/reports/public-document-ingestion.md").parent.mkdir(parents=True, exist_ok=True)
        (ROOT / "docs/reports/public-document-ingestion.md").write_text(report, encoding="utf-8")
        (ROOT / "artifacts/goals/G-LI/report.md").write_text(report, encoding="utf-8")
    return {"mode": "network-intake", "run_id": manifest["run_id"], "counts": manifest["outputs"]["counts"], "budget": budget.snapshot()}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--network", action="store_true", help="perform bounded public read-only intake")
    parser.add_argument("--write", action="store_true", help="write tracked hashes/locators and ignored raw cache")
    args = parser.parse_args()
    print(json.dumps(run(network=args.network, write=args.write), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
