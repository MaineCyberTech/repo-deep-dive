# Deterministic checks - mainecybertech-20261014-0033-full-main-7dd0402

Machine checks (no LLM). Findings use the repo-deep-dive `DET` area.

## Findings

| ID | Title | Severity |
|---|---|---|
| DET-P3-001 | [SEC] gitleaks not installed (secret scan skipped) | P3 |
| DET-P3-002 | [SUPPLY] 3 container image(s) without a digest pin | P3 |

## Detail

### Finding ID: DET-P3-001 - [SEC] gitleaks not installed (secret scan skipped)

Install gitleaks in CI to enable the secret scan.

### Finding ID: DET-P3-002 - [SUPPLY] 3 container image(s) without a digest pin

Pin images by digest (`image@sha256:...`) for reproducible, tamper-evident deploys.

Evidence:

- `infra/digitalocean/docker-compose.yml:82 ${MCT_API_IMAGE:-${GHCR_IMAGE_PREFIX:-ghcr.io/mainecybertech/mainecybertech}/mct-api:${IMAGE_TAG:?IMAGE_TAG must be set}}`
- `infra/digitalocean/docker-compose.yml:160 ${MCT_WORKER_IMAGE:-${GHCR_IMAGE_PREFIX:-ghcr.io/mainecybertech/mainecybertech}/mct-worker:${IMAGE_TAG:?IMAGE_TAG must be set}}`
- `infra/digitalocean/docker-compose.yml:233 ${MCT_WEB_IMAGE:-${GHCR_IMAGE_PREFIX:-ghcr.io/mainecybertech/mainecybertech}/mct-web:${IMAGE_TAG:?IMAGE_TAG must be set}}`

