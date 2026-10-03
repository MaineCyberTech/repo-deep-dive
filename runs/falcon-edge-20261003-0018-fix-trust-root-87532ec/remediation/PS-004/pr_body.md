# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Patch set **PS-004** closes **SC-P2-001** (CI installs Python dependencies without version
pinning or hashes) and **SC-P2-003** (CI downloads lint/scan binaries via `curl` without
checksum verification).

At the audited commit (`87532ec`, branch `fix/trust-root`) the workflow ran
`python3 -m pip install --quiet pyyaml` / `coverage` / `"zizmor==1.30.1"` with no hashes.
The current base `origin/main` (`af6f83a`) already pins those dependencies inline with
`--require-hashes` and verifies every tool archive with `sha256sum -c` (added by the prior
audit's commit `73e3ca9`, "CI toolchain integrity + release provenance gate"). What was still
missing — and is the fix the finding explicitly recommends — is the **committed, reviewable
`requirements-dev.txt`**: the pins lived only in runner-local heredocs, so
`docs/security/DEPENDENCY_POLICY.md` §3 ("Any `requirements*.txt` must use `==` exact versions
with hashes") had no artifact to apply to, and there was no single file to review, update or
scan.

This patch set:

- adds `requirements-dev.txt` with exact versions and SHA-256 hashes for `pyyaml`, `coverage`
  and `zizmor` (digests carried over from the base workflow);
- changes both `validate.yml` jobs to install with
  `python3 -m pip install --require-hashes --only-binary=:all: -r requirements-dev.txt`,
  replacing the inline heredocs; and
- leaves `SC-P2-003`'s checksum guards in place (`sha256sum -c` for actionlint, shellcheck,
  ruff and gitleaks) and exercises them with a corrupted-download test.

- Audit run: `20261003-0018-fix-trust-root-87532ec`
- Patch set: `PS-004` — supply-chain hardening (pinning + hashes)
- Repo / base: `falcon-edge` @ `origin/main` (`af6f83a`)
- Findings: `SC-P2-001`, `SC-P2-003`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `SC-P2-001` | P2 | open -> fixed | Python dev tooling is exact-pinned with `==` + `--hash=sha256:` in a committed `requirements-dev.txt`, installed with `--require-hashes --only-binary=:all:`. pip fails closed on unpinned/`>=` entries. |
| `SC-P2-003` | P2 | open -> already satisfied at base, verified | All four tool downloads (`actionlint`, `shellcheck`, `ruff`, `gitleaks`) are verified with `sha256sum -c`; a corrupted download fails the check (test in `verify.log`). No workflow change needed. |

## Changes

| File | What changed |
|---|---|
| `requirements-dev.txt` (new) | Exact `==` pins with `--hash=sha256:` for `pyyaml==6.0.3`, `coverage==7.16.2`, `zizmor==1.30.1` (the multi-hash entries cover the 3.12/3.13 matrix). Header documents that these are CI-only, not runtime deps. |
| `.github/workflows/validate.yml` | Both jobs' install steps now run `pip install --require-hashes --only-binary=:all: -r requirements-dev.txt`; the runner-local `requirements-{ci,coverage,zizmor}.txt` heredocs are removed; the `zizmor` step is now just `zizmor --format=plain`. No trigger, cron, permission, matrix, or gitleaks/checksum-step changes. |

### Scope note (reviewer attention)

- The patch plan lists `.github/workflows/validate.yml` and `requirements-dev.txt`; this diff
  touches exactly those two files.
- PS-003 (`SC-P2-002`) also edits `validate.yml` (checkout `fetch-depth: 0` + the gitleaks
  step). This patch set deliberately does **not** touch those hunks, so the two branches
  should merge without conflict.
- `SC-P2-003` needed no code change because the base already verifies every download; that is
  stated rather than claimed as a new fix.

## Verification Performed

All commands run on the **edge-builder VM** (172.23.128.51) against the working tree; raw
output and exit codes in `remediation/PS-004/verify.log`.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `actionlint .github/workflows/validate.yml` | edge-builder VM (actionlint 1.7.12) | 0 (clean) | `remediation/PS-004/verify.log` |
| `actionlint .github/workflows/*.yml` | edge-builder VM | 0 (clean) | `remediation/PS-004/verify.log` |
| `python3 -m pytest -q tests/phase2` | edge-builder VM (pytest 8.3.5 / Python 3.13.5) | 0 (73 passed) | `remediation/PS-004/verify.log` |
| `python3 /tmp/ps004_pincheck.py` | edge-builder VM (stdlib) | 0 — **PASS** (3 requirements, all `==`, 5 sha256 hashes) | `remediation/PS-004/verify.log` |
| `bash /tmp/ps004_checksum_test.sh` | edge-builder VM | 0 — matching digest OK (0), corrupted digest FAILED (1) | `remediation/PS-004/verify.log` |
| `gitleaks detect --no-git --redact --source . -v` | edge-builder VM (gitleaks 8.30.1) | 0 (no leaks) | `remediation/PS-004/verify.log` |
| `pip install --dry-run --require-hashes -r requirements-dev.txt` | edge-builder VM | **not run** — `/usr/bin/python3: No module named pip`; replaced by the stdlib pin/hash check | `remediation/PS-004/verify.log` |

Patch-plan verification was "corrupted tool download fails; unpinned install rejected":
the corrupted-download test shows the checksum guard fails closed, and the pin/hash check
asserts the requirements file admits only exact-pinned, hashed entries.

Non-gating observation: `bash ci/validate.sh` reports `FAILURES PRESENT` on the lab-synced
tree, all `hash mismatch: evidence/raw/**`. Cause is the Windows->Linux tar sync (lab tree is
CRLF, recorded/git-blob hashes are LF; confirmed by `file` + sha256 for one file). None of the
failures reference this patch set's files; the workflow itself is green under actionlint.

- Secret gate (gitleaks 8.30.1): **pass** — no leaks in the working tree.
- Scope check: **2 files** — exactly the patch set.

## Evidence bundle

- `remediation/PS-004/diff.patch` — SHA-256 `26F33333E3456A720CA79EFF7D8256025544859EAEECB47A3E57D6596F410744`
- `remediation/PS-004/manifest.json`
- `remediation/PS-004/verify.log`

## Risk and rollback

- Risk: low. The pinned versions and digests are the same ones the base workflow already used;
  the only behavioural change is that all three dev tools are installed in both jobs (the
  3.13 test leg and the validate job now also install `coverage`/`zizmor`). No runtime code,
  triggers, permissions, or secrets change.
- Residual risk: future version bumps must update the pin and its hashes together (documented
  in the file header and `docs/security/DEPENDENCY_POLICY.md`); a mismatch now fails closed.
- Rollback: `git revert acc85e3` restores the prior inline-hash workflow and removes
  `requirements-dev.txt`. No runtime state.

## Review checklist

- [ ] Diff touches only the patch-set files (and is non-conflicting with PS-003's `validate.yml` hunks)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Pins/hashes match the previously CI-green base values
- [ ] Rollback is practical

## Open questions

- Should a CI policy check be added that mechanically rejects any future bare `pip install`
  (or any `requirements*.txt` without `==`/`--hash=`)? `--require-hashes` already fails closed
  on this file; a repo-wide regex guard would be a larger, separate change (new `ci/` script),
  outside this patch set's file list.
- Should `docs/security/DEPENDENCY_POLICY.md` §"CI enforcement (current)" now list
  `requirements-dev.txt` + `--require-hashes`? That is a docs change owned by PS-005, so it is
  not included here.

## Definition of done (for this set)

From `patch_plan.md`: "corrupted tool download fails; unpinned install rejected" — demonstrated
by the corrupted-download checksum test and the pin/hash check, with actionlint and
`tests/phase2` green.
