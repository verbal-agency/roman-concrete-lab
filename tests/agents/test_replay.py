import json
import unittest

from jsonschema import validate

from src.roman_concrete_lab.agents.replay import ROOT, replay, run_society
from tools.tournament.policy import MemoryPermissionError, MemoryStore


class AgentReplayTests(unittest.TestCase):
    def test_sealed_replay_runs_all_cases_and_rejects_without_improvement(self):
        result = replay()
        self.assertEqual(result["case_count"], 8)
        self.assertEqual(result["run_count"], 24)
        self.assertEqual(result["adoption_decision"], "REJECT_AGENT_SOCIETY")
        self.assertEqual(result["critical_failures"], [])
        self.assertEqual(result["society_accuracy"], result["control_accuracy"])

    def test_development_iteration_changes_focus_without_touching_sealed_cases(self):
        iteration = replay()["development_iteration"]
        self.assertEqual(iteration["before_focus"], "round_robin")
        self.assertEqual(iteration["after_focus"], "provenance_first")
        self.assertTrue(iteration["sealed_cases_untouched"])

    def test_replay_is_stable_and_state_machine_fails_closed(self):
        first = replay()
        second = replay()
        self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))
        positive = run_society(ROOT / "fixtures/tournament/positive.json", 11)
        self.assertEqual(positive["state_trace"][-1], "awaiting_review")
        self.assertNotIn("completed", positive["state_trace"])
        budget = run_society(ROOT / "fixtures/tournament/budget-exhaustion.json", 11)
        self.assertEqual(budget["state_trace"][-1], "budget_exhausted")

    def test_memory_and_schema_authority_boundaries(self):
        evidence = [{"memory_id": "E-1", "text": "immutable", "source_locator": "fixture"}]
        store = MemoryStore(evidence)
        with self.assertRaises(MemoryPermissionError):
            store.write_evidence(evidence[0])
        schema = json.loads((ROOT / "schemas/agent-run.schema.json").read_text())
        for run in replay()["runs"]:
            validate(run, schema)
            self.assertEqual(run["authority"]["model_calls"], "none")
            self.assertEqual(run["authority"]["evidence_write"], "prohibited")
            self.assertEqual(len(run["roles"]), 5)


if __name__ == "__main__":
    unittest.main()
