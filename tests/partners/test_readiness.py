import csv
import json
import unittest
from pathlib import Path

from tools.partners.decision import classify_response, validate_response


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "fixtures/partners"


class PartnerReadinessTests(unittest.TestCase):
    def test_all_offline_fixtures_validate_and_classify(self):
        for path in sorted(FIXTURES.glob("*.json")):
            case = json.loads(path.read_text())
            validate_response(case["response"])
            self.assertEqual(classify_response(case["response"]), case["expected_gate"], path.name)

    def test_capability_matrix_distinguishes_required_and_optional(self):
        with (ROOT / "docs/partners/facility-capability-matrix.csv").open(newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertTrue(any(row["requirement_level"] == "required" for row in rows))
        self.assertTrue(any(row["requirement_level"] == "optional" for row in rows))

    def test_packet_preserves_unknowns_and_no_outbound_boundary(self):
        text = (ROOT / "docs/partners/partner-readiness-package.md").read_text()
        self.assertIn("NO OUTBOUND CONTACT", text)
        self.assertIn("UNKNOWN", text)
        self.assertIn("FEASIBLE_FOR_REVIEW", text)
        self.assertIn("Not safety approval", text)

    def test_outbound_status_is_immutable(self):
        case = json.loads((FIXTURES / "feasible.json").read_text())
        case["response"]["outbound_status"] = "SENT"
        with self.assertRaises(ValueError):
            validate_response(case["response"])


if __name__ == "__main__":
    unittest.main()
