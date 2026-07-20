"""Canonical MissionRevoker domain models.

The core model is intentionally independent of any particular agent framework,
identity provider, policy engine, MCP gateway, or A2A implementation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Mapping


class EventType(StrEnum):
    MISSION_CREATED = "mission.created"
    DELEGATION_CREATED = "delegation.created"
    AUTHORIZATION_DECISION = "authorization.decision"
    ACTION_QUEUED = "action.queued"
    ACTION_DISPATCHED = "action.dispatched"
    EXECUTION_ACKNOWLEDGED = "execution.acknowledged"
    EFFECT_OBSERVED = "effect.observed"
    REVOCATION_REQUESTED = "revocation.requested"
    REVOCATION_ENFORCED = "revocation.enforced"
    TASK_CANCELLED = "task.cancelled"
    EVIDENCE_GAP = "evidence.gap"


class NodeKind(StrEnum):
    MISSION = "mission"
    AGENT = "agent"
    DELEGATION = "delegation"
    TASK = "task"
    CREDENTIAL = "credential"
    ACTION = "action"
    EFFECT = "effect"


class NodeStatus(StrEnum):
    ACTIVE = "active"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    REVOKED = "revoked"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_datetime(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    else:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamps must include a timezone")
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class Event:
    event_id: str
    event_type: EventType
    occurred_at: datetime
    source_system: str
    mission_id: str
    node_id: str | None = None
    parent_id: str | None = None
    action_id: str | None = None
    attributes: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.event_id.strip():
            raise ValueError("event_id is required")
        if not self.mission_id.strip():
            raise ValueError("mission_id is required")
        object.__setattr__(self, "occurred_at", parse_datetime(self.occurred_at))
        object.__setattr__(self, "attributes", dict(self.attributes))

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["event_type"] = self.event_type.value
        result["occurred_at"] = self.occurred_at.isoformat()
        return result

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "Event":
        return cls(
            event_id=str(payload["event_id"]),
            event_type=EventType(str(payload["event_type"])),
            occurred_at=parse_datetime(str(payload["occurred_at"])),
            source_system=str(payload["source_system"]),
            mission_id=str(payload["mission_id"]),
            node_id=_optional_str(payload.get("node_id")),
            parent_id=_optional_str(payload.get("parent_id")),
            action_id=_optional_str(payload.get("action_id")),
            attributes=dict(payload.get("attributes", {})),
        )


@dataclass(slots=True)
class Node:
    node_id: str
    mission_id: str
    kind: NodeKind
    source_system: str
    parent_id: str | None = None
    status: NodeStatus = NodeStatus.ACTIVE
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["kind"] = self.kind.value
        result["status"] = self.status.value
        return result


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
