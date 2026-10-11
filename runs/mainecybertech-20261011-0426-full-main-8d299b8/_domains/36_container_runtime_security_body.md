# Container Runtime Security Audit

## Audit Metadata

- Audit name: repo-deep-dive (full hardening edition)
- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Repository: `MaineCyberTech/mainecybertech` (read-only worktree `/tmp/opencode/mct-audit-target`)
- Branch: `main`
- Commit SHA: `8d299b8d` (`8d299b8dc271c410b9ae2ceeda3d2c6c997af8fd`, 2026-10-11)
- Generated at: 2026-10-11
- Auditor: domain subagent 36 (area code CTR)
- Output path: `docs/audits/repo-deep-dive/mainecybertech-20261011-0426-full-main-8d299b8/36_container_runtime_security.md`
- Scope limitations:
  - Static review only. `docker` is not installed in the audit environment, so no image was built, run, pulled, or scanned; pinned digests were not resolved against a registry; image size and runtime behaviour are `not reproducible`.
  - No droplet or lab access was authorized/used, so "running container configuration vs declared configuration" is `Unknown` (checked repo-side only).
  - No secret values are printed; secret-like config is referenced by `path:line` + type.

## Scope

Reviewed at `8d299b8d`:

- Dockerfiles: `apps/api/Dockerfile`, `apps/web/Dockerfile`, `apps/worker/Dockerfile`
- Compose: `docker-compose.yml` (local/dev), `infra/digitalocean/docker-compose.yml` (prod)
- Build context: `.dockerignore`
- Entrypoints/health: `infra/digitalocean/redis-entrypoint.sh`, `apps/api/src/main.ts`, `apps/worker/src/{consumer-bullmq,consumer-sqs,logger}.ts`, `apps/api/src/lib/logger.ts`
- CI/CD: `.github/workflows/{deploy-do,build-push,e2e,sbom,test}.yml`, `.github/actions/dependency-audit/action.yml`, `.github/dependabot.yml`
- Operator docs: `infra/digitalocean/{README.md,.env.example,Caddyfile*}`, `docs/{SBOM_PROCESS,CI,FINAL_DEPLOYMENT_OPERATIONS_HANDBOOK,ROLLBACK_PROCEDURES}.md`, `SECURITY.md`
- Previous run: `runs/mainecybertech-20261004-full-main-9c0b88c/{follow_up_register,risk_register}.md` (all 10 CTR rows)

Not reviewed: image layers/registry manifests, GitHub environment settings, droplet runtime state, Terraform/cloud-init (domain 12), secret rotation inventory (domain 38).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `apps/api/Dockerfile`, `apps/worker/Dockerfile` | Dockerfile | API/worker build + runtime | 2 stages, digest-pinned `node:20-alpine`, `USER appuser`, `--prod --ignore-scripts`, HEALTHCHECK, npm/corepack removed |
| `apps/web/Dockerfile` | Dockerfile | Web build + runtime | 3 stages, digest-pinned base, `USER nextjs`, standalone bundle, `--chown`, HEALTHCHECK with start-period |
| `docker-compose.yml` | Compose (local) | Dev/e2e stack | e2e profile-gated + password required; repo-wide rw bind mount remains; no caps/limits |
| `infra/digitalocean/docker-compose.yml` | Compose (prod) | Deployed stack (7 services) | `x-security` (cap_drop ALL + no-new-privileges), read_only×5, pids_limit×7, mem_limit, log caps, digest pins |
| `.dockerignore` | Build hygiene | Context reduction / secret exclusion | `.env*` excluded; broad `*.md/*.txt/*.log` still present |
| `infra/digitalocean/redis-entrypoint.sh` | Entrypoint | Redis secret handling | 0600 `/tmp/redis.conf`, password off argv |
| `.github/workflows/deploy-do.yml` | CI/CD (push path) | Build → scan → SBOM → attest → verify → deploy | 3 image scans, attest-sbom, attest-build-provenance, `gh attestation verify` gate, health gate incl. worker |
| `.github/workflows/build-push.yml` | CI/CD (manual) | Reusable build pipeline | same scan/SBOM/attest steps; push triggers removed |
| `.github/dependabot.yml` | Automation | Digest refresh | 5 `docker` entries (root, apps/*, infra/digitalocean) |
| `docs/SBOM_PROCESS.md`, `SECURITY.md` | Docs | Claims about scanning/SBOM/attestation | Image SBOM + attestation documented; third-party images not covered |
| `infra/digitalocean/README.md`, `.env.example`, `docs/FINAL_DEPLOYMENT_OPERATIONS_HANDBOOK.md` | Docs | Declared operator config | Drift found (see finding) |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `grep -c "pids_limit" infra/digitalocean/docker-compose.yml` | static check | CTR-P2-005 | `7` — every prod service has a PID cap (128–256) |
| `grep -n "read_only" infra/digitalocean/docker-compose.yml` | static check | Read-only FS | 5×`true` (api/worker/web/prometheus/alertmanager), 1×`false` (redis, documented), caddy absent |
| `grep -rn "docker.sock\|privileged: true\|/var/run/docker"` (repo, non-node_modules) | static check | Socket/mount privilege | no matches — no docker socket or privileged container anywhere |
| `grep -rn "trivy\|attest\|sbom" .github/` | static check | CTR-P1-001/002/003 | image scans, image SBOMs, `attest-sbom`/`attest-build-provenance`, `gh attestation verify` all present |
| `grep -n "image-ref:" deploy-do.yml build-push.yml` | static check | Scan coverage | only `mct-api`/`mct-worker`/`mct-web` — third-party images unscanned |
| `grep -n "start_period" apps/*/Dockerfile infra/digitalocean/docker-compose.yml docker-compose.yml` | static check | CTR-P3-001 | compose paths set 30s (api/worker); Dockerfile api/worker still lack it; web Dockerfile has 40s |
| `grep -n "E2E_ADMIN_PASSWORD\|profiles" docker-compose.yml .github/workflows/e2e.yml` | static check | CTR-P2-002 | compose requires `${E2E_ADMIN_PASSWORD:?}` and profile-gates e2e; CI workflow still hardcodes `1` for the ephemeral runner-local stack |
| `find apps/api apps/web apps/worker packages -name '*.md' -o -name '*.txt' -o -name '*.log'` | static check | CTR-P3-002 | no matches — broad ignore patterns currently mask nothing needed by builds |
| `grep -rn "hadolint" .github/ package.json scripts/ tools/` | static check | Lint gate | no matches — no Dockerfile lint in CI |
| `grep -n -i "alertmanager\|redis-entrypoint\|metrics-token" infra/digitalocean/README.md` | static check | Docs drift | no matches — README omits services/files that exist in compose |
| `grep -rn ":latest" --include=*.yml --include=Dockerfile* .` | static check | Latest tags | no matches (only the `.env.example` placeholder `IMAGE_TAG=latest`) |
| `git status --porcelain` | safety | Read-only audit | clean — no target changes |

**Exact commands and observed results**

- `cd /tmp/opencode/mct-audit-target && git log -1 --format='%H %s'` → `8d299b8dc271c410b9ae2ceeda3d2c6c997af8fd Merge PR #168: promote develop to main`.
- `find . -iname 'Dockerfile*' -o -iname '*compose*'` → exactly 3 Dockerfiles and 2 compose files (inventory is closed; no stray container files in `templates/`).
- `grep -c pids_limit infra/digitalocean/docker-compose.yml` → `7` (redis 128, api 256, worker 256, web 256, prometheus 256, alertmanager 128, caddy 128).
- `grep -n "read_only" infra/digitalocean/docker-compose.yml` → lines 31 (`false`, redis), 121, 169, 201, 237, 301 (`true`); caddy has none.
- `grep -rn "docker.sock|privileged: true"` → no matches.
- `find apps/api apps/web apps/worker packages -name '*.md' -o -name '*.txt' -o -name '*.log'` (non-node_modules) → empty.
- `grep -n "E2E_ADMIN_PASSWORD" .github/workflows/e2e.yml` → line 168 `E2E_ADMIN_PASSWORD: 1` (ephemeral CI stack only).
- `grep -n "mem_limit" docs/FINAL_DEPLOYMENT_OPERATIONS_HANDBOOK.md` → line 233 says web is 256MB; `infra/digitalocean/docker-compose.yml:199` says `512m` (drift).
- `grep -n "provenance-verification-at-deploy" docs/CI.md` → line 49, the SECURITY.md link anchor exists.
- Runtime verification (`docker build`/`docker inspect`/`trivy image`/`gh attestation verify`) → `not reproducible` (no docker/registry/droplet access).

**Claim verdicts (headline claims in this area)**

| Claim | Source | Verdict |
|---|---|---|
| "every image is scanned with Trivy after build and before deploy" | `SECURITY.md:36-40` | `supported` for the 3 app images; `not applicable` to the 4 third-party images (new finding) |
| "the deploy pipeline verifies that attestation before pulling" | `SECURITY.md:37-44`, `deploy-do.yml:391-515` | `partially supported` — verification is by digest, the droplet then pulls by tag (TOCTOU; new finding) |
| "prod containers drop all capabilities, no-new-privileges, read-only" | `infra/digitalocean/docker-compose.yml:3-7,121,169,201` | `supported` for api/worker/web/prometheus/alertmanager; redis is `read_only:false` (documented) and caddy is writable (new finding) |
| "worker health is fatal to the deploy" | `deploy-do.yml:905-922` | `supported` |
| "redis password is off argv" | `redis-entrypoint.sh:13-21`, compose:42,58 | `supported`; the value remains in the container environment (`docker inspect` for host root) |
| "digest pins are refreshed automatically" | `dependabot.yml:41-92` | `supported` (weekly docker PRs for all four locations) |

## Executive Summary

The container posture remains strong and the previous run's CTR findings are almost entirely fixed at `8d299b8d`: the deploy path (not just the manual build pipeline) scans each app image with Trivy before `up`, generates digest-bound CycloneDX image SBOMs, attests both SBOM and build provenance, and gates the deploy on `gh attestation verify`; Dependabot refreshes all digest pins; redis keeps its password off argv; every prod service has a PID cap; api/worker healthchecks have `start_period` in both compose files; and the worker is now a fatal part of the deploy health gate.

The remaining gaps are narrower: a tag→digest TOCTOU between attestation verification and the droplet pull (P2), the third-party pinned images (redis/caddy/prometheus/alertmanager) never being vulnerability-scanned, caddy running with a writable rootfs and a writable Caddyfile bind mount, prometheus lacking a healthcheck while observability sits outside the deploy gate, image-level api/worker healthchecks still missing `--start-period`, operator docs drifting from the deployed stack (alertmanager omitted from the README; handbook mem_limit stale), and no Dockerfile lint gate. The local dev compose remains intentionally unhardened; its only residual from the previous register is the documented repo-wide rw bind mount (plus a hardcoded ephemeral test password in the CI e2e workflow).

Recommended next actions: (1) make the deploy pull by the verified digest, (2) add a scheduled scan of the four pinned third-party images, (3) `:ro` the Caddyfile and `read_only: true` caddy, (4) add a prometheus healthcheck and include observability in the gate, (5) add hadolint + `--start-period` parity, (6) refresh the infra README/.env.example/handbook.

**Overall Domain Score: 4.1 / 5** (production-ready, hardened runtime; gaps are the TOCTOU window, unscanned third-party images, and a few per-service hardening/documentation items).

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| API image | `apps/api/Dockerfile` | Express API | 2 stages, digest-pinned, `USER appuser`, `--prod --ignore-scripts`, HEALTHCHECK, EXPOSE 4000 | Low | image healthcheck lacks `--start-period` |
| Web image | `apps/web/Dockerfile` | Next.js standalone | 3 stages, digest-pinned, `USER nextjs`, `--chown`, HEALTHCHECK 40s start-period, EXPOSE 3000 | Low | builder stage installs full tree (accepted) |
| Worker image | `apps/worker/Dockerfile` | BullMQ consumer | 2 stages, digest-pinned, `USER appuser`, HEALTHCHECK, EXPOSE 3001 | Low | image healthcheck lacks `--start-period` |
| Prod compose | `infra/digitalocean/docker-compose.yml` | Droplet stack, 7 services | cap_drop ALL + no-new-privileges all; read_only×5; pids_limit×7; mem_limit; json-file log caps; digest pins | Low-Med | caddy writable; prometheus no healthcheck; redis rw documented |
| Local compose | `docker-compose.yml` | Dev/e2e | api/web/worker healthchecks; e2e profile-gated + required password; repo-wide rw mount | Medium (local only) | no caps/read_only/limits by design |
| Redis | prod compose:27-61 + `redis-entrypoint.sh` | Queue backend | digest-pinned, `user: redis`, password-file entrypoint, `REDISCLI_AUTH` healthcheck | Low | password still in env (docker inspect) |
| Caddy | prod compose:310-337 | TLS proxy | digest-pinned, cap_drop ALL + NET_BIND_SERVICE, `caddy validate` healthcheck | Low-Med | not read-only; Caddyfile mount rw |
| Prometheus | prod compose:207-237 | Metrics | digest-pinned, read_only, internal only, metrics-token 0400 | Low-Med | no healthcheck; not in deploy gate |
| Alertmanager | prod compose:244-307 | Alert delivery | digest-pinned, read_only, envsubst-style render, healthcheck | Low | secrets rendered into tmpfs config |
| Build context | `.dockerignore` | Context hygiene | excludes `.env*`, node_modules, docs, tests, infra | Low | broad `*.md/*.txt/*.log` theoretical |
| Image scan | `deploy-do.yml:206-219` etc. | CVE gate | Trivy image CRITICAL/HIGH, exit-code 1, pre-deploy | Low | app images only |
| SBOM | `deploy-do.yml:220-243` etc. + `docs/SBOM_PROCESS.md` | Bill of materials | digest-bound CycloneDX per image + `attest-sbom` | Low | lockfile SBOM retained as secondary |
| Provenance | `deploy-do.yml:391-515` | Supply chain | `attest-build-provenance` + `gh attestation verify` gate | Low-Med | pull-by-tag TOCTOU |
| Deploy | `deploy-do.yml:755-935` | Rollout | health-gated (api/web/worker), auto-rollback, worker fatal | Low | observability outside gate |
| Lint | — | Dockerfile hygiene | no hadolint/build-check gate | Low | manual fixes can regress |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Dockerfiles | 4 | 3 multi-stage, non-root, digest-pinned, prod-only deps | image-level api/worker healthchecks lack `--start-period` | add `--start-period=20s`; add hadolint gate |
| Compose | 4 | prod anchors, read_only×5, limits, log caps | caddy writable rootfs + rw Caddyfile; prometheus no healthcheck | `:ro` mount, `read_only: true`, healthcheck |
| Build stages | 4 | api/worker 2-stage; web deps/builder/runner | web `deps` installs full tree (accepted) | optional prod prune |
| Base images/tags | 4 | all `FROM`/`image` digest-pinned incl. Playwright; no `latest` | third-party digests never scanned | scheduled trivy scan of compose images |
| Package installs | 4 | `--frozen-lockfile`, `--prod --ignore-scripts`, store cleanup | `corepack prepare pnpm@10` floats (packageManager pins 10.34.3) | document; keep |
| Non-root users | 5 | `USER appuser`/`nextjs`; redis `user: redis` | third-party image defaults (caddy root) | consider `user:` where supported |
| File permissions | 4 | `chown`/`--chown`; redis conf 0600; metrics-token 0400 | Caddyfile bind mount is writable | mount `:ro` |
| Entrypoints | 4 | `CMD node …`; redis password-file entrypoint; alertmanager render | none material | maintain |
| Health checks | 4 | app + redis + caddy + alertmanager healthchecks | prometheus none; api/worker image-level start-period | add healthcheck + gate observability |
| Ports | 5 | prod publishes only caddy 80/443; obs expose-only | none | maintain |
| Build args | 5 | only `NEXT_PUBLIC_*` public args | none | maintain |
| Runtime env | 4 | `${VAR:?}` no fallback, `.env` 0600, token 0400 | env visible to host root; tag→digest TOCTOU | pull by verified digest |

## Detailed Review

### Item: API Dockerfile

- Evidence: `apps/api/Dockerfile:1,19,23,26-27,38,44-49,53,58-61`.
- What it does: base stage installs workspace deps for the API, builds `dist`; runtime stage re-installs `--prod --ignore-scripts`, removes npm/corepack/pnpm, creates `appuser` uid 1001, chowns `/app`, sets `USER appuser`, `NODE_ENV=production`, `EXPOSE 4000`, HEALTHCHECK on `/health`.
- Current controls: digest pin, non-root, prod-only deps, dev tooling removed, healthcheck.
- Missing controls: `--start-period` on the image healthcheck; no image-level scan inside the Dockerfile (handled in CI).
- Risks: slow first boot can be counted against healthcheck retries when run outside compose.
- Recommended improvement: add `--start-period=20s`; keep the rest.
- Suggested tests: build + `docker inspect` healthcheck; CI trivy image (exists).

### Item: Web Dockerfile

- Evidence: `apps/web/Dockerfile:1,9-13,16-34,37,45-46,52-57,62-66,68,73-76`.
- What it does: deps → builder (only `NEXT_PUBLIC_*` build args) → runner (standalone, static, public, `--chown=nextjs:nodejs`, `USER nextjs`, 40s start-period healthcheck).
- Current controls: digest pin, non-root, public-only args, telemetry off, npm/corepack removed.
- Missing controls: none material.
- Risks: a future `NEXT_PUBLIC_*` secret would be inlined into the image (documented constraint).
- Recommended improvement: maintain; document the public-arg rule (already in `docs/ENVIRONMENT_VARIABLES.md` family).

### Item: Worker Dockerfile

- Evidence: `apps/worker/Dockerfile:1,18,22,25-26,37,43-48,52-58`.
- Same pattern as API; `/health` on 3001; shutdown handlers in `apps/worker/src/consumer-bullmq.ts:65-66` and `consumer-sqs.ts:116-117`.
- Missing controls: image-level `--start-period`.
- Recommended improvement: add `--start-period=20s`.

### Item: Production compose

- Evidence: `infra/digitalocean/docker-compose.yml:3-7,19-23,27-61,68-128,130-184,186-204,207-237,244-307,310-337`.
- What it does: 7 services; all inherit `cap_drop: ALL` + `no-new-privileges`; api/worker/web/prometheus/alertmanager `read_only: true` with tmpfs; all have `pids_limit`; bounded json-file logs; third-party images digest-pinned; only caddy publishes ports.
- Missing controls: caddy rootfs/Caddyfile writable; prometheus healthcheck; observability not in the deploy gate.
- Risks: persistence/modification via a compromised caddy; silent observability breakage.
- Recommended improvement: caddy `read_only: true` + `tmpfs: /tmp` + `:ro` Caddyfile; prometheus `wget http://localhost:9090/-/healthy`; extend the health gate.
- Suggested tests: `docker compose config` assertions (published ports, read_only, caps); post-deploy prometheus probe.

### Item: Local compose

- Evidence: `docker-compose.yml:2-56,58-88`.
- What it does: builds api/web/worker with `.env.local`, healthchecks with `start_period` for api/worker; e2e is profile-gated (`:63`), requires `E2E_ADMIN_PASSWORD` (`:80`), mounts `.:/app` rw (`:72`).
- Missing controls: no cap_drop/read_only/pids limits (dev-only by design).
- Risks: shared-host misuse; repo-wide mount is the residual of CTR-P2-002.
- Recommended improvement: document local-only status in `README.dev.md`; keep the profile gate.

### Item: CI build/deploy pipeline

- Evidence: `deploy-do.yml:184-380,391-515,537-562,755-935`; `build-push.yml:3-6,49-90`.
- What it does: push to main/develop builds 3 images, scans (CRITICAL/HIGH, exit 1), emits digest-bound SBOMs, attests SBOM+provenance, verifies attestations fail-closed, then deploys over SSH with health gate + rollback.
- Missing controls: pull-by-tag after verification; third-party image scans.
- Risks: registry-write actor can retag between verify and pull.
- Recommended improvement: emit digests from `verify-attestations` and pull/run `image@sha256:…`.

### Item: Redis secret handling

- Evidence: `infra/digitalocean/docker-compose.yml:37,42-44,56-61`; `redis-entrypoint.sh:13-21`.
- What it does: `user: redis`, custom entrypoint writes `/tmp/redis.conf` (umask 077) and execs `redis-server "$CONF"`; healthcheck uses `REDISCLI_AUTH`.
- Missing controls: none for argv; env exposure inherent.
- Risks: `docker inspect` shows `REDIS_PASSWORD` to host root (same trust domain as `/opt/mct-portal/.env`, mode 600).

### Item: Graceful shutdown and stdout logging

- Evidence: `apps/api/src/main.ts:62-79,85-92`; `apps/worker/src/logger.ts:37-47`; `apps/api/src/lib/logger.ts:43-53`.
- What it does: SIGTERM/SIGINT drain with 10s force-exit; pino JSON to stdout in production (`pino-pretty` only in development), with redaction of credentials/PII keys.
- Missing controls: none material for containers.

### Item: Operator documentation

- Evidence: `infra/digitalocean/README.md:9-16,45-51`; `.env.example`; `docs/FINAL_DEPLOYMENT_OPERATIONS_HANDBOOK.md:233`.
- Drift found: alertmanager missing from the service table; supporting files list omits `redis-entrypoint.sh`, `alertmanager.tmpl.yml`, `metrics-token`; handbook mem_limit stale (256MB vs 512m); `.env.example` omits `METRICS_TOKEN`, `ALERTMANAGER_*`, `M365_CLIENT_STATE`, webhook secrets, `MFA_ENFORCEMENT_ENABLED`.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| CTR-001 | Dockerfiles | 3 Dockerfiles | multi-stage, non-root, digest-pinned, prod-only deps | image healthcheck start-period (api/worker) | P3 | add `--start-period`; hadolint gate |
| CTR-002 | Compose | 2 compose files | prod anchors + limits; local dev-only | caddy writable; prometheus healthcheck | P3 | `:ro`/read_only; healthcheck |
| CTR-003 | Build stages | Dockerfiles | api/worker 2-stage, web 3-stage | web deps full tree | P3 | optional prune |
| CTR-004 | Base images/tags | Dockerfiles/compose | all digest-pinned; Dependabot refresh | third-party not scanned | P3 | scheduled image scan |
| CTR-005 | Package installs | Dockerfiles | frozen lockfile, `--prod --ignore-scripts` | none material | — | maintain |
| CTR-006 | Non-root users | Dockerfiles/compose | all app/redis non-root | caddy image default root | P3 | consider `user:` |
| CTR-007 | File permissions | Dockerfiles/deploy | chown/--chown, 0600/0400 files | rw Caddyfile mount | P3 | mount `:ro` |
| CTR-008 | Entrypoints | Dockerfiles/scripts | node CMD; password-file redis; alertmanager render | none material | — | maintain |
| CTR-009 | Health checks | Dockerfiles/compose/deploy | all app services + redis/caddy/alertmanager; worker fatal | prometheus; image start-period | P3 | add healthcheck + gate |
| CTR-010 | Ports | compose | only caddy 80/443 published | none | — | maintain |
| CTR-011 | Build args | web Dockerfile | public-only `NEXT_PUBLIC_*` | none | — | maintain |
| CTR-012 | Runtime env | compose/deploy | `${VAR:?}`; .env 0600; token 0400 | env visible to host root; TOCTOU | P2 | pull by digest |

## Findings

### Finding: No Container Image Vulnerability Scan in CI (CTR-P1-001)

- Severity: P1 · Confidence: High · Area: CTR · Status: verified-fixed
- Evidence: `deploy-do.yml:206-219,273-285,342-354` — Trivy `scan-type: image`, `severity: CRITICAL,HIGH`, `exit-code: "1"`, `ignore-unfixed: true` after each build and before deploy; `build-push.yml:49-62,121-133,202-214` — same in the manual pipeline; `docs/CI.md`/`SECURITY.md:36-40` document it.
- What is happening: each built app image is scanned before it can reach the droplet; a HIGH/CRITICAL (fixed) finding fails the job.
- Why it matters: the previously identified gap (filesystem-only scanning) is closed for the deployed artifacts.
- Recommended fix: keep; extend scanning to third-party images (new finding).
- Suggested validation: seed a known-vuln base in a scratch branch and confirm the gate fails.
- Owner: platform/infrastructure · Effort: — · Dependencies: none
- Status: verified-fixed — re-verified at 8d299b8d: image scans present in both build paths; deploy path is push-triggered (`deploy-do.yml:16-29`).

### Finding: SBOM Is Lockfile-Only, Not an Image SBOM or Attestation (CTR-P1-002)

- Severity: P1 · Confidence: High · Area: CTR · Status: verified-fixed
- Evidence: `deploy-do.yml:220-243,286-305,355-374` — Trivy `format: cyclonedx` against the pushed **digest** + `actions/attest-sbom` with `push-to-registry: true`; `build-push.yml:64-83` etc. emit the artifact; `docs/SBOM_PROCESS.md:1-60` documents both artifacts and the digest binding.
- What is happening: image SBOMs (Alpine OS packages + npm-in-image) are now produced per image, bound to the pushed digest, and attested as OCI referrers.
- Recommended fix: keep; the lockfile SBOM remains a secondary artifact.
- Status: verified-fixed — re-verified at 8d299b8d.

### Finding: Unsigned Images With No Provenance/Attestation (CTR-P1-003)

- Severity: P1 · Confidence: High · Area: CTR · Status: verified-fixed
- Evidence: `deploy-do.yml:244-249,306-311,375-380` — `actions/attest-build-provenance` with `push-to-registry`; `deploy-do.yml:391-515` — `verify-attestations` resolves each tag to a digest and runs `gh attestation verify … --signer-workflow … --source-digest` (fail closed, with an explicit reviewed allow-list for legacy rollbacks); `deploy-do.yml:537-562` — `deploy` `needs:` the verify job and requires `success`.
- What is happening: images are cryptographically bound to this repository's workflow, and a missing/invalid attestation blocks the deploy.
- Recommended fix: keep; close the pull-by-tag TOCTOU (new finding).
- Status: verified-fixed — re-verified at 8d299b8d: the verification gate is real and on the deploy path.

### Finding: Pinned Base-Image Digests Have No Automated Refresh (CTR-P2-001)

- Severity: P2 · Confidence: High · Area: CTR · Status: verified-fixed
- Evidence: `.github/dependabot.yml:41-92` — `package-ecosystem: docker` entries for `/`, `/apps/api`, `/apps/web`, `/apps/worker`, `/infra/digitalocean` (weekly, `target-branch: develop`); pins at `apps/api/Dockerfile:1,26`, `apps/web/Dockerfile:1,37`, `apps/worker/Dockerfile:1,25`, `infra/digitalocean/docker-compose.yml:28,67(local),208,248,311`.
- Status: verified-fixed — re-verified at 8d299b8d.

### Finding: Local Compose Ships Default Credentials and Repo-Wide Bind Mount (CTR-P2-002)

- Severity: P2 · Confidence: High · Area: CTR · Status: partially-fixed
- Evidence: `docker-compose.yml:63` — `profiles: ["e2e"]` keeps the service out of a plain `up`; `:80` — `${E2E_ADMIN_PASSWORD:?set E2E_ADMIN_PASSWORD (the local seed password is 1)}` has no default; `:70-72` — documented repo-wide `.:/app` rw mount remains (harness reads the tree and writes reports/auth state); `.github/workflows/e2e.yml:168` — the CI e2e job still hardcodes `E2E_ADMIN_PASSWORD: 1` for its runner-local ephemeral stack.
- Impact: a shared-host `docker compose up` no longer starts the e2e container and no weak default ships; the mount remains by design.
- Recommended fix: keep the profile + required-variable pattern; document the mount's local-only constraint in `README.dev.md`; consider moving the CI seed password to a secret/env for parity.
- Status: partially-fixed — re-verified at 8d299b8d (residual = repo-wide rw mount + CI hardcode).

### Finding: Redis Password Exposed on Process Argument Vector (CTR-P2-003)

- Severity: P2 · Confidence: High · Area: CTR · Status: verified-fixed
- Evidence: `infra/digitalocean/docker-compose.yml:37` (`user: redis`), `:42` (custom entrypoint), `:58` (`REDISCLI_AUTH="$$REDIS_PASSWORD"` in the healthcheck); `redis-entrypoint.sh:13-21` — `umask 077`, password written to `/tmp/redis.conf`, `exec redis-server "$CONF"`.
- What is happening: the password never appears in argv (`ps`/`docker inspect` args); it travels via environment and a 0600 file on tmpfs.
- Residual: `REDIS_PASSWORD` is still in the container environment (visible to host root via `docker inspect`), inherent to env-injected compose secrets.
- Status: verified-fixed — re-verified at 8d299b8d.

### Finding: Deploy Health Gate Ignores Worker Health (CTR-P2-004)

- Severity: P2 · Confidence: High · Area: CTR · Status: verified-fixed
- Evidence: `infra/digitalocean/docker-compose.yml:174-184` — worker healthcheck on `127.0.0.1:3001/health` with 30s start-period; `deploy-do.yml:835-847` — compose-level gate requires api **and** web **and** worker `healthy` (18 attempts); `deploy-do.yml:905-922` — post-deploy worker probe over SSH fails the job and triggers rollback.
- Status: verified-fixed — re-verified at 8d299b8d.

### Finding: No Container Resource/PID Limits Beyond Memory (CTR-P2-005)

- Severity: P2 · Confidence: High · Area: CTR · Status: verified-fixed
- Evidence: `infra/digitalocean/docker-compose.yml:55,118,166,200,236,300,337` — `pids_limit` on all 7 services (128–256); `mem_limit` on all 7.
- Residual: the local dev compose (`docker-compose.yml`) has no `pids_limit`/`mem_limit` on api/web/worker (dev-only; no fork-bomb blast-radius isolation).
- Status: verified-fixed — re-verified at 8d299b8d.

### Finding: Missing `--start-period` on API and Worker Healthchecks (CTR-P3-001)

- Severity: P3 · Confidence: High · Area: CTR · Status: verified-fixed
- Evidence: `infra/digitalocean/docker-compose.yml:127-128` (api `start_period: 30s`), `:182-184` (worker); `docker-compose.yml:17,56` (local api/worker).
- Residual: the image-level `HEALTHCHECK` in `apps/api/Dockerfile:58` and `apps/worker/Dockerfile:57` still lacks `--start-period` (see new finding).
- Status: verified-fixed — re-verified at 8d299b8d for both compose paths.

### Finding: Broad `.dockerignore` `*.md`/`*.txt`/`*.log` Could Mask Needed Build Files (CTR-P3-002)

- Severity: P3 · Confidence: High · Area: CTR · Status: still-open
- Evidence: `.dockerignore:50-52` — patterns still present; `find apps/api apps/web apps/worker packages -name '*.md' -o -name '*.txt' -o -name '*.log'` (excluding node_modules) returns nothing, and `apps/web/public` contains no `.txt` (favicon/manifest/sw only).
- What is happening: no currently-required build file is masked, so there is no active breakage; the patterns remain a latent trap if a future build/package needs a README/LICENSE `.md`/`.txt` (e.g. a `robots.txt` added to `apps/web/public` would silently vanish from the image).
- Recommended fix: narrow the patterns to known-unneeded paths (e.g. `docs/`, `**/README.md`, `CHANGELOG.md`) or add explicit `!` re-includes for build-relevant files; add a build-time assertion (e.g. `test -f apps/web/public/robots.txt` when present).
- Status: still-open — re-verified at 8d299b8d; carried from the previous register without change.

### Finding: Deploy verifies attestations by digest but pulls and runs images by tag (TOCTOU) (new)

- Severity: P2 · Confidence: Medium · Area: CTR · Status: open
- Evidence: `deploy-do.yml:501-514` — `verify-attestations` resolves `${IMG}:${IMAGE_TAG}` to a digest and verifies that digest; `deploy-do.yml:786-788` — the deploy job then `docker pull`s `${prefix}/mct-<img>:${IMAGE_TAG}` (tag), and `infra/digitalocean/docker-compose.yml:69,131,187` references the images by `${IMAGE_TAG}` tag.
- What is happening: verification and execution resolve the tag independently; an actor with GHCR write access (or a compromised token) could move the tag to a different, unattested digest between the two jobs, and the droplet would run it.
- Why it matters: this is the exact substitution scenario the attestation gate was added for; the gate is bypassable by timing rather than defeated.
- Recommended fix: have `verify-attestations` output each verified digest (`$GITHUB_OUTPUT`), pass them to the deploy job, and pull/run `image@sha256:…` (compose image refs can interpolate `${MCT_API_DIGEST}` etc.), or verify on the droplet immediately before `up`.
- Suggested validation: in a scratch environment, push an image, verify, retag to a second digest, and assert the deploy uses the verified digest only.
- Owner: platform/infrastructure · Effort: S–M · Dependencies: attestation gate (present)
- Status: open — new finding at 8d299b8d.

### Finding: Caddy runs with a writable rootfs and a writable Caddyfile bind mount (new)

- Severity: P3 · Confidence: High · Area: CTR · Status: open
- Evidence: `infra/digitalocean/docker-compose.yml:310-337` — caddy has `cap_drop: ALL` + `NET_BIND_SERVICE` but no `read_only` and no tmpfs; `:320` — `./Caddyfile:/etc/caddy/Caddyfile` (no `:ro`; certs at `:321` are `:ro`); contrast api/web/prometheus/alertmanager which are `read_only: true`.
- What is happening: a process inside the caddy container can write to its rootfs and to the host-side `/opt/mct-portal/Caddyfile`; changes survive restarts and redeploys (the deploy copies the repo Caddyfile only on deploy).
- Why it matters: persistence/modification of the TLS termination config (or injected content served to all users) after any caddy compromise.
- Recommended fix: `- ./Caddyfile:/etc/caddy/Caddyfile:ro`, `read_only: true` + `tmpfs: [/tmp]` (state already lives in the `caddy-data`/`caddy-config` volumes), and consider `user: caddy` if the image supports binding 80/443 with the granted capability.
- Suggested validation: `docker compose config` assertion that the Caddyfile mount ends in `:ro` and caddy has `read_only: true`; attempt a write inside the container and expect failure.
- Owner: platform/infrastructure · Effort: S · Dependencies: none
- Status: open — new finding at 8d299b8d.

### Finding: Prometheus has no healthcheck and observability is outside the deploy health gate (new)

- Severity: P3 · Confidence: High · Area: CTR · Status: open
- Evidence: `infra/digitalocean/docker-compose.yml:207-237` — prometheus has no `healthcheck` key; `deploy-do.yml:835-847` gates only api/web/worker; recent METRICS_TOKEN fixes (`00cb3da6`, `f025e95c`) show the scrape path can silently break while the deploy stays green.
- What is happening: a prometheus container that fails to start/load config, or loses the metrics credential, is not detected by the deploy or rollback logic; `docker compose ps` still reports running.
- Recommended fix: add `healthcheck: wget -qO- http://localhost:9090/-/healthy` (interval 30s, start_period 20s) and either extend the compose health gate or add a post-deploy probe for prometheus/alertmanager/redis/caddy.
- Suggested validation: `docker compose config` healthcheck assertion; deploy test with a deliberately broken `prometheus.yml` and assert the gate fails.
- Owner: platform/infrastructure · Effort: S · Dependencies: none
- Status: open — new finding at 8d299b8d.

### Finding: Image-level HEALTHCHECK for api and worker lacks `--start-period` (new)

- Severity: P3 · Confidence: High · Area: CTR · Status: open
- Evidence: `apps/api/Dockerfile:58` — `HEALTHCHECK --interval=30s --timeout=5s --retries=3`; `apps/worker/Dockerfile:57` — same; `apps/web/Dockerfile:73` — has `--start-period=40s`.
- What is happening: both compose paths override the interval/start-period (`infra/digitalocean/docker-compose.yml:122-128,174-184`; `docker-compose.yml:12-17,51-56`), so the deployed paths are fine, but any `docker run`/other orchestrator uses the image default and can mark a slow-booting container unhealthy and restart it.
- Recommended fix: add `--start-period=20s` to both image healthchecks (parity with web/compose).
- Suggested validation: `docker inspect` the built image's healthcheck config in CI; assert `StartPeriod` is non-zero.
- Owner: platform/infrastructure · Effort: S · Dependencies: none
- Status: open — new finding at 8d299b8d (residual of CTR-P3-001's compose-level fix).

### Finding: infra/digitalocean operator docs and `.env.example` drift from the deployed stack (new)

- Severity: P3 · Confidence: High · Area: CTR · Status: open
- Evidence: `infra/digitalocean/README.md:9-16` — service table omits `alertmanager` (compose:244-307); `:45-51` — supporting files omit `redis-entrypoint.sh`, `alertmanager.tmpl.yml`, `metrics-token`; `infra/digitalocean/.env.example` omits `METRICS_TOKEN`, `ALERTMANAGER_*`, `M365_CLIENT_STATE`, `JIRA_WEBHOOK_SECRET`, `JSM_WEBHOOK_SECRET`, `MFA_ENFORCEMENT_ENABLED` (all referenced by compose:88-92,252-266); `docs/FINAL_DEPLOYMENT_OPERATIONS_HANDBOOK.md:233` — "web … current: 256MB" vs `infra/digitalocean/docker-compose.yml:199` `mem_limit: 512m`.
- What is happening: operators following the README/.env.example under-provision the dead-man's switch and metrics auth, and the OOM runbook points at the wrong limit.
- Recommended fix: update the README table + supporting files, sync `.env.example` with the compose keys, and correct the handbook's mem_limit (cross-ref SECRET-P2-001 for the secret-matrix portion).
- Owner: platform/infrastructure · Effort: S · Dependencies: none
- Status: open — new finding at 8d299b8d.

### Finding: Third-party pinned images are not vulnerability-scanned in CI (new)

- Severity: P3 · Confidence: High · Area: CTR · Status: open
- Evidence: `grep -n "image-ref:" deploy-do.yml build-push.yml` → only `mct-api`/`mct-worker`/`mct-web`; no workflow scans `redis:7-alpine` (`infra/digitalocean/docker-compose.yml:28`), `caddy:2-alpine` (`:311`), `prom/prometheus` (`:208`), `prom/alertmanager` (`:248`); `.github/dependabot.yml:84-92` only refreshes the pins weekly.
- What is happening: a digest that later becomes known-vulnerable can stay in production until a Dependabot PR lands and is merged; nothing gates it.
- Recommended fix: add a scheduled + dispatchable job that pulls the four pinned refs and runs Trivy (`severity: CRITICAL,HIGH`, `exit-code: 1`), reporting via the existing alerting path; keep Dependabot for the bump.
- Suggested validation: run the job against the current digests; seed a known-vuln digest in a scratch branch and assert failure.
- Owner: platform/infrastructure · Effort: S · Dependencies: registry access (public images)
- Status: open — new finding at 8d299b8d.

### Finding: No Dockerfile lint gate in CI (new)

- Severity: P3 · Confidence: High · Area: CTR · Status: open
- Evidence: `grep -rn "hadolint" .github/ package.json scripts/ tools/` → no matches; the earlier manual fixes (web runner `WORKDIR`, `apps/web/Dockerfile:59-62`; shell-form healthchecks) are not guarded, so they can regress unnoticed.
- Recommended fix: add hadolint (SHA-pinned action or container) to the PR/validate gate, plus optional `docker buildx build --check`; keep the existing digest-pin practice.
- Owner: platform/CI owner · Effort: S · Dependencies: none
- Status: open — new finding at 8d299b8d.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Substituted image runs via tag after attestation verified by digest | P2 | Low (needs registry write) | Production RCE under a trusted tag | `deploy-do.yml:501-514` vs `786-788` | Pull by verified digest |
| Known-vulnerable third-party image stays deployed | P3 | Medium | Exposed proxy/queue/services | no scan of compose images | Scheduled trivy scan |
| Caddy compromise persists via writable rootfs/Caddyfile | P3 | Low | TLS/content tampering | `infra/.../docker-compose.yml:310-337` | `:ro` + read_only |
| Silent observability failure ships green | P3 | Medium | Undetected metric/alert outage | prometheus no healthcheck; recent METRICS_TOKEN fixes | Healthcheck + gate |
| Operator under-provisions dead-man's switch from stale docs | P3 | Medium | No off-box alerting | README/.env.example drift | Doc sync |
| Local dev stack used on a shared host | P3 | Low | Repo-wide mount + unhardened services | `docker-compose.yml:58-88` | Document local-only |

## Recommendations

### Immediate / Release Blocking

- None. The P1 findings from the previous run are verified-fixed; the remaining items are hardening, not release-blocking.

### This Week

- Close the tag→digest TOCTOU: emit verified digests from `verify-attestations` and pull/run by digest (`deploy-do.yml:501-514`, `786-788`; compose image refs).
- Add the scheduled/dispatchable Trivy scan for the four third-party pinned images.
- `:ro` the Caddyfile mount and set `read_only: true` + tmpfs for caddy.

### This Month

- Add a prometheus healthcheck and extend the deploy gate/post-deploy probe to observability services.
- Add `--start-period` to api/worker image healthchecks; add a hadolint/build-check CI gate.
- Refresh `infra/digitalocean/README.md`, `.env.example`, and the handbook mem_limit; document the local-vs-prod compose security profile (see docs updates).

### Later / Platform Evolution

- Consider digest-form image references in compose as the steady state for app images (digest resolved by CI).
- Consider running third-party services (caddy) as non-root where the image supports it.
- Add `docker compose config` assertion tests to the PR gate so profile/hardening regressions fail fast.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| `:ro` on the Caddyfile mount | Stops config persistence from inside caddy | `infra/digitalocean/docker-compose.yml:320` | `docker compose config` diff |
| `read_only: true` + tmpfs for caddy | Removes writable rootfs | same file `:310-337` | write attempt fails |
| `--start-period=20s` (api/worker images) | Correct bare-`docker run` health | `apps/api/Dockerfile:58`, `apps/worker/Dockerfile:57` | `docker inspect` StartPeriod |
| Prometheus healthcheck | Catches scrape/config failures | compose `:207-237` | `docker compose ps` healthy |
| README/.env.example/handbook sync | Operators provision the real stack | infra docs | doc review |
| hadolint CI step | Keeps Dockerfile hygiene from regressing | workflow + config | lint passes |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Pull/run by verified image digest | P2 | platform/infrastructure | S–M | attestation gate (present) |
| Third-party image scan job | P3 | platform/infrastructure | S | none |
| Caddy read-only + `:ro` mount | P3 | platform/infrastructure | S | none |
| Prometheus healthcheck + observability gate | P3 | platform/infrastructure | S | none |
| Image-level healthcheck start-period | P3 | platform/infrastructure | S | none |
| Infra docs + `.env.example` sync | P3 | platform/infrastructure | S | none |
| hadolint/build-check CI gate | P3 | platform/CI owner | S | none |
| Local compose profile documentation | P3 | platform/infrastructure | S | none |

## Suggested Tests

- **CI/security**: `docker compose config` assertions — prod publishes only 80/443; e2e remains profile-gated; caddy mount ends in `:ro`; every service has `pids_limit` and `cap_drop: ALL`.
- **CI/security**: hadolint (or `docker buildx build --check`) step on PRs; trivy image scan for the four third-party pins on a schedule.
- **Regression**: assert `HEALTHCHECK` `StartPeriod` is non-zero for all three images (parse `docker inspect` output in CI).
- **Regression**: unset `E2E_ADMIN_PASSWORD` and assert `docker compose config` fails (fail-closed credential requirement).
- **Integration**: SIGTERM the api container mid-request and assert the drain completes (200 for in-flight, then exit 0); worker `/health` returns 503 while draining.
- **Manual validation**: `gh attestation verify oci://ghcr.io/<owner>/mct-api@<digest> --repo <owner>/<repo>` on the deployed digest; retag simulation for the TOCTOU fix.
- **E2E/deploy**: dispatch a dev deploy with a deliberately mismatched digest and assert `verify-attestations` fails closed.

## Suggested Documentation Updates

- `docs/CONTAINER_SECURITY.md` (new): runtime security profile baseline per service — expected `cap_drop`, `no-new-privileges`, `read_only` + tmpfs, `pids_limit`/`mem_limit`, non-root user, why redis is `read_only:false`, why caddy is the only published service, how to run `trivy image`/hadolint locally, and the digest-refresh procedure.
- `infra/digitalocean/README.md`: add alertmanager to the service table; list `redis-entrypoint.sh`, `alertmanager.tmpl.yml`, `metrics-token` under supporting files; state the runtime security profile summary.
- `infra/digitalocean/.env.example`: add `METRICS_TOKEN`, `ALERTMANAGER_*`, `M365_CLIENT_STATE`, `JIRA_WEBHOOK_SECRET`, `JSM_WEBHOOK_SECRET`, `MFA_ENFORCEMENT_ENABLED` with the same "optional/required" semantics as compose.
- `docs/FINAL_DEPLOYMENT_OPERATIONS_HANDBOOK.md:233`: correct web `mem_limit` to 512m.
- `README.dev.md`: explicit local-only caveat for the repo-root compose stack (profile-gated e2e, repo-wide mount, no hardening).
- `docs/CI.md`: document the third-party image scan (once added) and the pull-by-digest change.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Does the running droplet config match `infra/digitalocean/docker-compose.yml` (read_only, caps, limits, mounts)? | Drift check requires live state | `docker compose config` + `docker inspect` on the droplet (not authorized in this audit) |
| Are GHCR tags immutable (package settings), and is there a tag-protection rule? | Determines TOCTOU exploitability window | GHCR package settings / org policy (not in repo) |
| Is `verify-attestations` exercised on every prod deploy (recent green runs)? | "Configured" vs "exercised" | GitHub Actions run history (not available offline) |
| Do the pinned third-party digests resolve and carry no unfixed CRITICAL/HIGH today? | Baseline for the new scan job | `docker buildx imagetools inspect` + `trivy image` (no registry access here) |
| Was the redis 0600 `/data/dump.rdb` permission path re-tested after the `user: redis` change? | Comment cites a 2026-10-03 deploy fix | Droplet restart/upgrade logs |

## Appendix

### Container inventory (closed set at 8d299b8d)

| File | Stage/service | Base image | User | Healthcheck | Ports |
|---|---|---|---|---|---|
| `apps/api/Dockerfile` | api | `node:20-alpine@sha256:fb4cd12c…` | `appuser` (1001) | 30s/5s/3, no start-period | 4000 |
| `apps/web/Dockerfile` | web | `node:20-alpine@sha256:fb4cd12c…` | `nextjs` (1001) | 30s/10s/3, 40s start-period | 3000 |
| `apps/worker/Dockerfile` | worker | `node:20-alpine@sha256:fb4cd12c…` | `appuser` (1001) | 30s/5s/3, no start-period | 3001 |
| `infra/digitalocean/docker-compose.yml` | redis | `redis:7-alpine@sha256:e7723ff7…` | `redis` | REDISCLI_AUTH ping | none |
| ″ | caddy | `caddy:2-alpine@sha256:5f5c8640…` | image default | `caddy validate` | 80/443 |
| ″ | prometheus | `prom/prometheus:v3.5.1@sha256:4b0527…` | image default (nobody) | none | expose only |
| ″ | alertmanager | `prom/alertmanager:v0.28.1@sha256:27c475…` | image default (nobody) | wget `/-/healthy` | expose 9093 |
| `docker-compose.yml` | api/web/worker | built from source | image users | healthchecks (api/worker 30s start-period) | 4000/3000 |
| ″ | e2e | `mcr.microsoft.com/playwright:v1.61.0@sha256:57b65f…` | image default (root) | none (test runner) | none |

### Notes

- `build-push.yml` no longer runs on push (header `:3-6`); `deploy-do.yml` is the authoritative build+scan+attest+deploy path.
- No `privileged: true`, no docker-socket mounts, no host PID/network mode anywhere in the repo.
- The local e2e image and the prod third-party images are digest-pinned; app images are per-release SHA tags resolved+verified at deploy.
