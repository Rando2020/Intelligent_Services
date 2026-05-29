import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STACK_INTAKE = REPO_ROOT / "examples" / "free_trial" / "platform_stack_governance" / "messy_intake.md"
PACKAGE_SCRIPT = REPO_ROOT / "tools" / "generate_governed_delivery_package.py"


def test_platform_stack_profile_detection(tmp_path):
    output_dir = tmp_path / "platform_stack_package"

    result = subprocess.run(
        [
            sys.executable,
            str(PACKAGE_SCRIPT),
            "--input",
            str(STACK_INTAKE),
            "--output-dir",
            str(output_dir),
            "--title",
            "Platform Stack Governed Delivery Demo",
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Platform profile outputs generated" in result.stdout
    assert "Platform profile controls injected into package" in result.stdout

    report_path = output_dir / "platform_profile_report.json"
    assert report_path.exists()

    report = json.loads(report_path.read_text(encoding="utf-8"))
    detected_ids = {profile["id"] for profile in report["detected_profiles"]}

    expected_ids = {
        "PLATFORM-SNOWFLAKE",
        "PLATFORM-DBT",
        "PLATFORM-SFTP-MFT",
        "PLATFORM-REPORTING-BI",
        "PLATFORM-API-INTEGRATION",
        "PLATFORM-GENERIC-FILE-MOVER",
    }

    missing = expected_ids - detected_ids
    assert not missing, f"Missing expected platform profiles: {sorted(missing)}"

    assert any(item["level"] == "L6" for item in report["maturity_scale"])

    snowflake = next(profile for profile in report["detected_profiles"] if profile["id"] == "PLATFORM-SNOWFLAKE")
    assert "masking_policy_reviewed" in snowflake["required_checks"]
    assert "row_access_policy_reviewed" in snowflake["required_checks"]

    reporting = next(profile for profile in report["detected_profiles"] if profile["id"] == "PLATFORM-REPORTING-BI")
    assert "row_level_security_reviewed" in reporting["required_checks"]

    api = next(profile for profile in report["detected_profiles"] if profile["id"] == "PLATFORM-API-INTEGRATION")
    assert "payload_schema_reviewed" in api["required_checks"]

    tickets = json.loads((output_dir / "generated_ticket_hierarchy.json").read_text(encoding="utf-8"))
    ticket_titles = {ticket["title"] for ticket in tickets}
    assert "Platform Control Profile Governance" in ticket_titles
    assert "Review Snowflake data classification and object tags" in ticket_titles
    assert "Review dbt model ownership, tests, and lineage" in ticket_titles
    assert "Validate reporting access and row-level security" in ticket_titles
    assert "Review API endpoint, authentication, and payload contract" in ticket_titles

    evidence_packet = json.loads((output_dir / "evidence_packet.json").read_text(encoding="utf-8"))
    evidence_areas = {item["evidence_area"] for item in evidence_packet["evidence_items"]}
    assert "Platform profile: Snowflake Control Profile" in evidence_areas
    assert "Platform profile: dbt Transformation Control Profile" in evidence_areas
    assert "Platform profile: Tableau and Power BI Reporting Control Profile" in evidence_areas
