"""Run and replay the explicitly activated G10R-B2 comparison."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.roman_concrete_lab.agents.investigation import run_phase_b, write_json
from tools.evaluation.open_world_replay import replay as open_world_replay
from tools.tournament.replay import ROOT


OUTPUT_DIR = ROOT / "artifacts/goals/G10R-B2"
PHASE_PATH = ROOT / "artifacts/goals/G10R/phase-a-post-constraint-20261023.json"


def write_report(run: dict, replay: dict, path: Path) -> None:
    path.write_text(
        "\n".join([
            "# G10R-B2 post-constraint active-investigation rerun",
            "",
            "## Handoff",
            "",
            f"`{run.get('outcome', 'INCONCLUSIVE_ACTIVE_INVESTIGATION')}`",
            "",
            f"- Manifest: `{run.get('manifest_sha256')}`",
            f"- A1 completed cases: `{len(run.get('arm_results', {}).get('A1', []))}`",
            f"- A2-M completed cases: `{len(run.get('arm_results', {}).get('A2-M', []))}`",
            f"- Recorded cumulative spend: `${run.get('global_cost', {}).get('spent_usd', 0):.8f}` of `$25.00`",
            f"- Open-world replay: `{replay.get('status')}`",
            "",
            "This run used the distinct post-constraint manifest and output namespace. It did not promote evidence, authorize laboratory work, widen source policy, or grant production authority.",
            "",
            "## Authority",
            "",
            "Model calls and exact-host read-only retrieval were explicitly activated for this goal. No external writes, subscription access, lab execution, or evidence promotion were permitted.",
            "",
        ]) + "\n",
        encoding="utf-8",
    )


def run(*, output_dir: Path = OUTPUT_DIR) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    result = run_phase_b(
        owner_activated=True,
        output_dir=output_dir,
        phase_path=PHASE_PATH,
        spend_roots=[ROOT / "artifacts/goals/G10R/checkpoints", ROOT / "artifacts/goals/G10R-B2/checkpoints", output_dir / "checkpoints"],
    )
    run_path = output_dir / "run.json"
    replay = open_world_replay(
        run_path=run_path,
        checkpoint_dir=output_dir / "checkpoints",
        phase_path=PHASE_PATH,
    )
    write_json(output_dir / "replay.json", replay)
    write_report(result, replay, output_dir / "report.md")
    return {"run": result, "replay": replay}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    result = run(output_dir=args.output_dir)
    print(json.dumps({
        "outcome": result["run"].get("outcome"),
        "replay_status": result["replay"].get("status"),
        "spent_usd": result["run"].get("global_cost", {}).get("spent_usd"),
    }, indent=2))


if __name__ == "__main__":
    main()
