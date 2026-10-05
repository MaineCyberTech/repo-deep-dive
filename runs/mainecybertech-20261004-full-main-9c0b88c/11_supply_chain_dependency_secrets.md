# 11_supply_chain_dependency_secrets — Prompt 11 - Supply Chain, Dependency, and Secrets Audit

- Run: `mainecybertech-20261004-full-main-9c0b88c`
- Target: `mainecybertech` @ `9c0b88c` (branch `main`)
- Domain: `11_supply_chain_dependency_secrets.md` (area SC, prompt)

## Verification Performed

Reconciliation full-domain pass at main `9c0b88c` (2026-10-04). Baseline findings were carried from the repository's committed audit corpus and re-bound to this run: the `a97425d` verification ledger (ancestor of main, so its verified-fixed statuses hold here), the `178b91c` main-tip focused run, and the `20261002-0344` full run for domains the later ledgers did not cover. Each row cites its provenance. Machine deterministic checks are recorded in `lens_deterministic.md`.

## Findings

| ID | Severity | Title |
|---|---|---|
| SUPPLY-P3-001 | P3 | Unpinned container images (test/local only); production app images tag-based by design |
| SUPPLY-P3-002 | P3 | Dockerfile lint: missing WORKDIR in web runner stage and shell-form HEALTHCHECK |
| SC-P1-001 | P1 | Critical/high advisories persist in the dev dependency tree; `next` override is mis-scoped |
| SC-P2-001 | P2 | No image-level container scanning; Trivy scans filesystem only |
| SC-P2-002 | P2 | No artifact provenance, attestation, or signing; `id-token: write` requested but unused |
| SC-P2-003 | P2 | License policy not enforced in CI; non-OSI and LGPL licenses present |
| SC-P2-004 | P2 | SBOM is generated but not bound to a commit or attached to releases/images |
| SC-P2-005 | P2 | Dependabot PR backlog is large and not triaged; one stale update conflicts with resolved versions |
| SC-P3-001 | P3 | Root package license remains "ISC" |
| SC-P3-002 | P3 | e2e Docker image is not digest-pinned |
| SC-P3-003 | P3 | Secret-scanner pattern sets diverge between `.sh` and `.ps1` |
| SUPPLY-P2-001 | P2 | `licenses.json` is committed but unenforced and unverified |
| SUPPLY-P2-002 | P2 | Swagger UI loads an unpinned third-party script without SRI |
| SUPPLY-P3-003 | P3 | SBOM is produced as a transient artifact, not bound to a release |
| SUPPLY-P3-004 | P3 | A secrets file exists on disk outside git (should never be committed) |
