# 12_infra_deployment_environment_drift — Prompt 12 - Infrastructure, Deployment, and Environment Drift Audit

- Run: `snowride-20261005-full-main-38b34a9`
- Target: `snowride` @ `38b34a9` (branch `main`)
- Domain: `12_infra_deployment_environment_drift.md` (area INFRA, prompt)

## Verification Performed

Infra reviewed: compose, nginx templates, otel config and the committed crontab. The crontab is now version-controlled (OBS-P1-001 fix). Residual: the crontab references host paths and node under /home/user that are not in the repository, and the committed LAUNCH_ATTESTED_COMMIT is a stale revision, so a deploy of HEAD fails the launch gate (intended fail-closed, but the environment identity is not current).

## Findings

| ID | Severity | Title |
|---|---|---|
| INFRA-P3-001 | P3 | Committed host crontab references out-of-repo paths/binaries |
| INFRA-P3-002 | P3 | Committed launch attestation commit is stale versus repository HEAD |
