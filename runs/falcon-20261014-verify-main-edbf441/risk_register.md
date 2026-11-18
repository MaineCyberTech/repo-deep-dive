# Risk register

## Finding index

| ID | Severity | Title |
|---|---|---|
| ARCH-P1-001 | P1 | Single-host concentration: host loss is total pipeline loss |
| DATA-P1-001 | P1 | Wazuh/IRIS retention coverage is incomplete and the repository statement contradicts the live estate (alerts class not ISM-managed) |
| DR-P1-002 | P1 | Offsite upload state truncated to empty by the 2026-10-10 run; the 2026-10-11 run is re-uploading the full 68.3 GiB repository and the offsite success stamp is 33.6 h stale (24 h RPO target breached) |
| EVOL-P1-001 | P1 | Cross-repo shared tooling has drifted and still has no pin/hash enforcement |
| EVOL-P1-002 | P1 | MCT vendoring policy is proposed but not enforced; the pin gate remains blind to mct/compose |
| PERF-P1-002 | P1 | Root LV sits below the guard's 20 GiB threshold: 48 failed reclaims in ~19 h, alerting every 15 min, and no effective reclaim path for the root-resident snapshot repo |
| PRIV-P1-001 | P1 | Wazuh indexer and IRIS case data still have no retention or deletion window (owner-gated) |
| RES-P1-002 | P1 | Root LV below the 20 GiB disk-guard threshold; guard failing every 15 min while the snapshot repository grows ~4.3-5.5 GiB/night |
| RES-P2-002 | P1 | Wazuh VPN proxy socket boot race is not fixed: systemd still deletes the socket jobs on boot (listeners dead 45 min after the Oct 11 reboot) |
| WH-P1-001 | P1 | OpenSearch sink drops failed batches with no dead-letter/replay path (detection now closed and live-verified) |
| ACM-P2-001 | P2 | Live client-VPN enrollment credential is a single shared token with no expiry; per-device lifecycle implemented but unused |
| ACM-P2-003 | P2 | Deployed enrollment service does not enforce per-device token expiry; issuance tool and deployed enforcement disagree (no deployed-artifact binding) |
| ADMIN-P2-001 | P2 | Admin/observability consoles are exposed through public routers without origin authentication |
| ADMIN-P2-002 | P2 | The Access-posture gate accepts origin reachability; no automated check verifies Cloudflare Access enforcement anymore |
| ADMIN-P2-003 | P2 | No centralized actor-level audit trail for Grafana/ntfy/IRIS console admin actions |
| API-P2-001 | P2 | Ingest contract relies on a shared secret header, not request signing or idempotency keys |
| ARCH-P2-002 | P2 | Vendored MCT tree remains tag-only under a blanket pin waiver; live stacks are now tag@digest and lock-covered |
| ARCH-P2-003 | P2 | Live ingest authentication is an HTTP basic-auth shared credential, not mTLS or request signing |
| BP-P2-001 | P2 | CODEOWNERS is invalid: every entry uses an unresolvable org handle |
| CHAIN-P2-001 | P2 | The only automated Access-posture check no longer verifies Access (external-smoke accepts any 302 from the lab vantage) |
| CI-P2-001 | P2 | Auto-merge workflow holds `contents: write` with no environment protection and no head-commit pin |
| CI-P2-002 | P2 | external-smoke no longer asserts Cloudflare Access posture and passes on an owner-IP bypass |
| CI-P2-003 | P2 | Repository Actions settings default to permissive (write token, PR approvals, any action, no SHA-pin requirement) |
| CTR-P2-001 | P2 | Adopted MCT/Wazuh stacks run without baseline container hardening or healthchecks |
| DATA-P2-002 | P2 | Root LV is below the disk guard's 20 GiB threshold: the guard fails every 15 minutes and cannot reclaim back above it (69 GiB snapshot repo on root) |
| DATA-P2-003 | P2 | Edge control-plane spool keeps purging ~134 MiB per 10-14 h; nothing consumes it and the purge alert cannot fire at that rate |
| DET-P2-001 | P2 | [PORT] CRLF committed for 1 file(s) (index has CRLF) |
| DOC-P2-002 | P2 | Status artifacts still lag the live state: catalogue/README/CURRENT_STATE at 85 vs 86 provisioned/live, firing proofs at 75/77, evolution-guide block at 2026-10-01 |
| DR-P2-002 | P2 | Bulk telemetry snapshot repositories are still stored offsite unencrypted; only config/secrets archives are encrypted |
| DR-P2-003 | P2 | IRIS case database is not backed up; the coverage matrix marks it OPEN with unbounded RPO |
| EVOL-P2-001 | P2 | The OpenSearch identity apply is not merge-safe (R-28 hazard documented; owner decision pending) |
| FEAT-P2-001 | P2 | Vendored MCT services are present in Compose while the subtree policy calls the tree archive-only |
| HYGIENE-P2-001 | P2 | Large generated SBOM/vulnerability JSON remains committed (39 files, 29.6 MB, up to 3.0 MB each) |
| HYGIENE-P2-002 | P2 | Canonical release-gate page carries a superseded audit opinion; the newest full run's P0 is not referenced |
| HYGIENE-P2-003 | P2 | The publication flow force-tracks review-package/MANIFEST.sha256 while .gitignore, AGENTS.md, REPOSITORY.md and build_review_package.sh say the review package must not be committed; the file is load-bearing for the declared-commit gates |
| INFRA-P2-005 | P2 | Disk guard failing: root LV below its 20 GiB threshold after the nightly snapshot; reclaims exhausted |
| INFRA-P2-006 | P2 | Nightly offsite backup in a multi-hour catch-up; offsite RPO ~33 h at capture and not yet verifiable |
| INV-P2-001 | P2 | Repository is majority generated/derived content; largest trees bound, audit records and mct/ remain unbound |
| IR-P2-001 | P2 | No facilitated tabletop exercise has been run; Scenario 5 (total monitoring/alerting loss) remains unexercised |
| IR-P2-002 | P2 | Escalation contacts remain placeholders; the incident escalation path is unverified |
| IR-P2-003 | P2 | Recurring incidents still lack post-incident review; the Oct 10-11 events (offsite state damage, kernel reboot/socket outage, root-LV guard loop) have no record |
| IR-P2-004 | P2 | Previous-fix verification failed for the Wazuh proxy boot ordering: the 2026-10-01 'verified CLOSED' claim is contradicted by the 2026-10-11 boot |
| NOTIF-P2-002 | P2 | Notification noise remains high; the accurate disk-guard root alert now dominates and sub-repeat-interval flapping persists |
| OBS-P2-001 | P2 | ALERT_CATALOGUE.yaml, README and CURRENT_STATE lag live Grafana by one rule while claiming the catalogue cannot drift |
| OBS-P2-002 | P2 | Alert noise remains high and is now dominated by the disk-guard alert repeated every 15 minutes; planned reboots produce artifact alerts |
| OBS-P2-003 | P2 | Pipeline counters rule fires on benign edge_ingest HTTP method rejections and the lazily-registered Vector counters vanish, producing a counter reset inside the firing window |
| OBS-P2-004 | P2 | No alert for a stuck backup run or for failed systemd units; detection depends on 36 h staleness rules |
| ORCH-P2-001 | P2 | Committed 2026-10-05 full-run record contradicts the canonical gate and omits the domain evidence |
| ORCH-P2-002 | P2 | full_domain.py hardcodes profile=base and records area codes as lenses; falcon-lab coverage is not representable |
| PERF-P2-001 | P2 | Persistent host memory/swap pressure with uncapped Wazuh/IRIS stacks; measured capacity envelope and memory budget remain stale |
| PERF-P2-002 | P2 | Data-LV warning/reclaim thresholds remain GiB constants that sit above OpenSearch's default watermarks on a 224 GiB volume |
| PERF-P2-006 | P2 | 21.7 GiB stale migration bundle (plus 6.5 GiB Wazuh backup dir) sits on the root LV outside the guard's reclaim policy with no expiry |
| PERF-P2-007 | P2 | Root-disk projection rule is blind to the current below-threshold state; no alert on the guard's own root threshold or reclaim failure |
| PRIV-P2-001 | P2 | The vendored MCT client/vendor layer still has no privacy-classification boundary in this repository |
| PRIV-P2-003 | P2 | The published production verdict still binds a superseded package and carries a contradictory readiness line |
| REL-P2-001 | P2 | Deployment state is not bound to any release: no tags/VERSION and no deploy manifest; the live tree is now clean at main HEAD |
| REL-P2-002 | P2 | Published PACKAGE_MANIFEST.sha256 is stale: it disagrees with the declared review-package manifest on 8 files and no gate compares them |
| RES-P2-001 | P2 | Host memory/swap pressure improved but remains: ~33% available, ~4.0 GiB swap used; capacity envelope stale |
| SBOM-P2-001 | P2 | Release/SBOM artifacts are integrity-checked but unsigned; image/SBOM license gate not enforced |
| SC-P2-002 | P2 | Inherited credential estate is still pending rotation and 20 vendored scripts source credential files wholesale |
| SEARCH-P2-001 | P2 | Retention gaps remain on the Wazuh indexer alerts class and IRIS; RETENTION_MATRIX.md is stale |
| SEARCH-P2-002 | P2 | OpenSearch snapshot repository still on the root LV; root free is below the guard threshold and the guard now fails every 15 minutes |
| SEC-P2-001 | P2 | Public-facing routers have no origin authentication; ntfy-auth is dead config |
| SEC-P2-002 | P2 | Public rate limits key on client-supplied X-Forwarded-For; no per-account limits on auth endpoints |
| SEC-P2-004 | P2 | Deployed enrollment service is a stale build: per-device token expiry is not enforced and the documented issuance flow is rejected |
| SECRET-P2-001 | P2 | Inherited credential estate still 20/20 pending rotation; vendored scripts source credential stores wholesale |
| SECRET-P2-002 | P2 | Live owner credential file has undocumented keys and the validator is not wired into any gate |
| TEST-P2-001 | P2 | external-smoke no longer verifies Cloudflare Access from an external vantage; it accepts the owner-IP bypass |
| ACM-P3-001 | P3 | No consolidated access-control matrix; authorization remains per-service and distributed across four documents |
| ACM-P3-002 | P3 | Documented Cloudflare Access policy state does not match live behavior: the falcon app has no owner-IP bypass (and two dead apps remain) |
| AI-P3-001 | P3 | Agent/audit-run pointers are stale: the lifecycle runbook still calls the closed 2026-09-30 run 'the current run' and AGENTS.md/README point at it as the full-domain reference |
| AI-P3-002 | P3 | No AI-provenance policy and no per-tool agent instruction coverage |
| API-P3-002 | P3 | Public-access deploy script still names the retired dash.falcon/ntfy.falcon hostnames in its operator guidance |
| ARCH-P3-001 | P3 | Port matrix describes ingest auth as a shared secret header while the implementation is HTTP basic auth |
| ARCH-P3-002 | P3 | Container-level memory and policy-restart alerting for central services is still absent |
| BP-P3-001 | P3 | Dependabot auto-merge compensating control has never been exercised |
| CHAIN-P3-001 | P3 | Anonymous origin -> admin console exposure, plus latent docker.sock mounts in the vendored Shuffle compose |
| CHAIN-P3-002 | P3 | No automated live-vs-repo drift check for the exposure edges; the applied wg0 narrowing can regress silently |
| CI-P3-001 | P3 | Hosted-runner fallback is dead; scheduled/queued workflow failures stay silent |
| CI-P3-002 | P3 | Three probe workflows remain registered/active with no file on any branch |
| CI-P3-003 | P3 | CI/CD incident playbook section 8 is stale on tool pinning and captured-run evidence |
| CI-P3-004 | P3 | Review package is documented as a CI/release artifact but no CI job builds or publishes it |
| CTR-P3-001 | P3 | Vendored MCT compose still mounts docker.sock and uses unpinned images under a blanket waiver |
| CTR-P3-002 | P3 | Local OpenSearch image installs the repository-s3 plugin as root with no artifact pin; rebuild mismatch is warn-only |
| DATA-P3-004 | P3 | Nightly backup leaves an unencrypted config archive beside the encrypted one and never removes it |
| DATA-P3-005 | P3 | Retention documentation drift: snapshot cadence/keep count disagree and the Wazuh indexer backup job is not in the matrix |
| DET-P3-002 | P3 | [SEC] gitleaks not installed (secret scan skipped) |
| DET-P3-003 | P3 | [SUPPLY] 29 container image(s) without a digest pin |
| DET-P3-004 | P3 | [SUPPLY] hadolint not installed (Dockerfile lint skipped) |
| DOC-P2-001 | P3 | Pack-fidelity verification is still not wired into the delivery build; the notes file carries no verdict |
| DOC-P3-001 | P3 | Imprecise version shorthand in the README vs the pinned versions |
| DR-P3-001 | P3 | Scheduled end-to-end restore assertion still absent; the merged assertion exists in the live tree but is not scheduled |
| EVOL-P3-002 | P3 | No feature-flag mechanism; the documented additive-deploy substitute is pending owner acceptance |
| FEAT-P3-001 | P3 | Alert-rule count claims and the catalogue lag the provisioned set by one rule after the 2026-10-11 proxy-listener addition |
| HYGIENE-P3-001 | P3 | No root LICENSE/NOTICE file; README ownership section grants no terms |
| INV-P3-001 | P3 | Legacy host-absolute evidence paths require the resolver to resolve in a clone |
| INV-P3-002 | P3 | Delivery pack fidelity artifact ships two unresolved 'unexpected; investigate' entries |
| INV-P3-003 | P3 | 'A stale digest fails' is enforced by publication equality, not by the digest-binding check whose docstring claims it |
| INV-P3-004 | P3 | Published PACKAGE_MANIFEST.sha256 is two publication cycles stale and disagrees with the shipped review-package manifest; no check binds it |
| INV-P3-005 | P3 | HYG-P1-001 doctrine ('review-package is generated, gitignored, must not be committed') contradicts the tracked review-package/MANIFEST.sha256 |
| IR-P2-005 | P3 | The 2026-10-11 kernel-upgrade reboot was not recorded as a maintenance window and had no post-reboot verification |
| NOTIF-P2-001 | P3 | ntfy-auth Traefik middleware is still dead config; ntfy-native deny-all remains the only access control |
| NOTIF-P3-003 | P3 | Retired public lab-ntfy hostname still referenced in ledgers and the 97 deploy fallback text |
| ORCH-P3-001 | P3 | Run id does not start with the timestamp required by the consumer repo's lifecycle check |
| ORCH-P3-002 | P3 | Domain report and findings array disagree on a finding status inside the same 20261009 run artifact |
| PERF-P3-001 | P3 | Measured performance envelope and capacity model remain stale; the cost register still has no unit costs and no performance budgets exist |
| PERF-P3-002 | P3 | Per-minute whole-cluster monitoring queries still run against the single-node OpenSearch cluster with no exporter runtime budget |
| PERF-P3-008 | P3 | CI has no dependency or tool caching: every validate run re-downloads pinned tools and reinstalls hash-pinned Python deps |
| PERF-P3-009 | P3 | Edge ingest-spool purge counter advances ~268 MB/day, its data-loss meaning is unverified, and no live consumer of the spool is configured |
| PRIV-P3-001 | P3 | Owner/legal privacy inputs and the 'synthetic-only' wording remain outstanding |
| REL-P3-001 | P3 | No root CHANGELOG/release-notes generator; the 2026-10-04..11 window is undocumented |
| REL-P3-002 | P3 | Releases are not versioned: no tags, no VERSION file; binding artifacts overwrite in place |
| REL-P3-003 | P3 | The delivered package embeds a closeout bound to the previous publication cycle (b09a50f) while the digest declares 3c11752; the equality gate reads the working tree only |
| RES-P3-001 | P3 | Failure-injection coverage still omits the failure modes that actually occurred (aggregator OOM, host memory, boot-order/socket, root-LV exhaustion) |
| RES-P3-002 | P3 | No post-reboot verification was run or recorded after the 2026-10-11 kernel-upgrade reboot; post-reboot degradations were visible only through alerts |
| SBOM-P3-001 | P3 | Delivered review package excludes the SBOM set entirely; only the summary CSV ships |
| SBOM-P3-002 | P3 | SBOM enforcement doc contradicts the current CI gate (says --require-vuln is off) |
| SC-P3-001 | P3 | Published PACKAGE_MANIFEST.sha256 is stale vs the declared package manifest; no CI check compares them |
| SC-P3-002 | P3 | Dependabot security updates (automated fix PRs) remain disabled after alerts were enabled |
| SEARCH-P3-001 | P3 | Legacy falcon-eve indices keep divergent mappings; consumer queries silently under-return |
| SEC-P3-004 | P3 | wg0 tunnel has no peer-class separation; every peer (including client endpoints) can reach the edge control plane and Wazuh proxies |
| SEC-P3-005 | P3 | Console session cookies are not marked Secure (central OSD explicit cookie.secure: false; Grafana/Wazuh default) |
| SECRET-P3-001 | P3 | Rotation register/live-store paths for IRIS and the MCT stack are stale after consolidation |
| SECRET-P3-002 | P3 | Break-glass custody is procedural only (OD-04 pending); no custodian, sealed credential, or rehearsal |
| TEST-P3-001 | P3 | CI evidence-integrity check verifies zero captures; all meta files reference off-repo artifact paths |
| TEST-P3-002 | P3 | The test-requires skip marker is only honored in the first 15 lines; validate_gate_test.sh's marker is dead |
| WH-P3-001 | P3 | No replay/idempotency protection or tests on the notification path (ntfy); Shuffle path retired |
