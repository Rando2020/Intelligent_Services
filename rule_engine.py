"""
rule_engine.py

YAML-driven scoring engine for Intelligent Services.

Replaces the hardcoded numbers in build_scorecard() and the list-of-tuples in
build_launch_blockers() with logic read from rules/scoring_rules.yaml.

Design goals:
  - One source of truth: change scoring behavior by editing YAML, not Python.
  - Drop-in: produces the same scorecard dict shape the CLI already emits.
  - Safe: validates the config on load (weights sum to 100, bands ordered).
  - Predicates stay in Python (they inspect the Intake object), but every
    NUMBER, CAP, BAND, and BLOCKER definition lives in YAML.

Usage:
    from rule_engine import RuleEngine
    engine = RuleEngine.from_file("rules/scoring_rules.yaml")
    scorecard = engine.build_scorecard(intake, findings)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import yaml


# ---------------------------------------------------------------------------
# Predicate registry
# ---------------------------------------------------------------------------
# YAML references conditions by name (e.g. "legal_use_not_approved").
# Each maps to a function (intake) -> bool. This is the ONLY place new
# detection logic gets wired in; the YAML decides what the result *means*.
#
# Wire these to your real Intake fields. Defaults below are conservative
# (return False / "not a problem") so a missing field never silently blocks.

PredicateFn = Callable[[object], bool]
_PREDICATES: dict[str, PredicateFn] = {}


def predicate(name: str):
    def wrap(fn: PredicateFn) -> PredicateFn:
        _PREDICATES[name] = fn
        return fn
    return wrap


def _get(intake: object, attr: str, default=None):
    """Safe attribute access against the Intake dataclass or a dict."""
    if isinstance(intake, dict):
        return intake.get(attr, default)
    return getattr(intake, attr, default)


# --- gate-cap predicates ---------------------------------------------------
@predicate("dataset_unclassified")
def _dataset_unclassified(intake) -> bool:
    return not bool(_get(intake, "data_classified", False))

@predicate("sensitive_data_in_unmanaged_context")
def _sensitive_unmanaged(intake) -> bool:
    return bool(_get(intake, "sensitive_data_detected", False)) and not bool(
        _get(intake, "managed_environment_confirmed", False)
    )

@predicate("no_accountable_owner")
def _no_owner(intake) -> bool:
    return not bool(_get(intake, "data_owner_identified", False))

@predicate("no_minimization_review")
def _no_minimization(intake) -> bool:
    return not bool(_get(intake, "minimization_reviewed", False))

@predicate("no_outbound_delivery_control")
def _no_outbound(intake) -> bool:
    return bool(_get(intake, "external_delivery_required", False)) and not bool(
        _get(intake, "outbound_controls_confirmed", False)
    )

@predicate("wrong_recipient_risk")
def _wrong_recipient(intake) -> bool:
    return bool(_get(intake, "manual_routing_detected", False))


# --- launch-blocker predicates --------------------------------------------
@predicate("legal_use_not_approved")
def _legal_unapproved(intake) -> bool:
    return bool(_get(intake, "external_delivery_required", False)) and not bool(
        _get(intake, "legal_use_approved", False)
    )

@predicate("destination_not_verified")
def _dest_unverified(intake) -> bool:
    return bool(_get(intake, "file_movement_required", False)) and not bool(
        _get(intake, "destination_verified", False)
    )

@predicate("recipient_access_not_verified")
def _recipient_unverified(intake) -> bool:
    return bool(_get(intake, "file_movement_required", False)) and not bool(
        _get(intake, "recipient_access_verified", False)
    )

@predicate("no_production_equivalent_test")
def _no_test(intake) -> bool:
    return bool(_get(intake, "file_movement_required", False)) and not bool(
        _get(intake, "test_delivery_confirmed", False)
    )

@predicate("runbook_not_confirmed")
def _no_runbook(intake) -> bool:
    return bool(_get(intake, "file_movement_required", False)) and not bool(
        _get(intake, "runbook_confirmed", False)
    )


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------
@dataclass
class RuleEngine:
    config: dict
    predicates: dict[str, PredicateFn] = field(default_factory=lambda: dict(_PREDICATES))

    # ---- loading & validation ----
    @classmethod
    def from_file(cls, path: str | Path) -> "RuleEngine":
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        engine = cls(config=data)
        engine.validate()
        return engine

    def validate(self) -> None:
        dims = self.config.get("dimensions", [])
        total = sum(d["weight"] for d in dims)
        if dims and total != 100:
            # NOTE: the source scoring table in the docs currently sums to 110,
            # not 100 — this validator surfaced that. Decide which dimension(s)
            # to adjust, then this becomes a hard error. Warning for now.
            import warnings
            warnings.warn(
                f"dimension weights sum to {total}, expected 100 "
                f"(the source doc table also sums to {total} — needs reconciliation)."
            )

        bands = self.config.get("rating_bands", [])
        mins = [b["min"] for b in bands]
        if mins != sorted(mins, reverse=True):
            raise ValueError("rating_bands must be ordered high → low by `min`")

        for section in ("gate_caps", "launch_blockers"):
            for item in self.config.get(section, []):
                cond = item["condition"]
                if cond not in self.predicates:
                    raise ValueError(
                        f"{section}: '{item['id']}' references unknown predicate '{cond}'. "
                        f"Register it with @predicate('{cond}') in rule_engine.py."
                    )

    # ---- evaluation helpers ----
    def _truthy(self, intake: object, condition_name: str, *, has_blockers: bool) -> bool:
        if condition_name == "always":
            return True
        if condition_name == "has_blockers":
            return has_blockers
        fn = self.predicates.get(condition_name)
        return bool(fn(intake)) if fn else False

    def _first_match(self, rules: list[dict], intake, *, has_blockers: bool) -> str:
        for rule in rules:
            if self._truthy(intake, rule["when"], has_blockers=has_blockers):
                return rule["value"]
        return ""

    def evaluate_launch_blockers(self, intake: object) -> list[dict]:
        out = []
        for b in self.config.get("launch_blockers", []):
            if self._truthy(intake, b["condition"], has_blockers=False):
                out.append({
                    "blocker": b["blocker"],
                    "required_resolution": b["required_resolution"],
                    "owner_role": b["owner_role"],
                    "evidence_required": list(b.get("evidence_required", [])),
                })
        return out

    def apply_gate_caps(self, intake: object, score: int) -> tuple[int, list[dict]]:
        applied = []
        capped = score
        for g in self.config.get("gate_caps", []):
            if self._truthy(intake, g["condition"], has_blockers=False):
                if capped > g["cap"]:
                    capped = g["cap"]
                applied.append({"gate": g["id"], "cap": g["cap"], "reason": g["reason"]})
        return capped, applied

    def rating_for(self, score: int) -> dict:
        for band in self.config.get("rating_bands", []):
            if score >= band["min"]:
                return {"rating": band["rating"], "meaning": band["meaning"]}
        return {"rating": "Unrated", "meaning": ""}

    # ---- main entry point ----
    def build_scorecard(self, intake: object, findings: list | None = None) -> dict:
        findings = findings or []
        o = self.config["overall"]

        blockers = self.evaluate_launch_blockers(intake)
        has_blockers = bool(blockers)
        criticals = len([f for f in findings if _severity(f) == "critical"])

        raw = (
            o["base_score"]
            - len(blockers) * o["penalty_per_blocker"]
            - criticals * o["penalty_per_critical_finding"]
        )
        raw = max(o["min"], min(o["max"], raw))

        capped, gates_applied = self.apply_gate_caps(intake, raw)
        band = self.rating_for(capped)

        return {
            "overall_score": capped,
            "raw_score": raw,
            "overall_rating": self._first_match(o["rating"], intake, has_blockers=has_blockers),
            "launch_position": self._first_match(o["launch_position"], intake, has_blockers=has_blockers),
            "rating_band": band["rating"],
            "rating_meaning": band["meaning"],
            "gate_caps_applied": gates_applied,
            "launch_blockers": blockers,
            "findings": [_as_dict(f) for f in findings],
        }


def _severity(f) -> str:
    if isinstance(f, dict):
        return f.get("severity", "")
    return getattr(f, "severity", "")


def _as_dict(f):
    if isinstance(f, dict):
        return f
    if hasattr(f, "__dict__"):
        return dict(f.__dict__)
    return f


if __name__ == "__main__":
    # Smoke test with a dict standing in for an Intake.
    engine = RuleEngine.from_file(Path(__file__).parent / "scoring_rules.yaml")
    sample = {
        "external_delivery_required": True,
        "legal_use_approved": False,        # -> triggers legal blocker
        "file_movement_required": True,
        "destination_verified": False,      # -> destination blocker
        "recipient_access_verified": True,
        "test_delivery_confirmed": True,
        "runbook_confirmed": True,
        "data_classified": True,
        "data_owner_identified": True,
        "minimization_reviewed": True,
        "outbound_controls_confirmed": False,  # -> no_outbound gate cap (69)
    }
    sc = engine.build_scorecard(sample, findings=[{"severity": "critical"}])
    import json
    print(json.dumps(sc, indent=2))
