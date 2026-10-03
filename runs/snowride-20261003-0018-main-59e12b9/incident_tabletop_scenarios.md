# Incident Tabletop Scenarios — Snowride

Derived from `docs/runbooks/INCIDENT.md`, `KILL_SWITCHES.md`, `ROLLBACK.md`, `CERT_TLS.md`, `BACKUP_RESTORE.md`.

## S1 — Leaderboard compromise / score exploit
- Detection: `classificationFailures`, `snowride_realtime_runs_rejected_total`, admin submissions view, reopen signal.
- First move: `COMPETITIVE_ELIGIBILITY_MODE=off` (freeze ranked publishing); raise `leaderboard_compromise`; snapshot affected run IDs.
- Recovery: inspect run inspector, `LEDGER_VALIDATION_MODE`/`SESSION_STREAM_MODE` to enforce once shadow counters are clean.
- Gap: flags/flip require container recreate (process-local override lost on restart — ARCH-P2-003).

## S2 — Dependency outage (Supabase/JWKS unreachable)
- Detection: `/runs` 5xx, auth-failure storm.
- First move: confirm `/readyz` is misleading (ARCH-P2-002) — it currently stays ready.
- Recovery: verify JWKS/issuer; restore connectivity; redeploy if needed.

## S3 — Host resource exhaustion / disk full
- Detection: `/admin/ops`, assurance disk lane (`exit 12`), host alerts.
- First move: `scripts/assurance/reclaim-disk.sh`; stop non-essential services.
- Gap: no container resource limits (ARCH-P2-001); alerting is host-crontab only (OBS-P1-001).

## S4 — TLS certificate expiry / proxy misroute
- Detection: external probe failure; assurance cert-days lane (<14 d → exit 3).
- Recovery: `CERT_TLS.md` renew + `nginx -t && nginx -s reload`.

## S5 — Data loss / restore
- Detection: corruption or accidental delete.
- Recovery: `BACKUP_RESTORE.md` restore into scratch first; restore production; re-check `/admin/ops`.
- Gap: no documented RPO/RTO (FINAL-P2-001).

## Cross-cutting gaps

- No committed alert rules/SLOs (OBS-P1-001/002).
- No on-call rotation artifact in repo.
