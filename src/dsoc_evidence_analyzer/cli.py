from __future__ import annotations

import argparse
import json
from pathlib import Path

from .analyzer import analyze_file, render_markdown, write_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dsoc-evidence",
        description="Evaluate Distributed SOC experiment CSV results against acceptance criteria.",
    )
    parser.add_argument(
        "csv_file",
        type=Path,
        help="CSV file containing controlled experiment runs",
    )
    parser.add_argument("--json-out", type=Path, help="Write full analysis as JSON")
    parser.add_argument("--markdown-out", type=Path, help="Write a human-readable Markdown report")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = analyze_file(args.csv_file)

    if args.json_out:
        write_json(result, args.json_out)
    if args.markdown_out:
        args.markdown_out.write_text(render_markdown(result), encoding="utf-8")

    print(json.dumps(result["summary"], indent=2))
    return 0 if result["summary"]["overall_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
