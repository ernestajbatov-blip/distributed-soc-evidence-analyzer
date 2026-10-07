import subprocess
import sys
from pathlib import Path


def test_cli_generates_outputs(tmp_path: Path) -> None:
    root = Path(__file__).parents[1]
    json_out = tmp_path / "report.json"
    md_out = tmp_path / "report.md"
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "dsoc_evidence_analyzer",
            str(root / "data" / "sample_runs.csv"),
            "--json-out",
            str(json_out),
            "--markdown-out",
            str(md_out),
        ],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert json_out.exists()
    assert md_out.exists()
    assert "Overall result: PASS" in md_out.read_text(encoding="utf-8")
