# G2 — CI / supply chain / containers / testing — delta re-audit

Target: `main@3fa9f636c887fd28698852d37daa5dcef9593f60` (2026-11-07T01:23:44-05:00, "Promote develop -> main (Nov 7)")
Baseline: `main@6b7aa1a5` (Nov 3 full re-audit)
Delta window: `6b7aa1a..3fa9f63` (132 commits)
Worktree: `/tmp/opencode/mct-delta-g2` (read-only; no writes to app code)

## Verdict

| Status | Count |
|---|---|
| verified-fixed | 8 |
| partially-fixed | 3 |
| still-open | 3 |
| open (new) | 7 |
| regressed | 0 |
| **Total findings in lens** | **21** |

Severity of the 21: P1 5, P2 8, P3 8. New findings: 3 × P2, 4 × P3.

No active code-execution or merge bypass was found in the new AI reviewer for ordinary same-repo PRs, but the reviewer pin is cosmetic and the approval workflow fails open on a failed check query. Two controls that were reported fixed in the Nov 3 follow-up are only partly fixed on this target: the per-image Trivy exceptions still suppress the same 14 fixable HIGH CVEs in node-exporter, and the operator-doc fix left a duplicated stale monitoring table.

## Re-verification of the prior G2 IDs

| ID | Severity | Prior status | Status at 3fa9f63 | Evidence |
|---|---|---|---|---|
| CI-P1-005 | P1 | verified-fixed | **verified-fixed** | E2E run 42345667661 on PR #377 head `a58e171`: cache restore 06:09:24-06:09:59, load 06:09:59-06:12:04, `Start Supabase` **success** 06:12:04-06:12:43, Playwright green 06:16:21-06:22:43; `e2e (20.x)` check success, merged 06:23:44Z. Prior red run 41598757709 is not reproduced. |
| SBOM-P1-006 | P1 | verified-fixed | **verified-fixed** | `dependency-review.yml:28` and `docs/LICENSE_POLICY.md:25` include PSF-2.0, matching `security/license-policy.json:20`; PR #377's required `review` check success at 06:09:53Z (run 42345667680). New doc duplication is tracked as SBOM-P3-012. |
| CTR-P2-007 | P2 | verified-fixed | **partially-fixed** | Per-image mapping is implemented (`third-party-image-scan.yml:70-83,114`, `.trivyignore.d/{caddy,alertmanager,node-exporter}`), so cross-image leakage is gone. But `.trivyignore.d/node-exporter:22-35` still suppresses the same 14 fixable HIGH CVEs for the unchanged `prom/node-exporter@sha256:1b4e4438...` (`docker-compose.yml:276`). Local Trivy 0.76.2: 16 HIGH findings / 15 unique CVEs without an ignore file; only `CVE-2026-78661` remains with the per-image file, so the 14 older CVEs are still intentionally ignored. The next weekly scan will be red only because of the new CVE. |
| CTR-P3-006 | P3 | verified-fixed | **partially-fixed** | `infra/digitalocean/README.md:14-19` now lists the five services and v3.15.1/v0.29.0/node-exporter, but `README.md:14` still says `redis:7.4.11-alpine` vs compose `redis:7-alpine` (`docker-compose.yml:35`); `docs/CI.md:58-59` names `node-exporter` rather than the deploy-gated `node-exporter-probe` (`deploy-do.yml:1100`); `docs/MONITORING_AND_ALERTING.md:235-243` is a duplicate stale health table without the probe. |
| INFRA-P2-003 | P2 | verified-fixed | **partially-fixed** | Same residual doc drift as CTR-P3-006: README/CI/SBOM version and five-image fixes landed, but `docs/MONITORING_AND_ALERTING.md:235-243` duplicates the old health table and `docs/CI.md:58-59` names the wrong service; README redis tag also drifts. |
| INFRA-P3-011 | P3 | verified-fixed | **verified-fixed** | `.github/actions/prometheus-rules/action.yml:19` pins `prom/prometheus:v3.15.1@sha256:fa330...`, exactly matching `docker-compose.yml:342`; the prometheus-rules step in unit-tests run 42345667642 is green. |
| DET-P3-003 | P3 | verified-fixed | **verified-fixed** | `third-party-image-scan.yml:3-5,158` now says five images and includes node-exporter; the local resolver output is the five unique digest-pinned refs (caddy, alertmanager, node-exporter, prometheus, redis). `docs/CI.md:33` and `docs/SBOM_PROCESS.md:97-106` say five. |
| EVOL-P3-010 | P3 | verified-fixed | **verified-fixed** | `e2e.yml:56,87,112,194` uses 2.122.1; `supabase-migrations.yml:62-64` installs 2.122.1; `pnpm-lock.yaml:6802` resolves 2.122.1; `docs/CI.md:17` says 2.122.1; `package.json:51` is ^2.120.0. |
| DATA-P2-011 | P2 | open | **verified-fixed** | `scripts/preflight-check.sh:12-24` no longer aborts (`PASS=$((PASS + 1))`); a local run completed **16 passed, 0 failed, 1 skipped** (exit 0), including the duplicate-migration assertion at `:48-51`. `.github/actions/unit-tests/action.yml:152-158` runs it in the shared PR/deploy test job; that step was green in run 42345667642. |
| TEST-P2-011 | P2 | verified-fixed | **verified-fixed** | `e2e.yml:82-131,168-194`: v2 key, >=12-image guard, fail-loud partial handling, explicit save. Run 42345667661 was a cache hit, loaded and started Supabase successfully, and passed Playwright. |
| TEST-P2-010 | P2 | open | **verified-fixed** | PR #377 (head `a58e171` -> main) created 05:31:38Z, merged 06:23:44Z; all eight required contexts on the head were success before merge (test 06:10:49, security-scan 06:09:05, secrets-scan 06:08:34, lint 06:09:04, typecheck 06:09:13, e2e 06:22:46, Dependency Review 06:09:53, CodeQL 06:11:26). Caveat: 0 reviews (BP-P1-004). |
| BP-P1-004 | P1 | still-open | **still-open** | PR #377 merged 2026-11-07T06:23:44Z with `GET /pulls/377/reviews` = `[]` while `.github/branch-protection/main.json:3-19` requires 1 approving review + CODEOWNERS + `enforce_admins:true`; PR #376 merged with only `github-actions[bot]`'s approval and no human review; branch-protection-audit runs 41491379135, 40340906384, 39273950100 all failed. |
| CI-P1-001 | P1 | still-open | **still-open** | `docs/GITHUB_SECRETS_AND_VARIABLES_MATRIX.md:9-16` and `docs/RELEASING.md:141-154` still state that `prod-approval` has no required reviewers, so prod jobs run without pausing. No repo-side change in the delta. |
| CI-P1-003 | P1 | still-open | **still-open** | `docs/RELEASING.md:193-199` and `docs/GITHUB_SECRETS_AND_VARIABLES_MATRIX.md:204-236` still state that prod-approval lacks `SUPABASE_*`/`JWT_SECRET`/migration secrets, `DO_API_TOKEN` returns 401, and prod has no `DROPLET_IP` fallback. |

Notes:
- `TEST-P2-010` is marked verified-fixed only for the check-timing condition; the separate review bypass is BP-P1-004, still open.
- `CTR-P2-007`, `CTR-P3-006` and `INFRA-P2-003` were marked fixed in the Nov 3 follow-up. The delta shows they are only partly fixed; this is a correction of the prior status, not a new regression (except the duplicated doc block, which the Nov 3 doc patch itself introduced).

## New findings

### CI-P2-012 — AI-review pin is cosmetic; reviewer code comes from mutable `main` with all repo secrets (P2, open)

- Caller: `.github/workflows/ai-review.yml:25` pins `MaineCyberTech/ai-reviewer/.github/workflows/ai-review.yml@d401040c9777a63195396cbf177eec78192284d2`.
- Callee at that pin: `MaineCyberTech/ai-reviewer@d401040c:.github/workflows/ai-review.yml:58-64` checks the reviewer repo out at **`ref: main`** and then executes `.ai-reviewer/.github/scripts/ai_review.py` and `.ai-reviewer/.github/prompts/ai-review.md` (`:83-87`). `main` has already moved: d401040c (2026-11-06T17:03Z) → 80872e5 (2026-11-06T19:32Z).
- Amplifier: `.github/workflows/ai-review.yml:26` uses `secrets: inherit`, so every repository secret is available to that checkout, not only the three `AI_REVIEW_*` values documented in `AGENTS.md:109-111`.
- Impact: a change merged to `ai-reviewer/main` (a different repository) executes in this repo with this repo's secrets and a write `GITHUB_TOKEN`; the 40-character pin only fixes the workflow YAML, not the code. No active compromise was observed; this is a defense-in-depth failure.
- Remediation: check out the reviewer at the same SHA (or vendor the script/prompt), pass only the three AI secrets explicitly, and review the new SHA whenever it is bumped.

### CI-P2-013 — Bot approval fails open when `gh pr checks --required` errors (P2, open)

- `MaineCyberTech/ai-reviewer@d401040c:.github/workflows/bot-approval.yml:61-81`: both the wait loop (`:62`) and the final gate (`:76`) use `checks="$(gh pr checks "$PR" --required --json name,state)" || checks='[]'`.
- On any command failure (API/rate limit, auth, or no resolvable required contexts), `checks` becomes `[]`, `pending` is 0, and the workflow executes `POST /repos/$REPO/pulls/$PR/reviews` with `event=APPROVE` (`:83-85`).
- The caller grants the needed token at `.github/workflows/bot-approval.yml:9-12`. The gate is fail-open exactly when the check query cannot be trusted.
- Remediation: refuse on a non-zero exit/empty output, require a non-empty required-context set for the protected branch, and only approve after a fresh successful query.

### CI-P3-016 — Dependabot Node-major hold does not cover the app Dockerfile directories (P3, open)

- `.github/dependabot.yml:55-59` applies the `node` semver-major ignore only to `directory: "/"`.
- The per-directory docker entries for `/apps/api` (`:64-72`), `/apps/web` (`:74-82`) and `/apps/worker` (`:84-92`) have no ignore block, while all three Dockerfiles start `FROM node:20-alpine` (`apps/api/Dockerfile:1`, `apps/web/Dockerfile:1`, `apps/worker/Dockerfile:1`).
- Issue #361 holds the Node 25/26 jump; the closed PRs were exactly those directories: #266 `/apps/api`, #268 `/apps/web`, #269 `/apps/worker`. Dependabot will recreate them on the next weekly run.
- Remediation: add the same ignore to each app docker entry (or consolidate the Docker config).

### CI-P3-017 — AI review fails on Dependabot PRs, red-checking them and blocking bot approval (P3, open)

- `.github/workflows/ai-review.yml:5-7` triggers on every `pull_request`, including Dependabot. The callee declares `AI_REVIEW_ENDPOINT` and `AI_REVIEW_API_KEY` as required (`MaineCyberTech/ai-reviewer@d401040c:.github/workflows/ai-review.yml:16-22`) and exits when they are empty (`:75-78`).
- Dependabot-triggered runs do not receive repository Actions secrets. Observed 2026-11-07: ai-review run 42346875347 on Dependabot PR #379 failed with annotations "Secret AI_REVIEW_ENDPOINT is required, but not provided while calling" and "Secret AI_REVIEW_API_KEY is required, but not provided while calling". Run 42346888919 (PR #382) also failed; 42346879642/42346884197 were cancelled. No AI review comment exists on #379-#382, so bot-approval cannot approve them.
- Remediation: skip Dependabot/fork PRs at the caller job level, or add the values as Dependabot secrets; if advisory, make missing secrets a skip rather than a red check.

### CI-P3-018 — Bot approval accepts a historical AI-review comment, not a review of the approved SHA (P3, open)

- `bot-approval.yml:54-59` only requires that some `github-actions[bot]` comment contains "AI review (advisory)". It does not bind the comment to the current head or require the latest ai-review run to have succeeded.
- The caller now triggers on `synchronize` (`.github/workflows/ai-review.yml:7`); a failed/cancelled review after a new push leaves the old comment in place and the approval gate still passes.
- No current exploit observed; the gate proves a review exists, not that it covers the head SHA. Remediation: stamp the head SHA in the comment and require it to match the PR head.

### EVOL-P2-003 — tailwind-merge 3.x is paired with Tailwind CSS 3.4 (P2, open)

- `packages/ui/package.json:32` and `apps/web/package.json:32` declare `tailwind-merge: ^3.7.0`, while `apps/web/package.json:54` stays on `tailwindcss: ^3.4.19`; `packages/ui/src/lib/cn.ts:5` calls `twMerge` for every shared component.
- The tailwind-merge v3.7.0 README says: "Supports Tailwind v4.0 up to v4.3 (if you use Tailwind v3, use tailwind-merge v2.6.0)".
- Reproduced with the 3.7.0 bundle: `twMerge("outline-none", "outline")` returns both classes; shadow/rounded renames also change merge semantics versus Tailwind 3.
- Remediation: pin tailwind-merge 2.6.x while on Tailwind 3, or finish the Tailwind 4 migration before keeping v3; add a `cn()` fixture for v3 override names.

### SBOM-P3-012 — `docs/LICENSE_POLICY.md` lists the allowed-license block twice (P3, open)

- `docs/LICENSE_POLICY.md:22-29` contains the list twice: lines 23-26 end at `UPL-1.0`, then lines 28-29 repeat `CC-BY-4.0` through `UPL-1.0`.
- Introduced by the PSF-2.0 fix (commit 5601b97e) when the new full list was inserted above the old continuation. Enforcement is correct (`security/license-policy.json:20`, `dependency-review.yml:28`), so this is documentation-only.
- Remediation: delete lines 28-29.

## Dependabot holds / major upgrades

- Holds tracked in issue #361: `next` 16 and Docker `node` 25/26 remain held; the matching ignore entries for the completed upgrades were removed in the landing PRs (verify: `.github/dependabot.yml` has only `next` in npm and `node` in the root docker entry).
- Landed majors: dotenv 18.0.9 (#372), chromatic 18.13.9 (#371), bullmq 6.7.1 (#376), lucide-react 1.70.0 (#374); tailwind-merge 3.7.0 and jsdom 30.5.2 also landed. `dotenv` uses programmatic `config({ path, quiet: true })` (`apps/api/src/main.ts:2`, `apps/worker/src/env.ts:2`) so the v18 preload removal does not apply; BullMQ 6 still gets an explicit `ioredis` (`apps/api/package.json:30`, `apps/worker/package.json:25`); jsdom 30's non-configurable `window.location` is handled by `apps/web/lib/navigation.ts:1-12`.
- The hold is **not complete**: CI-P3-016 (Node major ignores missing from `/apps/*`).
- The tailwind-merge 3 upgrade is the one major that does not match its peer framework: EVOL-P2-003.

## Measured test counts

- `AGENTS.md:119-127` and `README.md:44-49,127,222` state 4,733 tests / 524 suites (API 2,048/178, Web 2,045/309, SDK 327/5, Worker 313/32, E2E 91 spec files).
- The counts are enforced, not just prose: `.github/actions/unit-tests/action.yml:61-70` sets `MCT_VERIFY_TEST_COUNTS=1`, and `scripts/check-docs-counts.mjs` compares each package total against the `.jest-results.json` produced by `test:coverage`. The unit-tests step (including "Check docs counts") was green in run 42345667642 on PR #377 head `a58e171`.
- No drift found; no new test-count finding.

## What changed since Nov 3

- The Nov 3 remediation batches (#335/#336/#339 etc.) fixed the E2E cache/CLI, PSF-2.0 license gate, promtool/production Prometheus alignment, five-image scan description, Supabase CLI pin, preflight duplicate-migration gate, and the main operator README table.
- Nov 6-7 added the advisory AI reviewer and bot approval (`ai-review.yml`, `bot-approval.yml`, reusable workflows pinned to `d401040c`), Dependabot hold ignores for #361, the alpine/zlib container patch upgrades (`apk upgrade --no-cache`), dotenv/chromatic/bullmq/lucide majors, and the jsdom 30 harness fix.
- The biggest new risk surface is the AI reviewer: the caller pins the workflow file, but the callee fetches `main` for the script/prompt and receives `secrets: inherit`; bot approval is triggered by a maintainer label but its check gate fails open. Neither produced an observed compromise.
- The Nov 3 doc patch introduced a duplicated stale monitoring table and a duplicated license list; both are documentation-only P3s.

## Coverage and limits

- Read-only worktree at `origin/main`; no app-code writes. Local executions: `bash scripts/preflight-check.sh` (16/0/1, exit 0); Trivy 0.76.2 scans of the pinned five third-party images with and without the per-image ignore files (results above); the five-image resolver extracted from `third-party-image-scan.yml`; `git diff`/`git log` on the delta.
- Live evidence came from the unauthenticated GitHub API and public run pages: PR #377/#376, check-runs for `a58e171` and `3fa9f636`, E2E job 42345667661, Test job 42345667642, ai-review runs 42346875347/42346888919/42346879642/42346884197. The live branch-protection API is 401 without auth, so BP-P1-004 is proved from the merged PR/review data rather than the live protection object.
- Not re-audited here: untouched G2-adjacent domains (secrets rotation, full SBOM licence tree, container runtime hardening) beyond the IDs listed above. Trivy results depend on the vulnerability DB at 2026-11-07; the next weekly run may differ as new CVEs land.
