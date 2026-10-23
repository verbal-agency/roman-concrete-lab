import json
import unittest

from src.roman_concrete_lab.agents.evidence_bus import EvidenceBus
from src.roman_concrete_lab.retrieval import PolicyBlocked, StaleContext


class EvidenceBusTests(unittest.TestCase):
    def setUp(self):
        self.bus = EvidenceBus(
            case_id="CASE-1",
            problem_id="roman-hot-mix",
            problem_version="1.0",
            treatment_id="A2-VIEWPOINT",
            context_hash="sha256:context",
        )
        self.source = {
            "schema_version": "1.0", "source_candidate_id": "SRC-1",
            "problem_id": "roman-hot-mix", "problem_version": "1.0",
            "title": "A candidate source", "locator": "https://example.org/source",
            "content_locator": None, "discovery_query": "lime mortar",
            "host": "example.org", "access_class": "PUBLIC", "rights_state": "PERMITTED",
            "identity_status": "CANONICAL", "attribution_status": "UNREVIEWED",
            "content_hash": None, "deduplication_key": "doi:example/1",
            "support_region": "review", "contradiction_ids": [], "status": "DISCOVERED",
        }
        self.action = {
            "schema_version": "1.0", "action_id": "ACT-1", "run_id": "RUN-1",
            "case_id": "CASE-1", "problem_id": "roman-hot-mix", "problem_version": "1.0",
            "arm": "A2-M", "branch_id": "VIEW-M1", "action_type": "SEARCH",
            "rationale": "Find a process-matched source.", "input": {"query": "lime mortar"},
            "policy_status": "ALLOWED",
            "budget_debit": {"queries": 1, "retained_sources": 1, "document_fetches": 0, "payload_bytes": 0, "simulation_calls": 0, "input_tokens": 0, "output_tokens": 0, "estimated_cost_usd": 0.0},
            "output_ids": ["SRC-1"], "replay_key": "sha256:action", "timestamp": "2026-10-12T00:00:00Z",
        }

    def _task(self, task_id="TASK-1", viewpoint_id="VIEW-M1"):
        return {
            "schema_version": "1.0", "task_id": task_id, "case_id": "CASE-1",
            "problem_id": "roman-hot-mix", "problem_version": "1.0", "treatment_id": "A2-VIEWPOINT",
            "viewpoint_id": viewpoint_id, "task_type": "RETRIEVAL",
            "charter": "Find evidence that could support or weaken the viewpoint.", "status": "COMPLETED",
        }

    def _report(self, report_id="REPORT-1", task_id="TASK-1", viewpoint_id="VIEW-M1", source_ids=None, stance="SUPPORTS"):
        return {
            "schema_version": "1.0", "report_id": report_id, "case_id": "CASE-1",
            "viewpoint_id": viewpoint_id, "support_task_id": task_id, "stance": stance,
            "action_ids": ["ACT-1"], "source_candidate_ids": source_ids if source_ids is not None else ["SRC-1"],
            "claim_ids": ["CLAIM-1"], "summary": "The source is relevant but still pending review.",
            "unresolved_questions": ["Does the comparator match the target?"], "status": "COMPLETE",
        }

    def _portfolio(self, source_ids=None):
        return {
            "schema_version": "1.0", "case_id": "CASE-1", "status": "REVIEW_REQUIRED",
            "summary": "A provisional viewpoint remains under review.",
            "source_candidate_ids": source_ids if source_ids is not None else ["SRC-1"],
            "hypotheses": [], "leading_hypothesis_id": None, "credible_rival_ids": ["VIEW-NULL"],
            "unresolved_disputes": ["Comparator fit remains unresolved."], "negative_searches": [],
            "next_discriminating_action": "Inspect the source and compare matched specimens.",
            "authority_note": "No evidence or laboratory authority is granted.",
        }

    def test_viewpoint_support_candidate_survives_to_portfolio_and_ledger(self):
        self.bus.register_action(self.action)
        self.bus.register_candidate(self.source)
        self.bus.assign_task(self._task())
        self.bus.add_support_report(self._report())
        dossier = self.bus.build_dossier(dossier_id="DOSSIER-1", viewpoint_id="VIEW-M1", report_ids=["REPORT-1"])
        self.assertEqual(dossier["status"], "COMPLETE")
        critique = {
            "schema_version": "1.0", "critique_id": "CRIT-1", "case_id": "CASE-1",
            "critic_id": "CRITIC-1", "target_viewpoint_id": "VIEW-M1",
            "compared_viewpoint_ids": ["VIEW-M1", "VIEW-NULL"], "dossier_ids": ["DOSSIER-1"],
            "source_candidate_ids": ["SRC-1"], "challenge": "Comparator fit is not established.",
            "proposed_discriminator": "Retrieve a matched comparator study.", "status": "REVIEW_REQUIRED",
        }
        self.bus.add_critique(critique)
        envelope = self.bus.portfolio_envelope(envelope_id="ENV-1", portfolio=self._portfolio(), dossier_ids=["DOSSIER-1"], critique_ids=["CRIT-1"])
        self.assertEqual(envelope["status"], "READY")
        self.assertEqual(envelope["viewpoint_ids"], ["VIEW-M1"])
        ledger = self.bus.attribution_ledger(ledger_id="LEDGER-1", envelope=envelope)
        self.assertEqual(ledger["status"], "READY")
        portfolio_entry = next(item for item in ledger["entries"] if item["record_type"] == "PORTFOLIO")
        self.assertEqual(portfolio_entry["source_candidate_ids"], ["SRC-1"])
        self.assertEqual(portfolio_entry["viewpoint_id"], "VIEW-M1")

    def test_support_agent_can_weaken_viewpoint(self):
        self.bus.register_candidate(self.source)
        self.bus.register_action(self.action)
        self.bus.assign_task(self._task(task_id="TASK-NEG"))
        report = self._report(report_id="REPORT-NEG", task_id="TASK-NEG", stance="WEAKENS")
        self.bus.add_support_report(report)
        dossier = self.bus.build_dossier(dossier_id="DOSSIER-NEG", viewpoint_id="VIEW-M1", report_ids=["REPORT-NEG"])
        self.assertEqual(dossier["dissenting_report_ids"], ["REPORT-NEG"])

    def test_unresolved_source_is_retained_and_diagnosed(self):
        self.bus.register_action(self.action)
        self.bus.assign_task(self._task())
        self.bus.add_support_report(self._report(source_ids=["SRC-MISSING"]))
        dossier = self.bus.build_dossier(dossier_id="DOSSIER-2", viewpoint_id="VIEW-M1", report_ids=["REPORT-1"])
        self.assertIn("unresolved_source_candidate:SRC-MISSING", dossier["diagnostics"])
        envelope = self.bus.portfolio_envelope(envelope_id="ENV-2", portfolio=self._portfolio(source_ids=["SRC-MISSING"]), dossier_ids=["DOSSIER-2"])
        self.assertEqual(envelope["status"], "REVIEW_REQUIRED")
        self.assertIn("unresolved_source_candidate:SRC-MISSING", envelope["diagnostics"])
        self.assertIn("SRC-MISSING", envelope["source_candidate_ids"])

    def test_candidate_omitted_by_final_portfolio_is_not_silently_dropped(self):
        self.bus.register_action(self.action)
        self.bus.register_candidate(self.source)
        self.bus.assign_task(self._task())
        self.bus.add_support_report(self._report())
        self.bus.build_dossier(dossier_id="DOSSIER-3", viewpoint_id="VIEW-M1", report_ids=["REPORT-1"])
        envelope = self.bus.portfolio_envelope(envelope_id="ENV-3", portfolio=self._portfolio(source_ids=[]), dossier_ids=["DOSSIER-3"])
        self.assertIn("portfolio_omitted_source_candidate:SRC-1", envelope["diagnostics"])
        self.assertIn("SRC-1", envelope["source_candidate_ids"])

    def test_duplicate_observations_and_substantive_variants_are_retained(self):
        self.bus.register_candidate(self.source)
        replay = self.bus.register_candidate(dict(self.source, discovery_query="different query", status="DUPLICATE"))
        self.assertTrue(replay["replayed"])
        self.assertFalse(replay["conflict"])
        self.assertEqual(len(self.bus.candidate_observations["SRC-1"]), 2)
        changed = dict(self.source, title="different")
        variant = self.bus.register_candidate(changed)
        self.assertTrue(variant["conflict"])
        self.assertEqual(self.bus.candidates["SRC-1"]["title"], "A candidate source")
        self.assertEqual(len(self.bus.candidate_conflicts["SRC-1"]), 1)
        self.assertTrue(self.bus.candidate_conflicts["SRC-1"][0]["promotable_after_validation"])
        with self.assertRaises(StaleContext):
            self.bus.from_checkpoint(self.bus.checkpoint(), context_hash="sha256:stale")
        resumed = EvidenceBus.from_checkpoint(self.bus.checkpoint())
        self.assertEqual(json.dumps(resumed.checkpoint(), sort_keys=True), json.dumps(self.bus.checkpoint(), sort_keys=True))


if __name__ == "__main__":
    unittest.main()
