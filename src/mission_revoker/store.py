"""SQLite persistence for canonical events and graph nodes."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable

from .models import Event, EventType, Node, NodeKind, NodeStatus, parse_datetime


class SQLiteStore:
    def __init__(self, path: str | Path = ":memory:") -> None:
        self.path = str(path)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self._initialize()

    def close(self) -> None:
        self.connection.close()

    def _initialize(self) -> None:
        self.connection.executescript(
            """
            PRAGMA foreign_keys = ON;
            CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                occurred_at TEXT NOT NULL,
                source_system TEXT NOT NULL,
                mission_id TEXT NOT NULL,
                node_id TEXT,
                parent_id TEXT,
                action_id TEXT,
                attributes_json TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_events_mission_time
                ON events(mission_id, occurred_at);

            CREATE TABLE IF NOT EXISTS nodes (
                node_id TEXT PRIMARY KEY,
                mission_id TEXT NOT NULL,
                kind TEXT NOT NULL,
                source_system TEXT NOT NULL,
                parent_id TEXT,
                status TEXT NOT NULL,
                metadata_json TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_nodes_mission
                ON nodes(mission_id);
            """
        )
        self.connection.commit()

    def put_event(self, event: Event) -> None:
        self.connection.execute(
            """
            INSERT OR REPLACE INTO events (
                event_id, event_type, occurred_at, source_system, mission_id,
                node_id, parent_id, action_id, attributes_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.event_id,
                event.event_type.value,
                event.occurred_at.isoformat(),
                event.source_system,
                event.mission_id,
                event.node_id,
                event.parent_id,
                event.action_id,
                json.dumps(dict(event.attributes), sort_keys=True),
            ),
        )
        self.connection.commit()

    def put_events(self, events: Iterable[Event]) -> None:
        with self.connection:
            for event in events:
                self.connection.execute(
                    """
                    INSERT OR REPLACE INTO events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        event.event_id,
                        event.event_type.value,
                        event.occurred_at.isoformat(),
                        event.source_system,
                        event.mission_id,
                        event.node_id,
                        event.parent_id,
                        event.action_id,
                        json.dumps(dict(event.attributes), sort_keys=True),
                    ),
                )

    def events_for_mission(self, mission_id: str) -> list[Event]:
        rows = self.connection.execute(
            "SELECT * FROM events WHERE mission_id = ? ORDER BY occurred_at, event_id",
            (mission_id,),
        ).fetchall()
        return [self._row_to_event(row) for row in rows]

    def put_node(self, node: Node) -> None:
        self.connection.execute(
            """
            INSERT OR REPLACE INTO nodes (
                node_id, mission_id, kind, source_system, parent_id, status, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                node.node_id,
                node.mission_id,
                node.kind.value,
                node.source_system,
                node.parent_id,
                node.status.value,
                json.dumps(node.metadata, sort_keys=True),
            ),
        )
        self.connection.commit()

    def nodes_for_mission(self, mission_id: str) -> list[Node]:
        rows = self.connection.execute(
            "SELECT * FROM nodes WHERE mission_id = ? ORDER BY node_id",
            (mission_id,),
        ).fetchall()
        return [
            Node(
                node_id=row["node_id"],
                mission_id=row["mission_id"],
                kind=NodeKind(row["kind"]),
                source_system=row["source_system"],
                parent_id=row["parent_id"],
                status=NodeStatus(row["status"]),
                metadata=json.loads(row["metadata_json"]),
            )
            for row in rows
        ]

    @staticmethod
    def _row_to_event(row: sqlite3.Row) -> Event:
        return Event(
            event_id=row["event_id"],
            event_type=EventType(row["event_type"]),
            occurred_at=parse_datetime(row["occurred_at"]),
            source_system=row["source_system"],
            mission_id=row["mission_id"],
            node_id=row["node_id"],
            parent_id=row["parent_id"],
            action_id=row["action_id"],
            attributes=json.loads(row["attributes_json"]),
        )
