# 02_architecture_runtime_topology — Prompt 02 - Architecture and Runtime Topology Audit

- Run: `snowride-20261005-full-main-38b34a9`
- Target: `snowride` @ `38b34a9` (branch `main`)
- Domain: `02_architecture_runtime_topology.md` (area ARCH, prompt)

## Verification Performed

Topology: Next.js web (3000) + authoritative realtime (3001) + OTel collector + nginx, single certified host, internal bridge network. Compose now sets cpus/mem_limit/pids_limit on every app-facing service, read_only roots, no-new-privileges, cap_drop ALL, and json-file log rotation (ARCH-P2-001 fixed). Readiness is dependency-aware and cached (ARCH-P2-002 fixed, server.ts:719-743). Residual: authoritative lobby/LiveOps state is process-local; the durable LiveOps publish override is re-applied at boot (server.ts:751-765), which mitigates the operator freeze case but rooms/replay caches are still lost on restart.

## Findings

| ID | Severity | Title |
|---|---|---|
| ARCH-P3-001 | P3 | Authoritative room/lobby state is process-local and lost on restart |
