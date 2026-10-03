# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Makes the monitoring dead-man path independent of the node-exporter textfile collector and
adds a textfile-independent alert on lost monitoring scrape jobs.

- Audit run: `20261003-0018-fix-backup-abort-markers-20b5e57`
- Patch set: `PATCH-4` - Monitoring-death independence (`OBS-P0-001`)
- Repo / base: `falcon` @ `main` (`430da82`)
- Branch: `remediation/PATCH-4-20261003-0018-fix-backup-abort-markers-20b5e57`
- Commit: `ee883646a6cb9b08b14d24bbcb72f185150de959`

The audited finding reported that Prometheus scraped only three targets and nearly all
`falcon_*` signals (including the monitoring-death path) depended on the node-exporter
textfile collector. The direct scrape portion was already landed on `main` by `65e18f1`
(vector-aggregator and grafana scraped directly); this branch adds the still-missing
independence of the dead-man itself and a scrape-level alert. This is stated honestly rather
than re-landing `65e18f1`.

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `OBS-P0-001` | P0 | open -> partially-fixed (open draft PR) | Direct scrapes already present on main (`65e18f1`); this adds independent heartbeat publish + `absent(up{...})` rule + regression test |

## Changes

| File | What changed |
|---|---|
| `automation/validation/heartbeat.sh` | Publishes the liveness heartbeat to the independent ntfy failure domain in addition to the lab topic, using the relay's user agent; independent credentials are optional and best effort. Adds env overrides for the offline test. No secrets printed. |
| `bootstrap/90-alerting.sh` | Adds `falcon-monitoring-scrape-absent`: fires on the scraped `up{}` series itself when `prometheus`/`node`/`vector-aggregator`/`grafana` disappears (not derived from the textfile). |
| `automation/validation/tests/heartbeat_independence_test.sh` | New offline regression: asserts the dual publish, the relay user agent, and that `heartbeat.sh` never references the textfile exporter. |

## Verification Performed

All commands ran on WSL `Ubuntu-24.04` in a clean LF git worktree (`/root/falcon-p4`) at
commit `ee883646a6cb9b08b14d24bbcb72f185150de959`, because the Windows checkout carries CRLF
line endings that break `bash -n`/the shell suites; a clean worktree applies the repository's
`eol=lf` attributes.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `bash -n automation/validation/heartbeat.sh` | WSL, clean worktree | 0 | `remediation/PATCH-4/verify.log` |
| `bash -n bootstrap/90-alerting.sh` | WSL, clean worktree | 0 | `remediation/PATCH-4/verify.log` |
| `bash -n automation/validation/tests/heartbeat_independence_test.sh` | WSL, clean worktree | 0 | `remediation/PATCH-4/verify.log` |
| `bash automation/validation/tests/heartbeat_independence_test.sh` | WSL, clean worktree | 0 (PASS) | `remediation/PATCH-4/verify.log` |
| `FALCON_EVIDENCE_OPTIONAL=1 python3 ci/validate.py --only parsers,shell-syntax,shell-tests` | WSL, clean worktree | 0 (31/31 suites) | `remediation/PATCH-4/verify.log` |
| `FALCON_EVIDENCE_OPTIONAL=1 python3 ci/validate.py` | WSL, clean worktree | 0 (`validation_failures=0`) | `remediation/PATCH-4/verify.log` |
| `gitleaks detect --no-git --source . --redact --config .gitleaks.toml` | WSL, gitleaks v8.30.1 (pinned sha256 verified) | 0 (no leaks found) | `remediation/PATCH-4/verify.log` |

Live validation (`stop the exporter timer; assert the staleness/absence rule fires`) was **not
run**: this audit/remediation host has no live Prometheus/Grafana stack. The rule is static
evidence only.

- Secret scan (gitleaks): pass (exit 0, "no leaks found"); `ci/validate.py` secret scan also passes.
- Scope check (files within patch set): pass - `bootstrap/90-alerting.sh`,
  `automation/validation/heartbeat.sh`, plus one regression test under
  `automation/validation/tests/`.

## Evidence bundle

- `remediation/PATCH-4/diff.patch` - SHA-256 `b9e56cdb2517174374978adc686e0c1b6551d68d6aa3f20c1c71c98f1f0abfcf`
- `remediation/PATCH-4/verify.log`
- `remediation/PATCH-4/manifest.json`

## Risk and rollback

- Risk: low. The heartbeat keeps its existing primary publish and only adds a best-effort
  independent publish; the alert rule is additive.
- Rollback: `git revert ee883646a6cb9b08b14d24bbcb72f185150de959` (or revert the three files).

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Definition of done (for this set)

Stop the exporter timer and assert a `falcon_*_last_run` staleness rule fires within the
configured window. Static rule + tests added here; **live firing proof remains for the lab**
(no live Prometheus/Grafana on the remediation host).
