# 36_container_runtime_security — Prompt 36 - Container Runtime Security Audit

- Run: `falcon-20261011-0416-full-f5cb7c9`
- Target: `falcon` @ `f5cb7c9` (branch `main`)
- Domain: `36_container_runtime_security.md` (area CTR, prompt)

## Verification Performed

# Container Runtime Security Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: falcon-20261011-0416-full-f5cb7c9
- Repository: falcon @ f5cb7c9 (branch main), live lab host `falcon`
- Generated at: 2026-10-11T04:40:00Z
- Auditor: subagent (repo-deep-dive full, area CTR)
- Area code: CTR
- Output path: docs/audits/repo-deep-dive/falcon-20261011-0416-full-f5cb7c9/36_container_runtime_security.md
- Scope limitations: read-only; no container rebuilds, no `compose up`, no image pulls. Live facts were captured with `sudo docker ps/inspect` and the repository's own read-only drift checks. The repo's `container_drift_check.sh` and `live_image_pin_check.sh` were executed without `--metric`, so no files were written to the live host.

## Scope

Reviewed at f5cb7c9: the one Dockerfile (compose/central/opensearch-s3.Dockerfile), compose/central (10 services), compose/probe (2 services), compose/mct (opencanary + iris-web), automation/wazuh multi-node compose (6 services + cloudflare/forwarder helpers), the vendored mct/compose tree (archive-only), pins/images.lock + pins/supply-chain-waivers.json, config/docker/daemon.json, sbom/ coverage, the image scan disposition, and the deploy scripts that build/run containers. Live state: all 27 running containers on the host (2026-10-11 04:20Z).

Not reviewed: image layers beyond scanner metadata, live syscall traces, the Wazuh manager VM 101 internals, and any host outside `falcon`.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| compose/central/docker-compose.yml | compose | central hardening baseline | 10 services, all tag@digest; 10x no-new-privileges, 4x cap_drop ALL, users set, healthchecks everywhere |
| compose/probe/docker-compose.yml | compose | SPAN capture stack | suricata host-net + cap_add; both services nnp; healthchecks present |
| compose/mct/docker-compose.opencanary.yml | compose | adopted canary stack | digest-pinned image; no user/security_opt/healthcheck |
| compose/mct/iris-web/*.yml | compose | adopted IRIS stack | digest-pinned images; no user/security_opt/healthcheck (base + override) |
| automation/wazuh/multi-node/docker-compose.yml | compose | adopted Wazuh stack | digest-pinned images; no security_opt/healthcheck; image-default users |
| mct/compose/docker-compose.shuffle.yml | compose | vendored (archive-only) | docker.sock mounts at lines 48, 87 |
| compose/central/opensearch-s3.Dockerfile | Dockerfile | only image build | base digest-pinned; USER root only for plugin install; returns to USER 1000 |
| compose/central/.dockerignore | build context | context minimization | allowlist: `*` then `!opensearch-s3.Dockerfile` |
| pins/images.lock, pins/supply-chain-waivers.json | pins/waivers | supply-chain scope | adopted MCT/Wazuh images now digest-locked; vuln scans pending with waiver to 2026-12-31 |
| config/docker/daemon.json + live /etc/docker/daemon.json | runtime | logging/live-restore | byte-identical |
| sbom/*.cdx.json | SBOM | adopted-image coverage | 25 CycloneDX files incl. IRIS/OpenCanary/Wazuh/cloudflared |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `sudo docker ps` + `docker inspect` (all 27 containers) | live | declared-vs-running profile | 0 privileged, 0 docker.sock, 11 with no-new-privileges, healthchecks on 13/27 |
| `automation/validation/container_drift_check.sh` (read-only, no --metric) | repo check | declared vs live config | all declared containers OK; 1 undeclared (falcon-wazuh-forwarder); no drift |
| `automation/validation/live_image_pin_check.sh` (read-only) | repo check | running images vs lock | 27/27 OK, drift=0 |
| sha256 daemon.json compare | live | runtime config drift | identical |
| docker.sock mount scan across all containers | live | privilege exposure | 0 mounts |

## Executive Summary

The first-party central and probe stacks remain well hardened and are now live-hardened too: every central/probe container runs with `no-new-privileges` (plus `cap_drop: ALL` on the four services that declare it), explicit users where the image supports it, healthchecks, digest-pinned images, and a matching read-only drift check reports zero drift and zero image-pin drift across all 27 running containers. The OpenSearch local-build Dockerfile remains the only Dockerfile; it is base-digest-pinned and returns to `USER 1000`, but still downloads the repository-s3 plugin unpinned and the deploy script only warns on a rebuild/digest mismatch (CTR-P3-002).

The two structural gaps from the prior run persist: the adopted MCT/Wazuh stacks (OpenCanary, IRIS, the Wazuh multi-node stack, and the docker-run Wazuh forwarder) still carry no baseline hardening (no `no-new-privileges`, no `cap_drop`, no explicit non-root user, no healthchecks), and the vendored Shuffle compose still mounts `docker.sock` under a blanket waiver. The adopted images have moved into pin+SBOM scope at this commit (lock entries and CycloneDX files exist; vulnerability scans are pending under a waiver to 2026-12-31). Live exposure of the socket mounts remains latent: 0 running containers mount docker.sock and mct/compose is archive-only per mct/VENDORING.md.

Recommended next actions: add `security_opt: [no-new-privileges:true]`, `cap_drop: [ALL]` (+ needed caps), non-root users where supported, and healthchecks to compose/mct/* and automation/wazuh/multi-node/*; scope the mct/compose waiver per ref or remove the socket mounts; pin the OpenSearch plugin artifact and fail closed on rebuild mismatch.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Dockerfile | compose/central/opensearch-s3.Dockerfile | local OpenSearch + repository-s3 | base digest-pinned; root only for install | Low/Medium | plugin unpinned; rebuild warn-only |
| Compose: central | compose/central/docker-compose.yml | central platform | hardened, digest-pinned, healthchecked | Low | 10 services |
| Compose: probe | compose/probe/docker-compose.yml | SPAN capture | hardened (suricata cap_add by design) | Low | 2 services |
| Compose: adopted MCT | compose/mct/*.yml | OpenCanary + IRIS | no security_opt/healthcheck/user | Medium | in lock+SBOM now; vuln scan pending |
| Compose: Wazuh | automation/wazuh/multi-node/*.yml | Wazuh multi-node | no security_opt/healthcheck; image-default users | Medium | digest-pinned |
| Helper: forwarder | automation/wazuh/forwarder-install.sh | docker-run alert forwarder | digest-pinned image; no nnp/healthcheck; undeclared in compose | Low | falcon-wazuh-forwarder |
| Vendored | mct/compose/docker-compose.shuffle.yml | Shuffle (staged) | docker.sock mounts; blanket waiver | Low (latent) | archive-only |
| Runtime daemon | config/docker/daemon.json | log rotation/live-restore | identical live | Low | json-file 20m x5 |
| Pins | pins/images.lock + waivers | supply chain | adopted images locked; vuln pending | Medium | waiver review_by 2026-12-31 |
| SBOM | sbom/ | provenance | 25 cdx.json incl. adopted images | Low | vuln JSONs older (2026-09-22) |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Dockerfiles | 3 | opensearch-s3.Dockerfile digest-pinned base, USER 1000 | plugin unpinned; warn-only rebuild mismatch | pin plugin artifact; fail closed on mismatch |
| Compose | 3 | central/probe hardened; adopted stacks not | adopted stacks lack baseline | add nnp/cap_drop/user/healthcheck |
| Build stages | 3 | single-stage minimal build | no multi-stage needed but no cache discipline | acceptable; document |
| Base images/tags | 4 | all running images digest-pinned (27/27) | cloudflared:latest floating tag (digest-pinned) | prefer version tag |
| Package installs | 3 | only repository-s3 plugin | unpinned plugin download as root | versioned artifact + hash |
| Non-root users | 3 | explicit users on 7 central/probe services | 16 containers run image-default users | add users where supported |
| File permissions | 4 | .dockerignore allowlist; secrets via env_file/mounts | none material | - |
| Entrypoints | 4 | stock entrypoints; redis command hardened | - | - |
| Health checks | 3 | 13/27 healthchecked (all central/probe) | adopted stacks + forwarder none | add healthchecks |
| Ports | 4 | declared ports match live; canary bound to mgmt IP | - | - |
| Build args | N/A | no build args used | - | - |
| Runtime env | 4 | secrets via /srv/falcon/secrets env_file + docker secrets | none material | - |

## Detailed Review

### Item: Central/probe stacks
- Evidence: compose/central/docker-compose.yml:26-332; compose/probe/docker-compose.yml:21-78; live inspect.
- What it does: 12 first-party services (platform + capture).
- Current controls: nnp on all; cap_drop ALL on vector/prometheus/grafana/ntfy; explicit users; healthchecks; digest pins; memory limits; live matches declared (drift check OK).
- Missing controls: ntopng intentionally lacks nnp (cap_add NET_ADMIN/NET_RAW/SYS_NICE documented); no read-only rootfs anywhere.
- Recommended improvement: consider `read_only: true` + tmpfs for stateless services (grafana, ntfy, prometheus).
- Suggested tests: extend container_drift_check to assert read-only rootfs if adopted.
- Suggested docs: docs/runbooks note on container hardening profile.

### Item: Adopted MCT/Wazuh stacks
- Evidence: compose/mct/docker-compose.opencanary.yml:29-48; compose/mct/iris-web/docker-compose.base.yml:18-30 + docker-compose.yml:24-58; automation/wazuh/multi-node/docker-compose.yml:3-202; live inspect (nnp=null for 16 containers).
- What it does: deception (OpenCanary), DFIR case management (IRIS), SIEM (Wazuh), forwarder.
- Current controls: digest-pinned images; IRIS nginx runs as www-data; indexers/dashboard run as image users; memory limits on some.
- Missing controls: nnp, cap_drop, healthchecks, explicit users for app/db/rabbitmq/manager; forwarder has no hardening at all.
- Risks: image-default root with no nnp is a lateral-movement amplifier if any adopted service is exploited; no healthchecks means silent degradation.
- Recommended improvement: add the central-stack baseline to these compose files; add a healthcheck for each long-running service; add nnp where caps allow.
- Suggested tests: extend container_drift_check.sh declared trees to require nnp on these services; add a compose lint test.
- Suggested docs: docs/runbooks/MCT_CONSOLIDATION.md hardening section.

### Item: Vendored Shuffle compose (archive-only)
- Evidence: mct/compose/docker-compose.shuffle.yml:48,87; pins/supply-chain-waivers.json:5-9; mct/VENDORING.md.
- Current controls: not deployed (0 docker.sock mounts live); blanket waiver with review_by 2026-12-31.
- Missing controls: per-ref waiver scope; no socket proxy.
- Recommended improvement: remove/justify socket mounts; scope waiver per ref; or record the archive-only status as the accepted control with a dated review.
- Suggested tests: the existing waiver expiry test; add a "not deployed" assertion.
- Suggested docs: mct/VENDORING.md.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| CTR-001 | Dockerfiles | opensearch-s3.Dockerfile:1-4 | digest base, USER 1000 | plugin unpinned, warn-only rebuild | P3 | versioned artifact + fail closed |
| CTR-002 | Compose (central/probe) | compose/central, compose/probe | full hardening baseline | none material | - | read-only rootfs consideration |
| CTR-003 | Build stages | single-stage | minimal context | - | - | - |
| CTR-004 | Base images/tags | 27/27 digest-pinned live | strong | cloudflared:latest tag | P3 | version tag |
| CTR-005 | Package installs | Dockerfile:3 | only one plugin | unpinned download as root | P3 | pin + hash |
| CTR-006 | Non-root users | live profile | 11/27 explicit | 16 image-default | P2 | set users where supported |
| CTR-007 | File permissions | .dockerignore; mounts | allowlist; ro mounts | - | - | - |
| CTR-008 | Entrypoints | compose files | stock | - | - | - |
| CTR-009 | Health checks | live 13/27 | all central/probe | adopted stacks + forwarder | P2 | add healthchecks |
| CTR-010 | Ports | live bindings match declared | management-IP canary binding | - | - | - |
| CTR-011 | Build args | none | - | - | - | - |
| CTR-012 | Runtime env | env_file/docker secrets | no secrets in images | - | - | - |

## Findings

### CTR-P2-001 - Adopted MCT/Wazuh stacks run without baseline container hardening or healthchecks

- Severity: P2
- Confidence: High
- Area: CTR
- Evidence:
  - `compose/mct/docker-compose.opencanary.yml:29-48` (no user/security_opt/healthcheck)
  - `compose/mct/iris-web/docker-compose.base.yml:18-30`, `compose/mct/iris-web/docker-compose.yml:24-58` (no hardening/healthcheck)
  - `automation/wazuh/multi-node/docker-compose.yml:3-202` (no security_opt/healthcheck)
  - `automation/wazuh/forwarder-install.sh:27-31` (docker run, no --security-opt/--user/--health-cmd)
  - Live: `sudo docker inspect <all>` 2026-10-11: 27 running, 0 privileged, 0 docker.sock, nnp=null for 16 containers, healthchecks 13/27
  - `pins/images.lock:100-160` + `sbom/*.cdx.json`: adopted images are digest-locked and SBOM'd; vuln scans pending per `pins/supply-chain-waivers.json` (review_by 2026-12-31)
- What is happening: the first-party central/probe baseline (nnp, cap_drop, users, healthchecks) was never applied to the adopted MCT/Wazuh services.
- Why it matters: adopted services handle hostile input (canary decoys, IRIS case data, Wazuh telemetry) yet run with more privilege and less supervision than the rest of the stack.
- User / business impact: a compromise of an adopted service has a larger blast radius; silent service degradation is not detected.
- Security / privacy / reliability impact: no privilege-escalation barrier (nnp) on 16 containers; no health-based restart for 14 of 27.
- Recommended fix: add `security_opt: ["no-new-privileges:true"]`, `cap_drop: [ALL]` (+ needed caps), explicit users where images support them, and healthchecks to compose/mct/* and automation/wazuh/multi-node/*; harden the forwarder run flags; refresh vuln scans and retire the waiver.
- Suggested validation: extend `automation/validation/container_drift_check.sh` to require nnp for these services; add a compose hardening test (like `compose_cap_drop_test.sh`) for the adopted trees.
- Owner suggestion: platform/security
- Effort estimate: M
- Dependencies: image capability review (some Wazuh/IRIS images may need caps or specific users)
- Status: still-open
- Endpoint / data path: n/a (container runtime)
- Attack path: exploited adopted service -> no-nnp escalation -> host/network lateral movement (composition with CHAIN-P3-001)

### CTR-P3-001 - Vendored MCT compose still mounts docker.sock and uses unpinned images under a blanket waiver

- Severity: P3
- Confidence: High
- Area: CTR
- Evidence:
  - `mct/compose/docker-compose.shuffle.yml:48,87` (/var/run/docker.sock mounts)
  - `pins/supply-chain-waivers.json:5-9` (blanket root=mct/compose ref=* waiver, review_by 2026-12-31)
  - `mct/VENDORING.md` (staged, not deployed)
  - Live: 0 docker.sock mounts in the 27 running containers (docker inspect scan)
- What is happening: the vendored Shuffle compose (archive-only) still declares docker.sock mounts and unpinned refs under a blanket waiver.
- Why it matters: if the vendored tree is ever deployed as-is, a compromised Shuffle backend gains host-root-equivalent docker access.
- User / business impact: latent; no live exposure today.
- Security / privacy / reliability impact: latent container-escape path.
- Recommended fix: remove/justify the socket mounts (socket proxy or rootless), scope the waiver per ref with an expiry, or record archive-only status as the explicit accepted control.
- Suggested validation: existing waiver expiry test + a "not deployed" assertion.
- Owner suggestion: platform
- Effort estimate: S
- Dependencies: owner decision on the vendored tree (EVOL-P1-002)
- Status: still-open
- Attack path: deploy vendored Shuffle -> docker.sock -> host root

### CTR-P3-002 - Local OpenSearch image installs the repository-s3 plugin as root with no artifact pin; rebuild mismatch is warn-only

- Severity: P3
- Confidence: High
- Area: CTR
- Evidence:
  - `compose/central/opensearch-s3.Dockerfile:1-4` (FROM digest; USER root; `opensearch-plugin install --batch repository-s3`; USER 1000)
  - `bootstrap/60-central-deploy.sh:48-63` (artifact URL + sha256 documented; rebuild logs WARN on digest mismatch, no failure)
  - `pins/images.lock:83-90` (falcon-opensearch-s3 digest)
- What is happening: the plugin is downloaded unpinned at build time; a rebuild that produces a different image only warns.
- Why it matters: a supply-chain compromise of the plugin URL or an unintended rebuild silently changes the running image.
- User / business impact: low probability, high impact (OpenSearch is the data platform).
- Security / privacy / reliability impact: build-time supply-chain integrity gap; weak fail-closed behavior.
- Recommended fix: install a versioned plugin artifact and verify the recorded sha256 during build; make a rebuild/digest mismatch fail closed unless an explicit override is set.
- Suggested validation: build test asserting the plugin hash; a negative test for mismatch handling.
- Owner suggestion: platform
- Effort estimate: S
- Dependencies: none
- Status: still-open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Adopted stack compromise escalates (no nnp) | P2 | Medium | High | 16 containers nnp=null | add nnp/cap_drop/users |
| Silent degradation of adopted services | P2 | Medium | Medium | 14/27 without healthchecks | add healthchecks |
| Latent docker.sock exposure in vendored tree | P3 | Low | High | shuffle compose:48,87 | remove mounts / scope waiver |
| Plugin rebuild drift | P3 | Low | Medium | Dockerfile:3; 60-central-deploy.sh:56-63 | pin artifact; fail closed |

## Recommendations

### Immediate / Release Blocking
- None (no live privilege or exposure finding at this commit).

### This Week
- Add nnp + cap_drop + healthchecks to compose/mct/* and automation/wazuh/multi-node/* (CTR-P2-001).

### This Month
- Pin the OpenSearch plugin artifact and fail closed on rebuild mismatch (CTR-P3-002).
- Scope or retire the mct/compose waiver; remove/justify socket mounts (CTR-P3-001).
- Refresh image vulnerability scans and retire the vuln_scan_pending waiver entries.

### Later / Platform Evolution
- Read-only rootfs + tmpfs for stateless central services.
- Version-tag cloudflared instead of `:latest`.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Add `security_opt: [no-new-privileges:true]` to adopted compose services | removes privilege-escalation path | compose/mct/*.yml, automation/wazuh/multi-node/*.yml | container_drift_check.sh |
| Add healthchecks to the 5 IRIS services + canary + wazuh manager/dashboard | detects silent failure | same | `docker compose config` + live inspect |
| Add `--security-opt no-new-privileges --user` to the forwarder run | small blast-radius reduction | automation/wazuh/forwarder-install.sh | reinstall + inspect |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Adopted-stack baseline hardening | P2 | platform | M | image capability review |
| Plugin artifact pin + fail-closed rebuild | P3 | platform | S | - |
| Waiver scoping / socket removal | P3 | platform | S | EVOL-P1-002 owner decision |
| Vuln scan refresh for adopted images | P2 | security | S | trivy refresh |

## Suggested Tests

- Unit: compose lint test asserting `security_opt`/`cap_drop`/healthcheck on adopted services.
- Integration: extend `container_drift_check.sh` declared sources to require nnp for adopted stacks.
- E2E: rebuild the OpenSearch image and assert the pinned plugin hash; negative test for mismatch.
- CI: add a Dockerfile lint (hadolint is currently not installed; DET-P3-005).
- Security: periodic `live_image_pin_check.sh` remains the running-image gate (0 drift now).
- Manual: verify adopted services still function after adding users/cap_drop (Wazuh indexer needs memlock ulimits, IRIS needs its entrypoint user).

## Suggested Documentation Updates

- docs/runbooks/MCT_CONSOLIDATION.md: hardening baseline for adopted services.
- docs/phase7/IMAGE_SCAN_DISPOSITION.md: refresh scope to include adopted images once scans land.
- compose/mct README: document why nnp/healthchecks were added.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Do Wazuh/IRIS images support `cap_drop: ALL` with their required caps? | determines the achievable baseline | container test |
| Is the vendored Shuffle tree ever intended to be deployed? | decides remove-vs-waiver for the socket mounts | owner decision (EVOL-P1-002) |
| When will the next trivy refresh land? | closes the vuln_scan_pending waiver | scan artifacts |

## Appendix

- Live container profile (2026-10-11 04:20Z): 27 running; 0 privileged; 0 docker.sock; 11 with no-new-privileges; 13 with healthchecks; added caps: suricata/ntopng (NET_ADMIN, NET_RAW, SYS_NICE), ntfy (NET_BIND_SERVICE).
- `container_drift_check.sh` output: all declared containers OK; undeclared: falcon-wazuh-forwarder.
- `live_image_pin_check.sh` output: containers=27 drift=0.
- Certification comparison (P7-G01): CERT containers=9 nnp=9 -> CURRENT containers=27 nnp=11.

## Findings

| ID | Severity | Title |
|---|---|---|
| CTR-P2-001 | P2 | Adopted MCT/Wazuh stacks run without baseline container hardening or healthchecks |
| CTR-P3-001 | P3 | Vendored MCT compose still mounts docker.sock and uses unpinned images under a blanket waiver |
| CTR-P3-002 | P3 | Local OpenSearch image installs the repository-s3 plugin as root with no artifact pin; rebuild mismatch is warn-only |
