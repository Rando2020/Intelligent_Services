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
    assert "Additional platform exports generated" in result.stdout

    expected_files = [
        "normalized_intake.json",
        "scorecard.json",
        "scorecard.md",
        "generated_ticket_hierarchy.json",
        "generated_ticket_hierarchy.md",
        "jira_export.csv",
        "ado_export.csv",
        "rally_export.csv",
        "asana_export.csv",
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

    tickets = json.loads((output_dir / "generated_ticket_hierarchy.json").read_text(encoding="utf-8"))
    assert len(tickets) >= 10
    assert any("file mover" in ticket["title"].lower() for ticket in tickets)
    assert any(ticket["launch_blocker"] for ticket in tickets)

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
