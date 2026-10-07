# Distributed SOC Experiment Evidence Analyzer

Research-software module for **Assignment 3: Software Development and Integration**. The project continues the Distributed SOC pilot from Assignments 1 and 2 and evaluates controlled experiment results against measurable acceptance criteria.

**Repository:** https://github.com/ernestajbatov-blip/distributed-soc-evidence-analyzer  
**CI/CD:** https://github.com/ernestajbatov-blip/distributed-soc-evidence-analyzer/actions

## Research purpose

The previous project defines measurable targets for ingest completeness, search latency, node-recovery time, detection validation and reproducibility. This module converts those criteria into deterministic, version-controlled checks so repeated experiment results can be evaluated consistently.

Default criteria:

- ingest completeness >= 99.9%;
- search p95 <= 5 s;
- recovery <= 300 s;
- detection pass ratio >= 90% and no failed critical scenario;
- maximum sustained-EPS deviation from the median across repeated runs <= 10%.

The sample dataset is synthetic. The repository does not contain production logs, secrets or confidential organizational data.

## Technology choice

- **Python 3.11+** — portable, readable and widely used for scientific data processing.
- **Python standard library** — CSV, JSON and statistics processing without runtime third-party dependencies.
- **pytest** — automated unit and CLI testing.
- **Ruff** — static linting.
- **Git + GitHub** — distributed version control, repository hosting and issue tracking.
- **GitHub Actions** — CI on Python 3.11, 3.12 and 3.13 plus a build artifact after successful pushes to `main`.

## Repository structure

```text
.
├── .github/
│   ├── ISSUE_TEMPLATE/
│   └── workflows/ci.yml
├── data/sample_runs.csv
├── docs/repository-and-ci.md
├── src/dsoc_evidence_analyzer/
├── tests/
├── LICENSE
├── pyproject.toml
└── README.md
```

## Input format

```text
run_id,generated_events,indexed_unique_events,duplicate_events,
search_p95_seconds,recovery_seconds,sustained_eps,
detection_passed,detection_total,critical_detection_failed
```

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## Run the analyzer

```bash
dsoc-evidence data/sample_runs.csv --json-out report.json --markdown-out report.md
```

Or:

```bash
python -m dsoc_evidence_analyzer data/sample_runs.csv
```

Exit code is `0` when all run-level checks and the reproducibility check pass; otherwise it is `2`.

## Tests and linting

```bash
ruff check .
pytest
```

## CI/CD

The workflow is stored in [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

On pushes and pull requests to `main`, GitHub Actions checks Python 3.11–3.13, installs development dependencies, runs Ruff and pytest, and after a successful push builds a wheel and source archive as a workflow artifact.

This is continuous integration plus a basic continuous-delivery output. The workflow deliberately does not deploy research software automatically to a production SOC.

## Issue tracking

The repository includes issue templates and initial improvement issues for latency-distribution input, schema validation and optional HTML visualization.

## Scientific software practices

- explicit inputs and acceptance rules;
- deterministic calculations;
- versioned implementation;
- automated regression tests;
- synthetic publishable example data;
- no production credentials or logs in Git;
- documented environment setup and rerun procedure.

## License

MIT License. See [LICENSE](LICENSE).
