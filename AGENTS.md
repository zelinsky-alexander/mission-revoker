# MissionRevoker Agent Instructions

## Project objective

Build an independent revocation-assurance and downstream-effect reconciliation layer for heterogeneous AI-agent workflows.

## Non-goals

- Do not create a new agent identity or delegation-token protocol.
- Do not replace existing authorization gateways.
- Do not claim that an absent event proves an action did not occur.

## Engineering rules

1. Keep the core independent of vendor SDKs. Put integration-specific code under `src/mission_revoker/adapters/`.
2. Preserve explicit `UNKNOWN` states when evidence is incomplete.
3. Use UTC timestamps and stable identifiers for missions, tasks, actions, and effects.
4. Re-check revocation at execution time, not only when a request enters a queue.
5. Add unit tests for every new revocation or reconciliation invariant.
6. Avoid GPL, AGPL, SSPL, source-available, or otherwise restrictive dependencies unless explicitly approved.
7. Document every dependency's package name, license, purpose, maintenance status, and notable concern.
