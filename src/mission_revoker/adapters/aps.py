"""Minimal normalization boundary for APS-style signed receipts."""

from __future__ import annotations

from typing import Any, Mapping

from ..models import Event, EventType, parse_datetime


def normalize_aps_receipt(payload: Mapping[str, Any], *, mission_id: str) -> Event:
    claim_type = str(payload.get("type") or payload.get("claim_type") or "")
    event_type = _map_claim(claim_type, payload)
    return Event(
        event_id=str(payload.get("receipt_id") or payload.get("id")),
        event_type=event_type,
        occurred_at=parse_datetime(str(payload.get("timestamp") or payload.get("issued_at"))),
        source_system="agent-passport-system",
        mission_id=mission_id,
        node_id=_text(payload.get("subject_agent")),
        parent_id=_text(payload.get("delegation_chain_root")),
        action_id=_text(payload.get("action_ref") or payload.get("action_id")),
        attributes={
            "claim_type": claim_type,
            "capture_mode": payload.get("capture_mode"),
            "self_attested": payload.get("self_attested"),
            "verdict": payload.get("verdict"),
            "scope_of_claim": payload.get("scope_of_claim"),
        },
    )


def _map_claim(claim_type: str, payload: Mapping[str, Any]) -> EventType:
    if "authority" in claim_type or "policy" in claim_type:
        return EventType.AUTHORIZATION_DECISION
    if payload.get("verdict") in {"deny", "denied"}:
        return EventType.AUTHORIZATION_DECISION
    if "action" in claim_type or "execution" in claim_type:
        return EventType.EXECUTION_ACKNOWLEDGED
    return EventType.EVIDENCE_GAP


def _text(value: Any) -> str | None:
    return str(value) if value not in (None, "") else None
