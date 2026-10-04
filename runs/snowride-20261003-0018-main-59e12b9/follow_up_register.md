# Follow-up register

Owner/Target/Status columns drive tools/collect_findings.py enrichment.

| ID | Severity | Title | Owner | Target | Status | Post-audit note |
|---|---|---|---|---|---|---|
| CI-P1-001 | P1 | No evidence of branch protection or required status checks on `main` |  |  | verified-fixed | re-audit 2026-10-04: closed |
| DATA-P1-001 | P1 | Attested migration head (0055) is one behind the repository head (0056) |  |  | verified-fixed | re-audit 2026-10-04: regression fixed by snowride#38 @ af7f796 |
| FINAL-P1-001 | P1 | Release trust is assembled from self-asserted and stale identities |  |  | still-open | re-audit 2026-10-04: still-open |
| OBS-P1-001 | P1 | Alerting and scheduled detection are defined only on the host, not in the repository |  |  | verified-fixed | re-audit 2026-10-04: closed by snowride#38 @ ce3f639 (assurance schedule version-controlled) |
| SEC-P1-001 | P1 | Launch owner approval is unverified free text, so release identity binding is not enforced |  |  | verified-fixed | re-audit 2026-10-04: closed |
| SUPPLY-P1-001 | P1 | No SBOM artifact generated or bound to the release commit |  |  | verified-fixed | re-audit 2026-10-04: closed |
| API-P2-001 | P2 | API contract is hand-maintained with no automated drift test |  |  | verified-fixed | re-audit 2026-10-04: closed |
| ARCH-P2-001 | P2 | Compose services define no CPU, memory or PID limits |  |  | verified-fixed | re-audit 2026-10-04: closed |
| ARCH-P2-002 | P2 | Readiness endpoint cannot fail when a dependency is unavailable |  |  | verified-fixed | re-audit 2026-10-04: closed |
| ARCH-P2-003 | P2 | Authoritative lobby/LiveOps state is process-local and lost on restart |  |  | still-open | re-audit 2026-10-04: still-open |
| CI-P2-001 | P2 | No dependency-vulnerability audit or repository secret scan in CI |  |  | verified-fixed | re-audit 2026-10-04: closed |
| CI-P2-002 | P2 | GitHub Actions are pinned by mutable tags, not commit SHAs |  |  | verified-fixed | re-audit 2026-10-04: closed |
| DATA-P2-001 | P2 | RLS/negative SQL suites are manual and not gated in CI |  |  | verified-fixed | re-audit 2026-10-04: closed |
| DATA-P2-002 | P2 | No migration checksum/manifest; gaps are only documented |  |  | verified-fixed | re-audit 2026-10-04: closed |
| EXEC-P2-001 | P2 | Release gate is conditional because release-identity controls are not yet enforced |  |  | still-open | re-audit 2026-10-04: still-open |
| FEAT-P2-001 | P2 | Kill-switch defaults drift between repo documentation and production compose |  |  | verified-fixed | re-audit 2026-10-04: closed |
| FINAL-P2-001 | P2 | Operational reliability controls are not version-controlled or exercised per release |  |  | still-open | re-audit 2026-10-04: still-open |
| HYG-P2-001 | P2 | Only `apps/web` is linted; the other workspaces have no lint script |  |  | still-open | re-audit 2026-10-04: still-open |
| HYG-P2-002 | P2 | Duplicated generated artifacts and a large binary inflate the repository |  |  | still-open | re-audit 2026-10-04: still-open |
| HYG-P2-003 | P2 | Backup runbook contradicts the (fixed) assurance freshness check |  |  | verified-fixed | re-audit 2026-10-04: closed |
| INV-P2-001 | P2 | Duplicate full-source repomix exports committed to the repository |  |  | verified-fixed | re-audit 2026-10-04: closed |
| INV-P2-002 | P2 | Evidence tree dominates the repository by file count and size |  |  | still-open | re-audit 2026-10-04: still-open |
| OBS-P2-001 | P2 | OTel traces are exported only to the collector `debug` exporter |  |  | verified-fixed | re-audit 2026-10-04: closed |
| OBS-P2-002 | P2 | No committed SLO/error-budget definitions |  |  | verified-fixed | re-audit 2026-10-04: closed |
| SEC-P2-001 | P2 | HTTP surface enforces no Origin/CORS allowlist |  |  | verified-fixed | re-audit 2026-10-04: closed |
| SEC-P2-002 | P2 | No repository-tree secret scanning in CI or pre-commit |  |  | verified-fixed | re-audit 2026-10-04: closed |
| SUPPLY-P2-001 | P2 | License and vulnerability enforcement is host-only, not merge-gating |  |  | verified-fixed | re-audit 2026-10-04: closed |
| SUPPLY-P2-002 | P2 | Install scripts are allowlisted for several dependencies without provenance checks |  |  | verified-fixed | re-audit 2026-10-04: closed |
| TEST-P2-001 | P2 | No coverage thresholds and coverage never runs in CI |  |  | verified-fixed | re-audit 2026-10-04: closed |
| TEST-P2-002 | P2 | E2E matrix is Chromium-only despite a multi-browser product claim |  |  | verified-fixed | re-audit 2026-10-04: closed |
| TEST-P2-003 | P2 | SQL negative/RLS suites are not gated by any pipeline |  |  | verified-fixed | re-audit 2026-10-04: closed |
| API-P3-001 | P3 | Public operational endpoints are unauthenticated and unversioned |  |  | still-open | re-audit 2026-10-04: still-open |
| API-P3-002 | P3 | No explicit CORS response headers for cross-origin HTTP dev/deploy |  |  | verified-fixed | re-audit 2026-10-04: closed |
| CI-P3-001 | P3 | CI produces no durable artifacts bound to the commit |  |  | verified-fixed | re-audit 2026-10-04: closed |
| DATA-P3-001 | P3 | Production database schema state is unverified in this audit |  |  | still-open | re-audit 2026-10-04: still-open |
| FEAT-P3-001 | P3 | `/launch-readiness` reports flags as `deployed: true` unconditionally |  |  | verified-fixed | re-audit 2026-10-04: closed |
| HYG-P3-001 | P3 | No release/version lineage in the repository |  |  | verified-fixed | re-audit 2026-10-04: closed |
| HYG-P3-002 | P3 | No `.gitattributes`; binary/large content handled plainly |  |  | verified-fixed | re-audit 2026-10-04: closed |
| INV-P3-001 | P3 | Tracked `.log` files contradict the `*.log` gitignore rule |  |  | still-open | re-audit 2026-10-04: still-open |
| INV-P3-002 | P3 | One-off review artifacts at repository root |  |  | verified-fixed | re-audit 2026-10-04: closed |
| OBS-P3-001 | P3 | Metrics are process-local counters with durable history only when the snapshot timer is enabled |  |  | still-open | re-audit 2026-10-04: still-open |
| SEC-P3-001 | P3 | Claim-less SQL callers are treated as trusted by `social_guard_*` |  |  | still-open | re-audit 2026-10-04: still-open |
| SEC-P3-002 | P3 | Service-role key delivered via environment rather than a Docker secret |  |  | still-open | re-audit 2026-10-04: still-open |
| SUPPLY-P3-001 | P3 | Dependabot is configured but ungrouped for security updates |  |  | verified-fixed | re-audit 2026-10-04: closed |
| TEST-P3-001 | P3 | `test:unit` script resolves to a non-existent path |  |  | verified-fixed | re-audit 2026-10-04: closed |
| TEST-P3-002 | P3 | Local `verify-all.sh` is a weaker gate than CI, and audit could not reproduce tests |  |  | still-open | re-audit 2026-10-04: still-open |
