#!/usr/bin/env python3
"""Build deterministic, sanitized public evidence from a private case-study manifest."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
import json
from pathlib import Path
import random
import re
from statistics import mean
from typing import Any, Iterable


PUBLIC_TRIAL_FIELDS = (
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
)
SECONDARY_FIELDS = (
    "steps",
    "input_tokens",
    "output_tokens",
    "elapsed_seconds",
    "peak_context_tokens",
)
VALID_ATTEMPT_STATUSES = {"completed", "model_agent_timeout", "model_agent_failure"}
ATTEMPT_STATUSES = VALID_ATTEMPT_STATUSES | {"environment_harness_failure"}
VERIFIER_STATUSES = {"complete", "missing", "verifier_only_failure"}
PUBLIC_ALIAS_RE = re.compile(r"[a-z0-9][a-z0-9._-]{0,63}")


def _is_safe_alias(value: Any) -> bool:
    return isinstance(value, str) and PUBLIC_ALIAS_RE.fullmatch(value) is not None


class AnalysisError(ValueError):
    """The private manifest cannot support a deterministic public analysis."""


@dataclass(frozen=True)
class Study:
    checkpoint_alias: str
    architecture: str
    engine_alias: str
    conditions: dict[str, dict[str, Any]]
    baseline_condition: str
    treatment_condition: str
    task_aliases: tuple[str, ...]
    repetitions: tuple[int, ...]

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "Study":
        required = (
            "checkpoint_alias",
            "architecture",
            "engine_alias",
            "conditions",
            "baseline_condition",
            "treatment_condition",
            "task_aliases",
            "repetitions",
        )
        missing = [field for field in required if field not in value]
        if missing:
            raise AnalysisError(f"study is missing fields: {', '.join(missing)}")
        conditions = value["conditions"]
        if not isinstance(conditions, dict) or len(conditions) != 2:
            raise AnalysisError("study.conditions must define exactly two conditions")
        baseline = str(value["baseline_condition"])
        treatment = str(value["treatment_condition"])
        if baseline == treatment or {baseline, treatment} != set(conditions):
            raise AnalysisError(
                "study baseline/treatment conditions must be distinct and name both conditions"
            )
        task_aliases = tuple(str(item) for item in value["task_aliases"])
        public_aliases = [
            value["checkpoint_alias"],
            value["architecture"],
            value["engine_alias"],
            *conditions,
            *task_aliases,
            *(details.get("scheme_alias") for details in conditions.values()),
        ]
        if any(not _is_safe_alias(alias) for alias in public_aliases):
            raise AnalysisError("public aliases must be safe slugs")
        return cls(
            checkpoint_alias=str(value["checkpoint_alias"]),
            architecture=str(value["architecture"]),
            engine_alias=str(value["engine_alias"]),
            conditions=conditions,
            baseline_condition=baseline,
            treatment_condition=treatment,
            task_aliases=task_aliases,
            repetitions=tuple(int(item) for item in value["repetitions"]),
        )


def _json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _nested_find(value: Any, names: Iterable[str]) -> Any:
    """Find the first named scalar in a Pier-style nested result structure."""
    wanted = tuple(names)
    if isinstance(value, dict):
        for name in wanted:
            if name in value and not isinstance(value[name], (dict, list)):
                return value[name]
        for child in value.values():
            found = _nested_find(child, wanted)
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = _nested_find(child, wanted)
            if found is not None:
                return found
    return None


def _load_trial(entry: dict[str, Any], manifest_dir: Path) -> dict[str, Any]:
    if "record_path" in entry:
        record_path = Path(entry["record_path"]).expanduser()
        if not record_path.is_absolute():
            record_path = manifest_dir / record_path
        record = _json(record_path)
        return {**record, **{k: v for k, v in entry.items() if k != "record_path"}}

    if "trial_path" in entry:
        trial_path = Path(entry["trial_path"]).expanduser()
        if not trial_path.is_absolute():
            trial_path = manifest_dir / trial_path
        result_path = trial_path / "result.json"
        reward_path = trial_path / "verifier" / "reward.json"
        result = _json(result_path) if result_path.exists() else {}
        reward = _json(reward_path) if reward_path.exists() else {}
        normalized = {**entry}
        normalized.pop("trial_path", None)
        normalized.setdefault(
            "attempt_status",
            "completed" if result else "environment_harness_failure",
        )
        normalized.setdefault(
            "verifier_status",
            "complete" if reward_path.exists() else "missing",
        )
        field_sources = {
            "reward": (reward, ("reward", "binary")),
            "f2p": (reward, ("f2p",)),
            "p2p": (reward, ("p2p",)),
            "steps": (result, ("n_agent_steps", "steps")),
            "input_tokens": (result, ("n_input_tokens", "input_tokens")),
            "output_tokens": (result, ("n_output_tokens", "output_tokens")),
            "elapsed_seconds": (result, ("elapsed_seconds", "duration_seconds")),
            "peak_context_tokens": (
                result,
                ("peak_context_tokens", "max_context_tokens"),
            ),
        }
        for field, (source, names) in field_sources.items():
            normalized.setdefault(field, _nested_find(source, names))
        return normalized

    return dict(entry)


def _mismatched_fields(record: dict[str, Any], study: Study) -> list[str]:
    mismatches: list[str] = []
    for field, expected in (
        ("checkpoint_alias", study.checkpoint_alias),
        ("architecture", study.architecture),
        ("engine_alias", study.engine_alias),
    ):
        if record.get(field) != expected:
            mismatches.append(field)

    precision = record.get("precision_alias")
    if precision not in study.conditions:
        mismatches.append("precision_alias")
    elif record.get("scheme_alias") != study.conditions[precision].get("scheme_alias"):
        mismatches.append("scheme_alias")

    if record.get("task_alias") not in study.task_aliases:
        mismatches.append("task_alias")
    if record.get("repetition") not in study.repetitions:
        mismatches.append("repetition")
    return sorted(set(mismatches))


def _sanitize(record: dict[str, Any]) -> dict[str, Any]:
    sanitized = {field: record.get(field) for field in PUBLIC_TRIAL_FIELDS}
    sanitized["attempt"] = record.get("attempt", 1)
    sanitized["selected_for_analysis"] = record.get("selected_for_analysis", True)
    return sanitized


def _validate_metrics(record: dict[str, Any], index: int) -> None:
    if record.get("attempt_status") not in ATTEMPT_STATUSES:
        raise AnalysisError(f"trial {index} has an undeclared attempt status")
    if record.get("verifier_status") not in VERIFIER_STATUSES:
        raise AnalysisError(f"trial {index} has an undeclared verifier status")
    for field in ("f2p", "p2p"):
        value = record.get(field)
        if value is not None and (
            not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 1
        ):
            raise AnalysisError(
                f"trial {index} {field} must be in the unit interval"
            )
    reward = record.get("reward")
    if reward is not None and reward not in (0, 1):
        raise AnalysisError(f"trial {index} reward must be binary")
    for field in SECONDARY_FIELDS:
        value = record.get(field)
        if value is not None and (
            not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0
        ):
            raise AnalysisError(f"trial {index} {field} must be non-negative")


def _metric_counts_complete(record: dict[str, Any]) -> bool:
    for field in ("f2p", "p2p"):
        numerator = record.get(f"{field}_numerator")
        denominator = record.get(f"{field}_denominator")
        if (
            not isinstance(numerator, int)
            or isinstance(numerator, bool)
            or not isinstance(denominator, int)
            or isinstance(denominator, bool)
            or denominator <= 0
            or not 0 <= numerator <= denominator
            or record.get(field) is None
            or abs(float(record[field]) - numerator / denominator) > 1e-9
        ):
            return False
    return True


def _provenance_reasons(manifest: dict[str, Any], study: Study) -> list[str]:
    provenance = manifest.get("private_provenance")
    if not isinstance(provenance, dict) or provenance.get("parity_status") != "verified":
        return ["immutable provenance is not verified"]

    sources = provenance.get("condition_sources")
    condition_mapping = manifest.get("private_condition_mapping")
    task_mapping = manifest.get("private_task_mapping")
    settings_hash = provenance.get("effective_settings_snapshot_sha256")
    complete = (
        provenance.get("alias_map_status") == "verified"
        and isinstance(settings_hash, str)
        and re.fullmatch(r"[0-9a-f]{64}", settings_hash) is not None
        and isinstance(sources, dict)
        and set(sources) == set(study.conditions)
        and isinstance(condition_mapping, dict)
        and set(condition_mapping) == set(study.conditions)
        and isinstance(task_mapping, dict)
        and set(task_mapping) == set(study.task_aliases)
    )
    if not complete:
        return ["provenance evidence is incomplete"]
    assert isinstance(sources, dict)
    assert isinstance(condition_mapping, dict)
    assert isinstance(task_mapping, dict)

    pairs: list[tuple[str, str]] = []
    for condition in (study.baseline_condition, study.treatment_condition):
        source = sources.get(condition)
        mapping = condition_mapping.get(condition)
        if not isinstance(source, dict) or not isinstance(mapping, dict):
            return ["provenance evidence is incomplete"]
        revision = source.get("checkpoint_source_revision")
        tokenizer = source.get("tokenizer_revision")
        model_id = mapping.get("model_id")
        if (
            not isinstance(revision, str)
            or not revision
            or revision.startswith("<")
            or not isinstance(tokenizer, str)
            or not tokenizer
            or tokenizer.startswith("<")
            or not isinstance(model_id, str)
            or not model_id
            or model_id.startswith("<")
            or model_id == condition
        ):
            return ["provenance evidence is incomplete"]
        pairs.append((revision, tokenizer))

    for alias in study.task_aliases:
        mapping = task_mapping.get(alias)
        if (
            not isinstance(mapping, dict)
            or not isinstance(mapping.get("task_id"), str)
            or not mapping["task_id"]
            or mapping["task_id"].startswith("<")
            or mapping["task_id"] == alias
        ):
            return ["provenance evidence is incomplete"]

    if len(set(pairs)) != 1:
        return ["immutable checkpoint or tokenizer parity failed"]
    return []


def _shape_reasons(manifest: dict[str, Any], study: Study) -> list[str]:
    matrix = manifest.get("matrix")
    frozen = (
        study.baseline_condition == "bf16"
        and study.treatment_condition == "mlx-affine-int8-g64"
        and study.task_aliases == tuple(f"task-{index:02d}" for index in range(1, 6))
        and study.repetitions == (1, 2, 3, 4)
        and isinstance(matrix, dict)
        and matrix.get("execution") == "sequential"
        and matrix.get("task_order") == "alias"
        and matrix.get("condition_order") == "alternating-by-repetition"
        and matrix.get("expected_trials") == 40
    )
    return [] if frozen else ["study shape does not match frozen 40-trial protocol"]


def _task_weighted_aggregate(
    pairs: list[dict[str, Any]], fields: Iterable[str]
) -> dict[str, float | None]:
    fields = tuple(fields)
    task_means = _task_means(pairs, fields)
    return {
        field: (
            mean(float(row[field]) for row in task_means if row[field] is not None)
            if any(row[field] is not None for row in task_means)
            else None
        )
        for field in fields
    }


def _task_means(
    pairs: list[dict[str, Any]], fields: Iterable[str]
) -> list[dict[str, Any]]:
    fields = tuple(fields)
    by_task: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for pair in pairs:
        by_task[pair["task_alias"]].append(pair)
    rows: list[dict[str, Any]] = []
    for task_alias in sorted(by_task):
        row: dict[str, Any] = {"task_alias": task_alias}
        for field in fields:
            values = [float(pair[field]) for pair in by_task[task_alias] if pair.get(field) is not None]
            row[field] = mean(values) if values else None
        rows.append(row)
    return rows


def _percentile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def _task_clustered_bootstrap(
    task_means: list[dict[str, Any]],
    fields: Iterable[str],
    *,
    seed: int = 20260715,
    replicates: int = 10_000,
) -> dict[str, dict[str, Any]]:
    intervals: dict[str, dict[str, Any]] = {}
    for field_index, field in enumerate(fields):
        values = [float(row[field]) for row in task_means if row.get(field) is not None]
        if not values:
            continue
        rng = random.Random(seed + field_index)
        draws = [
            mean(rng.choice(values) for _ in range(len(values)))
            for _ in range(replicates)
        ]
        intervals[field] = {
            "lower": _percentile(draws, 0.025),
            "upper": _percentile(draws, 0.975),
            "confidence": 0.95,
            "method": "task-clustered bootstrap percentile interval",
            "seed": seed,
            "replicates": replicates,
        }
    return intervals


def _pair_trials(
    trials: list[dict[str, Any]], study: Study
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    baseline = study.baseline_condition
    treatment = study.treatment_condition
    lookup = {
        (row["task_alias"], row["repetition"], row["precision_alias"]): row
        for row in trials
    }
    primary: list[dict[str, Any]] = []
    secondary: list[dict[str, Any]] = []
    for task in study.task_aliases:
        for repetition in study.repetitions:
            left = lookup.get((task, repetition, baseline))
            right = lookup.get((task, repetition, treatment))
            if left is None or right is None:
                continue

            if (
                left["attempt_status"] in VALID_ATTEMPT_STATUSES
                and right["attempt_status"] in VALID_ATTEMPT_STATUSES
                and left["verifier_status"] == "complete"
                and right["verifier_status"] == "complete"
                and all(
                    left.get(metric) is not None and right.get(metric) is not None
                    for metric in ("f2p", "p2p")
                )
            ):
                reward_delta = None
                if left.get("reward") is not None and right.get("reward") is not None:
                    reward_delta = float(right["reward"]) - float(left["reward"])
                primary.append(
                    {
                        "task_alias": task,
                        "repetition": repetition,
                        "f2p_delta": float(right["f2p"]) - float(left["f2p"]),
                        "p2p_delta": float(right["p2p"]) - float(left["p2p"]),
                        "reward_delta": reward_delta,
                    }
                )

            if (
                left["attempt_status"] not in VALID_ATTEMPT_STATUSES
                or right["attempt_status"] not in VALID_ATTEMPT_STATUSES
            ):
                continue
            secondary_row: dict[str, Any] = {
                "task_alias": task,
                "repetition": repetition,
            }
            for field in SECONDARY_FIELDS:
                if left.get(field) is not None and right.get(field) is not None:
                    secondary_row[f"{field}_delta"] = float(right[field]) - float(left[field])
            if len(secondary_row) > 2:
                secondary.append(secondary_row)
    return primary, secondary


def analyze_manifest(manifest_path: str | Path) -> dict[str, Any]:
    """Analyze one private manifest and return sanitized trials plus a summary."""
    path = Path(manifest_path)
    manifest = _json(path)
    study = Study.from_dict(manifest.get("study", {}))
    raw_entries = manifest.get("trials")
    if not isinstance(raw_entries, list):
        raise AnalysisError("manifest.trials must be a list")

    records = [_load_trial(entry, path.parent) for entry in raw_entries]
    in_scope: list[dict[str, Any]] = []
    out_of_scope: list[dict[str, Any]] = []
    seen_keys: set[tuple[Any, ...]] = set()
    selection_metadata_complete = True

    for index, record in enumerate(records):
        mismatches = _mismatched_fields(record, study)
        if mismatches:
            out_of_scope.append(
                {"trial_index": index, "mismatched_fields": mismatches}
            )
            continue
        _validate_metrics(record, index)
        attempt = record.get("attempt")
        selected = record.get("selected_for_analysis")
        if (
            not isinstance(attempt, int)
            or isinstance(attempt, bool)
            or attempt < 1
            or not isinstance(selected, bool)
        ):
            selection_metadata_complete = False
        key = (
            record["checkpoint_alias"],
            record["architecture"],
            record["engine_alias"],
            record["scheme_alias"],
            record["task_alias"],
            record["repetition"],
            record["precision_alias"],
            record.get("attempt", 1),
        )
        if key in seen_keys:
            raise AnalysisError(f"duplicate exact trial key at manifest index {index}")
        seen_keys.add(key)
        in_scope.append(_sanitize(record))

    condition_rank = {
        study.baseline_condition: 0,
        study.treatment_condition: 1,
    }
    in_scope.sort(
        key=lambda row: (
            row["task_alias"],
            row["repetition"],
            condition_rank[row["precision_alias"]],
            row["attempt"],
        )
    )
    selected_trials = [row for row in in_scope if row["selected_for_analysis"]]

    counts = {
        "discovered": len(records),
        "in_scope": len(in_scope),
        "out_of_scope": len(out_of_scope),
        "valid_attempts": sum(
            row["attempt_status"] in VALID_ATTEMPT_STATUSES for row in in_scope
        ),
        "verifier_covered": sum(
            row["verifier_status"] == "complete"
            and row["f2p"] is not None
            and row["p2p"] is not None
            for row in in_scope
        ),
        "successful_completions": sum(
            row["attempt_status"] in VALID_ATTEMPT_STATUSES
            and row["verifier_status"] == "complete"
            and row["reward"] == 1
            for row in in_scope
        ),
    }

    attrition: Counter[str] = Counter()
    for row in in_scope:
        if row["attempt_status"] not in VALID_ATTEMPT_STATUSES:
            attrition[str(row["attempt_status"])] += 1
        elif row["attempt_status"] != "completed":
            attrition[str(row["attempt_status"])] += 1
        elif row["verifier_status"] != "complete":
            attrition[str(row["verifier_status"])] += 1
        else:
            attrition["completed"] += 1
    for category in (
        "completed",
        "model_agent_timeout",
        "model_agent_failure",
        "environment_harness_failure",
        "verifier_only_failure",
    ):
        attrition.setdefault(category, 0)

    primary_pairs, secondary_pairs = _pair_trials(selected_trials, study)
    primary_fields = ("f2p_delta", "p2p_delta", "reward_delta")
    secondary_fields = tuple(f"{field}_delta" for field in SECONDARY_FIELDS)
    primary_aggregate = _task_weighted_aggregate(primary_pairs, primary_fields)
    primary_task_means = _task_means(primary_pairs, primary_fields)
    primary_intervals = _task_clustered_bootstrap(
        primary_task_means, ("f2p_delta", "p2p_delta")
    )
    reward_pairs = [pair for pair in primary_pairs if pair["reward_delta"] is not None]
    reward_aggregate = _task_weighted_aggregate(reward_pairs, ("reward_delta",))
    reward_task_means = _task_means(reward_pairs, ("reward_delta",))
    reward_intervals = _task_clustered_bootstrap(
        reward_task_means, ("reward_delta",)
    )
    secondary_aggregate = _task_weighted_aggregate(secondary_pairs, secondary_fields)
    secondary_task_means = _task_means(secondary_pairs, secondary_fields)
    secondary_intervals = _task_clustered_bootstrap(
        secondary_task_means, secondary_fields
    )
    secondary_distributions = {
        condition: {
            field: [
                row[field]
                for row in selected_trials
                if row["precision_alias"] == condition
                and row["attempt_status"] in VALID_ATTEMPT_STATUSES
                and row.get(field) is not None
            ]
            for field in SECONDARY_FIELDS
        }
        for condition in (study.baseline_condition, study.treatment_condition)
    }

    expected_keys = {
        (task, repetition, condition)
        for task in study.task_aliases
        for repetition in study.repetitions
        for condition in study.conditions
    }
    observed_keys = {
        (row["task_alias"], row["repetition"], row["precision_alias"])
        for row in selected_trials
    }
    selected_counts = Counter(
        (row["task_alias"], row["repetition"], row["precision_alias"])
        for row in selected_trials
    )
    expected_pairs = len(study.task_aliases) * len(study.repetitions)
    reasons: list[str] = [
        *_provenance_reasons(manifest, study),
        *_shape_reasons(manifest, study),
    ]
    if not selection_metadata_complete:
        reasons.append("attempt selection metadata is incomplete")
    if any(
        row["attempt_status"] not in VALID_ATTEMPT_STATUSES for row in selected_trials
    ):
        reasons.append("selected analysis attempt is not a valid model outcome")
    if any(not _metric_counts_complete(row) for row in selected_trials):
        reasons.append("verifier metric counts are incomplete")
    if not primary_pairs:
        reasons.append("no verifier-covered primary pairs")
    if observed_keys != expected_keys:
        reasons.append("trial matrix is incomplete")
    if set(selected_counts) != expected_keys or any(
        count != 1 for count in selected_counts.values()
    ):
        reasons.append("planned cell must have exactly one selected attempt")
    if len(primary_pairs) != expected_pairs:
        reasons.append("primary matrix is incomplete")
    if len(reward_pairs) != expected_pairs:
        reasons.append("reward guardrail matrix is incomplete")

    summary = {
        "study": {
            "checkpoint_alias": study.checkpoint_alias,
            "architecture": study.architecture,
            "engine_alias": study.engine_alias,
            "conditions": [study.baseline_condition, study.treatment_condition],
            "baseline_condition": study.baseline_condition,
            "treatment_condition": study.treatment_condition,
            "task_aliases": list(study.task_aliases),
            "repetitions": list(study.repetitions),
        },
        "counts": counts,
        "attrition": dict(sorted(attrition.items())),
        "out_of_scope": out_of_scope,
        "primary": {
            "pairs": primary_pairs,
            "task_means": primary_task_means,
            "aggregate": primary_aggregate,
            "confidence_intervals": primary_intervals,
        },
        "guardrail": {
            "reward_pair_count": len(reward_pairs),
            "task_means": reward_task_means,
            "aggregate": reward_aggregate,
            "confidence_intervals": reward_intervals,
        },
        "secondary": {
            "pairs": secondary_pairs,
            "task_means": secondary_task_means,
            "paired": secondary_aggregate,
            "confidence_intervals": secondary_intervals,
            "distributions": secondary_distributions,
        },
        "publication_gate": {
            "status": "blocked" if reasons else "ready",
            "reasons": reasons,
        },
    }
    return {"trials": in_scope, "summary": summary}


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--trials-out", type=Path, required=True)
    parser.add_argument("--summary-out", type=Path, required=True)
    args = parser.parse_args(argv)

    result = analyze_manifest(args.manifest)
    _write_json(args.trials_out, result["trials"])
    _write_json(args.summary_out, result["summary"])
    print(
        f"wrote {len(result['trials'])} sanitized trials; "
        f"publication gate: {result['summary']['publication_gate']['status']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
