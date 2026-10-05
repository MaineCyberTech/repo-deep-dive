# Owner-gated findings — proposals and residuals

Run: `snowride-20261005-full-main-38b34a9` · Target: `snowride` @ `38b34a9` (published at `75aba97`)

This run has **no P0** and exactly **one P1** (`FINAL-P1-001`). Its *mechanism* half is
code-fixable and is implemented in draft PR #44; the remaining half is an **owner decision**
(capture a fresh detached owner signature). No infrastructure was changed for the owner-gated
part.

## FINAL-P1-001 — Release identity is stale: attestation commit 9125913 != HEAD

- **Evidence**: `infra/compose/docker-compose.yml` (`LAUNCH_ATTESTED_COMMIT:
  9125913e5e87a105df290d9f57a9b3e7ca8722cc`, `LAUNCH_MIGRATION_HEAD: 0057_...`),
  `apps/realtime/src/config.ts` (`loadConfig` / `canPromoteRC` binding),
  `docs/runbooks/DEPLOY.md:11-14` (the previous fallback admitted "a missing export silently
  attests the OLD commit"). `INFRA-P3-002` is the same root cause.
- **Code-fixable half (done — draft PR [#44](https://github.com/MaineCyberTech/snowride/pull/44),
  commit `ef15f41`)**: the gate's expected commit is the *running* artifact's commit
  (`GIT_COMMIT`/`LAUNCH_EXPECTED_COMMIT`) and never the attested commit. A missing/stale value
  now fails closed (`attestation_commit_unverified` / `commit_mismatch`) instead of
  self-validating. Regression tests cover the no-running-commit case.
- **Owner-gated half (recommended option)**: capture a **fresh detached owner signature** over
  the canonical identity document
  (`apps/realtime/src/config.ts:canonicalLaunchAttestation`) at the released commit, migration
  head `0057_retire_consumable_category.sql`, the built image digests, and a fresh expiry:
  1. Choose the release commit `R` (and image digests `sha256:...`).
  2. Build the canonical payload with `rc`, `commit=R`, `images`, `migration=0057_...`,
     `backup`, `owner`, `attested_at`, `expires`.
  3. `openssl pkeyutl -sign -rawin -inkey owner.key -in canonical.txt -out sig.bin`
     (or `openssl dgst -sha256 -sign` for RSA/ECDSA); inject `LAUNCH_OWNER_SIGNATURE` and
     `LAUNCH_OWNER_PUBLIC_KEY` out-of-band (never committed).
  4. Deploy with `export GIT_COMMIT=$(git rev-parse HEAD)`; update `LAUNCH_ATTESTED_COMMIT`
     to `R` and the attested images.
  5. Record the signed identity + verification under `evidence/` (append-only) and update
     `docs/RELEASE_GATE.md`.
- **Alternative**: keep bounded runtime use explicitly *un-attested* (the current posture) and
  accept that `/beta`/`/launch-readiness` stay not-ready. Not recommended if an attested
  release claim is wanted.
- **Residual until decided**: the repository still contains the historical attestation at
  `9125913`; no owner signature exists for the current HEAD, so no release may be represented
  as owner-attested. Deploys fail closed until step 3–4 are performed.

## Other owner/plan-gated classes in scope (no P1 remaining)

There are no other open P1 findings. For completeness, the run's other owner-gated classes
(each remains recorded in the register, none is a P1): plan-gated / server-side branch
protection (`BP-P3-002`, read-only pass), operational RTO/RPO & restore drills
(`FINAL-P3-001`, `DR-P3-001`), retention/analytics consent (`AN-P3-001`), and third-party
credentials (host-only secrets, rotation runbook `SECRET-P3-001`). These are **not** part of
this P1 remediation and were left unchanged.
