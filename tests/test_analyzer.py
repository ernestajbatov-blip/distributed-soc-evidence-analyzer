from pathlib import Path

import pytest

from dsoc_evidence_analyzer.analyzer import analyze_file, evaluate_run, load_runs, summarize_runs
from dsoc_evidence_analyzer.models import ExperimentRun


def good_run(run_id: str = "r1", eps: float = 1000.0) -> ExperimentRun:
    return ExperimentRun(
        run_id=run_id,
        generated_events=3_600_000,
        indexed_unique_events=3_597_000,
        duplicate_events=200,
        search_p95_seconds=4.2,
        recovery_seconds=210.0,
        sustained_eps=eps,
        detection_passed=10,
        detection_total=10,
        critical_detection_failed=0,
    )


def test_good_run_passes() -> None:
    result = evaluate_run(good_run())
    assert result.passed
    assert result.completeness_pct == pytest.approx(99.916666, rel=1e-5)


def test_critical_detection_failure_fails_run() -> None:
    run = good_run()
    run = ExperimentRun(**{**run.__dict__, "critical_detection_failed": 1})
    result = evaluate_run(run)
    assert not result.detection_ok
    assert not result.passed


def test_reproducibility_fails_when_eps_varies_over_ten_percent() -> None:
    runs = [good_run("r1", 1000), good_run("r2", 1005), good_run("r3", 1250)]
    _, summary = summarize_runs(runs)
    assert not summary.reproducibility_ok
    assert not summary.overall_pass


def test_load_runs_rejects_missing_columns(tmp_path: Path) -> None:
    source = tmp_path / "bad.csv"
    source.write_text("run_id,generated_events\nr1,100\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing required columns"):
        load_runs(source)


def test_sample_file_passes() -> None:
    sample = Path(__file__).parents[1] / "data" / "sample_runs.csv"
    result = analyze_file(sample)
    assert result["summary"]["overall_pass"] is True
