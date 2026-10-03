# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Patch set **PS-002** hardens the Dependabot auto-merge workflow (`.github/workflows/dependabot-merge.yml`).
Previously the scheduled sweep listed Dependabot PRs, ran `gh pr checks`, and then merged with no
link to the commit that was checked:

```bash
gh pr checks "$pr" >/dev/null 2>&1 && gh pr merge "$pr" --squash --delete-branch
```

A commit pushed between the check and the merge would be merged unchecked, so the workflow could
violate the very "only merge on green" guarantee it exists to provide.

The sweep now:

- verifies the author via the API is the trusted `dependabot[bot]` app;
- only considers **patch/minor** semver bumps (major updates are left to a human; grouped or
  otherwise unparseable titles are skipped — fail closed);
- requires green checks, **re-reads the head commit after the check**, and refuses if it moved;
- merges with `--match-head-commit <sha>`, binding the merge to the exact checked commit.

- Audit run: `20261003-0018-fix-trust-root-87532ec`
- Patch set: `PS-002` — bind Dependabot auto-merge to the checked commit
- Repo / base: `falcon-edge` @ `origin/main` (`af6f83a`)
- Finding: `CI-P2-002`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `CI-P2-002` | P2 | open -> fixed | Merge is bound to the checked head SHA (`--match-head-commit`), re-checked after the CI gate; auto-merge limited to trusted patch/minor updates. |

## Changes

| File | What changed |
|---|---|
| `.github/workflows/dependabot-merge.yml` | Verify `dependabot[bot]` author; parse the title and skip non-patch/minor or unparseable (grouped) updates; capture the head SHA, run `gh pr checks`, re-read the head and refuse if it changed; merge with `--match-head-commit <sha>`. No trigger, cron, or permission changes. |

## Verification Performed

All commands run on the **edge-builder VM** (172.23.128.51) against the working tree; raw output
and exit codes in `remediation/PS-002/verify.log`.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `actionlint .github/workflows/dependabot-merge.yml` | edge-builder VM (actionlint 1.7.12) | 0 | `remediation/PS-002/verify.log` |
| `python3 -m pytest -q tests/phase2` | edge-builder VM (pytest 8.3.5) | 0 (73 passed) | `remediation/PS-002/verify.log` |
| `python3 -m pytest -q tests/phase10/test_ci_doc_drift.py` | edge-builder VM | 0 (2 passed) | `remediation/PS-002/verify.log` |
| `gitleaks detect --no-git --redact --source . -v` | edge-builder VM (gitleaks 8.30.1) | 0 (no leaks found) | `remediation/PS-002/verify.log` |
| `python3 /tmp/test_ps002_workflow.py` (executes the shipped run-block against a mock `gh`) | edge-builder VM | 0 (5/5 scenarios) | `remediation/PS-002/verify.log` |

The patch-plan verification is "workflow test where PR head changes mid-check". There is no
GitHub-hosted test harness for this in the repo, so the run-block shell was executed directly
against a mock `gh`:

- **S1 head moved mid-check** → *no merge*, logs `head moved aaaa -> bbbb during checks`.
- **S2 patch bump, checks green, head stable** → merges with `--match-head-commit aaaa`.
- **S3 major bump** (`1.2.3 -> 2.0.0`) → *no merge* (`not a verifiable patch/minor`).
- **S4 grouped update** (unparseable title) → *no merge* (fail closed).
- **S5 untrusted author** → *no merge* (`not the trusted dependabot[bot]`).

- Secret scan (gitleaks 8.30.1): **pass** — "no leaks found".
- Scope check: **pass** — only `.github/workflows/dependabot-merge.yml` changed.

## Evidence bundle

- `remediation/PS-002/diff.patch` — SHA-256 `5bd547528d6283f918ba4519a359019143eb7d352070484d28e28a1c9675da0f`
- `remediation/PS-002/manifest.json`
- `remediation/PS-002/verify.log`

## Risk and rollback

- Risk: low. The change only narrows what the bot merges (patch/minor, trusted author) and adds a
  head-commit binding. Non-Dependabot PRs are unaffected; triggers, cron, and permissions are
  unchanged. Major/grouped Dependabot PRs now need a human, which is the intended behavior.
- Rollback: `git revert f19e5bc` restores the previous sweep. No runtime state.

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Definition of done (for this set)

From `patch_plan.md`: "workflow test where PR head changes mid-check" — demonstrated by the
mock-`gh` run-block test (S1) and actionlint passing.
