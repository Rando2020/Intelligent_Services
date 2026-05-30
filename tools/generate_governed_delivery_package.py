#!/usr/bin/env python3
"""
Generate the complete governed delivery demo package.

This wrapper runs the core governed_delivery_cli pipeline, generates a YAML
rule match report, injects rule-driven controls, generates a platform control
profile report, injects platform-specific tickets/evidence, and then adds Jira,
ADO, Rally, and Asana CSV exports.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import governed_delivery_cli
from platform_exporters import write_all_platform_exports
from platform_profile_augmenter import augment_package as augment_with_platform_profiles
from platform_profile_detector import write_platform_report
from rule_loader import write_rule_report_from_files
from rule_match_augmenter import augment_package as augment_with_rule_matches


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROFILE_DIR = REPO_ROOT / "platform_profiles"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate governed delivery scorecards, rule matches, platform profiles, ticket hierarchy, evidence packet, and exports."
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
    parser.add_argument(
        "--profile-dir",
        default=str(DEFAULT_PROFILE_DIR),
        help="Directory containing platform profile JSON files.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_dir = Path(args.output_dir)

    governed_delivery_cli.run(input_path, output_dir, title=args.title)

    rule_outputs = write_rule_report_from_files(output_dir / "normalized_intake.json", output_dir)
    rule_augmented_outputs = augment_with_rule_matches(output_dir)

    platform_outputs = write_platform_report(input_path, output_dir, Path(args.profile_dir))
    platform_augmented_outputs = augment_with_platform_profiles(output_dir)

    extra_exports = write_all_platform_exports(output_dir)

    print("YAML rule match outputs generated:")
    for path in rule_outputs:
        print(f"- {path}")

    if rule_augmented_outputs:
        print("YAML rule controls injected into package:")
        for path in rule_augmented_outputs:
            print(f"- {path}")

    print("Platform profile outputs generated:")
    for path in platform_outputs:
        print(f"- {path}")

    if platform_augmented_outputs:
        print("Platform profile controls injected into package:")
        for path in platform_augmented_outputs:
            print(f"- {path}")

    print("Additional platform exports generated:")
    for path in extra_exports:
        print(f"- {path}")


if __name__ == "__main__":
    main()
