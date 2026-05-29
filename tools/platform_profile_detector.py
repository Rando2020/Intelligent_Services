#!/usr/bin/env python3
"""
Platform Profile Detector

Detects tools/platforms mentioned in messy intake and applies platform-specific
control profiles from platform_profiles/*.profile.json.

This is dependency-free and intentionally simple for the prototype stage.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROFILE_DIR = REPO_ROOT / "platform_profiles"


MATURITY_SCALE = [
    ("L0", "Unknown", "System/platform is named but governance controls are not identified."),
    ("L1", "Ad hoc", "Engineers use the platform, but controls depend on tribal knowledge."),
    ("L2", "Documented", "Basic owners, systems, data types, and workflows are documented."),
    ("L3", "Controlled", "Required reviews, access controls, QA, and delivery gates exist."),
    ("L4", "Evidence-backed", "Controls are documented with evidence, logs, approvals, and validation."),
    ("L5", "Automated / enforced", "Controls are built into workflows, permissions, CI/CD, jobs, or platform policies."),
    ("L6", "Adaptive / org-specific", "Organization-specific rules, control mappings, exception logic, and continuous monitoring apply."),
]


def load_profiles(profile_dir: Path = DEFAULT_PROFILE_DIR) -> list[dict[str, Any]]:
    profiles = []
    for path in sorted(profile_dir.glob("*.profile.json")):
        profiles.append(json.loads(path.read_text(encoding="utf-8")))
    return profiles


def detect_profiles(text: str, profiles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    lowered = text.lower()
    detected = []
    for profile in profiles:
        matched_keywords = [
            keyword for keyword in profile.get("detection_keywords", [])
            if keyword.lower() in lowered
        ]
        if matched_keywords:
            enriched = dict(profile)
            enriched["matched_keywords"] = sorted(set(matched_keywords))
            enriched["suggested_current_level"] = suggest_current_level(text, profile)
            detected.append(enriched)

    if not detected and any(word in lowered for word in ["file", "deliver", "delivery", "outbound", "recipient", "upload", "route"]):
        generic = next((p for p in profiles if p.get("id") == "PLATFORM-GENERIC-FILE-MOVER"), None)
        if generic:
            enriched = dict(generic)
            enriched["matched_keywords"] = ["inferred file delivery"]
            enriched["suggested_current_level"] = "L1"
            detected.append(enriched)

    return detected


def suggest_current_level(text: str, profile: dict[str, Any]) -> str:
    lowered = text.lower()
    if any(term in lowered for term in ["not confirmed", "unknown", "still need", "missing"]):
        return "L1"
    if any(term in lowered for term in ["approved", "validated", "reviewed", "evidence", "attached"]):
        return "L3"
    if profile.get("platform_type") in {"file_mover", "api_integration"}:
        return "L1"
    return "L2"


def build_platform_report(text: str, profile_dir: Path = DEFAULT_PROFILE_DIR) -> dict[str, Any]:
    profiles = load_profiles(profile_dir)
    detected = detect_profiles(text, profiles)
    return {
        "detected_platform_count": len(detected),
        "maturity_scale": [
            {"level": level, "name": name, "meaning": meaning}
            for level, name, meaning in MATURITY_SCALE
        ],
        "detected_profiles": [summarize_profile(profile) for profile in detected],
        "summary": build_summary(detected),
    }


def summarize_profile(profile: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": profile.get("id"),
        "name": profile.get("name"),
        "platform_type": profile.get("platform_type"),
        "matched_keywords": profile.get("matched_keywords", []),
        "suggested_current_level": profile.get("suggested_current_level", "L0"),
        "max_level": profile.get("maturity_scale", {}).get("max_level", "L6"),
        "supports_l6_org_specific": profile.get("maturity_scale", {}).get("supports_l6_org_specific", False),
        "default_risk_triggers": profile.get("default_risk_triggers", []),
        "required_checks": profile.get("required_checks", []),
        "required_evidence": profile.get("required_evidence", []),
        "launch_blockers": profile.get("launch_blockers", []),
        "recommended_tickets": profile.get("recommended_tickets", []),
    }


def build_summary(detected: list[dict[str, Any]]) -> str:
    if not detected:
        return "No platform-specific profiles were detected. Use generic governance checks and ask for systems, tools, delivery layers, and data platforms."
    names = ", ".join(profile.get("name", "Unknown") for profile in detected)
    return f"Detected platform profiles: {names}. Apply platform-aware controls in addition to baseline governance checks."


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    output = []
    output.append("| " + " | ".join(headers) + " |")
    output.append("|" + "|".join(["---" for _ in headers]) + "|")
    for row in rows:
        output.append("| " + " | ".join(str(cell).replace("\n", "<br>") for cell in row) + " |")
    return "\n".join(output)


def render_platform_report_md(report: dict[str, Any]) -> str:
    profiles = report.get("detected_profiles", [])
    profile_rows = [
        [
            profile["id"],
            profile["name"],
            profile["platform_type"],
            ", ".join(profile.get("matched_keywords", [])),
            profile.get("suggested_current_level", "L0"),
            profile.get("max_level", "L6"),
        ]
        for profile in profiles
    ]
    maturity_rows = [
        [item["level"], item["name"], item["meaning"]]
        for item in report.get("maturity_scale", [])
    ]

    sections = [
        "# Platform Control Profile Report\n\n",
        "## Summary\n\n",
        report.get("summary", ""),
        "\n\n## L0-L6 Maturity Scale\n\n",
        markdown_table(["Level", "Name", "Meaning"], maturity_rows),
        "\n\n## Detected Profiles\n\n",
    ]

    if profile_rows:
        sections.append(markdown_table(["Profile ID", "Name", "Type", "Matched Keywords", "Suggested Current Level", "Max Level"], profile_rows))
    else:
        sections.append("No platform profiles detected.\n")

    for profile in profiles:
        sections.append(f"\n\n## {profile['name']}\n\n")
        sections.append(f"**Profile ID:** {profile['id']}  \n")
        sections.append(f"**Platform Type:** {profile['platform_type']}  \n")
        sections.append(f"**Suggested Current Level:** {profile.get('suggested_current_level', 'L0')}  \n")
        sections.append(f"**Supports L6 Org-Specific Controls:** {'Yes' if profile.get('supports_l6_org_specific') else 'No'}\n")

        sections.append("\n### Required Checks\n")
        sections.extend([f"- {item}\n" for item in profile.get("required_checks", [])])

        sections.append("\n### Required Evidence\n")
        sections.extend([f"- {item}\n" for item in profile.get("required_evidence", [])])

        sections.append("\n### Launch Blockers\n")
        sections.extend([f"- {item}\n" for item in profile.get("launch_blockers", [])])

        sections.append("\n### Recommended Tickets\n")
        for ticket in profile.get("recommended_tickets", []):
            sections.append(f"- **{ticket.get('title')}** ({ticket.get('owner_role')}): {ticket.get('purpose')}\n")

    sections.append("\n## Agent Instruction\n\n")
    sections.append(
        "When a platform profile is detected, the agent should add the profile's checks, evidence, and launch blockers to the baseline scorecard, ticket hierarchy, and evidence packet. "
        "Engineers should not need to know governance language; the system should translate named tools into required controls.\n"
    )

    return "".join(sections)


def write_platform_report(input_path: Path, output_dir: Path, profile_dir: Path = DEFAULT_PROFILE_DIR) -> list[Path]:
    text = input_path.read_text(encoding="utf-8")
    report = build_platform_report(text, profile_dir=profile_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "platform_profile_report.json"
    md_path = output_dir / "platform_profile_report.md"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(render_platform_report_md(report), encoding="utf-8")
    return [json_path, md_path]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Detect platform control profiles from messy intake.")
    parser.add_argument("--input", required=True, help="Path to messy intake markdown or text file.")
    parser.add_argument("--output-dir", default="generated/governed_delivery", help="Directory for platform profile report outputs.")
    parser.add_argument("--profile-dir", default=str(DEFAULT_PROFILE_DIR), help="Directory containing *.profile.json files.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    outputs = write_platform_report(Path(args.input), Path(args.output_dir), Path(args.profile_dir))
    print("Platform profile report generated:")
    for path in outputs:
        print(f"- {path}")


if __name__ == "__main__":
    main()
