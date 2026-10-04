# Follow-up register

| Finding | Severity | Title | Owner | Target | Status | Note |
|---|---|---|---|---|---|---|
| SUPPLY-P1-001 | P1 | Vulnerable runtime transitive dependency @grpc/grpc-js 1.14.4 with a non-blocking audit gate | @owner | SUPPLY | verified-fixed | merged #30 @ cb583a2 |
| SUPPLY-P2-001 | P2 | GitHub Action upload-artifact@v4 not pinned to a commit SHA | @owner | SUPPLY | verified-fixed | merged #31 @ 34347c0 |
| SUPPLY-P2-002 | P2 | Container base and CI service images not pinned by digest | @owner | SUPPLY | verified-fixed | merged #32 @ 4c6e788 |
| CI-P2-001 | P2 | Supply-chain license/vulnerability workflow is not a required branch-protection check | @owner | CI | verified-fixed | merged #34 @ b5d6921 |
| PORT-P3-001 | P3 | Six tracked shell scripts lack the executable bit | @owner | PORT | open | git update-index --chmod=+x on the six files for consistency. |
| SEC-P3-001 | P3 | Secret scan allowlists whole files, masking future real secrets | @owner | SEC | open | Replace whole-file allowlists with rule/regex-scoped allowlists and periodically re-scan allowlisted files. |
| SEC-P3-002 | P3 | Metrics token compared non-constant-time and has no rotation path | @owner | SEC | open | Use crypto.timingSafeEqual on equal-length buffers and document METRICS_TOKEN rotation in the secret rotation runbook. |
| SECRET-P3-001 | P3 | Empty service-role key silently disables persistence; no committed rotation evidence | @owner | SECRET | open | Fail boot/readiness when NODE_ENV=production and the service-role key is empty; commit a dated rotation runbook. |
| CI-P3-001 | P3 | CODEOWNERS is a personal account; release/hotfix branch rules absent | @owner | CI | open | Replace with an organization team handle and add a release/hotfix ruleset to the declared policy. |
| CONF-P3-001 | P3 | Residual CRLF files and hadolint DL3025 HEALTHCHECK warnings | @owner | CONF | open | git add --renormalize the two files; optionally convert HEALTHCHECK to JSON array form. |
