from pathlib import Path
from tempfile import TemporaryDirectory
import json
import subprocess
import sys
import unittest

from scripts.analyze_case_study import analyze_manifest


FIXTURES = Path(__file__).parent / "fixtures" / "case-study"


class CaseStudyAnalysisTests(unittest.TestCase):
    def test_filters_every_out_of_scope_grouping_dimension(self):
        result = analyze_manifest(FIXTURES / "complete.json")
        summary = result["summary"]

        self.assertEqual(summary["counts"]["discovered"], 8)
        self.assertEqual(summary["counts"]["in_scope"], 4)
        self.assertEqual(summary["counts"]["out_of_scope"], 4)
        self.assertEqual(len(result["trials"]), 4)
        self.assertEqual(len(summary["primary"]["pairs"]), 2)
        self.assertTrue(
            all(t["checkpoint_alias"] == "dense-27b" for t in result["trials"])
        )
        mismatch_fields = {
            field
            for item in summary["out_of_scope"]
            for field in item["mismatched_fields"]
        }
        self.assertTrue(
            {"checkpoint_alias", "architecture", "engine_alias", "scheme_alias", "task_alias"}
            <= mismatch_fields
        )

    def test_reports_evidence_counts_and_attrition_separately(self):
        summary = analyze_manifest(FIXTURES / "attrition.json")["summary"]

        self.assertEqual(
            summary["counts"],
            {
                "discovered": 6,
                "in_scope": 6,
                "out_of_scope": 0,
                "valid_attempts": 5,
                "verifier_covered": 3,
                "successful_completions": 1,
            },
        )
        self.assertEqual(summary["attrition"]["environment_harness_failure"], 1)
        self.assertEqual(summary["attrition"]["model_agent_timeout"], 1)
        self.assertEqual(summary["attrition"]["verifier_only_failure"], 1)

    def test_retains_model_agent_timeout_as_an_outcome(self):
        result = analyze_manifest(FIXTURES / "attrition.json")
        timeout = next(
            trial
            for trial in result["trials"]
            if trial["attempt_status"] == "model_agent_timeout"
        )

        self.assertEqual(timeout["reward"], 0)
        self.assertEqual(timeout["elapsed_seconds"], 7200)
        self.assertFalse(timeout["verifier_status"] == "complete")

    def test_pairs_only_identical_task_and_repetition(self):
        summary = analyze_manifest(FIXTURES / "unmatched.json")["summary"]

        self.assertEqual(summary["primary"]["pairs"], [])
        self.assertEqual(summary["publication_gate"]["status"], "blocked")
        self.assertIn("no verifier-covered primary pairs", summary["publication_gate"]["reasons"])
        self.assertNotIn("headline", summary)

    def test_blocks_publication_when_primary_metrics_are_missing(self):
        summary = analyze_manifest(FIXTURES / "attrition.json")["summary"]

        self.assertEqual(summary["publication_gate"]["status"], "blocked")
        self.assertIn("primary matrix is incomplete", summary["publication_gate"]["reasons"])
        self.assertNotIn("headline", summary)

    def test_computes_primary_paired_metrics_before_secondary_efficiency(self):
        summary = analyze_manifest(FIXTURES / "complete.json")["summary"]
        pairs = summary["primary"]["pairs"]

        self.assertAlmostEqual(pairs[0]["f2p_delta"], -0.10)
        self.assertAlmostEqual(pairs[0]["p2p_delta"], -0.10)
        self.assertEqual(pairs[0]["reward_delta"], -1)
        self.assertAlmostEqual(pairs[1]["f2p_delta"], 0.05)
        self.assertAlmostEqual(pairs[1]["p2p_delta"], 0.05)
        self.assertEqual(pairs[1]["reward_delta"], 1)
        self.assertAlmostEqual(summary["primary"]["aggregate"]["f2p_delta"], -0.025)
        self.assertAlmostEqual(summary["primary"]["aggregate"]["p2p_delta"], -0.025)
        self.assertAlmostEqual(summary["primary"]["aggregate"]["reward_delta"], 0.0)
        self.assertAlmostEqual(summary["secondary"]["paired"]["steps_delta"], 0.0)
        self.assertEqual(summary["publication_gate"]["status"], "ready")

    def test_sanitizes_private_and_unvalidated_fields(self):
        result = analyze_manifest(FIXTURES / "complete.json")
        serialized = json.dumps(result, sort_keys=True).lower()

        self.assertNotIn("thought_duplication", serialized)
        self.assertNotIn("job_alias", serialized)
        self.assertNotIn("source_path", serialized)
        allowed = {
            "checkpoint_alias",
            "precision_alias",
            "architecture",
            "task_alias",
            "repetition",
            "attempt_status",
            "verifier_status",
            "reward",
            "f2p",
            "p2p",
            "steps",
            "input_tokens",
            "output_tokens",
            "elapsed_seconds",
            "peak_context_tokens",
        }
        self.assertTrue(all(set(trial) <= allowed for trial in result["trials"]))

    def test_cli_outputs_are_byte_stable(self):
        with TemporaryDirectory() as tmp:
            first_trials = Path(tmp) / "first-trials.json"
            first_summary = Path(tmp) / "first-summary.json"
            second_trials = Path(tmp) / "second-trials.json"
            second_summary = Path(tmp) / "second-summary.json"
            command = [
                sys.executable,
                "scripts/analyze_case_study.py",
                "--manifest",
                str(FIXTURES / "complete.json"),
            ]
            first = subprocess.run(
                command
                + ["--trials-out", str(first_trials), "--summary-out", str(first_summary)],
                cwd=Path(__file__).parents[1],
                capture_output=True,
                text=True,
                check=False,
            )
            second = subprocess.run(
                command
                + ["--trials-out", str(second_trials), "--summary-out", str(second_summary)],
                cwd=Path(__file__).parents[1],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(first_trials.read_bytes(), second_trials.read_bytes())
            self.assertEqual(first_summary.read_bytes(), second_summary.read_bytes())


if __name__ == "__main__":
    unittest.main()
