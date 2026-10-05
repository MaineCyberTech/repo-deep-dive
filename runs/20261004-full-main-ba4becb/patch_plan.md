# Patch plan

## EXEC-P1-001 — Release-gate condition (terminal revocation) is closed

None.

## FINAL-P1-001 — Release blocker (non-terminal revocation) is closed

None.

## SEC-P1-001 — Re-enrollment no longer resets a REVOKED/RETIRED sensor

None.

## API-P2-001 — Cursor pagination contract now honoured (keyset pagination)

None.

## API-P2-002 — SensorSummary.queueDepth now returned

None.

## ARCH-P2-001 — Control plane still executes a mutable working tree (dirty-guarded, not pinned)

Deploy a pinned bundle (release artifact with SHA-256) and run from it; keep the dirty check as defense in depth.

## ARCH-P2-002 — Edge control plane is a co-tenant single point of failure on the shared lab host

Isolate the control plane on its own host/VM or add a warm standby with a documented failover; record as a production-readiness precondition.

## AUTH-P2-001 — Device mTLS private key is group-readable (0640), contradicting its documented 0600

Keep the identity private key 0600 and give Vector its own client certificate; widen only the certificate (0640), never the private key. Correct the docstring.

## BP-P2-001 — Branch protection / required checks cannot be enforced on the current GitHub plan

Upgrade to GitHub Pro/Team and apply the ready payload (BRANCH_PROTECTION.md:576-587); until then keep compensating controls and re-review at each plan/cost review.

## CHAIN-P2-001 — Chain: co-tenant read of the agent key -> control-plane signing seed compromise -> unattended fleet code swap

Break the chain at each link: keep the agent key 0600 with a distinct Vector identity; isolate the control plane host; disable auto-apply by default; set update_allowed_hosts. Each single fix degrades the chain.

## CI-P2-001 — CI toolchain is downloaded and hash-verified (pinning enforced)

None.

## CI-P2-002 — bake-image no longer interpolates secrets into script text

None.

## DATA-P2-001 — Idempotency table is now bounded and stores a digest, not full bodies

None.

## DATA-P2-002 — Foreign keys and retention indexes added for events/state/heartbeat history

None.

## DATA-P2-003 — Schema migration mechanism now exists (not only CREATE TABLE IF NOT EXISTS)

None.

## EXEC-P2-001 — Production readiness remains insufficient-evidence

Do not grant production readiness; close the P2 chain items and produce a production plan before any GO.

## FEAT-P2-001 — SensorSummary.queueDepth is now populated (was documented-only)

None.

## FILE-P2-001 — Update artifact host allowlist exists but is not configured in the shipped image

Set update_allowed_hosts in the shipped agent.json (control-plane host / object store) so the URL is scheme- and host-restricted by default.

## FINAL-P2-001 — Cross-cutting theme: automation artifacts are not continuously bound to their sources

Add a signed deployment attestation (commit + artefact digest) and verify it at deploy time.

## HYG-P2-001 — Summary documentation no longer hardcodes drifted test counts / Dependabot cadence

None.

## HYG-P2-002 — Committed derived artifacts are guarded against staleness

None.

## INFRA-P2-001 — Lab config and shipped image config deliberately diverge (bind/TLS/auto-apply)

Keep the startup guard; add a fail-closed requirement that allow_insecure_enrollment only runs with an explicit lab flag, and assert image configs in CI.

## INV-P2-001 — Committed raw evidence is large and only now budget-guarded

Keep the size gate in ci/validate.sh; rehearse the archive-and-sidecar flow before the cap trips.

## INV-P2-002 — Pack inventory tooling now emits routes/schema/entrypoints

None; keep the extractors covered by the pack self-test.

## NOTIF-P2-001 — No alert/notification delivery path from the edge program (email/push/pager)

Wire the edge alert rules to an Alertmanager/receiver (or document the central-stack receiver as the authoritative path).

## OBS-P2-001 — No alert delivery path (no Alertmanager/pager); rules are visible only in Prometheus/Grafana

Wire rules to an Alertmanager/receiver or document the central stack's delivery as authoritative.

## OBS-P2-002 — Inventory alert metrics depend on host-side SSH to each sensor (single point of failure)

Prefer push/gateway metrics (the agent already reports over mTLS) over host-side SSH scraping.

## RES-P2-001 — Single-host control plane has no warm standby or tested failover

Add a warm standby or document an RTO/RPO and rehearse a host-loss restore (see DR drilling).

## SC-P2-001 — CI installs Python dependencies with exact versions and hashes

None.

## SC-P2-002 — Secret scanning covers git history, not only the working tree

None.

## SC-P2-003 — CI downloads lint/scan binaries with embedded SHA-256 verification

None.

## SC-P2-004 — Credential-bearing image artifacts/releases rely solely on private-repo access

Keep the repo private and rotate baked credentials per release; move to artifact-level access control if the exposure window must shrink.

## SEC-P2-001 — HTTP transport hardening (rate limit, headers, slow-client guard) present

None.

## SEC-P2-002 — Inventory metrics collector no longer disables SSH host-key verification

None.

## SEC-P2-003 — Raw host inventory file no longer world-readable on sensors

None.

## SUPPLY-P2-001 — Shipped sensor image auto-applies signed updates with no per-update human gate

Default update_auto_apply to false for stable/production (keep true for lab/canary), or require an explicit operator release action; the policy note is accurate but the shipped default remains permissive.

## TEST-P2-001 — Test-count claims no longer hardcoded in docs

None.

## TEST-P2-002 — Regression test for re-enrolment of a REVOKED/RETIRED sensor added

None.

## ACM-P3-001 — Operator identity map and revocation are implemented; single-operator fallback still allowed

For production, require operator_identities (non-empty) and refuse the default fallback; document the matrix in the audit.

## ADMIN-P3-001 — Admin surface is the operator CLI + mTLS operator APIs; no web console

Keep operator client key 0600 and revoke operator identities on offboarding (root-key-compromise runbook covers CA rotation).

## AI-P3-001 — Repository text is treated as untrusted instruction input by the agent rules

Keep the untrusted-input rule; add a note to the audit prompts that evidence text is data only.

## AN-P3-001 — Not applicable: no third-party analytics or tracking SDKs

Re-open if any third-party analytics is embedded.

## API-P3-001 — Problem `instance` now reflects the request path

None.

## ARCH-P3-001 — Bare stdlib HTTP transport now has connection cap, timeout and rate limiting

None.

## BILL-P3-001 — Not applicable: no billing, payment, or reconciliation code

Re-open if a billing integration is added.

## CI-P3-001 — Branch-protection documentation matches implemented Dependabot-merge behavior

None.

## CTR-P3-001 — Not applicable: no container runtime in the repository

Re-open if the edge control plane is containerised.

## DATA-P3-001 — Queue age-expiry / purge_expired wiring

None.

## DET-P3-001 — [GIT] No LICENSE file

Add a license.

## DET-P3-002 — [SEC] gitleaks not installed (secret scan skipped)

Install gitleaks in CI to enable the secret scan.

## DOC-P3-001 — Repository name vs lab working-directory drift is documented but still confusing

Rename the deployment directory to falcon-edge at the next host rebuild, or add a symlink + note in ENVIRONMENTS.md.

## DR-P3-001 — Backup/verify/restore runbook and tooling are strong; drills are manual/undated

Add a periodic (e.g. monthly) automated verify of the newest archive (dry-run) and record evidence.

## EVOL-P3-001 — Extensibility is documented (EXTENDING.md) with a plugin/adapter boundary

Add a versioned extension contract if third-party adapters are expected.

## FEAT-P3-001 — destroyKeys is audit-only server-side (no key destruction endpoint)

None.

## FEAT-P3-002 — create-token no longer prints the plaintext token unless --stdout

None.

## FILE-P3-001 — Root-side update verifier rejects symlink/traversal/setuid archive members

None beyond FILE-P2-001.

## HYG-P3-001 — Hardcoded sensor endpoint list removed from the metrics collector

None.

## INV-P3-001 — Generated models/schemas/dashboard JSON committed and can drift

Keep the generated-artifact checks in the advisory validate workflow and re-run before release.

## IR-P3-001 — Incident/tabletop scenarios exist but no dated exercise record in-repo

Run a tabletop against root-key-compromise + lost-sensor and capture the result under evidence/.

## MOB-P3-001 — Not applicable: no mobile app or PWA

Re-open if an operator mobile client is added.

## MT-P3-001 — No tenant model: isolation boundary is the device identity + site_id only

Record as not-applicable/future-readiness; if tenants are introduced, require a tenant_id on every table and a per-tenant authz check.

## OBS-P3-001 — Stale pending_directives metric fixed

None.

## PERF-P3-001 — No performance/scale evidence for a large fleet in-repo

Record a bounded load test (e.g. N synthetic sensors) before claiming fleet scale.

## PRIV-P3-001 — Host inventory (MAC/IP/hostnames) is minimised and retained under a documented policy

Keep the owner decision current; add a retention enforcement check if the inventory grows beyond the lab.

## REL-P3-001 — Releases are documented per-image but there is no CHANGELOG or generated release notes in-repo

Add a CHANGELOG.md (or generate release notes from tags) and reference it from README.

## RLS-P3-001 — Not applicable: no Supabase/Postgres or row-level-security layer

Re-open only if a hosted Postgres/Supabase backend is introduced.

## SBOM-P3-001 — No repository LICENSE file; SBOM is build-time/artefact-time, not CI-gated

Add an explicit LICENSE (and reference it from README.md); add a CI check that a release has an attached SBOM of non-zero component count.

## SC-P3-001 — Dependabot now watches the pip toolchain as well as GitHub Actions

None.

## SEARCH-P3-001 — Not applicable: no search index or indexing pipeline in-repo

Re-open if an in-repo index is added.

## SEC-P3-002 — Lab drill tooling disables SSH host-key and TLS verification

Pin lab host keys via managed known_hosts and verify TLS with the lab CA, mirroring inventory_metrics.py.

## SECRET-P3-001 — Trust-root and per-sensor rotation runbooks now exist

Exercise the runbook in a tabletop (see 33) and record evidence; keep backups of the signing seed in escrow.

## TEST-P3-001 — Coverage is now gated (fail under 85%)

None.

## TEST-P3-002 — Known-flaky time-relative test fixture addressed

None.

## USE-P3-001 — CLI-first workflow is documented; no measured operator task times

Keep the derived-artifact warning prominent; optionally capture operator task timings.

## UX-P3-001 — Not applicable: the edge program has no browser UI to assess

Re-open if an operator web UI is added.

## WH-P3-001 — Vector ingest is at-least-once with no idempotency key or dedupe

Add a content hash + dedupe window, or document at-least-once explicitly in the operator runbook.

