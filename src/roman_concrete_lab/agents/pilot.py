"""G10B closed-world, capped C1 versus C4-lite signal pilot."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import validate

from .providers import BudgetExceeded, OpenAIProvider, ProviderUnavailable
from .providers.openai_provider import BudgetLedger, Pricing
from tools.tournament.replay import ROOT


PROTOCOL_VERSION = "g10b.1-signal-pilot"
ROLES = ("evidence_skeptic", "mechanism_proposer", "experimental_designer")
CAP_USD = 25.0
ROLE_MAX_OUTPUT = 1800
SINGLE_MAX_OUTPUT = ROLE_MAX_OUTPUT * 4
PROHIBITED_AUTHORITY = (
    "approved for execution",
    "safe to execute",
    "validated performance",
    "proven effective",
    "authorized laboratory",
)


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical(value).encode()).hexdigest()


def file_digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    ids = [row.get("case_id") for row in rows]
    if not ids or len(ids) != len(set(ids)):
        raise ValueError("case IDs must be non-empty and unique")
    return rows


def public_packet(case: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in case.items() if key != "rubric"}


def output_schema() -> dict[str, Any]:
    return json.loads((ROOT / "schemas/g10b-output.schema.json").read_text(encoding="utf-8"))


def prompts() -> dict[str, Any]:
    return json.loads((ROOT / "fixtures/agents/g10b/prompts.json").read_text(encoding="utf-8"))


def _output_text(output: dict[str, Any]) -> str:
    parts = [output["summary"], output["recommended_action"], output["authority_note"]]
    for finding in output["findings"]:
        parts.extend(
            [
                finding["statement"],
                finding["predicted_observation"],
                finding["disconfirming_observation"],
                finding["uncertainty"],
            ]
        )
    return " ".join(parts).lower()


def score_output(case: dict[str, Any], output: dict[str, Any]) -> dict[str, Any]:
    validate(output, output_schema())
    valid_ids = {item["evidence_id"] for item in case["evidence"]}
    cited_ids = {
        evidence_id
        for finding in output["findings"]
        for evidence_id in finding["evidence_ids"]
    }
    invalid_ids = sorted(cited_ids - valid_ids)
    text = _output_text(output)
    hits = []
    for criterion in case["rubric"]:
        keyword_hit = any(keyword.lower() in text for keyword in criterion["keywords_any"])
        evidence_hit = bool(cited_ids.intersection(criterion["evidence_any"]))
        hits.append(
            {
                "criterion_id": criterion["criterion_id"],
                "points": criterion["points"] if keyword_hit and evidence_hit else 0,
                "keyword_hit": keyword_hit,
                "evidence_hit": evidence_hit,
            }
        )
    critical = [f"invalid_evidence_id:{item}" for item in invalid_ids]
    critical.extend(f"authority_expansion:{phrase}" for phrase in PROHIBITED_AUTHORITY if phrase in text)
    supported_pairs = sorted(
        {
            digest(
                {
                    "evidence_ids": sorted(finding["evidence_ids"]),
                    "prediction": finding["predicted_observation"].strip().lower(),
                    "disconfirmation": finding["disconfirming_observation"].strip().lower(),
                }
            )
            for finding in output["findings"]
            if finding["kind"] in {"HYPOTHESIS", "DISCRIMINATOR"}
            and finding["evidence_ids"]
            and not set(finding["evidence_ids"]) - valid_ids
            and finding["predicted_observation"].strip()
            and finding["disconfirming_observation"].strip()
        }
    )
    return {
        "score": sum(item["points"] for item in hits),
        "max_score": sum(item["points"] for item in case["rubric"]),
        "rubric_hits": hits,
        "cited_evidence_ids": sorted(cited_ids),
        "invalid_evidence_ids": invalid_ids,
        "provenance_completeness": round(
            sum(bool(item["evidence_ids"]) for item in output["findings"]) / len(output["findings"]), 4
        ),
        "supported_prediction_discriminator_digests": supported_pairs,
        "critical_failures": critical,
    }


def run_control(case: dict[str, Any]) -> dict[str, Any]:
    evidence = case["evidence"][0]
    output = {
        "case_id": case["case_id"],
        "task_type": case["task_type"],
        "status": "REVIEW_REQUIRED",
        "summary": f"The packet is incomplete; preserve uncertainty around {evidence['evidence_id']}.",
        "findings": [
            {
                "finding_id": "C0-1",
                "kind": "LIMITATION",
                "statement": evidence["text"],
                "evidence_ids": [evidence["evidence_id"]],
                "predicted_observation": "",
                "disconfirming_observation": "",
                "uncertainty": "The deterministic control does not generate a new rival or discriminator.",
            }
        ],
        "recommended_action": "Qualified review is required; do not promote the claim.",
        "authority_note": "This is a non-authorizing derived output.",
    }
    validate(output, output_schema())
    return output


def frozen_manifest() -> dict[str, Any]:
    paths = {
        "protocol": ROOT / "docs/protocols/g10b-real-model-ablation.md",
        "prompts": ROOT / "fixtures/agents/g10b/prompts.json",
        "development_cases": ROOT / "fixtures/agents/g10b/development.jsonl",
        "sealed_cases": ROOT / "fixtures/agents/g10b/sealed.jsonl",
        "output_schema": ROOT / "schemas/g10b-output.schema.json",
        "pilot_runner": ROOT / "src/roman_concrete_lab/agents/pilot.py",
        "openai_provider": ROOT / "src/roman_concrete_lab/agents/providers/openai_provider.py",
    }
    return {
        "protocol_version": PROTOCOL_VERSION,
        "files": {name: {"path": str(path.relative_to(ROOT)), "sha256": file_digest(path)} for name, path in paths.items()},
        "model": "gpt-6-luna",
        "reasoning_effort": "low",
        "call_count": 20,
        "budget_cap_usd": CAP_USD,
        "role_max_output_tokens": ROLE_MAX_OUTPUT,
        "single_max_output_tokens": SINGLE_MAX_OUTPUT,
        "store": False,
        "tools": [],
    }


def phase_a() -> dict[str, Any]:
    cases = load_jsonl(ROOT / "fixtures/agents/g10b/sealed.jsonl")
    schema = output_schema()
    controls = []
    for case in cases:
        output = run_control(case)
        validate(output, schema)
        controls.append({"case_id": case["case_id"], "output": output, "score": score_output(case, output)})
    perfect = all(item["score"]["score"] == item["score"]["max_score"] for item in controls)
    manifest = frozen_manifest()
    return {
        "phase": "A",
        "status": "READY_FOR_LIVE_PILOT" if not perfect else "INVALID_C0_CEILING",
        "manifest": manifest,
        "manifest_sha256": digest(manifest),
        "c0_has_headroom": not perfect,
        "controls": controls,
        "authority": {"model_calls": "none", "network": "none", "lab_execution": "prohibited"},
    }


def _instructions(base: str, treatment: str) -> str:
    return base + "\n\n" + treatment


def _load_checkpoint(path: Path, manifest_hash: str) -> dict[str, Any]:
    if not path.exists():
        return {"manifest_sha256": manifest_hash, "traces": {}}
    checkpoint = json.loads(path.read_text(encoding="utf-8"))
    if checkpoint.get("manifest_sha256") != manifest_hash:
        raise ValueError("STALE_CONTEXT: checkpoint manifest does not match frozen inputs")
    return checkpoint


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _call_or_replay(
    provider: OpenAIProvider,
    checkpoint: dict[str, Any],
    checkpoint_path: Path,
    *,
    call_id: str,
    instructions: str,
    packet: dict[str, Any],
    max_output_tokens: int,
) -> dict[str, Any]:
    if call_id in checkpoint["traces"]:
        trace = dict(checkpoint["traces"][call_id])
        trace["replayed"] = True
        return trace
    trace = provider.call(
        call_id=call_id,
        instructions=instructions,
        packet=packet,
        max_output_tokens=max_output_tokens,
    )
    trace["replayed"] = False
    checkpoint["traces"][call_id] = trace
    _write_json(checkpoint_path, checkpoint)
    return trace


def live_pilot(output_dir: Path | None = None) -> dict[str, Any]:
    output_dir = output_dir or (ROOT / "artifacts/goals/G10B")
    phase_a_result = phase_a()
    if phase_a_result["status"] != "READY_FOR_LIVE_PILOT":
        raise RuntimeError("Phase A did not establish C0 headroom")
    manifest_hash = phase_a_result["manifest_sha256"]
    checkpoint_path = output_dir / "live/checkpoint.json"
    checkpoint = _load_checkpoint(checkpoint_path, manifest_hash)
    already_spent = sum(
        trace.get("estimated_actual_cost_usd", 0.0) for trace in checkpoint["traces"].values()
    )
    budget = BudgetLedger(CAP_USD, already_spent)
    provider = OpenAIProvider(root=ROOT, schema=output_schema(), budget=budget, pricing=Pricing())
    prompt_set = prompts()
    cases = load_jsonl(ROOT / "fixtures/agents/g10b/sealed.jsonl")
    records = []
    try:
        for case in cases:
            packet = public_packet(case)
            single = _call_or_replay(
                provider,
                checkpoint,
                checkpoint_path,
                call_id=f"{case['case_id']}:C1",
                instructions=_instructions(prompt_set["system"], prompt_set["single_analyst"]),
                packet=packet,
                max_output_tokens=SINGLE_MAX_OUTPUT,
            )
            role_traces = []
            for role in ROLES:
                role_traces.append(
                    _call_or_replay(
                        provider,
                        checkpoint,
                        checkpoint_path,
                        call_id=f"{case['case_id']}:C4:{role}",
                        instructions=_instructions(prompt_set["system"], prompt_set["roles"][role]),
                        packet=packet,
                        max_output_tokens=ROLE_MAX_OUTPUT,
                    )
                )
            adjudication_packet = dict(packet)
            adjudication_packet["role_outputs"] = [
                {"role": role, "output": trace["output"]} for role, trace in zip(ROLES, role_traces)
            ]
            society = _call_or_replay(
                provider,
                checkpoint,
                checkpoint_path,
                call_id=f"{case['case_id']}:C4:adjudicator",
                instructions=_instructions(prompt_set["system"], prompt_set["adjudicator"]),
                packet=adjudication_packet,
                max_output_tokens=ROLE_MAX_OUTPUT,
            )
            records.append(
                {
                    "case_id": case["case_id"],
                    "C1": single,
                    "C4_lite": society,
                    "role_traces": role_traces,
                    "role_output_distinct_count": len({digest(trace["output"]) for trace in role_traces}),
                }
            )
    except BudgetExceeded:
        status = "BUDGET_EXHAUSTED"
    except ProviderUnavailable:
        status = "PROVIDER_UNAVAILABLE"
        raise
    else:
        status = "COMPLETED"
    result = finalize(phase_a_result, cases, records, checkpoint, status, budget.spent_usd)
    _write_json(output_dir / "run.json", result)
    return result


def finalize(
    phase_a_result: dict[str, Any],
    cases: list[dict[str, Any]],
    records: list[dict[str, Any]],
    checkpoint: dict[str, Any],
    status: str,
    spent_usd: float,
) -> dict[str, Any]:
    blinded = []
    arm_map = {}
    for record in records:
        for arm in ("C1", "C4_lite"):
            blind_id = digest({"case_id": record["case_id"], "arm": arm})[7:19]
            blinded.append({"blind_id": blind_id, "case_id": record["case_id"], "output": record[arm]["output"]})
            arm_map[blind_id] = arm
    scored_blind = []
    case_by_id = {case["case_id"]: case for case in cases}
    for item in sorted(blinded, key=lambda row: row["blind_id"]):
        scored_blind.append(
            {
                "blind_id": item["blind_id"],
                "case_id": item["case_id"],
                "score": score_output(case_by_id[item["case_id"]], item["output"]),
            }
        )
    scores = {(item["case_id"], arm_map[item["blind_id"]]): item["score"] for item in scored_blind}
    complete = len(records) == len(cases) and status == "COMPLETED"
    critical = [
        failure
        for score in scores.values()
        for failure in score["critical_failures"]
    ]
    improvements = []
    society_total = 0
    single_total = 0
    distinct_increment = False
    for case in cases:
        if (case["case_id"], "C1") not in scores:
            continue
        single = scores[(case["case_id"], "C1")]
        society = scores[(case["case_id"], "C4_lite")]
        delta = society["score"] - single["score"]
        improvements.append({"case_id": case["case_id"], "delta": delta})
        society_total += society["score"]
        single_total += single["score"]
        if delta >= 1 and set(society["supported_prediction_discriminator_digests"]) - set(
            single["supported_prediction_discriminator_digests"]
        ):
            distinct_increment = True
    role_collapse = any(record["role_output_distinct_count"] < 2 for record in records)
    if not complete:
        decision = "INCONCLUSIVE_G10B_EVALUATION"
    elif not critical and not role_collapse and any(item["delta"] >= 1 for item in improvements) and society_total >= single_total and distinct_increment:
        decision = "ESCALATE_TO_G10C_FULL_EVALUATION"
    else:
        decision = "DO_NOT_ESCALATE_AGENT_SOCIETY"
    return {
        "goal": "G10B",
        "protocol_version": PROTOCOL_VERSION,
        "phase_a": phase_a_result,
        "live_status": status,
        "decision": decision,
        "call_count_completed": len(checkpoint.get("traces", {})),
        "estimated_actual_cost_usd": round(spent_usd, 8),
        "budget_cap_usd": CAP_USD,
        "records": records,
        "blinded_scores": scored_blind,
        "arm_map": arm_map,
        "arm_map_sha256": digest(arm_map),
        "comparison": {
            "case_deltas": improvements,
            "C1_total": single_total,
            "C4_lite_total": society_total,
            "supported_distinct_increment": distinct_increment,
            "role_collapse": role_collapse,
            "critical_failures": critical,
        },
        "authority": {
            "network": "api.openai.com only",
            "retrieval": "none",
            "tools": "none",
            "evidence_write": "prohibited",
            "lab_execution": "prohibited",
            "external_communication": "prohibited",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("a", "live"), default="a")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.phase == "a":
        result = phase_a()
        if args.write:
            _write_json(ROOT / "artifacts/goals/G10B/phase-a.json", result)
    else:
        result = live_pilot()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
