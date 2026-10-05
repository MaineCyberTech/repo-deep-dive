# Patch plan

## FINAL-P1-001 — Release identity is stale: attestation commit 9125913 != HEAD 38b34a9

Capture a fresh owner detached signature over the canonical identity at the released commit + migration head (0057) and the built image digests.

## CHAIN-P2-001 — Low-severity credential-to-admin chain (no rotation + no admin rate limit + mode disclosure)

Prioritise the SECRET-P2-001 fail-closed fix and METRICS_TOKEN rotation; add an admin rate limit.

## DET-P2-001 — [PORT] 20 evidence/ files committed with mixed line endings

Leave evidence bytes untouched (MANIFEST.sha256 pins them); adjust the deterministic check to skip `-text` paths instead of flagging them.

## HYGIENE-P2-001 — Only apps/web is linted; four workspaces have no lint script

Add eslint config + lint scripts to the remaining workspaces and make `npm run lint` cover all of them.

## HYGIENE-P2-002 — Large generated evidence artifacts inflate the repository

Archive large generated exports outside git (LFS/object store) and keep only manifests/hashes in-tree.

## INV-P2-001 — Evidence tree dominates the repository by file count and size

Move multi-MB generated exports to Git LFS or an artifact store, keeping only the hash-pinned ledgers in-tree; keep the append-only rule for ledgers.

## SC-P2-001 — docs/SUPPLY_CHAIN.md is stale against the shipped supply-chain gates

Update docs/SUPPLY_CHAIN.md to the current blocking posture and note the cleared grpc-js advisory.

## SECRET-P2-001 — Empty service-role key silently disables trusted persistence

Fail boot/readiness when NODE_ENV=production and the service-role key is empty; add a readiness sub-check for the service client.

## ADMIN-P3-001 — Admin mutations have no rate limit or step-up authentication

Add a per-actor admin rate limit and require re-validation for high-impact mutations (refund, rollover, teardown).

## AI-P3-001 — AGENTS.md does not reference the audit-pack / full-domain workflow

Add a short 'audits' pointer in AGENTS.md to docs/audits and the evidence doctrine.

## AN-P3-001 — Anonymous performance sampling has no runtime consent/retention gate

Enforce sampling/retention in code (or document the legal basis) and surface the current rate in the privacy notice.

## API-P3-001 — Public operational endpoints are unauthenticated and unversioned

Serve only the minimum public subset and add an explicit contract version or deprecation window.

## API-P3-002 — /config exposes rollout-mode values to unauthenticated clients

Restrict /config to the fields the client actually needs, or gate it behind the metrics/ops token.

## ARCH-P3-001 — Authoritative room/lobby state is process-local and lost on restart

Document the maintenance-window expectation in the deploy runbook, and drain rooms before recreate (stop_grace_period is 30s).

## BP-P3-001 — BRANCH_PROTECTION.md runbook lists a stale required-check set

Update the runbook's required-check list (or make it reference the policy file as the single source).

## BP-P3-002 — Live branch protection not verified in this read-only pass

Run the live audit with an admin token and store the raw PASS output under evidence/.

## CI-P3-001 — CODEOWNERS is a personal account; required review is a single point

Replace with an organisation team handle once the repo moves under the org; document the fallback reviewer.

## CTR-P3-001 — App images use local mutable tags with no in-repo digest binding

Have the release job write the built image digests into the attestation evidence and verify them at deploy.

## DATA-P3-001 — Live production schema state unverified in this audit

Capture a live `migration list`/schema-head export into evidence at the release commit, bound like the existing attested head.

## DET-P3-001 — [SUPPLY] 2 container images without a digest pin

Keep the documented out-of-band released-digest record (LAUNCH_ATTESTED_IMAGES) and the docs/runbooks/DEPLOY.md refresh step.

## DOC-P3-001 — AGENTS.md migration range is stale (0056 vs head 0057)

Update the range (or reference the directory/manifest) so the head is not duplicated in prose.

## DR-P3-001 — Latest backup/restore drill evidence is not committed

Run and commit a dated restore drill transcript (append-only) and reference it from the release gate.

## EVOL-P3-001 — No ADR records the supply-chain/attestation hardening decision

Add an ADR for the detached-attestation and SBOM/supply-chain policy so the rationale is durable.

## FILE-P3-001 — No application-layer maximum replay size bound

Reject ghosts above a documented byte ceiling at admission, with a test, and reflect it in the bucket policy.

## FINAL-P3-001 — Operational reliability drills are not exercised per release

Bind one restore drill + one tabletop to each release candidate and append the transcripts.

## INFRA-P3-001 — Committed host crontab references out-of-repo paths/binaries

Bring the referenced host scripts (watchdog, backup, tunnel) under infra/ops/ or record their hashes as prerequisites.

## INFRA-P3-002 — Committed launch attestation commit is stale versus repository HEAD

Re-run the owner attestation at the released HEAD (see FINAL-P1-001).

## IR-P3-001 — No committed incident tabletop exercise for the current revision

Run a tabletop, capture the transcript append-only, and link it from the release gate.

## MOB-P3-001 — PWA manifest provides only an SVG icon (no raster/maskable PNG)

Add a 512x512 PNG maskable icon alongside the SVG and validate installability in the mobile journey.

## NOTIF-P3-001 — User notification preferences are recorded but never delivered

Either label preferences as 'future' in the UI or implement a delivery path with opt-in, retry, and a delivery log.

## OBS-P3-001 — Metrics are process-local; durable history depends on the snapshot timer

Make the snapshot timer mandatory in production compose/readiness and document the retention horizon.

## PERF-P3-001 — No performance regression gate on pull requests

Add a bounded frame-budget/capacity smoke gate to CI (or required check) with a documented threshold.

## PRIV-P3-001 — Account-erasure cascade not covered by a SQL negative test

Add an account-deletion cascade negative test to supabase/tests and run it in the migrations job.

## REL-P3-001 — Release notes/changelog are maintained manually

Add a generator (e.g. conventional-commits or git-cliff) and wire it to the release process.

## RES-P3-001 — Rollout-switch rollback requires a process restart

Document the restart-based rollback SLO and consider a durable, hot-applied override for the highest-risk switch.

## RLS-P3-001 — Claim-less SQL callers are treated as trusted by social_guard_*

Make the trusted branch require an explicit service-role assertion rather than the absence of claims; add a negative test.

## SBOM-P3-001 — SBOM is a 90-day CI artifact, not bound to the release attestation

Publish the SBOM (and its hash) to a durable release location and reference it from the launch attestation identity.

## SC-P3-001 — Registry signature verification is continue-on-error (provenance not blocking)

Track an owner decision/timebox and promote npm audit signatures to blocking once the upstream attestation issue clears.

## SEC-P3-001 — Ops/METRICS_TOKEN compared non-constant-time and has no rotation path

Use crypto.timingSafeEqual over equal-length buffers and document METRICS_TOKEN rotation alongside the other host secrets.

## SECRET-P3-001 — METRICS_TOKEN has no rotation path

Document METRICS_TOKEN rotation and use a constant-time compare.

## TEST-P3-001 — Local verify-all gate is weaker than the CI pipeline

Add a `verify-all --ci-parity` mode or document the exact gap in AGENTS.md so the local claim is bounded.

## UX-P3-001 — ESLint react-hooks/exhaustive-deps warning in the main game shell

Fix the dependency array or add a documented eslint-disable with justification.

