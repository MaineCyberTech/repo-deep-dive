<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Makes the pipeline's quality/security signals blocking instead of advisory, and closes the E2E
release-confidence gap. Security scans now fail closed on HIGH/CRITICAL findings, backed by an
explicit, time-boxed exception list so the known dependency backlog cannot silently mask new
issues. The E2E job is now blocking and self-provisioning: it boots local Supabase, applies
migrations **and seeds** via `supabase db reset`, generates `test-signin.json` from a seeded test
user, and runs the suite without depending on a committed credential file.

- Audit run: `20261003-0018-develop-a72b8cc`
- Patch set: `PATCH-07` — Make quality/security gates blocking
- Repo / base: `MaineCyberTech/chat` @ `a72b8cc43590848b052bd5e8954dbbc726b3d7fd`
- Branch: `remediation/patch-07-20261003-0018-develop-a72b8cc`
- Commit: `9afa84904cfc7c23abbbf3d204c584fdc4df5aa2`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `CI-P1-003` | P1 | open -> partially-fixed | `pnpm audit` and Trivy (fs + both image scans) now fail closed on HIGH/CRITICAL; time-boxed exception files added. |
| `TEST-P1-001` | P1 | open -> partially-fixed | E2E job is blocking and self-provisions credentials + seeds; no longer depends on the committed `test-signin.json`. Setup path verified in the lab; full test run blocked by a lab environment limitation (see Verification). |
| `FINAL-P2-003` | P2 | open -> partially-fixed | The advisory-gate release-confidence gap is closed by the above. |

Statuses map to `partially-fixed` because the PR is a draft; they become `verified-fixed` only
after a green CI run at the merge commit.

## Changes

| File | What changed |
|---|---|
| `.github/workflows/validate.yml` | `pnpm audit` no longer has `|| true`; wrapped in a blocking gate that fails on any HIGH/CRITICAL advisory outside `.pnpm-audit-exceptions.json` and once the list expires. Trivy fs scan sets `exit-code: "1"` (was `continue-on-error: true`). E2E job: removed `continue-on-error` from Supabase install/start and `Run E2E tests`; the broken/duplicate seed step (referencing a non-existent `supabase/seeds/seed.sql`) is replaced by `supabase db reset`, which applies migrations **and** `[db.seed].sql_paths` from `supabase/config.toml`; generates `test-signin.json` from the local seed user `marcus@seed.test`; installs Chromium with `--with-deps`. |
| `.github/workflows/build-push.yml` | Both Trivy image scans set `exit-code: "1"` (were `continue-on-error: true`), consulting `.trivyignore`. |
| `.trivyignore` | New. Time-boxed (exp 2026-11-03) list of the 30 pre-existing HIGH/CRITICAL CVE/GHSA IDs observed at base; remove entries as they are fixed. |
| `.pnpm-audit-exceptions.json` | New. Time-boxed (expires 2026-11-03) list of the 30 pre-existing HIGH/CRITICAL GHSAs; the audit gate fails on anything not listed and on the whole list after expiry. |

Scope: the two workflow files in the patch set, plus the two exception files the fix explicitly
requires (patch plan: "pnpm audit fails on high with an exceptions file"). No application code,
dependency bumps, or unrelated workflow edits.

## Verification Performed

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `actionlint` (validate + build-push vs base a72b8cc) | ci-runner | 0 | no new diagnostics (12+1 both) — `verify.log` §1 |
| `yq -e '.jobs \| keys'` both workflows | ci-runner | 0 | both parse — `verify.log` §2 |
| `pnpm install --frozen-lockfile` | ci-runner | 0 | `verify.log` §4 |
| `pnpm audit` gate with exceptions | ci-runner | 0 | 0 un-allowlisted HIGH/CRITICAL — `verify.log` §5 |
| **negative**: injected new HIGH advisory | ci-runner | 1 | gate failed closed — `verify.log` §6 |
| `trivy fs … --exit-code 1 --ignorefile .trivyignore` | ci-runner | 0 | `verify.log` §7 |
| **negative**: `trivy fs … --exit-code 1` (no ignores) | ci-runner | 1 | fails closed on pre-existing findings — `verify.log` §8 |
| `gitleaks` on the diff | ci-runner | 0 | no secrets added — `verify.log` §9a |
| `gitleaks` changed-file snapshot vs base | ci-runner | 1 | only a **pre-existing** jwt finding (unchanged Supabase anon key) — `verify.log` §9c |
| **E2E setup**: `supabase start` → `db reset` (75 migrations + 6 seeds) → query `marcus@seed.test` → write `test-signin.json` | ci-runner (supabase 2.119.0) | 0 | setup path verified — `verify.log` §10 |
| **E2E execution** (branch `9afa849`): `pnpm exec playwright test tests/e2e/auth.spec.ts` | ci-runner | 1 | browser launches (no libglib error); 5 auth tests fail on `#email element(s) not found` — `/login` stuck on a loading spinner (`verify.log` §11) |
| **E2E control** (base `a72b8cc`, same worktree pattern) | ci-runner | 1 | **identical** 5-failure `#email-not-visible` result — classifies the failure as **pre-existing**, not caused by this patch (`verify.log` §11) |

- Secret scan (gitleaks): **pass for the diff** (exit 0). The only changed-file finding is a
  pre-existing hardcoded Supabase anon key in `validate.yml` (base line 396 → branch line 424),
  which this patch does not add; tracked under the `SEC-P1-002` credential work.
- Scope check (files within patch set + required exception files): **pass**.
- E2E honesty: the setup path (Supabase boot, 75 migrations, all 6 seed files, `marcus@seed.test`,
  generated credentials, Chromium launch) was verified end-to-end. The auth spec itself fails
  because `/login` never renders its form (stuck loading spinner). A control run at base
  `a72b8cc` fails **identically**, so this is a **pre-existing app/render failure**, not caused by
  this patch. The new blocking E2E gate correctly surfaces it. A green E2E run (fixing the
  pre-existing render issue) is required before `TEST-P1-001` can move to `verified-fixed`.

## Evidence bundle

- `remediation/PATCH-07/diff.patch` — SHA-256 `9B13BC1B0AC3D1E2EAB04126979BA58C98A0E9286A1EFD5ECBA20679F013E160`
- `remediation/PATCH-07/manifest.json`
- `remediation/PATCH-07/verify.log`

## Risk and rollback

- Risk: **medium**. Making the gates blocking can surface the pre-existing dependency backlog
  (30 HIGH/CRITICAL advisories, 2 critical) and any pre-existing E2E failures. The exception
  files accept that backlog only until **2026-11-03** and do not accept new findings. Making E2E
  blocking is the intended outcome of `TEST-P1-001`; the first real run may reveal additional test
  fixes, which is the point of a blocking gate.
- Rollback: `git revert 9afa84904cfc7c23abbbf3d204c584fdc4df5aa2` (workflow-only + two config files).

## Review checklist

- [ ] Diff touches only the patch-set files (plus the two required exception files)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean on the diff
- [ ] Exception allowlists are acceptable to Security (time-boxed to 2026-11-03)
- [ ] Blocking E2E now surfaces a pre-existing `/login` render failure (identical at base); decide on app fix vs temporary E2E acceptance before merge
- [ ] Rollback is practical

## Definition of done (for this set)

- Security scans (pnpm audit + Trivy fs/image) fail closed on HIGH/CRITICAL.
- E2E is blocking and self-provisioning (no committed credential dependency).
- Supabase setup/seed failures can no longer pass silently.

## Open questions

1. The 30 allowlisted HIGH/CRITICAL advisories (including 2 `next` criticals) are accepted only
   until 2026-11-03. Security should schedule dependency remediation or extend the exception list
   with an explicit decision; this patch does not bump dependencies (out of scope).
2. E2E uses locally seeded users rather than a dedicated CI test user provisioned via the
   Supabase admin API (the audit's stronger recommendation). The seed-based approach is a minimal
   workflow-only step; a product/QA decision is needed on the longer-term fixture.
3. **Blocker for a green pipeline:** the auth E2E spec fails at base and on this branch because
   `/login` is stuck on a loading spinner (the form never mounts). Making E2E blocking (the intent
   of `TEST-P1-001`) will therefore turn CI red until the pre-existing render failure is fixed.
   That app fix is outside PATCH-07's workflow-only scope; a reviewer should treat it as a
   follow-up (or temporarily owner-accept the E2E gate) before merge.
