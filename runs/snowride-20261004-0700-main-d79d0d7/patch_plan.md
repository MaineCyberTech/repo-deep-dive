# Patch plan

## SUPPLY-P1-001 - Vulnerable runtime transitive dependency @grpc/grpc-js 1.14.4 with a non-blocking audit gate

Bump @grpc/grpc-js to 1.14.5 (overrides or lockfile refresh), then make the high-severity audit step blocking in both workflows.

## SUPPLY-P2-001 - GitHub Action upload-artifact@v4 not pinned to a commit SHA

Pin line 55 to the same ea165f8d... SHA and add a guard/Dependabot rule preventing tag refs.

## SUPPLY-P2-002 - Container base and CI service images not pinned by digest

Pin every node: and postgres: reference by @sha256 digest, or document a periodic digest-refresh step.

## CI-P2-001 - Supply-chain license/vulnerability workflow is not a required branch-protection check

Add license-and-vulnerability to requiredStatusChecks.contexts and extend verify-branch-protection.mjs to enumerate all workflow files.

## PORT-P3-001 - Six tracked shell scripts lack the executable bit

git update-index --chmod=+x on the six files for consistency.

## SEC-P3-001 - Secret scan allowlists whole files, masking future real secrets

Replace whole-file allowlists with rule/regex-scoped allowlists and periodically re-scan allowlisted files.

## SEC-P3-002 - Metrics token compared non-constant-time and has no rotation path

Use crypto.timingSafeEqual on equal-length buffers and document METRICS_TOKEN rotation in the secret rotation runbook.

## SECRET-P3-001 - Empty service-role key silently disables persistence; no committed rotation evidence

Fail boot/readiness when NODE_ENV=production and the service-role key is empty; commit a dated rotation runbook.

## CI-P3-001 - CODEOWNERS is a personal account; release/hotfix branch rules absent

Replace with an organization team handle and add a release/hotfix ruleset to the declared policy.

## CONF-P3-001 - Residual CRLF files and hadolint DL3025 HEALTHCHECK warnings

git add --renormalize the two files; optionally convert HEALTHCHECK to JSON array form.

