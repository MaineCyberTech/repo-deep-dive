# 36_container_runtime_security — Prompt 36 - Container Runtime Security Audit

- Run: `bench-test-20261013-0819-full-main-b916709`
- Target: `bench-test` @ `b916709` (branch `main`)
- Domain: `36_container_runtime_security.md` (area CTR, prompt)

## Verification Performed

# 36_container_runtime_security - 36_container_runtime_security.md

Domain subagent `36_container_runtime_security` (area CTR), read-only audit of `C:\temp\bench-test`.

## Checks / Evidence

- **P1 - Control-plane and upload bearer tokens are baked into the publicly downloadable live ISO image** (confidence: High)
  - `.github/workflows/build-iso.yml:62-71 - the BENCH_UPLOAD_CONF secret is written to live/private/bench-upload.conf (chmod 600) and baked into the image`
  - `.github/workflows/build-iso.yml:73-82 - the BENCH_AGENT_CONF secret (control-plane join token) is written to live/private/bench-agent.conf and baked into the image`
  - `live/Build-LiveUSB.sh:163-168 - rsync copies the repo tree into the ISO airootfs excluding live/private, but the workflow re-creates live/private before the build`
  - `AGENTS.md:178-182 - 'ISO releases are public downloads - anything baked into the image is world-readable. The control-plane token and the GitHub upload token are baked ... rotate the token if an ISO is shared outside the lab'`
  - `.github/workflows/build-iso.yml:44-45,114-131 - permissions: contents: write and softprops/action-gh-release publishes the ISO parts as public release assets`
  - Impact: Every published release ISO contains a live control-plane join/registration token and, when set, a GitHub upload token. Anyone who downloads the public ISO can extract live/private/*.conf from the squashfs and authenticate to the control plane (registration/operator bearer) or reuse the upload token, and the token does not expire on its own.
  - Recommendation: Stop baking long-lived tokens into the image. Ship a one-time enrollment token (or per-stick credential generated on first boot and exchanged for a short-lived key), inject BENCH_AGENT_CONF at runtime from a mounted config, and add an automatic rotation/deletion step for the build secret after the release. At minimum, gate ISO publishing on a truncated/least-privilege token and document a mandatory rotation on every public release.
- **P2 - CI ISO build runs a --privileged container with the host repository bind-mounted read-write** (confidence: High)
  - `live/ci-build.sh:57-62 - 'docker run --rm --privileged -v "$REPO:/work" -w /work -v "$WORKROOT:/bigwork" ... archlinux:latest'`
  - `live/ci-build.sh:74-85 - the container re-points host symlinks (.venv, live/out-<gpu>) inside the bind-mounted repo, i.e. it writes to the host checkout`
  - `live/ci-build.sh:71 - pacman -Sy runs inside the container pulling arbitrary repo packages`
  - `.github/workflows/build-iso.yml:30-32,53 - runner_labels is operator-selectable and can target a self-hosted runner (comment: 'ubuntu-latest = free for public repos' implies self-hosted is also supported)`
  - Impact: A --privileged container shares the host kernel, devices and (in practice) can escape to host root. Because the whole repository is mounted read-write and the build executes repo-supplied scripts (pacman/PKGBUILD/mkarchiso) as root, a compromised dependency or malicious commit gets effective root on the runner; on a self-hosted runner that is the persistent lab builder. The container also mutates the host checkout (symlink re-points).
  - Recommendation: Drop --privileged; grant only the capabilities actually needed (CAP_SYS_ADMIN + loop/mount for mkarchiso) and use a scoped /dev/loop* passthrough, or run the build on the dedicated Arch runner (build_native path) exclusively. Mount the source read-only and copy into a container-local scratch dir instead of writing back into $REPO; pin the base image by digest (see separate finding).
- **P2 - Unpinned mutable base image tag (archlinux:latest) in the build container** (confidence: High)
  - `live/ci-build.sh:62 - 'archlinux:latest' used as the build environment with no digest pin`
  - `live/ci-build.sh:71 - pacman -Sy --noconfirm then installs archiso/dosfstools/python into that mutable base`
  - Impact: The exact build environment is not reproducible and can change without any repo change: a new 'latest' image or an upstream pacman state can alter or compromise the ISO build silently, and there is no digest recorded to audit what was actually built.
  - Recommendation: Pin the base image by digest (e.g. archlinux@sha256:...) in live/ci-build.sh, or publish a controlled builder image and reference its digest; record the digest in the build log/artifact metadata. Combine with the least-privilege change above.
- **P2 - bench-agent service runs unsandboxed with no runtime hardening profile while executing control-plane shell commands** (confidence: Medium)
  - `server/bench-agent.service:1-17 - no User=, NoNewPrivileges, ProtectSystem, PrivateTmp, CapabilityBoundingSet or SystemCallFilter; runs as root by default`
  - `AGENTS.md:185-186 - 'The remote exec command is a real shell on the runner - it's gated by the operator token; treat it as privileged'`
  - `bench/agent.py:273-274,319-324 - the agent handles 'exec'/'shell' by calling run_exec(...)`
  - `bench/benchreport.py:811 - def run_exec(reporter, cmd, timeout=120, cwd=None) is the raw command runner`
  - `server/benchd.service:14-18 - by contrast benchd ships NoNewPrivileges/PrivateTmp/ProtectSystem/ProtectHome; the agent that actually executes commands has none`
  - Impact: The service that executes operator-supplied shell commands has no container-like confinement (no capability dropping, no filesystem/namespace restrictions), so any compromise of the control-plane token or the agent loop yields unconstrained root on the benchmark host. This is the runtime-hardening gap the domain asks to profile.
  - Recommendation: Add a systemd hardening block to server/bench-agent.service: User=/DynamicUser where feasible, NoNewPrivileges=true, ProtectSystem=strict + ReadWritePaths for the results/work dirs, ProtectHome, PrivateTmp, PrivateDevices (GPU paths need /dev/nvidia* so scope carefully), ProtectKernelTunables/Modules, RestrictSUIDSGID, SystemCallFilter=@system-service, and a CapabilityBoundingSet=~. Run exec jobs in a dedicated, least-privilege worker. Mirror the same profile for the live-USB units.
- **P3 - LXC deployment binds the control plane to 0.0.0.0 despite documented 'LAN/lab address only' posture** (confidence: Medium)
  - `server/benchd.service:11 - ExecStart=/usr/bin/python3 /opt/bench-test/server/benchd.py --host 0.0.0.0 --port 8722`
  - `docs/CONTROL_PLANE.md:208-209 - 'Bind to the LAN/lab address only. On the lab overlay it is reachable over the wgaudit0 WireGuard network'`
  - `docs/CONTROL_PLANE.md:170-185 - the documented deployment is an unprivileged LXC ('--unprivileged 1') running this unit`
  - `server/benchd.py:1439-1440 - at startup it logs 'OPEN (no token)' when no token is configured`
  - Impact: The shipped unit (and the LXC deploy recipe) exposes the control plane on every interface, contradicting the documented LAN-only intent; in an LXC with bridged networking this can reach networks beyond the lab. Combined with the no-token 'OPEN' mode, a misconfigured deploy is remotely reachable.
  - Recommendation: Have the unit bind the documented lab address (or make host configurable via /etc/benchd.conf and default to the overlay address), or add a firewall rule. Document that the 0.0.0.0 bind is intentional only when a host firewall/reverse proxy constrains it; refuse to start when no token is set.

## Verification Performed

Read-only source review of the target at commit `b916709`; the evidence above was
recorded by the domain subagent and normalized by `tools/full_domain.py` (mechanical
report body derived from that recorded findings JSON).

## Findings

| ID | Severity | Title |
|---|---|---|
| CTR-P1-001 | P1 | Control-plane and upload bearer tokens are baked into the publicly downloadable live ISO image |
| CTR-P2-001 | P2 | CI ISO build runs a --privileged container with the host repository bind-mounted read-write |
| CTR-P2-002 | P2 | Unpinned mutable base image tag (archlinux:latest) in the build container |
| CTR-P2-003 | P2 | bench-agent service runs unsandboxed with no runtime hardening profile while executing control-plane shell commands |
| CTR-P3-001 | P3 | LXC deployment binds the control plane to 0.0.0.0 despite documented 'LAN/lab address only' posture |
