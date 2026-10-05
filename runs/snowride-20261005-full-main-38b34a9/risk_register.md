# Follow-up register

Run: `snowride-20261005-full-main-38b34a9` · Target: `snowride` @ `38b34a9` · Profile: base

Register mirrored 1:1 with `risk_register.md` so `tools/check_run.sh` passes.

| Finding | Severity | Title | Owner | Target | Status | Note |
|---|---|---|---|---|---|---|
| FINAL-P1-001 | P1 | Release identity is stale: attestation commit 9125913 != HEAD 38b34a9 | @owner | FINAL | partially-fixed | Gate mechanism hardened (draft PR #44, commit ef15f41): expectedCommit is the running commit (GIT_COMMIT/LAUNCH_EXPECTED_COMMIT) and a missing/stale value fails closed (attestation_commit_unverified), so the stale committed attestation no longer self-validates. Residual owner-gated: capture a fresh detached owner signature at the released commit + migration head 0057 + built image digests. See OWNER_GATED_PROPOSALS.md. |
| CHAIN-P2-001 | P2 | Low-severity credential-to-admin chain (no rotation + no admin rate limit + mode disclosure) | @owner | CHAIN | open |  |
| DET-P2-001 | P2 | [PORT] 20 evidence/ files committed with mixed line endings | @owner | DET | owner-accepted | False-positive-by-design: evidence is append-only and hash-pinned. |
| HYGIENE-P2-001 | P2 | Only apps/web is linted; four workspaces have no lint script | @owner | HYGIENE | open |  |
| HYGIENE-P2-002 | P2 | Large generated evidence artifacts inflate the repository | @owner | HYGIENE | owner-accepted | Evidence is append-only by doctrine; recorded as owner-accepted. |
| INV-P2-001 | P2 | Evidence tree dominates the repository by file count and size | @owner | INV | owner-accepted | Size is intentional append-only evidence; recorded as owner-accepted. |
| SC-P2-001 | P2 | docs/SUPPLY_CHAIN.md is stale against the shipped supply-chain gates | @owner | SC | open |  |
| SECRET-P2-001 | P2 | Empty service-role key silently disables trusted persistence | @owner | SECRET | open |  |
| ADMIN-P3-001 | P3 | Admin mutations have no rate limit or step-up authentication | @owner | ADMIN | open |  |
| AI-P3-001 | P3 | AGENTS.md does not reference the audit-pack / full-domain workflow | @owner | AI | open |  |
| AN-P3-001 | P3 | Anonymous performance sampling has no runtime consent/retention gate | @owner | AN | open |  |
| API-P3-001 | P3 | Public operational endpoints are unauthenticated and unversioned | @owner | API | open |  |
| API-P3-002 | P3 | /config exposes rollout-mode values to unauthenticated clients | @owner | API | open |  |
| ARCH-P3-001 | P3 | Authoritative room/lobby state is process-local and lost on restart | @owner | ARCH | partially-fixed | Prior ARCH-P2-003; the publish-override half is now durable. |
| BP-P3-001 | P3 | BRANCH_PROTECTION.md runbook lists a stale required-check set | @owner | BP | open |  |
| BP-P3-002 | P3 | Live branch protection not verified in this read-only pass | @owner | BP | open |  |
| CI-P3-001 | P3 | CODEOWNERS is a personal account; required review is a single point | @owner | CI | open |  |
| CTR-P3-001 | P3 | App images use local mutable tags with no in-repo digest binding | @owner | CTR | open |  |
| DATA-P3-001 | P3 | Live production schema state unverified in this audit | @owner | DATA | open |  |
| DET-P3-001 | P3 | [SUPPLY] 2 container images without a digest pin | @owner | DET | owner-accepted | False-positive: locally built images, not registry pulls. |
| DOC-P3-001 | P3 | AGENTS.md migration range is stale (0056 vs head 0057) | @owner | DOC | open |  |
| DR-P3-001 | P3 | Latest backup/restore drill evidence is not committed | @owner | DR | open |  |
| EVOL-P3-001 | P3 | No ADR records the supply-chain/attestation hardening decision | @owner | EVOL | open |  |
| FILE-P3-001 | P3 | No application-layer maximum replay size bound | @owner | FILE | open |  |
| FINAL-P3-001 | P3 | Operational reliability drills are not exercised per release | @owner | FINAL | open |  |
| INFRA-P3-001 | P3 | Committed host crontab references out-of-repo paths/binaries | @owner | INFRA | open |  |
| INFRA-P3-002 | P3 | Committed launch attestation commit is stale versus repository HEAD | @owner | INFRA | partially-fixed | Same root as FINAL-P1-001; the gate now fails closed on the stale committed attestation (draft PR #44). Re-attestation at the released HEAD remains owner-gated. See OWNER_GATED_PROPOSALS.md. |
| IR-P3-001 | P3 | No committed incident tabletop exercise for the current revision | @owner | IR | open |  |
| MOB-P3-001 | P3 | PWA manifest provides only an SVG icon (no raster/maskable PNG) | @owner | MOB | open |  |
| NOTIF-P3-001 | P3 | User notification preferences are recorded but never delivered | @owner | NOTIF | open |  |
| OBS-P3-001 | P3 | Metrics are process-local; durable history depends on the snapshot timer | @owner | OBS | open |  |
| PERF-P3-001 | P3 | No performance regression gate on pull requests | @owner | PERF | open |  |
| PRIV-P3-001 | P3 | Account-erasure cascade not covered by a SQL negative test | @owner | PRIV | open |  |
| REL-P3-001 | P3 | Release notes/changelog are maintained manually | @owner | REL | open |  |
| RES-P3-001 | P3 | Rollout-switch rollback requires a process restart | @owner | RES | open |  |
| RLS-P3-001 | P3 | Claim-less SQL callers are treated as trusted by social_guard_* | @owner | RLS | open |  |
| SBOM-P3-001 | P3 | SBOM is a 90-day CI artifact, not bound to the release attestation | @owner | SBOM | open |  |
| SC-P3-001 | P3 | Registry signature verification is continue-on-error (provenance not blocking) | @owner | SC | open |  |
| SEC-P3-001 | P3 | Ops/METRICS_TOKEN compared non-constant-time and has no rotation path | @owner | SEC | open |  |
| SECRET-P3-001 | P3 | METRICS_TOKEN has no rotation path | @owner | SECRET | open |  |
| TEST-P3-001 | P3 | Local verify-all gate is weaker than the CI pipeline | @owner | TEST | open |  |
| UX-P3-001 | P3 | ESLint react-hooks/exhaustive-deps warning in the main game shell | @owner | UX | open |  |
