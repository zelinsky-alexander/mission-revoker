"""Normalize a small OpenTelemetry span subset into canonical events."""

from __future__ import annotations

from typing import Any, Mapping

from ..models import Event, EventType, parse_datetime


def normalize_otel_span(payload: Mapping[str, Any], *, mission_id: str) -> Event:
    attributes = dict(payload.get("attributes", {}))
    span_kind = str(payload.get("name", ""))
    event_type = (
        EventType.ACTION_DISPATCHED
        if "tool" in span_kind.lower() or attributes.get("gen_ai.tool.name")
        else EventType.EVIDENCE_GAP
    )
    return Event(
        event_id=str(payload.get("span_id") or payload.get("id")),
        event_type=event_type,
        occurred_at=parse_datetime(str(payload.get("start_time") or payload.get("timestamp"))),
        source_system="opentelemetry",
        mission_id=mission_id,
        node_id=_text(attributes.get("gen_ai.agent.id")),
        parent_id=_text(payload.get("parent_span_id")),
        action_id=_text(attributes.get("missionrevoker.action_id") or payload.get("trace_id")),
        attributes=attributes,
    )


def _text(value: Any) -> str | None:
    return str(value) if value not in (None, "") else None
