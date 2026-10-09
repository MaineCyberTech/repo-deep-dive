# Follow-up register

Run: `falcon-20261009-2117-full-08e20d1` · Target: `falcon` @ `08e20d1` · Profile: base

Register mirrored 1:1 with `risk_register.md` so `tools/check_run.sh` passes.

| Finding | Severity | Title | Owner | Target | Status | Note |
|---|---|---|---|---|---|---|
| DATA-P0-001 | P0 | 41-hour EVE ingestion outage with confirmed data loss (empty 10.08 index, ~1.74 GB spool purge, non-retriable sink drops); durable capacity fix absent from the audited tree | @owner | DATA | open |  |
| ARCH-P1-001 | P1 | Single-host concentration: host loss is total pipeline loss | @owner | ARCH | open |  |
| ARCH-P1-002 | P1 | Live host source tree has diverged from the audited commit and is dirty; merged remediation is not deployed | @owner | ARCH | open |  |
| ARCH-P1-003 | P1 | Central Vector aggregator is in a cgroup OOM restart loop; no container memory/restart alert covers it | @owner | ARCH | open |  |
| CHAIN-P1-001 | P1 | WireGuard peers still have host-wide reach: the committed SEC-P1-002 narrowing is not applied to the live host | @owner | CHAIN | still-open | Same chain as prior CHAIN-P1-001 (20261002 run) / SEC-P1-002 (20261003 run); remediation committed at config level, never applied live. |
| CI-P1-001 | P1 | Same-repo PR workflows execute on a passwordless-sudo self-hosted runner | @owner | CI | open |  |
| DATA-P1-001 | P1 | Wazuh/IRIS retention coverage is incomplete and the repository statement contradicts the live estate | @owner | DATA | open |  |
| DR-P1-001 | P1 | Nightly backup job failed 3 times in 7 days; Oct 8-9 snapshot hole; RPO gap ~37 h; no retry and no immediate alert | @owner | DR | open |  |
| EVOL-P1-001 | P1 | Cross-repo shared tooling has drifted and still has no pin/hash enforcement | @owner | EVOL | open |  |
| EVOL-P1-002 | P1 | MCT vendoring policy proposed but not enforced; the pin gate remains blind to mct/compose | @owner | EVOL | open |  |
| INFRA-P1-001 | P1 | Declared wg0 firewall narrowing (SEC-P1-002) is not applied; every VPN peer still has blanket access | @owner | INFRA | open |  |
| NOTIF-P1-001 | P1 | Public lab ntfy endpoint is dead: tunnel ingress and repo docs disagree on the hostname; watcher heartbeat read and owner public subscriptions cannot work | @owner | NOTIF | open |  |
| OBS-P0-001 | P1 | OBS-P0-001 remediation not provisioned live: 6 rules missing from Grafana; runtime tree 22 commits behind | @owner | OBS | open |  |
| OBS-P1-001 | P1 | Aggregator source-side event drops neither exported nor alerted; 0.7-1.5M events dropped unseen | @owner | OBS | open |  |
| PERF-P1-001 | P1 | Vector aggregator OOM-kill loop under catch-up load discards events at the ingest source | @owner | PERF | open |  |
| PERF-P1-002 | P1 | Root LV carries the relocated 56 GiB snapshot repository with no root-side retention or reclaim | @owner | PERF | open |  |
| PRIV-P1-001 | P1 | Wazuh indexer and IRIS case data still have no retention or deletion window (owner-gated) | @owner | PRIV | open |  |
| RES-P1-001 | P1 | Vector aggregator OOM crash-loop drops security telemetry (512 MiB cap; 23 kills; 0.7-1.5M source-side drops per window) | @owner | RES | open |  |
| SEC-P1-001 | P1 | SEC-P1-002 remediation committed but not applied live - WireGuard blanket accept still in effect | @owner | SEC | open |  |
| WH-P1-001 | P1 | OpenSearch sink drops failed batches with no dead-letter path and the failure counters stayed 0 through a 40-hour outage | @owner | WH | open |  |
| ACM-P2-001 | P2 | Live client-VPN enrollment credential is a single shared token with no expiry; per-device lifecycle implemented but unused | @owner | ACM | open |  |
| ADMIN-P2-001 | P2 | Admin/observability consoles are exposed through public routers without origin authentication | @owner | ADMIN | open |  |
| ADMIN-P2-002 | P2 | Access-posture gate accepts origin reachability; no automated check verifies Cloudflare Access enforcement anymore | @owner | ADMIN | open |  |
| ADMIN-P2-003 | P2 | No centralized actor-level audit trail for Grafana/ntfy/IRIS console admin actions | @owner | ADMIN | open |  |
| API-P2-001 | P2 | Ingest contract relies on a shared secret header, not request signing or idempotency keys | @owner | API | open |  |
| ARCH-P2-001 | P2 | Declared container hardening lags the running containers | @owner | ARCH | open |  |
| ARCH-P2-002 | P2 | Wazuh and vendored MCT stacks run tag-only images outside pin/SBOM scope | @owner | ARCH | open |  |
| ARCH-P2-003 | P2 | Live ingest authentication is a shared secret header, not mTLS | @owner | ARCH | open |  |
| BP-P2-001 | P2 | CODEOWNERS is invalid: every entry uses an unresolvable org handle | @owner | BP | open |  |
| CHAIN-P2-001 | P2 | The only automated Access-posture check no longer verifies Access (external-smoke accepts any 302 from the lab vantage) | @owner | CHAIN | open |  |
| CI-P2-001 | P2 | Auto-merge workflow holds `contents: write` with no environment protection | @owner | CI | open |  |
| CI-P2-002 | P2 | external-smoke no longer asserts Cloudflare Access posture and passes on an owner-IP bypass | @owner | CI | open |  |
| CI-P2-003 | P2 | Repository Actions settings default to permissive (write token, PR approvals, any action, no SHA-pin requirement) | @owner | CI | open |  |
| CTR-P2-001 | P2 | Adopted MCT/Wazuh stacks run without baseline container hardening or healthchecks | @owner | CTR | open |  |
| DOC-P2-002 | P2 | The 'authoritative' current-state page lags its sources (rule count, condition status, follow-up list) | @owner | DOC | open |  |
| DR-P2-001 | P2 | OpenSearch disk watermarks left relaxed (93/96/98) after the Oct 9 incident; cluster still yellow with 44 unassigned shards | @owner | DR | open |  |
| DR-P2-002 | P2 | Bulk telemetry snapshot repositories are stored offsite unencrypted; only config/secrets archives are encrypted | @owner | DR | open |  |
| EVOL-P2-001 | P2 | The OpenSearch identity apply is not merge-safe (R-28 hazard documented; owner decision pending) | @owner | EVOL | open |  |
| FEAT-P2-001 | P2 | Vendored MCT services are present in Compose while the subtree policy calls the tree archive-only | @owner | FEAT | open |  |
| FEAT-P2-002 | P2 | Alerting feature state is stale: 79 rules claimed/catalogued, 77 live; six merged rules are not provisioned | @owner | FEAT | open |  |
| HYGIENE-P2-001 | P2 | Large generated SBOM/vulnerability JSON remains committed (37 files, 29 MB, up to 3.0 MB each) | @owner | HYGIENE | still-open | Same issue as the prior full run; sizes grew since then. |
| HYGIENE-P2-002 | P2 | Canonical release-gate page carries a superseded audit opinion; the newest full run's P0 is not referenced | @owner | HYGIENE | open |  |
| INFRA-P2-001 | P2 | Live deployment tree is not the audited commit: 22 behind origin/main, 2 ahead, and its own CI fails | @owner | INFRA | open |  |
| INFRA-P2-002 | P2 | Live Prometheus alert rules exist only as uncommitted working-tree changes | @owner | INFRA | open |  |
| INFRA-P2-003 | P2 | Daily backup hook has failed for two consecutive runs and has not updated snapshot freshness | @owner | INFRA | open |  |
| INV-P2-001 | P2 | Repository is majority generated/derived content with no in-repo regeneration or drift check | @owner | INV | open |  |
| IR-P2-001 | P2 | No facilitated tabletop exercise has been run; Scenario 5 (total monitoring/alerting loss) remains unexercised | @owner | IR | open |  |
| IR-P2-002 | P2 | Escalation contacts remain placeholders; incident escalation path unverified (IR-P2-005 open) | @owner | IR | open |  |
| IR-P2-003 | P2 | Recurring incidents lack post-incident review; Oct 8-9 backup failure has no root-cause record | @owner | IR | open |  |
| NOTIF-P2-002 | P2 | Notification noise remains high: 409 messages/48h, 361 FIRING/RESOLVED transitions, and sub-repeat-interval flapping on several rules | @owner | NOTIF | open |  |
| OBS-P2-001 | P2 | ALERT_CATALOGUE.yaml contradicts live Grafana while claiming it cannot drift | @owner | OBS | open |  |
| OBS-P2-002 | P2 | Alert noise/flapping high during incidents; root-disk projection false-positive from the relocation step | @owner | OBS | open |  |
| ORCH-P2-001 | P2 | Committed 2026-10-05 full-run record contradicts the canonical gate and omits the domain evidence | @owner | ORCH | open |  |
| ORCH-P2-002 | P2 | full_domain.py hardcodes profile=base and records area codes as lenses; falcon-lab coverage is not representable | @owner | ORCH | open |  |
| PERF-P2-001 | P2 | Persistent host memory/swap pressure; capacity envelope and memory budget stale after Wazuh/IRIS consolidation | @owner | PERF | open |  |
| PERF-P2-002 | P2 | Data-LV warning/reclaim thresholds are GiB constants that coincide with OpenSearch's own watermarks on a 221 GiB volume | @owner | PERF | open |  |
| PERF-P2-003 | P2 | Pipeline-loss metrics track only the sink; ~1M source-side discards are invisible to alerting | @owner | PERF | open |  |
| PERF-P2-004 | P2 | Data-LV warning/reclaim thresholds are GiB constants that coincide with OpenSearch's own watermarks on a 221 GiB volume | @owner | PERF | open |  |
| PERF-P2-005 | P2 | Pipeline-loss metrics track only the sink; ~1 M source-side discards are invisible to alerting | @owner | PERF | open |  |
| PRIV-P2-001 | P2 | Vendored MCT client/vendor layer has no privacy-classification boundary in this repository | @owner | PRIV | open |  |
| PRIV-P2-003 | P2 | Published production verdict still binds a superseded package and carries a contradictory readiness line | @owner | PRIV | open |  |
| REL-P2-001 | P2 | Deployment state is not bound to any release: the live host runs a divergent worktree with uncommitted runtime config | @owner | REL | open |  |
| RES-P2-001 | P2 | Host memory headroom exhausted: ~18.5% available, 4.5/8 GiB swap used, recurring OOM kills | @owner | RES | open |  |
| SBOM-P2-001 | P2 | Release/SBOM artifacts are integrity-checked but unsigned; image/SBOM license gate not enforced | @owner | SBOM | open |  |
| SC-P2-001 | P2 | Dependabot vulnerability alerts disabled; Python CI dependencies uncovered by version updates | @owner | SC | open |  |
| SC-P2-002 | P2 | Inherited credential estate is still pending rotation and 19 vendored scripts source credential files wholesale | @owner | SC | open |  |
| SEARCH-P2-001 | P2 | Retention gaps remain on the Wazuh indexer alerts class and IRIS; RETENTION_MATRIX.md is stale vs the live clusters | @owner | SEARCH | still-open |  |
| SEC-P2-001 | P2 | Public-facing routers have no origin authentication; `ntfy-auth` is dead config | @owner | SEC | open |  |
| SEC-P2-002 | P2 | Public rate limits key on client-supplied X-Forwarded-For; no per-account limits on auth endpoints | @owner | SEC | open |  |
| SECRET-P2-001 | P2 | Inherited credential estate still 20/20 pending rotation; vendored scripts source credential stores wholesale | @owner | SECRET | open |  |
| SECRET-P2-002 | P2 | Live owner credential file has undocumented keys and the validator is not wired into any gate | @owner | SECRET | open |  |
| TEST-P2-001 | P2 | external-smoke no longer verifies Cloudflare Access from an external vantage; it accepts the owner-IP bypass | @owner | TEST | open |  |
| ACM-P3-001 | P3 | No consolidated access-control matrix; authorization remains per-service and distributed across four documents | @owner | ACM | open |  |
| ACM-P3-002 | P3 | Documented Cloudflare Access policy state does not match live behavior for the falcon host | @owner | ACM | open |  |
| AI-P3-001 | P3 | Agent/audit-run pointers are stale: the lifecycle runbook still calls the 2026-09-30 run 'the current run' and AGENTS.md points at it as the full-domain reference | @owner | AI | open |  |
| AI-P3-002 | P3 | No AI-provenance policy and no per-tool agent instruction coverage | @owner | AI | open |  |
| ARCH-P3-001 | P3 | Port matrix describes ingest auth as a shared secret header while the implementation is HTTP basic auth | @owner | ARCH | open |  |
| BP-P3-001 | P3 | Dependabot auto-merge compensating control has never been exercised | @owner | BP | open |  |
| CHAIN-P3-001 | P3 | Anonymous origin -> admin console exposure, plus latent docker.sock mounts in the vendored Shuffle compose | @owner | CHAIN | still-open | Same composition as prior CHAIN-P3-001; both legs verified live (exposure open; socket latent/not running). |
| CI-P3-001 | P3 | Hosted-runner dependency is dead and scheduled-workflow failures are silent | @owner | CI | open |  |
| CI-P3-002 | P3 | Three probe workflows remain registered/active with no file on any branch | @owner | CI | open |  |
| CTR-P3-001 | P3 | Vendored MCT compose still mounts docker.sock and uses unpinned images under a blanket waiver | @owner | CTR | open |  |
| CTR-P3-002 | P3 | Local OpenSearch image installs the repository-s3 plugin as root with no artifact pin; rebuild mismatch is warn-only | @owner | CTR | open |  |
| DET-P3-001 | P3 | [GIT] No LICENSE file | @owner | DET | open |  |
| DET-P3-002 | P3 | [SEC] gitleaks not installed (secret scan skipped) | @owner | DET | open |  |
| DET-P3-003 | P3 | [SUPPLY] 29 container image(s) without a digest pin | @owner | DET | open |  |
| DOC-P2-001 | P3 | Pack-fidelity verification is still not wired into the delivery build; the notes file carries no verdict | @owner | DOC | open |  |
| DOC-P3-001 | P3 | Imprecise version shorthand in the README vs the pinned versions | @owner | DOC | open |  |
| DR-P3-001 | P3 | Scheduled end-to-end restore assertion still absent; merged assertion not present in the live tree | @owner | DR | open |  |
| DR-P3-002 | P3 | Local snapshot retention was ad hoc under pressure; recovery evidence contains failing delete commands | @owner | DR | open |  |
| EVOL-P3-002 | P3 | No feature-flag mechanism; the documented additive-deploy substitute is pending owner acceptance | @owner | EVOL | open |  |
| HYGIENE-P3-001 | P3 | No root LICENSE/NOTICE file; README ownership section grants no terms | @owner | HYGIENE | open |  |
| INV-P3-001 | P3 | Legacy host-absolute evidence paths require manual rewrite to resolve in a clone | @owner | INV | open |  |
| INV-P3-002 | P3 | Delivery pack fidelity artifact ships two unresolved 'unexpected; investigate' entries | @owner | INV | open |  |
| INV-P3-003 | P3 | Gate claim 'a stale digest fails' is not implemented; the delivery digest binds an 11-commit-old tree | @owner | INV | open |  |
| NOTIF-P2-001 | P3 | ntfy-auth middleware is still dead config; ntfy-native deny-all is the actual control | @owner | NOTIF | partially-fixed |  |
| NOTIF-P3-001 | P3 | Stale ntfy test-topic ACLs remain in the live user DB from the storm/probe tests | @owner | NOTIF | open |  |
| OBS-P3-001 | P3 | Live alerting config is uncommitted drift ahead of the audited commit (edge-alerts.yaml) | @owner | OBS | open |  |
| ORCH-P3-001 | P3 | Run id does not start with the timestamp required by the consumer repo's lifecycle check | @owner | ORCH | open |  |
| PERF-P3-001 | P3 | Measured performance envelope and capacity model are stale; no performance budgets exist | @owner | PERF | open |  |
| PERF-P3-002 | P3 | Per-minute whole-cluster monitoring queries add avoidable load to the single-node cluster | @owner | PERF | open |  |
| PERF-P3-006 | P3 | Measured performance envelope and capacity model are stale; no performance budgets exist | @owner | PERF | open |  |
| PERF-P3-007 | P3 | Per-minute whole-cluster monitoring queries add avoidable load to the single-node cluster | @owner | PERF | open |  |
| PRIV-P3-001 | P3 | Owner/legal privacy inputs and notice/processor artifacts outstanding; the 'synthetic-only' wording persists | @owner | PRIV | open |  |
| REL-P3-001 | P3 | No root CHANGELOG/release-notes generator; the 2026-10-04..09 window is undocumented | @owner | REL | still-open | Same issue as the prior full run; the undocumented window has grown. |
| REL-P3-002 | P3 | Releases are not versioned: no tags, no VERSION file; binding artifacts overwrite in place | @owner | REL | open |  |
| RES-P3-001 | P3 | No failure-injection coverage for aggregator OOM / host memory exhaustion (the failure mode that actually occurred) | @owner | RES | open |  |
| SBOM-P3-001 | P3 | Delivered review package excludes the SBOM set entirely; only the summary CSV ships | @owner | SBOM | open |  |
| SEARCH-P3-001 | P3 | Legacy falcon-eve indices keep divergent mappings; consumer queries against them silently under-return | @owner | SEARCH | open |  |
| SECRET-P3-001 | P3 | Rotation register/live-store paths for IRIS and the MCT stack are stale after consolidation | @owner | SECRET | open |  |
| SECRET-P3-002 | P3 | Break-glass custody is procedural only (OD-04 pending); no custodian, sealed credential, or rehearsal | @owner | SECRET | open |  |
| TEST-P3-001 | P3 | CI evidence-integrity check verifies zero captures; all meta files reference off-repo artifact paths | @owner | TEST | open |  |
| TEST-P3-002 | P3 | The test-requires skip marker is only honored in the first 15 lines; validate_gate_test.sh's marker is dead | @owner | TEST | open |  |
| WH-P3-001 | P3 | No replay/idempotency protection or tests on the notification path (ntfy); Shuffle path retired | @owner | WH | open |  |
