# 36_container_runtime_security — Prompt 36 - Container Runtime Security Audit

- Run: `falcon-20261005-full-main-e267ce1`
- Target: `falcon` @ `e267ce1` (branch `main`)
- Domain: `36_container_runtime_security.md` (area CTR, prompt)

## Verification Performed

Domain subagent produced 1 finding(s) at the bound commit; machine IDs assigned by tools/full_domain.py.

## Findings

| ID | Severity | Title |
|---|---|---|
| CTR-P3-001 | P3 | Vendored MCT compose mounts docker.sock and uses floating tags under a blanket waiver |
