# Branch Protection Recommendation (Companion Artifact)

Companion to `34_branch_protection_required_checks.md` — run `20260930-0701-falcon-8282d3f_edge-45dfed0`.
**Status: recommendation only. Nothing here has been applied; the audit does not modify GitHub settings.**

## Purpose

Provide an implementation-ready target configuration for both repositories so the owner can apply it
in one sitting after deciding R-012 (`falcon-edge-build/ledgers/risk_register.md`). It maps each
workflow to the check it would contribute, lists required checks, review/ownership rules,
environment and tag protections, and the break-glass process.

## Current state (evidence at this run)

| Aspect | falcon-build | falcon-edge-build |
|---|---|---|
| Default branch | `main` only | `main` only |
| Branch protection / rulesets | Not documented → `Unknown` | Documented as unavailable on the current plan (`docs/GITHUB_CI.md` §Plan limitations; API attempts 2026-09-30) |
| Required checks | None enforced | None enforced |
| Advisory checks | `validate / validate` (added 2026-09-30) | `validate / tests (3.12)`, `tests (3.13)`, `validate` (live) |
| Environment approvals | none | `environment: bake` (record only; reviewers blocked by plan) |
| CODEOWNERS / PR template | absent | absent |
| Tag protection | none | none (`publish-release` creates `sensor-*`/`lab-*` tags) |
| Merge bot | none (Dependabot PRs merged manually) | `dependabot-merge.yml` merges on green (daily) |

## Target: ruleset for `main` (both repos)

- Name: `main-protection`; target: default branch; **Enforcement: Active**.
- Rules: require a pull request before merging (1 approval; dismiss stale approvals; require review
  from Code Owners; require approval of the most recent push), require status checks (below) and
  branches up to date, require conversation resolution, block force pushes, restrict deletions,
  require linear history (squash/rebase).
- Bypass: **Repository admin role only** (owner) — this is the break-glass actor; see §Break-glass.
  Do not add the `dependabot-merge` bot or agent tokens as bypass actors.
- Note: a plan upgrade (GitHub Pro/Team) is required to create rulesets/classic protection on a
  private repository; do not make either repo public (edge releases are credential-bearing).

## Workflow-to-check mapping and required checks

| Repo | Workflow / job (check name) | What it executes | Required? |
|---|---|---|---|
| falcon | `validate / validate` | actionlint, shellcheck (errors), ruff E9/F/B, gitleaks, zizmor, `ci/validate.py` | yes — after CI-P2-001/002 fixes (see CI report) |
| edge | `validate / tests (3.12)` | 163-test suite + informational coverage summary | yes |
| edge | `validate / tests (3.13)` | 163-test suite (device runtime) | yes |
| edge | `validate / validate` | actionlint, shellcheck (warning), ruff, gitleaks, zizmor, upstream drift, `ci/validate.sh`, review-package build+verify | yes |
| edge | `bake-image / bake` | credential-bearing image build + 45/45 verify + SBOM | no (manual; gate via `bake` environment) |
| edge | `boot-smoke / boot` | QEMU healthy-boot smoke | no (manual; run before each release) |
| edge | `publish-release / publish` | GitHub Release creation | no (manual; gate via new `release` environment) |
| edge | `dependabot-merge / merge` | bot squash-merge of green Dependabot PRs | no (scheduled) |

Required-check setting to use in the ruleset: the job names above, with "Require branches to be up to
date before merging" enabled. Keep `cancel-in-progress` for `validate` (already configured) so
superseded runs do not stall the gate.

## Review and ownership rules

- Add `.github/CODEOWNERS` in both repos (replace `@<owner-handle>` with the real owner account):
  - `* @<owner-handle>`; `/.github/ @<owner-handle>`; `/ci/ @<owner-handle>`;
    `/bootstrap/ @<owner-handle>` (falcon); `/deploy/ @<owner-handle>` (edge);
    `/pins/ @<owner-handle>`; `/secrets/ @<owner-handle>` where present.
- Add `.github/pull_request_template.md` with: what changed, evidence link, validation performed,
  rollback note, security/secret impact, and gate/ledger impact.
- Require Code Owner review + 1 approval in the ruleset.
- Edge `AGENTS.md` rule 7 (implementer cannot approve a review/production gate) becomes enforceable
  once required reviews exist; keep the doctrine text.

## Environment protection

- Existing `bake` environment (edge): add Required reviewers = owner, enable "Prevent self-review",
  restrict deployment branches to `main`. This activates the approval already documented as the only
  missing step (`docs/GITHUB_CI.md`; R-012).
- New `release` environment for `publish-release.yml`: same settings; add `environment: release` to
  the workflow.
- Optionally add `release` gating to `boot-smoke.yml` only if the owner wants an approval before
  consuming a bake artifact.
- Capture approval records (run id, approver, time) into the evidence tree at each release.

## Tag protection

- Add a tag ruleset targeting `sensor-*` and `lab-*`: restrict creations to the owner, block
  updates and deletions. This keeps the durable delivery point (releases) immutable.

## Bypass / break-glass process (to be documented in both repos)

1. Who: repository owner only; never bots or agent tokens.
2. When: production-impacting incident where the normal PR + checks path is unusable.
3. How: owner uses the ruleset bypass to merge/push; the change is minimal and time-boxed (≤24 h).
4. Record: decision-log entry the same day; post-hoc review recorded within 48 h; GitHub audit-log
   entry captured into `evidence/raw/` and linked from the decision-log entry.
5. Guardrails: bypass list limited to the owner; quarterly review of bypass usage; any second use of
   break-glass in a quarter triggers a process review.

## Implementation checklist

1. Owner resolves R-012: upgrade to GitHub Pro/Team for the org (both repos).
2. Add `.github/CODEOWNERS` and `.github/pull_request_template.md` (normal PRs; these can land before
   the plan upgrade).
3. Create the `main-protection` ruleset in `falcon-edge-build` with the required checks above,
   required reviews, and owner-only bypass.
4. Repeat in `falcon-build` once `validate / validate` is exercised and green (CI-P2-001/002 fixed);
   until then, do not require a check that cannot pass on a committed audit folder.
5. Add reviewers to `bake`; create `release` and wire it into `publish-release.yml`.
6. Add the tag ruleset for `sensor-*` / `lab-*`.
7. Decide the fate of `dependabot-merge.yml`: preferred — require reviews and let it merge only
   approved PRs; alternative — retire it and enable GitHub auto-merge (requires the paid plan).
8. Capture `gh api` snapshots of the rulesets, environments and tag rules into `evidence/raw/`.
9. Update `REPOSITORY.md` (both) and `docs/GITHUB_CI.md` (edge) to state the new enforced process.

## Verification checklist (prove the settings work)

- [ ] A failing PR cannot be merged; the merge button reports the missing required check.
- [ ] A direct push to `main` is rejected for a non-bypass actor.
- [ ] A force-push to `main` is rejected.
- [ ] A PR whose checks were skipped via `[skip ci]` cannot merge (required checks missing).
- [ ] `bake-image` dispatch waits for reviewer approval; self-review is blocked.
- [ ] `publish-release` dispatch waits for the `release` environment approval.
- [ ] A non-owner tag push to `sensor-*` is rejected; published tags cannot be moved.
- [ ] A Dependabot PR without review cannot be merged by the bot.
- [ ] One owner break-glass exercise is executed, recorded in the decision log, and the audit-log
      entry is captured; the bypass list shows only the owner.

## Notes and limitations

- The audit did not call the GitHub API and did not apply anything. Edge plan limitations are
  reproduced from `docs/GITHUB_CI.md`; falcon's state is `Unknown` until an owner capture exists
  (see BP-P2-003).
- Rule/settings drift is only visible via API captures; add a weekly/release-time snapshot (CI report
  recommendation for drift class "docs vs records").
- Keep Actions cadence lean — concurrency/timeouts are already in place; the edge usage note in
  `ledgers/progress_ledger.md` X-047 records 80 minutes for `falcon-edge` in the month.
