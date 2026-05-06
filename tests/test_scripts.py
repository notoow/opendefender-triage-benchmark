from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import make_prompt_batch  # noqa: E402
import generate_release_manifest  # noqa: E402
import score_model_outputs  # noqa: E402
import summarize_dataset  # noqa: E402
import validate_dataset  # noqa: E402
import validate_model_outputs  # noqa: E402


DATASET_PATH = REPO_ROOT / "data" / "sample_alerts.jsonl"
SAMPLE_OUTPUTS_PATH = REPO_ROOT / "examples" / "model_outputs.sample.jsonl"


class DatasetValidationTests(unittest.TestCase):
    def test_sample_dataset_validates(self) -> None:
        count, errors, categories = validate_dataset.validate_dataset(DATASET_PATH)

        self.assertEqual(count, 20)
        self.assertEqual(errors, [])
        self.assertEqual(categories, {"cloud", "collaboration", "email", "endpoint", "identity", "network"})

    def test_model_outputs_validate_against_known_cases(self) -> None:
        count, errors = validate_model_outputs.validate_outputs(DATASET_PATH, SAMPLE_OUTPUTS_PATH)

        self.assertEqual(count, 2)
        self.assertEqual(errors, [])


class PromptBatchTests(unittest.TestCase):
    def test_prompt_batch_generation_preserves_case_ids(self) -> None:
        cases = make_prompt_batch.load_jsonl(DATASET_PATH)
        template = make_prompt_batch.load_template(REPO_ROOT / "evaluation" / "prompt_template.md")
        prompt_records = [make_prompt_batch.make_prompt_record(case, template) for case in cases]

        self.assertEqual(len(prompt_records), 20)
        self.assertEqual(prompt_records[0]["case_id"], "odtb-0001")
        self.assertIn("Alert packet:", prompt_records[0]["prompt"])
        self.assertIn("identity_provider", prompt_records[0]["prompt"])

    def test_prompt_batch_write_outputs_jsonl(self) -> None:
        cases = make_prompt_batch.load_jsonl(DATASET_PATH)
        template = make_prompt_batch.load_template(REPO_ROOT / "evaluation" / "prompt_template.md")
        prompt_records = [make_prompt_batch.make_prompt_record(case, template) for case in cases[:2]]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "prompts.jsonl"
            make_prompt_batch.write_jsonl(output_path, prompt_records)
            lines = output_path.read_text(encoding="utf-8").splitlines()

        self.assertEqual(len(lines), 2)
        self.assertEqual(json.loads(lines[0])["case_id"], "odtb-0001")


class SummaryTests(unittest.TestCase):
    def test_summary_contains_core_counts(self) -> None:
        records = summarize_dataset.load_jsonl(DATASET_PATH)
        summary = summarize_dataset.generate_summary(records, Path("data/sample_alerts.jsonl"))

        self.assertIn("| Total cases | 20 |", summary)
        self.assertIn("| endpoint | 5 |", summary)
        self.assertIn("| medium | 8 |", summary)
        self.assertIn("## Difficulty Distribution", summary)
        self.assertIn("| hard | 7 |", summary)
        self.assertIn("| evidence_grounding | 9 |", summary)


class ReleaseManifestTests(unittest.TestCase):
    def test_release_manifest_contains_version_and_hashes(self) -> None:
        manifest = generate_release_manifest.build_manifest(
            REPO_ROOT,
            Path("data/sample_alerts.jsonl"),
            Path("DATASET_VERSION"),
            [Path(path) for path in generate_release_manifest.DEFAULT_ARTIFACTS],
        )

        self.assertEqual(manifest["dataset_version"], "0.1.0")
        self.assertEqual(manifest["case_count"], 20)
        self.assertEqual(manifest["difficulty_counts"]["hard"], 7)
        self.assertEqual(manifest["failure_mode_counts"]["over_escalation"], 8)
        self.assertEqual(len(manifest["artifacts"]), len(generate_release_manifest.DEFAULT_ARTIFACTS))
        self.assertTrue(all(len(artifact["sha256"]) == 64 for artifact in manifest["artifacts"]))


class ScoringTests(unittest.TestCase):
    def test_scoring_helpers(self) -> None:
        self.assertEqual(
            score_model_outputs.classification_score(
                "possible_account_compromise_attempt",
                "possible_account_compromise_attempt",
            ),
            4,
        )
        self.assertEqual(score_model_outputs.severity_score("medium", "high"), 2)
        self.assertEqual(score_model_outputs.severity_score("low", "critical"), 0)

    def test_sample_outputs_score_without_safety_flags(self) -> None:
        references = {
            record["id"]: record
            for record in score_model_outputs.load_jsonl(DATASET_PATH)
        }
        outputs = score_model_outputs.load_jsonl(SAMPLE_OUTPUTS_PATH)
        scores = [score_model_outputs.score_record(record, references) for record in outputs]

        self.assertEqual(len(scores), 2)
        self.assertTrue(all(score.total >= 15 for score in scores))
        self.assertFalse(any(score.safety_flag for score in scores))


if __name__ == "__main__":
    unittest.main()
