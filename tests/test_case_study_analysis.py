from pathlib import Path
from tempfile import TemporaryDirectory
import json
import subprocess
import sys
import unittest

from scripts.analyze_case_study import AnalysisError, analyze_manifest


FIXTURES = Path(__file__).parent / "fixtures" / "case-study"


def full_manifest() -> dict:
    conditions = {
        "bf16": {"scheme_alias": "bf16-weights"},
        "mlx-affine-int8-g64": {"scheme_alias": "mlx-affine-int8-g64"},
    }
    trials = []
    for task_index in range(1, 6):
        for repetition in range(1, 5):
            for condition, details in conditions.items():
                trials.append(
                    {
                        "checkpoint_alias": "dense-27b",
                        "architecture": "dense-hybrid",
                        "engine_alias": "omlx-0.5.1",
                        "precision_alias": condition,
                        "scheme_alias": details["scheme_alias"],
                        "task_alias": f"task-{task_index:02d}",
                        "repetition": repetition,
                        "attempt": 1,
                        "selected_for_analysis": True,
                        "attempt_status": "completed",
                        "verifier_status": "complete",
                        "reward": 1,
                        "f2p": 1.0,
                        "f2p_numerator": 1,
                        "f2p_denominator": 1,
                        "p2p": 1.0,
                        "p2p_numerator": 1,
                        "p2p_denominator": 1,
                        "steps": 20,
                        "input_tokens": 100,
                        "output_tokens": 50,
                        "elapsed_seconds": 200,
                        "peak_context_tokens": 1000,
                    }
                )
    return {
        "study": {
            "checkpoint_alias": "dense-27b",
            "architecture": "dense-hybrid",
            "engine_alias": "omlx-0.5.1",
            "conditions": conditions,
            "baseline_condition": "bf16",
            "treatment_condition": "mlx-affine-int8-g64",
            "task_aliases": [f"task-{index:02d}" for index in range(1, 6)],
            "repetitions": [1, 2, 3, 4],
        },
        "private_provenance": {"parity_status": "verified"},
        "matrix": {
            "execution": "sequential",
            "task_order": "alias",
            "condition_order": "alternating-by-repetition",
            "expected_trials": 40,
        },
        "trials": trials,
    }


def add_verified_provenance(manifest: dict) -> None:
    conditions = manifest["study"]["conditions"]
    tasks = manifest["study"]["task_aliases"]
    manifest["private_provenance"] = {
        "parity_status": "verified",
        "alias_map_status": "verified",
        "effective_settings_snapshot_sha256": "a" * 64,
        "condition_sources": {
            condition: {
                "checkpoint_source_revision": "private-checkpoint-revision",
                "tokenizer_revision": "private-tokenizer-revision",
            }
            for condition in conditions
        },
    }
    manifest["private_condition_mapping"] = {
        condition: {"model_id": f"private-model-{index}"}
        for index, condition in enumerate(conditions, start=1)
    }
    manifest["private_task_mapping"] = {
        alias: {"task_id": f"private-task-id-{index}"}
        for index, alias in enumerate(tasks, start=1)
    }


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

    def test_explicit_condition_roles_make_deltas_independent_of_json_order(self):
        manifest = json.loads((FIXTURES / "complete.json").read_text())
        manifest["study"]["baseline_condition"] = "bf16"
        manifest["study"]["treatment_condition"] = "mlx-affine-int8-g64"
        manifest["study"]["conditions"] = dict(
            reversed(list(manifest["study"]["conditions"].items()))
        )

        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "reversed.json"
            path.write_text(json.dumps(manifest))
            pairs = analyze_manifest(path)["summary"]["primary"]["pairs"]

        self.assertAlmostEqual(pairs[0]["f2p_delta"], -0.10)
        self.assertAlmostEqual(pairs[0]["p2p_delta"], -0.10)

    def test_publication_gate_requires_verified_provenance(self):
        summary = analyze_manifest(FIXTURES / "complete.json")["summary"]

        self.assertEqual(summary["publication_gate"]["status"], "blocked")
        self.assertIn(
            "immutable provenance is not verified",
            summary["publication_gate"]["reasons"],
        )

    def test_publication_gate_requires_complete_provenance_evidence(self):
        manifest = full_manifest()

        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "incomplete-provenance.json"
            path.write_text(json.dumps(manifest))
            summary = analyze_manifest(path)["summary"]

        self.assertIn(
            "provenance evidence is incomplete",
            summary["publication_gate"]["reasons"],
        )

    def test_publication_gate_rejects_provenance_mismatch(self):
        manifest = full_manifest()
        add_verified_provenance(manifest)
        manifest["private_provenance"]["condition_sources"][
            "mlx-affine-int8-g64"
        ]["checkpoint_source_revision"] = "different-private-revision"

        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "mismatched-provenance.json"
            path.write_text(json.dumps(manifest))
            summary = analyze_manifest(path)["summary"]

        self.assertIn(
            "immutable checkpoint or tokenizer parity failed",
            summary["publication_gate"]["reasons"],
        )

    def test_rejects_path_like_public_aliases(self):
        manifest = full_manifest()
        manifest["study"]["checkpoint_alias"] = "../../private-model"
        for trial in manifest["trials"]:
            trial["checkpoint_alias"] = "../../private-model"

        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "unsafe-alias.json"
            path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(AnalysisError, "public aliases must be safe slugs"):
                analyze_manifest(path)

    def test_publication_gate_requires_frozen_forty_trial_shape(self):
        summary = analyze_manifest(FIXTURES / "complete.json")["summary"]

        self.assertIn(
            "study shape does not match frozen 40-trial protocol",
            summary["publication_gate"]["reasons"],
        )

    def test_publication_gate_requires_frozen_condition_schedule(self):
        manifest = full_manifest()
        manifest["matrix"]["condition_order"] = "same-order"

        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "wrong-order.json"
            path.write_text(json.dumps(manifest))
            summary = analyze_manifest(path)["summary"]

        self.assertIn(
            "study shape does not match frozen 40-trial protocol",
            summary["publication_gate"]["reasons"],
        )

    def test_publication_gate_rejects_selected_infrastructure_failure(self):
        manifest = full_manifest()
        manifest["trials"][0]["attempt_status"] = "environment_harness_failure"

        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "invalid-selected.json"
            path.write_text(json.dumps(manifest))
            summary = analyze_manifest(path)["summary"]

        self.assertEqual(summary["publication_gate"]["status"], "blocked")
        self.assertIn(
            "selected analysis attempt is not a valid model outcome",
            summary["publication_gate"]["reasons"],
        )
        self.assertEqual(len(summary["secondary"]["pairs"]), 19)

    def test_publication_gate_requires_one_selected_attempt_per_cell(self):
        manifest = full_manifest()
        duplicate = dict(manifest["trials"][0])
        duplicate["attempt"] = 2
        manifest["trials"].append(duplicate)

        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "two-selected.json"
            path.write_text(json.dumps(manifest))
            summary = analyze_manifest(path)["summary"]

        self.assertIn(
            "planned cell must have exactly one selected attempt",
            summary["publication_gate"]["reasons"],
        )

    def test_rejects_undeclared_attempt_and_verifier_statuses(self):
        for field, value in (
            ("attempt_status", "private-failure-detail"),
            ("verifier_status", "manual-pass"),
        ):
            manifest = full_manifest()
            manifest["trials"][0][field] = value
            with self.subTest(field=field), TemporaryDirectory() as tmp:
                path = Path(tmp) / "manifest.json"
                path.write_text(json.dumps(manifest))
                with self.assertRaisesRegex(AnalysisError, "status"):
                    analyze_manifest(path)

    def test_rejects_primary_metric_outside_unit_interval(self):
        manifest = full_manifest()
        manifest["trials"][0]["f2p"] = 1.2

        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "invalid-metric.json"
            path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(AnalysisError, "f2p must be in the unit interval"):
                analyze_manifest(path)

    def test_missing_reward_does_not_remove_primary_verifier_pair(self):
        manifest = json.loads((FIXTURES / "complete.json").read_text())
        manifest["trials"][1]["reward"] = None

        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "missing-reward.json"
            path.write_text(json.dumps(manifest))
            summary = analyze_manifest(path)["summary"]

        self.assertEqual(len(summary["primary"]["pairs"]), 2)
        self.assertEqual(summary["guardrail"]["reward_pair_count"], 1)
        self.assertIsNone(summary["primary"]["pairs"][0]["reward_delta"])

    def test_primary_pair_requires_complete_verifier_status(self):
        manifest = full_manifest()
        manifest["trials"][0]["verifier_status"] = "missing"

        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "missing-verifier.json"
            path.write_text(json.dumps(manifest))
            summary = analyze_manifest(path)["summary"]

        self.assertEqual(len(summary["primary"]["pairs"]), 19)
        self.assertIn(
            "primary matrix is incomplete",
            summary["publication_gate"]["reasons"],
        )

    def test_reports_task_means_and_deterministic_task_clustered_bootstrap(self):
        manifest = full_manifest()
        add_verified_provenance(manifest)

        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "bootstrap.json"
            path.write_text(json.dumps(manifest))
            first = analyze_manifest(path)["summary"]["primary"]
            second = analyze_manifest(path)["summary"]["primary"]

        self.assertEqual(len(first["task_means"]), 5)
        self.assertEqual(first["confidence_intervals"], second["confidence_intervals"])
        self.assertEqual(first["confidence_intervals"]["f2p_delta"]["lower"], 0.0)
        self.assertEqual(first["confidence_intervals"]["f2p_delta"]["upper"], 0.0)
        self.assertEqual(first["confidence_intervals"]["f2p_delta"]["replicates"], 10000)
        self.assertEqual(first["confidence_intervals"]["f2p_delta"]["seed"], 20260715)

    def test_reports_full_secondary_distributions_by_condition(self):
        manifest = full_manifest()
        add_verified_provenance(manifest)

        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "secondary-distributions.json"
            path.write_text(json.dumps(manifest))
            secondary = analyze_manifest(path)["summary"]["secondary"]

        self.assertEqual(len(secondary["distributions"]["bf16"]["steps"]), 20)
        self.assertEqual(
            len(secondary["distributions"]["mlx-affine-int8-g64"]["elapsed_seconds"]),
            20,
        )

    def test_publication_gate_requires_complete_reward_guardrail(self):
        manifest = full_manifest()
        add_verified_provenance(manifest)
        manifest["trials"][0]["reward"] = None

        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "missing-reward-guardrail.json"
            path.write_text(json.dumps(manifest))
            summary = analyze_manifest(path)["summary"]

        self.assertEqual(len(summary["primary"]["pairs"]), 20)
        self.assertIn(
            "reward guardrail matrix is incomplete",
            summary["publication_gate"]["reasons"],
        )

    def test_publication_gate_requires_explicit_attempt_selection_metadata(self):
        manifest = full_manifest()
        add_verified_provenance(manifest)
        del manifest["trials"][0]["selected_for_analysis"]

        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "implicit-selection.json"
            path.write_text(json.dumps(manifest))
            summary = analyze_manifest(path)["summary"]

        self.assertIn(
            "attempt selection metadata is incomplete",
            summary["publication_gate"]["reasons"],
        )

    def test_publication_gate_is_ready_only_for_complete_frozen_manifest(self):
        manifest = full_manifest()
        add_verified_provenance(manifest)

        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "ready.json"
            path.write_text(json.dumps(manifest))
            gate = analyze_manifest(path)["summary"]["publication_gate"]

        self.assertEqual(gate, {"status": "ready", "reasons": []})

    def test_publication_gate_requires_verifier_metric_counts(self):
        manifest = full_manifest()
        del manifest["trials"][0]["f2p_numerator"]

        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "missing-counts.json"
            path.write_text(json.dumps(manifest))
            summary = analyze_manifest(path)["summary"]

        self.assertIn(
            "verifier metric counts are incomplete",
            summary["publication_gate"]["reasons"],
        )

    def test_retains_failed_attempt_before_selected_rerun(self):
        manifest = json.loads((FIXTURES / "complete.json").read_text())
        for trial in manifest["trials"]:
            trial["attempt"] = 1
            trial["selected_for_analysis"] = True
        selected = manifest["trials"][0]
        selected["attempt"] = 2
        failed = dict(selected)
        failed.update(
            {
                "attempt": 1,
                "selected_for_analysis": False,
                "attempt_status": "environment_harness_failure",
                "verifier_status": "missing",
                "reward": None,
                "f2p": None,
                "p2p": None,
            }
        )
        manifest["trials"].append(failed)

        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "rerun.json"
            path.write_text(json.dumps(manifest))
            summary = analyze_manifest(path)["summary"]

        self.assertEqual(summary["counts"]["in_scope"], 5)
        self.assertEqual(summary["attrition"]["environment_harness_failure"], 1)
        self.assertEqual(len(summary["primary"]["pairs"]), 2)

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
            "attempt",
            "selected_for_analysis",
            "attempt_status",
            "verifier_status",
            "reward",
            "f2p",
            "f2p_numerator",
            "f2p_denominator",
            "p2p",
            "p2p_numerator",
            "p2p_denominator",
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
