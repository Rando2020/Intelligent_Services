#!/usr/bin/env python3
"""
Rule Match Augmenter

Injects YAML-driven matched rules into generated governed delivery package files:
- scorecard.json / scorecard.md
- generated_ticket_hierarchy.json / generated_ticket_hierarchy.md
- evidence_packet.json / evidence_packet.md
- jira_export.csv

ADO/Rally/Asana exports should be regenerated after augmentation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import governed_delivery_cli


RULE_EPIC_ID = "EPIC-RULES-001"
RULE_EPIC_TITLE = "Rule-Driven Governance Controls"


def load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def first_initiative_id(tickets: list[dict[str, Any]]) -> str:
    for ticket in tickets:
        if ticket.get("work_item_type") == "initiative":
            return str(ticket.get("external_id", "INIT-001"))
    return "INIT-001"


def base_ticket_defaults(tickets: list[dict[str, Any]]) -> dict[str, Any]:
    first = tickets[0] if tickets else {}
    return {
        "platform": "generic",
        "request_type": first.get("request_type", "rule_governance"),
        "program": first.get("program", "Unknown"),
        "client": first.get("client", "Unknown"),
        "systems_impacted": first.get("systems_impacted", []),
        "data_involved": first.get("data_involved", []),
        "phi_flag": bool(first.get("phi_flag", False)),
        "pii_flag": bool(first.get("pii_flag", False)),
        "pci_flag": bool(first.get("pci_flag", False)),
        "external_recipient": bool(first.get("external_recipient", False)),
        "file_movement_required": bool(first.get("file_movement_required", False)),
        "delivery_method": first.get("delivery_method", "unknown"),
        "legal_review_required": bool(first.get("legal_review_required", True)),
        "security_review_required": bool(first.get("security_review_required", True)),
        "data_governance_required": bool(first.get("data_governance_required", True)),
        "qa_required": bool(first.get("qa_required", True)),
        "soc2_impact": first.get("soc2_impact", ["Access Control", "Change Management", "Processing Integrity", "Confidentiality"]),
        "risk_rating": "L4",
        "timeline_risk_rating": first.get("timeline_risk_rating", "L2"),
        "ticket_quality_rating": first.get("ticket_quality_rating", "L2"),
        "priority": "high",
        "assignee": "TBD",
        "due_date": first.get("due_date", ""),
        "sprint_or_iteration": "",
        "dependencies": [],
        "blockers": [],
        "evidence_links": [],
        "status": "New",
        "export_ready": True,
    }


def build_rule_epic(parent_id: str, defaults: dict[str, Any]) -> dict[str, Any]:
    return {
        "external_id": RULE_EPIC_ID,
        "parent_external_id": parent_id,
        "work_item_type": "epic",
        "title": RULE_EPIC_TITLE,
        "description": "Apply matched YAML-driven governance rules to the generated delivery package.",
        "business_context": "Matched governance rules make findings, blockers, tickets, and evidence traceable to configurable rule IDs.",
        "user_story": "As an accountable delivery team, I need rule-driven controls so that governance outputs are configurable and auditable.",
        "acceptance_criteria": [
            "Matched rules are visible in the rule match report.",
            "Launch-blocking rules are reflected in launch blockers and evidence requirements.",
            "Recommended rule tickets are created where applicable.",
            "Rule IDs remain visible for auditability and configuration."
        ],
        "definition_of_done": [
            "Rule match report is generated.",
            "Rule-driven tickets are created or marked not applicable.",
            "Rule-driven evidence is attached or explicitly marked not applicable.",
            "Open rule-driven blockers are resolved or accepted by authorized owners."
        ],
        "owner_role": "Product / PM / Governance Owner",
        "evidence_required": ["rule_match_report", "rule_driven_evidence"],
        "launch_blocker": True,
        **defaults,
    }


def build_rule_ticket(rule: dict[str, Any], index: int, defaults: dict[str, Any]) -> dict[str, Any]:
    recommended = rule.get("recommended_ticket", {}) or {}
    evidence = rule.get("required_evidence", [])
    return {
        "external_id": f"RULE-STORY-{index:03d}",
        "parent_external_id": RULE_EPIC_ID,
        "work_item_type": "story",
        "title": recommended.get("title") or f"Resolve matched governance rule {rule.get('id')}",
        "description": f"Rule {rule.get('id')}: {rule.get('name')}\n\nFinding: {rule.get('finding')}\n\nRequired action: {rule.get('required_action')}",
        "business_context": "This ticket was generated from a matched configurable governance rule.",
        "user_story": f"As an accountable owner, I need to resolve rule {rule.get('id')} so that the work can proceed with evidence-backed governance.",
        "acceptance_criteria": [
            f"Rule {rule.get('id')} is reviewed for applicability.",
            "Required action is completed or marked not applicable with rationale.",
            "Required evidence is attached.",
            "If the rule is launch-blocking, launch does not proceed until the blocker is resolved or formally accepted."
        ],
        "definition_of_done": [
            "Rule applicability is documented.",
            "Required evidence is attached or marked not applicable.",
            "Launch blockers are resolved or accepted by authorized owners.",
            "Ticket links back to the rule match report."
        ],
        "owner_role": recommended.get("owner_role", "Governance Owner"),
        "evidence_required": evidence,
        "launch_blocker": bool(rule.get("launch_blocker", False)),
        "source_rule_id": rule.get("id"),
        **defaults,
    }


def evidence_item_exists(packet: dict[str, Any], area: str, artifact: str) -> bool:
    for item in packet.get("evidence_items", []):
        if item.get("evidence_area") == area and item.get("required_artifact") == artifact:
            return True
    return False


def add_rule_evidence(packet: dict[str, Any], rule_report: dict[str, Any]) -> None:
    evidence_items = packet.setdefault("evidence_items", [])
    open_blockers = packet.setdefault("open_blockers", [])

    for rule in rule_report.get("matched_rules", []):
        area = f"Matched rule: {rule.get('id')}"
        for artifact in rule.get("required_evidence", []):
            if not evidence_item_exists(packet, area, artifact):
                evidence_items.append({
                    "evidence_area": area,
                    "required_artifact": artifact,
                    "owner_role": rule.get("recommended_ticket", {}).get("owner_role", "Governance Owner"),
                    "status": "missing",
                    "launch_blocker": bool(rule.get("launch_blocker", False)),
                    "evidence_link": "",
                    "decision_notes": "",
                    "approved_by": "",
                    "approved_at": "",
                    "expires_or_review_by": "",
                })
        if rule.get("launch_blocker"):
            blocker = f"Rule {rule.get('id')}: {rule.get('finding')}"
            if blocker not in open_blockers:
                open_blockers.append(blocker)

    if any(rule.get("launch_blocker") for rule in rule_report.get("matched_rules", [])):
        packet["launch_decision"] = "blocked"


def add_rule_findings(scorecard: dict[str, Any], rule_report: dict[str, Any]) -> None:
    findings = scorecard.setdefault("findings", [])
    launch_blockers = scorecard.setdefault("launch_blockers", [])
    existing_finding_ids = {item.get("id") for item in findings}
    existing_blockers = {item.get("blocker") for item in launch_blockers}

    for rule in rule_report.get("matched_rules", []):
        finding_id = f"RULE-{rule.get('id')}"
        if finding_id not in existing_finding_ids:
            findings.append({
                "id": finding_id,
                "severity": rule.get("severity", "medium"),
                "finding": rule.get("finding"),
                "required_action": rule.get("required_action"),
                "mapped_rule_id": rule.get("id"),
                "evidence_required": rule.get("required_evidence", []),
            })

        if rule.get("launch_blocker"):
            blocker = f"Rule {rule.get('id')}: {rule.get('finding')}"
            if blocker not in existing_blockers:
                launch_blockers.append({
                    "blocker": blocker,
                    "required_resolution": rule.get("required_action"),
                    "owner_role": rule.get("recommended_ticket", {}).get("owner_role", "Governance Owner"),
                    "evidence_required": rule.get("required_evidence", []),
                })

    if rule_report.get("matched_rules"):
        scorecard["matched_rule_count"] = rule_report.get("matched_rule_count", 0)
        scorecard["matched_rule_ids"] = [rule.get("id") for rule in rule_report.get("matched_rules", [])]


def augment_package(output_dir: Path) -> list[Path]:
    ticket_path = output_dir / "generated_ticket_hierarchy.json"
    evidence_path = output_dir / "evidence_packet.json"
    scorecard_path = output_dir / "scorecard.json"
    rule_report_path = output_dir / "rule_match_report.json"

    if not rule_report_path.exists():
        return []

    tickets: list[dict[str, Any]] = load_json(ticket_path)
    evidence_packet: dict[str, Any] = load_json(evidence_path)
    scorecard: dict[str, Any] = load_json(scorecard_path)
    rule_report: dict[str, Any] = load_json(rule_report_path)

    matched_rules = rule_report.get("matched_rules", [])
    if not matched_rules:
        return []

    defaults = base_ticket_defaults(tickets)
    parent_id = first_initiative_id(tickets)

    if not any(ticket.get("external_id") == RULE_EPIC_ID for ticket in tickets):
        tickets.append(build_rule_epic(parent_id, defaults))

    existing_rule_ids = {ticket.get("source_rule_id") for ticket in tickets if ticket.get("source_rule_id")}
    next_index = 1
    for rule in matched_rules:
        if rule.get("id") in existing_rule_ids:
            continue
        tickets.append(build_rule_ticket(rule, next_index, defaults))
        next_index += 1

    add_rule_evidence(evidence_packet, rule_report)
    add_rule_findings(scorecard, rule_report)

    write_json(ticket_path, tickets)
    write_json(evidence_path, evidence_packet)
    write_json(scorecard_path, scorecard)

    ticket_objects = [dict_to_ticket(ticket) for ticket in tickets]
    (output_dir / "generated_ticket_hierarchy.md").write_text(governed_delivery_cli.render_tickets_md(ticket_objects), encoding="utf-8")
    (output_dir / "evidence_packet.md").write_text(governed_delivery_cli.render_evidence_md(evidence_packet), encoding="utf-8")
    (output_dir / "scorecard.md").write_text(governed_delivery_cli.render_scorecard_md(scorecard), encoding="utf-8")
    governed_delivery_cli.write_jira_csv(output_dir / "jira_export.csv", ticket_objects)

    return [
        scorecard_path,
        output_dir / "scorecard.md",
        ticket_path,
        output_dir / "generated_ticket_hierarchy.md",
        evidence_path,
        output_dir / "evidence_packet.md",
        output_dir / "jira_export.csv",
    ]


def dict_to_ticket(data: dict[str, Any]) -> governed_delivery_cli.Ticket:
    fields = governed_delivery_cli.Ticket.__dataclass_fields__.keys()
    filtered = {field: data.get(field) for field in fields}

    list_fields = [
        "acceptance_criteria",
        "definition_of_done",
        "systems_impacted",
        "data_involved",
        "soc2_impact",
        "dependencies",
        "blockers",
        "evidence_required",
        "evidence_links",
    ]
    for field in list_fields:
        if filtered.get(field) is None:
            filtered[field] = []

    bool_fields = [
        "phi_flag",
        "pii_flag",
        "pci_flag",
        "external_recipient",
        "file_movement_required",
        "legal_review_required",
        "security_review_required",
        "data_governance_required",
        "qa_required",
        "launch_blocker",
        "export_ready",
    ]
    for field in bool_fields:
        filtered[field] = bool(filtered.get(field))

    string_defaults = {
        "external_id": "",
        "parent_external_id": "",
        "platform": "generic",
        "work_item_type": "task",
        "title": "",
        "description": "",
        "business_context": "",
        "user_story": "",
        "request_type": "rule_governance",
        "program": "Unknown",
        "client": "Unknown",
        "delivery_method": "unknown",
        "risk_rating": "L4",
        "timeline_risk_rating": "L2",
        "ticket_quality_rating": "L2",
        "priority": "high",
        "owner_role": "Governance Owner",
        "assignee": "TBD",
        "due_date": "",
        "sprint_or_iteration": "",
        "status": "New",
    }
    for field, default in string_defaults.items():
        if filtered.get(field) is None:
            filtered[field] = default

    return governed_delivery_cli.Ticket(**filtered)
