# Incident tabletop scenarios — snowride @ `38b34a9`

Companion artifact for `33_incident_tabletop_exercise.md`. Process authority is
`docs/runbooks/INCIDENT.md`; alert transport is ntfy.sh (operator only).
No committed tabletop transcript exists for this revision (`IR-P3-001`).

## Scenarios

| # | Scenario | Primary signals | First actions |
|---|---|---|---|
| 1 | Realtime service down | `/healthz` probe, ntfy watchdog | restart service, check `docker compose ps`, capture logs |
| 2 | Disk exhaustion | assurance `disk` lane (exit 12) | `scripts/assurance/reclaim-disk.sh`, prune images |
| 3 | Credential exposure (service-role/METRICS_TOKEN) | gitleaks / operator report | rotate secret, audit `admin_audit_events`, freeze publish |
| 4 | Score/ledger integrity incident | `LEDGER_VALIDATION_MODE` counters, admin signals | engage `LIVEOPS_KILL_PUBLISH`, snapshot evidence |
| 5 | TLS expiry | assurance TLS lane | acme.sh renew, nginx -t, reload |
| 6 | Database corruption | backup lane, restore drill | restore latest verified dump, reconcile |

## Exercise requirements

- Run at least scenarios 1, 3 and 6 per release candidate.
- Assign incident commander / comms / scribe; record timestamps in UTC.
- Append the transcript under `evidence/` and link it from the release gate.

## Exit criteria

- Roles and escalation timing demonstrated at the released commit.
- Any runbook gap found is filed as a finding in the next audit run.
