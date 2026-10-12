import json
import unittest
from copy import deepcopy
from pathlib import Path

from src.roman_concrete_lab.agents.viewpoint_society import (
    ViewpointSociety,
    allocate_viewpoint_focus,
    run_offline_fixture,
    score_viewpoint_portfolio,
    validate_viewpoint_roster,
)
from src.roman_concrete_lab.retrieval import PolicyBlocked
from tools.tournament.replay import ROOT


def load_rows(name):
    path = ROOT / "fixtures/investigation/viewpoint-society" / name
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class ViewpointSocietyTests(unittest.TestCase):
    def setUp(self):
        self.case = load_rows("development.jsonl")[0]

    def test_roster_has_distinct_viewpoints_null_and_open_slot(self):
        result = validate_viewpoint_roster(self.case["viewpoint_cards"], case_id=self.case["case_id"])
        self.assertTrue(result["passes"])
        self.assertEqual(result["candidate_count"], 2)
        self.assertEqual(len(result["null_ids"]), 1)
        self.assertEqual(len(result["open_slot_ids"]), 1)

    def test_viewpoint_teams_are_private_until_all_commit(self):
        society = ViewpointSociety(
            case_id=self.case["case_id"], problem_id=self.case["problem_id"], problem_version=self.case["problem_version"],
            treatment_id="A2-VIEWPOINT", viewpoint_cards=self.case["viewpoint_cards"], context_hash=self.case["context_hash"],
        )
        task = next(item for item in self.case["tasks"] if item["viewpoint_id"] == "VP-LIME")
        society.assign_support_task({
            "schema_version": "1.0", "task_id": task["task_id"], "case_id": self.case["case_id"],
            "problem_id": self.case["problem_id"], "problem_version": self.case["problem_version"],
            "treatment_id": "A2-VIEWPOINT", "viewpoint_id": task["viewpoint_id"], "task_type": task["task_type"],
            "charter": task["charter"], "status": "COMPLETED",
        })
        report = next(item for item in self.case["reports"] if item["viewpoint_id"] == "VP-LIME")
        action = {
            "schema_version": "1.0", "action_id": "ACT-PRIVATE", "run_id": "RUN-PRIVATE", "case_id": self.case["case_id"],
            "problem_id": self.case["problem_id"], "problem_version": self.case["problem_version"], "arm": "A2-M",
            "branch_id": "VP-LIME", "action_type": "SEARCH", "rationale": "fixture", "input": {"query": "fixture"},
            "policy_status": "ALLOWED", "budget_debit": {"queries": 1, "retained_sources": 0, "document_fetches": 0, "payload_bytes": 0, "simulation_calls": 0, "input_tokens": 0, "output_tokens": 0, "estimated_cost_usd": 0.0},
            "output_ids": [], "replay_key": "sha256:private", "timestamp": "2026-10-12T00:00:00Z",
        }
        society.register_action(action)
        society.submit_support_report(dict(report, schema_version="1.0", case_id=self.case["case_id"], action_ids=["ACT-PRIVATE"], source_candidate_ids=[], claim_ids=[]))
        society.commit_viewpoint("VP-LIME")
        with self.assertRaises(PolicyBlocked):
            society.read_shared()

    def test_support_can_weaken_its_own_viewpoint_and_dissent_survives(self):
        result = run_offline_fixture(self.case)
        self.assertTrue(result["portfolio"]["preserved_dissent_ids"])
        self.assertIn("REPORT-LIME-CRIT", result["portfolio"]["preserved_dissent_ids"])
        self.assertTrue(result["envelope"]["diagnostics"])
        self.assertFalse(result["score"]["evidence_promotion"])

    def test_open_slot_admission_is_typed_and_bounded(self):
        society = ViewpointSociety(
            case_id=self.case["case_id"], problem_id=self.case["problem_id"], problem_version=self.case["problem_version"],
            treatment_id="A2-VIEWPOINT", viewpoint_cards=self.case["viewpoint_cards"], context_hash=self.case["context_hash"],
        )
        card = deepcopy(next(item for item in self.case["viewpoint_cards"] if item["kind"] == "CANDIDATE"))
        card["viewpoint_id"] = "VP-OPEN-ADMITTED"
        card["statement"] = "A newly admitted bounded mechanism."
        society.admit_open_viewpoint(card, reason="distinct predicted discriminator")
        self.assertIn("VP-OPEN-ADMITTED", society.active_ids)
        with self.assertRaises(PolicyBlocked):
            society.admit_open_viewpoint(card, reason="duplicate")

    def test_focus_is_deterministic_and_preserves_null_and_rival(self):
        stats = self.case["focus_stats"]
        first = allocate_viewpoint_focus(stats, 4, null_viewpoint_id="VP-NULL")
        second = allocate_viewpoint_focus(list(reversed(stats)), 4, null_viewpoint_id="VP-NULL")
        self.assertEqual(first, second)
        self.assertTrue(first["null_retained"])
        self.assertTrue(first["rival_retained"])
        self.assertEqual(sum(first["allocations"].values()), 4)
        abstain = allocate_viewpoint_focus(stats, 1, null_viewpoint_id="VP-NULL")
        self.assertEqual(abstain["status"], "ABSTAIN")

    def test_cross_viewpoint_critique_requires_shared_dossiers(self):
        society = ViewpointSociety(
            case_id=self.case["case_id"], problem_id=self.case["problem_id"], problem_version=self.case["problem_version"],
            treatment_id="A2-VIEWPOINT", viewpoint_cards=self.case["viewpoint_cards"], context_hash=self.case["context_hash"],
        )
        with self.assertRaises(PolicyBlocked):
            society.add_cross_viewpoint_critique({"schema_version": "1.0", "critique_id": "CRIT", "case_id": self.case["case_id"], "critic_id": "C", "target_viewpoint_id": "VP-LIME", "compared_viewpoint_ids": ["VP-LIME", "VP-NULL"], "dossier_ids": [], "source_candidate_ids": [], "challenge": "challenge", "proposed_discriminator": "discriminator", "status": "REVIEW_REQUIRED"})

    def test_adjudication_preserves_rivals_and_does_not_reward_consensus(self):
        result = run_offline_fixture(self.case)
        portfolio = result["portfolio"]
        self.assertGreaterEqual(len(portfolio["credible_rival_ids"]), 1)
        self.assertGreaterEqual(len(portfolio["viewpoint_dossier_ids"]), 3)
        self.assertEqual(result["score"]["viewpoint_count_credit"], 0)
        self.assertEqual(result["score"]["consensus_credit"], 0)
        self.assertEqual(result["score"]["rhetoric_credit"], 0)

    def test_checkpoint_resume_and_sealed_fixture_replay(self):
        sealed = load_rows("sealed.jsonl")[0]
        first = run_offline_fixture(sealed)
        resumed = ViewpointSociety.from_checkpoint(first["checkpoint"], context_hash=sealed["context_hash"])
        self.assertEqual(json.dumps(resumed.checkpoint(), sort_keys=True), json.dumps(first["checkpoint"], sort_keys=True))
        second = run_offline_fixture(sealed)
        self.assertEqual(json.dumps(first["portfolio"], sort_keys=True), json.dumps(second["portfolio"], sort_keys=True))


if __name__ == "__main__":
    unittest.main()
