# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Patch set **PS-018** is the final-register / release-readiness batch from run
`20261003-0018-fix-trust-root-87532ec`. `patch_plan.md` lists it as `mixed (see owners in
risk_register.md)`, so each finding was located in its owning domain report and fixed (or
explicitly deferred) there rather than in one file.

- Audit run: `20261003-0018-fix-trust-root-87532ec`
- Patch set: `PS-018` — release/hygiene final batch
- Repo / base: `falcon-edge` @ `origin/main` (`f5811d1`)

Every finding was re-checked against current `origin/main` first. **OBS-P3-001 is already fixed
at base** and needed no change. **TEST-P3-001** and **TEST-P3-002** still reproduce and are fixed
in code/CI here. The remaining six are owner-accepted or owner-decision findings; this PR records
dated dispositions and **open questions** (it deliberately does not guess an owner decision).

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `OBS-P3-001` | P3 | verified-fixed-at-base | Already fixed on `f5811d1`: `AGENTS.md` records the metric is expiry-aware since 2026-10-03, `store.pending_directive` filters `expires_at > now`, and `tests/phase8/test_observability.py::test_pending_directives_are_expiry_aware` locks it. No change needed. |
| `TEST-P3-001` | P3 | open -> fixed | Added a fail-closed `coverage report --fail-under=85` step after the informational report; measured baseline is 86%. |
| `TEST-P3-002` | P3 | open -> fixed | `changes`/`prune` accept an injectable `--now`; the phase9 fixture uses a fixed reference time instead of `datetime.now()`. |
| `CI-P2-001` | P2 | owner-accepted -> re-affirmed | Dated 2026-10-03 re-affirmation added to `docs/security/BRANCH_PROTECTION.md`; the D-011 decision still stands (plan-gated on GitHub Free). |
| `SC-P2-004` | P2 | owner-accepted (open question) | Disposition + open question recorded in `ledgers/risk_register.md` (R-021). Encryption/rotation/release-scoping needs an owner decision. |
| `ARCH-P2-002` | P2 | open (open question) | Availability dependency recorded; dedicated-host + break-glass is an owner/hardware decision (R-022). |
| `HYG-P3-002` | P2 | open (open question) | `LICENSE`/`pyproject.toml` absent; license choice is an owner decision, not guessed (R-023). |
| `EXEC-P2-001` | P2 | open (open question) | Production readiness stays `INSUFFICIENT_EVIDENCE`; P10 owner gates remain (R-024). |
| `FINAL-P2-001` | P2 | open (open question) | Cross-cutting source-binding theme; constituent fixes tracked (PS-005/PS-011/PS-017); drift check deferred until PS-011 lands (R-025). |

## Changes

| File | What changed |
|---|---|
| `.github/workflows/validate.yml` | New `coverage gate (fail under 85%)` step (Python 3.12 matrix) running `coverage report --fail-under=85`, so coverage can no longer regress silently (TEST-P3-001). |
| `automation/validation/fleet_inventory.py` | Added `_now_epoch()` and a `--now` (ISO-8601 UTC) override to `changes` and `prune`, making the window injectable (TEST-P3-002). |
| `tests/phase9/test_fleet_inventory.py` | Replaced the time-relative fixture with a fixed `NOW` reference and passed `--now` to `changes`/`prune`; fully deterministic (TEST-P3-002). |
| `docs/security/BRANCH_PROTECTION.md` | Dated 2026-10-03 audit re-affirmation of the owner-accepted branch-protection gap (CI-P2-001). |
| `ledgers/risk_register.md` | Appended R-017..R-025 recording the batch dispositions and open questions (append-only register). |

## Verification Performed

All commands ran on the **edge-builder VM** (`172.23.128.52`, Ubuntu 24.04.5, Python 3.12.3,
pytest 7.4.4, gitleaks 8.30.1) against a clean `origin/main` `f5811d1` checkout with the
committed diff applied via `git apply` (`patch applied` in the log). Raw output and exit codes are
in `remediation/PS-018/verify.log`.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `bash ci/validate.sh` | edge-builder VM | 0 (`validation: ALL PASS`) | `remediation/PS-018/verify.log` |
| `python3 -m pytest -q tests/phase2 tests/phase3` | edge-builder VM | 0 (129 passed) | `remediation/PS-018/verify.log` |
| `python3 -m pytest -q tests/phase9/test_fleet_inventory.py` | edge-builder VM | 0 (10 passed) | `remediation/PS-018/verify.log` |
| `coverage run --source=src ... && coverage report --fail-under=85` | edge-builder VM (coverage 7.16.2) | 0 (TOTAL 86%, gate pass) | `remediation/PS-018/verify.log` |
| `actionlint .github/workflows/validate.yml` | edge-builder VM | 0 | `remediation/PS-018/verify.log` |
| `gitleaks detect --no-git --redact --source . -v` | edge-builder VM (gitleaks 8.30.1) | 0 (`no leaks found`, ~7.21 MB) | `remediation/PS-018/verify.log` |

Base check: on `origin/main` `f5811d1` OBS-P3-001 is already fixed; TEST-P3-001/TEST-P3-002
reproduce. On the patched tree the coverage gate passes at 86% and the phase9 suite passes with
the deterministic fixture.

- Secret scan: **pass** — "no leaks found".
- Scope check: **pass** — the diff is the two verified fixes plus their tests, one security-doc
  re-affirmation, and the append-only risk register. No product code, API, schema, or dependency
  changed.

## Evidence bundle

- `remediation/PS-018/diff.patch` — SHA-256 `39aa21889f6d4a7b7c56a77a93896b117c75300e810df246e2f30d91a4d44073`
- `remediation/PS-018/manifest.json`
- `remediation/PS-018/verify.log` — SHA-256 `837c8d00c0e77caff7e207f221beea45e87bbecc08f59cc5c83147c187ae5e8b`

## Risk and rollback

- Risk: **low**. The only behaviour change is a CI coverage floor (86% measured, floor 85%) and an
  optional `--now` test hook; neither changes runtime behaviour. The doc/register edits are
  non-functional.
- Rollback: `git revert eed97d7`.

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Open questions

1. **SC-P2-004 (owner).** The image/release is a credential bundle. Approve encrypting credential
   side-files, scoping releases to a protected environment, rotating baked credentials after first
   boot, and scheduling an access-revocation drill.
2. **ARCH-P2-002 (owner, hardware/budget).** Accept the shared-host availability risk for the lab,
   or fund a dedicated host/VM before production and document a break-glass procedure.
3. **HYG-P3-002 (owner).** Choose a license and root project metadata (open-source vs
   proprietary/all-rights-reserved vs internal-only).
4. **EXEC-P2-001 (owner).** Complete the P10-G02/G04/G06 owner gates before any production claim.
5. **FINAL-P2-001 (build-agent).** Add a docs/derived-artifact drift check to `ci/validate.sh`
   once PS-011 (dirty-tree fail-closed + regen guards) merges.

## Definition of done (for this set)

From `patch_plan.md`: "per-item validation in the owning domain report". TEST-P3-001 and
TEST-P3-002 are fixed and verified; OBS-P3-001 is verified-fixed-at-base; CI-P2-001 is
re-affirmed; the remaining owner-decision findings are explicitly deferred with open questions.
`bash ci/validate.sh`, `pytest tests/phase2 tests/phase3`, `pytest tests/phase9/test_fleet_inventory.py`,
the coverage gate, actionlint and gitleaks all pass on the patched tree.
