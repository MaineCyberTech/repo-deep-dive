# 02_architecture_runtime_topology — Prompt 02 - Architecture and Runtime Topology Audit

- Run: `falcon-20261005-full-main-e267ce1`
- Target: `falcon` @ `e267ce1` (branch `main`)
- Domain: `02_architecture_runtime_topology.md` (area ARCH, prompt)

## Verification Performed

Domain subagent produced 4 finding(s) at the bound commit; machine IDs assigned by tools/full_domain.py.

## Findings

| ID | Severity | Title |
|---|---|---|
| ARCH-P1-001 | P1 | Single-host concentration: host loss is total pipeline loss |
| ARCH-P2-001 | P2 | Declared container hardening lags the running containers |
| ARCH-P2-002 | P2 | Wazuh and vendored MCT stacks run tag-only images outside pin/SBOM scope |
| ARCH-P2-003 | P2 | Live ingest authentication is a shared secret header, not mTLS |
