import csv
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEMO_INTAKE = REPO_ROOT / "examples" / "free_trial" / "healthcare_file_mover_delivery" / "messy_intake.md"
PACKAGE_SCRIPT = REPO_ROOT / "tools" / "generate_governed_delivery_package.py"


def test_governed_delivery_package_generation(tmp_path):
    output_dir = tmp_path / "generated_package"

    result = subprocess.run(
        [
            sys.executable,
            str(PACKAGE_SCRIPT),
            "--input",
            str(DEMO_INTAKE),
            "--output-dir",
            str(output_dir),
            "--title",
            "Centene LAMP Governed File Delivery",
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Governed delivery package generated" in result.stdout
    assert "YAML rule match outputs generated" in result.stdout
    assert "YAML rule controls injected into package" in result.stdout
    assert "Additional platform exports generated" in result.stdout
    assert "Platform profile outputs generated" in result.stdout

    expected_files = [
        "normalized_intake.json",
        "scorecard.json",
        "scorecard.md",
        "rule_match_report.json",
        "rule_match_report.md",
        "generated_ticket_hierarchy.json",
        "generated_ticket_hierarchy.md",
        "jira_export.csv",
        "ado_export.csv",
        "rally_export.csv",
        "asana_export.csv",
        "platform_profile_report.json",
        "platform_profile_report.md",
        "evidence_packet.json",
        "evidence_packet.md",
        "launch_readiness_summary.md",
    ]

    for file_name in expected_files:
        assert (output_dir / file_name).exists(), f"Missing generated file: {file_name}"

    scorecard = json.loads((output_dir / "scorecard.json").read_text(encoding="utf-8"))
    assert scorecard["overall_rating"] == "at_risk"
    assert scorecard["launch_position"] == "not_launchable"
    assert len(scorecard["launch_blockers"]) >= 1
    assert scorecard["matched_rule_count"] >= 1
    assert "LAUNCH-BLOCKER-002" in scorecard["matched_rule_ids"]

    rule_report = json.loads((output_dir / "rule_match_report.json").read_text(encoding="utf-8"))
    assert rule_report["rule_count"] >= 1
    assert rule_report["matched_rule_count"] >= 1
    matched_rule_ids = {rule["id"] for rule in rule_report["matched_rules"]}
    assert "GOV-DELIVERY-002" in matched_rule_ids
    assert "LAUNCH-BLOCKER-002" in matched_rule_ids
    assert "TICKET-BUILDER-002" in matched_rule_ids

    platform_report = json.loads((output_dir / "platform_profile_report.json").read_text(encoding="utf-8"))
    assert platform_report["detected_platform_count"] >= 1
    assert "maturity_scale" in platform_report
    assert any(item["level"] == "L6" for item in platform_report["maturity_scale"])
    assert any(
        profile["id"] == "PLATFORM-GENERIC-FILE-MOVER"
        for profile in platform_report["detected_profiles"]
    )

    tickets = json.loads((output_dir / "generated_ticket_hierarchy.json").read_text(encoding="utf-8"))
    assert len(tickets) >= 10
    assert any("file mover" in ticket["title"].lower() for ticket in tickets)
    assert any(ticket["launch_blocker"] for ticket in tickets)
    assert any(ticket.get("source_rule_id") == "TICKET-BUILDER-002" for ticket in tickets)

    evidence_packet = json.loads((output_dir / "evidence_packet.json").read_text(encoding="utf-8"))
    assert any(item["evidence_area"] == "Matched rule: LAUNCH-BLOCKER-002" for item in evidence_packet["evidence_items"])

    for csv_name in ["jira_export.csv", "ado_export.csv", "rally_export.csv", "asana_export.csv"]:
        with (output_dir / csv_name).open("r", encoding="utf-8", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            assert rows, f"No rows generated for {csv_name}"
            fieldnames = reader.fieldnames or []
            for required_field in [
                "Risk Rating",
                "Legal Review Required",
                "Security Review Required",
                "Data Governance Required",
                "File Movement Required",
                "Launch Blocker",
            ]:
                assert required_field in fieldnames, f"{required_field} missing from {csv_name}"
