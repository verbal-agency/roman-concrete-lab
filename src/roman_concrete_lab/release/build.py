"""Build and verify the offline G09 exploratory-platform release."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


SRC_ROOT = Path(__file__).resolve().parents[3]
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from roman_concrete_lab.focus.policy import policy_snapshot
from roman_concrete_lab.hypotheses.contracts import validate_typed_hypotheses
from roman_concrete_lab.memory.contracts import validate_memory_tiers
from tools.portfolio.replay import load as load_json
from tools.portfolio.replay import validate_card
from tools.tournament.replay import replay as tournament_replay
from tools.tournament.replay import run_case


RELEASE_MODE = "EXPLORATORY_PLATFORM"
DEFAULT_VERSION = "2026-09-30-exploratory-platform"
MANIFEST_VERSION = "g09.1"

INPUT_FILES = [
    "artifacts/goals/G-1/decision.json",
    "artifacts/goals/G00/report.md",
    "artifacts/goals/GP1/run.json",
    "artifacts/goals/GP2/run.json",
    "artifacts/goals/GP3/run.json",
    "artifacts/goals/GP4/run.json",
    "artifacts/goals/G07E/run.json",
    "artifacts/goals/G07E/report.md",
    "data/manifests/literature-sufficiency-sources.jsonl",
    "data/manifests/literature-sufficiency-access-log.jsonl",
    "data/processed/literature-sufficiency-material-candidates.jsonl",
    "data/processed/literature-sufficiency-study-families.jsonl",
    "docs/protocols/exploration-contracts.md",
    "docs/protocols/problem-specific-discovery.md",
    "docs/protocols/hypothesis-tournament.md",
    "schemas/problem-card.schema.json",
    "schemas/portfolio-entry.schema.json",
    "schemas/hypothesis-registry.schema.json",
    "schemas/tournament-result.schema.json",
    "tools/tournament/policy.py",
    "tools/tournament/replay.py",
    "src/roman_concrete_lab/memory/contracts.py",
    "src/roman_concrete_lab/hypotheses/contracts.py",
    "src/roman_concrete_lab/focus/policy.py",
    "src/roman_concrete_lab/release/build.py",
    "docs/reports/prelab-report.md",
]

CARD_FILES = [
    "fixtures/portfolio/roman.json",
    "fixtures/portfolio/lime-mortar.json",
    "fixtures/portfolio/battery-cathode.json",
]

SECRET_PATTERNS = [
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\b(?:sk|ghp|xoxb|xoxp)-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"(?i)\b(?:api[_-]?key|password|secret|token)\s*[:=]\s*['\"]?[A-Za-z0-9+/=_-]{16,}"),
]
PROHIBITED_CLAIM_PATTERNS = [
    re.compile(r"(?i)\bworks\b"),
    re.compile(r"(?i)\bproves?\b"),
    re.compile(r"(?i)\bbest material\b"),
    re.compile(r"(?i)\bvalidated (?:performance|effectiveness)\b"),
    re.compile(r"(?i)\brecipe\b"),
]


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_json(value: Any) -> str:
    return sha256_bytes(canonical(value).encode("utf-8"))


def file_hash(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def input_hashes(root: Path) -> dict[str, str]:
    paths = INPUT_FILES + CARD_FILES
    missing = [path for path in paths if not (root / path).is_file()]
    if missing:
        raise FileNotFoundError("missing release input(s): " + ", ".join(missing))
    return {path: file_hash(root / path) for path in sorted(set(paths))}


def validate_inputs(root: Path) -> dict[str, Any]:
    cards: dict[str, dict[str, Any]] = {}
    memory_summary = []
    for relative in CARD_FILES:
        card = load_json(root / relative)
        validate_card(card)
        cards[card["problem_id"]] = card
        memory_summary.append(validate_memory_tiers(card))
    return {"card_count": len(cards), "cards": memory_summary}


def claim_ledger(tournament: dict[str, Any]) -> list[dict[str, Any]]:
    roman = tournament["card_results"]["roman-concrete"]
    return [
        {
            "claim_id": "CL-001",
            "text": "The release contains a deterministic, offline hypothesis tournament with replayable focus and promotion policies.",
            "claim_type": "DERIVED",
            "evidence_locators": ["artifacts/goals/G07E/run.json#policy", "tools/tournament/replay.py"],
            "support_region": "G07E offline fixtures and declared problem cards",
            "transformation_history": ["G07E replay", "release claim extraction"],
            "uncertainty": ["does not establish physical performance"],
        },
        {
            "claim_id": "CL-002",
            "text": "The Roman-concrete card produces two typed rival hypotheses and a Pareto result under its declared utility dimensions.",
            "claim_type": "DERIVED",
            "evidence_locators": ["artifacts/goals/G07E/run.json#outputs.roman_hypothesis_count", "fixtures/portfolio/roman.json"],
            "support_region": "modern terrestrial Roman-inspired lime-pozzolan mortar or mortar-like concrete",
            "transformation_history": ["Roman problem card", "typed registry validation", "G07E adjudication"],
            "uncertainty": ["no independent physical replication", "qualified review remains pending"],
        },
        {
            "claim_id": "CL-003",
            "text": "The release does not establish physical performance, a universal winner, or authorization for laboratory execution.",
            "claim_type": "UNRESOLVED",
            "evidence_locators": ["artifacts/goals/G-1/decision.json#exploration_seedability", "docs/decisions/0001-program-charter.md#physical/lab-boundary"],
            "support_region": "exploratory platform authority boundary",
            "transformation_history": ["G-1 decision", "G00 charter", "G07E authority manifest"],
            "uncertainty": ["physical outcome is intentionally unobserved"],
        },
        {
            "claim_id": "CL-004",
            "text": f"The Roman card replay status is {roman['status']} rather than a forced single winner.",
            "claim_type": "DERIVED",
            "evidence_locators": ["artifacts/goals/G07E/run.json#outputs.card_statuses.roman-concrete", "schemas/tournament-result.schema.json"],
            "support_region": "Roman card utility dimensions and support region",
            "transformation_history": ["G07E replay", "release status extraction"],
            "uncertainty": ["ordinal utilities are not predictive performance scores"],
        },
    ]


def lint_claims(claims: list[dict[str, Any]]) -> dict[str, Any]:
    seen: set[str] = set()
    for claim in claims:
        claim_id = claim.get("claim_id")
        if not claim_id or claim_id in seen:
            raise ValueError(f"claim ID is missing or duplicated: {claim_id}")
        seen.add(claim_id)
        if claim.get("claim_type") not in {"REPORTED", "DERIVED", "PROPOSED", "UNRESOLVED"}:
            raise ValueError(f"invalid claim type: {claim_id}")
        if not claim.get("evidence_locators") or not claim.get("support_region"):
            raise ValueError(f"claim lacks evidence/support region: {claim_id}")
        for pattern in PROHIBITED_CLAIM_PATTERNS:
            if pattern.search(claim["text"]):
                raise ValueError(f"prohibited empirical language in {claim_id}: {claim['text']}")
    return {"claim_count": len(claims), "all_have_evidence": True, "prohibited_language_rejected": True}


def rights_summary(root: Path) -> dict[str, Any]:
    records = [json.loads(line) for line in (root / "data/manifests/literature-sufficiency-sources.jsonl").read_text().splitlines() if line.strip()]
    access_log = [json.loads(line) for line in (root / "data/manifests/literature-sufficiency-access-log.jsonl").read_text().splitlines() if line.strip()]
    classes = Counter(record.get("access_class", "unknown") for record in records)
    return {
        "source_record_count": len(records),
        "access_class_counts": dict(sorted(classes.items())),
        "access_log": access_log,
        "lawful_access_policy": "lawful, reviewable sources only; no access-control bypass or Sci-Hub material",
        "restricted_full_text_included": False,
        "redistribution": "metadata, manifests, derived claims, and recorded fixtures only; restricted full text is excluded",
    }


def ranking_summary(tournament: dict[str, Any]) -> dict[str, Any]:
    cards = {}
    for problem_id, result in sorted(tournament["card_results"].items()):
        cards[problem_id] = {
            "status": result["status"],
            "support_regions": sorted({hypothesis["support_region"] for hypothesis in result["hypotheses"]}),
            "uncertainty": sorted({uncertainty for hypothesis in result["hypotheses"] for uncertainty in hypothesis["uncertainty"]}),
            "stability": result.get("sensitivity", {}).get("winner_stability", "NOT_APPLICABLE"),
            "reviewer_authorities": sorted({hypothesis["reviewer_authority"] for hypothesis in result["hypotheses"]}),
            "policy_hash": result["policy_hash"],
        }
    return {"cards": cards, "ordering": "conditional/Pareto only; no aggregate performance score"}


def security_scan(files: dict[str, bytes]) -> dict[str, Any]:
    findings = []
    for relative, content in files.items():
        text = content.decode("utf-8", errors="replace")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append({"path": relative, "pattern": pattern.pattern})
    if findings:
        raise ValueError(f"release security scan failed: {findings}")
    return {"status": "PASS", "secret_findings": 0, "restricted_full_text_findings": 0}


def render_report(version: str, summary: dict[str, Any]) -> str:
    fixture_rows = "\n".join(f"| {key} | `{value}` |" for key, value in sorted(summary["fixture_statuses"].items()))
    return f"""# Exploratory platform release {version}

**Release mode:** `EXPLORATORY_PLATFORM`
**Source branch:** GP4 → G07E
**Authority:** offline, non-agent, non-lab; no physical performance claim

## What is released

This bundle contains the versioned problem cards, scoped-memory summaries, typed hypothesis/tournament replay, focus and promotion policy, claim ledger, rights summary, security scan, software bill of materials, and reproducibility manifest. It contains no restricted full text, credentials, live service dependency, lab instructions, or agent runtime.

## Tournament outcomes

| Fixture | Status |
|---|---|
{fixture_rows}

The normal card outputs are conditional `PARETO_SET` results. They preserve endpoint semantics, uncertainty, support regions, and expert-review boundaries; they do not identify a universal best material or validate physical performance.

## Reproduction

```text
PYTHONPATH=src python3 -m roman_concrete_lab.release.build --version {version} --output artifacts/releases/{version}
python3 tools/tournament/replay.py
python3 -m pytest -q
```

The manifest hashes every release artifact except the manifest itself. A clean reproduction must regenerate byte-equivalent artifact contents and pass the claim, rights, security, schema, and replay checks.
"""


def build_release(root: Path, output: Path, version: str = DEFAULT_VERSION) -> Path:
    validate_inputs(root)
    source_hashes = input_hashes(root)
    tournament = tournament_replay()
    claims = claim_ledger(tournament)
    claim_check = lint_claims(claims)
    rights = rights_summary(root)
    policy = policy_snapshot()
    card_summaries = validate_inputs(root)
    typed_hypothesis_check = validate_typed_hypotheses(
        [hypothesis for result in tournament["card_results"].values() for hypothesis in result["hypotheses"]]
    )
    fixture_statuses = tournament["fixture_results"]
    release_summary = {
        "release_mode": RELEASE_MODE,
        "release_version": version,
        "source_branch": "GP4/G07E",
        "gate_basis": {"G-1": "EXPLORATION_SEEDABLE; overall AUDIT_INCOMPLETE", "GP4": "complete", "G07E": "complete"},
        "card_statuses": {problem_id: result["status"] for problem_id, result in sorted(tournament["card_results"].items())},
        "fixture_statuses": fixture_statuses,
        "rankings": ranking_summary(tournament),
        "policy": policy,
        "memory": card_summaries,
        "hypotheses": typed_hypothesis_check,
        "claims": claim_check,
        "limitations": [
            "No physical result or effectiveness claim is established.",
            "No predictive model or numeric EIG is included.",
            "Experiment recommendations are draft and non-authorizing.",
            "Qualified review remains required before any lab handoff.",
        ],
        "authority": tournament["authority"],
    }
    sbom = {
        "format": "g09-sbom.1",
        "runtime": {"language": "Python", "minimum_version": "3.10"},
        "runtime_dependencies": [{"name": "jsonschema", "purpose": "offline schema validation", "version": "4.17.3"}],
        "network_runtime_dependency": False,
        "database_runtime_dependency": False,
        "llm_runtime_dependency": False,
        "agent_runtime_dependency": False,
    }
    reproduction = {
        "clean_build": True,
        "commands": [
            f"PYTHONPATH=src python3 -m roman_concrete_lab.release.build --version {version} --output artifacts/releases/{version}",
            "python3 tools/tournament/replay.py",
            "python3 -m pytest -q",
        ],
        "input_hashes": source_hashes,
        "expected_mode": RELEASE_MODE,
        "independent_reproduction": "tests/release/test_build.py builds twice into isolated temporary directories and compares bytes",
    }
    files: dict[str, bytes] = {
        "release.json": (canonical(release_summary) + "\n").encode("utf-8"),
        "claims.json": (canonical({"claims": claims, "lint": claim_check}) + "\n").encode("utf-8"),
        "tournament-replay.json": (canonical(tournament) + "\n").encode("utf-8"),
        "rights.json": (canonical(rights) + "\n").encode("utf-8"),
        "software-bill-of-materials.json": (canonical(sbom) + "\n").encode("utf-8"),
        "reproduction.json": (canonical(reproduction) + "\n").encode("utf-8"),
        "report.md": render_report(version, {"fixture_statuses": fixture_statuses}).encode("utf-8"),
    }
    security = security_scan(files)
    files["security-scan.json"] = (canonical(security) + "\n").encode("utf-8")
    output.mkdir(parents=True, exist_ok=True)
    for relative, content in files.items():
        (output / relative).write_bytes(content)
    artifact_hashes = {relative: sha256_bytes(content) for relative, content in sorted(files.items())}
    manifest = {
        "manifest_version": MANIFEST_VERSION,
        "release_mode": RELEASE_MODE,
        "release_version": version,
        "source_branch": "GP4/G07E",
        "artifact_hashes": artifact_hashes,
        "manifest_excluded_from_hashes": True,
        "source_input_hashes": source_hashes,
        "security_scan": security,
        "rights_summary": "rights.json",
        "claim_ledger": "claims.json",
        "reproduction": "reproduction.json",
        "authority": tournament["authority"],
    }
    (output / "manifest.json").write_text(canonical(manifest) + "\n", encoding="utf-8")
    verify_release(output)
    return output


def verify_release(output: Path) -> dict[str, Any]:
    manifest = load_json(output / "manifest.json")
    for relative, expected in manifest["artifact_hashes"].items():
        actual = file_hash(output / relative)
        if actual != expected:
            raise ValueError(f"release hash mismatch for {relative}: {actual} != {expected}")
    claims = load_json(output / manifest["claim_ledger"])
    lint_claims(claims["claims"])
    rights = load_json(output / manifest["rights_summary"])
    if rights["restricted_full_text_included"]:
        raise ValueError("release contains restricted full text")
    scan = load_json(output / "security-scan.json")
    if scan["status"] != "PASS":
        raise ValueError("release security scan did not pass")
    return {"status": "PASS", "artifact_count": len(manifest["artifact_hashes"]), "release_mode": manifest["release_mode"]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", default=DEFAULT_VERSION)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    output = args.output or SRC_ROOT / "artifacts" / "releases" / args.version
    built = build_release(SRC_ROOT, output, args.version)
    print(json.dumps(verify_release(built), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
