"""Provider-neutral source policy, budget, ledger, and recorded retrieval."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from jsonschema import validate


class PolicyBlocked(RuntimeError):
    """An action is outside the frozen source or authority policy."""


class BudgetExhausted(RuntimeError):
    """The next action would exceed an aggregate treatment budget."""


class StaleContext(RuntimeError):
    """A write or replay does not match the frozen context."""


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def normalize_query(query: str) -> str:
    return re.sub(r"\s+", " ", query.strip().lower())


@dataclass(frozen=True)
class BudgetLimits:
    queries: int = 12
    retained_sources: int = 24
    document_fetches: int = 4
    payload_bytes: int = 5_000_000
    simulation_calls: int = 4
    input_tokens: int = 80_000
    output_tokens: int = 7_200
    estimated_cost_usd: float = 25.0


@dataclass
class BudgetUsage:
    queries: int = 0
    retained_sources: int = 0
    document_fetches: int = 0
    payload_bytes: int = 0
    simulation_calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost_usd: float = 0.0


class InvestigationBudget:
    """Fail-before-call aggregate budget shared by one treatment."""

    def __init__(self, limits: BudgetLimits | None = None, usage: BudgetUsage | None = None) -> None:
        self.limits = limits or BudgetLimits()
        self.usage = usage or BudgetUsage()

    def preflight(self, **debit: int | float) -> dict[str, int | float]:
        proposed = asdict(self.usage)
        limits = asdict(self.limits)
        for key, amount in debit.items():
            if key not in proposed or amount < 0:
                raise ValueError(f"invalid budget debit: {key}={amount}")
            proposed[key] += amount
            if proposed[key] > limits[key]:
                raise BudgetExhausted(
                    f"{key} would reach {proposed[key]} above frozen limit {limits[key]}"
                )
        return proposed

    def debit(self, **debit: int | float) -> dict[str, int | float]:
        proposed = self.preflight(**debit)
        for key, value in proposed.items():
            setattr(self.usage, key, value)
        return self.snapshot()

    def remaining(self) -> dict[str, int | float]:
        return {
            key: asdict(self.limits)[key] - value
            for key, value in asdict(self.usage).items()
        }

    def snapshot(self) -> dict[str, Any]:
        return {"limits": asdict(self.limits), "usage": asdict(self.usage), "remaining": self.remaining()}


class SourcePolicy:
    """Exact-host, read-only policy loaded from a frozen JSON artifact."""

    def __init__(self, record: dict[str, Any]) -> None:
        self.record = record
        self.version = record["policy_version"]
        self.hosts = {item["host"]: item for item in record["hosts"]}

    @classmethod
    def load(cls, path: Path) -> "SourcePolicy":
        return cls(json.loads(path.read_text(encoding="utf-8")))

    @property
    def sha256(self) -> str:
        return digest(self.record)

    def decide(self, locator: str, *, fetch_content: bool) -> dict[str, str]:
        parsed = urlparse(locator)
        if parsed.scheme != "https" or not parsed.hostname:
            raise PolicyBlocked("only exact HTTPS hosts are permitted")
        rule = self.hosts.get(parsed.hostname.lower())
        if rule is None:
            raise PolicyBlocked(f"host is not in frozen allowlist: {parsed.hostname}")
        access_class = rule["access_class"]
        if fetch_content and access_class != "PUBLIC":
            raise PolicyBlocked(f"content fetch is not permitted for {parsed.hostname}: {access_class}")
        return {
            "host": parsed.hostname.lower(),
            "access_class": access_class,
            "rights_state": "PERMITTED" if access_class == "PUBLIC" else "METADATA_ONLY",
            "payload_rule": rule["payload_rule"],
        }


SOURCE_TRANSITIONS = {
    "DISCOVERED": {"METADATA_SCREENED", "DUPLICATE", "RIGHTS_BLOCKED", "REJECTED", "ABSTAIN"},
    "METADATA_SCREENED": {"CANDIDATE", "DUPLICATE", "RIGHTS_BLOCKED", "REJECTED", "UNSUPPORTED", "ABSTAIN"},
    "CANDIDATE": {"EVIDENCE_PENDING", "DUPLICATE", "RIGHTS_BLOCKED", "REJECTED", "UNSUPPORTED", "ABSTAIN"},
    "EVIDENCE_PENDING": {"ADMISSIBLE_FOR_REVIEW", "DUPLICATE", "RIGHTS_BLOCKED", "REJECTED", "UNSUPPORTED", "ABSTAIN"},
}
TERMINAL_SOURCE_STATES = {
    "ADMISSIBLE_FOR_REVIEW", "REJECTED", "DUPLICATE", "RIGHTS_BLOCKED", "UNSUPPORTED", "ABSTAIN",
}


def transition_source_candidate(candidate: dict[str, Any], next_status: str) -> dict[str, Any]:
    """Apply the non-promoting candidate lifecycle without mutating the input."""
    current = candidate.get("status")
    if current in TERMINAL_SOURCE_STATES:
        raise PolicyBlocked(f"terminal source state is immutable: {current}")
    if next_status not in SOURCE_TRANSITIONS.get(current, set()):
        raise PolicyBlocked(f"illegal source transition: {current} -> {next_status}")
    result = dict(candidate)
    result["status"] = next_status
    return result


class AppendOnlyLedger:
    """Minimal scoped blackboard with immutable evidence and replay safety."""

    ALLOWED_DERIVED_TYPES = {
        "InvestigationAction",
        "SourceCandidate",
        "InvestigationClaim",
        "LateralHypothesis",
        "BranchReport",
        "InvestigationPortfolio",
        "SimulationTrace",
        "FocusDecision",
    }

    def __init__(self, *, problem_id: str, problem_version: str, context_hash: str) -> None:
        self.problem_id = problem_id
        self.problem_version = problem_version
        self.context_hash = context_hash
        self._records: dict[str, dict[str, Any]] = {}

    def append(
        self,
        *,
        record_id: str,
        record_type: str,
        problem_id: str,
        problem_version: str,
        context_hash: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        if record_type == "ImmutableEvidence" or record_type not in self.ALLOWED_DERIVED_TYPES:
            raise PolicyBlocked(f"record type is not writable: {record_type}")
        if problem_id != self.problem_id or problem_version != self.problem_version:
            raise PolicyBlocked("cross-problem memory access denied")
        if context_hash != self.context_hash:
            raise StaleContext("derived write uses stale context hash")
        if record_id in self._records:
            raise PolicyBlocked(f"duplicate append-only record: {record_id}")
        record = {
            "record_id": record_id,
            "record_type": record_type,
            "problem_id": problem_id,
            "problem_version": problem_version,
            "context_hash": context_hash,
            "payload": payload,
        }
        self._records[record_id] = record
        return record

    def records(self) -> list[dict[str, Any]]:
        return [self._records[key] for key in sorted(self._records)]


class RecordedRetrievalAdapter:
    """Deterministic query/fetch adapter backed only by recorded fixtures."""

    def __init__(
        self,
        *,
        source_path: Path,
        policy: SourcePolicy,
        budget: InvestigationBudget,
        source_schema: dict[str, Any],
    ) -> None:
        self.policy = policy
        self.budget = budget
        self.source_schema = source_schema
        self.sources = [
            json.loads(line)
            for line in source_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self._query_cache: dict[str, list[dict[str, Any]]] = {}
        self._seen_dedup: dict[str, str] = {}

    def search(self, query: str) -> dict[str, Any]:
        normalized = normalize_query(query)
        if not normalized:
            raise ValueError("query must not be empty")
        if normalized in self._query_cache:
            return {"query": normalized, "replayed": True, "results": self._query_cache[normalized]}
        self.budget.debit(queries=1)
        terms = set(normalized.split())
        matches = []
        for source in self.sources:
            aliases = [normalize_query(item) for item in source.get("_fixture_queries", [])]
            searchable = " ".join([source["title"], *aliases]).lower()
            if normalized in aliases or (terms and terms.issubset(set(re.findall(r"[a-z0-9]+", searchable)))):
                candidate = {key: value for key, value in source.items() if not key.startswith("_fixture_")}
                policy = self.policy.decide(candidate["locator"], fetch_content=False)
                candidate["host"] = policy["host"]
                key = candidate["deduplication_key"]
                if key in self._seen_dedup:
                    candidate["status"] = "DUPLICATE"
                else:
                    self.budget.debit(retained_sources=1)
                    self._seen_dedup[key] = candidate["source_candidate_id"]
                validate(candidate, self.source_schema)
                matches.append(candidate)
        matches.sort(key=lambda item: item["source_candidate_id"])
        self._query_cache[normalized] = matches
        return {"query": normalized, "replayed": False, "results": matches}

    def fetch(self, source_candidate_id: str) -> dict[str, Any]:
        source = next(
            (item for item in self.sources if item["source_candidate_id"] == source_candidate_id),
            None,
        )
        if source is None:
            raise KeyError(source_candidate_id)
        self.policy.decide(source["locator"], fetch_content=True)
        payload = source.get("_fixture_payload", "")
        payload_bytes = len(payload.encode("utf-8"))
        self.budget.debit(payload_bytes=payload_bytes)
        return {
            "source_candidate_id": source_candidate_id,
            "payload": payload,
            "payload_bytes": payload_bytes,
            "content_hash": "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest(),
        }
