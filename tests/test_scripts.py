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
import check_dataset_quality  # noqa: E402
import generate_baseline_report  # noqa: E402
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


class QualityTests(unittest.TestCase):
    def test_dataset_quality_gates_pass(self) -> None:
        records = check_dataset_quality.load_jsonl(DATASET_PATH)
        checks = check_dataset_quality.build_quality_checks(records)
        report = check_dataset_quality.format_markdown(records, checks, Path("data/sample_alerts.jsonl"))

        self.assertTrue(all(check.passed for check in checks))
        self.assertIn("| Failed checks | 0 |", report)
        self.assertIn("| Sensitive token scan | pass | no sensitive-token patterns detected |", report)

    def test_sensitive_token_scan_detects_email_like_values(self) -> None:
        records = [
            {
                "id": "odtb-9999",
                "alert_packet": {"business_context": "contact alice@example.com"},
            }
        ]

        hits = check_dataset_quality.find_sensitive_hits(records)

        self.assertEqual(hits, ["odtb-9999: matched email address"])


class ReleaseManifestTests(unittest.TestCase):
    def test_baseline_report_contains_grouped_results(self) -> None:
        report = generate_baseline_report.generate_report(DATASET_PATH, REPO_ROOT / "DATASET_VERSION")

        self.assertIn("Average total: 12.95 / 20", report)
        self.assertIn("Scores by Failure Mode", report)
        self.assertIn("| under_escalation | 4 | 11.75 |", report)

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
        groups = score_model_outputs.build_group_summaries(scores, references)
        markdown = score_model_outputs.format_markdown(scores, 18.0, 0, groups)

        self.assertEqual(len(scores), 2)
        self.assertTrue(all(score.total >= 15 for score in scores))
        self.assertFalse(any(score.safety_flag for score in scores))
        self.assertEqual([group.group for group in groups["by_category"]], ["cloud", "identity"])
        self.assertEqual(groups["by_difficulty"][0].group, "medium")
        self.assertIn("Scores by Failure Mode", markdown)


if __name__ == "__main__":
    unittest.main()
