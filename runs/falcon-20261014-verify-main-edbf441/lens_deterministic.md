# Deterministic checks - falcon

Machine checks (no LLM). Findings use the repo-deep-dive `DET` area.

## Findings

| ID | Title | Severity |
|---|---|---|
| DET-P2-001 | [PORT] CRLF committed for 1 file(s) (index has CRLF) | P2 |
| DET-P3-002 | [SEC] gitleaks not installed (secret scan skipped) | P3 |
| DET-P3-003 | [SUPPLY] 29 container image(s) without a digest pin | P3 |
| DET-P3-004 | [SUPPLY] hadolint not installed (Dockerfile lint skipped) | P3 |

## Detail

### Finding ID: DET-P2-001 - [PORT] CRLF committed for 1 file(s) (index has CRLF)

Committed line endings are CRLF, which breaks Linux CI (shell scripts, hash checks). Add `.gitattributes` with `* text=auto eol=lf`, then renormalize (`git add --renormalize .`).

Evidence:

- `evidence/raw/REVIEW-FIX/20261013T053408Z_ci-p3-002-stale-workflow-cleanup.out`

### Finding ID: DET-P3-002 - [SEC] gitleaks not installed (secret scan skipped)

Install gitleaks in CI to enable the secret scan.

### Finding ID: DET-P3-003 - [SUPPLY] 29 container image(s) without a digest pin

Pin images by digest (`image@sha256:...`) for reproducible, tamper-evident deploys.

Evidence:

- `mct/compose/docker-compose.shuffle.yml:112 opensearchproject/opensearch:3.2.0`
- `mct/compose/docker-compose.dfir-iris.yml:13 postgres:16-alpine`
- `mct/compose/docker-compose.dfir-iris.yml:27 redis:7-alpine`
- `mct/compose/docker-compose.misp.yml:14 mariadb:10.11`
- `mct/compose/docker-compose.misp.yml:43 valkey/valkey:7.2`
- `mct/compose/docker-compose.misp.yml:61 ghcr.io/misp/misp-docker/misp-modules:latest`
- `mct/compose/docker-compose.velociraptor.yml:14 velociraptor:latest`
- `mct/compose/docker-compose.otel.yml:7 otel/opentelemetry-collector-contrib:0.118.0`
- `mct/compose/docker-compose.phase2.yml:17 alpine:3.20`
- `mct/compose/docker-compose.greenbone.yml:5 registry.community.greenbone.net/community/vulnerability-tests`
- `mct/compose/docker-compose.greenbone.yml:13 registry.community.greenbone.net/community/notus-data`
- `mct/compose/docker-compose.greenbone.yml:20 registry.community.greenbone.net/community/scap-data`
- `mct/compose/docker-compose.greenbone.yml:27 registry.community.greenbone.net/community/cert-bund-data`
- `mct/compose/docker-compose.greenbone.yml:34 registry.community.greenbone.net/community/dfn-cert-data`
- `mct/compose/docker-compose.greenbone.yml:44 registry.community.greenbone.net/community/data-objects`

### Finding ID: DET-P3-004 - [SUPPLY] hadolint not installed (Dockerfile lint skipped)

Install hadolint to lint Dockerfiles in --deep mode.

