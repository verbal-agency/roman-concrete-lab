import json
import unittest
from pathlib import Path

from tools.tournament.policy import HypothesisRegistry, MemoryPermissionError
from tools.tournament.replay import ROOT, replay, run_case


class TournamentReplayTests(unittest.TestCase):
    def test_all_cases_match_prescribed_behavior(self):
        result = replay()
        self.assertEqual(result["card_count"], 3)
        self.assertEqual(result["fixture_results"], {
            "positive": "PARETO_SET",
            "contradictory": "REVIEW_REQUIRED",
            "malformed": "REVIEW_REQUIRED",
            "partial": "REVIEW_REQUIRED",
            "unsupported": "ABSTAIN",
            "unsafe": "UNSAFE_REJECTED",
            "no-feasible": "NO_FEASIBLE_CANDIDATE",
            "budget-exhaustion": "BUDGET_EXHAUSTED",
        })

    def test_replay_is_byte_stable_and_has_no_eig_or_universal_winner(self):
        first = replay()
        second = replay()
        first_json = json.dumps(first, sort_keys=True, separators=(",", ":"))
        second_json = json.dumps(second, sort_keys=True, separators=(",", ":"))
        self.assertEqual(first_json, second_json)
        self.assertNotIn("eig", first_json.lower())
        for result in first["card_results"].values():
            self.assertEqual(result["status"], "PARETO_SET")
            self.assertIsNone(result["stages"]["adjudicate"]["aggregate_score"])
            self.assertEqual(result["sensitivity"]["winner_stability"], "NO_SINGLE_WINNER")
        roman = first["card_results"]["roman-concrete"]
        self.assertEqual(len(roman["hypotheses"]), 2)
        self.assertTrue(all(item["rival_hypothesis_ids"] for item in roman["hypotheses"]))

    def test_memory_permissions_are_enforced(self):
        result = replay()
        roman = result["card_results"]["roman-concrete"]
        evidence = json.loads((ROOT / "fixtures/portfolio/roman.json").read_text())["scoped_memory"]["evidence"]
        from tools.tournament.policy import MemoryStore

        store = MemoryStore(evidence)
        with self.assertRaises(MemoryPermissionError):
            store.write_evidence(evidence[0])
        store.write_hypothesis(roman["hypotheses"][0])
        with self.assertRaises(MemoryPermissionError):
            store.write_hypothesis(roman["hypotheses"][0])
        store.write_note({"memory_id": "N-test", "memory_type": "untrusted_note", "text": "untrusted"})
        self.assertEqual(store.notes[0]["memory_id"], "N-test")

    def test_status_transition_rules_include_retraction_and_context_amendment(self):
        result = replay()["card_results"]["roman-concrete"]
        registry = HypothesisRegistry.empty()
        record = result["hypotheses"][0]
        registry.append(record)
        registry.transition(record["hypothesis_id"], "REVIEW_REQUIRED", "NEEDS_REVIEW")
        registry.transition(record["hypothesis_id"], "ABSTAIN", "REVIEW_ABSTAINED")
        with self.assertRaises(ValueError):
            registry.transition(record["hypothesis_id"], "HYPOTHESIS", "WRONG_REASON")
        registry.transition(record["hypothesis_id"], "HYPOTHESIS", "CONTEXT_AMENDED", new_context_version="1.1")
        registry.transition(record["hypothesis_id"], "RETIRED", "RETRACTED_AFTER_CONTEXT_AMENDMENT")
        self.assertEqual(registry.snapshot()[0]["status"], "RETIRED")

    def test_cross_card_outputs_preserve_problem_specific_support_regions(self):
        result = replay()
        support_regions = {
            problem_id: json.loads((ROOT / "fixtures/portfolio" / f"{filename}.json").read_text())["support_region"]
            for problem_id, filename in {
                "roman-concrete": "roman",
                "lime-mortar": "lime-mortar",
                "battery-cathode": "battery-cathode",
            }.items()
        }
        for problem_id, tournament in result["card_results"].items():
            self.assertEqual(tournament["problem_id"], problem_id)
            self.assertTrue(all(h["applicable_domain"] and h["support_region"] for h in tournament["hypotheses"]))
            self.assertNotEqual(tournament["problem_id"], "")
        self.assertEqual(len(set(support_regions.values())), 3)

    def test_budget_case_has_partial_manifest_and_no_scope_widening(self):
        result = run_case(ROOT / "fixtures/tournament/budget-exhaustion.json")
        self.assertEqual(result["status"], "BUDGET_EXHAUSTED")
        self.assertTrue(result["stages"]["focus"]["partial_manifest"])
        self.assertIn("do not widen scope", result["focus_decision"]["abstention_condition"])


if __name__ == "__main__":
    unittest.main()
