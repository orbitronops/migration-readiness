"""CLI: python -m orbitronops_migration assess <app.json> [--format text|json|markdown] [--output file]"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow running from a checkout without installing: `src` on sys.path.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from orbitronops_migration.models import App  # noqa: E402
from orbitronops_migration.report import render_json, render_markdown, render_text  # noqa: E402
from orbitronops_migration.scoring import assess  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="orbitronops-migration",
        description="Migration readiness assessment for EKS (OrbitronOps demo).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    assess_cmd = sub.add_parser("assess", help="Assess one application JSON file.")
    assess_cmd.add_argument("file", help="Path to an application JSON file. See examples/.")
    assess_cmd.add_argument("--format", choices=["text", "json", "markdown"], default="text")
    assess_cmd.add_argument("--output", default=None, help="Write the report to this file instead of stdout.")

    args = parser.parse_args(argv)

    if args.command == "assess":
        try:
            data = json.loads(Path(args.file).read_text(encoding="utf-8"))
        except FileNotFoundError:
            print(f"error: file not found: {args.file}", file=sys.stderr)
            return 2
        except json.JSONDecodeError as exc:
            print(f"error: invalid JSON in {args.file}: {exc}", file=sys.stderr)
            return 2

        result = assess(App.from_dict(data))
        if args.format == "json":
            output = render_json(result)
        elif args.format == "markdown":
            output = render_markdown(result)
        else:
            output = render_text(result)

        if args.output:
            Path(args.output).write_text(output + "\n", encoding="utf-8")
            print(f"Report written to: {args.output}")
        else:
            print(output)
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
