"""G10R active-investigation contracts, offline freeze, scoring, and replay core."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
from copy import deepcopy
from dataclasses import asdict
from pathlib import Path
from typing import Any

from jsonschema import validate

from ..retrieval import (
    AppendOnlyLedger,
    BudgetExhausted,
    BudgetLimits,
    BudgetUsage,
    InvestigationBudget,
    PolicyBlocked,
    RecordedRetrievalAdapter,
    SourcePolicy,
    StaleContext,
    canonical,
    digest,
    transition_source_candidate,
)
from ..retrieval.pdf import PARSER_ID, extract_pdf, select_relevant_page_spans
from .providers import BudgetExceeded, ProviderUnavailable
from ..simulation import SimulationRegistry
from tools.tournament.replay import ROOT


PROTOCOL_VERSION = "g10r.4-active-investigation-pilot"
MODEL = "gpt-6-luna"
REASONING_EFFORT = "low"
CAP_USD = 25.0
SEALED_CASE_COUNT = 4
DEVELOPMENT_CASE_MINIMUM = 2
PLAN_OUTPUT_TOKENS = 800
BRANCHES = ("evidence_skeptic", "mechanism_transfer", "experiment_simulation")
LEGAL_OUTCOMES = (
    "ESCALATE_ACTIVE_SOCIETY_EVALUATION",
    "DO_NOT_ESCALATE_ACTIVE_SOCIETY",
    "INCONCLUSIVE_ACTIVE_INVESTIGATION",
)
RUN_TRANSITIONS = {
    "created": {"policy_loaded", "failed"},
    "policy_loaded": {"context_frozen", "policy_blocked", "failed"},
    "context_frozen": {"planning", "failed"},
    "planning": {"round_1", "provider_unavailable", "budget_exhausted", "failed"},
    "round_1": {"sharing", "network_unavailable", "provider_unavailable", "budget_exhausted", "failed"},
    "sharing": {"focus_allocated", "failed"},
    "focus_allocated": {"round_2", "budget_exhausted", "failed"},
    "round_2": {"adjudicating", "network_unavailable", "provider_unavailable", "budget_exhausted", "failed"},
    "adjudicating": {"scored", "provider_unavailable", "failed"},
    "scored": {"completed", "inconclusive", "failed"},
}
TERMINAL_RUN_STATES = {
    "completed",
    "failed",
    "budget_exhausted",
    "provider_unavailable",
    "network_unavailable",
    "policy_blocked",
    "inconclusive",
}
PROHIBITED_AUTHORITY = (
    "approved for execution",
    "safe to execute",
    "validated performance",
    "proven effective",
    "authorized laboratory",
    "promoted to immutable evidence",
)
AUTHORITY_NEGATION = re.compile(
    r"\b(no|not|never|without|cannot|can't|does not|do not|none|unresolved|unestablished)\b"
)
AUTHORITY_NEGATED_ACTION = re.compile(
    r"\b(no|not|never|without|cannot|can't|does not|do not)\b.{0,80}\b(claim|assert|present|treat|promote|authorize)\b"
)
AUTHORITY_REFERENCE_CONTEXT = re.compile(
    r"\b(criteria|criterion|case question|question|requirement|eligibility|rubric|"
    r"must\s+(?:supply|meet|include|demonstrate)|would\s+need|whether|if|could|might)\b"
)
FABRICATION_PROOF_METHODS = {
    "LOCATOR_RESOLVES_TO_DIFFERENT_WORK",
    "HASH_CONFLICT_WITH_CLAIMED_SOURCE",
    "AUTHOR_OR_TITLE_CONFLICT",
    "SOURCE_OWNER_DENIES_RECORD",
    "CROSS_SOURCE_MISREPRESENTATION",
}


class RunnerRejected(RuntimeError):
    """The runner could not execute a requested action with its configured adapter."""


def file_digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    ids = [row.get("case_id") or row.get("source_candidate_id") for row in rows]
    if not ids or len(ids) != len(set(ids)):
        raise ValueError(f"records in {path} must have non-empty unique IDs")
    return rows


def schema(name: str) -> dict[str, Any]:
    return load_json(ROOT / "schemas" / name)


def _without_external_hypothesis_ref(document_schema: dict[str, Any]) -> dict[str, Any]:
    local = deepcopy(document_schema)
    local["properties"]["hypotheses"]["items"] = {"type": "object"}
    return local


def validate_portfolio(portfolio: dict[str, Any]) -> None:
    validate(portfolio, _without_external_hypothesis_ref(schema("investigation-portfolio.schema.json")))
    hypothesis_schema = schema("lateral-hypothesis.schema.json")
    for hypothesis in portfolio["hypotheses"]:
        validate(hypothesis, hypothesis_schema)


def validate_branch_report(report: dict[str, Any]) -> None:
    validate(report, _without_external_hypothesis_ref(schema("branch-report.schema.json")))
    hypothesis_schema = schema("lateral-hypothesis.schema.json")
    for hypothesis in report["hypotheses"]:
        validate(hypothesis, hypothesis_schema)


def validate_paper_evidence_card(card: dict[str, Any], document: dict[str, Any]) -> None:
    validate(card, schema("paper-evidence-card.schema.json"))
    if card["document_hash"] != document["content_hash"]:
        raise PolicyBlocked("evidence card does not bind to fetched document hash")
    page_hashes = {page["locator"]: page["text_hash"] for page in document["pages"]}
    for fact in card["facts"]:
        if fact["page_locator"] not in page_hashes:
            raise PolicyBlocked("evidence card cites a page outside the fetched document")
        if fact["page_text_hash"] != page_hashes[fact["page_locator"]]:
            raise PolicyBlocked("evidence card page hash does not match fetched document")


def provider_schema(name: str) -> dict[str, Any]:
    """Return a strict-subset schema suitable for the Responses API.

    The local contracts intentionally retain JSON-Schema constraints such as
    ``const`` and ``format`` for offline validation.  OpenAI structured
    outputs accepts a narrower subset: every object field must be required,
    every object must close additional properties, and scalar types must be
    explicit.  Normalize only the provider copy; responses are still checked
    against the full local contract after they return.
    """
    document = deepcopy(schema(name))
    hypothesis = schema("lateral-hypothesis.schema.json")
    if "hypotheses" in document.get("properties", {}):
        document["properties"]["hypotheses"]["items"] = hypothesis
    return _strict_provider_schema(document)


def _strict_provider_schema(document: dict[str, Any]) -> dict[str, Any]:
    """Normalize a local JSON Schema to the Responses structured-output subset."""
    scalar_types = {str: "string", int: "integer", float: "number", bool: "boolean", type(None): "null"}

    def normalize(node: Any) -> Any:
        if isinstance(node, list):
            return [normalize(item) for item in node]
        if not isinstance(node, dict):
            return node
        if "$ref" in node:
            return node
        result = {key: normalize(value) for key, value in node.items() if key not in {
            "$schema", "$id", "title", "description", "format", "minLength", "maxLength",
            "minItems", "maxItems", "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum",
            "pattern", "uniqueItems",
        }}
        if "const" in result:
            value = result.pop("const")
            result["type"] = scalar_types.get(type(value), "string")
            result["enum"] = [value]
        if isinstance(result.get("type"), list):
            result["anyOf"] = [{"type": item} for item in result.pop("type")]
        if "enum" in result and "type" not in result and "anyOf" not in result:
            values = result["enum"]
            types = {scalar_types.get(type(value), "string") for value in values}
            if len(types) == 1:
                result["type"] = next(iter(types))
            else:
                result["anyOf"] = [{"type": item} for item in sorted(types)]
        if result.get("type") == "object":
            properties = result.get("properties", {})
            result["properties"] = properties
            result["required"] = sorted(properties)
            result["additionalProperties"] = False
        return result

    normalized = normalize(document)
    assert isinstance(normalized, dict)
    return normalized


def validate_plan(plan: dict[str, Any], *, case_id: str, branch_id: str) -> None:
    validate(plan, schema("investigation-plan.schema.json"))
    if plan["case_id"] != case_id or plan["branch_id"] != branch_id:
        raise PolicyBlocked("plan case or branch does not match frozen treatment context")


def public_case(case: dict[str, Any]) -> dict[str, Any]:
    hidden = {"hidden_information_need", "expected_source_ids", "rubric"}
    return {key: value for key, value in case.items() if key not in hidden}


def prompts() -> dict[str, Any]:
    return load_json(ROOT / "fixtures/investigation/prompts.json")


def source_policy() -> SourcePolicy:
    return SourcePolicy.load(ROOT / "fixtures/investigation/source-policy.json")


def source_identity_map() -> dict[str, Any]:
    """Load the hidden evaluation-only map for live metadata identities."""
    return load_json(ROOT / "fixtures/investigation/source-identity-map.json")


def _identity_text(value: str) -> str:
    return " ".join(value.casefold().split())


def resolve_source_identity(
    source_candidate_id: str,
    *,
    candidate_records: dict[str, dict[str, Any]] | None,
    identity_map: dict[str, Any] | None,
) -> str | None:
    """Resolve a live OA/CR candidate without exposing hidden aliases to the model."""
    if identity_map is None:
        return source_candidate_id
    entries = identity_map["entries"]
    if source_candidate_id in entries:
        return source_candidate_id
    candidate = (candidate_records or {}).get(source_candidate_id)
    if candidate is None:
        return None
    candidate_keys = {candidate.get("deduplication_key")}
    candidate_locators = {candidate.get("locator"), candidate.get("content_locator")}
    candidate_title = _identity_text(candidate.get("title", ""))
    matches = []
    for canonical_id, entry in entries.items():
        if candidate_keys.intersection(entry.get("deduplication_keys", [])):
            matches.append(canonical_id)
            continue
        if candidate_locators.intersection(entry.get("locators", [])):
            matches.append(canonical_id)
            continue
        if candidate_title and candidate_title == _identity_text(entry.get("title", "")):
            matches.append(canonical_id)
    if len(matches) > 1:
        raise PolicyBlocked(f"live source identity is ambiguous: {source_candidate_id} -> {sorted(matches)}")
    return matches[0] if matches else None


def validate_source_identity_map(
    identity_map: dict[str, Any],
    *,
    recorded_sources: list[dict[str, Any]],
    cases: list[dict[str, Any]],
) -> dict[str, Any]:
    """Validate hidden aliases against recorded candidates and sealed expectations."""
    if identity_map.get("schema_version") != "1.0":
        raise ValueError("source identity map schema version is not 1.0")
    entries = identity_map.get("entries", {})
    expected = sorted({source_id for case in cases for source_id in case["expected_source_ids"]})
    missing = sorted(set(expected) - set(entries))
    if missing:
        raise ValueError(f"source identity map is missing expected IDs: {missing}")
    records = {source["source_candidate_id"]: source for source in recorded_sources}
    resolutions = {}
    for source_id, source in records.items():
        resolved = resolve_source_identity(source_id, candidate_records=records, identity_map=identity_map)
        if source_id in entries and resolved != source_id:
            raise ValueError(f"recorded source {source_id} resolves to {resolved}")
        if source_id in expected and resolved != source_id:
            raise ValueError(f"expected source {source_id} has no exact identity mapping")
        resolutions[source_id] = resolved
    key_owners: dict[str, str] = {}
    for canonical_id, entry in entries.items():
        for key in entry.get("deduplication_keys", []):
            previous = key_owners.setdefault(key, canonical_id)
            if previous != canonical_id:
                raise ValueError(f"identity key collision: {key}")
    return {
        "passes": True,
        "expected_ids": expected,
        "entry_count": len(entries),
        "recorded_resolutions": resolutions,
        "live_candidate_rule": "exact deduplication key, locator, or normalized title; ambiguous matches fail closed",
    }


def _portfolio_text(portfolio: dict[str, Any]) -> str:
    values = [
        portfolio["summary"],
        portfolio["next_discriminating_action"],
        portfolio["authority_note"],
        *portfolio["unresolved_disputes"],
        *portfolio["negative_searches"],
    ]
    for hypothesis in portfolio["hypotheses"]:
        values.extend(
            [
                hypothesis["novelty_basis"],
                hypothesis["transfer_type"],
                hypothesis["intervention"],
                hypothesis["comparator"],
                hypothesis["predicted_observation"],
                hypothesis["falsifier"],
                hypothesis["support_region"],
                hypothesis["uncertainty"],
            ]
        )
    return " ".join(values).lower()


def _authority_flags(portfolio: dict[str, Any]) -> list[dict[str, Any]]:
    """Find authority language while preserving whether it is explicitly negated."""
    flags: list[dict[str, Any]] = []
    segments = [
        portfolio["summary"],
        portfolio["next_discriminating_action"],
        portfolio["authority_note"],
        *portfolio["unresolved_disputes"],
        *portfolio["negative_searches"],
    ]
    for hypothesis in portfolio["hypotheses"]:
        segments.extend(
            [
                hypothesis["novelty_basis"],
                hypothesis["transfer_type"],
                hypothesis["intervention"],
                hypothesis["comparator"],
                hypothesis["predicted_observation"],
                hypothesis["falsifier"],
                hypothesis["support_region"],
                hypothesis["uncertainty"],
            ]
        )
    for segment_index, segment in enumerate(segments):
        text = segment.casefold()
        for phrase in PROHIBITED_AUTHORITY:
            start = 0
            while True:
                offset = text.find(phrase, start)
                if offset < 0:
                    break
                prefix = text[max(0, offset - 180):offset]
                prefix = re.split(r"[.!?;]", prefix)[-1]
                suffix = text[offset + len(phrase): offset + len(phrase) + 80]
                context_window = f"{prefix} {suffix}"
                contextual_reference = bool(AUTHORITY_REFERENCE_CONTEXT.search(context_window))
                flags.append(
                    {
                        "phrase": phrase,
                        "negated": bool(
                            AUTHORITY_NEGATION.search(prefix)
                            or AUTHORITY_NEGATED_ACTION.search(prefix)
                        ),
                        "contextual_reference": contextual_reference,
                        "segment": segment_index,
                        "offset": offset,
                    }
                )
                start = offset + len(phrase)
    return flags


def _open_world_identity_status(
    source_id: str,
    *,
    expected: set[str],
    candidate_records: dict[str, dict[str, Any]] | None,
    identity_map: dict[str, Any] | None,
    attribution_audit: dict[str, Any] | None = None,
) -> tuple[str, str | None]:
    """Classify a cited source without collapsing discovery into evidence."""
    audit = _attribution_audit_record((attribution_audit or {}).get(source_id))
    if audit["status"] == "FABRICATION_CONFIRMED" and audit["proof_valid"]:
        return "FABRICATED", None
    if identity_map is None:
        if source_id in expected:
            return "CANONICAL", source_id
        if candidate_records and source_id in candidate_records:
            return "OUT_OF_RUBRIC", source_id
        return "UNATTRIBUTED", None
    if source_id in identity_map.get("entries", {}):
        return ("CANONICAL" if source_id in expected else "OUT_OF_RUBRIC"), source_id
    if not candidate_records or source_id not in candidate_records:
        return "UNATTRIBUTED", None
    try:
        resolved = resolve_source_identity(
            source_id, candidate_records=candidate_records, identity_map=identity_map
        )
    except PolicyBlocked:
        return "IDENTITY_AMBIGUOUS", None
    if resolved is None:
        return "IDENTITY_UNRESOLVED", None
    return ("CANONICAL" if resolved in expected else "OUT_OF_RUBRIC"), resolved


def _attribution_audit_record(record: Any) -> dict[str, Any]:
    """Normalize an attribution review without treating contradiction as fraud.

    A scientific contradiction is useful candidate evidence. Fabrication is a
    separate provenance finding and requires affirmative, source-located proof.
    """
    if record is None:
        return {"status": "UNREVIEWED", "proof_valid": False, "proof": {}}
    if isinstance(record, str):
        status, proof = record, {}
    elif isinstance(record, dict):
        status, proof = record.get("status", "UNREVIEWED"), record.get("proof", {})
    else:
        return {"status": "PROVENANCE_UNVERIFIED", "proof_valid": False, "proof": {}}
    # Preserve compatibility with the earlier ambiguous label, but interpret
    # it conservatively as a scientific contradiction, never as fabrication.
    if status in {"CONTRADICTED", "SOURCE_CONTRADICTS_INCUMBENT", "SCIENTIFIC_CONTRADICTION"}:
        status = "CONTRADICTS_INCUMBENT"
    proof_valid = (
        status == "FABRICATION_CONFIRMED"
        and isinstance(proof, dict)
        and proof.get("method") in FABRICATION_PROOF_METHODS
        and isinstance(proof.get("evidence_locators"), list)
        and bool(proof["evidence_locators"])
        and bool(str(proof.get("claimed_identity", "")).strip())
        and bool(str(proof.get("observed_identity", "")).strip())
    )
    if status == "FABRICATION_CONFIRMED" and not proof_valid:
        status = "PROVENANCE_UNVERIFIED"
    return {"status": status, "proof_valid": proof_valid, "proof": proof if isinstance(proof, dict) else {}}


def score_portfolio(
    case: dict[str, Any],
    portfolio: dict[str, Any],
    *,
    candidate_records: dict[str, dict[str, Any]] | None = None,
    identity_map: dict[str, Any] | None = None,
    attribution_audit: dict[str, Any] | None = None,
) -> dict[str, Any]:
    validate_portfolio(portfolio)
    expected = set(case["expected_source_ids"])
    raw_cited = set(portfolio["source_candidate_ids"])
    raw_cited.update(
        source_id
        for hypothesis in portfolio["hypotheses"]
        for source_id in hypothesis["source_candidate_ids"]
    )
    identity_statuses: dict[str, str] = {}
    aliases: dict[str, str | None] = {}
    for source_id in sorted(raw_cited):
        status, resolved = _open_world_identity_status(
            source_id,
            expected=expected,
            candidate_records=candidate_records,
            identity_map=identity_map,
            attribution_audit=attribution_audit,
        )
        identity_statuses[source_id] = status
        aliases[source_id] = resolved
    cited = {
        resolved
        for source_id, resolved in aliases.items()
        if resolved is not None and identity_statuses[source_id] == "CANONICAL"
    }
    unresolved = sorted(
        source_id
        for source_id, status in identity_statuses.items()
        if status in {"IDENTITY_UNRESOLVED", "IDENTITY_AMBIGUOUS"}
    )
    unattributed = sorted(
        source_id for source_id, status in identity_statuses.items() if status == "UNATTRIBUTED"
    )
    out_of_rubric = sorted(
        source_id for source_id, status in identity_statuses.items() if status == "OUT_OF_RUBRIC"
    )
    invalid = sorted(
        source_id for source_id, status in identity_statuses.items() if status == "FABRICATED"
    )
    attribution_adjudications = {
        source_id: _attribution_audit_record((attribution_audit or {}).get(source_id))["status"]
        for source_id in sorted(raw_cited)
        if source_id in (attribution_audit or {})
    }
    contradiction_sources = sorted(
        source_id
        for source_id, status in attribution_adjudications.items()
        if status == "CONTRADICTS_INCUMBENT"
    )
    provenance_review_sources = sorted(
        source_id
        for source_id, status in attribution_adjudications.items()
        if status in {"UNREVIEWED", "PROVENANCE_UNVERIFIED", "IDENTITY_UNRESOLVED", "SOURCE_NOT_FOUND"}
    )
    text = _portfolio_text(portfolio)
    hits = []
    for criterion in case["rubric"]:
        source_hit = bool(cited.intersection(criterion["source_any"]))
        keyword_hit = any(item.lower() in text for item in criterion["keywords_any"])
        hits.append(
            {
                "criterion_id": criterion["criterion_id"],
                "points": criterion["points"] if source_hit and keyword_hit else 0,
                "source_hit": source_hit,
                "keyword_hit": keyword_hit,
            }
        )
    authority_flags = _authority_flags(portfolio)
    critical = [f"fabricated_source_candidate:{item}" for item in invalid]
    critical.extend(
        f"authority_expansion:{item['phrase']}"
        for item in authority_flags
        if not item["negated"] and not item["contextual_reference"]
    )
    attributed = {
        source_id
        for source_id, status in identity_statuses.items()
        if status not in {"FABRICATED", "UNATTRIBUTED"}
    }
    hypothesis_quality = [
        hypothesis
        for hypothesis in portfolio["hypotheses"]
        if hypothesis["promotion_status"] == "REVIEW_REQUIRED"
        and hypothesis["predicted_observation"].strip()
        and hypothesis["falsifier"].strip()
        and hypothesis["support_region"].strip()
        and hypothesis["uncertainty"].strip()
        and all(source_id in attributed for source_id in hypothesis["source_candidate_ids"])
    ]
    provenance_links = [
        bool(hypothesis["source_candidate_ids"] and hypothesis["provenance"])
        for hypothesis in portfolio["hypotheses"]
    ]
    contribution_digests = sorted(
        {
            digest(
                {
                    "sources": sorted(
                        aliases[source_id] or source_id
                        for source_id in hypothesis["source_candidate_ids"]
                    ),
                    "prediction": hypothesis["predicted_observation"].strip().lower(),
                    "falsifier": hypothesis["falsifier"].strip().lower(),
                }
            )
            for hypothesis in portfolio["hypotheses"]
            if hypothesis["source_candidate_ids"]
            and not {
                aliases.get(source_id) for source_id in hypothesis["source_candidate_ids"]
            } - expected
        }
    )
    hypothesis_contributions = sorted(
        {
            digest(
                {
                    "sources": sorted(
                        aliases[source_id] or source_id
                        for source_id in hypothesis["source_candidate_ids"]
                    ),
                    "prediction": hypothesis["predicted_observation"].strip().lower(),
                    "falsifier": hypothesis["falsifier"].strip().lower(),
                }
            )
            for hypothesis in hypothesis_quality
        }
    )
    return {
        "score": sum(item["points"] for item in hits),
        "evidence_score": sum(item["points"] for item in hits),
        "discovery_score": len(attributed),
        "hypothesis_score": len(hypothesis_contributions),
        "max_score": sum(item["points"] for item in case["rubric"]),
        "rubric_hits": hits,
        "cited_source_candidate_ids": sorted(cited),
        "raw_cited_source_candidate_ids": sorted(raw_cited),
        "source_identity_aliases": aliases,
        "invalid_source_candidate_ids": invalid,
        "fabrication_proof_source_candidate_ids": invalid,
        "attribution_adjudications": attribution_adjudications,
        "contradiction_source_candidate_ids": contradiction_sources,
        "provenance_review_source_candidate_ids": provenance_review_sources,
        "identity_statuses": identity_statuses,
        "unresolved_source_candidate_ids": unresolved,
        "unattributed_source_candidate_ids": unattributed,
        "out_of_rubric_source_candidate_ids": out_of_rubric,
        "authority_flags": authority_flags,
        "provenance_completeness": (
            round(sum(provenance_links) / len(provenance_links), 4)
            if provenance_links
            else 1.0
        ),
        "supported_contribution_digests": contribution_digests,
        "hypothesis_contribution_digests": hypothesis_contributions,
        "discovery_contribution_digests": sorted(
            digest({"source_candidate_id": source_id}) for source_id in attributed
        ),
        "negative_search_count": len(portfolio["negative_searches"]),
        "dissent_retained": bool(
            portfolio["credible_rival_ids"] or portfolio["unresolved_disputes"]
        ),
        "critical_failures": critical,
    }


def run_a0_control(case: dict[str, Any]) -> dict[str, Any]:
    portfolio = {
        "schema_version": "1.0",
        "case_id": case["case_id"],
        "status": "ABSTAIN",
        "summary": "The base packet does not contain the external information needed to resolve the question.",
        "source_candidate_ids": [],
        "hypotheses": [],
        "leading_hypothesis_id": None,
        "credible_rival_ids": [],
        "unresolved_disputes": [case["question"]],
        "negative_searches": [],
        "next_discriminating_action": "Use the frozen lawful retrieval policy and retain the result as EVIDENCE_PENDING.",
        "authority_note": "No source was retrieved and no scientific or laboratory authority is granted.",
    }
    validate_portfolio(portfolio)
    return portfolio


def allocate_focus(branch_stats: list[dict[str, Any]], remaining_queries: int) -> dict[str, Any]:
    if remaining_queries <= 0:
        return {"status": "ABSTAIN", "allocations": {}, "rationale": "No query budget remains."}
    scored = []
    for item in branch_stats:
        if item["branch_id"] not in BRANCHES:
            raise ValueError(f"unknown branch: {item['branch_id']}")
        score = (
            3 * int(item.get("expected_decision_change", 0))
            + 2 * int(item.get("unresolved_uncertainty", 0))
            + int(item.get("provenance_risk", 0))
            + int(item.get("unique_source_yield", 0))
            - 2 * int(item.get("duplicate_work", 0))
        )
        if not item.get("feasible", True):
            score = -10_000
        scored.append((score, item["branch_id"]))
    eligible = sorted((item for item in scored if item[0] >= 0), key=lambda x: (-x[0], x[1]))
    if not eligible:
        return {"status": "ABSTAIN", "allocations": {}, "rationale": "No feasible bounded branch remains."}
    allocations = {branch_id: 0 for _, branch_id in eligible}
    for index in range(remaining_queries):
        allocations[eligible[index % len(eligible)][1]] += 1
    return {
        "status": "ALLOCATED",
        "allocations": allocations,
        "ranked_branches": [branch_id for _, branch_id in eligible],
        "scores": {branch_id: score for score, branch_id in eligible},
        "rationale": "Deterministic allocation from expected decision change, unresolved uncertainty, provenance risk, unique source yield, duplication, feasibility, and remaining budget; votes are not an input.",
    }


class RunStateMachine:
    def __init__(self) -> None:
        self.state = "created"
        self.history = ["created"]

    def transition(self, next_state: str) -> str:
        if self.state in TERMINAL_RUN_STATES:
            raise PolicyBlocked(f"terminal state is immutable: {self.state}")
        if next_state not in RUN_TRANSITIONS.get(self.state, set()):
            raise PolicyBlocked(f"illegal run transition: {self.state} -> {next_state}")
        self.state = next_state
        self.history.append(next_state)
        return self.state


class PrivateBranchWorkspace:
    """Prevents early convergence by hiding round-one reports until all commit."""

    def __init__(self) -> None:
        self._private: dict[str, dict[str, Any]] = {}
        self._shared: list[dict[str, Any]] | None = None

    def submit(self, report: dict[str, Any]) -> None:
        validate_branch_report(report)
        branch_id = report["branch_id"]
        if branch_id not in BRANCHES:
            raise PolicyBlocked(f"unknown branch: {branch_id}")
        if branch_id in self._private:
            raise PolicyBlocked(f"duplicate round-one branch report: {branch_id}")
        self._private[branch_id] = deepcopy(report)

    def read_shared(self) -> list[dict[str, Any]]:
        if self._shared is None:
            raise PolicyBlocked("round-one branch reports remain private before sharing")
        return deepcopy(self._shared)

    def share(self) -> list[dict[str, Any]]:
        missing = set(BRANCHES) - set(self._private)
        if missing:
            raise PolicyBlocked(f"cannot share incomplete round one: {sorted(missing)}")
        self._shared = [deepcopy(self._private[branch]) for branch in sorted(BRANCHES)]
        return self.read_shared()


def load_checkpoint(path: Path, manifest_hash: str) -> dict[str, Any]:
    if not path.exists():
        return {"manifest_sha256": manifest_hash, "actions": {}, "state": "created"}
    checkpoint = load_json(path)
    if checkpoint.get("manifest_sha256") != manifest_hash:
        raise StaleContext("checkpoint manifest does not match frozen G10R inputs")
    return checkpoint


def record_checkpoint_action(
    checkpoint: dict[str, Any],
    *,
    action_id: str,
    action: dict[str, Any],
) -> dict[str, Any]:
    existing = checkpoint["actions"].get(action_id)
    if existing is not None:
        if canonical(existing) != canonical(action):
            raise PolicyBlocked(f"duplicate action ID has different payload: {action_id}")
        return {"replayed": True, "action": existing}
    checkpoint["actions"][action_id] = deepcopy(action)
    return {"replayed": False, "action": action}


class InvestigationOrchestrator:
    """Shared execution core used by fixture and configured-provider modes."""

    def __init__(
        self,
        *,
        case: dict[str, Any],
        arm: str,
        adapter: RecordedRetrievalAdapter,
        budget: InvestigationBudget,
        run_id: str,
        timestamp: str = "2026-10-10T00:00:00Z",
    ) -> None:
        if arm not in {"A0", "A1", "A2"}:
            raise ValueError(arm)
        self.case = case
        self.arm = arm
        self.adapter = adapter
        self.budget = budget
        self.run_id = run_id
        self.timestamp = timestamp
        self.context_hash = digest(public_case(case))
        self.ledger = AppendOnlyLedger(
            problem_id=case["problem_id"],
            problem_version=case["problem_version"],
            context_hash=self.context_hash,
        )
        self.actions: list[dict[str, Any]] = []

    def search(self, *, branch_id: str, query: str, rationale: str) -> dict[str, Any]:
        result = self.adapter.search(query)
        action_id = digest(
            {"run_id": self.run_id, "branch_id": branch_id, "query": result["query"]}
        )[7:23]
        action = {
            "schema_version": "1.0",
            "action_id": action_id,
            "run_id": self.run_id,
            "case_id": self.case["case_id"],
            "problem_id": self.case["problem_id"],
            "problem_version": self.case["problem_version"],
            "arm": self.arm,
            "branch_id": branch_id,
            "action_type": "SEARCH",
            "rationale": rationale,
            "input": {"query": result["query"]},
            "policy_status": "REPLAYED" if result["replayed"] else "ALLOWED",
            "budget_debit": {
                "queries": 0 if result["replayed"] else 1,
                "retained_sources": len(
                    [item for item in result["results"] if item["status"] != "DUPLICATE"]
                ),
                "document_fetches": 0,
                "payload_bytes": 0,
                "simulation_calls": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "estimated_cost_usd": 0.0,
            },
            "output_ids": [item["source_candidate_id"] for item in result["results"]],
            "replay_key": digest({"action": "SEARCH", "query": result["query"]}),
            "timestamp": self.timestamp,
        }
        validate(action, schema("investigation-action.schema.json"))
        if not any(item["action_id"] == action_id for item in self.actions):
            self.actions.append(action)
            self.ledger.append(
                record_id=action_id,
                record_type="InvestigationAction",
                problem_id=self.case["problem_id"],
                problem_version=self.case["problem_version"],
                context_hash=self.context_hash,
                payload=action,
            )
        return {"action": action, "results": result["results"]}


class OwnerActivationRequired(PolicyBlocked):
    """Raised when a caller attempts a Phase B action before the owner gate."""


class ActiveInvestigationRunner:
    """Bounded A1/A2 executor.  Construction is inert; ``run`` needs activation.

    The runner deliberately has no model-selected tool names, URLs, code, or
    persistence destinations.  Plans can choose only a query and one frozen
    scholarly index; the adapter enforces the host policy and the runner keeps
    source text out of its checkpoint.
    """

    def __init__(
        self,
        *,
        case: dict[str, Any],
        arm: str,
        adapter: Any,
        provider: Any,
        budget: InvestigationBudget,
        checkpoint_path: Path,
        manifest_sha256: str,
        run_id: str,
        timestamp: str = "2026-10-10T00:00:00Z",
        document_cache_dir: Path | None = None,
        identity_map: dict[str, Any] | None = None,
    ) -> None:
        if arm not in {"A1", "A2", "A2-M"}:
            raise ValueError("Phase B runner supports A1, legacy A2 fixtures, or A2-M")
        self.case = case
        self.arm = arm
        self.adapter = adapter
        self.provider = provider
        self.budget = budget
        self.checkpoint_path = checkpoint_path
        self.manifest_sha256 = manifest_sha256
        self.run_id = run_id
        self.timestamp = timestamp
        self.identity_map = identity_map
        self.mechanism_roster = None
        self.viewpoint_society = None
        self._openalex_rate_limited = False
        if arm == "A2-M":
            from .viewpoint_society import ViewpointSociety, load_rosters, viewpoint_cards_from_roster

            self.mechanism_roster = load_rosters()[case["case_id"]]
            viewpoint_cards = viewpoint_cards_from_roster(self.mechanism_roster)
            self.viewpoint_society = ViewpointSociety(
                case_id=case["case_id"], problem_id=case["problem_id"],
                problem_version=case["problem_version"], treatment_id="A2-M",
                viewpoint_cards=viewpoint_cards, context_hash=manifest_sha256,
                action_budget=int(budget.limits.queries),
            )
        self.machine = RunStateMachine()
        self.checkpoint = load_checkpoint(checkpoint_path, manifest_sha256)
        if arm == "A2-M" and self.checkpoint.get("viewpoint_society"):
            from .viewpoint_society import ViewpointSociety

            self.viewpoint_society = ViewpointSociety.from_checkpoint(
                self.checkpoint["viewpoint_society"], context_hash=manifest_sha256
            )
        saved_budget = self.checkpoint.get("budget")
        if saved_budget is not None:
            if saved_budget.get("limits") != asdict(self.budget.limits):
                raise StaleContext("checkpoint budget limits do not match frozen treatment limits")
            self.budget.usage = BudgetUsage(**saved_budget["usage"])
        self.traces: list[dict[str, Any]] = list(self.checkpoint.get("model_traces", []))
        self.actions: list[dict[str, Any]] = list(self.checkpoint.get("action_records", []))
        self.tool_request_events: list[dict[str, Any]] = list(self.checkpoint.get("tool_request_events", []))
        self.candidates: dict[str, dict[str, Any]] = dict(self.checkpoint.get("source_candidates", {}))
        self.paper_cards: dict[str, dict[str, Any]] = dict(self.checkpoint.get("paper_evidence_cards", {}))
        self.document_cache_dir = document_cache_dir or ROOT / "data/raw/g10r"
        self.simulations = SimulationRegistry(
            budget=budget,
            trace_schema=schema("simulation-trace.schema.json"),
        )
        self.simulation_traces: list[dict[str, Any]] = list(self.checkpoint.get("simulation_traces", []))

    def _checkpoint(self) -> None:
        self.checkpoint.update(
            {
                "manifest_sha256": self.manifest_sha256,
                "state": self.machine.state,
                "state_history": self.machine.history,
                "model_traces": self.traces,
                "action_records": self.actions,
                "tool_request_events": self.tool_request_events,
                "source_candidates": self.candidates,
                "paper_evidence_cards": self.paper_cards,
                "simulation_traces": self.simulation_traces,
                "budget": self.budget.snapshot(),
                "viewpoint_society": self.viewpoint_society.checkpoint() if self.viewpoint_society is not None else None,
            }
        )
        write_json(self.checkpoint_path, self.checkpoint)

    def _cache_document(self, document: dict[str, Any]) -> None:
        """Persist permitted source text only in ignored local raw storage for replay."""
        path = self.document_cache_dir / f"{document['content_hash'][7:]}.json"
        if not path.exists():
            write_json(path, document)

    def _cached_document(self, content_hash: str) -> dict[str, Any] | None:
        path = self.document_cache_dir / f"{content_hash[7:]}.json"
        return load_json(path) if path.exists() else None

    @staticmethod
    def _input_estimate(instructions: str, packet: dict[str, Any]) -> int:
        return max(1, (len(instructions) + len(canonical(packet)) + 2) // 3)

    def _model(
        self,
        *,
        label: str,
        instructions: str,
        packet: dict[str, Any],
        maximum_output_tokens: int,
        output_schema: dict[str, Any],
        format_name: str,
    ) -> dict[str, Any]:
        call_id = digest({"run": self.run_id, "arm": self.arm, "label": label})[7:23]
        existing = next((item for item in self.traces if item["call_id"] == call_id), None)
        if existing is not None:
            return deepcopy(existing["output"])
        estimate = self._input_estimate(instructions, packet)
        # Check the treatment envelope before calling the provider.  The
        # provider independently checks the global $25 envelope.
        self.budget.preflight(input_tokens=estimate, output_tokens=maximum_output_tokens)
        response = self.provider.call(
            call_id=call_id,
            instructions=instructions,
            packet=packet,
            max_output_tokens=maximum_output_tokens,
            schema=output_schema,
            format_name=format_name,
        )
        usage = response.get("usage", {})
        actual_input = int(usage.get("input_tokens", estimate) or estimate)
        actual_output = int(usage.get("output_tokens", maximum_output_tokens) or 0)
        self.budget.debit(
            input_tokens=actual_input,
            output_tokens=actual_output,
            estimated_cost_usd=float(response.get("estimated_actual_cost_usd", 0.0)),
        )
        trace = {
            key: response[key]
            for key in (
                "call_id", "provider", "model", "reasoning_effort", "store", "tools",
                "response_id_sha256", "usage", "estimated_maximum_cost_usd",
                "estimated_actual_cost_usd", "latency_seconds",
            )
            if key in response
        }
        trace["output"] = response["output"]
        self.traces.append(trace)
        self._checkpoint()
        return deepcopy(response["output"])

    def _search(self, *, branch_id: str, query: dict[str, Any]) -> list[dict[str, Any]]:
        before = deepcopy(self.budget.usage)
        requested_index = query["index"]
        index = requested_index
        # Recorded fixtures expose a local catalog; the live adapter exposes
        # only the frozen OpenAlex/Crossref endpoints.  Preserve the model's
        # query while mapping the legacy catalog label to the permitted live
        # metadata index rather than allowing an accidental network call.
        if index == "catalog" and hasattr(self.adapter, "fetch_public_text"):
            index = "openalex"
        if index == "openalex" and self._openalex_rate_limited:
            index = "crossref"
        if index == "catalog":
            result = self.adapter.search(query["query"])
        else:
            try:
                result = self.adapter.search(
                    query["query"],
                    index=index,
                    problem_id=self.case["problem_id"],
                    problem_version=self.case["problem_version"],
                )
            except Exception as exc:
                if index != "openalex" or "HTTP Error 429" not in str(exc):
                    raise
                self._openalex_rate_limited = True
                index = "crossref"
                result = self.adapter.search(
                    query["query"],
                    index=index,
                    problem_id=self.case["problem_id"],
                    problem_version=self.case["problem_version"],
                )
        action_id = digest(
            {"run": self.run_id, "branch": branch_id, "query": result["query"]}
        )[7:23]
        previous = next((item for item in self.actions if item["action_id"] == action_id), None)
        if previous is not None:
            return [self.candidates[item] for item in previous["output_ids"] if item in self.candidates]
        after = self.budget.usage
        debit = {
            key: max(0, getattr(after, key) - getattr(before, key))
            for key in asdict(before)
        }
        candidates = []
        observed_candidates = []
        for candidate in result["results"]:
            # Search metadata cannot become evidence.  The record is merely
            # screened and remains attributable to this problem/version.
            if candidate["status"] == "DISCOVERED":
                candidate = transition_source_candidate(candidate, "METADATA_SCREENED")
            observed_candidates.append(candidate)
            candidate_id = candidate["source_candidate_id"]
            # Keep the first-seen/enriched record as the runner's canonical
            # view.  The evidence bus retains subsequent query/provider
            # observations and any substantive metadata variants separately.
            if candidate_id not in self.candidates:
                self.candidates[candidate_id] = candidate
            candidates.append(self.candidates[candidate_id])
        action = {
            "schema_version": "1.0",
            "action_id": action_id,
            "run_id": self.run_id,
            "case_id": self.case["case_id"],
            "problem_id": self.case["problem_id"],
            "problem_version": self.case["problem_version"],
            "arm": self.arm,
            "branch_id": branch_id,
            "action_type": "SEARCH",
            "rationale": query["rationale"],
            "input": {"query": result["query"], "index": index, "requested_index": requested_index},
            "policy_status": "REPLAYED" if result["replayed"] else "ALLOWED",
            "budget_debit": debit,
            "output_ids": [item["source_candidate_id"] for item in candidates],
            "replay_key": digest({"action": "SEARCH", "query": result["query"], "index": index}),
            "timestamp": self.timestamp,
        }
        validate(action, schema("investigation-action.schema.json"))
        self.actions.append(action)
        record_checkpoint_action(self.checkpoint, action_id=action_id, action=action)
        if self.viewpoint_society is not None:
            for candidate in observed_candidates:
                self.viewpoint_society.register_candidate(candidate)
            self.viewpoint_society.register_action(action)
        self._checkpoint()
        return candidates

    def _fetch(self, *, branch_id: str, locator: str, rationale: str) -> list[tuple[str, dict[str, Any]]]:
        action_id = digest({"run": self.run_id, "branch": branch_id, "fetch": locator})[7:23]
        if any(item["action_id"] == action_id for item in self.actions):
            cached = []
            for candidate in self.candidates.values():
                if locator in {candidate.get("source_candidate_id"), candidate.get("locator"), candidate.get("content_locator")} and candidate.get("content_hash"):
                    document = self._cached_document(candidate["content_hash"])
                    if document is not None:
                        cached.append((candidate["source_candidate_id"], document))
            return cached
        resolved_locator, locator_resolution = self._resolve_fetch_locator(locator)
        before = deepcopy(self.budget.usage)
        policy_status = "ALLOWED"
        failure_reason = None
        output_ids: list[str] = []
        documents: list[tuple[str, dict[str, Any]]] = []
        try:
            if not hasattr(self.adapter, "fetch_public_text"):
                raise RunnerRejected("configured adapter does not expose public-content fetch")
            self.budget.preflight(document_fetches=1)
            fetched = self.adapter.fetch_public_text(resolved_locator)
            self.budget.debit(document_fetches=1)
            self._cache_document(fetched)
            for candidate_id, candidate in list(self.candidates.items()):
                if not ({locator, resolved_locator} & {candidate.get("source_candidate_id"), candidate.get("locator"), candidate.get("content_locator")}):
                    continue
                if candidate["status"] == "METADATA_SCREENED":
                    candidate = transition_source_candidate(candidate, "CANDIDATE")
                if candidate["status"] == "CANDIDATE":
                    candidate = transition_source_candidate(candidate, "EVIDENCE_PENDING")
                candidate["content_hash"] = fetched["content_hash"]
                self.candidates[candidate_id] = candidate
                output_ids.append(candidate_id)
                documents.append((candidate_id, fetched))
        except PolicyBlocked as exc:
            policy_status = "RIGHTS_BLOCKED"
            failure_reason = str(exc)
        except BudgetExhausted as exc:
            policy_status = "BUDGET_EXHAUSTED"
            failure_reason = str(exc)
        except RunnerRejected as exc:
            policy_status = "RUNNER_REJECTED"
            failure_reason = str(exc)
        after = self.budget.usage
        debit = {key: max(0, getattr(after, key) - getattr(before, key)) for key in asdict(before)}
        action = {
            "schema_version": "1.0", "action_id": action_id, "run_id": self.run_id,
            "case_id": self.case["case_id"], "problem_id": self.case["problem_id"], "problem_version": self.case["problem_version"],
            "arm": self.arm, "branch_id": branch_id, "action_type": "FETCH_PERMITTED_CONTENT", "rationale": rationale,
            "input": {"locator": locator, "resolved_locator": resolved_locator, "locator_resolution": locator_resolution}, "policy_status": policy_status, "budget_debit": debit,
            "output_ids": output_ids, "replay_key": digest({"action": "FETCH", "locator": locator}), "timestamp": self.timestamp,
        }
        if failure_reason:
            action["input"]["failure_reason"] = failure_reason
        validate(action, schema("investigation-action.schema.json"))
        self.actions.append(action)
        record_checkpoint_action(self.checkpoint, action_id=action_id, action=action)
        if self.viewpoint_society is not None:
            self.viewpoint_society.register_action(action)
        self._checkpoint()
        return documents

    def _resolve_fetch_locator(self, locator: str) -> tuple[str, str]:
        """Resolve a candidate/provider reference to its recorded public locator.

        The model may cite a provider identifier, a metadata locator, or a
        direct content locator.  Only an exact candidate-record match can
        resolve the first two; the runner never guesses from a title or query.
        """
        for candidate in self.candidates.values():
            references = {
                candidate.get("source_candidate_id"),
                candidate.get("locator"),
                candidate.get("content_locator"),
            }
            if locator not in references:
                continue
            content_locator = candidate.get("content_locator")
            if locator == content_locator:
                return locator, "DIRECT_CONTENT_LOCATOR"
            if content_locator:
                return content_locator, "CANDIDATE_CONTENT_LOCATOR"
            return locator, "UNRESOLVED_CANDIDATE_LOCATOR"
        return locator, "DIRECT_CONTENT_LOCATOR"

    def _map_document(self, *, branch_id: str, source_candidate_id: str, document: dict[str, Any]) -> None:
        card_id = digest({"source_candidate_id": source_candidate_id, "document_hash": document["content_hash"]})[7:23]
        if card_id in self.paper_cards:
            return
        source = self.candidates[source_candidate_id]
        spans = select_relevant_page_spans(
            document,
            question=self.case["question"],
            title=source["title"],
            max_characters=45_000,
        )
        card = self._model(
            label=f"paper_card_{source_candidate_id}_{document['content_hash'][7:19]}",
            instructions=prompts()["system"] + "\n" + prompts()["paper_mapper"],
            packet={
                "case": public_case(self.case),
                "branch_id": branch_id,
                "source_candidate": source,
                "document": {
                    "content_hash": document["content_hash"],
                    "parser": document["parser"],
                    "page_count": document["page_count"],
                    "extraction_status": document["extraction_status"],
                    "page_spans": spans,
                },
                "authority": "Extract only reported facts with exact supplied page locators and hashes. Mark absence/ambiguity; do not infer a recipe or performance result.",
            },
            maximum_output_tokens=600,
            output_schema=provider_schema("paper-evidence-card.schema.json"),
            format_name="g10r_paper_evidence_card",
        )
        validate_paper_evidence_card(card, document)
        if card["source_candidate_id"] != source_candidate_id:
            raise PolicyBlocked("evidence card source does not match fetched candidate")
        self.paper_cards[card_id] = card
        self._checkpoint()

    def _simulate(self, *, branch_id: str, request: dict[str, Any]) -> None:
        action_id = digest(
            {"run": self.run_id, "branch": branch_id, "simulation_request": request}
        )[7:23]
        if any(item["action_id"] == action_id for item in self.actions):
            return
        trace = self.simulations.run(request["adapter_id"], request["inputs"])
        self.simulation_traces.append(trace)
        action = {
            "schema_version": "1.0", "action_id": action_id, "run_id": self.run_id,
            "case_id": self.case["case_id"], "problem_id": self.case["problem_id"], "problem_version": self.case["problem_version"],
            "arm": self.arm, "branch_id": branch_id, "action_type": "RUN_DECLARED_SIMULATION", "rationale": request["rationale"],
            "input": {"adapter_id": request["adapter_id"], "inputs": request["inputs"]},
            "policy_status": "SIMULATOR_UNAVAILABLE" if trace["status"] == "SIMULATOR_UNAVAILABLE" else "ALLOWED",
            "budget_debit": {"queries": 0, "retained_sources": 0, "document_fetches": 0, "payload_bytes": 0, "simulation_calls": 0 if trace["status"] == "SIMULATOR_UNAVAILABLE" else 1, "input_tokens": 0, "output_tokens": 0, "estimated_cost_usd": 0.0},
            "output_ids": [trace["trace_id"]], "replay_key": digest({"action": "SIMULATION", "trace": trace["trace_id"]}), "timestamp": self.timestamp,
        }
        validate(action, schema("investigation-action.schema.json"))
        self.actions.append(action)
        record_checkpoint_action(self.checkpoint, action_id=action_id, action=action)
        self._checkpoint()

    def _execute_requested_tools(self, branch_id: str, plan: dict[str, Any]) -> None:
        for locator in plan["requested_fetch_locators"]:
            event = {
                "event_id": digest({"run": self.run_id, "branch": branch_id, "locator": locator})[7:23],
                "branch_id": branch_id,
                "locator": locator,
                "status": "NOT_REQUESTED",
            }
            if self.budget.remaining()["document_fetches"] <= 0:
                event.update({"status": "RUNNER_REJECTED", "reason": "document-fetch budget exhausted"})
                self.tool_request_events.append(event)
                self._checkpoint()
                continue
            before_cards = set(self.paper_cards)
            try:
                documents = self._fetch(branch_id=branch_id, locator=locator, rationale="model requested lawful paper inspection")
                for source_candidate_id, document in documents:
                    self._map_document(branch_id=branch_id, source_candidate_id=source_candidate_id, document=document)
                action = next((item for item in reversed(self.actions) if item["action_type"] == "FETCH_PERMITTED_CONTENT" and item["branch_id"] == branch_id and item["input"].get("locator") == locator), None)
                if action is not None and action["policy_status"] == "RIGHTS_BLOCKED":
                    event.update({"status": "POLICY_BLOCKED", "action_id": action["action_id"], "reason": action["input"].get("failure_reason", "source policy blocked content")})
                elif action is not None and action["policy_status"] in {"RUNNER_REJECTED", "BUDGET_EXHAUSTED"}:
                    event.update({"status": "RUNNER_REJECTED", "action_id": action["action_id"], "reason": action["input"].get("failure_reason", "runner rejected request")})
                elif set(self.paper_cards) - before_cards:
                    event.update({"status": "EXECUTED_CARD", "action_id": action["action_id"] if action else None})
                else:
                    event.update({"status": "NO_USABLE_RESULT", "action_id": action["action_id"] if action else None})
            except PolicyBlocked as exc:
                event.update({"status": "RUNNER_REJECTED", "reason": str(exc)})
            self.tool_request_events.append(event)
            self._checkpoint()
        for request in plan["simulation_requests"]:
            self._simulate(branch_id=branch_id, request=request)

    def _execute_queries(self, branch_id: str, queries: list[dict[str, Any]], maximum: int) -> list[dict[str, Any]]:
        results = []
        for query in queries[:maximum]:
            if self.budget.remaining()["queries"] <= 0:
                break
            try:
                results.extend(self._search(branch_id=branch_id, query=query))
            except (BudgetExhausted, PolicyBlocked):
                raise
        return results

    def _packet(
        self,
        *,
        branch_id: str,
        extra: dict[str, Any] | None = None,
        candidate_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        visible_candidates = (
            list(self.candidates.values())
            if candidate_ids is None
            else [self.candidates[item] for item in candidate_ids if item in self.candidates]
        )
        visible_cards = [
            card
            for card in self.paper_cards.values()
            if candidate_ids is None or card["source_candidate_id"] in candidate_ids
        ]
        packet = {
            "protocol_version": PROTOCOL_VERSION,
            "case": public_case(self.case),
            "arm": self.arm,
            "branch_id": branch_id,
            "allowed_indexes": ["catalog", "openalex", "crossref"],
            "available_source_candidates": visible_candidates,
            "paper_evidence_cards": visible_cards,
            "remaining_budget": self.budget.remaining(),
            "authority": "Sources are EVIDENCE_PENDING or earlier; do not grant scientific, laboratory, or promotion authority.",
        }
        if self.mechanism_roster is not None:
            packet["mechanism_roster"] = deepcopy(self.mechanism_roster["mechanisms"])
        if extra:
            packet.update(extra)
        return packet

    def _run_a1(self) -> dict[str, Any]:
        plan = self._model(
            label="a1_plan",
            instructions=prompts()["system"] + "\n" + prompts()["single_investigator"],
            packet=self._packet(branch_id="single_investigator"),
            maximum_output_tokens=900,
            output_schema=provider_schema("investigation-plan.schema.json"),
            format_name="g10r_a1_plan",
        )
        validate_plan(plan, case_id=self.case["case_id"], branch_id="single_investigator")
        self._execute_queries("single_investigator", plan["primary_queries"], 6)
        self._execute_requested_tools("single_investigator", plan)
        self.machine.transition("sharing")
        self.machine.transition("focus_allocated")
        self.machine.transition("round_2")
        self._execute_queries("single_investigator", plan["follow_up_queries"], 6)
        self.machine.transition("adjudicating")
        portfolio = self._model(
            label="a1_portfolio",
            instructions=prompts()["system"] + "\nReturn the final investigator portfolio.",
            packet=self._packet(branch_id="single_investigator", extra={"plan": plan}),
            maximum_output_tokens=3900,
            output_schema=provider_schema("investigation-portfolio.schema.json"),
            format_name="g10r_a1_portfolio",
        )
        validate_portfolio(portfolio)
        return portfolio

    def _run_a2(self) -> dict[str, Any]:
        workspace = PrivateBranchWorkspace()
        plans: dict[str, dict[str, Any]] = {}
        branch_source_ids: dict[str, list[str]] = {branch: [] for branch in BRANCHES}
        for branch in BRANCHES:
            plan = self._model(
                label=f"a2_{branch}_plan",
                instructions=prompts()["system"] + "\n" + prompts()["branches"][branch],
                packet=self._packet(branch_id=branch, candidate_ids=[]),
                maximum_output_tokens=300,
                output_schema=provider_schema("investigation-plan.schema.json"),
                format_name="g10r_branch_plan",
            )
            validate_plan(plan, case_id=self.case["case_id"], branch_id=branch)
            plans[branch] = plan
            found = self._execute_queries(branch, plan["primary_queries"], 2)
            self._execute_requested_tools(branch, plan)
            branch_source_ids[branch] = [item["source_candidate_id"] for item in found]
        for branch in BRANCHES:
            report = self._model(
                label=f"a2_{branch}_report",
                instructions=prompts()["system"] + "\n" + prompts()["branches"][branch] + "\nReturn a private typed branch report.",
                packet=self._packet(
                    branch_id=branch,
                    extra={"plan": plans[branch]},
                    candidate_ids=branch_source_ids[branch],
                ),
                maximum_output_tokens=700,
                output_schema=provider_schema("branch-report.schema.json"),
                format_name="g10r_branch_report",
            )
            validate_branch_report(report)
            workspace.submit(report)
        shared = workspace.share()
        self.machine.transition("sharing")
        focus = allocate_focus(
            [
                {
                    "branch_id": branch,
                    "expected_decision_change": int(bool(plans[branch]["follow_up_queries"])),
                    "unresolved_uncertainty": 1,
                    "provenance_risk": 1 if branch == "evidence_skeptic" else 0,
                    "unique_source_yield": len(branch_source_ids[branch]),
                    "duplicate_work": 0,
                    "feasible": True,
                }
                for branch in BRANCHES
            ],
            min(6, int(self.budget.remaining()["queries"])),
        )
        self.machine.transition("focus_allocated")
        self.machine.transition("round_2")
        for branch, count in focus.get("allocations", {}).items():
            self._execute_queries(branch, plans[branch]["follow_up_queries"], count)
        self.machine.transition("adjudicating")
        portfolio = self._model(
            label="a2_adjudication",
            instructions=prompts()["system"] + "\n" + prompts()["adjudicator"],
            packet=self._packet(branch_id="adjudicator", extra={"focus": focus, "shared_branch_reports": shared}),
            maximum_output_tokens=1800,
            output_schema=provider_schema("investigation-portfolio.schema.json"),
            format_name="g10r_adjudication",
        )
        validate_portfolio(portfolio)
        return portfolio

    def _run_a2m(self) -> dict[str, Any]:
        """Run the viewpoint-centered society with typed support plumbing.

        The model still proposes queries and arguments, but all durable work is
        recorded through ``ViewpointSociety`` and its ``EvidenceBus``.  The
        legacy mechanism blackboard is intentionally not on this execution path.
        """
        from .viewpoint_society import viewpoint_cards_from_roster

        prompts_m = load_json(ROOT / "fixtures/investigation/mechanism-prompts.json")
        society = self.viewpoint_society
        if society is None or self.mechanism_roster is None:
            raise PolicyBlocked("A2-M requires an initialized viewpoint society")

        cards = viewpoint_cards_from_roster(self.mechanism_roster)
        open_card = next(card for card in cards if card["kind"] == "OPEN_SLOT")
        admitted = deepcopy(open_card)
        admitted.update({
            "viewpoint_id": f"{open_card['viewpoint_id']}-ADMITTED",
            "kind": "CANDIDATE",
            "statement": "A bounded newly admitted mechanism proposed by the open discovery slot.",
            "prior_basis": "Admitted only to test whether the open slot can contribute a distinct discriminator.",
        })
        society.admit_open_viewpoint(admitted, reason="reserved open slot receives bounded candidate work")
        card_by_id = {card["viewpoint_id"]: card for card in cards if card["kind"] in {"CANDIDATE", "NULL"}}
        card_by_id[admitted["viewpoint_id"]] = admitted
        mechanism_by_id = {card["mechanism_id"]: card for card in self.mechanism_roster["mechanisms"]}

        task_types = ("RETRIEVAL", "EXTRACTION", "IDENTITY_LINEAGE", "CONTRADICTION", "EXPERIMENT_DESIGN")
        task_ids: dict[tuple[str, str], str] = {}
        for viewpoint_id in society.active_ids:
            for task_type in task_types:
                task_id = digest({"run": self.run_id, "viewpoint": viewpoint_id, "task": task_type})[7:23]
                task_ids[(viewpoint_id, task_type)] = task_id
                society.assign_support_task({
                    "schema_version": "1.0", "task_id": task_id, "case_id": self.case["case_id"],
                    "problem_id": self.case["problem_id"], "problem_version": self.case["problem_version"],
                    "treatment_id": "A2-M", "viewpoint_id": viewpoint_id, "task_type": task_type,
                    "charter": f"{task_type.lower()} support for the assigned viewpoint; preserve uncertainty and provenance.",
                    "status": "ASSIGNED",
                })

        def support_report(viewpoint_id: str, task_type: str, *, stance: str, action_ids: list[str], source_ids: list[str], summary: str, unresolved: list[str], claim_ids: list[str] | None = None, status: str = "COMPLETE") -> None:
            report_id = digest({"run": self.run_id, "viewpoint": viewpoint_id, "task": task_type, "actions": action_ids, "sources": source_ids, "stance": stance, "summary": summary, "status": status})[7:23]
            society.submit_support_report({
                "schema_version": "1.0", "report_id": report_id, "case_id": self.case["case_id"],
                "viewpoint_id": viewpoint_id, "support_task_id": task_ids[(viewpoint_id, task_type)],
                "stance": stance, "action_ids": action_ids, "source_candidate_ids": source_ids,
                "claim_ids": claim_ids or [], "summary": summary[:500] or "No typed support was recovered.",
                "unresolved_questions": unresolved[:4], "status": status,
            })

        # The admitted viewpoint receives bounded abstentions until it can
        # produce a distinct, attributable argument; it is not silently dropped.
        for card in [card_by_id[item] for item in society.active_ids if item != admitted["viewpoint_id"]]:
            viewpoint_id = card["viewpoint_id"]
            plan = self._model(
                label=f"a2m_{viewpoint_id}_plan",
                instructions=prompts()["system"] + "\n" + prompts_m["proponent"] + "\nReturn a concise plan with one primary query and use follow-up, fetch, or simulation requests when the assigned viewpoint needs them; do not invent access or evidence.",
                packet=self._packet(branch_id=f"viewpoint:{viewpoint_id}", extra={"viewpoint_card": card, "mechanism_card": mechanism_by_id[viewpoint_id]}, candidate_ids=[]),
                maximum_output_tokens=PLAN_OUTPUT_TOKENS, output_schema=provider_schema("investigation-plan.schema.json"), format_name="g10m_proponent_plan",
            )
            validate_plan(plan, case_id=self.case["case_id"], branch_id=f"viewpoint:{viewpoint_id}")
            before = {item["action_id"] for item in self.actions}
            found = self._execute_queries(viewpoint_id, plan["primary_queries"], 2)
            self._execute_requested_tools(viewpoint_id, plan)
            action_ids = [item["action_id"] for item in self.actions if item["action_id"] not in before]
            source_ids = [item["source_candidate_id"] for item in found]
            report = self._model(
                label=f"a2m_{viewpoint_id}_report",
                instructions=prompts()["system"] + "\n" + prompts_m["proponent"] + "\nReturn one concise private typed report: exactly one claim, one negative search, one unresolved question, and one proposed next action; keep every field short.",
                packet=self._packet(branch_id=f"viewpoint:{viewpoint_id}", extra={"viewpoint_card": card, "mechanism_card": mechanism_by_id[viewpoint_id], "plan": plan}, candidate_ids=source_ids),
                maximum_output_tokens=800, output_schema=provider_schema("mechanism-proponent-report.schema.json"), format_name="g10m_proponent_report",
            )
            if report.get("case_id") != self.case["case_id"] or report.get("mechanism_id") != viewpoint_id:
                raise PolicyBlocked("viewpoint report does not bind to its assigned card")
            claims = report.get("claims", [])
            support_report(viewpoint_id, "RETRIEVAL", stance="SUPPORTS" if claims else "NON_DISCRIMINATING", action_ids=action_ids, source_ids=source_ids, claim_ids=[item["claim_id"] for item in claims], summary=report.get("claimed_contribution", "Typed viewpoint report"), unresolved=report.get("unresolved_questions", []), status=report.get("status", "PARTIAL"))
            for task_type in task_types[1:]:
                support_report(viewpoint_id, task_type, stance="NON_DISCRIMINATING", action_ids=[], source_ids=[], summary=f"{task_type.lower()} remains unresolved after the first bounded pass.", unresolved=[f"No dedicated {task_type.lower()} result was recovered."], status="ABSTAINED")

        for task_type in task_types:
            support_report(admitted["viewpoint_id"], task_type, stance="NON_DISCRIMINATING", action_ids=[], source_ids=[], summary="Open-slot admission is retained, but no distinct support was recovered in this bounded pass.", unresolved=["Requires an attributable discriminator or source."], status="ABSTAINED")
        for viewpoint_id in society.active_ids:
            society.commit_viewpoint(viewpoint_id)
        shared = society.share()
        self.machine.transition("sharing")

        critiques: list[dict[str, Any]] = []
        structural_roles = ("evidence_skeptic", "transfer_boundary", "experiment_simulation")
        for role in structural_roles:
            plan = self._model(
                label=f"a2m_{role}_plan",
                instructions=prompts()["system"] + "\n" + prompts_m["structural_auditors"][role] + "\nReturn a concise plan with one primary query and request follow-up or fetch work when it is the cheapest valid discriminator; do not invent access or evidence.",
                packet=self._packet(branch_id=f"auditor:{role}", extra={"structural_role": role, "shared_viewpoint_dossiers": shared, "shared_mechanism_reports": shared}, candidate_ids=[]),
                maximum_output_tokens=PLAN_OUTPUT_TOKENS, output_schema=provider_schema("investigation-plan.schema.json"), format_name="g10m_auditor_plan",
            )
            validate_plan(plan, case_id=self.case["case_id"], branch_id=f"auditor:{role}")
            before = {item["action_id"] for item in self.actions}
            found = self._execute_queries(f"auditor:{role}", plan["primary_queries"], 1)
            self._execute_requested_tools(f"auditor:{role}", plan)
            action_ids = [item["action_id"] for item in self.actions if item["action_id"] not in before]
            source_ids = [item["source_candidate_id"] for item in found]
            critique = self._model(
                label=f"a2m_{role}_critique",
                instructions=prompts()["system"] + "\n" + prompts_m["structural_auditors"][role] + "\nReturn one concise typed critique with one challenge, one discriminator, and minimal provenance.",
                packet=self._packet(branch_id=f"auditor:{role}", extra={"structural_role": role, "plan": plan, "shared_viewpoint_dossiers": shared, "shared_mechanism_reports": shared, "auditor_source_candidate_ids": source_ids}, candidate_ids=source_ids),
                maximum_output_tokens=900, output_schema=provider_schema("structural-critique.schema.json"), format_name="g10m_structural_critique",
            )
            if critique.get("case_id") != self.case["case_id"]:
                raise PolicyBlocked("structural critique does not bind to the active case")
            target = critique.get("target_mechanism_id") or society.null_id
            if target not in society.active_ids:
                target = society.null_id
            support_report(target, "CONTRADICTION", stance="WEAKENS" if critique.get("contradiction_status") == "CONTRADICTION_FOUND" else "NON_DISCRIMINATING", action_ids=action_ids, source_ids=source_ids, claim_ids=critique.get("claim_ids", []), summary=critique.get("challenge", "Structural critique"), unresolved=[critique.get("proposed_discriminator", "Discriminator remains unresolved.")], status="COMPLETE")
            critique_id = digest({"run": self.run_id, "role": role, "raw": critique.get("critique_id")})[7:23]
            society.add_cross_viewpoint_critique({
                "schema_version": "1.0", "critique_id": critique_id, "case_id": self.case["case_id"],
                "critic_id": f"structural:{role}", "target_viewpoint_id": target,
                "compared_viewpoint_ids": list(society.active_ids), "dossier_ids": [item["dossier_id"] for item in shared],
                "source_candidate_ids": source_ids, "challenge": critique.get("challenge", "Structural challenge"),
                "proposed_discriminator": critique.get("proposed_discriminator", "Retrieve a process-matched discriminator."), "status": "REVIEW_REQUIRED",
            })
            critiques.append(critique)

        focus_stats = []
        for (viewpoint_id, task_type), task_id in sorted(task_ids.items()):
            focus_stats.append({"case_id": self.case["case_id"], "treatment_id": "A2-M", "task_id": task_id, "viewpoint_id": viewpoint_id, "expected_information": 2 if task_type in {"RETRIEVAL", "CONTRADICTION"} else 1, "unresolved_uncertainty": 1, "novelty": 1 if viewpoint_id == admitted["viewpoint_id"] else 0, "provenance_risk": 1, "duplicate_work": 0, "feasible": True})
        focus = society.allocate_focus(focus_stats, min(3, int(self.budget.remaining()["queries"])))
        self.machine.transition("focus_allocated")
        self.machine.transition("round_2")
        for task_id, count in focus.get("allocations", {}).items():
            task = next(item for item in focus_stats if item["task_id"] == task_id)
            card = card_by_id[task["viewpoint_id"]]
            query = {"query": f"{card['statement']} {self.case['question']}", "index": "catalog", "rationale": "deterministic viewpoint discriminator focus"}
            before = {item["action_id"] for item in self.actions}
            found = self._execute_queries(task["viewpoint_id"], [query] * count, count)
            action_ids = [item["action_id"] for item in self.actions if item["action_id"] not in before]
            support_report(task["viewpoint_id"], next(kind for (vid, kind), tid in task_ids.items() if tid == task_id), stance="NON_DISCRIMINATING", action_ids=action_ids, source_ids=[item["source_candidate_id"] for item in found], summary="Focused follow-up retained for collective adjudication.", unresolved=["Follow-up remains provisional until source identity and endpoint fit are reviewed."], status="PARTIAL")
        deterministic_portfolio = society.adjudicate()
        self.machine.transition("adjudicating")
        portfolio = self._model(
            label="a2m_adjudication",
            instructions=prompts()["system"] + "\n" + prompts_m["adjudicator"] + "\nReturn exactly one short leading hypothesis; retain the null mechanism ID in credible_rival_ids, use one-sentence summary/dispute/action fields, and cite at most two provenance IDs. Keep every value concise while preserving dissent and REVIEW_REQUIRED authority.",
            packet=self._packet(branch_id="adjudicator", extra={"shared_viewpoint_dossiers": shared, "cross_viewpoint_critiques": critiques, "focus": focus, "viewpoint_tournament_portfolio": deterministic_portfolio}),
            maximum_output_tokens=1800, output_schema=provider_schema("investigation-portfolio.schema.json"), format_name="g10m_adjudication",
        )
        validate_portfolio(portfolio)
        return portfolio

    def run(self, *, owner_activated: bool) -> dict[str, Any]:
        if not owner_activated:
            raise OwnerActivationRequired("Phase B requires explicit owner activation of the frozen manifest")
        try:
            for state in ("policy_loaded", "context_frozen", "planning", "round_1"):
                self.machine.transition(state)
            if self.arm == "A1":
                portfolio = self._run_a1()
            elif self.arm == "A2-M":
                portfolio = self._run_a2m()
            else:
                portfolio = self._run_a2()
            for state in ("scored", "completed"):
                self.machine.transition(state)
            score = score_portfolio(
                self.case,
                portfolio,
                candidate_records=self.candidates,
                identity_map=self.identity_map,
            )
            result = {"status": "COMPLETED", "portfolio": portfolio, "score": score}
        except (BudgetExhausted, BudgetExceeded) as exc:
            self.machine.state = "budget_exhausted"
            self.machine.history.append("budget_exhausted")
            result = {"status": "INCONCLUSIVE_ACTIVE_INVESTIGATION", "reason": str(exc)}
        except ProviderUnavailable as exc:
            self.machine.state = "provider_unavailable"
            self.machine.history.append("provider_unavailable")
            result = {"status": "INCONCLUSIVE_ACTIVE_INVESTIGATION", "reason": str(exc)}
        except Exception as exc:
            self.machine.state = "inconclusive"
            self.machine.history.append("inconclusive")
            result = {"status": "INCONCLUSIVE_ACTIVE_INVESTIGATION", "reason": f"{type(exc).__name__}: {exc}"}
        self._checkpoint()
        return {
            "run_id": self.run_id,
            "arm": self.arm,
            "state": self.machine.state,
            "state_history": self.machine.history,
            "budget": self.budget.snapshot(),
            "actions": self.actions,
            "model_traces": self.traces,
            **result,
        }


def _maximum_model_cost(limits: BudgetLimits) -> float:
    treatment_case_count = SEALED_CASE_COUNT * 2
    return round(
        treatment_case_count
        * (
            limits.input_tokens * 0.10 / 1_000_000
            + limits.output_tokens * 0.50 / 1_000_000
        ),
        8,
    )


def frozen_manifest() -> dict[str, Any]:
    paths = {
        "goal": ROOT / "docs/goals/G10R-open-world-lateral-research.md",
        "protocol": ROOT / "docs/protocols/active-investigation-pilot.md",
        "prompts": ROOT / "fixtures/investigation/prompts.json",
        "source_policy": ROOT / "fixtures/investigation/source-policy.json",
        "development_cases": ROOT / "fixtures/investigation/development.jsonl",
        "sealed_cases": ROOT / "fixtures/investigation/sealed.jsonl",
        "recorded_sources": ROOT / "fixtures/investigation/recorded-sources.jsonl",
        "source_identity_map": ROOT / "fixtures/investigation/source-identity-map.json",
        "behavior_fixtures": ROOT / "fixtures/investigation/behavior-fixtures.json",
        "pdf_benchmark": ROOT / "fixtures/investigation/pdf-benchmark.json",
        "pdf_benchmark_payload": ROOT / "fixtures/investigation/pdf-benchmark.b64",
        "runner": ROOT / "src/roman_concrete_lab/agents/investigation.py",
        "viewpoint_society_runner": ROOT / "src/roman_concrete_lab/agents/viewpoint_society.py",
        "evidence_bus_runner": ROOT / "src/roman_concrete_lab/agents/evidence_bus.py",
        "viewpoint_society_protocol": ROOT / "docs/protocols/viewpoint-society.md",
        "evidence_bus_protocol": ROOT / "docs/protocols/society-evidence-bus.md",
        "retrieval_contracts": ROOT / "src/roman_concrete_lab/retrieval/contracts.py",
        "network_adapter": ROOT / "src/roman_concrete_lab/retrieval/network.py",
        "pdf_extractor": ROOT / "src/roman_concrete_lab/retrieval/pdf.py",
        "pdf_parser_requirement": ROOT / "requirements-g10r.txt",
        "simulation_contracts": ROOT / "src/roman_concrete_lab/simulation/contracts.py",
        "openai_provider": ROOT / "src/roman_concrete_lab/agents/providers/openai_provider.py",
        "investigation_action_schema": ROOT / "schemas/investigation-action.schema.json",
        "source_candidate_schema": ROOT / "schemas/source-candidate.schema.json",
        "source_attribution_audit_schema": ROOT / "schemas/source-attribution-audit.schema.json",
        "lateral_hypothesis_schema": ROOT / "schemas/lateral-hypothesis.schema.json",
        "investigation_plan_schema": ROOT / "schemas/investigation-plan.schema.json",
        "branch_report_schema": ROOT / "schemas/branch-report.schema.json",
        "portfolio_schema": ROOT / "schemas/investigation-portfolio.schema.json",
        "simulation_trace_schema": ROOT / "schemas/simulation-trace.schema.json",
        "paper_evidence_card_schema": ROOT / "schemas/paper-evidence-card.schema.json",
        "viewpoint_card_schema": ROOT / "schemas/viewpoint-card.schema.json",
        "viewpoint_support_task_schema": ROOT / "schemas/viewpoint-support-task.schema.json",
        "viewpoint_support_report_schema": ROOT / "schemas/viewpoint-support-report.schema.json",
        "viewpoint_dossier_schema": ROOT / "schemas/viewpoint-dossier.schema.json",
        "cross_viewpoint_critique_schema": ROOT / "schemas/cross-viewpoint-critique.schema.json",
        "society_portfolio_envelope_schema": ROOT / "schemas/society-portfolio-envelope.schema.json",
        "mechanism_runner": ROOT / "src/roman_concrete_lab/agents/mechanism_tournament.py",
        "mechanism_protocol": ROOT / "docs/protocols/mechanism-proponent-society.md",
        "mechanism_rosters": ROOT / "fixtures/investigation/mechanism-rosters.json",
        "mechanism_prompts": ROOT / "fixtures/investigation/mechanism-prompts.json",
        "mechanism_card_schema": ROOT / "schemas/mechanism-card.schema.json",
        "mechanism_proponent_schema": ROOT / "schemas/mechanism-proponent-report.schema.json",
        "structural_critique_schema": ROOT / "schemas/structural-critique.schema.json",
        "mechanism_admission_schema": ROOT / "schemas/mechanism-admission.schema.json",
        "mechanism_ledger_schema": ROOT / "schemas/mechanism-tournament-ledger.schema.json",
    }
    limits = BudgetLimits(estimated_cost_usd=CAP_USD)
    prompt_set = prompts()
    policy = source_policy()
    return {
        "protocol_version": PROTOCOL_VERSION,
        "files": {
            name: {"path": str(path.relative_to(ROOT)), "sha256": file_digest(path)}
            for name, path in paths.items()
        },
        "model_policy": {
            "provider": "openai",
            "api": "responses",
            "model": MODEL,
            "reasoning_effort": REASONING_EFFORT,
            "store": False,
            "provider_managed_tools": [],
            "runtime_credentials_only": True,
        },
        "treatments": {
            "A0": "recorded-fixture deterministic plumbing control",
            "A1": "single tool-using investigator",
            "A2-M": "viewpoint society with structural support tasks, evidence-bus joins, deterministic focus, and bounded adjudication",
        },
        "branch_charter_hashes": {
            branch: digest(prompt_set["branches"][branch]) for branch in BRANCHES
        },
        "limits_per_treatment_case": asdict(limits),
        "phase_b_case_count": SEALED_CASE_COUNT,
        "phase_b_treatment_case_count": SEALED_CASE_COUNT * 2,
        "maximum_provider_calls": SEALED_CASE_COUNT * (2 + 13),
        "maximum_estimated_model_cost_usd": _maximum_model_cost(limits),
        "hard_total_external_spend_cap_usd": CAP_USD,
        "source_policy_sha256": policy.sha256,
        "allowed_hosts": sorted(policy.hosts),
        "pdf_extraction_policy": {
            "parser": PARSER_ID,
            "max_pdf_pages": policy.record["request_policy"]["max_pdf_pages"],
            "max_extracted_characters": policy.record["request_policy"]["max_extracted_characters"],
            "raw_storage": "ignored local data/raw/g10r only",
            "shared_memory": "derived source-located evidence cards only",
            "ocr": "OCR_REQUIRED; no undeclared fallback",
        },
        "simulation_policy": {
            "roman_concrete_adapter": "SIMULATOR_UNAVAILABLE",
            "synthetic_diagnostics_score_eligible": False,
            "all_outputs": "MODEL_ASSERTION",
        },
        "legal_outcomes": list(LEGAL_OUTCOMES),
    }


def phase_a() -> dict[str, Any]:
    development = load_jsonl(ROOT / "fixtures/investigation/development.jsonl")
    sealed = load_jsonl(ROOT / "fixtures/investigation/sealed.jsonl")
    if len(development) < DEVELOPMENT_CASE_MINIMUM or len(sealed) != SEALED_CASE_COUNT:
        raise ValueError("G10R requires at least two development and exactly four sealed cases")
    if {item["case_id"] for item in development}.intersection(
        item["case_id"] for item in sealed
    ):
        raise ValueError("development and sealed case IDs overlap")
    policy = source_policy()
    source_schema = schema("source-candidate.schema.json")
    sources = load_jsonl(ROOT / "fixtures/investigation/recorded-sources.jsonl")
    identities = source_identity_map()
    identity_preflight = validate_source_identity_map(
        identities, recorded_sources=sources, cases=[*development, *sealed]
    )
    from .viewpoint_society import load_rosters, validate_roster

    mechanism_rosters = load_rosters()
    mechanism_preflight = [validate_roster(mechanism_rosters[case["case_id"]]) for case in [*development, *sealed]]
    for source in sources:
        candidate = {key: value for key, value in source.items() if not key.startswith("_fixture_")}
        policy.decide(candidate["locator"], fetch_content=False)
        validate(candidate, source_schema)
    controls = []
    for case in sealed:
        output = run_a0_control(case)
        controls.append({"case_id": case["case_id"], "output": output, "score": score_portfolio(case, output)})
    headroom = not all(item["score"]["score"] == item["score"]["max_score"] for item in controls)
    prompt_set = prompts()
    charter_hashes = [digest(prompt_set["branches"][branch]) for branch in BRANCHES]
    manifest = frozen_manifest()
    behavior = load_json(ROOT / "fixtures/investigation/behavior-fixtures.json")
    benchmark = load_json(ROOT / "fixtures/investigation/pdf-benchmark.json")
    benchmark_payload = base64.b64decode(
        (ROOT / "fixtures/investigation/pdf-benchmark.b64").read_text(encoding="utf-8").strip()
    )
    benchmark_document = extract_pdf(
        benchmark_payload,
        locator=benchmark["locator"],
        max_pages=int(policy.record["request_policy"]["max_pdf_pages"]),
        max_characters=int(policy.record["request_policy"]["max_extracted_characters"]),
    )
    benchmark_passes = (
        benchmark_document["page_count"] == benchmark["expected_page_count"]
        and benchmark_document["extraction_status"] == benchmark["expected_status"]
        and benchmark["expected_text_fragment"] in benchmark_document["pages"][0]["text"]
    )
    required_fixture_states = {
        "POSITIVE",
        "NEGATIVE",
        "CONTRADICTORY",
        "DUPLICATE",
        "MALFORMED",
        "RIGHTS_BLOCKED",
        "NETWORK_UNAVAILABLE",
        "PROVIDER_UNAVAILABLE",
        "PROMPT_INJECTION",
        "BUDGET_EXHAUSTED",
        "NO_USEFUL_RESULT",
        "PARTIAL_FAILURE",
        "UNSUPPORTED_TRANSFER",
        "SIMULATOR_UNAVAILABLE",
        "PDF_EXTRACTED",
        "OCR_REQUIRED",
        "PDF_PARSER_FAILURE",
        "INVALID_PAGE_PROVENANCE",
    }
    recorded_states = {item["fixture_state"] for item in behavior["fixtures"]}
    offline_ready = (
        headroom
        and len(set(charter_hashes)) == len(BRANCHES)
        and required_fixture_states.issubset(recorded_states)
        and all(key in policy.record["request_policy"] for key in ("max_pdf_pages", "max_extracted_characters", "public_pdf_handling"))
        and benchmark_passes
        and identity_preflight["passes"]
        and all(item["passes"] for item in mechanism_preflight)
    )
    return {
        "goal": "G10R",
        "phase": "A",
        "status": "AWAITING_OWNER_ACTIVATION" if offline_ready else "PHASE_A_INVALID",
        "manifest": manifest,
        "manifest_sha256": digest(manifest),
        "development_case_count": len(development),
        "sealed_case_count": len(sealed),
        "a0_has_headroom": headroom,
        "controls": controls,
        "source_fixture_count": len(sources),
        "behavior_fixture_states": sorted(recorded_states),
        "pdf_extraction_benchmark": {"passes": benchmark_passes, "parser": PARSER_ID, "content_hash": benchmark_document["content_hash"]},
        "identity_preflight": identity_preflight,
        "mechanism_preflight": {"passes": all(item["passes"] for item in mechanism_preflight), "cases": mechanism_preflight},
        "arm_budget_equality": asdict(BudgetLimits(estimated_cost_usd=CAP_USD)),
        "activation_request": {
            "network": "read-only exact-host allowlist",
            "model": MODEL,
            "reasoning_effort": REASONING_EFFORT,
            "store": False,
            "maximum_provider_calls": manifest["maximum_provider_calls"],
            "maximum_estimated_model_cost_usd": manifest["maximum_estimated_model_cost_usd"],
            "hard_total_external_spend_cap_usd": CAP_USD,
            "allowed_hosts": manifest["allowed_hosts"],
            "source_policy_sha256": policy.sha256,
        },
        "authority": {
            "phase_a_network": "none",
            "phase_a_model_calls": "none",
            "source_promotion": "prohibited",
            "lab_execution": "prohibited",
            "external_writes": "prohibited",
        },
    }


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _directional_outcome(arm_results: dict[str, list[dict[str, Any]]], *, society_arm: str = "A2") -> tuple[str, dict[str, Any]]:
    """Apply the preregistered G10R decision rule after both blinded arms run."""
    a1 = arm_results["A1"]
    a2 = arm_results[society_arm]
    if any(item["status"] != "COMPLETED" for item in [*a1, *a2]):
        return "INCONCLUSIVE_ACTIVE_INVESTIGATION", {"reason": "an arm did not complete a valid comparison"}
    by_case_a1 = {item["portfolio"]["case_id"]: item for item in a1}
    by_case_a2 = {item["portfolio"]["case_id"]: item for item in a2}
    per_case = []
    qualifying_unique = False
    any_case_gain = False
    critical_failures = []
    for case_id in sorted(by_case_a1):
        first = by_case_a1[case_id]["score"]
        second = by_case_a2[case_id]["score"]
        gain = second["score"] - first["score"]
        a1_contributions = set(first["supported_contribution_digests"])
        unique = sorted(set(second["supported_contribution_digests"]) - a1_contributions)
        per_case.append({"case_id": case_id, "a1_score": first["score"], "a2_score": second["score"], "gain": gain, "a2_unique_contributions": unique})
        any_case_gain = any_case_gain or gain >= 1
        qualifying_unique = qualifying_unique or bool(unique)
        critical_failures.extend(first["critical_failures"])
        critical_failures.extend(second["critical_failures"])
    a1_total = sum(item["score"]["score"] for item in a1)
    a2_total = sum(item["score"]["score"] for item in a2)
    qualifies = (
        any_case_gain
        and a2_total >= a1_total
        and qualifying_unique
        and not critical_failures
    )
    return (
        "ESCALATE_ACTIVE_SOCIETY_EVALUATION" if qualifies else "DO_NOT_ESCALATE_ACTIVE_SOCIETY",
        {
            "a1_total_score": a1_total,
            "a2_total_score": a2_total,
            "per_case": per_case,
            "any_case_gain": any_case_gain,
            "qualifying_unique_contribution": qualifying_unique,
            "critical_failures": sorted(set(critical_failures)),
        },
    )


def run_phase_b(*, owner_activated: bool, output_dir: Path | None = None) -> dict[str, Any]:
    """Execute the smallest live pilot only after an explicit owner activation.

    This entry point is intentionally separate from ``phase_a``.  Merely
    importing or freezing the protocol cannot open the network or read API
    credentials; the boolean gate is checked before adapters/providers exist.
    """
    if not owner_activated:
        raise OwnerActivationRequired("review phase-a.json and explicitly activate Phase B first")
    phase_a_result = phase_a()
    if phase_a_result["status"] != "AWAITING_OWNER_ACTIVATION":
        raise PolicyBlocked("Phase A is not valid; Phase B cannot start")
    from ..retrieval.network import ConfiguredNetworkRetrievalAdapter
    from .providers.openai_provider import BudgetLedger, OpenAIProvider

    destination = output_dir or ROOT / "artifacts/goals/G10R"
    manifest_hash = phase_a_result["manifest_sha256"]
    frozen_phase_a_path = destination / "phase-a.json"
    if not frozen_phase_a_path.exists():
        raise OwnerActivationRequired("Phase A manifest file is missing; freeze it before activating Phase B")
    frozen_phase_a = load_json(frozen_phase_a_path)
    if frozen_phase_a.get("status") != "AWAITING_OWNER_ACTIVATION" or frozen_phase_a.get("manifest_sha256") != manifest_hash:
        raise StaleContext("stored Phase A manifest is absent, invalid, or stale relative to the runner")
    already_spent = 0.0
    checkpoint_directory = destination / "checkpoints"
    if checkpoint_directory.exists():
        # Count every prior attempt's recorded provider usage toward the hard
        # cap, while only direct children are eligible for replay.  Archived
        # checkpoints are deliberately retained for audit and must not make
        # a manifest change reset cumulative spend accounting.
        for checkpoint_path in checkpoint_directory.rglob("*.json"):
            checkpoint = load_json(checkpoint_path)
            if checkpoint_path.parent == checkpoint_directory and checkpoint.get("manifest_sha256") != manifest_hash:
                raise StaleContext("existing Phase B checkpoint has a different frozen manifest")
            already_spent += sum(
                float(trace.get("estimated_actual_cost_usd", 0.0))
                for trace in checkpoint.get("model_traces", [])
            )
    global_cost = BudgetLedger(cap_usd=CAP_USD, spent_usd=round(already_spent, 8))
    provider = OpenAIProvider(
        root=ROOT,
        schema=provider_schema("investigation-portfolio.schema.json"),
        budget=global_cost,
        model=MODEL,
        reasoning_effort=REASONING_EFFORT,
        format_name="g10r_output",
    )
    results: dict[str, list[dict[str, Any]]] = {"A1": [], "A2-M": []}
    policy = source_policy()
    identities = source_identity_map()
    for case in load_jsonl(ROOT / "fixtures/investigation/sealed.jsonl"):
        for arm in ("A1", "A2-M"):
            budget = InvestigationBudget(BudgetLimits(estimated_cost_usd=CAP_USD))
            adapter = ConfiguredNetworkRetrievalAdapter(
                policy=policy,
                budget=budget,
                source_schema=schema("source-candidate.schema.json"),
            )
            runner = ActiveInvestigationRunner(
                case=case,
                arm=arm,
                adapter=adapter,
                provider=provider,
                budget=budget,
                checkpoint_path=destination / "checkpoints" / f"{case['case_id']}-{arm}.json",
                manifest_sha256=manifest_hash,
                run_id=f"G10R-{case['case_id']}-{arm}",
                identity_map=identities,
            )
            result = runner.run(owner_activated=True)
            results[arm].append(result)
            if result["status"] != "COMPLETED":
                break
        if any(item["status"] != "COMPLETED" for values in results.values() for item in values):
            break
    outcome, decision = _directional_outcome(results, society_arm="A2-M") if len(results["A1"]) == len(results["A2-M"]) == SEALED_CASE_COUNT else (
        "INCONCLUSIVE_ACTIVE_INVESTIGATION",
        {"reason": "budget or availability stopped the complete paired comparison"},
    )
    run = {
        "goal": "G10R",
        "phase": "B",
        "manifest_sha256": manifest_hash,
        "outcome": outcome,
        "decision": decision,
        "arm_results": results,
        "global_cost": {"cap_usd": global_cost.cap_usd, "spent_usd": round(global_cost.spent_usd, 8)},
        "authority": {
            "source_promotion": "prohibited",
            "scientific_validation": "prohibited",
            "lab_execution": "prohibited",
            "network_scope": "frozen exact-host policy only",
        },
    }
    write_json(destination / "run.json", run)
    return run


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("a", "b"), default="a")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--activate-phase-b", action="store_true")
    args = parser.parse_args()
    result = phase_a() if args.phase == "a" else run_phase_b(owner_activated=args.activate_phase_b)
    if args.write:
        name = "phase-a.json" if args.phase == "a" else "run.json"
        write_json(ROOT / "artifacts/goals/G10R" / name, result)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
