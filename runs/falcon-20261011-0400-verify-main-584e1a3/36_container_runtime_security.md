# 36_container_runtime_security — Prompt 36 - Container Runtime Security Audit

- Run: `falcon-20261009-2117-full-08e20d1`
- Target: `falcon` @ `08e20d1` (branch `main`)
- Domain: `36_container_runtime_security.md` (area CTR, prompt)

## Verification Performed

# Container Runtime Security Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: falcon-20261009-2117-full-08e20d1
- Repository: falcon @ 08e20d1 (branch main), live lab host `falcon`
- Generated at: 2026-10-09T21:44:07Z
- Auditor: subagent (repo-deep-dive full, area CTR)
- Area code: CTR
- Output path: docs/audits/repo-deep-dive/falcon-20261009-2117-full-08e20d1/36_container_runtime_security.md
- Scope limitations: read-only; no container rebuilds, no `compose up`, no image pulls. Live facts were captured with `sudo docker ps/inspect` and the repo's own read-only drift check.

## Scope

Reviewed: the one Dockerfile (compose/central/opensearch-s3.Dockerfile), .dockerignore, all compose trees (compose/central, compose/probe, compose/mct, mct/compose, automation/wazuh), pins/images.lock + supply-chain waivers, config/docker/daemon.json, the image/SBOM/vuln set, deploy scripts that build/run containers, and the live container configuration on the host (27 running containers, 2026-10-09).

Not reviewed: image layers beyond the metadata captured by the repo's scanner, live runtime syscall traces, and any host outside `falcon`.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| compose/central/docker-compose.yml | compose | central stack hardening, healthchecks, ports | 10 services, all images tag@digest |
| compose/probe/docker-compose.yml | compose | SPAN capture stack | suricata host net + explicit caps |
| compose/mct/*, mct/compose/* | compose | adopted vs vendored MCT stacks | adopted = first-party, vendored = archive-only |
| automation/wazuh/multi-node/*.yml | compose | Wazuh stack (running) | no security_opt/healthcheck |
| compose/central/opensearch-s3.Dockerfile | Dockerfile | only image build | root for plugin install; USER 1000 |
| compose/central/.dockerignore | build context | context minimization | only the Dockerfile is in context |
| pins/images.lock, pins/supply-chain-waivers.json | supply chain | digests + explicit waivers | lock generated 2026-09-20 (18 d) |
| config/docker/daemon.json | runtime | log rotation, live-restore, proxy | identical to live /etc/docker/daemon.json |
| sbom/vuln-summary.csv, docs/phase7/IMAGE_SCAN_DISPOSITION.md | scanning | known CVEs + dispositions | scan 2026-09-22; adopted stacks outside disposition |
| automation/validation/container_drift_check.sh + live run | runtime check | running vs declared | 27 running, 26 matched, 0 drift, 1 undeclared |

## Verification Performed

| Check | Command / artifact | Result |
|---|---|---|
| Running vs declared drift | `sudo /home/user/falcon-build/automation/validation/container_drift_check.sh` (read-only) | running=27 declared_services=65 matched=26 undeclared=1; all drift kinds 0; metric written 2026-10-09T21:20:05Z |
| Privilege profile | `sudo docker inspect` over all containers | privileged=0, docker.sock=0, no-new-privileges=11/27, added_caps=3 (suricata, ntopng), all-interface publishers=5 |
| Healthcheck coverage | `docker inspect .Config.Healthcheck` count | 13/27 running containers have a healthcheck |
| Daemon config | `sudo docker info`, `sudo cat /etc/docker/daemon.json` | 29.1.3, live-restore=true, json-file 20m x5, userland-proxy=false, apparmor+seccomp builtin, no userns-remap; live daemon.json identical to repo |
| Build path | `bootstrap/60-central-deploy.sh:56-63` | builds falcon-opensearch-s3 when absent; WARN (not fail) if the built id differs from the pinned digest |
| Unpinned images | lens_deterministic.md DET-P3-003 | 29 unpinned refs, all in the waived mct/compose tree |
| Docker-socket exposure live | drift check + `docker inspect` mounts | 0 live containers mount /var/run/docker.sock |

## Executive Summary

Strengths: the certified central/probe path is genuinely hardened and was verified live — no privileged containers, no docker.sock mounts, digest-pinned images, `no-new-privileges` on the high-value services, `cap_drop: ALL` on vector/prometheus/grafana/ntfy, explicit non-root users, healthchecks on every central/probe service, log rotation and live-restore in the daemon config, a minimal build context, and a scheduled read-only drift check that currently reports zero drift. The declared-vs-running comparison is the strongest container control in the repo.

Risks: the hardening baseline stops at the certified stacks. The adopted first-party stacks that also run on this host — OpenCanary (network-facing decoys), DFIR-IRIS, the Wazuh multi-node stack, cloudflared, and the Wazuh forwarder — run as image-default root with no `no-new-privileges`, no `cap_drop`, and mostly no healthchecks (16/27 containers lack NNP; 14/27 lack healthchecks). The vendored mct/compose tree still contains docker.sock mounts and 29 unpinned refs under a blanket waiver (latent: not running). The local OpenSearch image installs an unpinned plugin as root and only warns on rebuild drift. These are follow-through gaps on a strong base, not failures of the certified path.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Central compose | compose/central/docker-compose.yml | OpenSearch/Grafana/Traefik/vector/ntfy/ntopng/redis/node-exporter | hardened, digest-pinned, healthchecked | low | ntopng intentionally without NNP (capture caps) |
| Probe compose | compose/probe/docker-compose.yml | Suricata + vector edge | hardened, digest-pinned, healthchecked | low | host net by design |
| Adopted MCT | compose/mct/docker-compose.opencanary.yml, compose/mct/iris-web/* | honeypot + IRIS | running, digest-pinned, unhardened | medium | root, no NNP/caps/healthcheck |
| Wazuh stack | automation/wazuh/multi-node/*.yml | Wazuh manager/indexer/dashboard/nginx/cloudflared | running, digest-pinned, unhardened | medium | 0.0.0.0 publishes for agent ports |
| Vendored MCT | mct/compose/* | archive-only import | not running; docker.sock + unpinned | low (latent) | blanket waiver review_by 2026-12-31 |
| Local image | compose/central/opensearch-s3.Dockerfile | OpenSearch + repository-s3 | digest-pinned result; unpinned plugin | low | rebuild mismatch WARN-only |
| Docker daemon | config/docker/daemon.json | logging, live-restore | matches live exactly | low | no userns-remap |
| Scanning/SBOM | sbom/, docs/phase7/IMAGE_SCAN_DISPOSITION.md | CVE + license data | 12 images scanned; 12 pending (waived) | medium | adopted stacks outside disposition |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Dockerfiles | 4 | single 4-line digest-based Dockerfile; USER 1000 restored; minimal context | plugin artifact unpinned; rebuild warn-only | pin plugin or fail closed on rebuild mismatch |
| Compose | 4 | digest-pinned; hardened central/probe; drift-checked live | adopted stacks unhardened | extend baseline to compose/mct + automation/wazuh |
| Build stages | 4 | single stage is appropriate for a plugin add-on | no reproducible-build check | record plugin hash in the image or lock |
| Base images/tags | 4 | all running images tag@digest; lock freshness check passes (18 d) | 29 unpinned refs in waived mct/compose | pin or keep archive-only with an expiring, scoped waiver |
| Package installs | 3 | plugin install only; no dev deps | `opensearch-plugin install` unpinned | version+hash the plugin |
| Non-root users | 3 | explicit users on vector/prometheus/grafana/ntfy; opensearch/iris/wazuh images set uid internally | opencanary/IRIS app/worker/Wazuh manager default to root | run non-root where the image supports it; document exceptions |
| File permissions | 4 | secrets mounted root 0600; read-only config mounts | none material | keep |
| Entrypoints | 4 | no entrypoint overrides that weaken the images | none | keep |
| Health checks | 3 | all central/probe services; iris nginx only | 14/27 running containers have none (adopted stacks) | add healthchecks to adopted stacks |
| Ports | 4 | intentional binds; opencanary on management IP; DOCKER-USER allowlist live | Wazuh 1516/1517/1518 published on 0.0.0.0 (firewall-scoped) | keep matrix reconciled |
| Build args | N/A | none used | none | n/a |
| Runtime env | 4 | env_file/secret files outside the repo; no env literals in compose | env_file injects whole files into container env (SECRET domain) | see SECRET report |

## Detailed Review

### Item: Certified central/probe hardening

- Evidence: compose/central/docker-compose.yml:24-330; compose/probe/docker-compose.yml:22-78; live drift check 2026-10-09.
- What it does: `no-new-privileges` on 11 services, `cap_drop: ALL` on 4, explicit users, healthchecks everywhere, digest pins, resource limits.
- Verification: live inspect confirms user/caps/security_opt match declared (0 drift); 0 privileged, 0 docker.sock.
- Risks: ntopng intentionally runs with NET_ADMIN/NET_RAW/SYS_NICE and no NNP; documented in-compose.

### Item: Adopted MCT/Wazuh stacks

- Evidence: compose/mct/docker-compose.opencanary.yml:29-40; compose/mct/iris-web/docker-compose.yml:25-60; automation/wazuh/multi-node/docker-compose.yml:3-117; live inspect profile.
- What it does: OpenCanary decoys (21/23/3306/1433/8008/9100 bound to the management IP), IRIS case management, Wazuh manager/indexer/dashboard, cloudflared tunnel.
- Current controls: digest-pinned images, network scoping, host firewall + DOCKER-USER allowlist.
- Missing controls: no `security_opt`, no `cap_drop`, no healthchecks, image-default users (root for opencanary/IRIS app/worker/Wazuh manager).
- Risks: a compromise of any of these has default capabilities and root in-container; no healthcheck means the drift check cannot see a wedged service.

### Item: Vendored mct/compose tree

- Evidence: mct/compose/docker-compose.shuffle.yml:48,87; pins/supply-chain-waivers.json:3-10; DET-P3-003.
- Current state: archive-only (mct/VENDORING.md), not running; 29 unpinned refs; docker.sock in the Shuffle backend/orborus services.
- Missing controls: no scoped waiver, no digest pins, no socket removal.

### Item: Local OpenSearch build

- Evidence: compose/central/opensearch-s3.Dockerfile:1-4; bootstrap/60-central-deploy.sh:56-63; pins/images.lock:83-90.
- Current state: digest-pinned result; plugin installed as root; rebuild mismatch is a WARN.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| CTR-001 | Dockerfiles | Dockerfile:1-4 | digest base, USER 1000 | unpinned plugin | P3 | version+hash plugin |
| CTR-002 | Compose | compose/central, compose/probe | hardened | adopted stacks lack baseline | P2 | extend hardening |
| CTR-003 | Build stages | single stage | appropriate | no reproducible check | P3 | record plugin hash |
| CTR-004 | Base images/tags | pins/images.lock | tag@digest, lock freshness gate | 29 waived refs | P3 | scope waiver, pin |
| CTR-005 | Package installs | Dockerfile:3 | batch plugin install | unpinned | P3 | pin artifact |
| CTR-006 | Non-root users | live inspect | 5 explicit users; images default elsewhere | root defaults in adopted stacks | P2 | non-root where possible |
| CTR-007 | File permissions | /srv/falcon/secrets 0600; ro mounts | good | none | - | keep |
| CTR-008 | Entrypoints | compose command/entrypoint | no weakening overrides | none | - | keep |
| CTR-009 | Health checks | compose + live | central/probe all; 13/27 live | 14 missing | P2 | add to adopted stacks |
| CTR-010 | Ports | live ss + matrix | intentional binds + allowlist | 0.0.0.0 agent ports (firewall-scoped) | P3 | keep reconciled |
| CTR-011 | Build args | none | n/a | none | - | n/a |
| CTR-012 | Runtime env | env_file/secret mounts | no literals | whole-file env injection | P2 (SECRET) | per-key secrets |

## Findings

### CTR-P3-001 - Vendored MCT compose still mounts docker.sock and uses unpinned images under a blanket waiver

- Severity: P3
- Confidence: High
- Area: CTR
- Evidence: mct/compose/docker-compose.shuffle.yml:48,87; pins/supply-chain-waivers.json:5-9; lens_deterministic.md:23-44 (DET-P3-003); live drift check 2026-10-09 (0 live docker.sock containers).
- What is happening: unchanged since the prior run. shuffle-backend and shuffle-orborus mount /var/run/docker.sock; the mct/compose tree is waived wholesale (root=mct/compose, ref=*) for digest/pin gates and 29 refs are unpinned. No shuffle container is running; the tree is archive-only.
- Why it matters: an imported tree that is one `compose up` away from granting Docker control to a workflow engine is a standing foot-gun; the blanket waiver also hides any new unpinned ref.
- User / business impact: latent; no live exposure today.
- Security / privacy / reliability impact: container-escape-equivalent capability if ever started; supply-chain drift not visible per ref.
- Recommended fix: remove or justify the socket mounts (socket proxy or rootless), pin images by digest, and replace the blanket waiver with per-ref entries that expire.
- Suggested validation: add a test asserting no `docker.sock` mount in any compose tree outside a documented exception, and that waivers are per-ref with review_by dates.
- Owner suggestion: platform owner.
- Effort estimate: S-M
- Dependencies: Shuffle is not currently deployed; mct/VENDORING.md policy.
- Status: still-open (prior CTR-P3-001)
- Attack path: compromised workflow -> Docker socket -> host root; currently not reachable (not running).

### CTR-P2-001 - Adopted MCT/Wazuh stacks run without baseline container hardening or healthchecks

- Severity: P2
- Confidence: High
- Area: CTR
- Evidence: compose/mct/docker-compose.opencanary.yml:29-40; compose/mct/iris-web/docker-compose.yml:25-60 and docker-compose.base.yml:20; automation/wazuh/multi-node/docker-compose.yml:3-117; live inspect 2026-10-09 (16/27 containers without no-new-privileges; 13/27 with healthchecks; opencanary/IRIS/Wazuh user empty = image default); docs/phase7/IMAGE_SCAN_DISPOSITION.md:91-93; repo audit CONTAINER-P1-001 (docs/audits/repo-deep-dive/20261002-0522-main-67dec27/36_container_runtime_security.md:52).
- What is happening: the central/probe hardening (NNP, cap_drop, users, healthchecks) was not applied to the adopted first-party stacks that run on the same host.
- Why it matters: network-facing honeypot and case-management containers run as root with default capabilities and no NNP; missing healthchecks also make the drift check unable to detect wedged services.
- User / business impact: larger blast radius from any single container compromise; slower detection of service failures.
- Security / privacy / reliability impact: privilege escalation surface inside containers; reduced failure visibility.
- Recommended fix: add `security_opt: [no-new-privileges:true]`, `cap_drop: [ALL]` (plus required caps), non-root users where supported, and healthchecks to compose/mct and automation/wazuh; bring those images into pin/SBOM/vuln scope.
- Suggested validation: extend the existing compose_cap_drop_test.sh pattern to all compose roots; assert NNP/healthcheck presence per service; re-run container_drift_check.
- Owner suggestion: platform owner.
- Effort estimate: M
- Dependencies: image support for non-root; Wazuh/IRIS upgrade windows.
- Status: open (pack-new; same root issue as repo CONTAINER-P1-001 / pack ARCH-P2-001 partially-fixed)
- Attack path: internet/LAN -> opencanary or IRIS vulnerability -> root-in-container with default caps -> lateral movement.

### CTR-P3-002 - Local OpenSearch image installs the repository-s3 plugin as root with no artifact pin; rebuild mismatch is warn-only

- Severity: P3
- Confidence: High
- Area: CTR
- Evidence: compose/central/opensearch-s3.Dockerfile:1-4; bootstrap/60-central-deploy.sh:56-63; pins/images.lock:83-90.
- What is happening: `USER root` + `opensearch-plugin install --batch repository-s3` downloads an unversioned, unverified plugin at build time; the deploy script compares the fresh image id to the pinned digest but only logs a WARN on mismatch.
- Why it matters: the digest pin is only meaningful if the build is reproducible or the mismatch is a failure; a future rebuild can silently produce a different image.
- User / business impact: low; the current running image matches the pin.
- Security / privacy / reliability impact: supply-chain integrity gap on the one local build.
- Recommended fix: install a versioned plugin and record its hash (or bake the plugin at a known release), and make a rebuild/digest mismatch fail closed or require an explicit override.
- Suggested validation: unit test that a deliberately changed Dockerfile produces a non-zero exit in the deploy preflight.
- Owner suggestion: platform owner.
- Effort estimate: S
- Dependencies: OpenSearch plugin distribution.
- Status: open
- Attack path: none identified (build-time only; result digest-pinned).

## Prior-Run Comparison

- CTR-P3-001 (vendored MCT docker.sock + floating tags + blanket waiver): verified still present at 08e20d1; kept with the prior ID, status still-open. Mitigation confirmed: no shuffle containers running, 0 live docker.sock mounts.
- No other prior CTR findings. The repo's own CONTAINER-P1-001/P2-001/P2-002/P3-001 items were reconciled: P2-001 (syslog port on all interfaces) is addressed (probe edge owns 514/15140; firewall-scoped); P3-001 is the prior CTR-P3-001; P2-002 is the new CTR-P3-002; P1-001 remains as CTR-P2-001.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Compromise of an unhardened adopted container | Medium | Medium | High | live profile 16/27 no NNP | CTR-P2-001 |
| Unpinned/waived vendored compose used accidentally | Medium | Low | High | mct/compose + waiver | CTR-P3-001 |
| Silent image rebuild drift | Low | Low | Medium | deploy WARN-only | CTR-P3-002 |
| Known fixable CRITICALs in running images | Medium | Medium | Medium | sbom/vuln-summary.csv (opensearch 14, dashboards 2, vector 3) | patch window; IMAGE_SCAN_DISPOSITION |

## Recommendations

### Immediate / Release Blocking
- None for the certified path; keep the drift check green.

### This Week
- Extend the central/probe hardening baseline to compose/mct and automation/wazuh (NNP + cap_drop + healthchecks).
- Scope the mct/compose waiver per ref and record the docker.sock disposition.

### This Month
- Pin or hash the OpenSearch plugin; make rebuild mismatch fail closed.
- Add the adopted images to pin/SBOM/vuln scope or renew their waivers explicitly.
- Patch-window refresh of the 2026-09-22 scan set.

### Later / Platform Evolution
- Non-root users for adopted images where supported; read-only rootfs trials; seccomp profile review.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Add NNP + healthcheck to opencanary | network-facing service with zero hardening today | compose/mct/docker-compose.opencanary.yml | container_drift_check after recreate |
| Split the blanket waiver | new unpinned refs become visible | pins/supply-chain-waivers.json | compose digest check |
| Remove the two .bak-edge-rules leftovers | avoid accidental deploys from stale files | live tree only | git status |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Adopted-stack hardening | P2 | platform | M | image support |
| Waiver scoping + digest pins | P3 | supply-chain | S | none |
| Plugin pin/reproducible build | P3 | platform | S | none |
| Adopted images into scan scope | P3 | security | M | trivy refresh |

## Suggested Tests

- Extend `automation/validation/tests/compose_cap_drop_test.sh` to assert NNP/healthcheck/cap policy across compose/mct and automation/wazuh.
- Add a negative test asserting no `docker.sock` mount outside a documented exception list.
- Add a rebuild-reproducibility check for the local image (build twice, compare ids) or fail-closed digest binding in bootstrap/60.

## Suggested Documentation Updates

- docs/runbooks/MCT_CONSOLIDATION.md: record the adopted-stack hardening status and exceptions.
- docs/phase7/IMAGE_SCAN_DISPOSITION.md: refresh the 2026-09-22 scan note and adopted-stack scope.
- compose/mct and automation/wazuh: add a hardening header comment mirroring compose/central.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Can IRIS/Wazuh images run non-root without breaking persistence? | non-root is the strongest residual control | image docs or a test recreate |
| Is the Wazuh stack intended to remain outside the certified baseline? | determines whether CTR-P2-001 is a fix or a recorded exception | owner decision/exception register row |
| Will the scan disposition be refreshed before the next patch window? | fixable CRITICALs pending | new sbom/vuln-summary.csv + capture |

## Limitations

- No image rebuild/pull was performed; the Dockerfile analysis is static.
- The live inspect was captured at one instant (2026-10-09 ~21:20-21:35Z) and does not trace runtime behavior.
- Vuln data is the 2026-09-22 scan; counts may have changed upstream.

## Appendix

Live privilege/exposure profile (2026-10-09, read-only):

```
CURRENT containers=27 privileged=0 docker.sock=0 no-new-privileges=11 added_caps=3 all_interface_publishers=5
DELTA containers=+18 privileged=+0 docker.sock=+0 no-new-privileges=+2 undeclared=1
```

No-NNP running containers: ntopng, falcon-wazuh-forwarder, iriswebapp_app/db/worker/rabbitmq, mct-security-stack-opencanary-1, multi-node-* (8), wazuh-cloudflared.
No-healthcheck running containers (14): opencanary, iriswebapp_app/db/worker/rabbitmq, multi-node-* (8).

## Findings

| ID | Severity | Title |
|---|---|---|
| CTR-P3-001 | P3 | Vendored MCT compose still mounts docker.sock and uses unpinned images under a blanket waiver |
| CTR-P2-001 | P2 | Adopted MCT/Wazuh stacks run without baseline container hardening or healthchecks |
| CTR-P3-002 | P3 | Local OpenSearch image installs the repository-s3 plugin as root with no artifact pin; rebuild mismatch is warn-only |
