# Third-Party Notices

MissionRevoker contains original project code and does not vendor third-party source code.

## Build dependency

- **setuptools** - MIT License. Used only as the Python package build backend. It is broadly maintained by the Python Packaging Authority. Main concern: build tooling should be kept patched; it is not a runtime dependency of MissionRevoker.

## Optional external evaluation targets

The experiment guide refers to external projects that are not copied, bundled, linked, or required by MissionRevoker:

- AWS `sample-agentic-delegation` - MIT-0
- Microsoft Agent Governance Toolkit - MIT
- Agent Gateway - Apache-2.0
- Alibaba Open Agent Auth - Apache-2.0
- Agent Passport System - Apache-2.0

Users must review each external project's current license and security posture before installation. This notice is informational and does not incorporate those projects into this repository.

## Code provenance note

The implementation in this repository was written as an original scaffold around standard Python APIs and conventional graph, event, SQLite, and command-line patterns. It should still receive normal legal, security, and similarity review before commercial publication or production deployment.
