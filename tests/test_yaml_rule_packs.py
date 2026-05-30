import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RULES_DIR = REPO_ROOT / "rules"
EXECUTABLE_RULE_PACKS = [
    RULES_DIR / "governed_delivery_rules.yaml",
    RULES_DIR / "launch_blocker_rules.yaml",
    RULES_DIR / "evidence_rules.yaml",
    RULES_DIR / "ticket_builder_rules.yaml",
]
SUPPORTED_OPERATORS = {"all", "any", "field", "equals", "not_equals", "contains_any", "min_length"}
SUPPORTED_SEVERITIES = {"low", "medium", "high", "critical"}
ID_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9-]+-\d{3}$")


def test_every_yaml_rule_pack_has_identifiable_rule_ids():
    yaml_files = sorted(RULES_DIR.glob("*.yaml"))
    assert yaml_files, "No YAML rule packs found"

    for path in yaml_files:
        text = path.read_text(encoding="utf-8")
        ids = re.findall(r"\bid:\s*['\"]?([A-Za-z0-9_-]+)['\"]?", text)
        assert ids, f"No rule IDs found in {path}"
        assert len(ids) == len(set(ids)), f"Duplicate rule IDs found in {path}"


def test_executable_rule_packs_are_json_compatible_yaml():
    for path in EXECUTABLE_RULE_PACKS:
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(payload, list), f"{path} must contain a list of rules"
        assert payload, f"{path} must contain at least one rule"


def test_executable_rules_have_required_fields_and_valid_shapes():
    required_fields = {
        "id",
        "name",
        "category",
        "severity",
        "applies_when",
        "finding",
        "required_action",
        "launch_blocker",
        "required_evidence",
    }

    all_ids = []
    for path in EXECUTABLE_RULE_PACKS:
        rules = json.loads(path.read_text(encoding="utf-8"))
        for rule in rules:
            missing = required_fields - set(rule)
            assert not missing, f"{path} rule {rule.get('id')} missing fields: {sorted(missing)}"

            assert ID_PATTERN.match(rule["id"]), f"Invalid rule ID format: {rule['id']}"
            assert rule["severity"] in SUPPORTED_SEVERITIES
            assert isinstance(rule["applies_when"], dict)
            assert isinstance(rule["launch_blocker"], bool)
            assert isinstance(rule["required_evidence"], list)
            assert all(isinstance(item, str) and item for item in rule["required_evidence"])
            assert isinstance(rule.get("recommended_ticket", {}), dict)

            if "recommended_ticket" in rule:
                ticket = rule["recommended_ticket"]
                for field in ["title", "owner_role", "purpose"]:
                    assert ticket.get(field), f"{rule['id']} recommended_ticket missing {field}"

            validate_condition_tree(rule["applies_when"], rule["id"])
            all_ids.append(rule["id"])

    assert len(all_ids) == len(set(all_ids)), "Executable rule IDs must be unique across rule packs"


def validate_condition_tree(condition, rule_id):
    assert isinstance(condition, dict), f"{rule_id} condition must be an object"
    unknown_keys = set(condition) - SUPPORTED_OPERATORS
    assert not unknown_keys, f"{rule_id} has unsupported condition keys: {sorted(unknown_keys)}"

    if "all" in condition:
        assert isinstance(condition["all"], list) and condition["all"], f"{rule_id} all must be a non-empty list"
        for child in condition["all"]:
            validate_condition_tree(child, rule_id)
        return

    if "any" in condition:
        assert isinstance(condition["any"], list) and condition["any"], f"{rule_id} any must be a non-empty list"
        for child in condition["any"]:
            validate_condition_tree(child, rule_id)
        return

    assert condition.get("field"), f"{rule_id} leaf condition must include field"
    operator_count = sum(1 for op in ["equals", "not_equals", "contains_any", "min_length"] if op in condition)
    assert operator_count == 1, f"{rule_id} leaf condition must include exactly one supported operator"

    if "contains_any" in condition:
        assert isinstance(condition["contains_any"], list) and condition["contains_any"], f"{rule_id} contains_any must be non-empty list"
    if "min_length" in condition:
        assert isinstance(condition["min_length"], int) and condition["min_length"] >= 0, f"{rule_id} min_length must be non-negative int"
