import csv
import json
import unittest
from pathlib import Path

from tools.portfolio.replay import replay, validate_card, validate_entry


ROOT = Path(__file__).resolve().parents[2]


class PortfolioValidationTests(unittest.TestCase):
    def test_three_cards_validate_and_emit_domain_scoped_outputs(self):
        result = replay()
        self.assertEqual(result["card_count"], 3)
        self.assertEqual(result["card_outputs"]["roman-concrete"], "PROVISIONAL_BEST")
        self.assertEqual(result["card_outputs"]["lime-mortar"], "PARETO_SET")
        self.assertEqual(result["card_outputs"]["battery-cathode"], "ABSTAIN")

    def test_behavior_fixtures_preserve_statuses_and_reject_cross_domain(self):
        result = replay()
        self.assertEqual(result["fixture_results"], {
            "positive": "PROVISIONAL_BEST",
            "contradictory": "REVIEW_REQUIRED",
            "incomplete": "REVIEW_REQUIRED",
            "unsupported": "ABSTAIN",
            "out-of-domain": "REJECT_COMPARISON",
        })

    def test_memory_tiers_are_separate(self):
        card = json.loads((ROOT / "fixtures/portfolio/roman.json").read_text())
        validate_card(card)
        memory = card["scoped_memory"]
        evidence = {item["memory_id"] for item in memory["evidence"]}
        hypotheses = {item["memory_id"] for item in memory["hypotheses"]}
        notes = {item["memory_id"] for item in memory["untrusted_notes"]}
        self.assertFalse(evidence & hypotheses)
        self.assertFalse(evidence & notes)
        self.assertFalse(hypotheses & notes)

    def test_schema_and_protocol_have_no_agent_or_lab_authority(self):
        protocol = (ROOT / "docs/protocols/problem-specific-discovery.md").read_text()
        self.assertIn("offline-only", protocol)
        self.assertIn("No output may claim", protocol)
        self.assertIn("no agent runtime", protocol)


if __name__ == "__main__":
    unittest.main()
