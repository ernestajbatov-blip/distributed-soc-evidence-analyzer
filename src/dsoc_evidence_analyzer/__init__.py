"""Distributed SOC experiment evidence analyzer."""

from .analyzer import analyze_file, evaluate_run, summarize_runs
from .models import AcceptanceCriteria, ExperimentRun

__all__ = [
    "AcceptanceCriteria",
    "ExperimentRun",
    "analyze_file",
    "evaluate_run",
    "summarize_runs",
]

__version__ = "0.1.0"
