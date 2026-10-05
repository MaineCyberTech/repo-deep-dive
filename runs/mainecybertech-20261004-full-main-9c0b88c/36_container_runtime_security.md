# 36_container_runtime_security — Prompt 36 - Container Runtime Security Audit

- Run: `mainecybertech-20261004-full-main-9c0b88c`
- Target: `mainecybertech` @ `9c0b88c` (branch `main`)
- Domain: `36_container_runtime_security.md` (area CTR, prompt)

## Verification Performed

Reconciliation full-domain pass at main `9c0b88c` (2026-10-04). Baseline findings were carried from the repository's committed audit corpus and re-bound to this run: the `a97425d` verification ledger (ancestor of main, so its verified-fixed statuses hold here), the `178b91c` main-tip focused run, and the `20261002-0344` full run for domains the later ledgers did not cover. Each row cites its provenance. Machine deterministic checks are recorded in `lens_deterministic.md`.

## Findings

| ID | Severity | Title |
|---|---|---|
| CTR-P1-001 | P1 | No Container Image Vulnerability Scan in CI |
| CTR-P1-002 | P1 | SBOM Is Lockfile-Only, Not an Image SBOM or Attestation |
| CTR-P1-003 | P1 | Unsigned Images With No Provenance/Attestation |
| CTR-P2-001 | P2 | Pinned Base-Image Digests Have No Automated Refresh |
| CTR-P2-002 | P2 | Local Compose Ships Default Credentials and Repo-Wide Bind Mount |
| CTR-P2-003 | P2 | Redis Password Exposed on Process Argument Vector |
| CTR-P2-004 | P2 | Deploy Health Gate Ignores Worker Health |
| CTR-P2-005 | P2 | No Container Resource/PID Limits Beyond Memory |
| CTR-P3-001 | P3 | Missing `--start-period` on API and Worker Healthchecks |
| CTR-P3-002 | P3 | Broad `.dockerignore` `*.md`/`*.txt`/`*.log` Could Mask Needed Build Files |
