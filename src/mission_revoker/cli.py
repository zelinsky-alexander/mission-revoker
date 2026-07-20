"""MissionRevoker command-line interface."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .demo import demo_events
from .graph import MissionGraph
from .io import load_jsonl
from .models import Node, NodeKind, NodeStatus
from .reconciliation import Reconciler
from .report import render_json, render_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mission-revoker",
        description="Verify revocation propagation and reconcile agent actions with downstream effects.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    demo_parser = subparsers.add_parser("demo", help="run the deterministic local demonstration")
    demo_parser.add_argument("--json", action="store_true", help="emit JSON instead of text")

    verify_parser = subparsers.add_parser("verify", help="verify canonical JSONL events")
    verify_parser.add_argument("events", type=Path)
    verify_parser.add_argument("--mission", help="mission ID; defaults to the first event")
    verify_parser.add_argument("--json", action="store_true")

    graph_parser = subparsers.add_parser("graph", help="show a basic graph projection from JSONL events")
    graph_parser.add_argument("events", type=Path)
    graph_parser.add_argument("--mission", help="mission ID; defaults to the first event")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "demo":
        report = Reconciler().reconcile(demo_events(), "mission-demo")
        print(render_json(report) if args.json else render_text(report))
        return 0 if report.overall == "TRUSTED" else 2

    events = load_jsonl(args.events)
    if not events:
        raise SystemExit("no events found")
    mission_id = args.mission or events[0].mission_id

    if args.command == "verify":
        report = Reconciler().reconcile(events, mission_id)
        print(render_json(report) if args.json else render_text(report))
        return 0 if report.overall == "TRUSTED" else 2

    if args.command == "graph":
        graph = _project_graph(events, mission_id)
        print(json.dumps(graph.to_dict(mission_id), indent=2, sort_keys=True))
        return 0

    raise AssertionError(f"unhandled command: {args.command}")


def _project_graph(events, mission_id: str) -> MissionGraph:
    graph = MissionGraph()
    graph.add_node(
        Node(
            node_id=mission_id,
            mission_id=mission_id,
            kind=NodeKind.MISSION,
            source_system="canonical",
        )
    )
    seen: set[str] = {mission_id}
    for event in events:
        if event.mission_id != mission_id or not event.node_id or event.node_id in seen:
            continue
        graph.add_node(
            Node(
                node_id=event.node_id,
                mission_id=mission_id,
                kind=NodeKind.ACTION if event.action_id else NodeKind.TASK,
                source_system=event.source_system,
                parent_id=event.parent_id or mission_id,
                status=NodeStatus.UNKNOWN,
            )
        )
        seen.add(event.node_id)
    return graph


if __name__ == "__main__":
    raise SystemExit(main())
