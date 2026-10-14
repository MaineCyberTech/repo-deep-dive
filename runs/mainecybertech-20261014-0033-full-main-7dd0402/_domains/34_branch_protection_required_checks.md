# Branch Protection and Required Checks Audit (re-audit)

- Run: `mainecybertech-20261014-0033-full-main-7dd0402`
- Target: `mainecybertech` @ `7dd0402` (branch `main`)
- Area code: BP · Previous full run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Scope: `.github/branch-protection/{main,develop}.json`, required-check guard + fixtures, CODEOWNERS + guard, Dependabot, PR template, hotfix/emergency runbooks, environment approvals, manual dispatch. Live GitHub settings are not inspectable read-only.

## Executive Summary

All 15 previous BP rows were re-verified: **13 verified-fixed, 2 partially-fixed, 0 open, 0 regressed**. The committed protection-as-code is coherent with the workflow estate — every required context resolves to a real check-run and no required workflow path-filters its `pull_request` trigger (guard reproduced: PASS). `enforce_admins:true`, code-owner reviews, conversation resolution, no force-push/deletion are set on both branches; prod mutations all attach `prod-approval`; the drift/bypass audit, break-glass runbook, and issue template exist and are fixture-tested.

Residuals are repo-admin/operator settings that cannot be verified or set from the repository: live settings application (the drift job needs `BRANCH_PROTECTION_READ_TOKEN` and fails closed until provisioned), GitHub's "Require code scanning results" setting (BP-P2-007), and Dependabot security-update separation (BP-P3-002). Note the related CI finding CI-P1-004: the current tree fails the docs-links guard, so the required `Test / test (20.x)` check cannot pass until fixed — that is a CI-domain defect, not a branch-protection defect.

## Verification Performed

| Evidence | Type | Why relevant | Result |
|---|---|---|---|
| `node scripts/check-required-checks.mjs` (executed) | Guard | Every required context resolves; no path-filtered required workflow | **PASS** (8 main / 6 develop) |
| `bash scripts/ci/check-required-checks.sh` (executed) | Fixture suite | Guard models names/matrices correctly | **PASS** 4/4 |
| `bash scripts/ci/check-codeowners.sh` (executed) | Fixture suite | CODEOWNERS syntax/team-handle guard | **PASS** |
| `bash scripts/ci/check-branch-protection-audit.sh` (executed) | Fixture suite | Drift + bypass detector self-test | **PASS** 5/5 |
| `.github/branch-protection/*.json` | Config | enforce_admins, owner reviews, contexts | verified |
| `branch-protection-audit.yml` | Workflow | Drift + bypass audit, alerting, records | verified |
| `docs/RUNBOOK_EMERGENCY_MERGE.md`, `RUNBOOK_HOTFIX.md`, `ISSUE_TEMPLATE/break_glass.yml` | Docs | Break-glass + hotfix process | verified |
| `docs/DEPENDENCY_POLICY.md`, `dependabot-triage-reminder.yml`, `PULL_REQUEST_TEMPLATE.md` | Docs/CI | Dependabot governance | partial (repo setting out of band) |

## Findings

| ID | Sev | Title | Status | Evidence (at 7dd0402) |
|---|---|---|---|---|
| BP-P1-001 | P1 | Required context `Dependency Review` no job emits | verified-fixed | main.json requires `Dependency Review / review`; dependency-review.yml job `review`; guard PASS |
| BP-P1-002 | P1 | `enforce_admins:false` bypass | verified-fixed | `enforce_admins:true` in both payloads |
| BP-P1-003 | P1 | Prod deploy uses unguarded `prod` env | verified-fixed | deploy-do.yml:648; supabase-migrations.yml:38; terraform-do.yml:204; read-only jobs keep `prod` by design |
| BP-P2-001 | P2 | CODEOWNERS advisory only | verified-fixed | `require_code_owner_reviews:true`; check-codeowners guard wired (unit-tests:146-154) |
| BP-P2-002 | P2 | No break-glass process/audit | verified-fixed | bypass audit + `[break-glass]` issues (branch-protection-audit.yml:94-186); runbook + template |
| BP-P2-003 | P2 | No drift detection vs live settings | verified-fixed | drift job (:43-92) fails+alerts+artifacts; needs operator token (fails closed) |
| BP-P2-004 | P2 | Path-filtered required checks | verified-fixed | no paths filter on required workflows; guard enforces |
| BP-P2-005 | P2 | Required-check guard not run on PRs | verified-fixed | unit-tests composite in PR gate (test.yml:41) and deploy gate (validate.yml:88) |
| BP-P2-006 | P2 | Prod dispatch from arbitrary ref | verified-fixed | main-only guard deploy-do.yml:61-69 (+ db-restore-test, load-test, smoke-check) |
| BP-P2-007 | P2 | Security scans not required checks | partially-fixed | `security-scan`, `secrets-scan`, CodeQL required on both branches; residual: "Require code scanning results" repo setting + Chromatic/a11y promotions are repo-admin |
| BP-P3-001 | P3 | Hotfix docs stub | verified-fixed | RUNBOOK_HOTFIX.md complete |
| BP-P3-002 | P3 | Dependabot triage/SLA + PR template | partially-fixed | SLA + weekly reminder + template link exist; security-update separation is a GitHub setting |
| BP-P3-003 | P3 | Docs disagree on prod env reviewers | verified-fixed | matrix:9-16, RELEASING.md:118-141, SECRETS_ROTATION.md:28-37 agree on `prod-approval` |
| BP-P3-004 | P3 | Guard mis-models names+matrices | verified-fixed | check-required-checks.mjs:73-90 + 4/4 fixtures |
| BP-P3-005 | P3 | No CODEOWNERS validation | verified-fixed | check-codeowners.mjs + fixtures; optional token fallback documented |

## Recommendations

- **This week**: operator — apply the committed payloads to live settings if not already (drift job will confirm), provision `BRANCH_PROTECTION_READ_TOKEN`, configure `prod-approval` reviewers (shared with CI-P1-001/003).
- **This month**: decide and set "Require code scanning results" on the code-scanning ruleset (closes the last BP-P2-007 residual); promote Chromatic/a11y once green.
- **This quarter**: enable Dependabot security updates + grouped security PRs in repo settings and record the setting in the matrix (BP-P3-002).

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Do live branch-protection settings match the committed JSON? | The payload is only effective when applied | `branch-protection-audit.mjs --mode drift` with an admin token |
| Is admin bypass still possible via the GitHub UI? | enforce_admins is committed but must be live | live protection payload |
| Are required checks actually blocking on main today? | CI-P1-004 makes the required test check fail | latest PR check runs / merge records |
