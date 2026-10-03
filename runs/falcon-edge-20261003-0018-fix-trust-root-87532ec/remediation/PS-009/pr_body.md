# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Patch set **PS-009** covers the inventory-metrics-collector security and hygiene findings from run
`20261003-0018-fix-trust-root-87532ec` (audit reports `06_security_authz_tenancy_audit.md` and
`21_repo_hygiene_maintainability.md`).

- Audit run: `20261003-0018-fix-trust-root-87532ec`
- Patch set: `PS-009`
- Repo / base: `falcon-edge` @ `origin/main` (`f5811d1`)
- Findings: `SEC-P2-002`, `HYG-P3-001`

Both findings were re-verified against current `origin/main` and **still reproduce**:
`automation/validation/inventory_metrics.py` still ran SSH with `StrictHostKeyChecking=no` and
still hardcoded the `SENSORS` endpoint/key list.

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `SEC-P2-002` | P2 | open -> fixed | The collector now pins sensor host keys: `StrictHostKeyChecking=yes` with an explicit `UserKnownHostsFile` (`known_hosts` in the config; default `/home/user/.ssh/known_hosts`). A changed/wrong host key is refused, and an absent known_hosts fails closed (every sensor reports `scan_ok 0`) instead of accepting any key. |
| `HYG-P3-001` | P3 | open -> fixed | The hardcoded `SENSORS` list and delivery-key literals are gone; endpoints/keys are read from a single config file, `config/fleet-sensors.json` (`--config` / `FALCON_FLEET_SENSORS` override). |

## Changes

| File | What changed |
|---|---|
| `automation/validation/inventory_metrics.py` | `load_config()` reads sensors + known_hosts from JSON; `ssh_command()` builds the read-only SSH query with `UserKnownHostsFile` + `StrictHostKeyChecking=yes` + `BatchMode=yes`; `collect()` takes sensors/known_hosts and fails closed when known_hosts is missing; SSH failure reasons are surfaced to stderr. New `--config` / `--known-hosts` options. |
| `config/fleet-sensors.json` | New single source of truth: the three sensors (name/host/key) and the `known_hosts` path. Endpoint/key values are preserved verbatim from the old literals. |
| `tests/phase9/test_inventory_metrics.py` | Tests: config drives sensor targets; the SSH command pins the host key (never `no`); a wrong host key fails closed; a missing known_hosts fails closed without invoking SSH. `test_ssh_command_pins_host_key` is a pure unit test. |
| `docs/ENVIRONMENTS.md` | Relocation table updated: targets/keys are config data, and a host-key-pinning row records the known_hosts behaviour. |
| `docs/runbooks/fleet-inventory.md` | Documents the sensor config and the fail-closed host-key pinning. |

## Verification Performed

All commands ran on the **edge-builder VM** (`172.23.128.52`, Ubuntu 24.04, Python 3.12.3,
pytest 7.4.4, gitleaks 8.30.1) against a `git archive --format=tar.gz` of the committed branch
(preserves modes/LF); raw output and exit codes are in `remediation/PS-009/verify.log`.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `python3 -m pytest -q tests/phase2 tests/phase3` | edge-builder VM (pytest 7.4.4) | 0 (129 passed) | `remediation/PS-009/verify.log` |
| `python3 -m pytest -v tests/phase9/test_inventory_metrics.py` | edge-builder VM | 0 (7 passed) | `remediation/PS-009/verify.log` |
| `python3 -m pytest -q tests/phase9` | edge-builder VM | 0 (19 passed) | `remediation/PS-009/verify.log` |
| `bash ci/validate.sh` | edge-builder VM | 0 (`validation: ALL PASS`) | `remediation/PS-009/verify.log` |
| `gitleaks detect --no-git --redact --source . -v` | edge-builder VM (gitleaks 8.30.1) | 0 (no leaks found) | `remediation/PS-009/verify.log` |

**Not run:** a live sensor SSH read with a real wrong host key. The sensors are not reachable from
the verification VM, and pinning real host keys would require committing lab key material; instead
the fail-closed behaviour is exercised in-process with a stand-in OpenSSH that enforces
`StrictHostKeyChecking=yes` + known_hosts. Recorded as `not run`, not asserted.

- Secret scan: **pass** — "no leaks found".
- Scope check: **pass** — `automation/validation/inventory_metrics.py` (the patch-set file) plus the
  config file the finding's recommended fix requires, the Phase-9 regression tests, and the two
  docs that described the old hardcoded targets.

## Evidence bundle

- `remediation/PS-009/diff.patch` — SHA-256 `3461cc80e2ae51b758aa243edb05d989286ec09047dbec25f5cd9221f0310a3e`
- `remediation/PS-009/manifest.json`
- `remediation/PS-009/verify.log`

## Risk and rollback

- Risk: **low-medium**. The behavioural change is deliberate hardening: if the lab host's
  `/home/user/.ssh/known_hosts` lacks a sensor key (e.g. after a reflash), that sensor now reports
  `scan_ok 0` until the key is re-pinned — previously it would have silently accepted the new key.
  This is the intended fail-closed behaviour and is documented in the runbook. No API, schema,
  dependency, or other runtime service changes.
- Rollback: `git revert` restores the previous `StrictHostKeyChecking=no` + hardcoded list; the
  config file becomes unused.

## Review checklist

- [ ] Diff touches only the patch-set file (+ the config/tests/docs the fix requires)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Open questions

- **SEC-P2-002 — which known_hosts does the deployed unit use?** The default is
  `/home/user/.ssh/known_hosts` (where `AGENTS.md` says the sensor host keys are tracked). If the
  hourly unit runs as a different user or in a sandbox that hides the home directory, pass
  `--known-hosts` / set the `known_hosts` key in the config. Also: should the collector repin the
  Zero W's changed host key (live ED25519 `SHA256:Xf5z+3KyFbAGwh8wzsjdJpfSq15eXBEfMCOi2GZtT9I`) in
  the lab known_hosts as part of the rollout?
- **HYG-P3-001 — canonical sensor addresses (LAN vs tunnel).** The config preserves the previous
  values verbatim (`3b` -> `10.11.12.158`, `3bplus` -> `10.99.0.32`, `zero` -> `10.11.12.211`).
  README/`AGENTS.md` describe the WireGuard tunnel addresses (`10.99.0.30/31/32`), and the Zero's
  LAN address is `10.11.12.211`. Which address is canonical for the collector is a lab/owner
  decision and was not guessed here; with the values now in one config file, changing them is a
  one-line edit.

## Definition of done (for this set)

From `patch_plan.md`: "wrong host key fails closed; sensors loaded from config". Both halves are
covered by the Phase-9 tests above; the collector-level fix is verified, and the two remaining
lab/owner decisions (the deployed known_hosts path and the canonical addresses) are recorded as
open questions rather than guessed.
