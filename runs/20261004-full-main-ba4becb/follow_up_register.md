# Follow-up register

Run: `20261004-full-main-ba4becb` · Target: `falcon-edge` @ `ba4becb` · Profile: base

Register mirrored 1:1 with `risk_register.md` so `tools/check_run.sh` passes.

| Finding | Severity | Title | Owner | Target | Status | Note |
|---|---|---|---|---|---|---|
| EXEC-P1-001 | P1 | Release-gate condition (terminal revocation) is closed | @owner | EXEC | verified-fixed | re-audit 2026-10-04: closed |
| FINAL-P1-001 | P1 | Release blocker (non-terminal revocation) is closed | @owner | FINAL | verified-fixed | re-audit 2026-10-04: closed |
| SEC-P1-001 | P1 | Re-enrollment no longer resets a REVOKED/RETIRED sensor | @owner | SEC | verified-fixed | merged PS-001/#17; re-audit 2026-10-04: closed |
| API-P2-001 | P2 | Cursor pagination contract now honoured (keyset pagination) | @owner | API | verified-fixed | merged 71cffcd; re-audit 2026-10-04: closed |
| API-P2-002 | P2 | SensorSummary.queueDepth now returned | @owner | API | verified-fixed | merged a4b388b; re-audit 2026-10-04: closed |
| ARCH-P2-001 | P2 | Control plane still executes a mutable working tree (dirty-guarded, not pinned) | @owner | ARCH | still-open | re-audit 2026-10-04: still-open; dirty guard added as mitigation |
| ARCH-P2-002 | P2 | Edge control plane is a co-tenant single point of failure on the shared lab host | @owner | ARCH | still-open | re-audit 2026-10-04: still-open |
| AUTH-P2-001 | P2 | Device mTLS private key is group-readable (0640), contradicting its documented 0600 | @owner | SEC | still-open | re-audit 2026-10-04: AUTH-001 held (#40); key still 0640 at ba4becb |
| BP-P2-001 | P2 | Branch protection / required checks cannot be enforced on the current GitHub plan | @owner | BP | owner-accepted | re-audit 2026-10-04: owner-accepted (plan-gated) |
| CHAIN-P2-001 | P2 | Chain: co-tenant read of the agent key -> control-plane signing seed compromise -> unattended fleet code swap | @owner | CHAIN | still-open | synthesised from AUTH/FILE/SUPPLY/ARCH findings at ba4becb |
| CI-P2-001 | P2 | CI toolchain is downloaded and hash-verified (pinning enforced) | @owner | CI | verified-fixed | re-audit 2026-10-04: closed |
| CI-P2-002 | P2 | bake-image no longer interpolates secrets into script text | @owner | CI | verified-fixed | merged #33 @0ee35df; re-audit 2026-10-04: closed |
| DATA-P2-001 | P2 | Idempotency table is now bounded and stores a digest, not full bodies | @owner | DATA | verified-fixed | re-audit 2026-10-04: closed |
| DATA-P2-002 | P2 | Foreign keys and retention indexes added for events/state/heartbeat history | @owner | DATA | verified-fixed | re-audit 2026-10-04: closed |
| DATA-P2-003 | P2 | Schema migration mechanism now exists (not only CREATE TABLE IF NOT EXISTS) | @owner | DATA | verified-fixed | re-audit 2026-10-04: closed |
| EXEC-P2-001 | P2 | Production readiness remains insufficient-evidence | @owner | EXEC | still-open | re-audit 2026-10-04: still-open |
| FEAT-P2-001 | P2 | SensorSummary.queueDepth is now populated (was documented-only) | @owner | FEAT | verified-fixed | merged falcon-edge a4b388b; re-audit 2026-10-04: closed |
| FILE-P2-001 | P2 | Update artifact host allowlist exists but is not configured in the shipped image | @owner | FILE | still-open | mechanism added (CHAIN/API/SEC fix); default config leaves it disabled |
| FINAL-P2-001 | P2 | Cross-cutting theme: automation artifacts are not continuously bound to their sources | @owner | FINAL | still-open | re-audit 2026-10-04: still-open |
| HYG-P2-001 | P2 | Summary documentation no longer hardcodes drifted test counts / Dependabot cadence | @owner | HYGIENE | verified-fixed | re-audit 2026-10-04: closed |
| HYG-P2-002 | P2 | Committed derived artifacts are guarded against staleness | @owner | HYGIENE | verified-fixed | re-audit 2026-10-04: closed |
| INFRA-P2-001 | P2 | Lab config and shipped image config deliberately diverge (bind/TLS/auto-apply) | @owner | INFRA | partially-fixed | guards + LAB ONLY comments added; divergence remains by design |
| INV-P2-001 | P2 | Committed raw evidence is large and only now budget-guarded | @owner | INV | verified-fixed | re-audit 2026-10-04: closed (budget guard present) |
| INV-P2-002 | P2 | Pack inventory tooling now emits routes/schema/entrypoints | @owner | INV | verified-fixed | re-audit 2026-10-04: closed |
| NOTIF-P2-001 | P2 | No alert/notification delivery path from the edge program (email/push/pager) | @owner | NOTIF | still-open | delivery gap; tracked as OBS-P2-001 |
| OBS-P2-001 | P2 | No alert delivery path (no Alertmanager/pager); rules are visible only in Prometheus/Grafana | @owner | OBS | still-open | re-audit 2026-10-04: still-open |
| OBS-P2-002 | P2 | Inventory alert metrics depend on host-side SSH to each sensor (single point of failure) | @owner | OBS | still-open | re-audit 2026-10-04: still-open |
| RES-P2-001 | P2 | Single-host control plane has no warm standby or tested failover | @owner | RES | still-open | related ARCH-P2-002; re-audit 2026-10-04: still-open |
| SC-P2-001 | P2 | CI installs Python dependencies with exact versions and hashes | @owner | SC | verified-fixed | re-audit 2026-10-04: closed |
| SC-P2-002 | P2 | Secret scanning covers git history, not only the working tree | @owner | SC | verified-fixed | re-audit 2026-10-04: closed |
| SC-P2-003 | P2 | CI downloads lint/scan binaries with embedded SHA-256 verification | @owner | SC | verified-fixed | re-audit 2026-10-04: closed |
| SC-P2-004 | P2 | Credential-bearing image artifacts/releases rely solely on private-repo access | @owner | SC | owner-accepted | re-audit 2026-10-04: owner-accepted |
| SEC-P2-001 | P2 | HTTP transport hardening (rate limit, headers, slow-client guard) present | @owner | SEC | verified-fixed | re-audit 2026-10-04: closed |
| SEC-P2-002 | P2 | Inventory metrics collector no longer disables SSH host-key verification | @owner | SEC | verified-fixed | re-audit 2026-10-04: closed |
| SEC-P2-003 | P2 | Raw host inventory file no longer world-readable on sensors | @owner | SEC | verified-fixed | re-audit 2026-10-04: closed |
| SUPPLY-P2-001 | P2 | Shipped sensor image auto-applies signed updates with no per-update human gate | @owner | SC | still-open | prior 'verified-fixed' was docs-only (#41 @3ae7e75, 1 file); image default still true at ba4becb |
| TEST-P2-001 | P2 | Test-count claims no longer hardcoded in docs | @owner | TEST | verified-fixed | re-audit 2026-10-04: closed |
| TEST-P2-002 | P2 | Regression test for re-enrolment of a REVOKED/RETIRED sensor added | @owner | TEST | verified-fixed | re-audit 2026-10-04: closed |
| ACM-P3-001 | P3 | Operator identity map and revocation are implemented; single-operator fallback still allowed | @owner | ACM | partially-fixed | multi-operator implemented; fallback retained for lab |
| ADMIN-P3-001 | P3 | Admin surface is the operator CLI + mTLS operator APIs; no web console | @owner | ADMIN | open | no web admin console; CLI/API surface reviewed |
| AI-P3-001 | P3 | Repository text is treated as untrusted instruction input by the agent rules | @owner | AI | partially-fixed | rule present; no automated injection check |
| AN-P3-001 | P3 | Not applicable: no third-party analytics or tracking SDKs | @owner | AN | open | not applicable |
| API-P3-001 | P3 | Problem `instance` now reflects the request path | @owner | API | verified-fixed | re-audit 2026-10-04: closed |
| ARCH-P3-001 | P3 | Bare stdlib HTTP transport now has connection cap, timeout and rate limiting | @owner | ARCH | verified-fixed | re-audit 2026-10-04: closed |
| BILL-P3-001 | P3 | Not applicable: no billing, payment, or reconciliation code | @owner | BILL | open | not applicable |
| CI-P3-001 | P3 | Branch-protection documentation matches implemented Dependabot-merge behavior | @owner | CI | verified-fixed | merged #36 @a169b7d; re-audit 2026-10-04: closed |
| CTR-P3-001 | P3 | Not applicable: no container runtime in the repository | @owner | CTR | open | not applicable |
| DATA-P3-001 | P3 | Queue age-expiry / purge_expired wiring | @owner | DATA | verified-fixed | re-audit 2026-10-04: closed |
| DET-P3-001 | P3 | [GIT] No LICENSE file | @owner | DET | open |  |
| DET-P3-002 | P3 | [SEC] gitleaks not installed (secret scan skipped) | @owner | DET | open |  |
| DOC-P3-001 | P3 | Repository name vs lab working-directory drift is documented but still confusing | @owner | DOC | partially-fixed | documented; paths unchanged |
| DR-P3-001 | P3 | Backup/verify/restore runbook and tooling are strong; drills are manual/undated | @owner | DR | open | no scheduled verification |
| EVOL-P3-001 | P3 | Extensibility is documented (EXTENDING.md) with a plugin/adapter boundary | @owner | EVOL | open | documented, unversioned |
| FEAT-P3-001 | P3 | destroyKeys is audit-only server-side (no key destruction endpoint) | @owner | FEAT | verified-fixed | re-audit 2026-10-04: closed |
| FEAT-P3-002 | P3 | create-token no longer prints the plaintext token unless --stdout | @owner | FEAT | verified-fixed | re-audit 2026-10-04: closed |
| FILE-P3-001 | P3 | Root-side update verifier rejects symlink/traversal/setuid archive members | @owner | FILE | verified-fixed | hardened; re-audit 2026-10-04: closed |
| HYG-P3-001 | P3 | Hardcoded sensor endpoint list removed from the metrics collector | @owner | HYGIENE | verified-fixed | re-audit 2026-10-04: closed |
| INV-P3-001 | P3 | Generated models/schemas/dashboard JSON committed and can drift | @owner | INV | verified-fixed | re-audit 2026-10-04: closed |
| IR-P3-001 | P3 | Incident/tabletop scenarios exist but no dated exercise record in-repo | @owner | IR | open | no exercise evidence |
| MOB-P3-001 | P3 | Not applicable: no mobile app or PWA | @owner | MOB | open | not applicable |
| MT-P3-001 | P3 | No tenant model: isolation boundary is the device identity + site_id only | @owner | MT | open | not applicable to the current single-owner lab; future-readiness recorded |
| OBS-P3-001 | P3 | Stale pending_directives metric fixed | @owner | OBS | verified-fixed | re-audit 2026-10-04: closed |
| PERF-P3-001 | P3 | No performance/scale evidence for a large fleet in-repo | @owner | PERF | open | lab-scale only |
| PRIV-P3-001 | P3 | Host inventory (MAC/IP/hostnames) is minimised and retained under a documented policy | @owner | PRIV | partially-fixed | access fixed; retention policy-only |
| REL-P3-001 | P3 | Releases are documented per-image but there is no CHANGELOG or generated release notes in-repo | @owner | REL | open | no in-repo changelog |
| RLS-P3-001 | P3 | Not applicable: no Supabase/Postgres or row-level-security layer | @owner | RLS | open | not applicable |
| SBOM-P3-001 | P3 | No repository LICENSE file; SBOM is build-time/artefact-time, not CI-gated | @owner | SBOM | open | LICENSE still absent at ba4becb |
| SC-P3-001 | P3 | Dependabot now watches the pip toolchain as well as GitHub Actions | @owner | SC | verified-fixed | merged #35 @9dce2a5 |
| SEARCH-P3-001 | P3 | Not applicable: no search index or indexing pipeline in-repo | @owner | SEARCH | open | not applicable |
| SEC-P3-002 | P3 | Lab drill tooling disables SSH host-key and TLS verification | @owner | SEC | still-open | re-audit 2026-10-04: still-open |
| SECRET-P3-001 | P3 | Trust-root and per-sensor rotation runbooks now exist | @owner | SECRET | verified-fixed | merged #37 @5549903; re-audit 2026-10-04: closed |
| TEST-P3-001 | P3 | Coverage is now gated (fail under 85%) | @owner | TEST | verified-fixed | re-audit 2026-10-04: closed |
| TEST-P3-002 | P3 | Known-flaky time-relative test fixture addressed | @owner | TEST | verified-fixed | re-audit 2026-10-04: closed |
| USE-P3-001 | P3 | CLI-first workflow is documented; no measured operator task times | @owner | USE | open | documented; unmeasured |
| UX-P3-001 | P3 | Not applicable: the edge program has no browser UI to assess | @owner | UX | open | not applicable |
| WH-P3-001 | P3 | Vector ingest is at-least-once with no idempotency key or dedupe | @owner | WH | partially-fixed | endpoint documented; dedupe still absent |
