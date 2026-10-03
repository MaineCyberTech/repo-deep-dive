# Container Runtime Security Audit

## Audit Metadata

- Audit name: repo-deep-dive · Run: `20260930-0701-falcon-8282d3f_edge-45dfed0` (full-domain) · Area code: CTR
- Repository: `falcon-build` @ `8282d3f` (working tree modified: REVIEW-FIX evidence + this run's `docs/audits/`) · Cross-repo: `falcon-edge-build` @ `f1c5def` (moved `45dfed0`→`f1c5def` during the run; CI-only delta)
- Generated at: 2026-09-30 · Auditor: wave-1 subagent (prompt 36) · Output: `docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/36_container_runtime_security.md`
- Scope limitations: no root, not in `docker` group → no `docker ps/inspect`; running config derived from compose, host units, `/srv/falcon/textfile/falcon_metrics.prom` and `live_snapshot.txt`; non-derivable items marked unverified; no image pulls/scans.

## Scope

Reviewed: `compose/central`, `compose/probe`, `compose/mct/*`, `mct/compose/*`, `automation/wazuh/*` compose + `forwarder-install.sh`, the local `opensearch-s3.Dockerfile`, pins/SBOM/vuln artifacts, host systemd execution paths, DOCKER-USER policy, and the live container census. Not reviewed: upstream image internals, other hosts (VM 101/103), live container filesystems, active config diff (no Docker access).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `compose/central/docker-compose.yml` | compose | Certified stack (10 services) | Pinned, healthchecks, `no-new-privileges`, limits, Docker secret |
| `compose/probe/docker-compose.yml` | compose | Probe stack | Suricata host net + caps; syslog ports |
| `compose/mct/{opencanary,iris-web}` | compose | Running MCT containers | Canary publishes 21/23/3306/1433/9100/8008 |
| `mct/compose/*` | compose | Imported stacks (not running) | `:latest` tags; Shuffle mounts docker.sock |
| `automation/wazuh/multi-node/docker-compose*.yml`, `forwarder-install.sh` | compose/code | Running Wazuh stack + forwarder | Tag-only `wazuh/*:4.14.7`; `python:3.12-alpine` |
| `compose/central/opensearch-s3.Dockerfile` | Dockerfile | Only local build | `repository-s3` installed at build |
| `ci/validate.py:77-104`; `pins/images.lock` | CI/provenance | Pin enforcement | Scans `compose/**` only; Wazuh/forwarder absent |
| `config/systemd/*.service`; live `systemctl cat falcon-*` | runtime | Root execution paths | ExecStart under `/home/user/*` (both repos) |
| `bootstrap/31-docker-user-firewall.sh`; `falcon.nft` | firewall | Published-port policy | mgmt/admin return-all, else DROP |
| `falcon-edge-build/image/overlay/usr/local/sbin/falcon-apply-update.sh`; `deploy/*.service|.path` | edge | Privileged apply | Trusts agent request |
| `evidence/raw/P7-G01/20260921T020201Z_phase7-security-checks.out:10-13` | evidence | Prior hardening claim | 9 containers: 0 privileged/docker.sock |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| Compose `@sha256` refs vs pins lock (local script) | reproduced | Digest drift | All `compose/**` digest refs match the 18 lock entries |
| Running census from `falcon_container_cpu_percent{name=…}` | reproduced | Runtime vs declared | 27 names; service-level match (10 central + 2 probe + 5 IRIS + 1 canary + 7 Wazuh + cloudflared + forwarder) |
| `systemctl cat` all `falcon-*` (central + edge) | reproduced | Root trust input | Root units execute user-writable repo scripts |
| `git log 45dfed0..f1c5def`; history of `falcon-apply-update.sh` | reproduced | Binding | Apply script unchanged since `38f42b4` |
| `python3 ci/validate.py` | reproduced | Gate state | Pin/ledger/evidence PASS; secret scan FAIL on this run's docs (SECRET-P3-010) |
| `docker ps` / digest re-verify | not reproducible | Live drift | No socket → CTR-P2-005 |

## Prior-Run Findings Verification

| Prior ID | Status | Evidence at current commits |
|---|---|---|
| REV-P1-005 (update-apply root trust) | **still-open** | Apply script unchanged; request path/sha256 agent-written → CTR-P1-002 |
| INTG-P2-003 (secrets in release surface) | **still-open** | Delivery backups + manifest hashes unchanged → SECRET-P1-003 |
| INTG-P1-003 (edge PKI backup local-only) | **still-open** | No offsite path for edge secrets → SECRET-P1-003 |
| P7-G01 hardening claim | **scope-stale** | Certified 9 containers (2026-09-21); 27 run now → CTR-P2-004 |

## Executive Summary

The certified central and probe stacks are genuinely hardened for a lab (digest pins, healthchecks, `no-new-privileges` with two documented exceptions, resource limits, internal backend network, file-mounted secrets, DOCKER-USER allowlist). The estate has outgrown that certification: 27 containers run now, including the migrated Wazuh stack, DFIR-IRIS and OpenCanary, whose image pins and privileges were never brought into the pin/SBOM/hardening process (CTR-P2-003/004). The sharpest runtime issue is host-side: root systemd jobs execute scripts from user-writable repositories, so compromise of the single operator account becomes root (CTR-P1-001); the same account can self-authorize the edge update path (CTR-P1-002). Drift detection is evidence-based, not measured: no routine running-vs-declared check, and the last digest verification predates pin changes (CTR-P2-005). Next: relocate root-run code, root-side verify updates, extend pin/SBOM/scan to all running stacks, add a drift capture.

## Inventory

| Item | Path / symbol | Purpose | State | Risk | Notes |
|---|---|---|---|---|---|
| Central stack | `compose/central/docker-compose.yml` | 10 services | Running 10/10 | Medium | Pinned, healthchecks |
| Probe stack | `compose/probe/docker-compose.yml` | suricata, vector-edge | Running 2/2 | Medium | 514/15140 published |
| IRIS | `compose/mct/iris-web/*` | Case management (5) | Running | Medium | No healthchecks; env secrets |
| OpenCanary | `compose/mct/docker-compose.opencanary.yml` | Deception (1) | Running | Medium | 6 fake services all-interfaces |
| Wazuh multi-node | `automation/wazuh/multi-node/*` | 7 containers | Running | Medium | Tag-only images |
| Cloudflared / forwarder | `.../docker-compose.cloudflare.yml`, `forwarder-install.sh` | Tunnel; alert forwarding | Running | Medium/Low | `latest@sha256`; unpinned python |
| MCT app stacks | `mct/compose/*` | shuffle/misp/velociraptor/greenbone/otel | Not running | Medium | `:latest`; docker.sock (Shuffle) |
| Edge apply path | `falcon-edge-build/.../falcon-apply-update.sh` | Root apply/rollback | Deployed | High | Trusts agent request |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Dockerfiles | 3 | Digest base; USER root→1000; no secrets | No `.dockerignore`; plugin at build | Document build; pin plugin |
| Compose | 4 | Pinned/hardened certified stacks | Unchecked trees; no cap_drop/read_only | Extend checks; add caps |
| Build stages | 3 | Single-stage plugin install | Rebuild reproducibility unverified | Lock plugin version |
| Base images/tags | 3 | 18 pins, 12 SBOMs | Wazuh/forwarder absent; floating tags in mct | Pin + SBOM all running |
| Package installs | 3 | Trivy per pinned image; disposition doc | Not owner-closed/stale | Rescan; close OD-17 record |
| Non-root users | 3 | 4 services set `user:` | New stacks default root | Add `user:` where possible |
| File permissions | 2 | Read-only secret mounts | Root runs user-writable code | Move scripts root-owned |
| Entrypoints | 3 | Explicit commands; bounded restarts | No init/tini | Evaluate `init: true` |
| Health checks | 4 | All 12 certified services; gauge 0 | None on IRIS/Wazuh/canary | Add checks |
| Ports | 3 | DOCKER-USER allowlist | Canary all-interfaces; 1516/1517 any-source | Document exposure |
| Build args | 2 | No secret args | Local build inputs uncaptured | Record build inputs |
| Runtime env | 3 | env_file from root-only stores | Env visible to root inspect | Prefer file mounts |

## Detailed Review

### Item: Privileged systemd execution surface (CTR-P1-001)
- Evidence: `config/systemd/*.service`; live `systemctl cat` central falcon-* + edge metrics/secrets-backup/operator-cert units. Timers run root jobs whose ExecStart lives in `user:user 775` repo trees; missing controls: root-owned code path, unit hardening, in-repo unit sources; fix: `/usr/local/libexec/falcon*`, harden, commit units; test/docs: CI ownership check, `HOST_SERVICE_HARDENING.md`.

### Item: Edge update-apply trust boundary (CTR-P1-002)
- Evidence: `deploy/falcon-update-apply.{path:7,service:5}`, `falcon-apply-update.sh:42-44,66-80,90-96`, `runner.py:444-527`. Root script re-hashes/extracts the file the unprivileged agent names; missing: root-side signature/pin, path constraint, tar member-type filter; fix/test: root-side verify + `filter="data"`, forged/symlink negatives; docs: `update-rollback.md`.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| CTR-001 | Root services run repo scripts | `config/systemd/*` | Root-owned units | User-writable code | P1 | Move to `/usr/local/libexec` |
| CTR-002 | Update-apply trusted input | apply script refs | Agent-side signature | Self-attested request | P1 | Root-side verification |
| CTR-003 | Image provenance | `ci/validate.py:83-85`; Wazuh compose | Lock for `compose/**` | Wazuh/forwarder unmanaged | P2 | Pin all, extend check |
| CTR-004 | Privilege profile of live set | compose caps; P7-G01 | Certified 9 | 27 running; no cap_drop/read-only | P2 | Re-run hardening review |
| CTR-005 | Drift detection | metrics; evidence | Post-reboot health | No digest/mount diff | P2 | Routine drift capture |
| CTR-006 | Vuln disposition | `IMAGE_SCAN_DISPOSITION.md` | Trivy + thresholds | Not owner-closed; stale | P3 | Reconcile + rescan |
| CTR-007 | Local build supply chain | Dockerfile | Digest base | Plugin unpinned; no ignore | P3 | Document/pin plugin |
| CTR-008 | Health checks | compose | Certified services covered | New stacks lack | P3 | Add checks |
| CTR-009 | Ports/exposure | canary compose; firewall | Allowlist + DROP | Canary all-interfaces | P3 | Document intent |
| CTR-010 | Non-root runtime | compose `user:` | 4 services | New stacks root | P3 | Add `user:` |
| CTR-011 | Build args/secrets | compose scan | No literals/args | — | — | Keep |
| CTR-012 | Runtime env/secrets | env_file/mounts | Root-only stores | Env inspectable by root | P3 | Prefer file mounts |

## Findings

### Finding ID: CTR-P1-001 - Root systemd services execute code from user-writable repository trees
- Severity: P1 · Confidence: High · Area: CTR
- Evidence: `config/systemd/falcon-backup.service` (`ExecStart=/home/user/falcon-build/bootstrap/85-backup-job.sh`, no `User=` → root); live units `falcon-alert-relay`, `falcon-metrics`, `falcon-disk-guard`, `falcon-service-probe`, `falcon-heartbeat`, `falcon-docker-user-firewall`, and edge `falcon-edge-metrics.service` (`User=root`), `falcon-edge-secrets-backup.service`, `falcon-edge-operator-cert.service`; trees are `user:user 775`, `/home/user` is `750`.
- What is happening: timers/oneshots run root jobs whose executables are writable by the account they should be insulated from.
- Why it matters: the owner credential file (`/home/user/.env`, contains the sudo password) shares that account; compromise yields root on the next timer without a prompt.
- User / business impact: full host compromise from a single account.
- Security / privacy / reliability impact: root code execution; destructive backup/firewall actions possible.
- Recommended fix: install ExecStart scripts to root-owned `/usr/local/libexec/falcon*/` (0755); add `NoNewPrivileges`/`ProtectSystem=strict`/minimal `ReadWritePaths`; commit unit sources under `config/systemd/`.
- Suggested validation: CI/test failing when a root unit points under `/home`; reboot drill after relocation.
- Owner suggestion: Central host owner + edge maintainer · Effort estimate: M · Dependencies: None · Status: open
### Finding ID: CTR-P1-002 - Privileged update-apply path trusts an agent-writable request (REV-P1-005)
- Severity: P1 · Confidence: High · Area: CTR
- Evidence: `deploy/falcon-update-apply.path:7` watches `/var/lib/falcon-agent/updates/apply-request.json`; `…service:5` runs the apply script as root; `falcon-apply-update.sh:42-44` reads agent-written `path`/`sha256`, `:66-72` hashes the named file, `:76-80` `extractall` without `filter="data"` (only absolute/`..` names rejected), `:90-96` swaps the package and restarts; `runner.py:498-527` writes the request with a self-computed digest, Ed25519 verification is agent-side only (`runner.py:444-469`).
- What is happening: the root transaction re-verifies only that the file matches the digest the unprivileged agent wrote; it never consults the signed manifest/pinned digest and accepts any path and tar member type.
- Why it matters: the mechanism meant to protect the agent can be subverted by the agent (the threat model's base case).
- User / business impact: fleet-integrity mechanism untrustworthy; rollback equally affected.
- Security / privacy / reliability impact: root-level abuse on sensor devices.
- Recommended fix: root-side verification against a root-owned signed manifest/pinned digest; constrain `path` to the updates dir; `tarfile.extractall(filter="data")`; reject links/devices; check ownership; consider a dedicated apply user.
- Suggested validation: negative tests for forged path, forged digest, symlink/device members (must reject, no swap).
- Owner suggestion: Edge maintainer · Effort estimate: M · Dependencies: Existing signed-manifest format · Status: still-open
### Finding ID: CTR-P2-003 - Running stacks outside image pin/SBOM enforcement
- Severity: P2 · Confidence: High · Area: CTR
- Evidence: `ci/validate.py:83-85` scans only `compose/**`; `automation/wazuh/multi-node/docker-compose.yml:4,53,91,117,139,161` use `wazuh/wazuh-{manager,indexer,dashboard}:4.14.7` (tag only, absent from the 18-entry lock); `forwarder-install.sh:31` runs `python:3.12-alpine`; `docker-compose.cloudflare.yml` uses `cloudflare/cloudflared:latest@sha256:…`; `mct/compose/docker-compose.{misp,velociraptor,greenbone}.yml` use `:latest`.
- What is happening: images added after Phase-7 certification run unpinned/unscanned in the same daemon.
- Why it matters: provenance and CVE posture of much of the running estate is unknown; a registry tag move silently changes code.
- User / business impact: monitoring/IR integrity depends on unmanaged images.
- Security / privacy / reliability impact: supply-chain compromise and unpatched CVEs undetected.
- Recommended fix: extend `check_compose_pins` to every repo `*.yml` (explicit excludes); pin Wazuh/forwarder digests; add to lock/SBOM/Trivy; drop floating tags.
- Suggested validation: validate fails on an unpinned fixture; SBOM/vuln-summary lists added images.
- Owner suggestion: Build agent + MCT owner · Effort estimate: M · Dependencies: Registry access · Status: open
### Finding ID: CTR-P2-004 - Live privilege/exposure profile outgrew the container hardening certification
- Severity: P2 · Confidence: Medium · Area: CTR
- Evidence: `compose/central/docker-compose.yml:252-255` ntopng caps `NET_ADMIN/NET_RAW/SYS_NICE`; `compose/probe/docker-compose.yml` suricata `network_mode: host` + caps; `compose/central/docker-compose.yml:287,292-294` node-exporter `pid: host`, `/:/host:ro,rslave`; `compose/mct/docker-compose.opencanary.yml` publishes 21/23/3306/1433/9100/8008 all-interfaces while `bootstrap/31-docker-user-firewall.sh` returns mgmt/admin traffic to every published port; `mct/compose/docker-compose.shuffle.yml:48,87` mounts docker.sock (not running); `P7-G01/…phase7-security-checks.out:10-13` certified 9 containers, 0 privileged/docker.sock; metrics show 27 now; no `cap_drop`/`read_only` anywhere.
- What is happening: the hardening review covered the certified estate; migrated/imported stacks were never checked for privileged mode, socket mounts or capabilities.
- Why it matters: unknown privileges on containers handling external telemetry; no baseline to detect regression.
- User / business impact: a compromised container may have more host reach than intended.
- Security / privacy / reliability impact: escape/DoS surface; canary exposure intentional but undocumented.
- Recommended fix: re-run and capture the privileged/docker.sock/no-new-privileges sweep across all 27; add `cap_drop: [ALL]`/`read_only`/`tmpfs` to new stacks where supported; document canary exposure.
- Suggested validation: captured sweep + alert on new privileged containers.
- Owner suggestion: Central owner · Effort estimate: S · Dependencies: Docker access · Status: open
### Finding ID: CTR-P2-005 - No routine running-vs-declared drift check; digest evidence stale
- Severity: P2 · Confidence: Medium · Area: CTR
- Evidence: `falcon_metrics.prom` exposes only cpu/mem per container (no digest/mount/privilege); last digest verification evidence `P1-G04/20260920T230718Z_verify-digests.out` (2026-09-20), lock changed since (ntopng repin); `post_reboot_verify.sh` counted "containers healthy: 13" (2026-09-28) vs 27 now; audit account `docker ps` → permission denied.
- What is happening: drift is inferred from a human-run script; the running estate is larger than any capture covers; running digests cannot be confirmed.
- Why it matters: tag moves, manual `docker run` additions (e.g. forwarder) or container edits go unnoticed.
- User / business impact: declared configuration loses credibility over time.
- Security / privacy / reliability impact: unauthorized/unpinned workloads run undetected.
- Recommended fix: root-run read-only drift capture diffing `docker inspect` digests/mounts/privileged flags against lock/compose; expose a metric and alert; weekly evidence.
- Suggested validation: induce a mismatch in a test env; alert fires.
- Owner suggestion: Central owner · Effort estimate: M · Dependencies: Docker access · Status: open
### Finding ID: CTR-P3-006 - Image vulnerability disposition not closed and partly stale
- Severity: P3 · Confidence: High · Area: CTR
- Evidence: `sbom/vuln-summary.csv` (2026-09-22) e.g. grafana 104 fixable HIGH, opensearch 61/14, vector 82/3, ntopng 95/1; `docs/phase7/IMAGE_SCAN_DISPOSITION.md:4` still says OD-17 confirmation requested and its ntopng row predates the digest repin; `OWNER_ACCEPTANCE.md:20` records OD-17 accepted 2026-09-22 while `OWNER_DECISIONS.json` says `PENDING`.
- What is happening: scanning exists but disposition records no longer match pins/decisions.
- Why it matters: operators cannot tell whether accepted risk is current; agents may re-litigate closed decisions.
- User / business impact: patch-planning friction.
- Security / privacy / reliability impact: fixable CVEs accepted ambiguously.
- Recommended fix: reconcile OD-17 append-only; update the disposition to current pins; re-run `vuln-summary.sh`; add acceptance dates.
- Suggested validation: disposition references current lock digests and scan hash.
- Owner suggestion: Central owner · Effort estimate: S · Dependencies: Trivy (present) · Status: open
### Finding ID: CTR-P3-007 - Local image build: plugin fetched at build; no `.dockerignore`
- Severity: P3 · Confidence: Medium · Area: CTR
- Evidence: `compose/central/opensearch-s3.Dockerfile` (`FROM …@sha256:…`, `USER root`, `opensearch-plugin install --batch repository-s3`, `USER 1000`); resulting image in lock/compose (`falcon-opensearch-s3:2.19.6@sha256:07e7…`); no `.dockerignore` in the repository.
- What is happening: the only first-party image fetches its plugin from the network; build inputs are not captured in the lock.
- Why it matters: clean-host rebuild reproducibility is unproven; a rebuild could pull a different plugin artifact.
- User / business impact: rebuild risk (known theme).
- Security / privacy / reliability impact: low-probability supply-chain variance.
- Recommended fix: record the plugin version/digest in the bootstrap step; add `.dockerignore`; document rebuild and verify the produced digest.
- Suggested validation: clean rebuild digest equals lock.
- Owner suggestion: Build agent · Effort estimate: S · Dependencies: None · Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Operator account → root via root-run repo scripts | P1 | Medium | Critical | CTR-P1-001 | Relocate code; harden units |
| Compromised agent self-authorizes update as root | P1 | Medium | High | CTR-P1-002 | Root-side verify; tar filter |
| Unmanaged images (Wazuh/forwarder) | P2 | Medium | High | CTR-P2-003 | Pin + scan + lock |
| Unknown privileges in new stacks | P2 | Medium | High | CTR-P2-004 | Re-run hardening sweep |
| Undetected runtime drift | P2 | Medium | Medium | CTR-P2-005 | Drift capture + metric |

## Recommendations

### Immediate / Release Blocking
1. CTR-P1-002: root-side signed-manifest/pinned-digest verification + `filter="data"` + forged-request negative tests before any fleet update rollout.

### This Week
2. CTR-P1-001: relocate root ExecStart scripts to root-owned paths; add unit hardening; record in decision log. 3. CTR-P2-004: capture the privileged/docker.sock/no-new-privileges sweep across all 27 containers.

### This Month
4. CTR-P2-003: pin Wazuh/forwarder images; extend the pin check to all compose paths; add to SBOM/Trivy. 5. CTR-P2-005: implement the drift capture/metric/alert. 6. CTR-P3-006: reconcile and re-run the vulnerability disposition.

### Later / Platform Evolution
7. CTR-P3-007 + scorecard gaps: `.dockerignore`, `cap_drop`/`read_only`/`init`, healthchecks for IRIS/Wazuh/canary. 8. Evaluate rootless/userns-remap for non-certified stacks (canary excluded intentionally).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Move root scripts to `/usr/local/libexec/falcon/` | Breaks user→root chain | `config/systemd/*.service` | Unit run after `daemon-reload` |
| `extractall(filter="data")` | Blocks symlink/device members | `falcon-apply-update.sh` | Crafted-tarball unit test |
| Extend pin-check glob | Finds unpinned images | `ci/validate.py` | Fails on fixture |
| `cap_drop: [ALL]` for headerless services | Shrinks privileges | compose files | compose config + smoke |
| Document canary exposure | Separates intent from drift | opencanary compose/runbooks | Doc review |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Root-owned systemd execution paths | P1 | owner | M | — |
| Update-apply root-side verification | P1 | edge maintainer | M | — |
| Pin/SBOM Wazuh + forwarder images | P2 | build agent | M | registry |
| Full container hardening sweep | P2 | owner | S | docker |
| Drift capture metric + alert | P2 | owner | M | docker |
| Vuln disposition reconciliation | P3 | owner | S | trivy |
| `.dockerignore` + plugin version | P3 | build agent | S | — |
| Healthchecks for IRIS/Wazuh/canary | P3 | owner | S | upstream |

## Suggested Tests

- CI: pin-check over `automation/**`/`mct/compose/**`; root-unit ExecStart ownership check.
- Unit: update-apply negatives (forged path/digest, symlink/device members, oversized bundle).
- Security: privileged/socket/no-new-privileges sweep across all running containers.

## Suggested Documentation Updates

- `docs/runbooks/HOST_SERVICE_HARDENING.md` (new): root unit ownership, hardening, drift capture.
- `docs/phase7/IMAGE_SCAN_DISPOSITION.md`: reconcile OD-17 and pins.
- `pins/README.md`: scope all compose paths.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Do running containers differ from declared images/mounts? | Core drift question | `docker inspect` capture (authorized) |
| Is the Wazuh stack production or transitional? | Pin/scan urgency | owner roadmap |

## Appendix

- Running census (metrics, 2026-09-30T13:50Z; 27): 10× `falcon-central-*`, 2× `falcon-probe-*`, 5× `iriswebapp_*`, `mct-security-stack-opencanary-1`, 7× Wazuh multi-node, `wazuh-cloudflared`, `falcon-wazuh-forwarder`.
- Central gate state: `ci/validate.py` pinning/ledger/evidence PASS; secret-scan FAIL (2 `long_hex` in this run's reports) — see `38_env_secret_rotation.md` SECRET-P3-010.
