# Remediation PR — PS-003 (CI workflow hardening)

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Hardens the org-wide deterministic workflow's supply chain, secret handling, and
failure visibility. All GitHub Actions are pinned to commit SHAs; the remote
tools (actionlint, gitleaks, hadolint, trivy) are installed from versioned
release artifacts and verified by SHA-256 without piped `sudo`; the PAT is moved
out of the clone URL; a `.gitleaks.toml` allowlist is added and P1 secret
findings now fail the job; and failure-masking `|| true` is removed.

- Audit run: `20261003-0018-main-7bac320`
- Patch set: `PS-003` — CI workflow hardening
- Repo / base: `repo-deep-dive` @ `b3d038250f5437490df21e1d25a1ea1297530559` (`main`)
- Branch: `remediation/ps-003-20261003-0018-main-7bac320`
- Commit: `e03c1168a4fb99e1f6ab49fa0d9f224d82150e31`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `SEC-P1-001` | P1 | open -> fixed | Tools pinned by version+sha256, unpacked to `$RUNNER_TEMP/tools` without `sudo`, install fails closed. |
| `SEC-P1-002` | P1 | open -> fixed | PAT passed via `git -c http.extraheader`, never in the URL; `::add-mask::` added. |
| `SEC-P2-003` | P2 | open -> fixed | Added `.gitleaks.toml` (default rules + narrow allowlist) and a step that fails the job on P1 SEC findings. |
| `CI-P2-003` | P2 | open -> fixed | Pinned tool versions; removed silent `\|\| true` failures. |
| `CI-P2-004` | P2 | open -> fixed | Added `concurrency`, `timeout-minutes: 90`, and a protected `environment`. |
| `SUPPLY-P1-001` | P1 | open -> fixed | `actions/checkout`/`actions/upload-artifact` pinned to 40-hex SHAs; tools pinned by version+sha256. |
| `SUPPLY-P2-002` | P2 | open -> fixed | Added `.github/dependabot.yml` for `github-actions`. |
| `OBS-P2-002` | P2 | open -> partially-fixed | Removed failure-masking `\|\| true`; clone/scan errors and P1 secret findings now fail the job. Baseline diff (new P0/P1 vs previous run) deferred — see open questions. |

Statuses map per `profiles/remediation.md`: an open draft PR reconciles to
`partially-fixed`; `verified-fixed` requires a merge/release artifact.

## Changes

| File | What changed |
|---|---|
| `.github/workflows/deep-dive-deterministic.yml` | Pin actions to SHAs; pin+checksum tool installs; add-mask + `http.extraheader` clone; `concurrency`/`timeout-minutes`/`environment`; add P1-SEC gate; remove `\|\| true`; fail closed on clone/scan errors. |
| `.gitleaks.toml` (new) | `[extend] useDefault = true` + allowlist for the config itself, `examples/*.example.json`, and redacted `runs/**/remediation/**gitleaks*` logs. |
| `.github/dependabot.yml` (new) | Weekly `github-actions` update PRs. |
| `PACK_DIGEST.txt` | Regenerated (`tools/pack_digest.sh`) for the two new files + workflow hash. |

## Verification Performed

All commands run in WSL Ubuntu-24.04 against the patched clone at commit
`e03c1168a4fb99e1f6ab49fa0d9f224d82150e31`, using the repo's real gates and the
lab's gitleaks 8.30.1 / actionlint 1.7.12. Full raw output:
`remediation/PS-003/verify.log`.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `actionlint -no-color .github/workflows/deep-dive-deterministic.yml` | lab actionlint 1.7.12 | 0 | `verify.log` §1 |
| `bash tools/lint_pack.sh` | repo gate | 0 (`RESULT: PASS`) | `verify.log` §5 |
| `bash tools/self_test.sh` | repo gate | 0 (`RESULT: PASS`) | `verify.log` §6 |
| gitleaks: real-format `ghp_`<36> PAT fixture (non-allowlisted path) | lab gitleaks 8.30.1 | 1 (leak found: `github-pat`) | `verify.log` §7a |
| gitleaks: same secret under allowlisted `examples/*.example.json` | lab gitleaks 8.30.1 | 0 (suppressed) | `verify.log` §7b |
| changed-files secret scan with new config | lab gitleaks 8.30.1 | 0 (no leaks) | `verify.log` §8 |
| P1-SEC gate: P1 finding -> exit 1, clean -> exit 0 | python3 | 0 (assertion) | `verify.log` §9 |
| all `uses:` refs 40-hex; 4 versioned downloads + 4 sha256 checks | harness assertions | 0 | `verify.log` §2–§3 |

- Secret scan (gitleaks): **pass** — changed-file scan reports no leaks; a real-format
  `ghp_` PAT fixture is detected by the built-in `github-pat` rule and the
  `examples/*.example.json` allowlist suppresses only that path.
- Scope check (files within patch set): **pass** — only the three PS-003 files plus
  the generated `PACK_DIGEST.txt`.
- Note: gitleaks' built-in global stopword allowlist contains the literal
  `abcdefghijklmnopqrstuvwxyz`, so low-entropy sample tokens are not detected; the
  fixture uses a high-entropy random PAT, verified empirically.

## Evidence bundle

- `remediation/PS-003/diff.patch` — SHA-256 `F22C38B4E8C1CC0F8ABC6AEA74D1755789B7F0F08DA6A18EF28AFE960470F609`
- `remediation/PS-003/manifest.json`
- `remediation/PS-003/verify.log`

## Risk and rollback

- Risk: **low–medium**. Pinned versions (actionlint 1.7.12, gitleaks 8.30.1,
  hadolint 2.15.1, trivy 0.75.0) can drift from upstream; Dependabot will open
  update PRs. The job now fails when a scanner/clone fails or a P1 secret is
  found, so a previously-green scheduled run may correctly turn red.
- `environment: deep-dive-scan` documents intent to gate the PAT-bearing job; if
  the org later adds required reviewers to that environment, scheduled runs would
  pause until approved (operator decision).
- `PACK_DIGEST.txt` is a generated aggregate and also changes in PS-002 (#1, open);
  regenerate with `tools/pack_digest.sh` when rebasing either PR.
- Rollback: `git revert e03c1168a4fb99e1f6ab49fa0d9f224d82150e31`.

## Review checklist

- [ ] Diff touches only the patch-set files (+ generated `PACK_DIGEST.txt`)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Open questions

- `OBS-P2-002`: a true "new P0/P1 vs previous run" regression diff needs a
  persisted baseline (committed run, artifact download, or a state branch). This
  PR fails closed on scanner/clone errors and on P1 secrets, but the diff-based
  regression alert is deferred pending a product decision on where the baseline
  lives.

## Definition of done (for this set)

`patch_plan.md` PS-003 verification: *every `uses:` pinned to a commit SHA; tool
downloads versioned+sha256; clone failure logs contain no token; fixture secret
fails the job.* All four are demonstrated in `verify.log` (§2–3, §7, §4/§8/§9).
