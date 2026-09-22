from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from datetime import UTC, date, datetime
from hashlib import sha256
from json import dumps


@dataclass(frozen=True)
class Initiative:
    initiative_id: str
    title: str
    objective: str
    owner: str
    deadline: date
    strategic_alignment: float
    value: float
    urgency: float
    feasibility: float
    dependencies: tuple[str, ...] = ()
    adoption_complexity: float = 0.2
    data_sensitivity: str = "internal"
    state: str = "draft"

    def validate(self) -> None:
        if not all((self.initiative_id, self.title, self.objective, self.owner)):
            raise ValueError("initiative id, title, objective and owner are required")
        for name in ("strategic_alignment", "value", "urgency", "feasibility", "adoption_complexity"):
            if not 0 <= getattr(self, name) <= 1:
                raise ValueError(f"{name} must be between 0 and 1")
        if self.data_sensitivity not in {"public", "internal", "confidential", "restricted"}:
            raise ValueError("unsupported data sensitivity")


TRANSITIONS = {
    "draft": {"analyzed"},
    "analyzed": {"awaiting_approval"},
    "awaiting_approval": {"approved", "rejected"},
    "approved": {"executing"},
    "executing": {"closed"},
    "rejected": set(),
    "closed": set(),
}


class ProjectOffice:
    def __init__(self, initiatives: list[Initiative]):
        self.initiatives = {item.initiative_id: item for item in initiatives}
        if len(self.initiatives) != len(initiatives):
            raise ValueError("initiative_id must be unique")
        for item in initiatives:
            item.validate()
        self.audit: list[dict[str, object]] = []

    def priority(self, initiative_id: str) -> dict[str, object]:
        item = self.initiatives[initiative_id]
        risk = 0.4 * item.adoption_complexity + 0.35 * min(len(item.dependencies) / 3, 1) + 0.25 * (item.data_sensitivity in {"confidential", "restricted"})
        components = {
            "strategic_alignment": 0.30 * item.strategic_alignment,
            "value": 0.25 * item.value,
            "urgency": 0.20 * item.urgency,
            "feasibility": 0.15 * item.feasibility,
            "risk_adjustment": -0.10 * risk,
        }
        score = 100 * sum(components.values())
        return {"initiative_id": initiative_id, "priority_score": round(score, 1), "components": {key: round(value, 4) for key, value in components.items()}, "risk": round(risk, 3)}

    def analyze(self, initiative_id: str) -> dict[str, object]:
        item = self.initiatives[initiative_id]
        findings = []
        if len(item.dependencies) >= 2:
            findings.append("DEPENDENCY_CONCENTRATION")
        if item.adoption_complexity >= 0.6:
            findings.append("CHANGE_ADOPTION")
        if item.data_sensitivity in {"confidential", "restricted"}:
            findings.append("DATA_GOVERNANCE")
        if (item.deadline - datetime.now(UTC).date()).days < 30:
            findings.append("TIMELINE_PRESSURE")
        workshop = [
            "Confirm business outcome and accountable owner",
            "Review assumptions, dependencies and evidence",
            "Agree success metrics and decision rights",
            "Assign mitigations and next review date",
        ]
        if item.state == "draft":
            self.transition(initiative_id, "analyzed", actor="analysis-agents", role="agent")
        return {"priority": self.priority(initiative_id), "risk_findings": findings, "workshop_agenda": workshop}

    def transition(self, initiative_id: str, target: str, actor: str, role: str, reason: str = "") -> Initiative:
        item = self.initiatives[initiative_id]
        if target == item.state:
            return item
        if target not in TRANSITIONS[item.state]:
            raise ValueError(f"invalid transition {item.state} -> {target}")
        if target in {"approved", "rejected"} and role != "human-approver":
            raise PermissionError("approval decisions require a human approver")
        updated = replace(item, state=target)
        self.initiatives[initiative_id] = updated
        self._record(initiative_id, item.state, target, actor, role, reason)
        return updated

    def _record(self, initiative_id: str, source: str, target: str, actor: str, role: str, reason: str) -> None:
        previous_hash = self.audit[-1]["event_hash"] if self.audit else "GENESIS"
        event = {
            "sequence": len(self.audit) + 1,
            "timestamp": datetime.now(UTC).isoformat(),
            "initiative_id": initiative_id,
            "from": source,
            "to": target,
            "actor": actor,
            "role": role,
            "reason": reason,
            "previous_hash": previous_hash,
        }
        event["event_hash"] = sha256(dumps(event, sort_keys=True).encode()).hexdigest()
        self.audit.append(event)

    def verify_audit_chain(self) -> bool:
        previous = "GENESIS"
        for stored in self.audit:
            event = {key: value for key, value in stored.items() if key != "event_hash"}
            if event["previous_hash"] != previous or sha256(dumps(event, sort_keys=True).encode()).hexdigest() != stored["event_hash"]:
                return False
            previous = stored["event_hash"]
        return True

    def executive_report(self) -> dict[str, object]:
        ranked = sorted((self.priority(key) for key in self.initiatives), key=lambda row: row["priority_score"], reverse=True)
        states: dict[str, int] = {}
        for item in self.initiatives.values():
            states[item.state] = states.get(item.state, 0) + 1
        return {
            "portfolio_size": len(self.initiatives),
            "state_distribution": states,
            "ranked_priorities": ranked,
            "management_message": f"Portfolio contains {len(self.initiatives)} initiatives; {ranked[0]['initiative_id']} is the current highest priority.",
            "audit_chain_valid": self.verify_audit_chain(),
        }

    def records(self):
        return [asdict(item) for item in self.initiatives.values()]


def demo_office() -> ProjectOffice:
    return ProjectOffice([
        Initiative("AI-101", "AI knowledge assistant", "Reduce search time for engineering guidance", "M. Owner", date(2026, 12, 15), 0.92, 0.78, 0.72, 0.68, ("data-catalog", "iam"), 0.55, "internal"),
        Initiative("OPS-220", "Reporting automation", "Automate monthly portfolio reporting", "A. Owner", date(2026, 11, 30), 0.80, 0.70, 0.85, 0.88, ("erp-export",), 0.30, "confidential"),
    ])
