# MissionRevoker Local Experiment Plan

An illustrated PDF accompanies the initial scaffold deliverable and can also be kept under `docs/` for local reference.

## Objective

Demonstrate measurable added value over an authorization or governance product alone by verifying whether revocation actually propagated across heterogeneous components and whether any real effect occurred afterward.

## Recommended sequence

1. Run the MissionRevoker deterministic demo and unit tests.
2. Run the AWS secure-delegation sample locally as a baseline delegation fixture.
3. Normalize Microsoft Agent Governance Toolkit audit events.
4. Normalize Agent Passport System receipts and revocation state.
5. Add agentgateway in WSL2 as a real MCP/A2A traffic boundary.
6. Add Alibaba Open Agent Auth as a separate authorization target.
7. Run cached-credential, queued-action, asynchronous-task, bypass, misleading-receipt, and network-partition scenarios.
8. Compare baseline product-only results with product-plus-MissionRevoker results.

## Core metrics

- Descendant coverage
- Revocation enforcement latency
- Post-revocation attempts
- Post-revocation observed effects
- Cancellation success rate
- Reconciliation coverage
- Unknown-path count
- False cancellation rate
- Runtime overhead

## Safety rule

Never interpret missing evidence as proof that no action occurred. Report `UNKNOWN` when a path cannot be independently verified.
