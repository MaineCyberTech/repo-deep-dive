# Patch plan

## OBS-P0-001 — Prometheus scrapes only 3 targets; nearly all `falcon_*` signals hinge on the node-exporter textfile collector

Scrape OpenSearch/ntfy/relay directly and/or alert on the collector freshness so signal loss is visible.

## API-P1-001 — Cross-repo pairing contract cannot be verified in this environment

Vendor the edge pin + verifier inputs so the pairing contract verifies from a clean clone.

## ARCH-P1-001 — Single-host concentration: host loss is total pipeline loss

Add a warm standby or a documented, tested RTO/RPO acceptance with owner sign-off.

## BP-P1-001 — Branch protection and required checks are plan-gated and unenforceable server-side

Upgrade to GitHub Pro/Team and apply the ready payload, or record per-merge validate attestation.

## CI-P1-001 — Branch protection and required checks are not enforced server-side

Upgrade the plan and apply the ready payload, or record a per-merge attestation.

## DATA-P1-001 — Wazuh and IRIS data have no retention (unbounded index growth)

Owner decision + apply ISM/ILM retention for Wazuh and IRIS indices, then record the policy id.

## FINAL-P1-001 — Operational resilience remains incomplete across the backup lifecycle

Close the offsite/dead-man residuals and add an end-to-end restore assertion to the gate.

## HYGIENE-P1-001 — Committed `review-package/` is a stale snapshot duplicate of the source tree

Stop committing the generated package or rebuild+rebind it and gate content drift.

## ADMIN-P2-001 — Admin/observability consoles are exposed through public routers without origin authentication

Put admin consoles behind Cloudflare Access or an auth middleware and remove anonymous routes.

## API-P2-001 — Ingest contract relies on a shared secret header, not request signing or idempotency keys

Add request signing / idempotency keys to the vector ingest contract.

## ARCH-P2-001 — Declared container hardening lags the running containers

Bring declared security_opt/read_only/cap_drop in compose to parity with live and gate it.

## ARCH-P2-002 — Wazuh and vendored MCT stacks run tag-only images outside pin/SBOM scope

Extend pins/images.lock + SBOM coverage to Wazuh/MCT or scope the waiver per ref.

## ARCH-P2-003 — Live ingest authentication is a shared secret header, not mTLS

Move edge→aggregator ingest to certificate/mTLS identity or add request signing + idempotency.

## CI-P2-001 — Auto-merge workflow holds `contents: write` with no environment protection

Scope permissions to minimum and add --match-head-commit to the merge command.

## FEAT-P2-001 — Vendored MCT services are present in Compose while the subtree policy calls the tree archive-only

Make the vendored tree non-deployable (separate profile) or drop the archive-only claim.

## HYGIENE-P2-001 — Large generated SBOM/vulnerability JSON committed (39 files, up to ~122 KB each)

Move generated SBOM/vuln JSON to release artifacts or compress and gate regeneration.

## INFRA-P2-001 — Generated/derived trees are not bound to HEAD by an automated drift gate

Add a generated-drift gate for review-package/sbom/closeout or record the deferral as an owner decision.

## INV-P2-001 — Repository is majority generated/derived content with no in-repo regeneration or drift check

Regenerate the derived trees and bind them to HEAD in CI; the review-package rebind is the open half.

## NOTIF-P2-001 — Public ntfy routers lack origin authentication; `ntfy-auth` middleware is not wired

Wire the ntfy auth middleware or gate the public route behind Cloudflare Access.

## SBOM-P2-001 — Release/SBOM artifacts are integrity-checked but unsigned; image/SBOM license gate not enforced

Sign sbom/SBOM_MANIFEST.sha256 (ed25519/GPG or GitHub attestations) and enforce a license allow/deny gate.

## SEARCH-P2-001 — Search/index retention is enforced only for falcon-eve; Wazuh/IRIS indices grow unbounded

Apply retention policies to Wazuh/IRIS indices and add a metrics check for unmanaged indices.

## SEC-P2-001 — Public-facing routers have no origin authentication; `ntfy-auth` is dead config

Wire the ntfy/Traefik auth middleware or document the origin-trust decision explicitly.

## SECRET-P2-001 — Inherited credential estate is still pending rotation and 28 vendored scripts source credential files wholesale

Execute the rotation order with name-only evidence; migrate vendored scripts to the single-key reader.

## ACM-P3-001 — No consolidated access-control matrix; authorization is per-service basic-auth / console accounts

Publish an access-control matrix mapping services→roles→auth mechanism and review it each patch window.

## CHAIN-P3-001 — Chained path: anonymous public router → admin console abuse, plus docker.sock in vendored compose

Break the chain at origin auth (Cloudflare Access) and remove docker.sock from the vendored stack.

## CTR-P3-001 — Vendored MCT compose mounts docker.sock and uses floating tags under a blanket waiver

Remove/justify docker.sock mounts, pin by digest, and scope the waiver per ref.

## DET-P3-001 — [GIT] No LICENSE file

Add a LICENSE or an explicit proprietary review-only notice consistent with the owner decision.

## DET-P3-002 — [SUPPLY] 58 container image(s) without a digest pin

Pin images by digest (image@sha256:...) for reproducible, tamper-evident deploys, or scope the waiver per ref.

## DET-P3-003 — [SUPPLY] hadolint not available on the check runner (Dockerfile lint skipped)

Install hadolint in the deterministic CI job so Dockerfile lint is not a coverage gap.

## DET-P3-004 — [DEP] trivy not available on the check runner (dependency vuln scan skipped)

Install trivy in the deterministic CI job so dependency/image scanning is enforced, not skipped.

## DR-P3-001 — Offsite/dead-man residuals remain owner-side; no scheduled restore assertion in CI

Schedule an end-to-end restore assertion and close the DO-side dead-man residual.

## INV-P3-001 — Legacy host-absolute evidence paths require manual rewrite to resolve in a clone

Finish the evidence-index path normalization so every recorded path resolves in a clean clone.

## REL-P3-001 — No root CHANGELOG/release-notes generator; release notes live only in mct/

Add a root CHANGELOG/release-notes generator fed from the gate/decision ledgers.

## WH-P3-001 — Webhook/relay delivery has no replay/idempotency evidence for Shuffle and ntfy paths

Add replay/idempotency tests (duplicate delivery, out-of-order) for the Shuffle and ntfy paths.

