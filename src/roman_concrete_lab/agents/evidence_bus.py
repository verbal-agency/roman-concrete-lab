"""Typed, append-only evidence plumbing for viewpoint-centered societies.

This module is deliberately provider- and network-free.  It validates the
joins between viewpoint teams, their structural support tasks, source/action
records, dossiers, critiques, and final portfolio attribution.  Unresolved
or missing joins are retained as diagnostics; they are never silently dropped
and are never promoted to evidence.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from jsonschema import validate

from ..retrieval import PolicyBlocked, StaleContext, canonical, digest
from tools.tournament.replay import ROOT


SCHEMA_VERSION = "1.0"


def _load_schema(name: str) -> dict[str, Any]:
    return json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))


def _validate(name: str, value: dict[str, Any]) -> None:
    validate(value, _load_schema(name))


class EvidenceBus:
    """Append-only, scoped joins for one case and treatment."""

    def __init__(
        self,
        *,
        case_id: str,
        problem_id: str,
        problem_version: str,
        treatment_id: str,
        context_hash: str,
    ) -> None:
        self.case_id = case_id
        self.problem_id = problem_id
        self.problem_version = problem_version
        self.treatment_id = treatment_id
        self.context_hash = context_hash
        self.actions: dict[str, dict[str, Any]] = {}
        self.candidates: dict[str, dict[str, Any]] = {}
        self.tasks: dict[str, dict[str, Any]] = {}
        self.reports: dict[str, dict[str, Any]] = {}
        self.dossiers: dict[str, dict[str, Any]] = {}
        self.critiques: dict[str, dict[str, Any]] = {}
        self._append_order: list[tuple[str, str]] = []

    def _scope(self, record: dict[str, Any], *, context_hash: str | None = None) -> None:
        if "case_id" in record and record.get("case_id") != self.case_id:
            raise PolicyBlocked("evidence-bus record uses a different case")
        if record.get("problem_id") not in {None, self.problem_id}:
            raise PolicyBlocked("cross-problem evidence-bus record")
        if record.get("problem_version") not in {None, self.problem_version}:
            raise PolicyBlocked("evidence-bus record uses a different problem version")
        if context_hash is not None and context_hash != self.context_hash:
            raise StaleContext("evidence-bus write uses a stale context hash")

    def _append(self, collection: dict[str, dict[str, Any]], kind: str, key: str, value: dict[str, Any]) -> dict[str, Any]:
        existing = collection.get(key)
        if existing is not None:
            if canonical(existing) != canonical(value):
                raise PolicyBlocked(f"duplicate {kind} has a different payload: {key}")
            return {"replayed": True, "record": deepcopy(existing)}
        collection[key] = deepcopy(value)
        self._append_order.append((kind, key))
        return {"replayed": False, "record": deepcopy(value)}

    def register_action(self, action: dict[str, Any]) -> dict[str, Any]:
        self._scope(action)
        action_id = action.get("action_id")
        if not action_id:
            raise PolicyBlocked("action is missing action_id")
        return self._append(self.actions, "ACTION", action_id, action)

    def register_candidate(self, candidate: dict[str, Any]) -> dict[str, Any]:
        self._scope(candidate)
        candidate_id = candidate.get("source_candidate_id")
        if not candidate_id:
            raise PolicyBlocked("candidate is missing source_candidate_id")
        return self._append(self.candidates, "SOURCE_CANDIDATE", candidate_id, candidate)

    def assign_task(self, task: dict[str, Any]) -> dict[str, Any]:
        _validate("viewpoint-support-task.schema.json", task)
        self._scope(task)
        if task["treatment_id"] != self.treatment_id:
            raise PolicyBlocked("support task treatment does not match evidence bus")
        return self._append(self.tasks, "SUPPORT_TASK", task["task_id"], task)

    def add_support_report(self, report: dict[str, Any]) -> dict[str, Any]:
        _validate("viewpoint-support-report.schema.json", report)
        self._scope(report)
        task = self.tasks.get(report["support_task_id"])
        if task is None:
            raise PolicyBlocked("support report references an unknown task")
        if task["viewpoint_id"] != report["viewpoint_id"]:
            raise PolicyBlocked("support report viewpoint does not match assigned task")
        return self._append(self.reports, "SUPPORT_REPORT", report["report_id"], report)

    def build_dossier(self, *, dossier_id: str, viewpoint_id: str, report_ids: list[str]) -> dict[str, Any]:
        if not report_ids:
            raise PolicyBlocked("viewpoint dossier requires at least one support report")
        reports = []
        diagnostics: list[str] = []
        for report_id in report_ids:
            report = self.reports.get(report_id)
            if report is None:
                diagnostics.append(f"missing_support_report:{report_id}")
                continue
            if report["viewpoint_id"] != viewpoint_id:
                raise PolicyBlocked("dossier mixes reports from different viewpoints")
            reports.append(report)
        if not reports:
            raise PolicyBlocked("dossier has no recoverable support reports")
        task_ids = sorted({report["support_task_id"] for report in reports})
        action_ids = sorted({action_id for report in reports for action_id in report["action_ids"]})
        source_ids = sorted({source_id for report in reports for source_id in report["source_candidate_ids"]})
        claim_ids = sorted({claim_id for report in reports for claim_id in report["claim_ids"]})
        for action_id in action_ids:
            if action_id not in self.actions:
                diagnostics.append(f"unresolved_action:{action_id}")
        for source_id in source_ids:
            if source_id not in self.candidates:
                diagnostics.append(f"unresolved_source_candidate:{source_id}")
        dossier = {
            "schema_version": SCHEMA_VERSION,
            "dossier_id": dossier_id,
            "case_id": self.case_id,
            "viewpoint_id": viewpoint_id,
            "support_task_ids": task_ids,
            "report_ids": sorted(report_ids),
            "action_ids": action_ids,
            "source_candidate_ids": source_ids,
            "claim_ids": claim_ids,
            "dissenting_report_ids": sorted(report["report_id"] for report in reports if report["stance"] == "WEAKENS"),
            "diagnostics": sorted(set(diagnostics)),
            "status": "PARTIAL" if diagnostics else "COMPLETE",
        }
        _validate("viewpoint-dossier.schema.json", dossier)
        return self._append(self.dossiers, "VIEWPOINT_DOSSIER", dossier_id, dossier)["record"]

    def add_critique(self, critique: dict[str, Any]) -> dict[str, Any]:
        _validate("cross-viewpoint-critique.schema.json", critique)
        self._scope(critique)
        if any(dossier_id not in self.dossiers for dossier_id in critique["dossier_ids"]):
            raise PolicyBlocked("critique references an unknown viewpoint dossier")
        if critique["target_viewpoint_id"] not in critique["compared_viewpoint_ids"]:
            raise PolicyBlocked("critique target must be one of the compared viewpoints")
        return self._append(self.critiques, "CROSS_VIEWPOINT_CRITIQUE", critique["critique_id"], critique)

    def portfolio_envelope(
        self,
        *,
        envelope_id: str,
        portfolio: dict[str, Any],
        dossier_ids: list[str],
        critique_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        critique_ids = critique_ids or []
        dossiers = [self.dossiers[dossier_id] for dossier_id in dossier_ids if dossier_id in self.dossiers]
        diagnostics: list[str] = []
        diagnostics.extend(f"missing_viewpoint_dossier:{item}" for item in dossier_ids if item not in self.dossiers)
        for critique_id in critique_ids:
            if critique_id not in self.critiques:
                diagnostics.append(f"missing_cross_viewpoint_critique:{critique_id}")
        viewpoint_ids = sorted({dossier["viewpoint_id"] for dossier in dossiers})
        support_task_ids = sorted({task_id for dossier in dossiers for task_id in dossier["support_task_ids"]})
        dossier_source_ids = {source_id for dossier in dossiers for source_id in dossier["source_candidate_ids"]}
        portfolio_source_ids = set(portfolio.get("source_candidate_ids", []))
        for hypothesis in portfolio.get("hypotheses", []):
            portfolio_source_ids.update(hypothesis.get("source_candidate_ids", []))
        omitted = sorted(dossier_source_ids - portfolio_source_ids)
        diagnostics.extend(f"portfolio_omitted_source_candidate:{source_id}" for source_id in omitted)
        source_ids = sorted(dossier_source_ids | portfolio_source_ids)
        if any(source_id not in self.candidates for source_id in source_ids):
            diagnostics.extend(
                f"unresolved_source_candidate:{source_id}"
                for source_id in source_ids
                if source_id not in self.candidates
            )
        status = "REVIEW_REQUIRED" if diagnostics else "READY"
        envelope = {
            "schema_version": SCHEMA_VERSION,
            "envelope_id": envelope_id,
            "case_id": self.case_id,
            "treatment_id": self.treatment_id,
            "portfolio": deepcopy(portfolio),
            "viewpoint_ids": viewpoint_ids,
            "support_task_ids": support_task_ids,
            "dossier_ids": sorted(dossier_ids),
            "critique_ids": sorted(critique_ids),
            "source_candidate_ids": source_ids,
            "diagnostics": sorted(set(diagnostics)),
            "status": status,
        }
        _validate("society-portfolio-envelope.schema.json", envelope)
        return envelope

    def attribution_ledger(self, *, ledger_id: str, envelope: dict[str, Any]) -> dict[str, Any]:
        _validate("society-portfolio-envelope.schema.json", envelope)
        entries: list[dict[str, Any]] = []
        for kind, key in self._append_order:
            collection = {
                "ACTION": self.actions,
                "SOURCE_CANDIDATE": self.candidates,
                "SUPPORT_TASK": self.tasks,
                "SUPPORT_REPORT": self.reports,
                "VIEWPOINT_DOSSIER": self.dossiers,
                "CROSS_VIEWPOINT_CRITIQUE": self.critiques,
            }.get(kind)
            if collection is None:
                continue
            record = collection[key]
            if kind == "ACTION":
                linked_reports = [
                    report for report in self.reports.values()
                    if key in report.get("action_ids", [])
                ]
                linked_viewpoints = sorted({report["viewpoint_id"] for report in linked_reports})
                linked_tasks = sorted({report["support_task_id"] for report in linked_reports})
                action_diagnostics = []
                if not linked_reports:
                    action_diagnostics.append("action_has_no_viewpoint_join")
                entries.append({
                    "record_id": key, "record_type": "ACTION",
                    "viewpoint_id": linked_viewpoints[0] if len(linked_viewpoints) == 1 else None,
                    "support_task_id": linked_tasks[0] if len(linked_tasks) == 1 else None,
                    "action_ids": [key], "source_candidate_ids": list(record.get("output_ids", [])),
                    "parent_record_ids": sorted(report["report_id"] for report in linked_reports),
                    "join_status": "ATTRIBUTED" if linked_reports and len(linked_viewpoints) == 1 and len(linked_tasks) == 1 else "HISTORICAL_UNASSIGNED",
                    "diagnostics": action_diagnostics,
                })
            elif kind == "SUPPORT_REPORT":
                missing = [source_id for source_id in record["source_candidate_ids"] if source_id not in self.candidates]
                entries.append({
                    "record_id": key, "record_type": "SUPPORT_REPORT", "viewpoint_id": record["viewpoint_id"],
                    "support_task_id": record["support_task_id"], "action_ids": sorted(record["action_ids"]),
                    "source_candidate_ids": sorted(record["source_candidate_ids"]), "parent_record_ids": [],
                    "join_status": "PARTIAL" if missing else "ATTRIBUTED",
                    "diagnostics": [f"unresolved_source_candidate:{item}" for item in missing],
                })
            elif kind == "VIEWPOINT_DOSSIER":
                entries.append({
                    "record_id": key, "record_type": "DOSSIER", "viewpoint_id": record["viewpoint_id"],
                    "support_task_id": record["support_task_ids"][0] if len(record["support_task_ids"]) == 1 else None,
                    "action_ids": sorted(record["action_ids"]), "source_candidate_ids": sorted(record["source_candidate_ids"]),
                    "parent_record_ids": sorted(record["report_ids"]),
                    "join_status": "PARTIAL" if record["diagnostics"] else "ATTRIBUTED",
                    "diagnostics": list(record["diagnostics"]),
                })
        dossier_ids = set(envelope["dossier_ids"])
        portfolio_diag = list(envelope["diagnostics"])
        entries.append({
            "record_id": envelope["envelope_id"], "record_type": "PORTFOLIO",
            "viewpoint_id": envelope["viewpoint_ids"][0] if len(envelope["viewpoint_ids"]) == 1 else None,
            "support_task_id": envelope["support_task_ids"][0] if len(envelope["support_task_ids"]) == 1 else None,
            "action_ids": [], "source_candidate_ids": sorted(envelope["source_candidate_ids"]),
            "parent_record_ids": sorted(dossier_ids | set(envelope["critique_ids"])),
            "join_status": "PARTIAL" if portfolio_diag else "ATTRIBUTED", "diagnostics": portfolio_diag,
        })
        diagnostics = sorted({item for entry in entries for item in entry["diagnostics"]})
        ledger = {
            "schema_version": SCHEMA_VERSION,
            "ledger_id": ledger_id,
            "case_id": self.case_id,
            "treatment_id": self.treatment_id,
            "entries": entries,
            "diagnostics": diagnostics,
            "status": "REVIEW_REQUIRED" if diagnostics else "READY",
        }
        _validate("society-attribution-ledger.schema.json", ledger)
        return ledger

    def checkpoint(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "case_id": self.case_id,
            "problem_id": self.problem_id,
            "problem_version": self.problem_version,
            "treatment_id": self.treatment_id,
            "context_hash": self.context_hash,
            "actions": deepcopy(self.actions),
            "candidates": deepcopy(self.candidates),
            "tasks": deepcopy(self.tasks),
            "reports": deepcopy(self.reports),
            "dossiers": deepcopy(self.dossiers),
            "critiques": deepcopy(self.critiques),
            "append_order": deepcopy(self._append_order),
        }

    @classmethod
    def from_checkpoint(cls, checkpoint: dict[str, Any], *, context_hash: str | None = None) -> "EvidenceBus":
        expected_context = checkpoint["context_hash"]
        if context_hash is not None and context_hash != expected_context:
            raise StaleContext("evidence-bus checkpoint uses a stale context hash")
        bus = cls(
            case_id=checkpoint["case_id"], problem_id=checkpoint["problem_id"],
            problem_version=checkpoint["problem_version"], treatment_id=checkpoint["treatment_id"],
            context_hash=expected_context,
        )
        for name in ("actions", "candidates", "tasks", "reports", "dossiers", "critiques"):
            setattr(bus, name, deepcopy(checkpoint.get(name, {})))
        bus._append_order = [tuple(item) for item in checkpoint.get("append_order", [])]
        return bus
