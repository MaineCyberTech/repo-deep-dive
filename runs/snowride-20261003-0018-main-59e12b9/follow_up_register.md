# Follow-up register

Owner/Target/Status columns drive tools/collect_findings.py enrichment.

| ID | Severity | Title | Owner | Target | Status | Post-audit note |
|---|---|---|---|---|---|---|
| CI-P1-001 | P1 | No evidence of branch protection or required status checks on `main` |  |  | partially-fixed | Draft PR #8: branch protection declared as code + consistency test in foundation; live GitHub protection remains operator action (token lacks administration:read) |
| DATA-P1-001 | P1 | Attested migration head (0055) is one behind the repository head (0056) |  |  | partially-fixed | Draft PR #7; de-hardcoded release identity + crypto-attested owner signature; verify.log clean worktree 5f4ee0b |
| FINAL-P1-001 | P1 | Release trust is assembled from self-asserted and stale identities |  |  | partially-fixed | Draft PR #7; de-hardcoded release identity + crypto-attested owner signature; verify.log clean worktree 5f4ee0b |
| OBS-P1-001 | P1 | Alerting and scheduled detection are defined only on the host, not in the repository |  |  | partially-fixed | incident runbook documents signals/thresholds/escalation/rollback/drill; committed schedule still open |
| SEC-P1-001 | P1 | Launch owner approval is unverified free text, so release identity binding is not enforced |  |  | partially-fixed | Draft PR #7; de-hardcoded release identity + crypto-attested owner signature; verify.log clean worktree 5f4ee0b |
| SUPPLY-P1-001 | P1 | No SBOM artifact generated or bound to the release commit |  |  | partially-fixed | Draft PR #9: generate CycloneDX SBOM in foundation + upload commit-bound artifact (sbom-<sha>); actions pinned to SHAs; verify.log clean LF worktree d61c968 |
| API-P2-001 | P2 | API contract is hand-maintained with no automated drift test |  |  | partially-fixed |  |
| ARCH-P2-001 | P2 | Compose services define no CPU, memory or PID limits |  |  | partially-fixed |  |
| ARCH-P2-002 | P2 | Readiness endpoint cannot fail when a dependency is unavailable |  |  | partially-fixed |  |
| ARCH-P2-003 | P2 | Authoritative lobby/LiveOps state is process-local and lost on restart |  |  | partially-fixed |  |
| CI-P2-001 | P2 | No dependency-vulnerability audit or repository secret scan in CI |  |  | partially-fixed |  |
| CI-P2-002 | P2 | GitHub Actions are pinned by mutable tags, not commit SHAs |  |  | partially-fixed |  |
| DATA-P2-001 | P2 | RLS/negative SQL suites are manual and not gated in CI |  |  | partially-fixed | remediation PS-U04 draft PR #14 at dcdceca; DB suites + manifest verified on ci-runner |
| DATA-P2-002 | P2 | No migration checksum/manifest; gaps are only documented |  |  | partially-fixed | remediation PS-U04 draft PR #14 at dcdceca; DB suites + manifest verified on ci-runner |
| EXEC-P2-001 | P2 | Release gate is conditional because release-identity controls are not yet enforced |  |  | partially-fixed | remediation PS-U05 draft PR #15 at 3e9e56c: in-repo release-gate record (docs/RELEASE_GATE.md) makes the conditional gate + blocking conditions explicit; verified-fixed gated on P1-1..P1-4 + fresh attestation |
| FEAT-P2-001 | P2 | Kill-switch defaults drift between repo documentation and production compose |  |  | partially-fixed | PS-U06 draft PR #16 open |
| FINAL-P2-001 | P2 | Operational reliability controls are not version-controlled or exercised per release |  |  | partially-fixed | PS-U07 draft PR #17: versioned reliability controls + RPO/RTO + per-release backup/alert/rollback drills (docs/runbooks/RELIABILITY_DRILLS.md); verified-fixed gated on captured drill evidence at the released commit and the OBS-P1-001 committed schedule |
| HYG-P2-001 | P2 | Only `apps/web` is linted; the other workspaces have no lint script |  |  | partially-fixed | PS-U08 catch-all: backup runbook, .gitattributes, CHANGELOG, repomix gitignore; HYG-P2-001 deferred |
| HYG-P2-002 | P2 | Duplicated generated artifacts and a large binary inflate the repository |  |  | partially-fixed | PS-U08 catch-all: backup runbook, .gitattributes, CHANGELOG, repomix gitignore; HYG-P2-001 deferred |
| HYG-P2-003 | P2 | Backup runbook contradicts the (fixed) assurance freshness check |  |  | partially-fixed | PS-U08 catch-all: backup runbook, .gitattributes, CHANGELOG, repomix gitignore; HYG-P2-001 deferred |
| INV-P2-001 | P2 | Duplicate full-source repomix exports committed to the repository |  |  | partially-fixed | remediation PS-U09 open 8f369a62f019bf8a0527908e9e61307f931fa6e9 https://github.com/MaineCyberTech/snowride/pull/19 |
| INV-P2-002 | P2 | Evidence tree dominates the repository by file count and size |  |  | partially-fixed | remediation PS-U09 open 8f369a62f019bf8a0527908e9e61307f931fa6e9 https://github.com/MaineCyberTech/snowride/pull/19 |
| OBS-P2-001 | P2 | OTel traces are exported only to the collector `debug` exporter |  |  | partially-fixed | remediation PS-U10 open 7c61d27cea59c1b5e5004fb1f14172d1e76e8e32 https://github.com/MaineCyberTech/snowride/pull/20 |
| OBS-P2-002 | P2 | No committed SLO/error-budget definitions |  |  | partially-fixed | remediation PS-U10 open 7c61d27cea59c1b5e5004fb1f14172d1e76e8e32 https://github.com/MaineCyberTech/snowride/pull/20 |
| SEC-P2-001 | P2 | HTTP surface enforces no Origin/CORS allowlist |  |  | partially-fixed | remediation PS-U11 open 559170d011b0f11a6be3566760c320043e7f53e9 https://github.com/MaineCyberTech/snowride/pull/21 |
| SEC-P2-002 | P2 | No repository-tree secret scanning in CI or pre-commit |  |  | partially-fixed | remediation PS-U11 open 559170d011b0f11a6be3566760c320043e7f53e9 https://github.com/MaineCyberTech/snowride/pull/21 |
| SUPPLY-P2-001 | P2 | License and vulnerability enforcement is host-only, not merge-gating |  |  | partially-fixed | remediation PS-U12 open b1c0f21781607084626789ba95d587444de83b64 https://github.com/MaineCyberTech/snowride/pull/22 |
| SUPPLY-P2-002 | P2 | Install scripts are allowlisted for several dependencies without provenance checks |  |  | partially-fixed | remediation PS-U12 open b1c0f21781607084626789ba95d587444de83b64 https://github.com/MaineCyberTech/snowride/pull/22 |
| TEST-P2-001 | P2 | No coverage thresholds and coverage never runs in CI |  |  | partially-fixed | remediation PS-U13 open a7fb4a6270774ad588f68184fa4a21cd5d61565c https://github.com/MaineCyberTech/snowride/pull/23 |
| TEST-P2-002 | P2 | E2E matrix is Chromium-only despite a multi-browser product claim |  |  | partially-fixed | remediation PS-U13 open a7fb4a6270774ad588f68184fa4a21cd5d61565c https://github.com/MaineCyberTech/snowride/pull/23 |
| TEST-P2-003 | P2 | SQL negative/RLS suites are not gated by any pipeline |  |  | partially-fixed | remediation PS-U13 open a7fb4a6270774ad588f68184fa4a21cd5d61565c https://github.com/MaineCyberTech/snowride/pull/23 |
| API-P3-001 | P3 | Public operational endpoints are unauthenticated and unversioned |  |  | partially-fixed |  |
| API-P3-002 | P3 | No explicit CORS response headers for cross-origin HTTP dev/deploy |  |  | partially-fixed |  |
| CI-P3-001 | P3 | CI produces no durable artifacts bound to the commit |  |  | partially-fixed | Draft PR #9: generate CycloneDX SBOM in foundation + upload commit-bound artifact (sbom-<sha>); actions pinned to SHAs; verify.log clean LF worktree d61c968 |
| DATA-P3-001 | P3 | Production database schema state is unverified in this audit |  |  | partially-fixed | remediation PS-U04 draft PR #14 at dcdceca; DB suites + manifest verified on ci-runner |
| FEAT-P3-001 | P3 | `/launch-readiness` reports flags as `deployed: true` unconditionally |  |  | partially-fixed | PS-U06 draft PR #16 open |
| HYG-P3-001 | P3 | No release/version lineage in the repository |  |  | partially-fixed | PS-U08 catch-all: backup runbook, .gitattributes, CHANGELOG, repomix gitignore; HYG-P2-001 deferred |
| HYG-P3-002 | P3 | No `.gitattributes`; binary/large content handled plainly |  |  | partially-fixed | PS-U08 catch-all: backup runbook, .gitattributes, CHANGELOG, repomix gitignore; HYG-P2-001 deferred |
| INV-P3-001 | P3 | Tracked `.log` files contradict the `*.log` gitignore rule |  |  | partially-fixed | remediation PS-U09 open 8f369a62f019bf8a0527908e9e61307f931fa6e9 https://github.com/MaineCyberTech/snowride/pull/19 |
| INV-P3-002 | P3 | One-off review artifacts at repository root |  |  | partially-fixed | remediation PS-U09 open 8f369a62f019bf8a0527908e9e61307f931fa6e9 https://github.com/MaineCyberTech/snowride/pull/19 |
| OBS-P3-001 | P3 | Metrics are process-local counters with durable history only when the snapshot timer is enabled |  |  | partially-fixed | remediation PS-U10 open 7c61d27cea59c1b5e5004fb1f14172d1e76e8e32 https://github.com/MaineCyberTech/snowride/pull/20 |
| SEC-P3-001 | P3 | Claim-less SQL callers are treated as trusted by `social_guard_*` |  |  | partially-fixed | remediation PS-U11 open 559170d011b0f11a6be3566760c320043e7f53e9 https://github.com/MaineCyberTech/snowride/pull/21 |
| SEC-P3-002 | P3 | Service-role key delivered via environment rather than a Docker secret |  |  | partially-fixed | remediation PS-U11 open 559170d011b0f11a6be3566760c320043e7f53e9 https://github.com/MaineCyberTech/snowride/pull/21 |
| SUPPLY-P3-001 | P3 | Dependabot is configured but ungrouped for security updates |  |  | partially-fixed | remediation PS-U12 open b1c0f21781607084626789ba95d587444de83b64 https://github.com/MaineCyberTech/snowride/pull/22 |
| TEST-P3-001 | P3 | `test:unit` script resolves to a non-existent path |  |  | partially-fixed | remediation PS-U13 open a7fb4a6270774ad588f68184fa4a21cd5d61565c https://github.com/MaineCyberTech/snowride/pull/23 |
| TEST-P3-002 | P3 | Local `verify-all.sh` is a weaker gate than CI, and audit could not reproduce tests |  |  | partially-fixed | remediation PS-U13 open a7fb4a6270774ad588f68184fa4a21cd5d61565c https://github.com/MaineCyberTech/snowride/pull/23 |
