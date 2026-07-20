"""Input/output helpers for canonical JSON Lines events."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .models import Event


def load_jsonl(path: str | Path) -> list[Event]:
    events: list[Event] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                payload = json.loads(line)
                events.append(Event.from_dict(payload))
            except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                raise ValueError(f"invalid event at {path}:{line_number}: {exc}") from exc
    return events


def write_jsonl(events: Iterable[Event], path: str | Path) -> None:
    with Path(path).open("w", encoding="utf-8", newline="\n") as handle:
        for event in events:
            handle.write(json.dumps(event.to_dict(), sort_keys=True))
            handle.write("\n")
