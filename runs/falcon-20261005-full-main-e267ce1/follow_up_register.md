# Follow-up register

Run: `falcon-20261005-full-main-e267ce1` · Target: `falcon` @ `e267ce1` · Profile: base

Register mirrored 1:1 with `risk_register.md` so `tools/check_run.sh` passes.

| Finding | Severity | Title | Owner | Target | Status | Note |
|---|---|---|---|---|---|---|
| OBS-P0-001 | P0 | Prometheus scrapes only 3 targets; nearly all `falcon_*` signals hinge on the node-exporter textfile collector | @owner | OBS | partially-fixed |  |
| API-P1-001 | P1 | Cross-repo pairing contract cannot be verified in this environment | @owner | API | partially-fixed |  |
| ARCH-P1-001 | P1 | Single-host concentration: host loss is total pipeline loss | @owner | ARCH | still-open | owner-gated: propose a documented/tested RTO/RPO acceptance (RPO 24h nightly offsite; RTO 24h cold restore) tied to the PR #48 restore assertion instead of a warm standby. Residual: host loss = total pipeline loss until a cold restore; needs owner sign-off. See OWNER_GATED_PROPOSALS.md |
| BP-P1-001 | P1 | Branch protection and required checks are plan-gated and unenforceable server-side | @owner | BP | owner-accepted |  |
| CI-P1-001 | P1 | Branch protection and required checks are not enforced server-side | @owner | CI | owner-accepted |  |
| DATA-P1-001 | P1 | Wazuh and IRIS data have no retention (unbounded index growth) | @owner | DATA | still-open | owner-gated: propose ISM/ILM retention (Wazuh/IRIS hot 90d, delete 180d) with recorded policy ids; destructive, needs owner-approved windows. No infra change made. See OWNER_GATED_PROPOSALS.md |
| FINAL-P1-001 | P1 | Operational resilience remains incomplete across the backup lifecycle | @owner | FINAL | partially-fixed |  |
| HYGIENE-P1-001 | P1 | Committed `review-package/` is a stale snapshot duplicate of the source tree | @owner | HYGIENE | verified-fixed |  |
| ADMIN-P2-001 | P2 | Admin/observability consoles are exposed through public routers without origin authentication | @owner | ADMIN | still-open |  |
| API-P2-001 | P2 | Ingest contract relies on a shared secret header, not request signing or idempotency keys | @owner | API | partially-fixed |  |
| ARCH-P2-001 | P2 | Declared container hardening lags the running containers | @owner | ARCH | partially-fixed |  |
| ARCH-P2-002 | P2 | Wazuh and vendored MCT stacks run tag-only images outside pin/SBOM scope | @owner | ARCH | partially-fixed |  |
| ARCH-P2-003 | P2 | Live ingest authentication is a shared secret header, not mTLS | @owner | ARCH | partially-fixed |  |
| CI-P2-001 | P2 | Auto-merge workflow holds `contents: write` with no environment protection | @owner | CI | still-open |  |
| FEAT-P2-001 | P2 | Vendored MCT services are present in Compose while the subtree policy calls the tree archive-only | @owner | FEAT | partially-fixed |  |
| HYGIENE-P2-001 | P2 | Large generated SBOM/vulnerability JSON committed (39 files, up to ~122 KB each) | @owner | HYGIENE | partially-fixed |  |
| INFRA-P2-001 | P2 | Generated/derived trees are not bound to HEAD by an automated drift gate | @owner | INFRA | open |  |
| INV-P2-001 | P2 | Repository is majority generated/derived content with no in-repo regeneration or drift check | @owner | INV | partially-fixed |  |
| NOTIF-P2-001 | P2 | Public ntfy routers lack origin authentication; `ntfy-auth` middleware is not wired | @owner | NOTIF | still-open |  |
| SBOM-P2-001 | P2 | Release/SBOM artifacts are integrity-checked but unsigned; image/SBOM license gate not enforced | @owner | SBOM | open |  |
| SEARCH-P2-001 | P2 | Search/index retention is enforced only for falcon-eve; Wazuh/IRIS indices grow unbounded | @owner | SEARCH | still-open |  |
| SEC-P2-001 | P2 | Public-facing routers have no origin authentication; `ntfy-auth` is dead config | @owner | SEC | still-open |  |
| SECRET-P2-001 | P2 | Inherited credential estate is still pending rotation and 28 vendored scripts source credential files wholesale | @owner | SECRET | still-open |  |
| ACM-P3-001 | P3 | No consolidated access-control matrix; authorization is per-service basic-auth / console accounts | @owner | ACM | open |  |
| CHAIN-P3-001 | P3 | Chained path: anonymous public router → admin console abuse, plus docker.sock in vendored compose | @owner | CHAIN | open |  |
| CTR-P3-001 | P3 | Vendored MCT compose mounts docker.sock and uses floating tags under a blanket waiver | @owner | CTR | still-open |  |
| DET-P3-001 | P3 | [GIT] No LICENSE file | @owner | DET | open |  |
| DET-P3-002 | P3 | [SUPPLY] 58 container image(s) without a digest pin | @owner | DET | open |  |
| DET-P3-003 | P3 | [SUPPLY] hadolint not available on the check runner (Dockerfile lint skipped) | @owner | DET | open |  |
| DET-P3-004 | P3 | [DEP] trivy not available on the check runner (dependency vuln scan skipped) | @owner | DET | open |  |
| DR-P3-001 | P3 | Offsite/dead-man residuals remain owner-side; no scheduled restore assertion in CI | @owner | DR | still-open |  |
| INV-P3-001 | P3 | Legacy host-absolute evidence paths require manual rewrite to resolve in a clone | @owner | INV | partially-fixed |  |
| REL-P3-001 | P3 | No root CHANGELOG/release-notes generator; release notes live only in mct/ | @owner | REL | open |  |
| WH-P3-001 | P3 | Webhook/relay delivery has no replay/idempotency evidence for Shuffle and ntfy paths | @owner | WH | open |  |
