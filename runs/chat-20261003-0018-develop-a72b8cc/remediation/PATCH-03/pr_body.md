# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Stops the deploy workflows from destroying Docker named volumes on every release.
Both `deploy-production.yml` and `deploy-development.yml` ran
`docker system prune -af --volumes` immediately after `docker compose down`, which
deletes the now-unused named volumes — including Redis `redis-data` (AOF/queued
jobs/idempotency/presence state) and Caddy certificate data. This patch removes the
`--volumes` flag at all three call sites so only unused images, build cache and
networks are pruned; named data volumes are preserved.

- Audit run: `20261003-0018-develop-a72b8cc`
- Patch set: `PATCH-03` — Stop volume pruning (DATA-P1-002, CI-P1-004)
- Repo / base: `MaineCyberTech/chat` @ `a72b8cc43590848b052bd5e8954dbbc726b3d7fd` (develop)
- Branch: `remediation/patch-03-20261003-0018-develop-a72b8cc`
- Commit: `6733291c22a8c21a7c2b094e52886ade75229d8e`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `DATA-P1-002` | P1 | open -> partially-fixed | `--volumes` removed (prod :287 and :527, dev :219). Redis/Caddy named volumes now survive a deploy. |
| `CI-P1-004` | P1 | open -> partially-fixed | Deploy no longer prunes all Docker volumes; remaining prune commands are image/builder only. |

Both remain `partially-fixed` until a human merges and a real deploy confirms volume
persistence (see "Definition of done").

## Changes

| File | What changed |
|---|---|
| `.github/workflows/deploy-production.yml` | `docker system prune -af --volumes` -> `docker system prune -af` at lines 287 and 527; comment corrected to say volumes are preserved. |
| `.github/workflows/deploy-development.yml` | `docker system prune -af --volumes` -> `docker system prune -af` at line 219; comment corrected. |

5 line replacements, 0 net line change. No other files touched.

## Verification Performed

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `actionlint deploy-production.yml deploy-development.yml` | ci-runner (actionlint 1.7.12) | 1 | `remediation/PATCH-03/verify.log` — 20 pre-existing shellcheck/expression diagnostics, byte-identical to base a72b8cc; **0 new diagnostics** |
| `rg -n -- 'docker system prune[^\n]*--volumes\|prune[^\n]*--volumes\|--volumes' deploy-production.yml deploy-development.yml` | ci-runner | 1 (no matches) | `remediation/PATCH-03/verify.log` — pass |
| `rg -n -- 'docker [a-z]+ prune' deploy-production.yml deploy-development.yml` | ci-runner | 0 | every remaining prune is image/builder-only |
| `gitleaks protect --staged --redact --exit-code 1` | ci-runner (gitleaks 8.30.1) | 0 | no leaks found |
| `gitleaks detect --no-git --redact --exit-code 1 -s <patched files>` | ci-runner | 0 | 0 findings (base also 0) |
| `git diff --name-only` / `--numstat` | local | 0 | 2 in-scope files; `2/2` and `3/3` |

- Secret scan (gitleaks): **pass** — staged-diff gate exit 0, and a working-tree scan of the two changed files reports 0 findings (same as base).
- Scope check (files within patch set): **pass** — only the two deploy workflows.

Honest caveat: `actionlint` exits non-zero, but it is already red at base `a72b8cc`
with the same 20 unrelated shellcheck/expression diagnostics. The gate evidence is
the base-vs-patched equivalence (0 new issues), not a green exit. The patch plan's
runtime check ("deploy twice; `docker volume ls` retains `redis-data`") was **not run** —
it needs two live deployments and is out of scope for this runner.

## Evidence bundle

- `remediation/PATCH-03/diff.patch` — SHA-256 `08554A93F4B760E218AAC4A0D1A2013A483820D138DB5B98104E4ADD4700BD8E`
- `remediation/PATCH-03/manifest.json`
- `remediation/PATCH-03/verify.log`

## Risk and rollback

- Risk: low. Removing `--volumes` only makes cleanup less destructive; disk usage can
  grow modestly with old anonymous volumes, but image/builder pruning still runs.
- Rollback: `git revert 6733291c22a8c21a7c2b094e52886ade75229d8e`.

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Definition of done (for this set)

- No `--volumes` flag remains in either deploy workflow.
- After a real deploy, `docker volume ls` on the target host retains `redis-data`.
  (Runtime confirmation pending; static proof recorded above.)
