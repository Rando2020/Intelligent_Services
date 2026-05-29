#!/usr/bin/env python3
"""
Generate the complete governed delivery demo package.

This wrapper runs the core governed_delivery_cli pipeline and then adds
ADO, Rally, and Asana CSV exports from the generated generic ticket JSON.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import governed_delivery_cli
from platform_exporters import write_all_platform_exports


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate governed delivery scorecards, ticket hierarchy, evidence packet, and platform exports."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to messy intake markdown, text, or JSON file.",
    )
    parser.add_argument(
        "--output-dir",
        default="generated/governed_delivery",
        help="Directory where generated artifacts should be written.",
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Optional request title override.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    governed_delivery_cli.run(Path(args.input), output_dir, title=args.title)
    extra_exports = write_all_platform_exports(output_dir)
    print("Additional platform exports generated:")
    for path in extra_exports:
        print(f"- {path}")


if __name__ == "__main__":
    main()
