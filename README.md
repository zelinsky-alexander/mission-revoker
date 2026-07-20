# MissionRevoker

MissionRevoker is a pre-alpha, open-source **revocation-assurance and downstream-effect reconciliation** scaffold for heterogeneous AI-agent workflows.

It does not try to replace agent identity systems, authorization gateways, MCP proxies, A2A runtimes, or policy engines. It consumes their events and answers a narrower operational question:

> After a human or operator revoked a mission, did every known descendant task, credential, queued action, retry, and real downstream effect actually stop?

## Current capabilities

- Canonical event model for missions, delegations, actions, revocations, cancellations, acknowledgements, and observed effects.
- Mission dependency graph with descendant and orphan discovery.
- Revocation fan-out through adapter interfaces.
- Four-stage action reconciliation: authorized, dispatched, acknowledged, observed.
- Post-revocation violation and evidence-gap detection.
- SQLite persistence using the Python standard library.
- Offline CLI demo and verifier.
- Adapter stubs for AGT-style audit events, APS-style receipts, OpenTelemetry spans, MCP calls, and A2A tasks.

## Architecture

```text
Existing agents / gateways / identity systems
          | events and revocation APIs
          v
+----------------------------------------+
| MissionRevoker                         |
|                                        |
|  Canonical event normalizer            |
|  Mission dependency graph              |
|  Revocation coordinator                |
|  Execution/effect reconciler           |
|  Evidence-gap and blast-radius report  |
+-------------------+--------------------+
                    |
                    v
        CLI / JSON report / future UI
```

## Quick start

Requirements: Python 3.12 or newer.

```powershell
py -3.12 -m venv .venv
.venv\Scripts\activate
python -m pip install -e .
mission-revoker demo
python -m unittest discover -s tests -v
```

On Linux or WSL2:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
mission-revoker demo
python -m unittest discover -s tests -v
```

## Example result

```text
Mission: mission-demo
Revoked at: 2026-07-20T10:00:00+00:00
Known descendants: 4
Post-revocation attempts: 1
Post-revocation observed effects: 1
Evidence gaps: 1
Overall: UNTRUSTED
```

## CLI

```text
mission-revoker demo
mission-revoker verify examples/demo-events.jsonl
mission-revoker graph examples/demo-events.jsonl
```

## Project layout

```text
src/mission_revoker/
  models.py          Canonical data model
  graph.py           Mission dependency graph
  store.py           SQLite event and node store
  revocation.py      Fan-out coordinator and adapter protocol
  reconciliation.py  Authorization-to-effect reconciliation
  report.py          Human-readable and JSON findings
  adapters/          Vendor/protocol normalization boundaries
  cli.py             Command-line interface
examples/
  demo-events.jsonl  Deterministic post-revocation scenario
tests/
  test_graph.py
  test_reconciliation.py
  test_revocation.py
docs/
  EXPERIMENT_PLAN.md
```

## Status and limitations

This repository is an experiment scaffold, not a finished security product.

- Adapters are deliberately minimal and do not claim full compatibility with upstream projects.
- The local event store is not a transparency log.
- The demo uses deterministic mock evidence rather than a real LLM.
- External-effect verification requires target-specific integrations.
- `UNKNOWN` is a valid and important result when coverage is incomplete.

## License

Apache License 2.0. See `LICENSE` and `THIRD_PARTY_NOTICES.md`.
