#!/usr/bin/env python3
"""
Governed Delivery CLI

A dependency-free prototype that converts messy delivery intake into:
- normalized_intake.json
- scorecard.json / scorecard.md
- generated_ticket_hierarchy.json / generated_ticket_hierarchy.md
- jira_export.csv
- evidence_packet.json / evidence_packet.md
- launch_readiness_summary.md

This is an operational governance support tool. It does not provide legal,
security, privacy, or compliance approval.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


RATING_LABELS = {
    "L0": "Unknown",
    "L1": "Assumed",
    "L2": "Draft / At risk",
    "L3": "Validated",
    "L4": "Controlled",
    "L5": "Automated and auditable",
}

DELIVERY_METHOD_KEYWORDS = {
    "managed_file_transfer": ["moveit", "mft", "managed file transfer", "goanywhere", "kiteworks", "cleo", "sterling", "axway"],
    "sftp": ["sftp", "secure ftp"],
    "ftps": ["ftps"],
    "api": ["api", "endpoint", "rest", "graphql"],
    "webhook": ["webhook"],
    "cloud_storage": ["s3", "azure blob", "gcs", "cloud storage", "bucket", "container"],
    "client_portal": ["client portal", "portal upload", "payer portal", "vendor portal"],
    "reporting_export": ["tableau", "power bi", "looker", "report export", "dashboard export", "scheduled report"],
    "secure_email": ["secure email", "encrypted email", "email attachment"],
    "shared_folder": ["sharepoint", "onedrive", "google drive", "box", "dropbox", "shared folder"],
    "manual_upload": ["manual upload", "local upload", "upload manually"],
}

SENSITIVE_DATA_KEYWORDS = {
    "phi": ["phi", "patient", "member", "claims", "eligibility", "medication", "adherence", "pharmacy", "clinical"],
    "pii": ["pii", "name", "email", "phone", "address", "dob", "ssn", "member id"],
    "pci": ["pci", "card", "pan", "cvv", "payment"],
    "credentials_or_secrets": ["password", "token", "api key", "private key", "secret"],
    "claims": ["claims"],
    "eligibility": ["eligibility"],
    "medication": ["medication", "drug", "rx"],
    "client_confidential": ["client", "partner", "confidential"],
}

MISSING_PHRASES = {
    "legal_review_confirmed": ["legal approval not confirmed", "legal has approved", "legal approval", "legal review"],
    "data_governance_review_confirmed": ["field list approval", "final field list", "data governance", "minimum necessary"],
    "security_review_confirmed": ["security approval", "security review", "access review"],
    "destination_confirmed": ["destination folder", "destination endpoint", "final delivery folder", "endpoint"],
    "recipient_access_confirmed": ["recipient access", "who should receive access", "recipient allowlist"],
    "production_equivalent_test_completed": ["test delivery", "production-equivalent", "production equivalent"],
    "runbook_confirmed": ["runbook"],
    "monitoring_confirmed": ["monitoring", "alerting"],
}


@dataclass
class Intake:
    request_title: str
    business_goal: str
    request_type: str = "data_delivery"
    client_or_partner: str = "Unknown"
    program_or_workstream: str = "Unknown"
    desired_launch_date: str = "Unknown"
    is_contractual_date: bool = False
    source_of_request: str = "unknown"
    systems_impacted: list[str] = field(default_factory=list)
    data_types: list[str] = field(default_factory=list)
    contains_phi: bool = False
    contains_pii: bool = False
    contains_pci: bool = False
    contains_credentials_or_secrets: bool = False
    external_recipient: bool = False
    file_movement_required: bool = False
    delivery_method: str = "unknown"
    delivery_tool_name: str = ""
    source_system: str = ""
    destination_system: str = ""
    destination_confirmed: bool = False
    recipient_access_confirmed: bool = False
    legal_review_confirmed: bool = False
    security_review_confirmed: bool = False
    data_governance_review_confirmed: bool = False
    qa_review_confirmed: bool = False
    production_equivalent_test_completed: bool = False
    monitoring_confirmed: bool = False
    runbook_confirmed: bool = False
    known_dependencies: list[str] = field(default_factory=list)
    known_approvals: list[str] = field(default_factory=list)
    unknowns: list[str] = field(default_factory=list)
    raw_intake_text: str = ""


@dataclass
class CategoryScore:
    category: str
    score: int
    rating: str
    meaning: str
    required_action: str


@dataclass
class Finding:
    id: str
    severity: str
    finding: str
    required_action: str
    mapped_rule_id: str = ""
    evidence_required: list[str] = field(default_factory=list)


@dataclass
class LaunchBlocker:
    blocker: str
    required_resolution: str
    owner_role: str
    evidence_required: list[str] = field(default_factory=list)


@dataclass
class Ticket:
    external_id: str
    parent_external_id: str
    platform: str
    work_item_type: str
    title: str
    description: str
    business_context: str
    user_story: str
    acceptance_criteria: list[str]
    definition_of_done: list[str]
    request_type: str
    program: str
    client: str
    systems_impacted: list[str]
    data_involved: list[str]
    phi_flag: bool
    pii_flag: bool
    pci_flag: bool
    external_recipient: bool
    file_movement_required: bool
    delivery_method: str
    legal_review_required: bool
    security_review_required: bool
    data_governance_required: bool
    qa_required: bool
    soc2_impact: list[str]
    risk_rating: str
    timeline_risk_rating: str
    ticket_quality_rating: str
    priority: str
    owner_role: str
    assignee: str
    due_date: str
    sprint_or_iteration: str
    dependencies: list[str]
    blockers: list[str]
    evidence_required: list[str]
    evidence_links: list[str]
    launch_blocker: bool
    status: str
    export_ready: bool


def read_input(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    return path.read_text(encoding="utf-8")


def contains_any(text: str, keywords: Iterable[str]) -> bool:
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in keywords)


def detect_delivery_method(text: str) -> str:
    lowered = text.lower()
    for method, keywords in DELIVERY_METHOD_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            return method
    if contains_any(lowered, ["file", "deliver", "outbound", "upload", "transfer", "route"]):
        return "unknown"
    return "not_applicable"


def detect_client(text: str) -> str:
    table_match = re.search(r"\|\s*Client\s*\|\s*([^|\n]+)\|", text, flags=re.IGNORECASE)
    if table_match:
        return table_match.group(1).strip()
    patterns = [
        r"onboard\s+([A-Z][A-Za-z0-9_-]+)",
        r"for\s+([A-Z][A-Za-z0-9_-]+)\s+for\s+weekly",
        r"client\s+([A-Z][A-Za-z0-9_-]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    return "Unknown"


def detect_program(text: str) -> str:
    table_match = re.search(r"\|\s*Program\s*\|\s*([^|\n]+)\|", text, flags=re.IGNORECASE)
    if table_match:
        return table_match.group(1).strip()
    known_programs = ["LAMP", "HEDIS", "Core", "My Programs", "Measure Hosting", "EDS"]
    for program in known_programs:
        if program.lower() in text.lower():
            return program
    return "Unknown"


def detect_launch_date(text: str) -> str:
    table_match = re.search(r"\|\s*Target launch date\s*\|\s*([^|\n]+)\|", text, flags=re.IGNORECASE)
    if table_match:
        return table_match.group(1).strip()
    match = re.search(r"by\s+([A-Z][a-z]+\s+\d{1,2}(?:,\s*\d{4})?)", text)
    if match:
        return match.group(1).strip()
    match = re.search(r"(\d{4}-\d{2}-\d{2})", text)
    if match:
        return match.group(1)
    return "Unknown"


def detect_data_types(text: str) -> list[str]:
    detected: list[str] = []
    for data_type, keywords in SENSITIVE_DATA_KEYWORDS.items():
        if contains_any(text, keywords):
            detected.append(data_type)
    return sorted(set(detected))


def infer_boolean_confirmation(text: str, field_name: str) -> bool:
    lowered = text.lower()
    negative_patterns = [
        "not confirmed",
        "not yet confirmed",
        "still need to confirm",
        "unknown",
        "missing",
        "not complete",
        "not completed",
    ]

    keywords = MISSING_PHRASES.get(field_name, [])
    if not keywords:
        return False

    if any(keyword in lowered for keyword in keywords):
        window_hit = any(pattern in lowered for pattern in negative_patterns)
        if window_hit:
            return False
        if any(phrase in lowered for phrase in ["approved", "confirmed", "completed", "done"]):
            return True

    return False


def normalize_intake(text: str, title: str | None = None) -> Intake:
    data_types = detect_data_types(text)
    delivery_method = detect_delivery_method(text)
    external_recipient = contains_any(text, ["external", "client", "partner", "vendor", "outbound", "delivered", "delivery"])
    file_movement_required = delivery_method != "not_applicable" or contains_any(text, ["file", "outbound", "deliver", "delivery", "upload", "transfer"])

    client = detect_client(text)
    program = detect_program(text)
    launch_date = detect_launch_date(text)

    unknowns = []
    unknown_map = {
        "legal_review_confirmed": "Legal approval or permitted-use decision",
        "data_governance_review_confirmed": "Final approved field list and minimum necessary review",
        "security_review_confirmed": "Security/access review",
        "destination_confirmed": "Approved destination, endpoint, folder, portal, bucket, report, or mailbox",
        "recipient_access_confirmed": "Recipient allowlist and access permissions",
        "production_equivalent_test_completed": "Production-equivalent test delivery",
        "runbook_confirmed": "Operational runbook",
        "monitoring_confirmed": "Monitoring and alerting",
    }

    confirmations = {
        field_name: infer_boolean_confirmation(text, field_name)
        for field_name in unknown_map
    }

    for field_name, label in unknown_map.items():
        if not confirmations[field_name]:
            unknowns.append(label)

    request_title = title or f"{client} {program} governed external delivery"
    business_goal = (
        f"Deliver {program} output for {client} through a governed external delivery process."
        if client != "Unknown" or program != "Unknown"
        else "Deliver requested output through a governed delivery process."
    )

    return Intake(
        request_title=request_title,
        business_goal=business_goal,
        request_type="data_delivery" if file_movement_required else "unknown",
        client_or_partner=client,
        program_or_workstream=program,
        desired_launch_date=launch_date,
        systems_impacted=sorted(set(["source data platform", "file mover / delivery layer", "QA environment"])),
        data_types=data_types,
        contains_phi="phi" in data_types or any(dt in data_types for dt in ["claims", "eligibility", "medication"]),
        contains_pii="pii" in data_types or "phi" in data_types,
        contains_pci="pci" in data_types,
        contains_credentials_or_secrets="credentials_or_secrets" in data_types,
        external_recipient=external_recipient,
        file_movement_required=file_movement_required,
        delivery_method=delivery_method,
        delivery_tool_name="",
        destination_confirmed=confirmations["destination_confirmed"],
        recipient_access_confirmed=confirmations["recipient_access_confirmed"],
        legal_review_confirmed=confirmations["legal_review_confirmed"],
        security_review_confirmed=confirmations["security_review_confirmed"],
        data_governance_review_confirmed=confirmations["data_governance_review_confirmed"],
        production_equivalent_test_completed=confirmations["production_equivalent_test_completed"],
        monitoring_confirmed=confirmations["monitoring_confirmed"],
        runbook_confirmed=confirmations["runbook_confirmed"],
        known_dependencies=[],
        known_approvals=[],
        unknowns=unknowns,
        raw_intake_text=text,
    )


def score_category_scores(intake: Intake) -> list[CategoryScore]:
    file_mover_rating = "L1" if intake.file_movement_required and not intake.destination_confirmed else "L3"
    if intake.file_movement_required and intake.destination_confirmed and intake.recipient_access_confirmed and intake.production_equivalent_test_completed:
        file_mover_rating = "L4"

    data_rating = "L4" if intake.contains_phi or intake.contains_pii or intake.external_recipient else "L2"
    timeline_rating = "L2" if intake.desired_launch_date != "Unknown" and len(intake.unknowns) >= 4 else "L3"
    intake_rating = "L2" if len(intake.unknowns) >= 4 else "L3"
    ticket_rating = "L2" if len(intake.unknowns) >= 4 else "L3"

    return [
        CategoryScore(
            category="Intake Quality",
            score=65 if intake_rating == "L2" else 78,
            rating=intake_rating,
            meaning="Draft intake with enough context to generate discovery and gate tickets.",
            required_action="Resolve missing approvals, owners, and delivery details before delivery execution.",
        ),
        CategoryScore(
            category="Timeline Risk",
            score=58 if timeline_rating == "L2" else 76,
            rating=timeline_rating,
            meaning="Target launch date exists while required controls remain incomplete.",
            required_action="Re-sequence Legal, Data Governance, Security, QA, file mover validation, and launch approval gates.",
        ),
        CategoryScore(
            category="Data Risk",
            score=82,
            rating=data_rating,
            meaning="Healthcare, personal, client, or external delivery data requires governed review.",
            required_action="Attach approved field list, permitted-use evidence, and data minimization review.",
        ),
        CategoryScore(
            category="File Mover Risk",
            score=45 if file_mover_rating == "L1" else 72 if file_mover_rating == "L3" else 88,
            rating=file_mover_rating,
            meaning="External delivery layer is referenced, but route, recipient, destination, and evidence are not fully validated.",
            required_action="Validate delivery mechanism, destination, recipient allowlist, route, manifest, logs, and test delivery.",
        ),
        CategoryScore(
            category="Ticket Quality",
            score=66 if ticket_rating == "L2" else 80,
            rating=ticket_rating,
            meaning="Ticket hierarchy can be generated, but several child work items must remain gate/discovery tickets.",
            required_action="Create governed work items with acceptance criteria and evidence requirements.",
        ),
    ]


def build_findings(intake: Intake) -> list[Finding]:
    findings: list[Finding] = []

    if intake.contains_phi or intake.contains_pii:
        findings.append(Finding(
            id="FINDING-DATA-001",
            severity="critical",
            finding="Sensitive or regulated data appears to be involved.",
            required_action="Require Legal, Data Governance, Security, and QA review before launch.",
            mapped_rule_id="DATAENG-PRINCIPLE-001",
            evidence_required=["approved_field_list", "permitted_use_reference", "minimum_necessary_review"],
        ))

    if intake.external_recipient:
        findings.append(Finding(
            id="FINDING-DELIVERY-001",
            severity="critical",
            finding="External recipient or client delivery is in scope.",
            required_action="Require recipient allowlist, destination validation, access review, manifest, and delivery evidence.",
            mapped_rule_id="DATAENG-PRINCIPLE-004",
            evidence_required=["recipient_allowlist", "destination_validation", "delivery_log"],
        ))

    if intake.file_movement_required and not intake.destination_confirmed:
        findings.append(Finding(
            id="FINDING-DELIVERY-002",
            severity="critical",
            finding="File mover or delivery layer is referenced, but the destination is not confirmed.",
            required_action="Identify and approve the destination folder, endpoint, bucket, portal, report, or mailbox.",
            mapped_rule_id="FILEMOVER-GATE-DESTINATION",
            evidence_required=["approved_destination"],
        ))

    if intake.file_movement_required and not intake.recipient_access_confirmed:
        findings.append(Finding(
            id="FINDING-DELIVERY-003",
            severity="critical",
            finding="Recipient access is not confirmed.",
            required_action="Complete access review and attach recipient allowlist evidence.",
            mapped_rule_id="FILEMOVER-GATE-ACCESS",
            evidence_required=["recipient_allowlist", "access_review"],
        ))

    if not intake.legal_review_confirmed:
        findings.append(Finding(
            id="FINDING-LEGAL-001",
            severity="high",
            finding="Legal or permitted-use approval is not confirmed.",
            required_action="Route targeted review to Legal or Compliance with field list and business purpose.",
            mapped_rule_id="LEGAL-TRIGGER-003",
            evidence_required=["legal_decision", "contract_or_baa_reference"],
        ))

    if intake.file_movement_required and not intake.production_equivalent_test_completed:
        findings.append(Finding(
            id="FINDING-QA-001",
            severity="high",
            finding="Production-equivalent test delivery is not confirmed.",
            required_action="Execute test delivery and attach evidence for destination, recipient, naming, payload, and manifest validation.",
            mapped_rule_id="FILEMOVER-GATE-TEST-DELIVERY",
            evidence_required=["test_delivery_log", "delivery_receipt", "qa_validation"],
        ))

    return findings


def build_launch_blockers(intake: Intake) -> list[LaunchBlocker]:
    blockers: list[LaunchBlocker] = []

    blocker_defs = [
        (
            not intake.legal_review_confirmed,
            "Legal approval not confirmed",
            "Attach Legal, Compliance, contract, BAA, SOW, or permitted-use approval.",
            "Legal / Compliance",
            ["legal_decision", "permitted_use_reference"],
        ),
        (
            not intake.data_governance_review_confirmed,
            "Final field list not approved",
            "Attach approved field list and minimum necessary review.",
            "Data Governance / Product",
            ["approved_field_list", "minimum_necessary_review"],
        ),
        (
            intake.file_movement_required and not intake.destination_confirmed,
            "Destination not confirmed",
            "Attach approved destination evidence for the file mover or delivery layer.",
            "Implementation / Platform Operations",
            ["approved_destination"],
        ),
        (
            intake.file_movement_required and not intake.recipient_access_confirmed,
            "Recipient access not confirmed",
            "Attach recipient allowlist and access review.",
            "Security / Platform Operations",
            ["recipient_allowlist", "access_review"],
        ),
        (
            intake.file_movement_required and not intake.production_equivalent_test_completed,
            "Production-equivalent test delivery not completed",
            "Run and attach test delivery evidence.",
            "QA / Platform Operations",
            ["test_delivery_log", "delivery_receipt", "qa_validation"],
        ),
        (
            intake.file_movement_required and not intake.runbook_confirmed,
            "Operational runbook not confirmed",
            "Create runbook with cadence, owner, monitoring, exception handling, and pause/rollback plan.",
            "Implementation / Operations",
            ["runbook"],
        ),
    ]

    for condition, blocker, resolution, owner, evidence in blocker_defs:
        if condition:
            blockers.append(LaunchBlocker(
                blocker=blocker,
                required_resolution=resolution,
                owner_role=owner,
                evidence_required=evidence,
            ))

    return blockers


def build_scorecard(intake: Intake) -> dict:
    category_scores = score_category_scores(intake)
    findings = build_findings(intake)
    blockers = build_launch_blockers(intake)
    overall_score = max(0, min(100, 82 - (len(blockers) * 2) - (len([f for f in findings if f.severity == "critical"]) * 2)))
    overall_rating = "at_risk" if blockers else "controlled"
    launch_position = "not_launchable" if blockers else "launchable_with_controls"

    return {
        "overall_score": overall_score,
        "overall_rating": overall_rating,
        "launch_position": launch_position,
        "summary": (
            "The request can be translated into governed delivery work, but launch is blocked until missing approvals, "
            "destination, recipient access, test delivery, and evidence controls are resolved."
            if blockers
            else "The request appears controlled enough to proceed with standard approval gates."
        ),
        "category_scores": [asdict(item) for item in category_scores],
        "findings": [asdict(item) for item in findings],
        "missing_information": intake.unknowns,
        "required_reviews": required_reviews(intake),
        "launch_blockers": [asdict(item) for item in blockers],
        "recommended_tickets": [
            "Review approved outbound data fields",
            "Confirm Legal and permitted-use approval",
            "Build source-to-target mapping",
            "Confirm approved external delivery mechanism",
            "Configure file mover route and destination",
            "Review recipient access and permissions",
            "Validate file naming and manifest controls",
            "Execute production-equivalent test delivery",
            "Create operational runbook",
            "Approve production launch",
        ],
        "assumptions_to_challenge": [
            "Prior client delivery patterns prove this delivery is safe.",
            "A correct SQL pipeline means the launch is ready.",
            "Folder names, file names, or labels prove the payload belongs to the intended recipient.",
            "A test delivery is sufficient if it does not match production route behavior.",
        ],
    }


def required_reviews(intake: Intake) -> list[str]:
    reviews = []
    if intake.contains_phi or intake.contains_pii or intake.contains_pci:
        reviews.extend(["Legal", "Privacy", "Compliance", "Data Governance"])
    if intake.external_recipient or intake.file_movement_required:
        reviews.extend(["Security", "QA", "Platform Operations"])
    if not reviews:
        reviews.append("Operational SME")
    return sorted(set(reviews))


def build_tickets(intake: Intake, scorecard: dict) -> list[Ticket]:
    client = intake.client_or_partner
    program = intake.program_or_workstream
    parent_title = f"{client} {program} External File Delivery Implementation"
    blockers = [item["blocker"] for item in scorecard["launch_blockers"]]
    common = {
        "platform": "generic",
        "request_type": intake.request_type,
        "program": program,
        "client": client,
        "systems_impacted": intake.systems_impacted,
        "data_involved": intake.data_types,
        "phi_flag": intake.contains_phi,
        "pii_flag": intake.contains_pii,
        "pci_flag": intake.contains_pci,
        "external_recipient": intake.external_recipient,
        "file_movement_required": intake.file_movement_required,
        "delivery_method": intake.delivery_method,
        "legal_review_required": intake.contains_phi or intake.contains_pii or intake.external_recipient,
        "security_review_required": intake.external_recipient or intake.file_movement_required,
        "data_governance_required": bool(intake.data_types),
        "qa_required": True,
        "soc2_impact": ["Access Control", "Change Management", "Processing Integrity", "Confidentiality"],
        "risk_rating": "L4" if (intake.contains_phi or intake.external_recipient) else "L2",
        "timeline_risk_rating": "L2" if blockers else "L3",
        "ticket_quality_rating": "L2" if blockers else "L3",
        "assignee": "TBD",
        "due_date": intake.desired_launch_date,
        "sprint_or_iteration": "",
        "dependencies": [],
        "blockers": blockers,
        "evidence_links": [],
        "status": "New",
        "export_ready": True,
    }

    tickets: list[Ticket] = []

    def add_ticket(external_id: str, parent_id: str, work_item_type: str, title: str, owner_role: str,
                   description: str, acceptance_criteria: list[str], evidence_required: list[str],
                   launch_blocker: bool = True, priority: str = "high", user_story: str = "") -> None:
        tickets.append(Ticket(
            external_id=external_id,
            parent_external_id=parent_id,
            work_item_type=work_item_type,
            title=title,
            description=description,
            business_context=intake.business_goal,
            user_story=user_story or f"As an accountable delivery team, I need {title.lower()} so that the launch is controlled and auditable.",
            acceptance_criteria=acceptance_criteria,
            definition_of_done=[
                "Acceptance criteria are complete.",
                "Required evidence is attached or explicitly marked not applicable.",
                "Open blockers are resolved or formally accepted by an authorized owner.",
                "Ticket is linked to the correct parent work item.",
            ],
            owner_role=owner_role,
            evidence_required=evidence_required,
            launch_blocker=launch_blocker,
            priority=priority,
            **common,
        ))

    add_ticket(
        "INIT-001", "", "initiative", parent_title, "Product / PM / Implementation",
        f"Govern, build, validate, and approve {program} external file delivery for {client}.",
        ["Child epics are created.", "Launch blockers are tracked.", "Evidence packet is complete before production launch."],
        ["launch_decision", "evidence_packet"], True
    )

    add_ticket(
        "EPIC-001", "INIT-001", "epic", f"{program} Data and Field Governance", "Product / Data Governance",
        "Confirm approved data fields, permitted use, source-to-target mapping, and data QA controls.",
        ["Legal and data governance approvals are attached.", "Source-to-target mapping is complete."],
        ["approved_field_list", "minimum_necessary_review", "source_to_target_mapping"], True
    )

    add_ticket(
        "STORY-001", "EPIC-001", "story", f"Review approved {program} outbound data fields", "Data Governance / Product",
        "Review final outbound field list and confirm minimum necessary fields for the approved purpose.",
        ["Final field list is documented.", "Each field has purpose, source, sensitivity, and approval status.", "PHI/PII fields are approved or removed."],
        ["approved_field_list", "field_classification_matrix", "minimum_necessary_review"], True
    )

    add_ticket(
        "STORY-002", "EPIC-001", "story", "Confirm Legal and permitted-use approval", "Legal / Compliance",
        "Confirm contract, BAA, SOW, or permitted-use approval for outbound delivery.",
        ["Legal confirms permitted use.", "Contract, BAA, SOW, or approval reference is linked.", "Restricted fields or use cases are documented."],
        ["legal_decision", "contract_or_baa_reference"], True
    )

    add_ticket(
        "STORY-003", "EPIC-001", "story", "Build source-to-target mapping", "Data Engineering",
        "Document source tables, joins, filters, transformations, and target outbound fields.",
        ["Source tables are documented.", "Target fields match approved field list.", "Row counts and reconciliation logic are defined.", "Peer review is complete."],
        ["source_to_target_mapping", "peer_review"], True
    )

    add_ticket(
        "EPIC-002", "INIT-001", "epic", "File Mover Delivery Configuration", "Implementation / Platform Operations",
        "Configure and validate the external delivery layer, destination, access, naming, manifest, and route controls.",
        ["Delivery mechanism is confirmed.", "Destination and recipient access are approved.", "Route and manifest controls are validated."],
        ["approved_destination", "recipient_allowlist", "route_config_review"], True
    )

    add_ticket(
        "STORY-004", "EPIC-002", "story", "Confirm approved external delivery mechanism", "Implementation / Security / Client Operations",
        "Identify approved delivery mechanism such as MFT, SFTP, API, cloud storage, client portal, reporting export, or another file mover.",
        ["Delivery mechanism is identified.", "Approved destination is documented.", "Client or recipient ownership is confirmed with canonical ID."],
        ["delivery_mechanism_approval", "approved_destination"], True
    )

    add_ticket(
        "STORY-005", "EPIC-002", "story", "Configure file mover route and destination", "Platform Operations / Data Engineering",
        "Configure source, destination, environment, schedule, owner, and route controls using canonical identifiers where possible.",
        ["Route uses canonical client or program identifiers where possible.", "Configuration is peer reviewed.", "Change ticket is linked."],
        ["route_config_review", "change_ticket"], True
    )

    add_ticket(
        "STORY-006", "EPIC-002", "story", "Review recipient access and permissions", "Security / Platform Operations",
        "Validate recipient allowlist, access group, service account permissions, and least privilege.",
        ["Recipient allowlist is documented.", "Access is limited to intended recipients only.", "Security approval evidence is attached."],
        ["recipient_allowlist", "access_review"], True
    )

    add_ticket(
        "STORY-007", "EPIC-002", "story", "Validate file naming and manifest controls", "Data Engineering / QA",
        "Confirm naming convention, payload ownership reconciliation, manifest, control totals, checksum, and batch ID logic.",
        ["File name is reconciled to payload ownership.", "Manifest or control totals are defined.", "Validation evidence is attached."],
        ["file_naming_convention", "manifest", "checksum_or_control_totals"], True
    )

    add_ticket(
        "EPIC-003", "INIT-001", "epic", "QA, Launch Readiness, and Operations", "QA / PM / Operations",
        "Complete test delivery, runbook, monitoring, and final launch approval.",
        ["Production-equivalent test delivery is complete.", "Runbook and monitoring are defined.", "Final launch decision is documented."],
        ["test_delivery_log", "runbook", "launch_decision"], True
    )

    add_ticket(
        "STORY-008", "EPIC-003", "story", "Execute production-equivalent test delivery", "QA / Platform Operations",
        "Run production-equivalent test delivery and validate destination, recipient, file name, payload, manifest, and logs.",
        ["Test uses production-equivalent route or documented delta review.", "Delivery log or receipt is attached.", "Destination, recipient, file name, payload, and manifest are validated."],
        ["test_delivery_log", "delivery_receipt", "qa_validation"], True
    )

    add_ticket(
        "STORY-009", "EPIC-003", "story", "Create operational runbook", "Implementation / Operations",
        "Document weekly cadence, owner, monitoring, exception handling, escalation, and pause or rollback plan.",
        ["Runbook explains cadence, owner, monitoring, exceptions, and escalation.", "Pause or rollback process is documented.", "Support handoff is complete."],
        ["runbook", "support_handoff"], True
    )

    add_ticket(
        "STORY-010", "EPIC-003", "story", "Configure monitoring and alerting", "Platform Operations / Data Engineering",
        "Define job success/failure monitoring, delivery confirmation, failure alert, and exception owner.",
        ["Job monitoring is defined.", "Failure alert is configured or documented.", "Exception owner is assigned."],
        ["monitoring_plan", "alerting_evidence"], False, priority="medium"
    )

    add_ticket(
        "STORY-011", "EPIC-003", "story", "Approve production launch", "Product / PM / Compliance",
        "Confirm required approvals, evidence, and launch decision before production delivery begins.",
        ["Legal approval is attached.", "Data Governance approval is attached.", "Security approval is attached.", "QA evidence is attached.", "Launch decision is documented."],
        ["legal_decision", "data_governance_approval", "security_approval", "qa_evidence", "launch_decision"], True
    )

    return tickets


def build_evidence_packet(intake: Intake, scorecard: dict) -> dict:
    evidence_items = [
        ("Business approval", "Approved business purpose or implementation request", "Product / Implementation", True),
        ("Legal approval", "Contract, BAA, SOW, permitted-use approval, or Legal decision", "Legal / Compliance", True),
        ("Data Governance", "Approved field list and minimum necessary review", "Data Governance / Product", True),
        ("Source-to-target mapping", "Mapping document with source fields, transformations, filters, and target fields", "Data Engineering", True),
        ("Data QA", "Row counts, reconciliation totals, schema validation, and exception review", "QA / Data Engineering", True),
        ("Delivery mechanism", "Approved file mover, API, portal, cloud folder, report export, or other delivery layer", "Implementation / Platform Ops", True),
        ("Destination validation", "Folder path, endpoint, bucket, portal location, report location, or recipient mailbox evidence", "Platform Ops / Security", True),
        ("Recipient allowlist", "Approved users, groups, service accounts, or partner endpoints", "Security", True),
        ("Access review", "Permission review and least-privilege confirmation", "Security", True),
        ("File naming control", "Naming convention and payload ownership reconciliation", "Data Engineering / QA", True),
        ("Manifest/checksum", "Row count, file count, checksum, batch ID, schema version, or control file", "Data Engineering", True),
        ("Test delivery", "Production-equivalent delivery log, receipt, confirmation, or redacted screenshot", "QA / Platform Ops", True),
        ("Monitoring", "Job status, alert routing, failure notification, and exception owner", "Platform Ops", False),
        ("Runbook", "Weekly operation steps, owner, escalation path, and pause/rollback plan", "Implementation / Operations", True),
        ("Launch approval", "Final go/no-go decision with named approvers", "Product / PM / Compliance", True),
    ]

    return {
        "packet_id": f"EVIDENCE-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "request_title": intake.request_title,
        "client_or_partner": intake.client_or_partner,
        "program_or_workstream": intake.program_or_workstream,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "evidence_items": [
            {
                "evidence_area": area,
                "required_artifact": artifact,
                "owner_role": owner,
                "status": "missing",
                "launch_blocker": blocker,
                "evidence_link": "",
                "decision_notes": "",
                "approved_by": "",
                "approved_at": "",
                "expires_or_review_by": "",
            }
            for area, artifact, owner, blocker in evidence_items
        ],
        "sensitive_data_warning": "Do not paste PHI, PCI, credentials, secrets, or live client data into unmanaged tools.",
        "open_blockers": [item["blocker"] for item in scorecard["launch_blockers"]],
        "accepted_risks": [],
        "launch_decision": "blocked" if scorecard["launch_blockers"] else "requires_review",
        "final_approvers": [],
    }


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    output = []
    output.append("| " + " | ".join(headers) + " |")
    output.append("|" + "|".join(["---" for _ in headers]) + "|")
    for row in rows:
        output.append("| " + " | ".join(str(cell).replace("\n", "<br>") for cell in row) + " |")
    return "\n".join(output)


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def render_scorecard_md(scorecard: dict) -> str:
    category_rows = [
        [item["category"], str(item["score"]), item["rating"], item["meaning"], item["required_action"]]
        for item in scorecard["category_scores"]
    ]
    finding_rows = [
        [item["id"], item["severity"], item["finding"], item["required_action"]]
        for item in scorecard["findings"]
    ]
    blocker_rows = [
        [item["blocker"], item["required_resolution"], item["owner_role"], ", ".join(item["evidence_required"])]
        for item in scorecard["launch_blockers"]
    ]

    return f"""# Governed Delivery Scorecard

## Overall Result

| Field | Value |
|---|---|
| Overall Score | {scorecard["overall_score"]} / 100 |
| Overall Rating | {scorecard["overall_rating"]} |
| Launch Position | {scorecard["launch_position"]} |

## Summary

{scorecard["summary"]}

## Category Scores

{markdown_table(["Category", "Score", "Rating", "Meaning", "Required Action"], category_rows)}

## Findings

{markdown_table(["ID", "Severity", "Finding", "Required Action"], finding_rows)}

## Missing Information

{chr(10).join(f"- {item}" for item in scorecard["missing_information"])}

## Required Reviews

{chr(10).join(f"- {item}" for item in scorecard["required_reviews"])}

## Launch Blockers

{markdown_table(["Blocker", "Required Resolution", "Owner Role", "Evidence Required"], blocker_rows)}

## Assumptions to Challenge

{chr(10).join(f"- {item}" for item in scorecard["assumptions_to_challenge"])}
"""


def render_tickets_md(tickets: list[Ticket]) -> str:
    sections = ["# Generated Ticket Hierarchy\n"]
    for ticket in tickets:
        sections.append(f"## {ticket.external_id}: {ticket.title}\n")
        sections.append(f"**Type:** {ticket.work_item_type}  \n")
        sections.append(f"**Parent:** {ticket.parent_external_id or 'None'}  \n")
        sections.append(f"**Owner Role:** {ticket.owner_role}  \n")
        sections.append(f"**Risk Rating:** {ticket.risk_rating}  \n")
        sections.append(f"**Launch Blocker:** {'Yes' if ticket.launch_blocker else 'No'}\n")
        sections.append(f"\n{ticket.description}\n")
        sections.append("\n### Acceptance Criteria\n")
        sections.extend([f"{idx}. {item}\n" for idx, item in enumerate(ticket.acceptance_criteria, start=1)])
        sections.append("\n### Evidence Required\n")
        sections.extend([f"- {item}\n" for item in ticket.evidence_required])
        sections.append("\n")
    return "".join(sections)


def render_evidence_md(packet: dict) -> str:
    rows = [
        [
            item["evidence_area"],
            item["required_artifact"],
            item["owner_role"],
            item["status"],
            "Yes" if item["launch_blocker"] else "No",
        ]
        for item in packet["evidence_items"]
    ]
    return f"""# Evidence Packet

## Request

| Field | Value |
|---|---|
| Packet ID | {packet["packet_id"]} |
| Request Title | {packet["request_title"]} |
| Client / Partner | {packet["client_or_partner"]} |
| Program / Workstream | {packet["program_or_workstream"]} |
| Launch Decision | {packet["launch_decision"]} |

## Sensitive Data Warning

{packet["sensitive_data_warning"]}

## Evidence Items

{markdown_table(["Area", "Required Artifact", "Owner Role", "Status", "Launch Blocker"], rows)}

## Open Blockers

{chr(10).join(f"- {item}" for item in packet["open_blockers"])}
"""


def render_launch_summary_md(intake: Intake, scorecard: dict, tickets: list[Ticket]) -> str:
    blocker_count = len(scorecard["launch_blockers"])
    required_ticket_count = len(tickets)
    return f"""# Launch Readiness Summary

## Request

| Field | Value |
|---|---|
| Title | {intake.request_title} |
| Client / Partner | {intake.client_or_partner} |
| Program / Workstream | {intake.program_or_workstream} |
| Desired Launch Date | {intake.desired_launch_date} |
| Delivery Method | {intake.delivery_method} |
| External Recipient | {'Yes' if intake.external_recipient else 'No'} |
| File Movement Required | {'Yes' if intake.file_movement_required else 'No'} |

## Result

| Field | Value |
|---|---|
| Overall Score | {scorecard["overall_score"]} / 100 |
| Overall Rating | {scorecard["overall_rating"]} |
| Launch Position | {scorecard["launch_position"]} |
| Generated Tickets | {required_ticket_count} |
| Launch Blockers | {blocker_count} |

## Executive Readout

{scorecard["summary"]}

## Top Launch Blockers

{chr(10).join(f"- {item['blocker']}: {item['required_resolution']}" for item in scorecard["launch_blockers"])}

## Recommended Next Action

Resolve the launch blockers before production delivery. The fastest path is to complete Legal approval, approved field list review, destination validation, recipient access review, production-equivalent test delivery, and runbook evidence.
"""


def write_jira_csv(path: Path, tickets: list[Ticket]) -> None:
    fieldnames = [
        "Issue Type",
        "Summary",
        "Epic Name",
        "Parent",
        "Description",
        "Priority",
        "Labels",
        "Risk Rating",
        "Timeline Risk Rating",
        "Legal Review Required",
        "Security Review Required",
        "Data Governance Required",
        "QA Required",
        "PHI Flag",
        "PII Flag",
        "External Recipient",
        "File Movement Required",
        "Launch Blocker",
        "Acceptance Criteria",
        "Evidence Required",
    ]
    with path.open("w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for ticket in tickets:
            issue_type = {
                "initiative": "Epic",
                "epic": "Epic",
                "story": "Story",
                "task": "Task",
                "subtask": "Sub-task",
                "bug": "Bug",
            }.get(ticket.work_item_type, "Task")
            writer.writerow({
                "Issue Type": issue_type,
                "Summary": ticket.title,
                "Epic Name": ticket.title if issue_type == "Epic" else "",
                "Parent": ticket.parent_external_id,
                "Description": ticket.description,
                "Priority": ticket.priority.title(),
                "Labels": ",".join(["GovernedDelivery", ticket.program, ticket.client, "FileMover"]),
                "Risk Rating": ticket.risk_rating,
                "Timeline Risk Rating": ticket.timeline_risk_rating,
                "Legal Review Required": yes_no(ticket.legal_review_required),
                "Security Review Required": yes_no(ticket.security_review_required),
                "Data Governance Required": yes_no(ticket.data_governance_required),
                "QA Required": yes_no(ticket.qa_required),
                "PHI Flag": yes_no(ticket.phi_flag),
                "PII Flag": yes_no(ticket.pii_flag),
                "External Recipient": yes_no(ticket.external_recipient),
                "File Movement Required": yes_no(ticket.file_movement_required),
                "Launch Blocker": yes_no(ticket.launch_blocker),
                "Acceptance Criteria": " | ".join(ticket.acceptance_criteria),
                "Evidence Required": " | ".join(ticket.evidence_required),
            })


def yes_no(value: bool) -> str:
    return "Yes" if value else "No"


def run(input_path: Path, output_dir: Path, title: str | None = None) -> None:
    text = read_input(input_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    intake = normalize_intake(text, title=title)
    scorecard = build_scorecard(intake)
    tickets = build_tickets(intake, scorecard)
    evidence_packet = build_evidence_packet(intake, scorecard)

    write_json(output_dir / "normalized_intake.json", asdict(intake))
    write_json(output_dir / "scorecard.json", scorecard)
    write_json(output_dir / "generated_ticket_hierarchy.json", [asdict(ticket) for ticket in tickets])
    write_json(output_dir / "evidence_packet.json", evidence_packet)

    (output_dir / "scorecard.md").write_text(render_scorecard_md(scorecard), encoding="utf-8")
    (output_dir / "generated_ticket_hierarchy.md").write_text(render_tickets_md(tickets), encoding="utf-8")
    (output_dir / "evidence_packet.md").write_text(render_evidence_md(evidence_packet), encoding="utf-8")
    (output_dir / "launch_readiness_summary.md").write_text(render_launch_summary_md(intake, scorecard, tickets), encoding="utf-8")
    write_jira_csv(output_dir / "jira_export.csv", tickets)

    print("Governed delivery package generated:")
    print(f"- {output_dir / 'normalized_intake.json'}")
    print(f"- {output_dir / 'scorecard.md'}")
    print(f"- {output_dir / 'generated_ticket_hierarchy.md'}")
    print(f"- {output_dir / 'jira_export.csv'}")
    print(f"- {output_dir / 'evidence_packet.md'}")
    print(f"- {output_dir / 'launch_readiness_summary.md'}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate governed delivery scorecards, tickets, Jira CSV, and evidence packets from messy intake."
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
    run(Path(args.input), Path(args.output_dir), title=args.title)


if __name__ == "__main__":
    main()
