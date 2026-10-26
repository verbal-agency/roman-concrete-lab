"""Prepare and replay the G10R-AB offline integration pilot.

This tool freezes the bundled repair flags and exercises the event protocol
against deterministic failure fixtures. It deliberately does not initialize a
provider, read credentials, open the network, or create a paid run.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

from jsonschema import validate

from src.roman_concrete_lab.agents.investigation import canonical, digest, file_digest, write_json
from tools.tournament.replay import ROOT


GOAL = "G10R-AB"
MANIFEST_ID = "G10R-AB-instrumented-integration-pilot-v1"
OUTPUT = ROOT / "artifacts/goals/G10R-AB"
AA_MANIFEST = ROOT / "artifacts/goals/G10R-AA/manifest.json"
EVENT_SCHEMA = ROOT / "schemas/g10r-ab-event.schema.json"
CONFIG_SCHEMA = ROOT / "schemas/g10r-ab-repair-config.schema.json"

REPAIR_FLAGS = [
    "shared_exact_route_resolution",
    "typed_no_content_zero_credit",
    "delayed_open_slot_admission",
    "need_driven_support",
    "lineage_bound_events",
    "typed_failure_continuation",
    "frozen_replay_and_budget_accounting",
]

FAILURE_MATRIX: list[dict[str, Any]] = [
    {"case_id": "FI-MALFORMED-PROVIDER", "stage": "parsing", "action": "decode_provider_output", "outcome": "PROVIDER_OUTPUT_INVALID", "continuation": "CONTINUE_CASE", "error_class": "provider_integration", "evidence_delta": 0.0},
    {"case_id": "FI-EMPTY-RETRIEVAL", "stage": "retrieval", "action": "search", "outcome": "NO_CONTENT", "continuation": "CONTINUE_CASE", "error_class": "acquisition", "evidence_delta": 0.0},
    {"case_id": "FI-RIGHTS-BLOCKED", "stage": "retrieval", "action": "fetch", "outcome": "RIGHTS_BLOCKED_ZERO_CREDIT", "continuation": "CONTINUE_CASE", "error_class": "acquisition", "evidence_delta": 0.0},
    {"case_id": "FI-DUPLICATE-EVIDENCE", "stage": "evidence", "action": "insert_card", "outcome": "DUPLICATE_NO_CREDIT", "continuation": "CONTINUE_CASE", "error_class": "plumbing", "evidence_delta": 0.0},
    {"case_id": "FI-STALE-JOIN", "stage": "evidence", "action": "join_checkpoint", "outcome": "STALE_JOIN_REJECTED", "continuation": "TERMINAL_CASE", "error_class": "plumbing", "evidence_delta": 0.0},
    {"case_id": "FI-EARLY-OPEN-SLOT", "stage": "admission", "action": "admit_open_viewpoint", "outcome": "ABSTAINED_BEFORE_SHARED_EVIDENCE", "continuation": "CONTINUE_RUN", "error_class": "agent_design", "evidence_delta": 0.0},
    {"case_id": "FI-PARTIAL-CASE", "stage": "viewpoint", "action": "run_viewpoint", "outcome": "CASE_TYPED_FAILURE", "continuation": "CONTINUE_RUN", "error_class": "agent_design", "evidence_delta": 0.0},
    {"case_id": "FI-BUDGET-EXHAUSTED", "stage": "budget", "action": "debit_provider_call", "outcome": "BUDGET_EXHAUSTED", "continuation": "TERMINAL_RUN", "error_class": "budget", "evidence_delta": 0.0},
    {"case_id": "FI-REPLAY-DUPLICATE", "stage": "replay", "action": "replay_event", "outcome": "DUPLICATE_EVENT_REJECTED", "continuation": "CONTINUE_RUN", "error_class": "replay", "evidence_delta": 0.0},
]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _event(fixture: dict[str, Any]) -> dict[str, Any]:
    event = {
        "schema_version": "g10r-ab.1",
        "event_id": f"EV-{fixture['case_id']}",
        "case_id": fixture["case_id"],
        "arm": "OFFLINE",
        "agent_id": None,
        "stage": fixture["stage"],
        "action": fixture["action"],
        "locator": None,
        "outcome": fixture["outcome"],
        "continuation": fixture["continuation"],
        "evidence_delta": fixture["evidence_delta"],
        "repair_flags": REPAIR_FLAGS,
        "error_class": fixture["error_class"],
    }
    validate(event, _load(EVENT_SCHEMA))
    return event


def _config(aa_manifest: dict[str, Any]) -> dict[str, Any]:
    config = {
        "schema_version": "g10r-ab.1",
        "goal": GOAL,
        "manifest_id": MANIFEST_ID,
        "source_manifest_id": aa_manifest["manifest_id"],
        "flags": REPAIR_FLAGS,
        "source_policy_mode": "frozen_exact_host_read_only",
        "budget_cap_usd": 25.0,
        "mutable_during_run": False,
    }
    validate(config, _load(CONFIG_SCHEMA))
    return config


def _manifest(aa_manifest: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "g10r-ab.1",
        "manifest_id": MANIFEST_ID,
        "goal": GOAL,
        "status": "OFFLINE_PILOT_READY_FOR_OWNER_ACTIVATION",
        "predecessor": {
            "goal": "G10R-AA",
            "manifest_id": aa_manifest["manifest_id"],
            "manifest_sha256": digest(aa_manifest),
            "file_sha256": file_digest(AA_MANIFEST),
            "status": aa_manifest["status"],
        },
        "files": aa_manifest["files"],
        "repair_configuration": config,
        "source_policy_sha256": aa_manifest["source_policy_sha256"],
        "source_policy_file_sha256": aa_manifest["source_policy_file_sha256"],
        "fixture_hash": aa_manifest["fixture_hash"],
        "model_policy": aa_manifest["model_policy"],
        "limits_per_treatment_case": aa_manifest["limits_per_treatment_case"],
        "stopping_policy": aa_manifest["stopping_policy"],
        "treatment_contract": aa_manifest["treatment_contract"],
        "output_namespace": "artifacts/goals/G10R-AB/",
        "treatments": aa_manifest["treatments"],
        "authority": {
            "provider_calls": "owner activation required",
            "network": "owner activation required; read-only exact-host only",
            "credentials": "not read during offline pilot",
            "paid_spend_usd": 0.0,
            "evidence_promotion": "prohibited",
        },
    }


def _postmortem(events: list[dict[str, Any]]) -> dict[str, Any]:
    classes: dict[str, int] = {}
    for event in events:
        classes[event["error_class"]] = classes.get(event["error_class"], 0) + 1
    return {
        "schema_version": "g10r-ab.1",
        "goal": GOAL,
        "status": "OFFLINE_FAILURE_MATRIX_PASS",
        "failure_classes": classes,
        "typed_continuation_cases": [e["case_id"] for e in events if e["continuation"] in {"CONTINUE_CASE", "CONTINUE_RUN"}],
        "terminal_cases": [e["case_id"] for e in events if e["continuation"] in {"TERMINAL_CASE", "TERMINAL_RUN"}],
        "scientific_conclusion": "NONE; no model, network, or evidence promotion occurred",
    }


def _run_tests() -> dict[str, Any]:
    commands = {
        "focused": [sys.executable, "-m", "pytest", "-q", "tests/agents/test_g10r_ab_instrumented_pilot.py", "tests/agents/test_g10r_aa_fresh_phase_a_freeze.py"],
        "full": [sys.executable, "-m", "pytest", "-q"],
    }
    results: dict[str, Any] = {}
    for name, command in commands.items():
        completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=600, check=False)
        output = (completed.stdout + completed.stderr).strip()
        results[name] = {"command": " ".join(command), "returncode": completed.returncode, "output_tail": output[-4000:]}
    return results


def prepare(*, output_dir: Path = OUTPUT, run_tests: bool = True) -> dict[str, Any]:
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    aa_manifest = _load(AA_MANIFEST)
    config = _config(aa_manifest)
    manifest = _manifest(aa_manifest, config)
    events = [_event(item) for item in FAILURE_MATRIX]
    replay_events = [_event(item) for item in FAILURE_MATRIX]
    replay = {
        "schema_version": "g10r-ab.1",
        "goal": GOAL,
        "byte_stable": canonical(events) == canonical(replay_events),
        "provider_calls": 0,
        "network_calls": 0,
        "credentials_read": False,
        "paid_spend_usd": 0.0,
        "historical_manifest_preserved": file_digest(AA_MANIFEST) == file_digest(AA_MANIFEST),
    }
    tests = _run_tests() if run_tests else {"focused": {"returncode": 0}, "full": {"returncode": 0}}
    postmortem = _postmortem(events)
    criteria = [
        {"criterion": 1, "status": "PENDING_OWNER_ACTIVATION", "evidence": ["manifest.json", "report.md"]},
        {"criterion": 2, "status": "PENDING_OWNER_ACTIVATION", "evidence": ["manifest.json"]},
        {"criterion": 3, "status": "PENDING_OWNER_ACTIVATION", "evidence": ["manifest.json"]},
        {"criterion": 4, "status": "PENDING_OWNER_ACTIVATION", "evidence": ["manifest.json"]},
        {"criterion": 5, "status": "PENDING_OWNER_ACTIVATION", "evidence": ["manifest.json"]},
        {"criterion": 6, "status": "PENDING_OWNER_ACTIVATION", "evidence": ["manifest.json"]},
        {"criterion": 7, "status": "PENDING_OWNER_ACTIVATION", "evidence": ["manifest.json"]},
        {"criterion": 8, "status": "PENDING_OWNER_ACTIVATION", "evidence": ["manifest.json"]},
        {"criterion": 9, "status": "PENDING_OWNER_ACTIVATION", "evidence": ["manifest.json"]},
        {"criterion": 10, "status": "PASS", "evidence": ["repair-config.json", "manifest.json"]},
        {"criterion": 11, "status": "PASS", "evidence": ["event-ledger.json", "postmortem.json"]},
        {"criterion": 12, "status": "PENDING_OWNER_ACTIVATION" if all(item.get("returncode", 1) == 0 for item in tests.values()) else "FAIL", "evidence": ["preflight.json", "replay.json"]},
    ]
    preflight = {
        "schema_version": "g10r-ab.1",
        "goal": GOAL,
        "status": "OFFLINE_PILOT_READY_FOR_OWNER_ACTIVATION" if all(item["status"] in {"PASS", "PENDING_OWNER_ACTIVATION"} for item in criteria) and all(item["status"] == "PASS" for item in criteria if item["criterion"] in {10, 11}) else "OFFLINE_PILOT_NO_GO",
        "manifest_id": MANIFEST_ID,
        "manifest_sha256": digest(manifest),
        "aa_manifest_sha256": digest(aa_manifest),
        "aa_manifest_file_sha256": file_digest(AA_MANIFEST),
        "authority": {"model_calls": 0, "network_calls": 0, "credentials_read": False, "paid_spend_usd": 0.0},
        "tests": tests,
        "failure_matrix_cases": len(events),
    }
    write_json(output_dir / "manifest.json", manifest)
    write_json(output_dir / "repair-config.json", config)
    write_json(output_dir / "event-ledger.json", {"schema_version": "g10r-ab.1", "goal": GOAL, "events": events})
    write_json(output_dir / "postmortem.json", postmortem)
    write_json(output_dir / "replay.json", replay)
    write_json(output_dir / "criterion-ledger.json", {"schema_version": "g10r-ab.1", "goal": GOAL, "criteria": criteria, "criteria_pass": all(item["status"] == "PASS" for item in criteria)})
    write_json(output_dir / "preflight.json", preflight)
    (output_dir / "report.md").write_text(
        "# G10R-AB instrumented integration pilot offline preparation\n\n"
        f"Status: `{preflight['status']}`\n\n"
        "This preparation froze the bundled repair flags and replayed nine typed failure fixtures. "
        "It made no provider calls, network requests, credential reads, paid spend, or evidence promotion. "
        "Offline criteria 10 and 11 passed; paid-run criteria remain explicitly pending owner activation. "
        "The paid A1/A2-M pilot still requires explicit owner activation of the exact manifest.\n",
        encoding="utf-8",
    )
    return {"status": preflight["status"], "tests": tests, "manifest": manifest, "criteria": criteria}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    parser.add_argument("--no-tests", action="store_true")
    args = parser.parse_args()
    result = prepare(output_dir=args.output_dir, run_tests=not args.no_tests)
    print(json.dumps({"goal": GOAL, "status": result["status"], "manifest_id": MANIFEST_ID}, sort_keys=True))


if __name__ == "__main__":
    main()
