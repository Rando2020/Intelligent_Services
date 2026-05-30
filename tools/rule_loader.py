#!/usr/bin/env python3
"""
Rule Loader and Matcher

Dependency-free first pass at a YAML-driven governance rule engine.

Important prototype convention:
- Rule files use .yaml extension for product readability.
- File contents are JSON-compatible YAML so the standard library json parser can load them.

Supported conditions:
- equals
- not_equals
- contains_any
- min_length
- all
- any

The matcher accepts a normalized intake dictionary and returns matched rules.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RULE_FILES = [
    REPO_ROOT / "rules" / "governed_delivery_rules.yaml",
    REPO_ROOT / "rules" / "launch_blocker_rules.yaml",
    REPO_ROOT / "rules" / "evidence_rules.yaml",
    REPO_ROOT / "rules" / "ticket_builder_rules.yaml",
]


class RuleLoaderError(ValueError):
    """Raised when a rule file cannot be loaded or validated."""


def load_rule_file(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Rule file not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuleLoaderError(
            f"Rule file {path} must be JSON-compatible YAML for the dependency-free prototype: {exc}"
        ) from exc
    if not isinstance(data, list):
        raise RuleLoaderError(f"Rule file {path} must contain a list of rule objects")
    for rule in data:
        validate_rule(rule, path)
    return data


def load_rules(rule_files: list[Path] | None = None) -> list[dict[str, Any]]:
    files = rule_files or DEFAULT_RULE_FILES
    rules: list[dict[str, Any]] = []
    for path in files:
        rules.extend(load_rule_file(path))
    return rules


def validate_rule(rule: dict[str, Any], path: Path) -> None:
    required = ["id", "name", "category", "severity", "applies_when", "finding", "required_action"]
    missing = [field for field in required if field not in rule]
    if missing:
        raise RuleLoaderError(f"Rule in {path} is missing required fields: {missing}")
    if "required_evidence" not in rule:
        rule["required_evidence"] = []
    if "launch_blocker" not in rule:
        rule["launch_blocker"] = False


def get_field_value(context: dict[str, Any], field: str) -> Any:
    current: Any = context
    for part in field.split("."):
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current


def evaluate_condition(condition: dict[str, Any], context: dict[str, Any]) -> bool:
    if "all" in condition:
        return all(evaluate_condition(item, context) for item in condition["all"])
    if "any" in condition:
        return any(evaluate_condition(item, context) for item in condition["any"])

    field = condition.get("field")
    if not field:
        return False
    value = get_field_value(context, field)

    if "equals" in condition:
        return value == condition["equals"]
    if "not_equals" in condition:
        return value != condition["not_equals"]
    if "contains_any" in condition:
        expected = [str(item).lower() for item in condition["contains_any"]]
        if isinstance(value, list):
            actual = [str(item).lower() for item in value]
            return any(item in actual for item in expected)
        if isinstance(value, str):
            lowered = value.lower()
            return any(item in lowered for item in expected)
        return False
    if "min_length" in condition:
        try:
            return len(value or []) >= int(condition["min_length"])
        except TypeError:
            return False

    return False


def match_rules(context: dict[str, Any], rules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    matched = []
    for rule in rules:
        if evaluate_condition(rule.get("applies_when", {}), context):
            matched.append(rule)
    return matched


def build_rule_report(context: dict[str, Any], rules: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    loaded_rules = rules or load_rules()
    matched = match_rules(context, loaded_rules)
    return {
        "rule_count": len(loaded_rules),
        "matched_rule_count": len(matched),
        "matched_rules": [summarize_rule(rule) for rule in matched],
        "summary": build_summary(matched),
    }


def summarize_rule(rule: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": rule.get("id"),
        "name": rule.get("name"),
        "category": rule.get("category"),
        "severity": rule.get("severity"),
        "finding": rule.get("finding"),
        "required_action": rule.get("required_action"),
        "launch_blocker": bool(rule.get("launch_blocker", False)),
        "required_evidence": rule.get("required_evidence", []),
        "recommended_ticket": rule.get("recommended_ticket", {}),
    }


def build_summary(matched: list[dict[str, Any]]) -> str:
    if not matched:
        return "No YAML-driven governance rules matched the normalized intake."
    blocker_count = sum(1 for rule in matched if rule.get("launch_blocker"))
    return f"Matched {len(matched)} governance rules, including {blocker_count} launch-blocking rules."


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    output = []
    output.append("| " + " | ".join(headers) + " |")
    output.append("|" + "|".join(["---" for _ in headers]) + "|")
    for row in rows:
        output.append("| " + " | ".join(str(cell).replace("\n", "<br>") for cell in row) + " |")
    return "\n".join(output)


def render_rule_report_md(report: dict[str, Any]) -> str:
    rows = [
        [
            rule["id"],
            rule["name"],
            rule["category"],
            rule["severity"],
            "Yes" if rule["launch_blocker"] else "No",
            ", ".join(rule.get("required_evidence", [])),
        ]
        for rule in report.get("matched_rules", [])
    ]

    return f"""# YAML Rule Match Report

## Summary

{report.get("summary", "")}

| Field | Value |
|---|---|
| Rules Loaded | {report.get("rule_count", 0)} |
| Rules Matched | {report.get("matched_rule_count", 0)} |

## Matched Rules

{markdown_table(["Rule ID", "Name", "Category", "Severity", "Launch Blocker", "Required Evidence"], rows) if rows else "No rules matched."}

## Agent Instruction

Matched rules should be included in scorecard findings, launch blockers, generated tickets, and evidence packet requirements. Rule IDs should remain visible so outputs are auditable and configurable by organization.
"""


def write_rule_report_from_files(normalized_intake_path: Path, output_dir: Path) -> list[Path]:
    context = json.loads(normalized_intake_path.read_text(encoding="utf-8"))
    report = build_rule_report(context)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "rule_match_report.json"
    md_path = output_dir / "rule_match_report.md"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(render_rule_report_md(report), encoding="utf-8")
    return [json_path, md_path]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Match YAML-driven governance rules against normalized intake JSON.")
    parser.add_argument("--normalized-intake", required=True, help="Path to normalized_intake.json")
    parser.add_argument("--output-dir", required=True, help="Directory for rule match report outputs")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    outputs = write_rule_report_from_files(Path(args.normalized_intake), Path(args.output_dir))
    print("Rule match report generated:")
    for path in outputs:
        print(f"- {path}")


if __name__ == "__main__":
    main()
