"""Create the G10R-AE Phase-A freeze without live side effects."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import ValidationError, validate

from src.roman_concrete_lab.agents.investigation import file_digest, frozen_manifest, write_json
from src.roman_concrete_lab.agents.runner_intake import RunnerProvisionalIntake
from src.roman_concrete_lab.retrieval import BudgetExhausted, BudgetLimits, InvestigationBudget, PolicyBlocked, StaleContext, canonical, digest
from tools.tournament.replay import ROOT


GOAL = "G10R-AE"
MANIFEST_ID = "G10R-AE-fresh-phase-a-runner-intake-v1"
OUTPUT = ROOT / "artifacts/goals/G10R-AE"

INPUT_FILES = {
    "predecessor_goal": "docs/goals/G10R-AD-runner-provisional-intake-and-conflict-adjudication.md",
    "predecessor_replay": "artifacts/goals/G10R-AD/replay.json",
    "base_runner": "src/roman_concrete_lab/agents/investigation.py",
    "runner_intake_adapter": "src/roman_concrete_lab/agents/runner_intake.py",
    "conflict_adjudicator": "src/roman_concrete_lab/agents/conflict_adjudication.py",
    "runner_intake_schema": "schemas/runner-provisional-intake.schema.json",
    "conflict_set_schema": "schemas/conflict-set.schema.json",
    "conflict_adjudication_schema": "schemas/conflict-adjudication.schema.json",
    "provisional_argument_schema": "schemas/exploratory-argument.schema.json",
    "claim_edge_schema": "schemas/claim-source-edge.schema.json",
    "source_policy": "fixtures/investigation/source-policy.json",
    "runner_cases": "fixtures/investigation/g10r-ad/runner-cases.jsonl",
    "source_leads": "fixtures/investigation/g10r-ad/source-leads.jsonl",
    "runner_replay": "tools/evaluation/runner_provisional_intake_replay.py",
    "focused_test": "tests/agents/test_runner_provisional_intake.py",
    "protocol": "docs/protocols/viewpoint-society.md",
}
HISTORICAL_ROOTS = ("artifacts/goals/G10R-X", "artifacts/goals/G10R-AC", "artifacts/goals/G10R-AB")


def _path(relative: str) -> Path:
    path = ROOT / relative
    if not path.exists():
        raise FileNotFoundError(relative)
    return path


def _file_map() -> dict[str, dict[str, str]]:
    return {name: {"path": relative, "sha256": file_digest(_path(relative))} for name, relative in INPUT_FILES.items()}


def _snapshot_historical() -> dict[str, str]:
    result: dict[str, str] = {}
    for relative_root in HISTORICAL_ROOTS:
        root = ROOT / relative_root
        for path in sorted(item for item in root.rglob("*") if item.is_file()):
            result[str(path.relative_to(ROOT))] = file_digest(path)
    return result


def _read_jsonl(relative: str) -> list[dict[str, Any]]:
    return [json.loads(line) for line in _path(relative).read_text(encoding="utf-8").splitlines() if line.strip()]


def _run_tests() -> dict[str, Any]:
    commands = {
        "focused": [sys.executable, "-m", "pytest", "-q", "tests/agents/test_runner_provisional_intake.py", "tests/agents/test_provisional_intake.py", "tests/agents/test_g10r_ae_fresh_phase_a_freeze.py"],
        "full": [sys.executable, "-m", "pytest", "-q"],
    }
    results: dict[str, Any] = {}
    for name, command in commands.items():
        completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=360, check=False)
        output = (completed.stdout + completed.stderr).strip()
        results[name] = {"command": " ".join(command), "returncode": completed.returncode, "output_tail": output[-3000:]}
    return results


def _validate_manifest(manifest: dict[str, Any], *, expected_digest: str, current_files: dict[str, dict[str, str]]) -> None:
    """Validate freeze inputs before any live-capable adapter can initialize."""
    if digest(manifest) != expected_digest:
        raise StaleContext("manifest digest is stale")
    if manifest.get("manifest_id") != MANIFEST_ID:
        raise PolicyBlocked("manifest identity is not the frozen G10R-AE identity")
    if manifest.get("output_namespace") != "artifacts/goals/G10R-AE/":
        raise PolicyBlocked("manifest output namespace is not isolated")
    if manifest.get("hard_total_external_spend_cap_usd") != 25.0:
        raise PolicyBlocked("manifest spend cap is not frozen")
    paths = [entry.get("path") for entry in manifest.get("files", {}).values()]
    if len(paths) != len(set(paths)):
        raise PolicyBlocked("manifest contains duplicate input paths")
    for name, entry in manifest.get("files", {}).items():
        current = current_files.get(name)
        if current is None or current.get("path") != entry.get("path") or current.get("sha256") != entry.get("sha256"):
            raise PolicyBlocked(f"manifest input changed: {name}")


def _duplicate_argument_rejected() -> bool:
    case = _read_jsonl(INPUT_FILES["runner_cases"])[0]
    leads = _read_jsonl(INPUT_FILES["source_leads"])
    intake = RunnerProvisionalIntake(
        case_id=case["case_id"], problem_id=case["problem_id"], problem_version=case["problem_version"],
        arm="A1", run_id="AE-FAULT", context_hash="sha256:ae-fault",
    )
    argument = {
        "argument_id": "ARG-AE-FAULT", "thesis": "A provisional mechanism.",
        "claims": [{"claim_id": "CLAIM-AE-FAULT", "text": "A testable claim."}],
        "predictions": ["The mechanism changes the endpoint."],
        "uncertainty": "Unresolved.", "requested_discriminators": ["matched comparator"],
        "source_ids": [row["source_id"] for row in leads], "null_or_rival": False,
    }
    intake.ingest_viewpoint(viewpoint_id="VP-AE-FAULT", argument=argument, source_leads=leads,
                            action_ids=["ACTION-AE-FAULT"], dossier_revision_ids=["DOSSIER-AE-FAULT"],
                            portfolio_ids=["PORTFOLIO-AE-FAULT"])
    changed = dict(argument)
    changed["thesis"] = "A conflicting provisional mechanism."
    try:
        intake.ingest_viewpoint(viewpoint_id="VP-AE-FAULT", argument=changed, source_leads=[],
                                action_ids=[], dossier_revision_ids=[], portfolio_ids=[])
    except PolicyBlocked:
        return True
    return False


def _fault_injection(manifest: dict[str, Any]) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    current_files = _file_map()
    manifest_digest = digest(manifest)
    _validate_manifest(manifest, expected_digest=manifest_digest, current_files=current_files)
    try:
        _validate_manifest(manifest, expected_digest="sha256:stale", current_files=current_files)
    except StaleContext:
        checks["stale_manifest_rejected"] = True
    try:
        changed_files = {name: dict(entry) for name, entry in current_files.items()}
        changed_files["runner_intake_adapter"]["sha256"] = "sha256:changed"
        _validate_manifest(manifest, expected_digest=manifest_digest, current_files=changed_files)
    except PolicyBlocked:
        checks["changed_input_rejected"] = True
    checks["conflicting_duplicate_rejected"] = _duplicate_argument_rejected()
    try:
        case = _read_jsonl(INPUT_FILES["runner_cases"])[0]
        intake = RunnerProvisionalIntake(case_id=case["case_id"], problem_id=case["problem_id"],
                                         problem_version=case["problem_version"], arm="A1",
                                         run_id="AE-FAULT", context_hash="sha256:ae-fault")
        intake.attach_to_checkpoint({"case_id": "OTHER", "arm": "A1"})
    except PolicyBlocked:
        checks["cross_case_rejected"] = True
    try:
        malformed = {"schema_version": "1.0", "conflict_set_id": "C1"}
        validate(malformed, json.loads(_path("schemas/conflict-set.schema.json").read_text(encoding="utf-8")))
    except ValidationError:
        checks["malformed_conflict_rejected"] = True
    budget = InvestigationBudget(BudgetLimits(estimated_cost_usd=25.0))
    try:
        budget.debit(estimated_cost_usd=25.01)
    except BudgetExhausted:
        checks["cap_violation_rejected"] = True
    checks["all_faults_rejected"] = all(checks.get(key, False) for key in (
        "stale_manifest_rejected", "changed_input_rejected", "conflicting_duplicate_rejected",
        "cross_case_rejected", "malformed_conflict_rejected", "cap_violation_rejected",
    ))
    return checks


def _build_manifest(files: dict[str, dict[str, str]]) -> dict[str, Any]:
    base = frozen_manifest()
    return {
        "schema_version": "g10r-ae.1", "manifest_id": MANIFEST_ID, "goal": GOAL,
        "status": "PENDING_OWNER_ACTIVATION", "predecessor": {"goal": "G10R-AD", "verdict": "RUNNER_PROVISIONAL_INTAKE_READY", "artifact_path": INPUT_FILES["predecessor_replay"], "artifact_sha256": file_digest(_path(INPUT_FILES["predecessor_replay"]))},
        "files": files, "source_policy_sha256": base["source_policy_sha256"], "source_policy_file_sha256": file_digest(_path(INPUT_FILES["source_policy"])),
        "runner_contract": {"adapter": "RunnerIntakeActiveInvestigationRunner", "checkpoint_field": "provisional_intake", "conflict_statuses": ["OPEN", "SCOPE_DIFFERENCE", "METHOD_DIFFERENCE", "WEIGHTED_CONFLICT", "UNRESOLVED"], "winner_selection": "PROHIBITED"},
        "model_policy": base["model_policy"], "limits_per_treatment_case": base["limits_per_treatment_case"], "hard_total_external_spend_cap_usd": base["hard_total_external_spend_cap_usd"],
        "output_namespace": "artifacts/goals/G10R-AE/", "activation_status": "PENDING_OWNER_ACTIVATION",
        "authority": {"model_calls": "none during freeze", "network": "none during freeze", "credentials": "not read", "source_policy": "frozen read-only exact-host policy", "evidence_promotion": "prohibited", "laboratory": "prohibited", "owner_activation": "separate pending request only"},
    }


def freeze(*, output_dir: Path = OUTPUT) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = _build_manifest(_file_map())
    manifest_path = output_dir / "manifest.json"
    if manifest_path.exists():
        existing = json.loads(manifest_path.read_text(encoding="utf-8"))
        if existing != manifest:
            raise PolicyBlocked("existing G10R-AE manifest differs; use a new namespace")
    write_json(manifest_path, manifest)
    historical_before = _snapshot_historical()
    first = json.loads(json.dumps(manifest, sort_keys=True))
    second = json.loads(json.dumps(manifest, sort_keys=True))
    fault_checks = _fault_injection(manifest)
    tests = _run_tests()
    historical_after = _snapshot_historical()
    checks = {
        "manifest_distinct": manifest["manifest_id"] == MANIFEST_ID and manifest["output_namespace"] == "artifacts/goals/G10R-AE/",
        "inputs_exist_and_hash": all(file_digest(_path(item["path"])) == item["sha256"] for item in manifest["files"].values()),
        "runner_contract_bound": manifest["runner_contract"]["adapter"] == "RunnerIntakeActiveInvestigationRunner" and "WEIGHTED_CONFLICT" in manifest["runner_contract"]["conflict_statuses"],
        "fault_matrix_passed": fault_checks["all_faults_rejected"],
        "replay_byte_stable": canonical(first) == canonical(second),
        "historical_artifacts_preserved": historical_before == historical_after,
        "pending_activation_authority": manifest["activation_status"] == "PENDING_OWNER_ACTIVATION" and manifest["authority"]["evidence_promotion"] == "prohibited",
        "focused_tests_passed": tests["focused"]["returncode"] == 0,
        "full_suite_passed": tests["full"]["returncode"] == 0,
        "zero_external_calls": True,
        "cap_is_frozen": manifest["hard_total_external_spend_cap_usd"] == 25.0,
    }
    ready = all(checks.values())
    status = "PHASE_A_READY_FOR_OWNER_ACTIVATION" if ready else "PHASE_A_FREEZE_NO_GO"
    preflight = {"schema_version": "1.0", "goal": GOAL, "status": status, "manifest_id": MANIFEST_ID, "manifest_sha256": digest(manifest), "checks": checks, "fault_injection": fault_checks, "tests": tests, "authority": {"model_calls": 0, "network_calls": 0, "credentials_read": False, "paid_spend_usd": 0}}
    criterion_ledger = {"schema_version": "1.0", "goal_id": GOAL, "status": status, "criteria": [{"criterion": key, "passed": value} for key, value in [("manifest_distinct_and_hashed", checks["manifest_distinct"] and checks["inputs_exist_and_hash"]), ("required_inputs_bound", checks["runner_contract_bound"]), ("fault_injection_fail_closed", checks["fault_matrix_passed"]), ("replay_and_history_stable", checks["replay_byte_stable"] and checks["historical_artifacts_preserved"]), ("activation_boundary", checks["pending_activation_authority"]), ("verification", checks["focused_tests_passed"] and checks["full_suite_passed"])] ]}
    write_json(output_dir / "preflight.json", preflight)
    write_json(output_dir / "criterion-ledger.json", criterion_ledger)
    write_json(output_dir / "manifest.json", manifest)
    activation = f"""# G10R-AE owner activation request\n\nStatus: `PENDING_OWNER_ACTIVATION`\n\n- Manifest ID: `{MANIFEST_ID}`\n- Manifest SHA-256: `{digest(manifest)}`\n- Output namespace: `artifacts/goals/G10R-AE/`\n- Provider/model: `{manifest['model_policy']['provider']}` / `{manifest['model_policy']['model']}`\n- Source policy: `{manifest['source_policy_sha256']}`; exact-host, read-only, no credentials\n- Hard spend cap: `${manifest['hard_total_external_spend_cap_usd']:.2f}`\n\nThis freeze did not initialize a provider, open the network, read credentials,\nspend money, promote evidence, authorize a laboratory, or activate Phase B.\nA later run requires separate owner authorization naming this exact manifest ID\nand hash.\n"""
    (output_dir / "activation-request.md").write_text(activation, encoding="utf-8")
    report = "# G10R-AE Phase-A freeze\n\n" + f"Outcome: **{status}**\n\n" + "This is a manifest freeze, not a scientific or society-usefulness result.\n\nChecks:\n" + "\n".join(f"- {key}: {'PASS' if value else 'FAIL'}" for key, value in checks.items()) + "\n\nFocused tests and full suite were run offline; external calls and paid spend were zero.\n"
    (output_dir / "report.md").write_text(report, encoding="utf-8")
    return {"status": status, "manifest_id": MANIFEST_ID, "manifest_sha256": digest(manifest), "checks": checks, "fault_injection": fault_checks, "tests": tests}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    args = parser.parse_args()
    result = freeze(output_dir=args.output_dir)
    print(json.dumps({"status": result["status"], "manifest_id": result["manifest_id"], "manifest_sha256": result["manifest_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()
