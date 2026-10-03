# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Patch set **PS-008** covers the observability/alerting findings from run
`20261003-0018-fix-trust-root-87532ec` (audit report `14_observability_monitoring_incident_readiness.md`).

- Audit run: `20261003-0018-fix-trust-root-87532ec`
- Patch set: `PS-008`
- Repo / base: `falcon-edge` @ `origin/main` (`f5811d1`)
- Findings: `OBS-P2-001`, `OBS-P2-002`

Both findings were re-verified against current `origin/main`: they **still reproduce** —
`docs/CURRENT_STATE.md` still states there is no Alertmanager, and
`automation/validation/inventory_metrics.py` is still a host-side SSH collector.

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `OBS-P2-002` | P2 | open -> partially fixed | The inventory metrics collector is still the single host-side vantage. This PR adds collector self-health metrics and makes the alert rules distinguish "collector down" from "sensor down" (the finding's own suggested validation). Per-sensor self-export remains an agent-plumbing item. |
| `OBS-P2-001` | P2 | open (deferred) | A real fix needs an Alertmanager / Grafana-alerting receiver for `severity=critical`, owned by the monitoring program. **No receiver is fabricated here.** The audit's open question ("Is a central Alertmanager planned?") is recorded. The recommendation's "alert path alive heartbeat" is inert without a receiver, so no no-op rule was added (the rule set stays at 21). |

## Changes

| File | What changed |
|---|---|
| `automation/validation/inventory_metrics.py` | Emits collector self-health on every run, independent of any sensor read: `falcon_edge_inventory_collector_ok`, `_collector_last_run_timestamp`, `_collector_sensors_ok` / `_sensors_total`, and `_collector_errors_total{reason="db"|"ssh"}`. Empty-label series are now written without an empty `{}` label set. |
| `config/prometheus/edge-alerts.yaml` | `EdgeInventoryStale` / `EdgeInventoryUnreadable` are gated on a fresh collector heartbeat (2 h), so a host/collector outage no longer fires per-sensor alerts. `EdgeInventoryExporterDown` also fires when the collector heartbeat is stale and tightens from 3 h to 30 m. Rule count unchanged (21). |
| `tests/phase9/test_inventory_metrics.py` | New unit test: a completed collector pass that cannot read a DB reports `collector_ok=1` with `scan_ok=0`. |
| `docs/runbooks/fleet-inventory.md` | Documents the collector-vs-sensor series and semantics. |

## Verification Performed

All commands ran on the **edge-builder VM** (`172.23.128.52`, Ubuntu 24.04, Python 3.12.3,
pytest 7.4.4, gitleaks 8.30.1) against a `git archive --format=tar.gz` of the committed branch
(preserves modes/LF); raw output and exit codes are in `remediation/PS-008/verify.log`.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `python3 -m pytest -q tests/phase2 tests/phase3` | edge-builder VM (pytest 7.4.4) | 0 (129 passed) | `remediation/PS-008/verify.log` |
| `python3 -m pytest -q tests/phase9/test_inventory_metrics.py` | edge-builder VM | 0 (3 passed) | `remediation/PS-008/verify.log` |
| `python3 -m pytest -q tests/phase8 tests/phase9` | edge-builder VM | 0 (27 passed) | `remediation/PS-008/verify.log` |
| `bash ci/validate.sh` | edge-builder VM | 0 (`validation: ALL PASS`) | `remediation/PS-008/verify.log` |
| python YAML + structural parse of `edge-alerts.yaml` (`promtool` not installed) | edge-builder VM (pyyaml 6.0.1) | 0 (21 rules, each with alert/expr/for/severity/runbook) | `remediation/PS-008/verify.log` |
| `gitleaks detect --no-git --redact --source . -v` | edge-builder VM (gitleaks 8.30.1) | 0 (no leaks found) | `remediation/PS-008/verify.log` |

**Not run:** the patch plan's end-to-end check "synthetic critical alert delivered end-to-end"
(OBS-P2-001) — it requires the monitoring program's delivery stack, which is absent on the
verification VM and is an owner decision. Recorded as `not run`, not asserted.

- Secret scan: **pass** — "no leaks found".
- Scope check: **pass** — `config/prometheus/edge-alerts.yaml`, `automation/validation/inventory_metrics.py`
  (the two patch-set files) plus the Phase-9 regression test and the fleet-inventory runbook.

## Evidence bundle

- `remediation/PS-008/diff.patch` — SHA-256 `a9569f81e414f401c8605e2116883498c00ef8b00343febf46d19852674455a1`
- `remediation/PS-008/manifest.json`
- `remediation/PS-008/verify.log`

## Risk and rollback

- Risk: **low**. The change is additive metrics plus a tightened/gated alert expression; no API,
  schema, dependency, or runtime service changes, and the rule count is unchanged. A collector
  that keeps running but reads no sensor now reports `collector_ok=1` with `sensors_ok=0` instead
  of only per-sensor zeros.
- Rollback: `git revert` restores the prior expressions and drops the collector series; the
  existing deployed rules (21) are untouched until `deploy_edge_alert_rules.sh` is re-run.

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Open questions

- **OBS-P2-001 — is a central Alertmanager planned, or should the edge rules move to Grafana
  unified alerting?** The monitoring program's delivery path is Grafana-managed alerts ->
  relay `:9099` -> ntfy; the edge rules sit in Prometheus with no Alertmanager, so they never
  reach that path. Choosing and wiring the receiver (and its secret/topic) is an
  owner/monitoring-program decision; no receiver or secret is guessed in this PR.
- **OBS-P2-002 — can the sensors self-export inventory metrics (like the agent does)?** That is
  the durable fix that removes the host SSH single point of failure; it needs agent-plumbing
  design and is deferred from this in-repo patch.

## Definition of done (for this set)

From `patch_plan.md`: "synthetic critical alert delivered end-to-end". That end-to-end check is
**not run** because it needs the central delivery stack (owner decision). What is verified here is
the in-repo half of OBS-P2-002 and the supporting regression test; OBS-P2-001 remains open with the
owner question recorded.
