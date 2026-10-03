# Remediation PR — PS-011 (Ownership and gate)

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Closes the executive/release-governance gaps for this run: adds review-routing
ownership and resolves the release-gate owner, and binds the gate to an explicit
machine-validation path. No product code; ~2 files plus the generated digest.

- Audit run: `20261003-0018-main-7bac320`
- Patch set: `PS-011` — Ownership and gate
- Repo / base: `repo-deep-dive` @ `b3d038250f5437490df21e1d25a1ea1297530559` (`main`)
- Branch: `remediation/ps-011-20261003-0018-main-7bac320`
- Commit: `fd9cf670164dba78f5a9fee8635da9c7d95f5725`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `EXEC-P2-001` | P2 | open -> partially-fixed | `.github/CODEOWNERS` added (review routing) and the release-gate owner resolved; this run's patch sets mapped to an owner. `verified-fixed` requires merge evidence. |
| `EXEC-P3-002` | P3 | open -> partially-fixed | The gate now names its owner and documents the exact machine-validation round-trip. The base-profile scaffold PASS capture stays blocked by the seed defect (`DATA-P1-002`, PS-002 #1); reproduced in `verify.log` §4. |

Statuses map per `profiles/remediation.md`: an open draft PR reconciles to
`partially-fixed`; `verified-fixed` requires a merge/release artifact.

## Changes

| File | What changed |
|---|---|
| `.github/CODEOWNERS` (new) | Default `*` plus per-path review routing for `/.github/`, `/ci/`, `/tools/`, `/schemas/`, `/profiles/`. |
| `runs/repo-deep-dive-20261003-0018-main-7bac320/RELEASE_GATE.md` | New `## Ownership` section (resolved owner + patch-set→owner mapping); new `## Machine validation (EXEC-P3-002)` section; sign-off owner resolved from `Unknown`. Verdict is unchanged (`GO WITH CONDITIONS`). |
| `PACK_DIGEST.txt` | Regenerated (`tools/pack_digest.sh`) for the new/changed files. |

## Overlap with PS-004 (#3)

PS-004 also adds `.github/CODEOWNERS`. The file here is **byte-identical** to the
PS-004 branch copy (`verify.log` §2), so either merge order is conflict-free — one
merge simply lands the same content and the other becomes a no-op for that file.
PS-004 additionally adds the maintainers/required-checks section to
`CONTRIBUTING.md`, which this PR deliberately does not duplicate. PS-011 keeps the
ownership change self-contained in case PS-004 is deferred.

## Verification Performed

Commands run in WSL Ubuntu-24.04 against the patched clone at commit
`fd9cf670164dba78f5a9fee8635da9c7d95f5725`, using gitleaks 8.30.1. Full raw
output: `remediation/PS-011/verify.log`.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `bash tools/self_test.sh` | repo gate | 0 (`RESULT: PASS`) | `verify.log` §5 |
| `bash tools/lint_pack.sh` | repo gate | 0 (`RESULT: PASS`) | `verify.log` §6 |
| `tools/pack_digest.sh` idempotent + lint check 8 | repo gate | 0 | `verify.log` §7 |
| `new_run.py --profile base` then `check_run.sh` (defect reproduction) | repo gate | `check_run.sh` exit 1, as expected | `verify.log` §4 |
| `diff` PS-011 vs PS-004 `CODEOWNERS` | git | 0 (identical) | `verify.log` §2 |
| gitleaks changed-file scan (default rules) | lab gitleaks 8.30.1 | 0 (no leaks) | `verify.log` §8 |

- Secret scan (gitleaks): **pass** — the changed files report no leaks.
- Scope check (files within patch set + generated digest): **pass** —
  `.github/CODEOWNERS`, `runs/.../RELEASE_GATE.md`, `PACK_DIGEST.txt`.
- `EXEC-P3-002` reproduction: `new_run.py --profile base` seeds a manifest missing
  the required `profile`/`scope`/`findings` keys, so `check_run.sh` prints
  `RESULT: FAIL (6 check(s))`. This confirms the PASS capture cannot be attached
  until PS-002 lands.

## Evidence bundle

- `remediation/PS-011/diff.patch` — SHA-256 `5b3fc268f2bad167e4e1eac5062eaf9ba7510b27024c1f39e61548bbbf72e3e5`
- `remediation/PS-011/verify.log` — SHA-256 `9d72fa6d2fb0509c1db46651e4960f4b1953104accf3dcb656288da10a080734`
- `remediation/PS-011/manifest.json`

## Risk and rollback

- Risk: **low**. Docs/governance only; no runtime code, no CI behavior change.
- `EXEC-P3-002` is intentionally **not** claimed fixed: the scaffold defect is
  owned by PS-002 (#1). Merging this PR does not, by itself, produce the
  machine-validated PASS capture.
- Rollback: `git revert fd9cf670164dba78f5a9fee8635da9c7d95f5725`.

## Review checklist

- [ ] Diff touches only the patch-set files (+ generated `PACK_DIGEST.txt`)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Definition of done (for this set)

`patch_plan.md` PS-011 verification: *owners resolve; gate cites validated run.*
Owners resolve (`verify.log` §1, §3). The gate now documents its validation path
and owner, but the validated run citation depends on PS-002 (#1) landing; §4
reproduces the blocking defect rather than asserting success.

## Dependencies / disjointness

PS-002 (#1) and PS-004 (#3) are open on `main`; PS-011 depends on both. This PR
touches only `.github/CODEOWNERS` (also in PS-004; identical content — see above),
this run's `RELEASE_GATE.md`, and the shared generated `PACK_DIGEST.txt`.
Regenerate the digest with `tools/pack_digest.sh` when rebasing any other PR.
