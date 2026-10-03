# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Patch set **PS-003** closes **SC-P2-002**: secret scanning only covered the working tree, never
git history. The `validate` workflow ran:

```bash
./gitleaks detect --no-git --source . --redact --config .gitleaks.toml
```

`--no-git` scans the checked-out files only, so a secret that was committed and later deleted
stays recoverable in clone history and is never flagged. The program's central rule is "no secrets
in commits"; history is exactly where a committed secret persists.

The workflow now:

- checks out the `validate` job with `fetch-depth: 0` (full history); and
- runs `gitleaks detect --source . --redact --config .gitleaks.toml --log-opts=--all`, scanning
  every commit reachable from every branch and tag, on push, PR, and the existing weekly schedule.

- Audit run: `20261003-0018-fix-trust-root-87532ec`
- Patch set: `PS-003` — scan git history for secrets
- Repo / base: `falcon-edge` @ `origin/main` (`af6f83a`)
- Finding: `SC-P2-002`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `SC-P2-002` | P2 | open -> fixed | Validate job now scans full git history (`fetch-depth: 0` + `gitleaks --log-opts=--all`); a committed-then-deleted secret is detected. |

## Changes

| File | What changed |
|---|---|
| `.github/workflows/validate.yml` | `validate` job checkout sets `fetch-depth: 0`; gitleaks step drops `--no-git` and adds `--log-opts=--all`; step name/comments updated. No trigger, cron, or permission changes. |
| `.gitleaks.toml` | Converted the single `[allowlist]` to `[[allowlists]]` (gitleaks 8.x syntax for multiple allowlists) and added one commit+rule-scoped entry for two **attested historical false positives** that the new history scan surfaces. |

### Scope note (reviewer attention)

The patch plan lists only `.github/workflows/validate.yml`. The `.gitleaks.toml` change is the
minimal config required to make the new history scan usable: enabling it without this was verified
to fail on two pre-existing `generic-api-key` matches that were already remediated in the tree but
remain in history. The added allowlist is scoped to the **exact commits**
(`a64c629`, `3798060`) **and** `targetRules = ["generic-api-key"]`, so any other finding in those
commits, or any finding in those files today, is still reported.

The two false positives (verified by inspection of those commits — no real secret value):

1. `tests/phase0/test_capture_hardening.py` @ `a64c629` — a synthetic redaction fixture literal
   (`"token=abcdef1234567890"`), removed from the tree in `74bdb09` by building the values at runtime.
2. `tests/phase3/test_agent_integration.py` @ `3798060` — an `Idempotency-Key` comment, reworded in
   `5b1a09e` (commit message: "gitleaks generic-api-key false positive").

`ci/secret_scan.py` (the repo's own walker) is unchanged and still tree-only; the independent
history coverage is now provided by gitleaks.

## Verification Performed

All commands run on the **edge-builder VM** (172.23.128.51) against the working tree; raw output and
exit codes in `remediation/PS-003/verify.log`.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `actionlint .github/workflows/validate.yml` | edge-builder VM (actionlint 1.7.12) | 0 (clean) | `remediation/PS-003/verify.log` |
| `gitleaks detect --no-git --redact --source . -v` | edge-builder VM (gitleaks 8.30.1) | 0 (no leaks) | `remediation/PS-003/verify.log` |
| `gitleaks detect --source . --redact --config .gitleaks.toml --log-opts=--all` | edge-builder VM (gitleaks 8.30.1) | 0 (312 commits, no leaks) | `remediation/PS-003/verify.log` |
| `/tmp/ps003_gitleaks_history_test.sh` (injected-then-deleted secret) | edge-builder VM | 0 — **PASS** | `remediation/PS-003/verify.log` |
| `python3 -m pytest -q tests/phase2` | edge-builder VM (pytest 8.3.5 / Python 3.13.5) | 0 (73 passed) | `remediation/PS-003/verify.log` |

The patch-plan verification is "`gitleaks detect --source .` (git mode) finds an injected dummy
secret". There is no GitHub-hosted harness for this; the shipped command semantics were exercised
directly against a scratch git repo:

- commit a fake `ghp_...` token, then commit its deletion;
- **old command** (`--no-git`): `no leaks found`, `TREE_EXIT=0` — the deleted secret is missed;
- **new command** (`--log-opts=--all`): `leaks found: 1`, `GIT_EXIT=1` — detected from history;
- `RESULT=PASS`.

The new history scan of the real repository is also green after the scoped allowlist
(312 commits scanned, no leaks). Without the allowlist, the same scan reported exactly 2
`generic-api-key` hits, both the attested false positives above.

- Secret gate (gitleaks 8.30.1): **pass** — no leaks in tree or history.
- Scope check: **2 files** — the patch-set workflow plus the required `.gitleaks.toml` entry (see
  scope note).

## Evidence bundle

- `remediation/PS-003/diff.patch` — SHA-256 `f823977eeba9980431333f097083082855171569d62f7e2a52b727aeee4afe2c`
- `remediation/PS-003/manifest.json`
- `remediation/PS-003/verify.log`

## Risk and rollback

- Risk: low. The workflow scans more (full history) and the scanner is pinned by URL + SHA-256 and
  installed with `--require-hashes`. Larger clone (`fetch-depth: 0`) adds modest CI time; the repo
  is ~8 MB / 312 commits.
- Residual risk: the history scan is fail-closed, so a genuine historical secret will now fail the
  build. That is intended; confirmed false positives are scoped out by commit+rule. The
  `git filter-repo` rotation runbook the finding asks for is **not** included here (out of scope)
  and is listed below.
- Rollback: `git revert 252d411` restores the tree-only scan and the prior allowlist. No runtime state.

## Review checklist

- [ ] Diff touches only the patch-set files (+ the documented `.gitleaks.toml` config the fix requires)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean (tree + history)
- [ ] The commit+rule-scoped allowlist is acceptable (vs. rewriting history)
- [ ] Rollback is practical

## Open questions

- Should the two historical false-positive commits be rewritten out of history with `git filter-repo`
  (and force-push) instead of allowlisted by commit? That is destructive and needs owner sign-off;
  not done here.
- Should `ci/secret_scan.py` also gain a history mode, or is the gitleaks history scan sufficient as
  the single independent history control? (This patch set is workflow-scoped.)
- Add the `git filter-repo` rotation runbook recommended by SC-P2-002 (not included; docs change).

## Definition of done (for this set)

From `patch_plan.md`: "`gitleaks detect --source .` (git mode) finds an injected dummy secret" —
demonstrated by the injected-then-deleted secret test (tree mode misses, git mode catches), with
actionlint and `tests/phase2` green.
