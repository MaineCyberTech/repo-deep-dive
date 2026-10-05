# Deterministic checks — deterministic

Machine checks (no LLM). Findings use the `DET` area.

## Findings

| ID | Title | Severity |
|---|---|---|
| DET-P3-001 | [GIT] No LICENSE file | P3 |
| DET-P3-002 | [SUPPLY] 58 container image(s) without a digest pin | P3 |
| DET-P3-003 | [SUPPLY] hadolint not available on the check runner (Dockerfile lint skipped) | P3 |
| DET-P3-004 | [DEP] trivy not available on the check runner (dependency vuln scan skipped) | P3 |

## Detail

### Finding ID: DET-P3-001 - [GIT] No LICENSE file

Add a LICENSE or an explicit proprietary review-only notice consistent with the owner decision.

- `git ls-files shows no LICENSE/COPYING/NOTICE`
- `README.md names the owner but grants no license terms`

### Finding ID: DET-P3-002 - [SUPPLY] 58 container image(s) without a digest pin

Pin images by digest (image@sha256:...) for reproducible, tamper-evident deploys, or scope the waiver per ref.

- `mct/compose/docker-compose.greenbone.yml:5 registry.community.greenbone.net/community/vulnerability-tests`
- `mct/compose/docker-compose.misp.yml:43 valkey/valkey:7.2`
- `mct/compose/docker-compose.greenbone.yml:76 registry.community.greenbone.net/community/pg-gvm:stable`
- `pins/supply-chain-waivers.json:5-7 blanket mct/compose waiver review_by 2026-12-31`

### Finding ID: DET-P3-003 - [SUPPLY] hadolint not available on the check runner (Dockerfile lint skipped)

Install hadolint in the deterministic CI job so Dockerfile lint is not a coverage gap.

- `lab runner: actionlint=MISSING hadolint=MISSING trivy=MISSING`

### Finding ID: DET-P3-004 - [DEP] trivy not available on the check runner (dependency vuln scan skipped)

Install trivy in the deterministic CI job so dependency/image scanning is enforced, not skipped.

- `lab runner: trivy=MISSING`
