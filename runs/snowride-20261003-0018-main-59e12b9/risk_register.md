# Risk Register — Snowride @ 59e12b9

Severity: P0 critical, P1 high, P2 medium, P3 low. Status vocabulary: open / partially-fixed / verified-fixed / still-open / regressed / owner-accepted.

| # | ID | Sev | Area | Risk | Evidence | Fix | Owner | Effort | Status |
|---|---|---|---|---|---|---|---|---|---|
| 1 | SEC-P1-001 | P1 | SEC | Launch approval is unverified free text | `infra/compose/docker-compose.yml` 103–121; `config.ts` 182–207 | Cryptographic signature verification; remove committed approval | Owner/Release | M | open |
| 2 | DATA-P1-001 | P1 | DATA | Attested migration head 0055 < repo head 0056 | `0056_hash_legacy_gpu.sql`; compose 117 | Re-attest; CI head-equality check | Owner/Release | S | open |
| 3 | SUPPLY-P1-001 | P1 | SUPPLY | No SBOM bound to release | `package.json` devDep only; no CI SBOM step | Generate/bind CycloneDX SBOM | Release | S | open |
| 4 | OBS-P1-001 | P1 | OBS | Alerting/scheduling host-only, not reproducible | `scripts/assurance/assurance.sh`; no crontab in repo | Commit schedule/alerts + self-test | Operator | M | open |
| 5 | CI-P1-001 | P1 | CI | Branch protection unproven | `ci-foundation.yml`; no evidence artifact | Require checks on `main`; capture evidence | Owner | S | open |
| 6 | FINAL-P1-001 | P1 | FINAL | Release trust self-asserted + stale | compose 103–121; HEAD 59e12b9 | Close #1–#5; re-attest | Owner | M | open |
| 7 | DATA-P2-001 | P2 | DATA | RLS negative suites not in CI | `AGENTS.md` 16; workflow | Run suites in migrations job | DB/CI | M | open |
| 8 | TEST-P2-003 | P2 | TEST | RLS suites un-gated (dup view) | same | same | DB/CI | M | open |
| 9 | TEST-P2-001 | P2 | TEST | No coverage thresholds | `vitest.config.ts` 18–20; CI | Coverage + ratchet | QA | M | open |
| 10 | TEST-P2-002 | P2 | TEST | E2E Chromium-only | `playwright.config.ts` 51–56 | Add Firefox/WebKit or bound claim | Web/QA | M | open |
| 11 | ARCH-P2-001 | P2 | ARCH | No container resource limits | `docker-compose.yml` services | mem/cpu/pids limits | Operator | S | open |
| 12 | ARCH-P2-002 | P2 | ARCH | Readiness doesn't probe deps | `server.ts` ~842; `healthz/route.ts` | Dependency-aware `/readyz` | Realtime | S | open |
| 13 | ARCH-P2-003 | P2 | ARCH | LiveOps overrides lost on restart | `server.ts`; `KILL_SWITCHES.md` 55 | Persist/restore overrides | Realtime | M | open |
| 14 | SEC-P2-001 | P2 | SEC | No HTTP origin enforcement | `server.ts` 564–570, 803 | Validate Origin on HTTP | Realtime | S | open |
| 15 | SEC-P2-002 | P2 | SEC | No repo-tree secret scan | `ci-foundation.yml`; bundle gate only | Add gitleaks/trufflehog | CI/Sec | S | open |
| 16 | CI-P2-001 | P2 | CI | No per-PR audit/secret scan | workflow; `assurance.sh` daily only | Add to CI | CI/Sec | S | open |
| 17 | CI-P2-002 | P2 | CI | Actions pinned by tags | `ci-foundation.yml` 20,23 | Pin SHAs | CI | S | open |
| 18 | SUPPLY-P2-001 | P2 | SUPPLY | License/vuln enforcement host-only | `assurance.sh` 95–117 | Move to CI | CI/Legal | M | open |
| 19 | SUPPLY-P2-002 | P2 | SUPPLY | Install scripts allowlisted | `package.json` allowScripts | Document/verify provenance | Build | M | open |
| 20 | OBS-P2-001 | P2 | OBS | Traces to debug exporter only | `otel/collector-config.yaml` 12–20 | Add trace backend/retention | Operator | M | open |
| 21 | OBS-P2-002 | P2 | OBS | No SLO/error budget | repo; `/launch-readiness` sloBurn | Define SLIs/SLOs | Operator | M | open |
| 22 | HYG-P2-001 | P2 | HYG | Only web linted | `package.json` 19; workspace pkgs | Lint all workspaces | Maintainer | M | open |
| 23 | HYG-P2-002 | P2 | HYG | Duplicate artifacts/binary weight | repomix ×3; 6.88 MB PDF | De-dup; size budget | Maintainer | S | open |
| 24 | HYG-P2-003 | P2 | HYG | Backup runbook contradicts code | `BACKUP_RESTORE.md` 16–19 | Update doc | Operator | S | open |
| 25 | INV-P2-001 | P2 | INV | Duplicate repomix exports | `evidence/production-acceptance/repomix-*` | Remove duplicates | Maintainer | S | open |
| 26 | INV-P2-002 | P2 | INV | Evidence dominates repo | `inventory.json` 849 files | Archive policy | Maintainer | M | open |
| 27 | FEAT-P2-001 | P2 | FEAT | Flag defaults drift (prod overrides) | `config.ts`; compose 93–94,125,128 | Single documented source | Realtime | S | open |
| 28 | API-P2-001 | P2 | API | Hand-maintained API contract | `docs/API.md` 3–6 | Generate/parity test | Realtime | M | open |
| 29 | FINAL-P2-001 | P2 | FINAL | Ops controls not versioned/exercised | ARCH/OBS findings; backup doc | Version + drill per release | Operator | M | open |
| 30 | EXEC-P2-001 | P2 | EXEC | Gate conditional on identity controls | `RELEASE_GATE.md` | Close #1–#6 | Owner | M | open |
| 31 | INV-P3-001 | P3 | INV | Tracked `.log` vs gitignore | `.gitignore`; 94 tracked `.log` | Reconcile | Maintainer | S | open |
| 32 | INV-P3-002 | P3 | INV | Root review artifacts | root files list | Re-home | Maintainer | S | open |
| 33 | FEAT-P3-001 | P3 | FEAT | `/launch-readiness` `deployed` constant | `server.ts` 903–926 | Derive | Realtime | S | open |
| 34 | SEC-P3-001 | P3 | SEC | Claim-less SQL callers trusted | `0017` 391–455 | `current_user` check | DB | S | open |
| 35 | SEC-P3-002 | P3 | SEC | Service key via env not secret | compose 73–75 | Docker secret | Operator | M | open |
| 36 | DATA-P2-002 | P2 | DATA | No migration checksum manifest | `supabase/migrations` | Add manifest | DB/CI | S | open |
| 37 | DATA-P3-001 | P3 | DATA | Prod schema unverified | `EXCEPTION_REGISTER.md` E3-003 | Read-only schema check | Owner | S | open |
| 38 | API-P3-001 | P3 | API | Public ops endpoints unversioned | `server.ts` 853–1016 | Review/version | Realtime | S | open |
| 39 | API-P3-002 | P3 | API | No CORS headers for HTTP | `server.ts` 811 | Docs/headers | Web | S | open |
| 40 | TEST-P3-001 | P3 | TEST | `test:unit` broken glob | `package.json` 22 | Fix path | Maintainer | S | open |
| 41 | TEST-P3-002 | P3 | TEST | Local gate weaker than CI | `verify-all.sh` | Align/document | CI | S | open |
| 42 | CI-P3-001 | P3 | CI | No CI artifacts bound to commit | workflow | Upload artifacts | CI | S | open |
| 43 | SUPPLY-P3-001 | P3 | SUPPLY | Dependabot security ungrouped | `.github/dependabot.yml` | Security grouping | Maintainer | S | open |
| 44 | OBS-P3-001 | P3 | OBS | Process-local metrics | `server.ts` counters | Document/ensure timer | Operator | S | open |
| 45 | HYG-P3-001 | P3 | HYG | No release/version lineage | `package.json` 0.1.0 | Version/changelog | Release | S | open |
| 46 | HYG-P3-002 | P3 | HYG | No `.gitattributes` | root | Add file | Maintainer | S | open |

Note: row 8 (TEST-P2-003) is the same control as row 7 (DATA-P2-001) viewed from the testing area; both IDs are retained because the reports cite them independently.

## Finding index

| ID | Severity | Title |
|---|---|---|
| CI-P1-001 | P1 | No evidence of branch protection or required status checks on `main` |
| DATA-P1-001 | P1 | Attested migration head (0055) is one behind the repository head (0056) |
| FINAL-P1-001 | P1 | Release trust is assembled from self-asserted and stale identities |
| OBS-P1-001 | P1 | Alerting and scheduled detection are defined only on the host, not in the repository |
| SEC-P1-001 | P1 | Launch owner approval is unverified free text, so release identity binding is not enforced |
| SUPPLY-P1-001 | P1 | No SBOM artifact generated or bound to the release commit |
| API-P2-001 | P2 | API contract is hand-maintained with no automated drift test |
| ARCH-P2-001 | P2 | Compose services define no CPU, memory or PID limits |
| ARCH-P2-002 | P2 | Readiness endpoint cannot fail when a dependency is unavailable |
| ARCH-P2-003 | P2 | Authoritative lobby/LiveOps state is process-local and lost on restart |
| CI-P2-001 | P2 | No dependency-vulnerability audit or repository secret scan in CI |
| CI-P2-002 | P2 | GitHub Actions are pinned by mutable tags, not commit SHAs |
| DATA-P2-001 | P2 | RLS/negative SQL suites are manual and not gated in CI |
| DATA-P2-002 | P2 | No migration checksum/manifest; gaps are only documented |
| EXEC-P2-001 | P2 | Release gate is conditional because release-identity controls are not yet enforced |
| FEAT-P2-001 | P2 | Kill-switch defaults drift between repo documentation and production compose |
| FINAL-P2-001 | P2 | Operational reliability controls are not version-controlled or exercised per release |
| HYG-P2-001 | P2 | Only `apps/web` is linted; the other workspaces have no lint script |
| HYG-P2-002 | P2 | Duplicated generated artifacts and a large binary inflate the repository |
| HYG-P2-003 | P2 | Backup runbook contradicts the (fixed) assurance freshness check |
| INV-P2-001 | P2 | Duplicate full-source repomix exports committed to the repository |
| INV-P2-002 | P2 | Evidence tree dominates the repository by file count and size |
| OBS-P2-001 | P2 | OTel traces are exported only to the collector `debug` exporter |
| OBS-P2-002 | P2 | No committed SLO/error-budget definitions |
| SEC-P2-001 | P2 | HTTP surface enforces no Origin/CORS allowlist |
| SEC-P2-002 | P2 | No repository-tree secret scanning in CI or pre-commit |
| SUPPLY-P2-001 | P2 | License and vulnerability enforcement is host-only, not merge-gating |
| SUPPLY-P2-002 | P2 | Install scripts are allowlisted for several dependencies without provenance checks |
| TEST-P2-001 | P2 | No coverage thresholds and coverage never runs in CI |
| TEST-P2-002 | P2 | E2E matrix is Chromium-only despite a multi-browser product claim |
| TEST-P2-003 | P2 | SQL negative/RLS suites are not gated by any pipeline |
| API-P3-001 | P3 | Public operational endpoints are unauthenticated and unversioned |
| API-P3-002 | P3 | No explicit CORS response headers for cross-origin HTTP dev/deploy |
| CI-P3-001 | P3 | CI produces no durable artifacts bound to the commit |
| DATA-P3-001 | P3 | Production database schema state is unverified in this audit |
| FEAT-P3-001 | P3 | `/launch-readiness` reports flags as `deployed: true` unconditionally |
| HYG-P3-001 | P3 | No release/version lineage in the repository |
| HYG-P3-002 | P3 | No `.gitattributes`; binary/large content handled plainly |
| INV-P3-001 | P3 | Tracked `.log` files contradict the `*.log` gitignore rule |
| INV-P3-002 | P3 | One-off review artifacts at repository root |
| OBS-P3-001 | P3 | Metrics are process-local counters with durable history only when the snapshot timer is enabled |
| SEC-P3-001 | P3 | Claim-less SQL callers are treated as trusted by `social_guard_*` |
| SEC-P3-002 | P3 | Service-role key delivered via environment rather than a Docker secret |
| SUPPLY-P3-001 | P3 | Dependabot is configured but ungrouped for security updates |
| TEST-P3-001 | P3 | `test:unit` script resolves to a non-existent path |
| TEST-P3-002 | P3 | Local `verify-all.sh` is a weaker gate than CI, and audit could not reproduce tests |
