import csv
import json
import tempfile
import unittest
from pathlib import Path

from tools.literature_audit.landscape_replay import (
    build_landscape,
    field_state,
    index_unique,
    replay,
)


ROOT = Path(__file__).resolve().parents[2]


class LandscapeReplayTests(unittest.TestCase):
    def paths(self):
        return {
            "sources_path": ROOT / "data/manifests/literature-sufficiency-sources.jsonl",
            "screening_path": ROOT / "data/manifests/literature-sufficiency-screening.csv",
            "families_path": ROOT / "data/processed/literature-sufficiency-study-families.jsonl",
            "candidates_path": ROOT / "data/processed/literature-sufficiency-material-candidates.jsonl",
            "access_path": ROOT / "data/manifests/literature-sufficiency-access-register.csv",
            "decision_path": ROOT / "artifacts/goals/G-1/decision.json",
            "protocol_path": ROOT / "docs/protocols/landscape-readiness.md",
        }

    def test_replay_is_deterministic_and_reports_incomplete_landscape(self):
        first = replay(**self.paths())
        second = replay(**self.paths())
        self.assertEqual(first, second)
        self.assertEqual(first["run"]["readiness"], "LANDSCAPE_INCOMPLETE")
        self.assertEqual(first["record_count"], 38)
        self.assertEqual(first["map"]["study_family_count"], 24)
        self.assertEqual(first["map"]["candidate_count"], 5)
        self.assertTrue(first["map"]["second_review"])
        self.assertTrue(all(item["result"] == "PASS" for item in first["map"]["second_review"]))
        self.assertIn("route-level access register covers 14/38 source records", first["run"]["blockers"])

    def test_missingness_is_not_coerced_to_zero(self):
        missing = field_state("UNRESOLVED")
        not_reported = field_state("NOT_REPORTED")
        self.assertEqual(missing, {"status": "UNRESOLVED"})
        self.assertEqual(not_reported, {"status": "NOT_REPORTED"})
        self.assertNotIn("value", missing)

    def test_duplicate_ids_fail_without_snapshot(self):
        with self.assertRaisesRegex(ValueError, "duplicate record_id"):
            index_unique([{"record_id": "S01"}, {"record_id": "S01"}], "record_id", "sources")

    def test_unknown_family_reference_fails(self):
        paths = self.paths()
        with tempfile.TemporaryDirectory() as directory:
            temp_screening = Path(directory) / "screening.csv"
            rows = list(csv.DictReader(paths["screening_path"].open(encoding="utf-8", newline="")))
            rows[0]["study_family_id"] = "F-UNKNOWN"
            with temp_screening.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
            paths["screening_path"] = temp_screening
            with self.assertRaisesRegex(ValueError, "unknown study family F-UNKNOWN"):
                build_landscape(**paths)

    def test_input_change_gets_new_run_id(self):
        paths = self.paths()
        first = replay(**paths)["run"]["run_id"]
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".md") as handle:
            handle.write(paths["protocol_path"].read_text(encoding="utf-8") + "\n# fixture change\n")
            handle.flush()
            paths["protocol_path"] = Path(handle.name)
            second = replay(**paths)["run"]["run_id"]
        self.assertNotEqual(first, second)

    def test_offline_fixture_covers_contract_cases(self):
        fixture = ROOT / "fixtures/landscape/cases.jsonl"
        cases = [json.loads(line) for line in fixture.read_text(encoding="utf-8").splitlines() if line]
        self.assertEqual(
            {case["case_id"] for case in cases},
            {
                "complete_ready",
                "partial_access",
                "duplicate_source_id",
                "contradictory_field_values",
                "malformed_record",
                "rights_restricted",
                "unsupported_transfer",
                "budget_exhaustion",
            },
        )


if __name__ == "__main__":
    unittest.main()
