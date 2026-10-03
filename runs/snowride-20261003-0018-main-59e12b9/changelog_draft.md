# Changelog Draft — Snowride hardening

## [Unreleased] — audit 20261003-0018-main-59e12b9

### Security
- Enforce cryptographic release attestation; remove committed approval string (SEC-P1-001).
- Add repository-tree secret scanning and per-PR dependency audit to CI (SEC-P2-002, CI-P2-001).
- Validate `Origin` on browser-facing HTTP endpoints (SEC-P2-001).
- Pin GitHub Actions to commit SHAs (CI-P2-002).

### Data
- Pin `LAUNCH_MIGRATION_HEAD` to the repo head and add a head-equality CI check (DATA-P1-001).
- Run `supabase/tests/*` negative/RLS suites in CI (DATA-P2-001).
- Add a migration checksum manifest (DATA-P2-002).

### Supply chain
- Generate and bind a CycloneDX SBOM per release (SUPPLY-P1-001).
- Move license/OSV enforcement into CI (SUPPLY-P2-001).
- Document/verify install-script allowlist (SUPPLY-P2-002).

### Reliability / Observability
- Add container resource limits (ARCH-P2-001).
- Dependency-aware `/readyz` (ARCH-P2-002).
- Persist LiveOps kill-switch overrides across restarts (ARCH-P2-003).
- Commit alert schedule/rules; define SLOs and RPO/RTO; add trace retention (OBS-P1-001/002, OBS-P2-001/002).

### Quality / Hygiene
- Lint all workspaces (HYG-P2-001).
- Coverage thresholds + Firefox/WebKit e2e (TEST-P2-001/002).
- Fix `test:unit`; align local and CI gates (TEST-P3-001/002).
- De-duplicate repomix/PDF artifacts; reconcile `.gitignore`; add `.gitattributes`; correct `BACKUP_RESTORE.md` (INV-P2-001, INV-P3-001, HYG-P2-002/003, HYG-P3-002).
