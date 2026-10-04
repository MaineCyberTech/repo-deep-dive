# Executive Summary — post-merge verification

**Repo:** `MaineCyberTech/mainecybertech` · **Commit:** `a97425db` (develop) ·
**Original run:** `20261003-0018-fix-p2-batch-31-2295958d` · **Date:** 2026-10-04

## Verdict

**GO WITH CONDITIONS** for develop. All P0/P1 code remediation is on the default
line and verified at the merged commit; one P1 (`CI-P1-001`) remains
operator-blocked on the `prod` environment, and five P2/P3 findings are owner
decisions rather than code defects.

## What was verified

- The 16 remediation PRs stranded on `fix/p2-batch-31` were integrated to
  develop by PR #72 (merge `a97425db`) with conflict resolution against the
  earlier #70/#71 fixes. CI (unit/lint/typecheck/E2E/dependency+license gates/
  secret scan/prompt provenance) is green at the merge; CodeQL remains red on the
  pre-existing alert tracked in issue #31.
- Every original finding was re-checked against the merged tree and, where
  runtime-observable, against the dev deployment.
- The deploy pipeline (`deploy-do` 37188587849) passed end to end, including the
  new digest-bound SBOM attestations; the dev droplet is healthy at `a97425db`.
  New fail-closed boot gates are satisfied: `FIELD_ENCRYPTION_KEY`,
  `TURNSTILE_SECRET_KEY` (Cloudflare test pair on dev), and a non-empty
  `RLS_READS_ENABLED`.

## Results

| Status | Count | Notes |
|---|---:|---|
| verified-fixed | 34 | Evidence per finding in `verification_log.md` |
| partially-fixed | 9 | Owner/operator work outstanding (below) |
| still-open | 1 | `CI-P1-001` — prod environment provisioning |
| regressed | 0 | No P0/P1 regressions in the machine re-audit |

## Conditions / follow-ups

1. **`CI-P1-001` (P1, operator):** the fail-closed deploy gate is merged, but the
   `prod` environment still has only the two AWS role secrets and no reviewer
   protection beyond the `prod`/`prod-approval` reviewers already configured.
2. **`HYG-P2-001` / `HYG-P2-002` (owner):** corpus externalization and the
   duplicate product catalogs remain decisions.
3. **`ARCH-P2-001` / `CI-P3-001` / `OBS-P2-003` (owner):** single-droplet SPOF,
   `main` promotion/scheduled jobs, and backup verification.
4. **`ARCH-P2-002` (operational):** continue the per-module RLS rollout; the
   startup guard now refuses an empty read allow-list in production.
5. Machine findings: exec bits on 17 scripts (`DET-P2-002`, pre-existing) and
   digest-pinned images (`DET-P3-004`) are optional hardening.

## Evidence highlights

- `apps/worker/src/tasks/orphan-cleanup.ts` — folder entries never reach
  `remove()`; unsafe paths abort the bucket; chunked reference lookups.
- `apps/api/src/config/env.ts` — production refuses to boot without
  `FIELD_ENCRYPTION_KEY` or `TURNSTILE_SECRET_KEY`; `lib/field-encryption.ts`
  throws rather than writing reversible plaintext.
- `apps/api/src/routes/search.ts` — tenant scope fails closed.
- `apps/api/src/middleware/api-key.ts` — machine credentials authenticate
  through the existing permission chain.
- Dev droplet: internal endpoints (`/health/detail`, `/api/v1/docs`,
  `/api/v1/openapi.json`, `/api/v1/metrics`) 404 without a token.
