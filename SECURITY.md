# Security Policy

MissionRevoker is pre-alpha research software. Do not rely on it as the only control protecting production agent actions.

## Reporting a vulnerability

Please report suspected vulnerabilities privately to the repository owner rather than opening a public issue that includes exploit details.

## Security assumptions

- External adapters and target systems may omit or falsify events.
- A successful revocation API response is not proof that downstream effects stopped.
- The verifier reports `UNKNOWN` when evidence is incomplete.
- Demo signing and storage are not a production key-management or tamper-proof logging system.
