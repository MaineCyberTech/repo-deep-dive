# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Patch set **PS-010** covers the fleet-inventory data-at-rest / raw-identifier exposure finding from
run `20261003-0018-fix-trust-root-87532ec` (audit report `06_security_authz_tenancy_audit.md`).

- Audit run: `20261003-0018-fix-trust-root-87532ec`
- Patch set: `PS-010`
- Repo / base: `falcon-edge` @ `origin/main` (`f5811d1`)
- Findings: `SEC-P2-003`

The finding was re-verified against current `origin/main` and **still reproduces**: the on-sensor
SQLite DB was created world-readable (`0644`), and `show`/`associate` printed raw MAC/IP.

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `SEC-P2-003` | P2 | open -> fixed (draft PR) | The DB directory and SQLite files are now created owner-only (`0700`/`0600`), and `show`/`associate` hash MAC/IP by default with an explicit `--raw` opt-in. An already-loose DB is tightened on the next write. |

## Changes

| File | What changed |
|---|---|
| `automation/validation/fleet_inventory.py` | `open_db()` creates the DB directory `0700` and, via the new `restrict_db_permissions()`, tightens `inventory.db` and its `-wal`/`-shm` to `0600` (also on an existing loose DB). New `hash_identifier()` is shared by `export`. `show` and `associate` hash MAC/IP unless `--raw` is passed. Usage docstring updated. |
| `tests/phase9/test_fleet_inventory.py` | New tests: owner-only dir/DB mode, tightening a pre-existing `0644` DB, `show`/`associate` hashed-by-default and `--raw`. |
| `docs/runbooks/fleet-inventory.md` | Documents the owner-only DB, the hashed `show`/`associate` output and `--raw`. |
| `docs/TROUBLESHOOTING.md` | Corrects the now-stale "group-writable 0775 / read as any user" guidance for the inventory DB. |

## Verification Performed

All commands ran on the **edge-builder VM** (`172.23.128.52`, Ubuntu 24.04, Python 3.12.3,
pytest 7.4.4, gitleaks 8.30.1) against a `git archive --format=tar.gz` of the committed branch
(preserves modes/LF); raw output and exit codes are in `remediation/PS-010/verify.log`.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `python3 -m pytest -q tests/phase2 tests/phase3` | edge-builder VM | 0 (129 passed) | `remediation/PS-010/verify.log` |
| `python3 -m pytest -v tests/phase9/test_fleet_inventory.py` | edge-builder VM | 0 (15 passed) | `remediation/PS-010/verify.log` |
| `python3 -m pytest -q tests/phase9` | edge-builder VM | 0 (19 passed) | `remediation/PS-010/verify.log` |
| `bash ci/validate.sh` | edge-builder VM | 0 (`validation: ALL PASS`) | `remediation/PS-010/verify.log` |
| `gitleaks detect --no-git --redact --source . -v` | edge-builder VM (gitleaks 8.30.1) | 0 (no leaks found) | `remediation/PS-010/verify.log` |

Base reproduction on the same VM (archive of `origin/main`): DB file mode `0644`; `show` printed
the raw MAC and IP. Patched check: DB file `0600`, directory `0700`; `show` default has no raw
identifiers and `show --raw` restores them. Both recorded in `verify.log`.

- Secret scan: **pass** — "no leaks found".
- Scope check: **pass** — `automation/validation/fleet_inventory.py` (the patch-set file) plus the
  Phase-9 tests and the two docs that documented the old world-readable/raw behaviour.

## Evidence bundle

- `remediation/PS-010/diff.patch` — SHA-256 `b307848386941f70599da0e98a498d369cf218c9c65575ae74bd56ecb6996194`
- `remediation/PS-010/manifest.json`
- `remediation/PS-010/verify.log`

## Risk and rollback

- Risk: **low-medium**. This is deliberate hardening. The main behavioural change is that a
  non-owner account can no longer read the inventory DB; the hourly lab-host
  `inventory_metrics.py` unit reads the DB directly, so if it does not run as the owning account
  it will report the sensor unreadable until ownership is reconciled (flagged as an open question
  below). `show`/`associate` output is hashed unless `--raw`, which is a usability change for
  operators. No API, schema, or dependency changes.
- Rollback: `git revert <sha>` restores the previous permissions/hashing behaviour.

## Review checklist

- [ ] Diff touches only the patch-set file (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Open questions

- **Which account owns/reads the inventory DB?** The finding's dependency is owner authorization
  (ED-20). The tool now creates the DB (and directory) owner-only; the daily `falcon-inventory`
  scan runs as root, while the hourly `inventory_metrics.py` lab-host unit reads the same file
  directly. If that unit is not root/the owning account, it must be moved to the owning account or
  granted group access (e.g. `root:falcon` `0640`) as an owner decision — the fix deliberately
  does not jump to group-readable, because the finding asks to restrict beyond the owning account.
- **Deployed systemd units.** The repo has no `falcon-inventory.service`/`.timer` file (units are
  installed per host; see `docs/ENVIRONMENTS.md`). If the install step or `ReadWritePaths` sets
  directory modes, reconcile it with the new `0700`/`0600` defaults when rolling out.
- **`changes` output.** The finding's recommended fix names `show`/`associate` only; `changes`
  still prints raw MAC/IP. Left unchanged here to keep scope minimal and is a candidate follow-up
  (also raised as PRIV-P3-001 in the earlier `20261002-0630` run).

## Definition of done (for this set)

From `patch_plan.md`: "DB mode/ownership test". The Phase-9 tests assert `0700`/`0600` on create
and tighten a pre-existing `0644` DB; the functional check on edge-builder confirms the same and
that hashed output is the default.
