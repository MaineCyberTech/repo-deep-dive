# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Patch set **PS-001** makes revocation/retirement a **terminal trust-root state** on the
control-plane enrollment path. Previously `h_enroll` never inspected the existing sensor's
lifecycle: a bootstrap token bound to a REVOKED (or RETIRED) sensor, or a re-enrollment by the
original `deviceUuid`, would issue a fresh certificate and set the sensor back to `CONFIGURING`,
silently undoing revocation.

`h_enroll` now resolves the target sensor (both the device-`deviceUuid` branch and the
token-bound-incumbent branch) and refuses with `403 SENSOR_REVOKED` / `403 SENSOR_RETIRED`
before any certificate is issued or token redeemed. This restores the documented C6
"revocation is terminal" intent and closes the consolidated release blockers.

- Audit run: `20261003-0018-fix-trust-root-87532ec`
- Patch set: `PS-001` — terminal revocation trust-root
- Repo / base: `falcon-edge` @ `origin/main` (`af6f83a`)

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `SEC-P1-001` | P1 | open -> fixed | Re-enrollment of a REVOKED/RETIRED sensor is now refused (403). |
| `FINAL-P1-001` | P1 | open -> fixed | Consolidated release blocker: revocation is now terminal on the enrollment path. |
| `EXEC-P1-001` | P1 | open -> fixed | Release-gate condition "revocation must be terminal" satisfied by the guard. |
| `TEST-P2-002` | P2 | open -> fixed | Added integration regression test covering REVOKED and RETIRED re-enrollment. |

## Changes

| File | What changed |
|---|---|
| `src/falcon_control/service.py` | `h_enroll`: track the target sensor's `lifecycle_state` (`existing` and `incumbent` branches) and return `403 SENSOR_REVOKED`/`SENSOR_RETIRED` before redeeming the token or issuing a certificate. |
| `tests/phase2/test_service_integration.py` | Added `test_re_enrollment_of_revoked_or_retired_sensor_is_refused` (+ `enrollment_body` helper). |

## Verification Performed

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `python3 -m pytest -q tests/phase2` | edge-builder VM | not run | No pytest module in the lab image (`No module named pytest`). Recorded in `verify.log`. |
| `python3 -m unittest discover -s tests/phase2 -t . -v` | edge-builder VM | 0 (74 tests OK) | `remediation/PS-001/verify.log` |
| `gitleaks detect --no-git --redact --source . -v` | edge-builder VM | 0 (no leaks found) | `remediation/PS-001/verify.log` |

- Secret scan (gitleaks 8.30.1): **pass** — "no leaks found".
- Scope check (files within patch set): **pass** — only `src/falcon_control/service.py` and
  `tests/phase2/test_service_integration.py` changed.

Focused behaviour confirmed by the new test in the lab: re-enrollment by original `deviceUuid`
and by a new `deviceUuid` with a sensor-bound token both return `403 SENSOR_REVOKED`; a
RETIRED sensor returns `403 SENSOR_RETIRED`; the state remains terminal; the refusal happens
before token redemption (a second attempt is refused identically, not `TOKEN_REDEEMED`).

## Evidence bundle

- `remediation/PS-001/diff.patch` — SHA-256 `b71cf6b1c8a826214e9831a723b100a529d8cd22ccf9e59abf9a49443e801045`
- `remediation/PS-001/manifest.json`
- `remediation/PS-001/verify.log`

## Risk and rollback

- Risk: low. The change only adds a fail-closed check on existing/incumbent enrollment; new
  sensor enrollment is unchanged, and non-terminal states (`CONFIGURING`/`ACTIVE`/`QUARANTINED`/
  `SUSPENDED`) still renew as before.
- Rollback: `git revert 63f0fce` reverts the guard; keep the test (it documents intended behavior).

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Definition of done (for this set)

From `patch_plan.md`: `python -m unittest tests.phase2.test_service_integration`;
re-enroll REVOKED returns 403/409.
