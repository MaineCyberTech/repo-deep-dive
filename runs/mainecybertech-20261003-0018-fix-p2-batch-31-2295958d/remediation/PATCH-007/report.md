# PATCH-007 (CI-P2-001) — no change required: already fixed at the PR base

## Outcome

No commit, branch, or PR was created for this patch set.

`CI-P2-001` ("Branch protection permits admin bypass and ignores CODEOWNERS") is
**already fixed on the remediation base branch `fix/p2-batch-31`** (`11746adc`).
The fix came from prior remediation commit `8b02f91a` ("fix(ci): make
branch-protection required checks match real check-runs"), merged via
**PR #30**, which is an ancestor of the base.

## Reproduction at the base

| Claim in CI-P2-001 (evidence @ audited `2295958d`) | State at base `11746adc` | Result |
|---|---|---|
| `main.json` `"enforce_admins": false` → admins bypass checks | `"enforce_admins": true` | **fixed** |
| `main.json` `"require_code_owner_reviews": false` → `CODEOWNERS` advisory | `"require_code_owner_reviews": true` | **fixed** |
| required contexts omit `CodeQL`, `Validate`, `SBOM` | contexts are the real emitted check-runs; `CodeQL`/`Validate`/`SBOM` intentionally not required | **not applied — see below** |

The diff of `.github/branch-protection/main.json` from the audited commit to the
base is exactly `8b02f91a` (see `verify.log` §3–§5). `develop.json` carries the
same `true`/`true` settings.

## Why CodeQL / Validate / SBOM were not added as required contexts

The audit's recommended fix hedged these with "(once stable)". Inspecting the
base shows adding them now would be unsafe or impossible:

- **`Validate`** — `.github/workflows/validate.yml` is `on: workflow_call` only.
  Its callers are `deploy-do.yml` (push `main`/`develop` or dispatch) and
  `terraform-do.yml` (dispatch), so it **never emits a check-run on a PR**.
  Making it required would leave the check perpetually "Expected — Waiting for
  status to be reported" — the exact `CI-P1-002` failure mode the repo fixed in
  `8b02f91a`.
- **`CodeQL`** — `AGENTS.md:63` records that CodeQL "remains red on the
  **pre-existing** high-severity CSRF alert (see issue #31) … and **not a
  required check**." Requiring a currently-red check would block every merge to
  `main`.
- **`SBOM`** — `docs/CI.md:27` classifies it as "Artifact-only (not a gate)"; it
  is a design choice, not an unenforced gate.

This residual is an **open question** for the repo admin (stability/desirability
of requiring SAST/SBOM), not a code defect this patch should guess at.

## Verification (real output in `verify.log`)

| Command | Runner | Exit | Result |
|---|---|---|---|
| `git merge-base --is-ancestor 8b02f91a origin/fix/p2-batch-31` | local git | 0 | prior fix is merged into the base |
| `node scripts/check-required-checks.mjs` | ci-runner (LXC 200) node v20.20.2 | 0 | `PASS: all required checks match a workflow job` (2 files, 41 check-run names) |
| `actionlint <changed workflows>` | — | — | not run: no workflow changed (no diff) |
| `gitleaks detect --no-git --redact` | — | — | not run: no diff produced / nothing pushed |

## Why the audit still reported it

The audit ran against a **stale local clone**: `C:\temp\mainecybertech` was at
`2295958d`, a divergent line that does not contain the `fix/audit-20261002-p0`
merge (`571f8205`) or `8b02f91a`. At `2295958d` the audit's evidence is correct
(`enforce_admins:false`, `require_code_owner_reviews:false`). The remediation
target (`origin/fix/p2-batch-31`, `11746adc`) already carries the fix.

## Guardrails

- No fabricated diff, no duplicate/no-op PR, no secrets committed.
- Original audit findings were not modified; status reconciled via
  `tools/remediation_status.py` (`PATCH-007 → merged → verified-fixed`, evidence
  `8b02f91a`).

## Open questions

- Should `CodeQL` (once the pre-existing CSRF alert is cleared) and/or `SBOM`
  become required checks on `main`/`develop`? This is a repo-admin
  stability/coverage decision; `Validate` can never be a PR required check.
