import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from roman_concrete_lab.release.build import build_release, lint_claims, verify_release


class ReleaseBuildTests(unittest.TestCase):
    def test_clean_build_reproduces_byte_identical_release(self):
        with tempfile.TemporaryDirectory() as temporary:
            first = build_release(ROOT, Path(temporary) / "first", "test-exploratory-platform")
            second = build_release(ROOT, Path(temporary) / "second", "test-exploratory-platform")
            first_files = sorted(path.relative_to(first) for path in first.rglob("*") if path.is_file())
            second_files = sorted(path.relative_to(second) for path in second.rglob("*") if path.is_file())
            self.assertEqual(first_files, second_files)
            for relative in first_files:
                self.assertEqual((first / relative).read_bytes(), (second / relative).read_bytes(), str(relative))
            self.assertEqual(verify_release(first)["status"], "PASS")

    def test_release_mode_claims_rights_and_runtime_boundaries(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = build_release(ROOT, Path(temporary) / "release", "test-exploratory-platform")
            manifest = json.loads((output / "manifest.json").read_text())
            release = json.loads((output / "release.json").read_text())
            tournament = json.loads((output / "tournament-replay.json").read_text())
            rights = json.loads((output / "rights.json").read_text())
            sbom = json.loads((output / "software-bill-of-materials.json").read_text())
            self.assertEqual(manifest["release_mode"], "EXPLORATORY_PLATFORM")
            self.assertEqual(release["source_branch"], "GP4/G07E")
            self.assertEqual(tournament["goal"], "G07E")
            self.assertIn("roman-concrete", release["rankings"]["cards"])
            self.assertTrue(release["rankings"]["cards"]["roman-concrete"]["reviewer_authorities"])
            self.assertFalse(rights["restricted_full_text_included"])
            self.assertFalse(sbom["network_runtime_dependency"])
            self.assertFalse(sbom["llm_runtime_dependency"])
            self.assertFalse(sbom["agent_runtime_dependency"])

    def test_claim_linter_requires_evidence_and_rejects_empirical_language(self):
        with self.assertRaises(ValueError):
            lint_claims([{
                "claim_id": "bad",
                "text": "This material works and proves the best material recipe.",
                "claim_type": "DERIVED",
                "evidence_locators": ["fixture://bad"],
                "support_region": "fixture",
            }])
        with self.assertRaises(ValueError):
            lint_claims([{
                "claim_id": "missing-evidence",
                "text": "A bounded derived assertion.",
                "claim_type": "DERIVED",
                "evidence_locators": [],
                "support_region": "fixture",
            }])


if __name__ == "__main__":
    unittest.main()
