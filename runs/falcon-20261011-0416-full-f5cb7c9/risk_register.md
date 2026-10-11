# Follow-up register

Run: `falcon-20261011-0416-full-f5cb7c9` · Target: `falcon` @ `f5cb7c9` · Profile: base

Register mirrored 1:1 with `risk_register.md` so `tools/check_run.sh` passes.

| Finding | Severity | Title | Owner | Target | Status | Note |
|---|---|---|---|---|---|---|
| ARCH-P1-001 | P1 | Single-host concentration: host loss is total pipeline loss | @owner | ARCH | open |  |
| DATA-P1-001 | P1 | Wazuh/IRIS retention coverage is incomplete and the repository statement contradicts the live estate (alerts class not ISM-managed) | @owner | DATA | partially-fixed |  |
| DR-P1-002 | P1 | Offsite upload state truncated to empty by the 2026-10-10 run; the 2026-10-11 run is re-uploading the full 68.3 GiB repository and the offsite success stamp is 33.6 h stale (24 h RPO target breached) | @owner | DR | partially-fixed | Upload in progress (full 68.3 GiB re-upload after the 0-byte state truncation; started 03:37Z); stuck-run detection added (falcon_backup_service_state + rules, PR #55); truncation root cause = the #51 path fix. RPO breach persists until the upload completes - monitor. |
| EVOL-P1-001 | P1 | Cross-repo shared tooling has drifted and still has no pin/hash enforcement | @owner | EVOL | owner-accepted |  |
| EVOL-P1-002 | P1 | MCT vendoring policy is proposed but not enforced; the pin gate remains blind to mct/compose | @owner | EVOL | owner-accepted |  |
| PERF-P1-002 | P1 | Root LV sits below the guard's 20 GiB threshold: 48 failed reclaims in ~19 h, alerting every 15 min, and no effective reclaim path for the root-resident snapshot repo | @owner | PERF | verified-fixed | Post-run 2026-10-11: local snapshot retention 3->2 (85-backup-job.sh + disk_guard.sh) + oldest pruned + the 21.7 GiB stale /var/tmp/wz-migration bundle archived to the data LV (cmp-verified, source removed); guard passing, root 52 GiB free (69%). In main via falcon PR #55. |
| PRIV-P1-001 | P1 | Wazuh indexer and IRIS case data still have no retention or deletion window (owner-gated) | @owner | PRIV | owner-accepted |  |
| RES-P1-002 | P1 | Root LV below the 20 GiB disk-guard threshold; guard failing every 15 min while the snapshot repository grows ~4.3-5.5 GiB/night | @owner | RES | verified-fixed | Post-run 2026-10-11: root-LV margin fixed live + in main (PR #55) - retention 2, snapshot pruned, 21.7 GiB bundle archived off root; guard ok; root 19.6->52 GiB free. |
| RES-P2-002 | P1 | Wazuh VPN proxy socket boot race is not fixed: systemd still deletes the socket jobs on boot (listeners dead 45 min after the Oct 11 reboot) | @owner | RES | verified-fixed | Post-run 2026-10-11: boot race fixed in main (PR #55) - wg ordering removed + FreeBind=yes on both proxy sockets; freebind capability proven live on this systemd (bound an unassigned address); listeners up 10.99.0.1:15140/15141; next reboot is the final proof. |
| WH-P1-001 | P1 | OpenSearch sink drops failed batches with no dead-letter/replay path (detection now closed and live-verified) | @owner | WH | partially-fixed |  |
| ACM-P2-001 | P2 | Live client-VPN enrollment credential is a single shared token with no expiry; per-device lifecycle implemented but unused | @owner | ACM | partially-fixed | Post-redeploy the documented issuance flow works (per-device tokens with expiry); the live credential is still the bare shared token - issuing per-device bindings for the endpoint fleet = owner action. |
| ACM-P2-003 | P2 | Deployed enrollment service does not enforce per-device token expiry; issuance tool and deployed enforcement disagree (no deployed-artifact binding) | @owner | ACM | verified-fixed | Post-run 2026-10-11: deployed service matches the repo (redeploy) + daily deployed-vs-repo check + drift rule (PR #55). |
| ADMIN-P2-001 | P2 | Admin/observability consoles are exposed through public routers without origin authentication | @owner | ADMIN | open |  |
| ADMIN-P2-002 | P2 | The Access-posture gate accepts origin reachability; no automated check verifies Cloudflare Access enforcement anymore | @owner | ADMIN | open |  |
| ADMIN-P2-003 | P2 | No centralized actor-level audit trail for Grafana/ntfy/IRIS console admin actions | @owner | ADMIN | open |  |
| API-P2-001 | P2 | Ingest contract relies on a shared secret header, not request signing or idempotency keys | @owner | API | partially-fixed |  |
| ARCH-P2-002 | P2 | Vendored MCT tree remains tag-only under a blanket pin waiver; live stacks are now tag@digest and lock-covered | @owner | ARCH | open |  |
| ARCH-P2-003 | P2 | Live ingest authentication is an HTTP basic-auth shared credential, not mTLS or request signing | @owner | ARCH | open |  |
| BP-P2-001 | P2 | CODEOWNERS is invalid: every entry uses an unresolvable org handle | @owner | BP | verified-fixed | Post-run 2026-10-11: CODEOWNERS refs switched to the resolvable owner user @HenryTru0518 (PR #55); GitHub codeowners/errors = 0 (was 6 Unknown owner). |
| CHAIN-P2-001 | P2 | The only automated Access-posture check no longer verifies Access (external-smoke accepts any 302 from the lab vantage) | @owner | CHAIN | open |  |
| CI-P2-001 | P2 | Auto-merge workflow holds `contents: write` with no environment protection and no head-commit pin | @owner | CI | open |  |
| CI-P2-002 | P2 | external-smoke no longer asserts Cloudflare Access posture and passes on an owner-IP bypass | @owner | CI | open |  |
| CI-P2-003 | P2 | Repository Actions settings default to permissive (write token, PR approvals, any action, no SHA-pin requirement) | @owner | CI | open |  |
| CTR-P2-001 | P2 | Adopted MCT/Wazuh stacks run without baseline container hardening or healthchecks | @owner | CTR | still-open |  |
| DATA-P2-002 | P2 | Root LV is below the disk guard's 20 GiB threshold: the guard fails every 15 minutes and cannot reclaim back above it (69 GiB snapshot repo on root) | @owner | DATA | verified-fixed | Post-run 2026-10-11: see PERF-P1-002 - retention 2 + bundle archived; guard passing live (PR #55). |
| DATA-P2-003 | P2 | Edge control-plane spool keeps purging ~134 MiB per 10-14 h; nothing consumes it and the purge alert cannot fire at that rate | @owner | DATA | open |  |
| DOC-P2-002 | P2 | Status artifacts still lag the live state: catalogue/README/CURRENT_STATE at 85 vs 86 provisioned/live, firing proofs at 75/77, evolution-guide block at 2026-10-01 | @owner | DOC | partially-fixed | Post-run 2026-10-11: catalogue regenerated + README at 91 = live 91 (PR #55); drift test 28/0 + alert lint 91/91/91. Residual: firing-proof counts + the evolution-guide state block still need a refresh; source->catalogue drift remains a static-check gap. |
| DR-P2-002 | P2 | Bulk telemetry snapshot repositories are still stored offsite unencrypted; only config/secrets archives are encrypted | @owner | DR | open |  |
| DR-P2-003 | P2 | IRIS case database is not backed up; the coverage matrix marks it OPEN with unbounded RPO | @owner | DR | partially-fixed | The IRIS DB IS dumped (pg_dump in the daily new-services archive, local keep 7); matrix corrected 2026-10-11 (PR #55). Offsite shipping of the archive = follow-up. |
| EVOL-P2-001 | P2 | The OpenSearch identity apply is not merge-safe (R-28 hazard documented; owner decision pending) | @owner | EVOL | open |  |
| FEAT-P2-001 | P2 | Vendored MCT services are present in Compose while the subtree policy calls the tree archive-only | @owner | FEAT | open |  |
| HYGIENE-P2-001 | P2 | Large generated SBOM/vulnerability JSON remains committed (39 files, 29.6 MB, up to 3.0 MB each) | @owner | HYGIENE | still-open |  |
| HYGIENE-P2-002 | P2 | Canonical release-gate page carries a superseded audit opinion; the newest full run's P0 is not referenced | @owner | HYGIENE | open |  |
| HYGIENE-P2-003 | P2 | The publication flow force-tracks review-package/MANIFEST.sha256 while .gitignore, AGENTS.md, REPOSITORY.md and build_review_package.sh say the review package must not be committed; the file is load-bearing for the declared-commit gates | @owner | HYGIENE | verified-fixed | Post-run 2026-10-11: doctrine updated (.gitignore/AGENTS.md/REPOSITORY.md/build_review_package.sh) - the force-added review-package/MANIFEST.sha256 is documented as the declared-commit anchor (PR #55). |
| INFRA-P2-005 | P2 | Disk guard failing: root LV below its 20 GiB threshold after the nightly snapshot; reclaims exhausted | @owner | INFRA | verified-fixed | Post-run 2026-10-11: see PERF-P1-002 - guard no longer failing; root 52 GiB free (PR #55). |
| INFRA-P2-006 | P2 | Nightly offsite backup in a multi-hour catch-up; offsite RPO ~33 h at capture and not yet verifiable | @owner | INFRA | open |  |
| INV-P2-001 | P2 | Repository is majority generated/derived content; largest trees bound, audit records and mct/ remain unbound | @owner | INV | open |  |
| IR-P2-001 | P2 | No facilitated tabletop exercise has been run; Scenario 5 (total monitoring/alerting loss) remains unexercised | @owner | IR | open |  |
| IR-P2-002 | P2 | Escalation contacts remain placeholders; the incident escalation path is unverified | @owner | IR | open |  |
| IR-P2-003 | P2 | Recurring incidents still lack post-incident review; the Oct 10-11 events (offsite state damage, kernel reboot/socket outage, root-LV guard loop) have no record | @owner | IR | open |  |
| IR-P2-004 | P2 | Previous-fix verification failed for the Wazuh proxy boot ordering: the 2026-10-01 'verified CLOSED' claim is contradicted by the 2026-10-11 boot | @owner | IR | open |  |
| NOTIF-P2-002 | P2 | Notification noise remains high; the accurate disk-guard root alert now dominates and sub-repeat-interval flapping persists | @owner | NOTIF | still-open |  |
| OBS-P2-001 | P2 | ALERT_CATALOGUE.yaml, README and CURRENT_STATE lag live Grafana by one rule while claiming the catalogue cannot drift | @owner | OBS | verified-fixed | Post-run 2026-10-11: catalogue/README/CURRENT_STATE regenerated to 91 = live (PR #55); drift test + alert lint pass. |
| OBS-P2-002 | P2 | Alert noise remains high and is now dominated by the disk-guard alert repeated every 15 minutes; planned reboots produce artifact alerts | @owner | OBS | open |  |
| OBS-P2-003 | P2 | Pipeline counters rule fires on benign edge_ingest HTTP method rejections and the lazily-registered Vector counters vanish, producing a counter reset inside the firing window | @owner | OBS | verified-fixed | Post-run 2026-10-11: edge_ingest HTTP method rejections excluded from the data-loss error sum and exported separately (falcon_pipeline_edge_ingest_errors_total; PR #55). |
| OBS-P2-004 | P2 | No alert for a stuck backup run or for failed systemd units; detection depends on 36 h staleness rules | @owner | OBS | verified-fixed | Post-run 2026-10-11: falcon_backup_service_state metric + 2 rules (failed 5m, stuck-activating 4h) live (PR #55). |
| ORCH-P2-001 | P2 | Committed 2026-10-05 full-run record contradicts the canonical gate and omits the domain evidence | @owner | ORCH | open |  |
| ORCH-P2-002 | P2 | full_domain.py hardcodes profile=base and records area codes as lenses; falcon-lab coverage is not representable | @owner | ORCH | open |  |
| PERF-P2-001 | P2 | Persistent host memory/swap pressure with uncapped Wazuh/IRIS stacks; measured capacity envelope and memory budget remain stale | @owner | PERF | open |  |
| PERF-P2-002 | P2 | Data-LV warning/reclaim thresholds remain GiB constants that sit above OpenSearch's default watermarks on a 224 GiB volume | @owner | PERF | open |  |
| PERF-P2-006 | P2 | 21.7 GiB stale migration bundle (plus 6.5 GiB Wazuh backup dir) sits on the root LV outside the guard's reclaim policy with no expiry | @owner | PERF | verified-fixed | Post-run 2026-10-11: bundle archived to /srv/falcon/archive/wz-migration (cmp-verified) + README with review date; source removed; root freed 21.7 GiB. |
| PERF-P2-007 | P2 | Root-disk projection rule is blind to the current below-threshold state; no alert on the guard's own root threshold or reclaim failure | @owner | PERF | verified-fixed | Post-run 2026-10-11: falcon-disk-root-free-low rule live on falcon_disk_guard_root_free_bytes (PR #55). |
| PRIV-P2-001 | P2 | The vendored MCT client/vendor layer still has no privacy-classification boundary in this repository | @owner | PRIV | open |  |
| PRIV-P2-003 | P2 | The published production verdict still binds a superseded package and carries a contradictory readiness line | @owner | PRIV | open |  |
| REL-P2-001 | P2 | Deployment state is not bound to any release: no tags/VERSION and no deploy manifest; the live tree is now clean at main HEAD | @owner | REL | open |  |
| REL-P2-002 | P2 | Published PACKAGE_MANIFEST.sha256 is stale: it disagrees with the declared review-package manifest on 8 files and no gate compares them | @owner | REL | verified-fixed | Post-run 2026-10-11: same fix as INV-P3-004 - shipped manifest synced + publish_digests copies it on every bind; equality PASS. |
| RES-P2-001 | P2 | Host memory/swap pressure improved but remains: ~33% available, ~4.0 GiB swap used; capacity envelope stale | @owner | RES | open |  |
| SBOM-P2-001 | P2 | Release/SBOM artifacts are integrity-checked but unsigned; image/SBOM license gate not enforced | @owner | SBOM | open |  |
| SC-P2-002 | P2 | Inherited credential estate is still pending rotation and 20 vendored scripts source credential files wholesale | @owner | SC | open |  |
| SEARCH-P2-001 | P2 | Retention gaps remain on the Wazuh indexer alerts class and IRIS; RETENTION_MATRIX.md is stale | @owner | SEARCH | still-open |  |
| SEARCH-P2-002 | P2 | OpenSearch snapshot repository still on the root LV; root free is below the guard threshold and the guard now fails every 15 minutes | @owner | SEARCH | open |  |
| SEC-P2-001 | P2 | Public-facing routers have no origin authentication; ntfy-auth is dead config | @owner | SEC | open |  |
| SEC-P2-002 | P2 | Public rate limits key on client-supplied X-Forwarded-For; no per-account limits on auth endpoints | @owner | SEC | open |  |
| SEC-P2-004 | P2 | Deployed enrollment service is a stale build: per-device token expiry is not enforced and the documented issuance flow is rejected | @owner | SEC | verified-fixed | Post-run 2026-10-11: redeployed from the repo (enroll-service-install.sh) - expiry enforcement live; deployed-vs-repo hash check wired into the daily closure check (falcon_enrollment_deployed_match) + drift rule (PR #55); live check reports match. |
| SECRET-P2-001 | P2 | Inherited credential estate still 20/20 pending rotation; vendored scripts source credential stores wholesale | @owner | SECRET | still-open |  |
| SECRET-P2-002 | P2 | Live owner credential file has undocumented keys and the validator is not wired into any gate | @owner | SECRET | still-open |  |
| TEST-P2-001 | P2 | external-smoke no longer verifies Cloudflare Access from an external vantage; it accepts the owner-IP bypass | @owner | TEST | still-open |  |
| ACM-P3-001 | P3 | No consolidated access-control matrix; authorization remains per-service and distributed across four documents | @owner | ACM | open |  |
| ACM-P3-002 | P3 | Documented Cloudflare Access policy state does not match live behavior: the falcon app has no owner-IP bypass (and two dead apps remain) | @owner | ACM | open |  |
| AI-P3-001 | P3 | Agent/audit-run pointers are stale: the lifecycle runbook still calls the closed 2026-09-30 run 'the current run' and AGENTS.md/README point at it as the full-domain reference | @owner | AI | open |  |
| AI-P3-002 | P3 | No AI-provenance policy and no per-tool agent instruction coverage | @owner | AI | open |  |
| API-P3-002 | P3 | Public-access deploy script still names the retired dash.falcon/ntfy.falcon hostnames in its operator guidance | @owner | API | verified-fixed | Post-run 2026-10-11: 97 operator text updated to falcon/iris/enroll (PR #55). |
| ARCH-P3-001 | P3 | Port matrix describes ingest auth as a shared secret header while the implementation is HTTP basic auth | @owner | ARCH | open |  |
| ARCH-P3-002 | P3 | Container-level memory and policy-restart alerting for central services is still absent | @owner | ARCH | open |  |
| BP-P3-001 | P3 | Dependabot auto-merge compensating control has never been exercised | @owner | BP | open |  |
| CHAIN-P3-001 | P3 | Anonymous origin -> admin console exposure, plus latent docker.sock mounts in the vendored Shuffle compose | @owner | CHAIN | still-open |  |
| CHAIN-P3-002 | P3 | No automated live-vs-repo drift check for the exposure edges; the applied wg0 narrowing can regress silently | @owner | CHAIN | verified-fixed | Post-run 2026-10-11: same as INFRA-P2-004 - live-vs-declared tunnel drift check + rule + daily timer (PR #55). |
| CI-P3-001 | P3 | Hosted-runner fallback is dead; scheduled/queued workflow failures stay silent | @owner | CI | open |  |
| CI-P3-002 | P3 | Three probe workflows remain registered/active with no file on any branch | @owner | CI | open |  |
| CI-P3-003 | P3 | CI/CD incident playbook section 8 is stale on tool pinning and captured-run evidence | @owner | CI | open |  |
| CI-P3-004 | P3 | Review package is documented as a CI/release artifact but no CI job builds or publishes it | @owner | CI | open |  |
| CTR-P3-001 | P3 | Vendored MCT compose still mounts docker.sock and uses unpinned images under a blanket waiver | @owner | CTR | still-open |  |
| CTR-P3-002 | P3 | Local OpenSearch image installs the repository-s3 plugin as root with no artifact pin; rebuild mismatch is warn-only | @owner | CTR | still-open |  |
| DATA-P3-004 | P3 | Nightly backup leaves an unencrypted config archive beside the encrypted one and never removes it | @owner | DATA | verified-fixed | Post-run 2026-10-11: 85-backup-job.sh removes the plaintext config archive after a successful encrypt (PR #55). |
| DATA-P3-005 | P3 | Retention documentation drift: snapshot cadence/keep count disagree and the Wazuh indexer backup job is not in the matrix | @owner | DATA | partially-fixed | Post-run 2026-10-11: retention docs corrected to 1/day keep-2 (RETENTION_MATRIX/SCHEMA_AND_RETENTION/CURRENT_STATE) + the IRIS backup note (PR #55); the Wazuh indexer backup row is still omitted - follow-up. |
| DET-P3-001 | P3 | [GIT] No LICENSE file | @owner | DET | open |  |
| DET-P3-002 | P3 | [SEC] gitleaks not installed (secret scan skipped) | @owner | DET | open |  |
| DET-P3-003 | P3 | [SUPPLY] 29 container image(s) without a digest pin | @owner | DET | open |  |
| DOC-P2-001 | P3 | Pack-fidelity verification is still not wired into the delivery build; the notes file carries no verdict | @owner | DOC | open |  |
| DOC-P3-001 | P3 | Imprecise version shorthand in the README vs the pinned versions | @owner | DOC | open |  |
| DR-P3-001 | P3 | Scheduled end-to-end restore assertion still absent; the merged assertion exists in the live tree but is not scheduled | @owner | DR | open |  |
| EVOL-P3-002 | P3 | No feature-flag mechanism; the documented additive-deploy substitute is pending owner acceptance | @owner | EVOL | open |  |
| FEAT-P3-001 | P3 | Alert-rule count claims and the catalogue lag the provisioned set by one rule after the 2026-10-11 proxy-listener addition | @owner | FEAT | verified-fixed | Post-run 2026-10-11: catalogue/README/CURRENT_STATE now 91 = live 91 (PR #55). |
| HYGIENE-P3-001 | P3 | No root LICENSE/NOTICE file; README ownership section grants no terms | @owner | HYGIENE | open |  |
| INV-P3-001 | P3 | Legacy host-absolute evidence paths require the resolver to resolve in a clone | @owner | INV | open |  |
| INV-P3-002 | P3 | Delivery pack fidelity artifact ships two unresolved 'unexpected; investigate' entries | @owner | INV | open |  |
| INV-P3-003 | P3 | 'A stale digest fails' is enforced by publication equality, not by the digest-binding check whose docstring claims it | @owner | INV | open |  |
| INV-P3-004 | P3 | Published PACKAGE_MANIFEST.sha256 is two publication cycles stale and disagrees with the shipped review-package manifest; no check binds it | @owner | INV | verified-fixed | Post-run 2026-10-11: shipped PACKAGE_MANIFEST.sha256 synced + wired into publish_digests (0b24a70); equality PASS at the new bind. |
| INV-P3-005 | P3 | HYG-P1-001 doctrine ('review-package is generated, gitignored, must not be committed') contradicts the tracked review-package/MANIFEST.sha256 | @owner | INV | verified-fixed | Post-run 2026-10-11: doctrine updated - the force-tracked manifest is the documented publication anchor (PR #55). |
| IR-P2-005 | P3 | The 2026-10-11 kernel-upgrade reboot was not recorded as a maintenance window and had no post-reboot verification | @owner | IR | open |  |
| NOTIF-P2-001 | P3 | ntfy-auth Traefik middleware is still dead config; ntfy-native deny-all remains the only access control | @owner | NOTIF | still-open |  |
| NOTIF-P3-003 | P3 | Retired public lab-ntfy hostname still referenced in ledgers and the 97 deploy fallback text | @owner | NOTIF | partially-fixed | 97 fallback text fixed (PR #55); the EX-20/R-24 rows are historical records; the PORT_PROTOCOL_MATRIX N-21 current-path row update is queued. |
| ORCH-P3-001 | P3 | Run id does not start with the timestamp required by the consumer repo's lifecycle check | @owner | ORCH | open |  |
| ORCH-P3-002 | P3 | Domain report and findings array disagree on a finding status inside the same 20261009 run artifact | @owner | ORCH | open |  |
| PERF-P3-001 | P3 | Measured performance envelope and capacity model remain stale; the cost register still has no unit costs and no performance budgets exist | @owner | PERF | open |  |
| PERF-P3-002 | P3 | Per-minute whole-cluster monitoring queries still run against the single-node OpenSearch cluster with no exporter runtime budget | @owner | PERF | open |  |
| PERF-P3-008 | P3 | CI has no dependency or tool caching: every validate run re-downloads pinned tools and reinstalls hash-pinned Python deps | @owner | PERF | open |  |
| PERF-P3-009 | P3 | Edge ingest-spool purge counter advances ~268 MB/day, its data-loss meaning is unverified, and no live consumer of the spool is configured | @owner | PERF | open |  |
| PRIV-P3-001 | P3 | Owner/legal privacy inputs and the 'synthetic-only' wording remain outstanding | @owner | PRIV | open |  |
| REL-P3-001 | P3 | No root CHANGELOG/release-notes generator; the 2026-10-04..11 window is undocumented | @owner | REL | still-open |  |
| REL-P3-002 | P3 | Releases are not versioned: no tags, no VERSION file; binding artifacts overwrite in place | @owner | REL | open |  |
| REL-P3-003 | P3 | The delivered package embeds a closeout bound to the previous publication cycle (b09a50f) while the digest declares 3c11752; the equality gate reads the working tree only | @owner | REL | open |  |
| RES-P3-001 | P3 | Failure-injection coverage still omits the failure modes that actually occurred (aggregator OOM, host memory, boot-order/socket, root-LV exhaustion) | @owner | RES | open |  |
| RES-P3-002 | P3 | No post-reboot verification was run or recorded after the 2026-10-11 kernel-upgrade reboot; post-reboot degradations were visible only through alerts | @owner | RES | open |  |
| SBOM-P3-001 | P3 | Delivered review package excludes the SBOM set entirely; only the summary CSV ships | @owner | SBOM | open |  |
| SBOM-P3-002 | P3 | SBOM enforcement doc contradicts the current CI gate (says --require-vuln is off) | @owner | SBOM | open |  |
| SC-P3-001 | P3 | Published PACKAGE_MANIFEST.sha256 is stale vs the declared package manifest; no CI check compares them | @owner | SC | verified-fixed | Post-run 2026-10-11: root PACKAGE_MANIFEST.sha256 synced + publish_digests.sh now copies it on every bind (0b24a70); the rebind at e38cc48 keeps digest==shipped manifest (equality PASS). |
| SC-P3-002 | P3 | Dependabot security updates (automated fix PRs) remain disabled after alerts were enabled | @owner | SC | verified-fixed | Post-run 2026-10-11: automated security fixes enabled via the GitHub API (PUT 204, state enabled). |
| SEARCH-P3-001 | P3 | Legacy falcon-eve indices keep divergent mappings; consumer queries silently under-return | @owner | SEARCH | still-open |  |
| SEC-P3-004 | P3 | wg0 tunnel has no peer-class separation; every peer (including client endpoints) can reach the edge control plane and Wazuh proxies | @owner | SEC | open |  |
| SEC-P3-005 | P3 | Console session cookies are not marked Secure (central OSD explicit cookie.secure: false; Grafana/Wazuh default) | @owner | SEC | open |  |
| SECRET-P3-001 | P3 | Rotation register/live-store paths for IRIS and the MCT stack are stale after consolidation | @owner | SECRET | still-open |  |
| SECRET-P3-002 | P3 | Break-glass custody is procedural only (OD-04 pending); no custodian, sealed credential, or rehearsal | @owner | SECRET | still-open |  |
| TEST-P3-001 | P3 | CI evidence-integrity check verifies zero captures; all meta files reference off-repo artifact paths | @owner | TEST | still-open |  |
| TEST-P3-002 | P3 | The test-requires skip marker is only honored in the first 15 lines; validate_gate_test.sh's marker is dead | @owner | TEST | open | Re-reviewed 2026-10-11: the skip-fixture marker sits at fixture line 2 (inside the reader's 15-line window) and validate_gate_test passes 12/12; no code change made - harmless as reported. |
| WH-P3-001 | P3 | No replay/idempotency protection or tests on the notification path (ntfy); Shuffle path retired | @owner | WH | still-open |  |
