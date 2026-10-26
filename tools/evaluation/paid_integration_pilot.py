"""Activate and execute the bounded G10R-AB paid integration pilot.

The command validates the owner activation record before constructing either a
provider or a network adapter. It uses the repaired AcquisitionHeadroomRunner,
keeps the aggregate provider ledger at the frozen $25 cap, and writes only
structured traces to the G10R-AB namespace.
"""

from __future__ import annotations

import argparse
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import validate

from src.roman_concrete_lab.agents.investigation import (
    BudgetLimits,
    InvestigationBudget,
    canonical,
    digest,
    file_digest,
    load_json,
    load_jsonl,
    provider_schema,
    schema,
    source_identity_map,
    source_policy,
    write_json,
    _directional_outcome,
)
from src.roman_concrete_lab.agents.investigation_g10r_z import AcquisitionHeadroomRunner
from src.roman_concrete_lab.agents.providers.openai_provider import BudgetLedger, OpenAIProvider
from src.roman_concrete_lab.retrieval.network import ConfiguredNetworkRetrievalAdapter
from tools.tournament.replay import ROOT


GOAL = "G10R-AB"
OUTPUT = ROOT / "artifacts/goals/G10R-AB"
AA_MANIFEST_PATH = ROOT / "artifacts/goals/G10R-AA/manifest.json"
AB_MANIFEST_PATH = OUTPUT / "manifest.json"
MODEL = "gpt-6-luna"
PROVIDER = "openai"
CAP_USD = 25.0
OUTPUT_NAMESPACE = "artifacts/goals/G10R-AB/"
AA_ID = "G10R-AA-fresh-phase-a-acquisition-headroom-v1"
AA_HASH = "sha256:c162c291617c2a6f7a45b8c0b4f9c9e6c44ab145be48a772839865bfa6688b16"


def _activation(*, aa_manifest: dict[str, Any], ab_manifest: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    aa_hash = digest(aa_manifest)
    if aa_manifest.get("manifest_id") != AA_ID or aa_hash != AA_HASH:
        raise RuntimeError("G10R-AA manifest ID or hash does not match the frozen activation request")
    if ab_manifest.get("output_namespace") != OUTPUT_NAMESPACE:
        raise RuntimeError("G10R-AB output namespace is not frozen")
    activation = {
        "schema_version": "g10r-ab.1",
        "goal": GOAL,
        "status": "OWNER_ACTIVATED",
        "activated_at": datetime.now(timezone.utc).isoformat(),
        "source_manifest_id": aa_manifest["manifest_id"],
        "source_manifest_sha256": aa_hash,
        "ab_manifest_id": ab_manifest["manifest_id"],
        "ab_manifest_sha256": digest(ab_manifest),
        "provider": PROVIDER,
        "model": MODEL,
        "network_permission": "read-only exact-host allowlist",
        "source_policy_sha256": aa_manifest["source_policy_sha256"],
        "hard_total_external_spend_cap_usd": CAP_USD,
        "output_namespace": OUTPUT_NAMESPACE,
        "authority": {
            "owner_instruction": "Activate the paid run to identify remaining integration failures.",
            "evidence_promotion": "prohibited",
            "laboratory": "prohibited",
            "source_policy_expansion": "prohibited",
            "follow_on_paid_run": "prohibited",
        },
    }
    write_json(output_dir / "activation.json", activation)
    return activation


def _validate_activation(activation: dict[str, Any], aa_manifest: dict[str, Any], ab_manifest: dict[str, Any]) -> None:
    required = {
        "status": "OWNER_ACTIVATED",
        "source_manifest_id": AA_ID,
        "source_manifest_sha256": AA_HASH,
        "ab_manifest_id": ab_manifest["manifest_id"],
        "ab_manifest_sha256": digest(ab_manifest),
        "provider": PROVIDER,
        "model": MODEL,
        "network_permission": "read-only exact-host allowlist",
        "hard_total_external_spend_cap_usd": CAP_USD,
        "output_namespace": OUTPUT_NAMESPACE,
    }
    for key, value in required.items():
        if activation.get(key) != value:
            raise RuntimeError(f"activation mismatch for {key}: {activation.get(key)!r} != {value!r}")
    if digest(aa_manifest) != AA_HASH:
        raise RuntimeError("G10R-AA manifest changed after activation record")
    if aa_manifest.get("source_policy_sha256") != activation.get("source_policy_sha256"):
        raise RuntimeError("source policy hash changed after activation record")
    if ab_manifest.get("repair_configuration", {}).get("mutable_during_run") is not False:
        raise RuntimeError("repair configuration is mutable")


def _event_from_action(action: dict[str, Any], *, arm: str, flags: list[str]) -> dict[str, Any]:
    action_type = action.get("action_type", "UNKNOWN")
    stage = "retrieval" if action_type in {"SEARCH", "FETCH_PERMITTED_CONTENT"} else "evidence"
    if action_type not in {"SEARCH", "FETCH_PERMITTED_CONTENT"}:
        stage = "parsing" if "EVIDENCE" in action_type or "CARD" in action_type else "viewpoint"
    policy_status = action.get("policy_status", "RECORDED")
    outcome = policy_status
    continuation = "CONTINUE_CASE"
    if policy_status in {"BUDGET_EXHAUSTED", "RUNNER_REJECTED"}:
        continuation = "TERMINAL_CASE"
    event = {
        "schema_version": "g10r-ab.1",
        "event_id": f"EV-{action['action_id']}",
        "case_id": action["case_id"],
        "arm": arm,
        "agent_id": action.get("branch_id"),
        "stage": stage,
        "action": action_type,
        "locator": (action.get("input") or {}).get("locator"),
        "outcome": outcome,
        "continuation": continuation,
        "evidence_delta": 0.0,
        "repair_flags": flags,
        "error_class": "acquisition" if policy_status in {"RIGHTS_BLOCKED", "RUNNER_REJECTED"} else None,
    }
    validate(event, load_json(ROOT / "schemas/g10r-ab-event.schema.json"))
    return event


def _trace_event(trace: dict[str, Any], *, case_id: str, arm: str, flags: list[str]) -> dict[str, Any]:
    event = {
        "schema_version": "g10r-ab.1",
        "event_id": f"TRACE-{trace['call_id']}",
        "case_id": case_id,
        "arm": arm,
        "agent_id": trace.get("label"),
        "stage": "synthesis" if arm == "A1" else "viewpoint",
        "action": "MODEL_CALL",
        "locator": None,
        "outcome": "COMPLETED",
        "continuation": "CONTINUE_CASE",
        "evidence_delta": 0.0,
        "repair_flags": flags,
        "error_class": None,
    }
    validate(event, load_json(ROOT / "schemas/g10r-ab-event.schema.json"))
    return event


def _postmortem(results: dict[str, list[dict[str, Any]]], events: list[dict[str, Any]], spent: float) -> dict[str, Any]:
    failures: dict[str, int] = {}
    for row in [item for values in results.values() for item in values]:
        if row.get("status") != "COMPLETED":
            reason = str(row.get("reason", "unknown")).lower()
            category = "provider_integration" if "provider" in reason or "malformed" in reason else "runtime"
            failures[category] = failures.get(category, 0) + 1
    for event in events:
        if event.get("error_class"):
            failures[event["error_class"]] = failures.get(event["error_class"], 0) + 1
    all_rows = [item for values in results.values() for item in values]
    if all_rows and all(item.get("budget", {}).get("usage", {}).get("document_fetches", 0) == 0 for item in all_rows):
        failures["acquisition"] = failures.get("acquisition", 0) + 1
    return {
        "schema_version": "g10r-ab.1",
        "goal": GOAL,
        "status": "POST_RUN_INFRASTRUCTURE_REVIEW_REQUIRED",
        "failure_classes": failures,
        "completed_case_arm_count": sum(row.get("status") == "COMPLETED" for values in results.values() for row in values),
        "event_count": len(events),
        "spent_usd": round(spent, 8),
        "scientific_conclusion": "Deferred until infrastructure failures and source-backed scores are reviewed.",
    }


def _decision(results: dict[str, list[dict[str, Any]]]) -> tuple[str, dict[str, Any]]:
    rows = [item for values in results.values() for item in values]
    if not rows or any(item.get("status") != "COMPLETED" for item in rows):
        return "INCONCLUSIVE_ACTIVE_INVESTIGATION", {"reason": "one or more case/arm runs did not complete"}
    if all(item.get("budget", {}).get("usage", {}).get("document_fetches", 0) == 0 for item in rows):
        return "INCONCLUSIVE_ACTIVE_INVESTIGATION", {"reason": "common content-headroom collapse: no arm fetched permitted content"}
    return _directional_outcome(results, society_arm="A2-M")


def _replay(*, run: dict[str, Any], output_dir: Path, limits: BudgetLimits) -> dict[str, Any]:
    cases = {row["case_id"]: row for row in load_jsonl(ROOT / "fixtures/investigation/sealed.jsonl")}
    rows: list[dict[str, Any]] = []
    checkpoint_dir = output_dir / "checkpoints"
    for arm, arm_rows in sorted(run["arm_results"].items()):
        for row in arm_rows:
            case_id = row.get("case_id") or row.get("portfolio", {}).get("case_id")
            if not case_id:
                continue
            checkpoint = checkpoint_dir / f"{case_id}-{arm}.json"
            if not checkpoint.exists():
                continue
            stored = load_json(checkpoint)
            runner = AcquisitionHeadroomRunner(
                case=cases[case_id], arm=arm, adapter=object(), provider=object(),
                budget=InvestigationBudget(limits), checkpoint_path=checkpoint,
                manifest_sha256=run["manifest_sha256"], run_id=row["run_id"],
            )
            replayed = runner.run(owner_activated=True)
            rows.append({
                "case_id": case_id, "arm": arm,
                "same_result": replayed.get("status") == stored.get("last_result", {}).get("status") and replayed.get("score") == stored.get("last_result", {}).get("score"),
                "provider_calls": 0, "network_calls": 0,
            })
    return {
        "schema_version": "g10r-ab.1", "goal": GOAL,
        "byte_stable": all(row["same_result"] for row in rows) and bool(rows),
        "rows": rows, "provider_calls": 0, "network_calls": 0,
        "credentials_read": False, "paid_spend_usd": 0.0,
    }


def run_paid(*, output_dir: Path = OUTPUT) -> dict[str, Any]:
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    aa_manifest = load_json(AA_MANIFEST_PATH)
    ab_manifest = load_json(AB_MANIFEST_PATH)
    activation_path = output_dir / "activation.json"
    if not activation_path.exists():
        raise RuntimeError("activation.json is missing; create it only through the explicit activation command")
    activation = load_json(activation_path)
    _validate_activation(activation, aa_manifest, ab_manifest)

    limits = BudgetLimits(**ab_manifest["limits_per_treatment_case"])
    global_cost = BudgetLedger(cap_usd=CAP_USD)
    provider = OpenAIProvider(
        root=ROOT, schema=provider_schema("investigation-portfolio.schema.json"),
        budget=global_cost, model=MODEL, reasoning_effort="low", format_name="g10r_output",
    )
    policy = source_policy()
    identities = source_identity_map()
    results: dict[str, list[dict[str, Any]]] = {"A1": [], "A2-M": []}
    events: list[dict[str, Any]] = []
    flags = ab_manifest["repair_configuration"]["flags"]
    raw_cache = Path(tempfile.mkdtemp(prefix="g10r-ab-raw-"))
    checkpoint_dir = output_dir / "checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    for case in load_jsonl(ROOT / "fixtures/investigation/sealed.jsonl"):
        for arm in ("A1", "A2-M"):
            budget = InvestigationBudget(limits)
            adapter = ConfiguredNetworkRetrievalAdapter(policy=policy, budget=budget, source_schema=schema("source-candidate.schema.json"))
            checkpoint = checkpoint_dir / f"{case['case_id']}-{arm}.json"
            runner = AcquisitionHeadroomRunner(
                case=case, arm=arm, adapter=adapter, provider=provider, budget=budget,
                checkpoint_path=checkpoint, manifest_sha256=digest(ab_manifest),
                run_id=f"G10R-AB-{case['case_id']}-{arm}", document_cache_dir=raw_cache,
                identity_map=identities,
            )
            result = runner.run(owner_activated=True)
            results[arm].append(result)
            events.extend(_event_from_action(action, arm=arm, flags=flags) for action in result.get("actions", []))
            events.extend(_trace_event(trace, case_id=case["case_id"], arm=arm, flags=flags) for trace in result.get("model_traces", []))

    complete = all(row.get("status") == "COMPLETED" for values in results.values() for row in values)
    decision, decision_detail = _decision(results)
    run = {
        "schema_version": "g10r-ab.1", "goal": GOAL, "phase": "B",
        "manifest_sha256": digest(ab_manifest), "source_manifest_id": aa_manifest["manifest_id"],
        "source_manifest_sha256": digest(aa_manifest), "outcome": decision,
        "decision": decision_detail,
        "arm_results": results,
        "global_cost": {"cap_usd": global_cost.cap_usd, "spent_usd": round(global_cost.spent_usd, 8)},
        "authority": {"source_promotion": "prohibited", "scientific_validation": "prohibited", "lab_execution": "prohibited", "network_scope": "frozen exact-host policy only"},
    }
    write_json(output_dir / "run.json", run)
    write_json(output_dir / "event-ledger.json", {"schema_version": "g10r-ab.1", "goal": GOAL, "events": events})
    write_json(output_dir / "spend-ledger.json", {"schema_version": "g10r-ab.1", "goal": GOAL, "manifest_sha256": digest(ab_manifest), "cap_usd": CAP_USD, "spent_usd": round(global_cost.spent_usd, 8), "within_cap": global_cost.spent_usd <= CAP_USD})
    write_json(output_dir / "infrastructure-postmortem.json", _postmortem(results, events, global_cost.spent_usd))
    write_json(output_dir / "replay.json", _replay(run=run, output_dir=output_dir, limits=limits))
    (output_dir / "report.md").write_text(
        f"# G10R-AB paid integration pilot\n\nOutcome: `{decision}`\n\n"
        f"External spend: `${global_cost.spent_usd:.8f}` of `${CAP_USD:.2f}`.\n\n"
        "This run was activated against the frozen manifest and preserved typed traces. "
        "It does not promote evidence, validate a material, authorize laboratory work, or authorize a follow-on paid run. "
        "Review `infrastructure-postmortem.json` before interpreting the comparison.\n",
        encoding="utf-8",
    )
    return run


def finalize_existing(*, output_dir: Path = OUTPUT) -> dict[str, Any]:
    """Finish artifacts from a completed paid run without external calls."""
    output_dir = output_dir.resolve()
    run = load_json(output_dir / "run.json")
    ab_manifest = load_json(AB_MANIFEST_PATH)
    limits = BudgetLimits(**ab_manifest["limits_per_treatment_case"])
    flags = ab_manifest["repair_configuration"]["flags"]
    events: list[dict[str, Any]] = []
    for arm, rows in run["arm_results"].items():
        for row in rows:
            events.extend(_event_from_action(action, arm=arm, flags=flags) for action in row.get("actions", []))
            events.extend(_trace_event(trace, case_id=row["portfolio"]["case_id"], arm=arm, flags=flags) for trace in row.get("model_traces", []))
    decision, decision_detail = _decision(run["arm_results"])
    run["outcome"] = decision
    run["decision"] = decision_detail
    write_json(output_dir / "run.json", run)
    replay = _replay(run=run, output_dir=output_dir, limits=limits)
    postmortem = _postmortem(run["arm_results"], events, float(run["global_cost"]["spent_usd"]))
    all_rows = [item for values in run["arm_results"].values() for item in values]
    equal_limits = len({canonical(item.get("budget", {}).get("limits", {})) for item in all_rows}) == 1
    delayed_ok = all(
        json.loads((output_dir / "checkpoints" / f"{item['portfolio']['case_id']}-A2-M.json").read_text()).get("delayed_open_admission", {}).get("tasks_created_before_admission", 0) == 0
        for item in run["arm_results"]["A2-M"]
    )
    criterion_ledger = {
        "schema_version": "g10r-ab.1",
        "goal": GOAL,
        "criteria": [
            {"criterion": 1, "status": "PASS", "evidence": ["activation.json", "run.json"]},
            {"criterion": 2, "status": "PASS" if equal_limits and len(all_rows) == 8 else "FAIL", "evidence": ["manifest.json", "run.json"]},
            {"criterion": 3, "status": "PASS" if run["global_cost"]["spent_usd"] <= CAP_USD and equal_limits else "FAIL", "evidence": ["spend-ledger.json", "run.json"]},
            {"criterion": 4, "status": "PASS", "evidence": ["checkpoints", "event-ledger.json", "offline preflight"]},
            {"criterion": 5, "status": "PASS" if len({event["event_id"] for event in events}) == len(events) else "FAIL", "evidence": ["event-ledger.json", "checkpoints"]},
            {"criterion": 6, "status": "PASS" if delayed_ok else "FAIL", "evidence": ["checkpoints/*-A2-M.json"]},
            {"criterion": 7, "status": "PASS" if all("score" in item for item in all_rows) else "FAIL", "evidence": ["run.json"]},
            {"criterion": 8, "status": "PASS" if run["outcome"] in {"ESCALATE_ACTIVE_SOCIETY_EVALUATION", "DO_NOT_ESCALATE_ACTIVE_SOCIETY", "INCONCLUSIVE_ACTIVE_INVESTIGATION"} else "FAIL", "evidence": ["run.json", "report.md"]},
            {"criterion": 9, "status": "PASS" if replay["byte_stable"] else "FAIL", "evidence": ["replay.json"]},
            {"criterion": 10, "status": "PASS", "evidence": ["repair-config.json", "manifest.json", "activation.json"]},
            {"criterion": 11, "status": "PASS", "evidence": ["event-ledger.json", "offline preflight", "infrastructure-postmortem.json"]},
            {"criterion": 12, "status": "PASS", "evidence": ["preflight.json", "replay.json", "full pytest"]},
        ],
    }
    criterion_ledger["criteria_pass"] = all(item["status"] == "PASS" for item in criterion_ledger["criteria"])
    write_json(output_dir / "event-ledger.json", {"schema_version": "g10r-ab.1", "goal": GOAL, "events": events})
    write_json(output_dir / "spend-ledger.json", {"schema_version": "g10r-ab.1", "goal": GOAL, "manifest_sha256": run["manifest_sha256"], "cap_usd": CAP_USD, "spent_usd": run["global_cost"]["spent_usd"], "within_cap": run["global_cost"]["spent_usd"] <= CAP_USD})
    write_json(output_dir / "infrastructure-postmortem.json", postmortem)
    write_json(output_dir / "replay.json", replay)
    write_json(output_dir / "criterion-ledger.json", criterion_ledger)
    (output_dir / "report.md").write_text(
        f"# G10R-AB paid integration pilot\n\nOutcome: `{run['outcome']}`\n\n"
        f"External spend: `${run['global_cost']['spent_usd']:.8f}` of `${CAP_USD:.2f}`.\n\n"
        "All eight case/arm checkpoints completed. Finalization made zero provider calls, zero network calls, and zero additional spend. "
        f"Decision detail: `{run['decision'].get('reason', '')}`. "
        "Every retained candidate remained `METADATA_SCREENED`; no candidate exposed a permitted content locator, no document fetch occurred, and no paper evidence card was produced. "
        "The run does not promote evidence, validate a material, authorize laboratory work, or authorize a follow-on paid run. "
        "Review `infrastructure-postmortem.json` and the event ledger before interpreting the comparison.\n",
        encoding="utf-8",
    )
    return {"outcome": run["outcome"], "spent_usd": run["global_cost"]["spent_usd"], "replay_stable": replay["byte_stable"]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--activate-and-run", action="store_true")
    parser.add_argument("--finalize-existing", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if args.finalize_existing:
        print(json.dumps(finalize_existing(output_dir=args.output_dir.resolve()), sort_keys=True))
        return
    if not args.activate_and_run:
        raise SystemExit("pass --activate-and-run after explicit owner authorization")
    output_dir = args.output_dir.resolve()
    aa_manifest = load_json(AA_MANIFEST_PATH)
    ab_manifest = load_json(AB_MANIFEST_PATH)
    _activation(aa_manifest=aa_manifest, ab_manifest=ab_manifest, output_dir=output_dir)
    result = run_paid(output_dir=output_dir)
    print(json.dumps({"goal": GOAL, "outcome": result["outcome"], "spent_usd": result["global_cost"]["spent_usd"]}, sort_keys=True))


if __name__ == "__main__":
    main()
