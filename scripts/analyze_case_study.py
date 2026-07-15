#!/usr/bin/env python3
"""Build deterministic, sanitized public evidence from a private case-study manifest."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
import json
from pathlib import Path
from statistics import mean
from typing import Any, Iterable


PUBLIC_TRIAL_FIELDS = (
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
)
SECONDARY_FIELDS = (
    "steps",
    "input_tokens",
    "output_tokens",
    "elapsed_seconds",
    "peak_context_tokens",
)
VALID_ATTEMPT_STATUSES = {"valid", "model_agent_timeout", "model_agent_failure"}


class AnalysisError(ValueError):
    """The private manifest cannot support a deterministic public analysis."""


@dataclass(frozen=True)
class Study:
    checkpoint_alias: str
    architecture: str
    engine_alias: str
    conditions: dict[str, dict[str, Any]]
    task_aliases: tuple[str, ...]
    repetitions: tuple[int, ...]

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "Study":
        required = (
            "checkpoint_alias",
            "architecture",
            "engine_alias",
            "conditions",
            "task_aliases",
            "repetitions",
        )
        missing = [field for field in required if field not in value]
        if missing:
            raise AnalysisError(f"study is missing fields: {', '.join(missing)}")
        conditions = value["conditions"]
        if not isinstance(conditions, dict) or len(conditions) != 2:
            raise AnalysisError("study.conditions must define exactly two conditions")
        return cls(
            checkpoint_alias=str(value["checkpoint_alias"]),
            architecture=str(value["architecture"]),
            engine_alias=str(value["engine_alias"]),
            conditions=conditions,
            task_aliases=tuple(str(item) for item in value["task_aliases"]),
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
            "valid" if result else "environment_harness_failure",
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
    return {field: record.get(field) for field in PUBLIC_TRIAL_FIELDS}


def _task_weighted_aggregate(
    pairs: list[dict[str, Any]], fields: Iterable[str]
) -> dict[str, float | None]:
    by_task: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for pair in pairs:
        by_task[pair["task_alias"]].append(pair)
    aggregate: dict[str, float | None] = {}
    for field in fields:
        task_means = [
            mean(float(row[field]) for row in rows if row.get(field) is not None)
            for rows in by_task.values()
            if any(row.get(field) is not None for row in rows)
        ]
        aggregate[field] = mean(task_means) if task_means else None
    return aggregate


def _pair_trials(
    trials: list[dict[str, Any]], study: Study
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    condition_order = tuple(study.conditions)
    baseline, treatment = condition_order
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

            if all(left.get(field) is not None and right.get(field) is not None for field in ("f2p", "p2p", "reward")):
                primary.append(
                    {
                        "task_alias": task,
                        "repetition": repetition,
                        "f2p_delta": float(right["f2p"]) - float(left["f2p"]),
                        "p2p_delta": float(right["p2p"]) - float(left["p2p"]),
                        "reward_delta": float(right["reward"]) - float(left["reward"]),
                    }
                )

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

    for index, record in enumerate(records):
        mismatches = _mismatched_fields(record, study)
        if mismatches:
            out_of_scope.append(
                {"trial_index": index, "mismatched_fields": mismatches}
            )
            continue
        key = (
            record["checkpoint_alias"],
            record["architecture"],
            record["engine_alias"],
            record["scheme_alias"],
            record["task_alias"],
            record["repetition"],
            record["precision_alias"],
        )
        if key in seen_keys:
            raise AnalysisError(f"duplicate exact trial key at manifest index {index}")
        seen_keys.add(key)
        in_scope.append(_sanitize(record))

    condition_rank = {name: index for index, name in enumerate(study.conditions)}
    in_scope.sort(
        key=lambda row: (
            row["task_alias"],
            row["repetition"],
            condition_rank[row["precision_alias"]],
        )
    )

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
            row["verifier_status"] == "complete" and row["reward"] == 1
            for row in in_scope
        ),
    }

    attrition: Counter[str] = Counter()
    for row in in_scope:
        if row["attempt_status"] != "valid":
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

    primary_pairs, secondary_pairs = _pair_trials(in_scope, study)
    primary_fields = ("f2p_delta", "p2p_delta", "reward_delta")
    secondary_fields = tuple(f"{field}_delta" for field in SECONDARY_FIELDS)
    primary_aggregate = _task_weighted_aggregate(primary_pairs, primary_fields)
    secondary_aggregate = _task_weighted_aggregate(secondary_pairs, secondary_fields)

    expected_keys = {
        (task, repetition, condition)
        for task in study.task_aliases
        for repetition in study.repetitions
        for condition in study.conditions
    }
    observed_keys = {
        (row["task_alias"], row["repetition"], row["precision_alias"])
        for row in in_scope
    }
    expected_pairs = len(study.task_aliases) * len(study.repetitions)
    reasons: list[str] = []
    if not primary_pairs:
        reasons.append("no verifier-covered primary pairs")
    if observed_keys != expected_keys:
        reasons.append("trial matrix is incomplete")
    if len(primary_pairs) != expected_pairs:
        reasons.append("primary matrix is incomplete")

    summary = {
        "study": {
            "checkpoint_alias": study.checkpoint_alias,
            "architecture": study.architecture,
            "engine_alias": study.engine_alias,
            "conditions": list(study.conditions),
            "task_aliases": list(study.task_aliases),
            "repetitions": list(study.repetitions),
        },
        "counts": counts,
        "attrition": dict(sorted(attrition.items())),
        "out_of_scope": out_of_scope,
        "primary": {
            "pairs": primary_pairs,
            "aggregate": primary_aggregate,
        },
        "secondary": {
            "pairs": secondary_pairs,
            "paired": secondary_aggregate,
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
