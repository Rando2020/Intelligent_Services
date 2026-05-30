from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FORGE_APP = REPO_ROOT / "apps" / "jira-forge-governed-delivery"


def test_jira_forge_scaffold_files_exist():
    expected_files = [
        "manifest.yml",
        "package.json",
        "README.md",
        "src/index.js",
        "src/resolvers.js",
        "src/static/index.html",
        "src/static/app.js",
        "src/static/styles.css",
    ]

    for relative_path in expected_files:
        assert (FORGE_APP / relative_path).exists(), f"Missing Forge scaffold file: {relative_path}"


def test_jira_forge_scaffold_uses_dry_run_issue_payloads():
    resolvers = (FORGE_APP / "src" / "resolvers.js").read_text(encoding="utf-8")
    assert "dryRun: true" in resolvers
    assert "No Jira issues were created" in resolvers
    assert "preparedIssues" in resolvers
    assert "analyzeIntake" in resolvers


def test_jira_forge_manifest_declares_project_page_and_issue_panel():
    manifest = (FORGE_APP / "manifest.yml").read_text(encoding="utf-8")
    assert "jira:projectPage" in manifest
    assert "jira:issuePanel" in manifest
    assert "Governed Delivery Agent" in manifest
