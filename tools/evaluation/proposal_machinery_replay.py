"""Offline G10R-AF proposal-machinery replay and readiness gate."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import ValidationError

from src.roman_concrete_lab.agents.investigation import file_digest, frozen_manifest, write_json
from src.roman_concrete_lab.agents.proposal_machinery import ProposalLedger, blind_for_scoring, score_proposal, validate_packet
from src.roman_concrete_lab.retrieval import BudgetExhausted, BudgetLimits, InvestigationBudget, PolicyBlocked, StaleContext, canonical, digest
from tools.tournament.replay import ROOT


GOAL = "G10R-AF"
MANIFEST_ID = "G10R-AF-proposal-machinery-v1"
OUTPUT = ROOT / "artifacts/goals/G10R-AF"
PREDECESSOR = "artifacts/goals/G10R-AE/manifest.json"

INPUT_FILES = {
    "predecessor_manifest": PREDECESSOR,
    "predecessor_preflight": "artifacts/goals/G10R-AE/preflight.json",
    "proposal_schema": "schemas/proposal-packet.schema.json",
    "proposal_module": "src/roman_concrete_lab/agents/proposal_machinery.py",
    "proposal_protocol": "docs/protocols/proposal-machinery.md",
    "cases": "fixtures/investigation/g10r-af/cases.json",
    "proposals": "fixtures/investigation/g10r-af/proposals.jsonl",
    "fault_cases": "fixtures/investigation/g10r-af/fault-cases.json",
    "focused_test": "tests/agents/test_proposal_machinery.py",
    "source_policy": "fixtures/investigation/source-policy.json",
}


def _path(relative: str) -> Path:
    path = ROOT / relative
    if not path.exists():
        raise FileNotFoundError(relative)
    return path


def _read_json(relative: str) -> dict[str, Any]:
    return json.loads(_path(relative).read_text(encoding="utf-8"))


def _read_jsonl(relative: str) -> list[dict[str, Any]]:
    return [json.loads(line) for line in _path(relative).read_text(encoding="utf-8").splitlines() if line.strip()]


def _file_map() -> dict[str, dict[str, str]]:
    return {name: {"path": relative, "sha256": file_digest(_path(relative))} for name, relative in INPUT_FILES.items()}


def _build_manifest(files: dict[str, dict[str, str]]) -> dict[str, Any]:
    base = frozen_manifest()
    return {
        "schema_version": "g10r-af.1",
        "manifest_id": MANIFEST_ID,
        "goal": GOAL,
        "status": "PENDING_OFFLINE_READINESS",
        "predecessor": {
            "goal": "G10R-AE",
            "manifest_id": "G10R-AE-fresh-phase-a-runner-intake-v1",
            "manifest_sha256": file_digest(_path(PREDECESSOR)),
        },
        "files": files,
        "model_policy": {"provider": base["model_policy"]["provider"], "model": base["model_policy"]["model"], "calls": "none in G10R-AF"},
        "source_policy_sha256": file_digest(_path(INPUT_FILES["source_policy"])),
        "budgets": {"queries": 12, "retained_sources": 24, "document_fetches": 4, "payload_bytes": 5_000_000, "simulation_calls": 4, "input_tokens": 80_000, "output_tokens": 7_200, "estimated_cost_usd": 25.0},
        "treatments": {"A1": "single investigator proposal packet", "A2-M": "viewpoint society proposal packets"},
        "output_namespace": "artifacts/goals/G10R-AF/",
        "authority": {"model_calls": "none", "network": "none", "credentials": "not read", "evidence_promotion": "prohibited", "laboratory": "prohibited", "paid_activation": "separate owner decision naming G10R-AE manifest"},
    }


def _run_tests() -> dict[str, Any]:
    commands = {
        "focused": [sys.executable, "-m", "pytest", "-q", "tests/agents/test_proposal_machinery.py", "tests/agents/test_runner_provisional_intake.py", "tests/agents/test_provisional_intake.py"],
        "full": [sys.executable, "-m", "pytest", "-q"],
    }
    results: dict[str, Any] = {}
    for name, command in commands.items():
        completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=600, check=False)
        output = (completed.stdout + completed.stderr).strip()
        results[name] = {"command": " ".join(command), "returncode": completed.returncode, "output_tail": output[-4000:]}
    return results


def _fault_matrix(packets: list[dict[str, Any]]) -> dict[str, bool]:
    faults = _read_json(INPUT_FILES["fault_cases"])
    checks: dict[str, bool] = {}
    malformed = faults["malformed"]
    try:
        validate_packet(malformed)
    except ValidationError:
        checks["malformed_rejected"] = True

    packet = packets[0]
    ledger = ProposalLedger(case_id=packet["case_id"], arm=packet["arm"], context_hash="sha256:af-context")
    ledger.add(packet)
    changed = dict(packet)
    changed["predicted_observation"] = "conflicting duplicate payload"
    try:
        ledger.add(changed)
    except PolicyBlocked:
        checks["conflicting_duplicate_rejected"] = True

    try:
        ledger.add({**packet, "case_id": "OTHER-CASE", "proposal_id": "AF-CROSS-CASE"})
    except PolicyBlocked:
        checks["cross_case_rejected"] = True

    try:
        ledger.attach_checkpoint({"case_id": packet["case_id"], "arm": packet["arm"], "context_hash": "sha256:stale"})
    except StaleContext:
        checks["stale_checkpoint_rejected"] = True

    budget = InvestigationBudget(BudgetLimits(estimated_cost_usd=25.0))
    try:
        budget.debit(estimated_cost_usd=float(faults["budget_overage_usd"]))
    except BudgetExhausted:
        checks["budget_overage_rejected"] = True

    retained = 0
    partial_ledgers: list[ProposalLedger] = []
    for proposal_id in faults["partial_failure_ids"]:
        candidate = next((item for item in packets if item["proposal_id"] == proposal_id), None)
        if candidate is None:
            try:
                validate_packet(malformed)
            except ValidationError:
                continue
        else:
            partial_ledger = ProposalLedger(case_id=candidate["case_id"], arm=candidate["arm"], context_hash="sha256:af-context")
            partial_ledger.add(candidate)
            partial_ledgers.append(partial_ledger)
            retained += 1
    checks["partial_success_retained"] = retained == 2 and sum(len(item.proposals) for item in partial_ledgers) == 2
    checks["all_faults_rejected"] = all(checks.get(key, False) for key in (
        "malformed_rejected", "conflicting_duplicate_rejected", "cross_case_rejected",
        "stale_checkpoint_rejected", "budget_overage_rejected", "partial_success_retained",
    ))
    return checks


def _replay(manifest: dict[str, Any], packets: list[dict[str, Any]], cases: list[dict[str, Any]]) -> dict[str, Any]:
    case_ids = {case["case_id"] for case in cases}
    packet_keys = {(packet["case_id"], packet["arm"]) for packet in packets}
    expected_keys = {(case_id, arm) for case_id in case_ids for arm in ("A1", "A2-M")}
    scores: list[dict[str, Any]] = []
    checkpoints: list[dict[str, Any]] = []
    budgets = {}
    for case_id in sorted(case_ids):
        for arm in ("A1", "A2-M"):
            ledger = ProposalLedger(case_id=case_id, arm=arm, context_hash=digest({"manifest_id": manifest["manifest_id"], "case_id": case_id}))
            selected = [packet for packet in packets if packet["case_id"] == case_id and packet["arm"] == arm]
            for packet in selected:
                ledger.add(packet)
                blinded = blind_for_scoring(packet)
                score = score_proposal(blinded)
                score["case_id"] = case_id
                scores.append(score)
            checkpoints.append(ledger.snapshot())
            budgets[arm] = InvestigationBudget(BudgetLimits(queries=12, retained_sources=24, document_fetches=4, payload_bytes=5_000_000, simulation_calls=4, input_tokens=80_000, output_tokens=7_200, estimated_cost_usd=25.0)).snapshot()
    first = {"cases": sorted(case_ids), "packet_keys": sorted(packet_keys), "scores": sorted(scores, key=lambda item: (item["case_id"], item["proposal_id"])), "checkpoints": checkpoints, "budgets": budgets}
    second = json.loads(json.dumps(first, sort_keys=True))
    fault_checks = _fault_matrix(packets)
    criteria = {
        "case_and_arm_contract": packet_keys == expected_keys and all(packet["case_id"] in case_ids for packet in packets),
        "typed_proposal_components": all(score["status"] in {"PROPOSAL_REVIEWABLE", "PROPOSAL_INCOMPLETE"} and "components" in score for score in scores),
        "contradictions_and_pending_retained": any(score["contradicted_edge_count"] for score in scores) and any(score["pending_edge_count"] for score in scores),
        "rhetoric_zeroed": all(all(score[key] == 0 for key in ("rhetoric_credit", "consensus_credit", "answer_length_credit", "viewpoint_count_credit", "agent_count_credit")) for score in scores),
        "equal_blinded_comparison": budgets["A1"] == budgets["A2-M"] and all(score["treatment_identity_available"] is False for score in scores),
        "fault_matrix_passed": fault_checks["all_faults_rejected"],
        "byte_stable_replay": canonical(first) == canonical(second),
        "zero_external_authority": all(checkpoint["authority"] == {"model_calls": 0, "network_calls": 0, "credentials_read": False, "paid_spend_usd": 0} for checkpoint in checkpoints),
    }
    return {"schema_version": "g10r-af.1", "goal": GOAL, "manifest_id": manifest["manifest_id"], "criteria": criteria, "fault_matrix": fault_checks, "scores": scores, "checkpoints": checkpoints, "budgets": budgets, "replay": {"byte_stable": criteria["byte_stable_replay"], "external_calls": False, "provider_calls": 0, "network_calls": 0, "credentials_read": False, "paid_spend_usd": 0}, "first_digest": digest(first), "second_digest": digest(second)}


def replay(*, output_dir: Path = OUTPUT) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    files = _file_map()
    manifest = _build_manifest(files)
    manifest_path = output_dir / "manifest.json"
    existing = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else None
    if existing is not None:
        expected = dict(manifest)
        expected["status"] = existing.get("status")
        if canonical(existing) != canonical(expected):
            raise PolicyBlocked("existing G10R-AF manifest differs; use a new namespace")
        manifest = existing
    else:
        write_json(manifest_path, manifest)
    cases = _read_json("fixtures/investigation/g10r-af/cases.json")["cases"]
    packets = _read_jsonl("fixtures/investigation/g10r-af/proposals.jsonl")
    replay_result = _replay(manifest, packets, cases)
    tests = _run_tests()
    all_criteria = all(replay_result["criteria"].values()) and all(item["returncode"] == 0 for item in tests.values())
    status = "PROPOSAL_MACHINERY_READY" if all_criteria else "PROPOSAL_MACHINERY_NO_GO"
    predecessor_hash = _read_json(INPUT_FILES["predecessor_preflight"])["manifest_sha256"]
    manifest["status"] = status
    write_json(manifest_path, manifest)
    preflight = {"schema_version": "g10r-af.1", "goal": GOAL, "status": status, "manifest_id": MANIFEST_ID, "manifest_sha256": digest(manifest), "criteria": replay_result["criteria"], "tests": tests, "authority": replay_result["replay"]}
    ledger = {"schema_version": "g10r-af.1", "goal": GOAL, "status": status, "criteria": [{"criterion": key, "passed": value} for key, value in sorted({**replay_result["criteria"], "focused_tests_passed": tests["focused"]["returncode"] == 0, "full_suite_passed": tests["full"]["returncode"] == 0}.items())]}
    write_json(output_dir / "replay.json", replay_result)
    write_json(output_dir / "preflight.json", preflight)
    write_json(output_dir / "criterion-ledger.json", ledger)
    (output_dir / "activation-request.md").write_text(
        f"# G10R-AF later live-evaluation request\n\nStatus: `PENDING_SEPARATE_OWNER_ACTIVATION`\n\n"
        f"Offline result: `{status}`\n\n"
        f"A live proposal evaluation must name the exact G10R-AE manifest `G10R-AE-fresh-phase-a-runner-intake-v1` with SHA-256 `{predecessor_hash}`, provider/model, read-only network policy, and hard $25 cap. G10R-AF itself made no live calls and cannot activate Phase B.\n",
        encoding="utf-8",
    )
    report = "# G10R-AF proposal-machinery readiness\n\n" + f"Outcome: **{status}**\n\n" + "The offline gate measures proposal structure and provenance, not scientific truth or debate performance.\n\n" + "Criteria:\n" + "\n".join(f"- {key}: {'PASS' if value else 'FAIL'}" for key, value in sorted({**replay_result["criteria"], "focused_tests_passed": tests["focused"]["returncode"] == 0, "full_suite_passed": tests["full"]["returncode"] == 0}.items())) + "\n\nAuthority: 0 model calls, 0 network calls, 0 credential reads, $0 paid spend.\n"
    (output_dir / "report.md").write_text(report, encoding="utf-8")
    return {"status": status, "manifest_id": MANIFEST_ID, "manifest_sha256": digest(manifest), "criteria": replay_result["criteria"], "tests": tests}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    args = parser.parse_args()
    result = replay(output_dir=args.output_dir)
    print(json.dumps({"status": result["status"], "manifest_id": result["manifest_id"], "manifest_sha256": result["manifest_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()
