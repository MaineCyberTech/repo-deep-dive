# Falcon verify register — main@db8c409

| ID | Sev | Status | Title |
|---|---|---|---|
| ACM-P2-004 | P1 | verified-fixed | Endpoint-script sync embeds the entire enrollment token file (all per-device tokens) into every device script |
| ARCH-P1-001 | P1 | owner-accepted | Single-host concentration: host loss is total pipeline loss |
| DATA-P1-001 | P1 | owner-accepted | Wazuh/IRIS retention coverage is incomplete and the repository statement contradicts the live estate (alerts c |
| DR-P1-002 | P1 | partially-fixed | Offsite upload-state truncation class is still not fail-closed; live RPO is currently met |
| EVOL-P1-001 | P1 | partially-fixed | Cross-repo shared tooling has drifted and still has no pin/hash enforcement |
| EVOL-P1-002 | P1 | verified-fixed | MCT vendoring policy is proposed but not enforced; the pin gate remains blind to mct/compose |
| PERF-P1-002 | P1 | verified-fixed | Root LV incident condition is cleared; guard and projection rules are healthy |
| PRIV-P1-001 | P1 | verified-fixed | Wazuh indexer and IRIS case data still have no retention or deletion window (owner-gated) |
| RES-P1-002 | P1 | verified-fixed | Root LV is above the disk-guard threshold; guard/alert state is healthy |
| RES-P2-002 | P1 | verified-fixed | Wazuh VPN proxy socket boot race is fixed and has survived a boot |
| WH-P1-001 | P1 | partially-fixed | OpenSearch sink drops failed batches with no dead-letter/replay path (detection now closed and live-verified) |
| ACM-P2-001 | P2 | partially-fixed | Live client-VPN enrollment credential is a single shared token with no expiry; per-device lifecycle implemente |
| ACM-P2-003 | P2 | verified-fixed | Deployed enrollment service does not enforce per-device token expiry; issuance tool and deployed enforcement d |
| ADMIN-P2-001 | P2 | verified-fixed | Admin/observability consoles are exposed through public routers without origin authentication |
| ADMIN-P2-002 | P2 | partially-fixed | The Access-posture gate accepts origin reachability; no automated check verifies Cloudflare Access enforcement |
| ADMIN-P2-003 | P2 | partially-fixed | No centralized actor-level audit trail for Grafana/ntfy/IRIS console admin actions |
| ADMIN-P2-004 | P2 | verified-fixed | Kestrel cutover left Cloudflare Access in the independent posture check, deploy provisioning and current-state |
| ADMIN-P2-005 | P2 | partially-fixed | Console API still requires a Cloudflare Access JWT and grants admin to owner-IP/LAN, not the Kestrel identity  |
| ADMIN-P2-006 | P2 | verified-fixed | Console action endpoints have no CSRF/Origin enforcement and trust an owner-IP/LAN admin identity |
| ADMIN-P2-007 | P2 | verified-fixed | Trusted-header SSO trusts entire Docker subnets: any frontend/backend container can self-assert Grafana/OpenSe |
| API-P2-001 | P2 | partially-fixed | Ingest contract relies on a shared secret header, not request signing or idempotency keys |
| ARCH-P2-002 | P2 | owner-accepted | Vendored MCT tree remains tag-only under a blanket pin waiver; live stacks are tag@digest and lock-covered |
| ARCH-P2-003 | P2 | partially-fixed | Live ingest authentication is an HTTP basic-auth shared credential, not mTLS or request signing |
| ARCH-P2-003 | P2 | verified-fixed | Live ingest authentication is an HTTP basic-auth shared credential, not mTLS or request signing |
| BP-P2-001 | P2 | verified-fixed | CODEOWNERS resolves to the owner account |
| CHAIN-P2-001 | P2 | partially-fixed | The only automated Access-posture check no longer verifies Access (external-smoke accepts any 302 from the lab |
| CI-P2-001 | P2 | partially-fixed | Auto-merge workflow holds contents:write with no environment protection |
| CI-P2-002 | P2 | partially-fixed | Independent Access-posture check no longer matches the live identity gate and is stuck in 'alerted' |
| CI-P2-003 | P2 | partially-fixed | Repository Actions settings remain partly permissive |
| CI-P2-004 | P2 | verified-fixed | CI installs two Python shell-test dependencies by bare version with no hashes or update path |
| CTR-P2-001 | P2 | partially-fixed | Adopted stacks now have hardening overlays and healthchecks, but not the full baseline |
| DATA-P2-002 | P2 | verified-fixed | Root LV is below the disk guard's 20 GiB threshold: the guard fails every 15 minutes and cannot reclaim back a |
| DATA-P2-003 | P2 | partially-fixed | Edge control-plane spool keeps purging ~134 MiB per 10-14 h; nothing consumes it and the purge alert cannot fi |
| DET-P2-001 | P2 | open | [PORT] CRLF committed for 1 file (raw evidence capture; policy edge) |
| DOC-P2-002 | P2 | partially-fixed | Status artifacts still lag the live state: catalogue/README/CURRENT_STATE at 94 vs 95 provisioned, firing proo |
| DOC-P2-003 | P2 | verified-fixed | Operator entry docs still route to Grafana at the public root and describe basic auth after the Console/Kestre |
| DR-P2-002 | P2 | partially-fixed | Nightly offsite is encrypted, but historical plaintext bulk objects remain and SSE is not set |
| DR-P2-003 | P2 | verified-fixed | IRIS case database is dumped daily and shipped encrypted offsite |
| DR-P2-004 | P2 | verified-fixed | Offsite verification passes vacuously on an empty or unexpectedly tiny snapshot repository |
| EVOL-P2-001 | P2 | verified-fixed | The OpenSearch identity apply is not merge-safe (R-28 hazard documented; owner decision pending) |
| FEAT-P2-001 | P2 | verified-fixed | Vendored MCT services are present in Compose while the subtree policy calls the tree archive-only |
| HYGIENE-P2-001 | P2 | partially-fixed | Large generated SBOM/vulnerability JSON remains committed (56 files, 58.4 MB, up to 3.0 MB each) |
| HYGIENE-P2-002 | P2 | partially-fixed | Canonical release-gate page carries a superseded audit opinion; the newest full run's P0 is not referenced |
| HYGIENE-P2-003 | P2 | verified-fixed | The publication flow force-tracks review-package/MANIFEST.sha256 while .gitignore, AGENTS.md, REPOSITORY.md an |
| INV-P2-001 | P2 | open | Repository is majority generated/derived content; largest trees bound, audit records and mct/ remain unbound |
| INV-P2-002 | P2 | verified-fixed | The review pack omits the entire SBOM/vuln set but the package manifest lists it; pack fidelity still reports  |
| INV-P2-003 | P2 | verified-fixed | Review package omits the Falcon Console source and the root LICENSE/NOTICE/VERSION/CHANGELOG files |
| IR-P2-001 | P2 | open | No facilitated tabletop exercise has been run |
| IR-P2-002 | P2 | open | Escalation contacts remain placeholders |
| IR-P2-003 | P2 | partially-fixed | Recurring incidents still lack post-incident review |
| IR-P2-004 | P2 | verified-fixed | Wazuh proxy boot-order fix has now survived a boot; the stale comment is cosmetic |
| NOTIF-P2-002 | P2 | partially-fixed | Notification noise remains high; the accurate disk-guard root alert now dominates and sub-repeat-interval flap |
| OBS-P2-001 | P2 | verified-fixed | Alert catalogue/README/CURRENT_STATE drifted again: script has 95 rules, catalogue has 94 |
| OBS-P2-002 | P2 | partially-fixed | Alert noise is improved but repeat/reboot tuning remains |
| OBS-P2-003 | P2 | verified-fixed | Benign edge_ingest HTTP rejections are excluded from the data-loss signal |
| OBS-P2-004 | P2 | verified-fixed | Stuck/failed backup runs and generic systemd unit failure are visible |
| ORCH-P2-001 | P2 | partially-fixed | Committed 2026-10-05 full-run record contradicts the canonical gate and omits the domain evidence |
| ORCH-P2-002 | P2 | partially-fixed | full_domain.py hardcodes profile=base and records area codes as lenses; falcon-lab coverage is not representab |
| ORCH-P2-003 | P2 | open | The newest committed audit run fails the audit pack's own run checker (manifest keys and status vocabulary) |
| PERF-P2-001 | P2 | partially-fixed | Memory/swap pressure remains; caps and envelope were refreshed |
| PERF-P2-002 | P2 | verified-fixed | Data-LV guard/alert thresholds sit above the OpenSearch watermarks |
| PERF-P2-006 | P2 | verified-fixed | Stale migration bundle is archived off the root LV with a review date |
| PERF-P2-007 | P2 | verified-fixed | Projection and root-free rules now cover the actual constraint |
| PRIV-P2-001 | P2 | verified-fixed | The vendored MCT client/vendor layer still has no privacy-classification boundary in this repository |
| PRIV-P2-003 | P2 | open | The published production verdict still binds a superseded package and carries a contradictory readiness line |
| REL-P2-001 | P2 | open | Deployment state is not bound to any release: no tags/VERSION and no deploy manifest; the live tree is now cle |
| REL-P2-002 | P2 | verified-fixed | Published PACKAGE_MANIFEST.sha256 is stale: it disagrees with the declared review-package manifest on 8 files  |
| REL-P2-003 | P2 | verified-fixed | Main is unbound and red after the Kestrel SSO merges: publication equality fails at db8c409 and the package st |
| RES-P2-001 | P2 | partially-fixed | Host memory/swap pressure improved but remains; capacity budget is still not codified |
| SBOM-P2-001 | P2 | partially-fixed | SBOM signature and license gate exist, but the manifest hash is not bound into PACKAGE_DIGEST |
| SC-P2-002 | P2 | partially-fixed | Inherited credential estate is still partly unrotated and 20 vendored scripts source credential files wholesal |
| SEARCH-P2-001 | P2 | partially-fixed | Retention gaps remain on the Wazuh indexer alerts class and IRIS; RETENTION_MATRIX.md is stale |
| SEARCH-P2-002 | P2 | verified-fixed | OpenSearch snapshot repository still on the root LV; root free is below the guard threshold and the guard now  |
| SEC-P2-001 | P2 | verified-fixed | Public-facing routers have no origin authentication; ntfy-auth is dead config |
| SEC-P2-002 | P2 | partially-fixed | Public rate limits key on client-supplied X-Forwarded-For; no per-account limits on auth endpoints |
| SEC-P2-004 | P2 | verified-fixed | Deployed enrollment service is a stale build: per-device token expiry is not enforced and the documented issua |
| SEC-P2-005 | P2 | partially-fixed | SSO header adapter authenticates unsigned X-Authentik-*/Remote-* headers on 0.0.0.0:8090 |
| SEC-P2-006 | P2 | verified-fixed | Client VPN peer-class firewall rule is a hardcoded three-address set; dynamically enrolled clients .23-.99 rea |
| SECRET-P2-001 | P2 | partially-fixed | Inherited credential estate is still 11/20 pending; vendored scripts still source stores wholesale |
| SECRET-P2-002 | P2 | verified-fixed | Owner-env validator is wired into the gate |
| TEST-P2-001 | P2 | verified-fixed | external-smoke no longer verifies Cloudflare Access from an external vantage; it accepts the owner-IP bypass |
| TEST-P2-002 | P2 | open | The mTLS ingest migration left three plaintext HTTP validation paths that can no longer exercise replay/DLQ in |
| ACM-P3-001 | P3 | open | No consolidated access-control matrix; authorization remains per-service and distributed across four documents |
| ACM-P3-002 | P3 | open | Documented Cloudflare Access policy state does not match live behavior: the falcon app has no owner-IP bypass  |
| AI-P3-001 | P3 | partially-fixed | Agent/audit-run pointers are stale: the lifecycle runbook still calls the closed 2026-09-30 run 'the current r |
| AI-P3-002 | P3 | partially-fixed | No AI-provenance policy and no per-tool agent instruction coverage |
| API-P3-002 | P3 | verified-fixed | Public-access deploy script still names the retired dash.falcon/ntfy.falcon hostnames in its operator guidance |
| ARCH-P3-001 | P3 | verified-fixed | Port matrix describes ingest auth as a shared secret header while the implementation is HTTP basic auth |
| ARCH-P3-002 | P3 | verified-fixed | Container-level memory and policy-restart alerting for central services is still absent |
| BP-P3-001 | P3 | open | Dependabot auto-merge compensating control still has never been exercised |
| CHAIN-P3-001 | P3 | verified-fixed | Anonymous origin -> admin console exposure, plus latent docker.sock mounts in the vendored Shuffle compose |
| CHAIN-P3-002 | P3 | open | No automated live-vs-repo drift check for the exposure edges; the applied wg0 narrowing can regress silently |
| CI-P3-001 | P3 | verified-fixed | Hosted-runner fallback is gone and scheduled/queued CI failures are watched |
| CI-P3-002 | P3 | verified-fixed | Stale workflow registrations no longer exist |
| CI-P3-003 | P3 | verified-fixed | CI/CD incident playbook section 8 matches the pinned-tool state |
| CI-P3-004 | P3 | open | Review package is still documented as a CI/release artifact but no CI job builds it |
| CTR-P3-001 | P3 | partially-fixed | Vendored MCT compose no longer mounts docker.sock but still carries unpinned refs under a blanket waiver |
| CTR-P3-002 | P3 | open | Local OpenSearch image installs the S3 plugin as root with no artifact checksum; rebuild mismatch is warn-only |
| DATA-P3-004 | P3 | verified-fixed | Nightly backup leaves an unencrypted config archive beside the encrypted one and never removes it |
| DATA-P3-005 | P3 | partially-fixed | Retention documentation drift: snapshot cadence/keep count disagree and the Wazuh indexer backup job is not in |
| DET-P3-002 | P3 | open | [SEC] gitleaks is not installed on the host running the deterministic lens |
| DET-P3-003 | P3 | owner-accepted | [SUPPLY] 30 container image refs without a digest pin (vendored/archive-only trees) |
| DET-P3-004 | P3 | open | [SUPPLY] hadolint is not installed and CI has no Dockerfile lint step |
| DOC-P2-001 | P3 | verified-fixed | Pack-fidelity verification is still not wired into the delivery build; the notes file carries no verdict |
| DOC-P3-001 | P3 | verified-fixed | Imprecise version shorthand in the README vs the pinned versions |
| DOC-P3-002 | P3 | verified-fixed | Check-engine runbook status block contradicts its own phase table and the deployed 2026-10-15 waves |
| DOC-P3-003 | P3 | verified-fixed | Policy/guide status text still says proposed/not implemented where the repository records implemented controls |
| DR-P3-001 | P3 | open | Scheduled end-to-end live restore assertion is still absent |
| EVOL-P3-002 | P3 | verified-fixed | No feature-flag mechanism; the documented additive-deploy substitute is pending owner acceptance |
| FEAT-P3-001 | P3 | verified-fixed | Alert-rule count claims and the catalogue lag the provisioned set by one rule after the 2026-10-11 proxy-liste |
| HYGIENE-P3-001 | P3 | verified-fixed | No root LICENSE/NOTICE file; README ownership section grants no terms |
| INV-P3-001 | P3 | open | Legacy host-absolute evidence paths require the resolver to resolve in a clone |
| INV-P3-002 | P3 | verified-fixed | Delivery pack fidelity artifact ships two unresolved 'unexpected; investigate' entries |
| INV-P3-003 | P3 | verified-fixed | 'A stale digest fails' is enforced by publication equality, not by the digest-binding check whose docstring cl |
| INV-P3-004 | P3 | verified-fixed | Published PACKAGE_MANIFEST.sha256 is two publication cycles stale and disagrees with the shipped review-packag |
| INV-P3-005 | P3 | verified-fixed | HYG-P1-001 doctrine ('review-package is generated, gitignored, must not be committed') contradicts the tracked |
| IR-P2-005 | P3 | verified-fixed | The 2026-10-11 reboot/post-reboot verification is recorded |
| NOTIF-P2-001 | P3 | verified-fixed | ntfy-auth Traefik middleware is still dead config; ntfy-native deny-all remains the only access control |
| NOTIF-P3-003 | P3 | partially-fixed | Retired public lab-ntfy hostname still referenced in ledgers and the 97 deploy fallback text |
| OBS-P3-001 | P3 | open | Console Prometheus-backed sections are blank after the 2026-11-05 reboot |
| ORCH-P3-001 | P3 | verified-fixed | Run id does not start with the timestamp required by the consumer repo's lifecycle check |
| ORCH-P3-002 | P3 | open | Domain report and findings array disagree on a finding status inside the same 20261009 run artifact |
| PERF-P3-001 | P3 | partially-fixed | Performance envelope refreshed, but the capacity model, unit costs and budgets are stale |
| PERF-P3-002 | P3 | open | Whole-cluster monitoring queries still run every 120 s with no exporter runtime budget |
| PERF-P3-008 | P3 | verified-fixed | CI tool and Python dependency caching is in place |
| PERF-P3-009 | P3 | partially-fixed | Edge spool now has 7-day retention, but its data-loss meaning and consumer remain unverified |
| PRIV-P3-001 | P3 | open | Owner/legal privacy inputs and the 'synthetic-only' wording remain outstanding |
| REL-P3-001 | P3 | partially-fixed | No root CHANGELOG/release-notes generator; the 2026-10-04..11 window is undocumented |
| REL-P3-002 | P3 | verified-fixed | Releases are not versioned: no tags, no VERSION file; binding artifacts overwrite in place |
| REL-P3-003 | P3 | partially-fixed | The delivered package embeds a closeout bound to the previous publication cycle while the digest declares the  |
| RES-P3-001 | P3 | open | Failure-injection coverage still omits the failure modes that actually occurred |
| RES-P3-002 | P3 | open | Post-reboot verification is still manual and the 2026-11-05 boot has no record |
| SBOM-P3-001 | P3 | verified-fixed | Review package now ships the SBOM set |
| SBOM-P3-002 | P3 | partially-fixed | SBOM enforcement document still contradicts the CI gate |
| SC-P3-001 | P3 | verified-fixed | Published package manifest equals the bound review-package manifest |
| SC-P3-002 | P3 | verified-fixed | Dependabot security updates are enabled |
| SEARCH-P3-001 | P3 | verified-fixed | Legacy falcon-eve indices keep divergent mappings; consumer queries silently under-return |
| SEC-P3-004 | P3 | open | wg0 tunnel has no peer-class separation; every peer (including client endpoints) can reach the edge control pl |
| SEC-P3-005 | P3 | verified-fixed | Console session cookies are not marked Secure (central OSD explicit cookie.secure: false; Grafana/Wazuh defaul |
| SECRET-P3-001 | P3 | open | Rotation register and vendored checklist still name pre-consolidation IRIS/MCT paths |
| SECRET-P3-002 | P3 | open | Break-glass custody is still procedural only (OD-04 pending) |
| TEST-P3-001 | P3 | partially-fixed | CI evidence-integrity check verifies zero captures; all meta files reference off-repo artifact paths |
| TEST-P3-002 | P3 | open | The test-requires skip marker is only honored in the first 15 lines; validate_gate_test.sh's marker is dead |
| WH-P3-001 | P3 | partially-fixed | No replay/idempotency protection or tests on the notification path (ntfy); Shuffle path retired |
