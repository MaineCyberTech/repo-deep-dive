# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Closes the remaining test-quality gap called out by `TEST-P2-002` (catch-all set
`PS-U13`): coverage floors were low and the change-focused diff-coverage check
could not fail. This patch:

1. raises the global coverage floors in `packages/config/vitest.config.base.ts`
   to the highest integer below the coverage measured at the audited commit, and
2. makes the `Check diff coverage thresholds` step in `.github/workflows/validate.yml`
   **blocking** by removing `continue-on-error: true`.

- Audit run: `20261003-0018-develop-a72b8cc`
- Patch set: `PS-U13` — Unassigned TEST findings (catch-all)
- Repo / base: `MaineCyberTech/chat` @ `a72b8cc43590848b052bd5e8954dbbc726b3d7fd` (develop)
- Branch: `remediation/ps-u13-20261003-0018-develop-a72b8cc`
- Commit: `fe04ab3a01cd04ff3dcc8c9a4cce6153c0340f9b`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `TEST-P2-002` | P2 | open -> partially-fixed | Global floors raised and the diff-coverage threshold step is now blocking. Measured coverage at the commit is above every new floor (see below). |

Status advances to `verified-fixed` on merge (a draft PR can only be `partially-fixed`).

## Changes

| File | What changed |
|---|---|
| `packages/config/vitest.config.base.ts` | Coverage thresholds raised: lines `35 -> 36`, functions `30 -> 40`, branches `25 -> 60`, statements `35 -> 36`. Values are the highest integer below measured coverage at this commit, so the gate is meaningful without being unreachable. |
| `.github/workflows/validate.yml` | `continue-on-error: true` removed from the `Check diff coverage thresholds` step (renamed `(blocking)`). The existing 20/20/15/20 diff thresholds now fail the job when unmet. |

Scope: one config file and one workflow step. No application code, dependencies,
job topology, or other config changes.

### Coverage floors vs measured coverage at `a72b8cc` / `fe04ab3`

| Metric | Old floor | New floor | Measured | Headroom |
|---|---|---|---|---|
| lines | 35 | 36 | 36.85 | +0.85 |
| functions | 30 | 40 | 45.98 | +5.98 |
| branches | 25 | 60 | 66.62 | +6.62 |
| statements | 35 | 36 | 36.85 | +0.85 |

## Verification Performed

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `corepack pnpm install --frozen-lockfile` | lab `ci-runner` (172.23.128.51) | 0 | install ok — `remediation/PS-U13/verify.log` §1 |
| `corepack pnpm --filter @chat/api test` (required) | lab `ci-runner` | 0 | 62 files / 485 tests passed — §1 |
| `corepack pnpm vitest run --config vitest.config.ts --coverage` | lab `ci-runner` | 0 | `All files 36.85 / 66.62 / 45.98 / 36.85` vs floors `36/60/40/36` — §2 |
| `actionlint .github/workflows/validate.yml` | lab `ci-runner` | 1 (12 diagnostics) | base is also 12 -> no new diagnostics — §3 |
| `yq -e . .github/workflows/validate.yml` | lab `ci-runner` | 0 | YAML parses — §4 |
| **negative**: diff-coverage threshold logic vs 10/10/5/10 summary | lab `ci-runner` | 1 | fails closed — §6 |
| **positive**: same logic vs 80% summary | lab `ci-runner` | 0 | passes — §7 |
| **negative**: raised global floor vs 35/39/59/35 report | lab `ci-runner` | 1 | new floors enforce — §8 |
| `git diff origin/develop..HEAD \| gitleaks stdin --redact` | lab `ci-runner` (gitleaks 8.30.1) | 0 | `no leaks found` — §9 |
| full worktree `gitleaks detect --no-git` | lab `ci-runner` | 1 | 5 **pre-existing** findings, none in the diff — §9 |

- Secret scan (gitleaks): **pass on the diff**. The 5 worktree findings are
  pre-existing (`validate.yml` jwt fixture, `keyboard-shortcuts.tsx` generic-api-key,
  `infra/docker/.env.dev.example` jwt x3), identical to the base set documented under
  PATCH-07 / PS-U03 / PS-U12.
- Scope check: **pass** — two files only (`packages/config/vitest.config.base.ts`,
  `.github/workflows/validate.yml`), both cited by the finding.
- Lab evidence was captured at `fe04ab3` (re-synced after commit).

## Evidence bundle

- `remediation/PS-U13/diff.patch` — SHA-256 `c883f2af222eb38f18ccabee76f288ca3217de53a2a1d3b59119cd53d9f8d8f8`
- `remediation/PS-U13/manifest.json`
- `remediation/PS-U13/verify.log`

## Risk and rollback

- Risk: **low**. One config constant set and one `continue-on-error` flag. The only
  behavior change is that coverage below the (already-passing) floors now fails the
  CI `test` job, and an unmet diff threshold fails the `diff-coverage` job. Both were
  already computed; they now gate.
- Rollback: `git revert fe04ab3a01cd04ff3dcc8c9a4cce6153c0340f9b` (two files).

## Review checklist

- [ ] Diff touches only the patch-set files
- [ ] New floors are acceptable as the baseline (set just below measured coverage)
- [ ] Blocking diff-coverage step is acceptable (no `continue-on-error`)
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean on the diff
- [ ] Rollback is practical

## Open questions

1. **Pre-existing diff-coverage command defect (out of scope).** The `Run diff
   coverage` step runs `pnpm test -- --changed --coverage ...`, but the root `test`
   script is `turbo test`, so `--changed` is forwarded to turbo and rejected
   (`ERROR unexpected argument '--changed' found`). This fails at base `a72b8cc`
   and is not caused by this patch set; it means that job currently fails before
   reaching the now-blocking threshold step. Making diff coverage *actually run*
   (e.g. calling vitest directly, and reconciling the changed-only run with the
   global floors) is a separate change and was deliberately left out to keep this
   patch minimal. See `verify.log` §10.
2. The lines/statements floors (36) have only +0.85 headroom over measured coverage.
   If the team prefers more margin despite lower enforcement, these can be relaxed;
   functions/branches have ~6 points of margin.
