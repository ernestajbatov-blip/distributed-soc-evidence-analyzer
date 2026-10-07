from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AcceptanceCriteria:
    """Acceptance targets inherited from the Distributed SOC pilot."""

    minimum_completeness_pct: float = 99.9
    maximum_search_p95_seconds: float = 5.0
    maximum_recovery_seconds: float = 300.0
    minimum_detection_pass_ratio: float = 0.90
    require_all_critical_detections: bool = True
    maximum_reproducibility_deviation_pct: float = 10.0


@dataclass(frozen=True)
class ExperimentRun:
    """One controlled SOC experiment run."""

    run_id: str
    generated_events: int
    indexed_unique_events: int
    duplicate_events: int
    search_p95_seconds: float
    recovery_seconds: float
    sustained_eps: float
    detection_passed: int
    detection_total: int
    critical_detection_failed: int


@dataclass(frozen=True)
class RunEvaluation:
    run_id: str
    completeness_pct: float
    detection_pass_ratio: float
    completeness_ok: bool
    search_latency_ok: bool
    recovery_ok: bool
    detection_ok: bool
    passed: bool


@dataclass(frozen=True)
class ExperimentSummary:
    run_count: int
    passed_runs: int
    median_eps: float
    max_eps_deviation_pct: float
    reproducibility_ok: bool
    overall_pass: bool
