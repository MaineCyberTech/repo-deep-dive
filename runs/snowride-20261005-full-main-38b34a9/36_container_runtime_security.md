# 36_container_runtime_security — Prompt 36 - Container Runtime Security Audit

- Run: `snowride-20261005-full-main-38b34a9`
- Target: `snowride` @ `38b34a9` (branch `main`)
- Domain: `36_container_runtime_security.md` (area CTR, prompt)

## Verification Performed

Container runtime: both apps build from digest-pinned node bases, run as uid 1001, exec-form HEALTHCHECK, and the compose overlay adds read_only root, tmpfs /tmp, cap_drop ALL, no-new-privileges, and resource limits. The deterministic scanner's two 'unpinned image' hits are the locally built certified tags (documented as build outputs).

## Findings

| ID | Severity | Title |
|---|---|---|
| CTR-P3-001 | P3 | App images use local mutable tags with no in-repo digest binding |
