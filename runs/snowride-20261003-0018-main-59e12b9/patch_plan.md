# Patch Plan — Snowride @ 59e12b9

Concrete, implementation-ready changes. Every item names the file(s) and the finding it closes. No repository code was modified during the audit.

## P1 — this week

### P1-1 Re-attest and de-hardcode release identity
- Files: `infra/compose/docker-compose.yml`, `apps/realtime/src/config.ts`, release runbook.
- Change: remove the hardcoded `LAUNCH_OWNER_SIGNATURE` approval sentence; set `LAUNCH_ATTESTED_COMMIT`/`LAUNCH_MIGRATION_HEAD` to the released HEAD and `0056`; make the signature an out-of-band artifact verified cryptographically at gate evaluation.
- Closes: SEC-P1-001, DATA-P1-001, FINAL-P1-001.
- Validate: `/beta` reports the correct first unmet requirement on a tampered/stale identity.

### P1-2 Branch protection
- Action: require PR review + `foundation` and `migrations` checks on `main`; export a screenshot/JSON as evidence.
- Closes: CI-P1-001.
- Validate: a red-CI PR cannot merge.

### P1-3 SBOM in CI
- Files: `.github/workflows/ci-foundation.yml`.
- Change: `npx @cyclonedx/cyclonedx-npm --output-file sbom.json`; upload as artifact; retain per release.
- Closes: SUPPLY-P1-001, CI-P3-001.
- Validate: artifact downloadable for the commit.

### P1-4 Alerting as code
- Files: new committed schedule (cron/systemd timer) + alert thresholds; `docs/runbooks/INCIDENT.md`.
- Change: version the schedule and thresholds; add `ASSURANCE_DRILL=1` output to release evidence.
- Closes: OBS-P1-001.
- Validate: forced failure produces an ntfy alert after a clean rebuild.

## P2 — this month

| Patch | File(s) | Change | Finding |
|---|---|---|---|
| P2-1 | `.github/workflows/ci-foundation.yml` | run `supabase/tests/*.sql` after the dry-run | DATA-P2-001, TEST-P2-003 |
| P2-2 | workflow + new script | `npm audit --omit=dev` and pinned gitleaks on PRs | CI-P2-001, SEC-P2-002, SUPPLY-P2-001 |
| P2-3 | workflow | pin actions to SHAs | CI-P2-002 |
| P2-4 | `vitest.config.ts`, workflow | coverage + thresholds + artifact | TEST-P2-001 |
| P2-5 | `playwright.config.ts` | add firefox/webkit projects (mobile/a11y) | TEST-P2-002 |
| P2-6 | `infra/compose/docker-compose.yml` | `mem_limit`/`cpus`/`pids_limit` per service | ARCH-P2-001 |
| P2-7 | `apps/realtime/src/server.ts` | dependency probe in `/readyz` | ARCH-P2-002 |
| P2-8 | `apps/realtime/src/server.ts` | persist/restore `liveOpsOverrides` | ARCH-P2-003 |
| P2-9 | `apps/realtime/src/server.ts` | reject disallowed `Origin` on HTTP | SEC-P2-001 |
| P2-10 | `infra/otel/collector-config.yaml` | add retained/queryable trace exporter | OBS-P2-001 |
| P2-11 | new `SLO.md` + alerts | SLIs/SLOs/error budgets | OBS-P2-002 |
| P2-12 | workspace `package.json`s + root config | lint all packages | HYG-P2-001 |
| P2-13 | `docs/runbooks/BACKUP_RESTORE.md` | correct the freshness note; add RPO/RTO | HYG-P2-003, FINAL-P2-001 |
| P2-14 | `supabase/migrations/MANIFEST.sha256` + CI | checksum manifest + head-equality check | DATA-P2-002, DATA-P1-001 |
| P2-15 | `docs/API.md` + test | route/event parity snapshot | API-P2-001 |
| P2-16 | `infra/compose/docker-compose.yml` / `.env.example` | document production flag overrides | FEAT-P2-001 |

## P3 — this quarter

| Patch | File(s) | Change | Finding |
|---|---|---|---|
| P3-1 | `package.json` | fix `test:unit` glob | TEST-P3-001 |
| P3-2 | `scripts/verify-all.sh` | align with CI / document delta | TEST-P3-002 |
| P3-3 | `.gitignore` / evidence | reconcile tracked `.log`; move to `.txt` | INV-P3-001 |
| P3-4 | root | re-home `ext_review.md`, `reviewer.md`, PDF, etc. | INV-P3-002 |
| P3-5 | `evidence/` | remove 2 of 3 repomix copies; size budget | INV-P2-001, HYG-P2-002 |
| P3-6 | `apps/realtime/src/server.ts` | derive `deployed` in `/launch-readiness` | FEAT-P3-001 |
| P3-7 | SQL migrations | explicit `current_user` trust check in `social_guard_*` | SEC-P3-001 |
| P3-8 | compose | service-role key as Docker secret | SEC-P3-002 |
| P3-9 | `.github/dependabot.yml` | security-update grouping | SUPPLY-P3-001 |
| P3-10 | root | add `.gitattributes`; release versioning/changelog | HYG-P3-001/002 |
| P3-11 | `SECURITY.md` | document current signature semantics + SBOM process | SEC-P1-001, SUPPLY-P1-001 |

## Verification plan

1. `bash scripts/verify-all.sh` green.
2. CI (`foundation`, `migrations`, `e2e`) green with the new steps.
3. Re-run this audit in verification mode at the new commit; target status `verified-fixed` for all P1s.
