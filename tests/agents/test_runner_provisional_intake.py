import unittest

from tools.evaluation.runner_provisional_intake_replay import replay
from src.roman_concrete_lab.agents.conflict_adjudication import ConflictAdjudicationLedger
from src.roman_concrete_lab.retrieval import PolicyBlocked
from tools.tournament.replay import ROOT


class RunnerProvisionalIntakeTests(unittest.TestCase):
    def test_offline_runner_replay_passes_all_criteria(self):
        result = replay(root=ROOT)
        self.assertEqual(result["status"], "RUNNER_PROVISIONAL_INTAKE_READY")
        self.assertTrue(all(result["criteria"].values()))
        self.assertEqual(result["authority"]["model_calls"], 0)

    def test_runner_checkpoint_contains_both_arms_and_conflict_statuses(self):
        result = replay(root=ROOT)
        for arm in ("A1", "A2-M"):
            intake = result["checkpoints"][arm]["provisional_intake"]
            self.assertEqual(intake["arm"], arm)
            self.assertEqual({item["status"] for item in intake["conflict_sets"]}, {"SCOPE_DIFFERENCE", "WEIGHTED_CONFLICT"})
            self.assertIn("CONTRADICTED", {item["status"] for item in intake["edges"]})

    def test_conflict_adjudication_does_not_allow_weighting_incomparable_edges(self):
        ledger = ConflictAdjudicationLedger(case_id="case", problem_id="problem", problem_version="1")
        conflict = ledger.open_set(
            claim_id="C1",
            edges=[{"edge_id": "E1", "source_id": "S1", "status": "SUPPORTED"}, {"edge_id": "E2", "source_id": "S2", "status": "CONTRADICTED"}],
            scope={"material": "a", "process": "b", "comparator": "c", "endpoint": "d", "method": "e"},
        )
        with self.assertRaises(PolicyBlocked):
            ledger.adjudicate(
                conflict_set_id=conflict["conflict_set_id"], reviewer_role="ADJUDICATOR", comparable=False,
                scope_checks={"material": False, "process": False, "comparator": False, "endpoint": False, "method": False, "independence": True},
                outcome="WEIGHTED_CONFLICT", rationale="not comparable", unresolved_questions=[],
            )

    def test_completed_replay_has_no_new_calls_or_spend(self):
        result = replay(root=ROOT)
        self.assertTrue(result["replay"]["deterministic"])
        self.assertEqual(result["authority"]["paid_spend_usd"], 0)


if __name__ == "__main__":
    unittest.main()
