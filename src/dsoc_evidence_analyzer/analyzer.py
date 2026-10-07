from __future__ import annotations

import csv
import json
import statistics
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

from .models import AcceptanceCriteria, ExperimentRun, ExperimentSummary, RunEvaluation


REQUIRED_COLUMNS = {
    "run_id",
    "generated_events",
    "indexed_unique_events",
    "duplicate_events",
    "search_p95_seconds",
    "recovery_seconds",
    "sustained_eps",
    "detection_passed",
    "detection_total",
    "critical_detection_failed",
}


def _nonnegative_int(value: str, field: str) -> int:
    result = int(value)
    if result < 0:
        raise ValueError(f"{field} must be non-negative")
    return result


def _nonnegative_float(value: str, field: str) -> float:
    result = float(value)
    if result < 0:
        raise ValueError(f"{field} must be non-negative")
    return result


def load_runs(path: str | Path) -> list[ExperimentRun]:
    """Load experiment runs from a CSV file with explicit schema validation."""

    csv_path = Path(path)
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("CSV file has no header")
        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            raise ValueError(f"CSV is missing required columns: {', '.join(sorted(missing))}")

        runs: list[ExperimentRun] = []
        for row_number, row in enumerate(reader, start=2):
            try:
                run = ExperimentRun(
                    run_id=row["run_id"].strip(),
                    generated_events=_nonnegative_int(row["generated_events"], "generated_events"),
                    indexed_unique_events=_nonnegative_int(
                        row["indexed_unique_events"], "indexed_unique_events"
                    ),
                    duplicate_events=_nonnegative_int(row["duplicate_events"], "duplicate_events"),
                    search_p95_seconds=_nonnegative_float(
                        row["search_p95_seconds"], "search_p95_seconds"
                    ),
                    recovery_seconds=_nonnegative_float(
                        row["recovery_seconds"], "recovery_seconds"
                    ),
                    sustained_eps=_nonnegative_float(row["sustained_eps"], "sustained_eps"),
                    detection_passed=_nonnegative_int(row["detection_passed"], "detection_passed"),
                    detection_total=_nonnegative_int(row["detection_total"], "detection_total"),
                    critical_detection_failed=_nonnegative_int(
                        row["critical_detection_failed"], "critical_detection_failed"
                    ),
                )
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid data on CSV row {row_number}: {exc}") from exc

            if not run.run_id:
                raise ValueError(f"run_id is empty on CSV row {row_number}")
            if run.generated_events == 0:
                raise ValueError(f"generated_events must be greater than zero on row {row_number}")
            if run.detection_total == 0:
                raise ValueError(f"detection_total must be greater than zero on row {row_number}")
            if run.indexed_unique_events > run.generated_events:
                raise ValueError(
                    f"indexed_unique_events cannot exceed generated_events on row {row_number}"
                )
            if run.detection_passed > run.detection_total:
                raise ValueError(
                    f"detection_passed cannot exceed detection_total on row {row_number}"
                )
            runs.append(run)

    if not runs:
        raise ValueError("CSV contains no experiment runs")
    return runs


def evaluate_run(
    run: ExperimentRun, criteria: AcceptanceCriteria | None = None
) -> RunEvaluation:
    """Evaluate one run against the pilot acceptance criteria."""

    criteria = criteria or AcceptanceCriteria()
    completeness_pct = (run.indexed_unique_events / run.generated_events) * 100.0
    detection_pass_ratio = run.detection_passed / run.detection_total

    completeness_ok = completeness_pct >= criteria.minimum_completeness_pct
    search_latency_ok = run.search_p95_seconds <= criteria.maximum_search_p95_seconds
    recovery_ok = run.recovery_seconds <= criteria.maximum_recovery_seconds
    detection_ok = detection_pass_ratio >= criteria.minimum_detection_pass_ratio
    if criteria.require_all_critical_detections:
        detection_ok = detection_ok and run.critical_detection_failed == 0

    passed = completeness_ok and search_latency_ok and recovery_ok and detection_ok
    return RunEvaluation(
        run_id=run.run_id,
        completeness_pct=completeness_pct,
        detection_pass_ratio=detection_pass_ratio,
        completeness_ok=completeness_ok,
        search_latency_ok=search_latency_ok,
        recovery_ok=recovery_ok,
        detection_ok=detection_ok,
        passed=passed,
    )


def _deviation_from_median_pct(values: Iterable[float]) -> tuple[float, float]:
    values_list = list(values)
    median = statistics.median(values_list)
    if median == 0:
        return median, 0.0 if all(value == 0 for value in values_list) else float("inf")
    deviation = max(abs(value - median) / median * 100.0 for value in values_list)
    return median, deviation


def summarize_runs(
    runs: list[ExperimentRun], criteria: AcceptanceCriteria | None = None
) -> tuple[list[RunEvaluation], ExperimentSummary]:
    """Evaluate all runs and summarize throughput reproducibility."""

    if not runs:
        raise ValueError("At least one run is required")
    criteria = criteria or AcceptanceCriteria()
    evaluations = [evaluate_run(run, criteria) for run in runs]
    median_eps, max_deviation = _deviation_from_median_pct(run.sustained_eps for run in runs)
    reproducibility_ok = max_deviation <= criteria.maximum_reproducibility_deviation_pct
    passed_runs = sum(item.passed for item in evaluations)
    overall_pass = passed_runs == len(evaluations) and reproducibility_ok

    return evaluations, ExperimentSummary(
        run_count=len(runs),
        passed_runs=passed_runs,
        median_eps=median_eps,
        max_eps_deviation_pct=max_deviation,
        reproducibility_ok=reproducibility_ok,
        overall_pass=overall_pass,
    )


def analyze_file(path: str | Path) -> dict[str, object]:
    """Analyze a CSV file and return a JSON-serializable result."""

    runs = load_runs(path)
    evaluations, summary = summarize_runs(runs)
    return {
        "source": str(Path(path)),
        "criteria": asdict(AcceptanceCriteria()),
        "runs": [asdict(item) for item in evaluations],
        "summary": asdict(summary),
    }


def render_markdown(result: dict[str, object]) -> str:
    summary = result["summary"]
    assert isinstance(summary, dict)
    runs = result["runs"]
    assert isinstance(runs, list)

    lines = [
        "# Distributed SOC Experiment Evidence Report",
        "",
        f"Source: `{result['source']}`",
        "",
        "## Summary",
        "",
        f"- Runs: {summary['run_count']}",
        f"- Passed runs: {summary['passed_runs']}",
        f"- Median sustained EPS: {summary['median_eps']:.2f}",
        f"- Maximum EPS deviation from median: {summary['max_eps_deviation_pct']:.2f}%",
        f"- Reproducibility: {'PASS' if summary['reproducibility_ok'] else 'FAIL'}",
        f"- Overall result: {'PASS' if summary['overall_pass'] else 'FAIL'}",
        "",
        "## Per-run evaluation",
        "",
        "| Run | Completeness | Search | Recovery | Detection | Result |",
        "|---|---:|:---:|:---:|:---:|:---:|",
    ]
    for item in runs:
        assert isinstance(item, dict)
        lines.append(
            "| {run_id} | {completeness_pct:.3f}% | {search_latency_ok} | "
            "{recovery_ok} | {detection_ok} | {passed} |".format(**item)
        )
    lines.append("")
    return "\n".join(lines)


def write_json(result: dict[str, object], path: str | Path) -> None:
    Path(path).write_text(json.dumps(result, indent=2), encoding="utf-8")
