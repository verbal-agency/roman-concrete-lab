"""Finalize the activated G10R-V run without external calls.

This is deliberately a post-run artifact builder.  It never initializes a
provider or retrieval adapter that can make a network request; completed
checkpoints are replayed through the runner's completed-run path with inert
objects and their returned portfolio/score/status are compared to the stored
result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.roman_concrete_lab.agents.investigation import (
    ActiveInvestigationRunner,
    InvestigationBudget,
    load_jsonl,
)
from tools.tournament.replay import ROOT


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def replay_run(*, run_path: Path, checkpoint_dir: Path) -> dict[str, Any]:
    run = json.loads(run_path.read_text(encoding="utf-8"))
    cases = {row["case_id"]: row for row in load_jsonl(ROOT / "fixtures/investigation/sealed.jsonl")}
    rows: list[dict[str, Any]] = []
    for arm, arm_rows in sorted(run["arm_results"].items()):
        for row in sorted(arm_rows, key=lambda item: item["portfolio"]["case_id"]):
            case_id = row["portfolio"]["case_id"]
            checkpoint = checkpoint_dir / f"{case_id}-{arm}.json"
            stored = json.loads(checkpoint.read_text(encoding="utf-8"))
            runner = ActiveInvestigationRunner(
                case=cases[case_id],
                arm=arm,
                adapter=object(),
                provider=object(),
                budget=InvestigationBudget(),
                checkpoint_path=checkpoint,
                manifest_sha256=run["manifest_sha256"],
                run_id=row["run_id"],
            )
            replayed = runner.run(owner_activated=True)
            same_result = replayed["portfolio"] == stored["last_result"]["portfolio"] and replayed["score"] == stored["last_result"]["score"] and replayed["status"] == stored["last_result"]["status"]
            rows.append(
                {
                    "arm": arm,
                    "case_id": case_id,
                    "checkpoint": str(checkpoint.relative_to(ROOT)),
                    "stored_last_result_digest": digest(stored["last_result"]),
                    "replayed_result_digest": digest({"portfolio": replayed["portfolio"], "score": replayed["score"], "status": replayed["status"]}),
                    "same_portfolio_score_status": same_result,
                    "provider_calls": 0,
                    "network_calls": 0,
                }
            )
    return {
        "schema_version": "g10r-v-replay.1",
        "run_id": run_path.stem,
        "manifest_sha256": run["manifest_sha256"],
        "external_calls": False,
        "replay_stable": all(row["same_portfolio_score_status"] for row in rows),
        "rows": rows,
    }


def _arm_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    usage = [row["budget"]["usage"] for row in rows]
    scores = [row["score"] for row in rows]
    return {
        "cases": len(rows),
        "discovery_score_raw": sum(score.get("discovery_score", 0) for score in scores),
        "hypothesis_score_raw": sum(score.get("hypothesis_score", 0) for score in scores),
        "rubric_score": sum(score.get("score", 0) for score in scores),
        "evidence_score": sum(score.get("evidence_score", 0) for score in scores),
        "unique_contribution_count": sum(len(score.get("supported_contribution_digests", [])) for score in scores),
        "unresolved_source_count": sum(len(score.get("unresolved_source_candidate_ids", [])) for score in scores),
        "queries": sum(item.get("queries", 0) for item in usage),
        "retained_sources": sum(item.get("retained_sources", 0) for item in usage),
        "fetches": sum(item.get("document_fetches", 0) for item in usage),
        "input_tokens": sum(item.get("input_tokens", 0) for item in usage),
        "output_tokens": sum(item.get("output_tokens", 0) for item in usage),
        "estimated_cost_usd": round(sum(item.get("estimated_cost_usd", 0.0) for item in usage), 7),
        "model_trace_count": sum(len(row.get("model_traces", [])) for row in rows),
    }


def finalize(*, root: Path = ROOT) -> dict[str, Any]:
    source_manifest = root / "artifacts/goals/G10R-X/manifest.json"
    output = root / "artifacts/goals/G10R-V"
    run_path = output / "run.json"
    run = json.loads(run_path.read_text(encoding="utf-8"))
    manifest = json.loads(source_manifest.read_text(encoding="utf-8"))
    manifest_hash = digest(manifest)
    if manifest_hash != run["manifest_sha256"]:
        raise RuntimeError(f"run/manifest mismatch: {run['manifest_sha256']} != {manifest_hash}")
    target_manifest = output / "manifest.json"
    shutil.copyfile(source_manifest, target_manifest)

    replay = replay_run(run_path=run_path, checkpoint_dir=output / "checkpoints")
    (output / "replay.json").write_text(json.dumps(replay, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    arm_summaries = {arm: _arm_summary(rows) for arm, rows in sorted(run["arm_results"].items())}
    decision = run["decision"]
    spend = {
        "schema_version": "g10r-v-spend-ledger.1",
        "run_id": run_path.stem,
        "manifest_sha256": run["manifest_sha256"],
        "provider": "OpenAI Responses / gpt-6-luna / low",
        "cap_usd": run["global_cost"]["cap_usd"],
        "spent_usd": run["global_cost"]["spent_usd"],
        "within_cap": run["global_cost"]["spent_usd"] <= run["global_cost"]["cap_usd"],
        "arms": arm_summaries,
    }
    (output / "spend-ledger.json").write_text(json.dumps(spend, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    report = f"""# G10R-V post-run report

**Outcome:** `{run['outcome']}`
**Manifest:** `{run['manifest_sha256']}`
**Provider:** OpenAI Responses / `gpt-6-luna` / low reasoning
**External spend:** `${run['global_cost']['spent_usd']:.7f}` of `${run['global_cost']['cap_usd']:.2f}`

## What was tested

The frozen four-case comparison ran A1 (single investigator) and A2-M (viewpoint society with structural support agents) under the same source policy and ceilings. The run completed all eight case/arm checkpoints. No laboratory work, evidence promotion, subscription access, or source-policy expansion was authorized.

## Result

The terminal decision is `{run['outcome']}`. Neither arm earned a positive rubric score or evidence score, and the society produced no qualifying unique contribution over A1:

```json
{json.dumps(decision, indent=2, sort_keys=True)}
```

The raw discovery/hypothesis counters are useful diagnostics, not evidence credit. A1 produced more raw discovery and hypothesis material in aggregate than A2-M, while A2-M did produce some candidates and hypotheses. Those records remained unresolved or unsupported by the typed source-backed rubric, so they could not change the decision.

## Arm diagnostics

| arm | raw discovery | raw hypotheses | rubric score | evidence score | unresolved sources | queries | estimated cost |
|---|---:|---:|---:|---:|---:|---:|---:|
| A1 | {arm_summaries['A1']['discovery_score_raw']} | {arm_summaries['A1']['hypothesis_score_raw']} | {arm_summaries['A1']['rubric_score']} | {arm_summaries['A1']['evidence_score']} | {arm_summaries['A1']['unresolved_source_count']} | {arm_summaries['A1']['queries']} | ${arm_summaries['A1']['estimated_cost_usd']:.7f} |
| A2-M | {arm_summaries['A2-M']['discovery_score_raw']} | {arm_summaries['A2-M']['hypothesis_score_raw']} | {arm_summaries['A2-M']['rubric_score']} | {arm_summaries['A2-M']['evidence_score']} | {arm_summaries['A2-M']['unresolved_source_count']} | {arm_summaries['A2-M']['queries']} | ${arm_summaries['A2-M']['estimated_cost_usd']:.7f} |

## Replay and integrity

Offline replay was run for all eight completed checkpoints with inert provider/adapter objects. It made zero provider and zero network calls; `replay.json` records the per-checkpoint comparisons. The replay result is `{str(replay['replay_stable']).lower()}`. The exact G10R-X manifest was copied and hash-checked before finalization, and the hard aggregate cap was not exceeded.

## Interpretation and next goal

This is a fair negative signal for the current society wiring and task design, not proof that agent societies are intrinsically unhelpful. The bottleneck is conversion: the run generated some candidate and hypothesis material, but source identity, task-criterion matching, and evidence attribution did not turn it into supported contributions. The next goal should be offline diagnosis and targeted ablation of acquisition-to-rubric conversion (including why A1 outperformed A2-M on the same cases), with no automatic paid rerun until that diagnosis produces a new frozen treatment.
"""
    (output / "report.md").write_text(report, encoding="utf-8")
    return {"outcome": run["outcome"], "manifest_sha256": run["manifest_sha256"], "replay_stable": replay["replay_stable"], "spend": spend}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    print(json.dumps(finalize(root=args.root), indent=2, sort_keys=True))
