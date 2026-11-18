# Follow-up register

Run: `bench-test-20261013-0819-full-main-b916709` · Target: `bench-test` @ `b916709` · Profile: base

Register mirrored 1:1 with `risk_register.md` so `tools/check_run.sh` passes.

| Finding | Severity | Title | Owner | Target | Status | Note |
|---|---|---|---|---|---|---|
| CHAIN-P0-001 | P0 | Single shared secret is both the runner join token and the operator bearer, and it is baked into public app bundles / live ISOs -> anyone who downloads a release gets fleet-wide remote code execution (exec/shell) on every runner | @owner | CHAIN | open |  |
| EXEC-P0-001 | P0 | Release gate = NO-GO: 3 unresolved P0s, all about one shared operator secret baked into public artifacts | @owner | EXEC | open |  |
| FINAL-P0-001 | P0 | One shared operator/join token is baked into public app bundles and the live ISO, so any release download yields fleet-wide remote code execution (merged across 10 domains) | @owner | FINAL | open |  |
| FINAL-P0-002 | P0 | A write-capable GitHub PAT is baked into the publicly downloadable live ISO, and runners auto-pull code from main, turning repo write into fleet code execution (merged across 4 domains) | @owner | FINAL | open |  |
| SC-P0-001 | P0 | GitHub PAT with Contents:Read/Write is baked into the publicly-downloadable live ISO | @owner | SC | open |  |
| SEC-P0-001 | P0 | Operator token (and a repo-write GitHub PAT) baked into public release artifacts | @owner | SEC | open |  |
| ACM-P1-001 | P1 | Shared join token is the full operator credential and is baked into public releases | @owner | ACM | open |  |
| ACM-P1-002 | P1 | machine_id adoption hands out another runner's API key | @owner | ACM | open |  |
| ADMIN-P1-001 | P1 | Shared all-powerful operator token is distributed to every runner | @owner | ADMIN | open |  |
| ADMIN-P1-002 | P1 | Runner identity takeover via machine_id | @owner | ADMIN | open |  |
| AI-P1-001 | P1 | Test suite is documented as mandatory but no CI gate runs it, so an agent can land a red change on main | @owner | AI | open |  |
| API-P1-001 | P1 | POST /api/v1/register gives away another runner's api_key via unproven machine_id adoption | @owner | API | open |  |
| ARCH-P1-001 | P1 | Single shared token is both the join credential and an all-powerful operator credential, and is shipped in public artifacts | @owner | ARCH | open |  |
| BP-P1-001 | P1 | No test/CI workflow exists, so no required status check can gate merges to main | @owner | BP | open |  |
| BP-P1-002 | P1 | Release workflow writes directly to main and cuts tags with no approval or documented bypass | @owner | BP | open |  |
| CHAIN-P1-001 | P1 | Runner identity takeover via /register machine_id adoption: any authenticated runner can claim another runner's row and is handed that row's api_key (the runner_id path was fixed, the machine_id path was not) | @owner | CHAIN | open |  |
| CHAIN-P1-002 | P1 | A Contents:Read/Write GitHub PAT is baked into the public live ISO and every runner auto-pulls code from main at startup -> repo write access becomes code execution on the whole fleet (CI-to-production / supply-chain chain) | @owner | CHAIN | open |  |
| CI-P1-001 | P1 | Build workflows bake live credentials into public release artifacts | @owner | CI | open |  |
| CI-P1-002 | P1 | No test/lint/secret-scan CI gate; nothing runs on pull_request | @owner | CI | open |  |
| CTR-P1-001 | P1 | Control-plane and upload bearer tokens are baked into the publicly downloadable live ISO image | @owner | CTR | open |  |
| DATA-P1-001 | P1 | DELETE /api/v1/runs/<id> does not delete the run's logs; they stay orphaned in the DB and remain readable | @owner | DATA | open |  |
| DR-P1-001 | P1 | No backup of the control-plane SQLite database, which is the single system of record | @owner | DR | open |  |
| DR-P1-002 | P1 | Restore is never exercised: no restore script, runbook, or test; the only import path cannot rebuild the DB | @owner | DR | open |  |
| EXEC-P1-001 | P1 | Cross-domain convergence: a single shared BENCHD_TOKEN serves both the low-trust join tier and the highest-privilege operator tier | @owner | EXEC | open |  |
| EXEC-P1-002 | P1 | Runner identity takeover via POST /register machine_id adoption is unfixed and gives an attacker another runner's API key | @owner | EXEC | open |  |
| EXEC-P1-003 | P1 | No CI test/quality gate: main merges and auto-releases land with zero automated verification | @owner | EXEC | open |  |
| EXEC-P1-004 | P1 | Disaster recovery is absent: the single SQLite system of record has no backup, no restore, and no exercise | @owner | EXEC | open |  |
| FINAL-P1-001 | P1 | Control plane fails open: with no BENCHD_TOKEN it serves the full operator API unauthenticated while bound to 0.0.0.0 (reproduced across 4 domains) | @owner | FINAL | open |  |
| FINAL-P1-002 | P1 | Any enrolled runner can take over another runner's identity via unproven machine_id adoption and be handed that runner's api_key (merged across 5 domains) | @owner | FINAL | open |  |
| FINAL-P1-003 | P1 | No CI test/lint/secret gate, while the release workflow self-modifies main and auto-tags with no approval (merged across 5 domains) | @owner | FINAL | open |  |
| FINAL-P1-004 | P1 | Data lifecycle is unmanaged: run delete leaves logs behind (reproduced), telemetry/artifacts have no retention, and there is no backup, restore, or incident plan (merged across 6 domains) | @owner | FINAL | open |  |
| FINAL-P1-005 | P1 | The most destructive operation fails open on integrity checks, and third-party code is fetched and executed without verification; no SBOM or license inventory exists (merged across 4 domains) | @owner | FINAL | open |  |
| FINAL-P1-006 | P1 | ~10,000 generated result files (~55 MB, with machine PII) are committed to a public repo despite a results/ ignore rule (merged across 6 domains) | @owner | FINAL | open |  |
| HYGIENE-P1-001 | P1 | 9,555 generated result files (~55 MB) committed under results/ | @owner | HYGIENE | open |  |
| INFRA-P1-001 | P1 | benchd fails open: with no BENCHD_TOKEN it serves the full operator API unauthenticated (reproduced) | @owner | INFRA | open |  |
| INFRA-P1-002 | P1 | The shared operator token is baked into publicly downloadable app bundles and the live ISO, and it is the same token that grants operator control | @owner | INFRA | open |  |
| INV-P1-001 | P1 | Shared control-plane token baked into public releases | @owner | INV | open |  |
| IR-P1-001 | P1 | No incident-response documentation, severity taxonomy, roles, or postmortem process exists anywhere in the repository | @owner | IR | open |  |
| PERF-P1-001 | P1 | Unbounded SQLite growth: telemetry/logs/events/artifacts have no retention, cap, or capacity signal | @owner | PERF | open |  |
| PERF-P1-002 | P1 | Web dashboard re-fetches 300 full run rows and an unbounded /trends scan on every refresh tick | @owner | PERF | open |  |
| PRIV-P1-001 | P1 | Unredacted hostnames and absolute home paths (usernames) committed to the public repository | @owner | PRIV | open |  |
| REL-P1-001 | P1 | No CHANGELOG and no release notes are generated for version tags; release.yml only cuts a bare tag | @owner | REL | open |  |
| RES-P1-001 | P1 | iso_fetch returns ok=True even when SHA256SUMS verification fails, so a bad ISO is accepted for a destructive write | @owner | RES | open |  |
| SBOM-P1-001 | P1 | No SBOM is produced for either shipped artifact set (PyInstaller app bundles and the live ISO) | @owner | SBOM | open |  |
| SBOM-P1-002 | P1 | Third-party binary LibreHardwareMonitor is redistributed in release bundles with no tracked license/attribution (MPL-2.0 compliance gap) | @owner | SBOM | open |  |
| SC-P1-001 | P1 | Control-plane operator token is baked into public app bundles | @owner | SC | open |  |
| SC-P1-002 | P1 | Third-party binaries are downloaded and executed without integrity verification (LibreHardwareMonitor 'latest', nvfancontrol) | @owner | SC | open |  |
| SEARCH-P1-001 | P1 | Deleting a run does not delete its console logs; they stay retrievable by run id | @owner | SEARCH | open |  |
| SEC-P1-001 | P1 | Fail-open authentication when no token is configured | @owner | SEC | open |  |
| SEC-P1-002 | P1 | /api/v1/register discloses other runners' API keys | @owner | SEC | open |  |
| SECRET-P1-001 | P1 | Shared operator/join token is baked into public app release bundles | @owner | SECRET | open |  |
| SECRET-P1-002 | P1 | Write-capable GitHub PAT is baked into the public live-USB ISO | @owner | SECRET | open |  |
| TEST-P1-001 | P1 | No CI job runs the test suite or any compile/lint gate | @owner | TEST | open |  |
| ACM-P2-001 | P2 | No lifecycle for runner API keys or the operator token: no expiry, rotation, or per-key revocation; keys stored in plaintext | @owner | ACM | open |  |
| ACM-P2-002 | P2 | Control plane fails open: with no BENCHD_TOKEN every request is a full operator (RCE/reboot/delete), and the shipped unit binds 0.0.0.0 | @owner | ACM | open |  |
| ACM-P2-003 | P2 | No credential lifecycle (expiry/rotation/revocation); keys plaintext | @owner | ACM | open |  |
| ACM-P2-004 | P2 | Fail-open when no token is set, on a 0.0.0.0 unit | @owner | ACM | open |  |
| ACM-P2-005 | P2 | No audit trail / actor attribution for privileged actions | @owner | ACM | open |  |
| ACM-P2-006 | P2 | Operator token in URLs + wildcard CORS | @owner | ACM | open |  |
| ADMIN-P2-001 | P2 | No audit log for privileged, destructive, or export actions; actions are unattributable because the token is shared | @owner | ADMIN | open |  |
| ADMIN-P2-002 | P2 | Destructive actions are gated only in the browser; the API enforces nothing and deletes are irreversible with no undo | @owner | ADMIN | open |  |
| ADMIN-P2-003 | P2 | No audit trail for privileged/delete/export actions | @owner | ADMIN | open |  |
| ADMIN-P2-004 | P2 | Destructive actions gated only in the browser; deletes irreversible | @owner | ADMIN | open |  |
| ADMIN-P2-005 | P2 | Fail-open when no token; docs bind 0.0.0.0 | @owner | ADMIN | open |  |
| ADMIN-P2-006 | P2 | exec/shell is fleet-wide RCE with no approval and idle output is dropped | @owner | ADMIN | open |  |
| ADMIN-P2-007 | P2 | Operator token in URL/localStorage; no expiry, rotation, or lockout | @owner | ADMIN | open |  |
| AI-P2-001 | P2 | No PR, contribution, review or small-batch guidance; auto-tagging on direct main pushes means no human approval gate | @owner | AI | open |  |
| AI-P2-002 | P2 | No prompt-injection / untrusted-content guidance while agents are directed to read committed run logs and results | @owner | AI | open |  |
| AI-P2-003 | P2 | Agent instruction file misstates repository shape: 'a few runs' tracked vs 10,299 tracked result files (97.6% of the repo) | @owner | AI | open |  |
| AN-P2-001 | P2 | System inventory captures stable hardware identifiers and PII with no redaction switch, and committed examples expose a real GPU serial plus MAC/IP | @owner | AN | open |  |
| AN-P2-002 | P2 | Results (including full system inventory) are auto-published to a GitHub repository with no consent prompt and no minimization step | @owner | AN | open |  |
| AN-P2-003 | P2 | Control plane stores client IP, hostname and a persistent machine_id in SQLite with no retention or deletion policy | @owner | AN | open |  |
| API-P2-001 | P2 | Write endpoints perform no body validation: malformed JSON is treated as success | @owner | API | open |  |
| API-P2-002 | P2 | Run creation is not idempotent: a repeated client-supplied run id returns 500 and leaks the DB schema | @owner | API | open |  |
| API-P2-003 | P2 | DELETE /api/v1/runs/<id> leaves the run's log rows orphaned; the doc contract says '+data' | @owner | API | open |  |
| API-P2-004 | P2 | Realtime SSE fan-out silently drops events once a subscriber's queue fills (no backpressure, no metric) | @owner | API | open |  |
| ARCH-P2-001 | P2 | Single-node control plane with local SQLite and in-memory bus (SPOF, no backup) | @owner | ARCH | open |  |
| ARCH-P2-002 | P2 | Realtime SSE drops events silently and cannot resume | @owner | ARCH | open |  |
| ARCH-P2-003 | P2 | Operator token in URLs, logged in full, and wildcard CORS | @owner | ARCH | open |  |
| BP-P2-001 | P2 | Secret-bearing public-release workflows run with no environment approval gate | @owner | BP | open |  |
| BP-P2-002 | P2 | No Dependabot and all third-party actions are referenced by mutable tags | @owner | BP | open |  |
| BP-P2-003 | P2 | No documented branch/release/hotfix model or break-glass process | @owner | BP | open |  |
| CHAIN-P2-001 | P2 | The operator/exec chains are effectively silent: no audit trail or alerting for command issuance, no operator identity (single shared token), and exec output is dropped when no run is active | @owner | CHAIN | open |  |
| CI-P2-001 | P2 | Actions pinned to mutable tags, not commit SHAs | @owner | CI | open |  |
| CI-P2-002 | P2 | release.yml self-pushes to main with contents:write and no environment/reviewer gate | @owner | CI | open |  |
| CI-P2-003 | P2 | runner_labels input allows arbitrary/self-hosted runners; secrets inline in shell | @owner | CI | open |  |
| CI-P2-004 | P2 | No Dependabot/secret scanning/SBOM/CODEOWNERS; branch protection undocumented | @owner | CI | open |  |
| CTR-P2-001 | P2 | CI ISO build runs a --privileged container with the host repository bind-mounted read-write | @owner | CTR | open |  |
| CTR-P2-002 | P2 | Unpinned mutable base image tag (archlinux:latest) in the build container | @owner | CTR | open |  |
| CTR-P2-003 | P2 | bench-agent service runs unsandboxed with no runtime hardening profile while executing control-plane shell commands | @owner | CTR | open |  |
| DATA-P2-001 | P2 | No retention or aging policy for telemetry, logs, events or artifacts - the SQLite database grows without bound | @owner | DATA | open |  |
| DATA-P2-002 | P2 | Schema declares no foreign keys and never enables FK enforcement (PRAGMA foreign_keys = 0) | @owner | DATA | open |  |
| DATA-P2-003 | P2 | Migrations are best-effort additive ALTERs with no schema version tracking, rollback, or drift detection | @owner | DATA | open |  |
| DATA-P2-004 | P2 | Phase writes use a non-atomic check-then-insert with no UNIQUE(run_id, seq), so concurrent or replayed posts can create duplicate phase rows | @owner | DATA | open |  |
| DET-P2-003 | P2 | [PORT] CRLF committed for 11 file(s) (index has CRLF) | @owner | DET | open |  |
| DET-P2-005 | P2 | [SUPPLY] 9 GitHub Action ref(s) not pinned to a commit SHA | @owner | DET | open |  |
| DOC-P2-001 | P2 | Documented test command (`python tests/run_all.py`) fails on Windows: needs `windows-curses`, which the docs never say | @owner | DOC | open |  |
| DOC-P2-002 | P2 | README release/version is stale and self-contradictory (v1.1.0 vs VERSION 1.11.5 vs the 1.11.3 written directly below it) | @owner | DOC | open |  |
| DOC-P2-003 | P2 | docs/PHASE_TIMINGS.md reports the same preset on the same machine as both ~11.5 min and ~14.1 min, contradicting itself | @owner | DOC | open |  |
| DOC-P2-004 | P2 | LICENSE declares the repo PROPRIETARY AND CONFIDENTIAL while README instructs the public to clone and download its public releases | @owner | DOC | open |  |
| DR-P2-001 | P2 | Destructive deletes purge run data irreversibly with no snapshot, soft-delete, or confirmation | @owner | DR | open |  |
| DR-P2-002 | P2 | Schema has no version record and migrations are additive-only with no rollback path (bad-migration drill impossible) | @owner | DR | open |  |
| DR-P2-003 | P2 | Secrets have no backup/recovery or rotation procedure (per-runner keys live only in the DB) | @owner | DR | open |  |
| DR-P2-004 | P2 | No encryption at rest for the database, artifacts, or (hypothetical) backups | @owner | DR | open |  |
| EVOL-P2-001 | P2 | Adding a benchmark module/phase requires editing 6+ hardcoded lists; there is no registry or module template | @owner | EVOL | open |  |
| EVOL-P2-002 | P2 | No CI workflow runs the test suite, so platform changes are merged unverified | @owner | EVOL | open |  |
| EVOL-P2-003 | P2 | Schema 'migration' is unversioned, additive-only column checks run on every startup | @owner | EVOL | open |  |
| EVOL-P2-004 | P2 | Authorization is a hardcoded two-tier boolean checked per handler; no role/permission model to extend | @owner | EVOL | open |  |
| EVOL-P2-005 | P2 | Telemetry/summary metric catalogue is duplicated across Python and JavaScript with no single source of truth | @owner | EVOL | open |  |
| EXEC-P2-001 | P2 | Evidence binding gap: the run is pinned to b916709 but the working tree advanced 5 commits and findings reproduce at 60ab90eb/72c18734 | @owner | EXEC | open |  |
| EXEC-P2-002 | P2 | Published-artifact and privacy hygiene: ~9.5k generated files are tracked on a public repo with host/user identifiers | @owner | EXEC | open |  |
| FEAT-P2-001 | P2 | Deleting a run orphans its logs rows | @owner | FEAT | open |  |
| FILE-P2-001 | P2 | iso_fetch reports ok:true and acks "done" even when the ISO checksum is missing or mismatched | @owner | FILE | open |  |
| FILE-P2-002 | P2 | Artifact upload has no MIME/extension/size validation, no content-scanning hook, and no per-run quota | @owner | FILE | open |  |
| FILE-P2-003 | P2 | All file downloads are authorized by one static shared token carried in the query string, with no expiry, rotation, or revocation | @owner | FILE | open |  |
| HYGIENE-P2-001 | P2 | History is 94% auto-generated `bench:` commits | @owner | HYGIENE | open |  |
| HYGIENE-P2-002 | P2 | Duplicate nested `results/results/` tree | @owner | HYGIENE | open |  |
| HYGIENE-P2-003 | P2 | README release drift (v1.1.0 vs VERSION 1.11.3) | @owner | HYGIENE | open |  |
| HYGIENE-P2-004 | P2 | Stdlib-only test suite fails on Windows system Python | @owner | HYGIENE | open |  |
| INFRA-P2-001 | P2 | Documented BENCHD_DB config key is never read; DB path is hard-coded and has no backup/retention | @owner | INFRA | open |  |
| INFRA-P2-002 | P2 | Operator token is transported in URLs and kept in browser localStorage; no TLS/reverse proxy exists in the repo | @owner | INFRA | open |  |
| INFRA-P2-003 | P2 | benchd systemd unit runs as root on 0.0.0.0 with no User/CapabilityBoundingSet and no readiness probe | @owner | INFRA | open |  |
| INFRA-P2-004 | P2 | Deployment is an unversioned manual pct snippet that does not ship VERSION or write a commit stamp, breaking the fleet staleness comparison | @owner | INFRA | open |  |
| INV-P2-001 | P2 | Generated run output committed en masse | @owner | INV | open |  |
| INV-P2-002 | P2 | Recursively nested/duplicated result trees committed | @owner | INV | open |  |
| INV-P2-003 | P2 | No dependency manifest or lockfile | @owner | INV | open |  |
| INV-P2-004 | P2 | README version stale vs VERSION and tags | @owner | INV | open |  |
| IR-P2-001 | P2 | No monitoring or alerting: failures are only visible when a human watches the web dashboard | @owner | IR | open |  |
| IR-P2-002 | P2 | No backup or restore procedure for the control-plane SQLite database (all fleet history, artifacts and per-runner keys) | @owner | IR | open |  |
| IR-P2-003 | P2 | No operator audit log: privileged commands and destructive deletes carry no actor identity or durable trail | @owner | IR | open |  |
| IR-P2-004 | P2 | No data-breach or vulnerability-disclosure process, while a public repo bakes a world-readable operator token into ISO/app artifacts | @owner | IR | open |  |
| MOB-P2-001 | P2 | Primary tab bar cannot fit a phone: it is a non-wrapping flex row with no horizontal scroll | @owner | MOB | open |  |
| MOB-P2-002 | P2 | Fixed multi-column grids never collapse on phones, forcing horizontal overflow or unreadable cells | @owner | MOB | open |  |
| MOB-P2-003 | P2 | Interactive controls are below the 44x44px minimum touch target | @owner | MOB | open |  |
| MOB-P2-004 | P2 | Header and filter bars clip or overflow on narrow screens instead of wrapping | @owner | MOB | open |  |
| NOTIF-P2-001 | P2 | No out-of-band alert/notification delivery for critical health verdicts | @owner | NOTIF | open |  |
| OBS-P2-001 | P2 | No alerting or uptime monitoring for the control plane or for failed runs | @owner | OBS | open |  |
| OBS-P2-002 | P2 | No structured logging and no request IDs / correlation IDs | @owner | OBS | open |  |
| OBS-P2-003 | P2 | Server-side errors are swallowed; no error tracking or stack traces | @owner | OBS | open |  |
| OBS-P2-004 | P2 | /health conflates liveness and readiness and performs a DB query plus a network call | @owner | OBS | open |  |
| OBS-P2-005 | P2 | No runtime/service metrics and no monitoring-of-the-monitoring | @owner | OBS | open |  |
| ORCH-P2-001 | P2 | Published audit run uses two conflicting finding-ID schemes | @owner | ORCH | open |  |
| ORCH-P2-002 | P2 | risk_register.md is a verbatim copy of follow_up_register.md | @owner | ORCH | open |  |
| ORCH-P2-003 | P2 | Run INDEX and audit_manifest.json omit the deterministic lens artifacts | @owner | ORCH | open |  |
| PERF-P2-001 | P2 | Per-run detail, stats and CSV endpoints load and re-parse every telemetry row on the request thread | @owner | PERF | open |  |
| PERF-P2-002 | P2 | Realtime path scales by unbounded threads and broadcasts whole telemetry batches to every subscriber | @owner | PERF | open |  |
| PERF-P2-003 | P2 | CI rebuilds a multi-GB ISO and both app bundles on every bench/** or live/** push with no dependency caching | @owner | PERF | open |  |
| PERF-P2-004 | P2 | Heartbeat/liveness path performs a blocking GitHub compare call with an 8 s timeout, longer than the runner's 6 s client timeout | @owner | PERF | open |  |
| PRIV-P2-001 | P2 | Collectors capture stable hardware identifiers and PII with no redaction mode, and the uploader publishes the whole results directory to public GitHub | @owner | PRIV | open |  |
| PRIV-P2-002 | P2 | No attributable audit trail for privileged/admin actions (shared operator token, commands record no actor) | @owner | PRIV | open |  |
| PRIV-P2-003 | P2 | Deletion is incomplete: deleting a run leaves its console logs, and deleting a runner leaves its runs/telemetry/inventory | @owner | PRIV | open |  |
| PRIV-P2-004 | P2 | No retention or scheduled-purge policy for telemetry, logs, artifacts and the SQLite database | @owner | PRIV | open |  |
| PRIV-P2-005 | P2 | Per-runner API keys are stored in plaintext in SQLite and looked up by direct comparison | @owner | PRIV | open |  |
| REL-P2-001 | P2 | README's release/version strings are stale and self-contradictory, so the shipped docs disagree with VERSION | @owner | REL | open |  |
| REL-P2-002 | P2 | Release artifacts are tagged by workflow run number, not by version or commit, so notes cannot be tied to a build | @owner | REL | open |  |
| REL-P2-003 | P2 | Changelog input is unenforced: no PR/issue templates or CONTRIBUTING, and commit subjects are 94% auto-generated noise | @owner | REL | open |  |
| REL-P2-004 | P2 | No upgrade/rollback notes are possible: schema changes are unversioned additive ALTERs and the deploy does not ship VERSION | @owner | REL | open |  |
| REL-P2-005 | P2 | Release notes carry no generation metadata (commit/version/date), and the repo's only release-note-like artifact is a one-line verdict | @owner | REL | open |  |
| REL-P2-006 | P2 | No separate user/admin/operator/security note tracks; operator-mandated changes (token handling, exec/shell, deletes) have no release channel | @owner | REL | open |  |
| RES-P2-001 | P2 | A completed run is recorded as 'failed' and its summary lost when the final finish post fails (no retry/idempotency) | @owner | RES | open |  |
| RES-P2-002 | P2 | Backfill importer is not idempotent (re-running duplicates every run) and --reset deletes all history | @owner | RES | open |  |
| RES-P2-003 | P2 | agent 'start' has a TOCTOU race that can run two benchmark batteries concurrently on one machine | @owner | RES | open |  |
| RES-P2-004 | P2 | Documented rollback paths (A/B slot auto-revert, live toolkit self-update) are never exercised, and a bad toolkit update has no rollback | @owner | RES | open |  |
| SBOM-P2-001 | P2 | No package manifest or lockfile anywhere; dependencies are installed unpinned at runtime, so no reproducible dependency set exists to inventory | @owner | SBOM | open |  |
| SBOM-P2-002 | P2 | GitHub Actions dependencies are mutable major tags and there is no Dependabot, dependency-review or vulnerability scanning | @owner | SBOM | open |  |
| SBOM-P2-003 | P2 | No release provenance: no build attestation/signing, and app/ISO release tags are run-number based rather than commit-bound | @owner | SBOM | open |  |
| SBOM-P2-004 | P2 | No license policy, allow/deny list, CI license gate or exception process | @owner | SBOM | open |  |
| SC-P2-001 | P2 | No dependency manifest or lockfile; compute deps are pip-installed unpinned, sometimes with an extra index | @owner | SC | open |  |
| SC-P2-002 | P2 | GitHub Actions are pinned to mutable major tags and there is no dependency automation or dependency-review/license gate | @owner | SC | open |  |
| SC-P2-003 | P2 | bootstrap.py extracts a downloaded tarball without a safe extraction filter and its integrity check fails open | @owner | SC | open |  |
| SEARCH-P2-001 | P2 | No retention policy or cleanup job for logs, telemetry, artifacts or events - run data is kept forever | @owner | SEARCH | open |  |
| SEARCH-P2-002 | P2 | Deleting a runner orphans its runs, telemetry, logs and artifacts | @owner | SEARCH | open |  |
| SEARCH-P2-003 | P2 | Shared operator token is accepted in the URL query string and compared non-constant-time | @owner | SEARCH | open |  |
| SEC-P2-001 | P2 | Operator token in the URL query + cleartext logs over HTTP | @owner | SEC | open |  |
| SEC-P2-002 | P2 | Wildcard CORS on authenticated endpoints and SSE | @owner | SEC | open |  |
| SEC-P2-003 | P2 | No rate limiting or lockout | @owner | SEC | open |  |
| SEC-P2-004 | P2 | Unbounded request body (DoS) | @owner | SEC | open |  |
| SECRET-P2-001 | P2 | Placeholder token 'change-me' is accepted silently; no token strength/startup validation | @owner | SECRET | open |  |
| SECRET-P2-002 | P2 | No secret rotation / revocation / break-glass runbook or inventory | @owner | SECRET | open |  |
| TEST-P2-001 | P2 | Releases, tags and public ISO/app artifacts are published with no test or smoke verification of the artifact | @owner | TEST | open |  |
| TEST-P2-002 | P2 | Documented test command fails on Windows: suite needs third-party windows-curses but is described as stdlib-only | @owner | TEST | open |  |
| TEST-P2-003 | P2 | The 23 PowerShell battery scripts and the web dashboard are only validated by substring assertions, never executed or linted | @owner | TEST | open |  |
| USE-P2-001 | P2 | Control-plane commands report success on enqueue and never surface the runner's ack, so a rejected start/stop/exec looks successful | @owner | USE | open |  |
| USE-P2-002 | P2 | Web Start-run form has no input validation; blank/zero/negative durations and sizes are sent silently | @owner | USE | open |  |
| USE-P2-003 | P2 | GUI 'Clean up environment' deletes the cached runner interpreter with no confirmation and no in-run guard | @owner | USE | open |  |
| USE-P2-004 | P2 | Remote terminal / ad-hoc exec is only offered while a run is live, so idle runners cannot be diagnosed from the dashboard | @owner | USE | open |  |
| UX-P2-001 | P2 | Web dashboard's primary interactions are mouse-only (runner cards, sortable headers, table rows) | @owner | UX | open |  |
| UX-P2-002 | P2 | Modal dialog has no dialog semantics, no focus trap, and no focus restore | @owner | UX | open |  |
| UX-P2-003 | P2 | No ARIA anywhere in the web dashboard; tab strip and live SSE updates are not exposed to assistive tech | @owner | UX | open |  |
| UX-P2-004 | P2 | Canvas charts have no accessible alternative and their tooltips are pointer-only | @owner | UX | open |  |
| UX-P2-005 | P2 | Tk GUI suppresses the keyboard focus indicator and has no keyboard accelerators | @owner | UX | open |  |
| ACM-P3-001 | P3 | Inconsistent constant-time credential comparison (bearer uses compare_digest; ?token=, _runner_ok and _caller use ==) | @owner | ACM | open |  |
| ACM-P3-007 | P3 | Inconsistent constant-time token comparison | @owner | ACM | open |  |
| ADMIN-P3-001 | P3 | Inconsistent confirmation for destructive console actions (schedule delete has none) | @owner | ADMIN | open |  |
| ADMIN-P3-008 | P3 | Inconsistent confirmation (schedule delete has none) | @owner | ADMIN | open |  |
| AI-P3-001 | P3 | README release/version text is stale and contradicts VERSION, which agents are told is the single source of truth | @owner | AI | open |  |
| AI-P3-002 | P3 | Secrets guidance names only the ISO workflow, omitting that build-app.yml bakes the same world-readable token into public app bundles | @owner | AI | open |  |
| AN-P3-001 | P3 | No privacy/analytics governance artifacts (vendor list, consent, do-not-track, retention docs) and no privacy tests | @owner | AN | open |  |
| API-P3-001 | P3 | Error responses leak internal exception type and message; invalid client input returns 500 instead of 4xx | @owner | API | open |  |
| API-P3-002 | P3 | No rate limiting or request throttling on any endpoint; /health is unauthenticated | @owner | API | open |  |
| API-P3-003 | P3 | No machine-readable API contract (OpenAPI/schema); the prose contract already drifts from the handlers | @owner | API | open |  |
| ARCH-P3-001 | P3 | Documented topology drifts from code (dashboard commands; iso_write BENCHDATA guard) | @owner | ARCH | open |  |
| ARCH-P3-002 | P3 | Telemetry/logs/events have no retention or pruning | @owner | ARCH | open |  |
| BP-P3-001 | P3 | No CODEOWNERS file | @owner | BP | open |  |
| BP-P3-002 | P3 | No pull-request template or contributing guide | @owner | BP | open |  |
| CHAIN-P3-001 | P3 | Unauthenticated /health discloses deployment identity and fleet size, and every API response sets Access-Control-Allow-Origin: * | @owner | CHAIN | open |  |
| CI-P3-001 | P3 | Release tags do not map to a commit | @owner | CI | open |  |
| CTR-P3-001 | P3 | LXC deployment binds the control plane to 0.0.0.0 despite documented 'LAN/lab address only' posture | @owner | CTR | open |  |
| DATA-P3-001 | P3 | Request bodies are not validated as JSON objects (non-object body returns 500 + internal exception), and the documented BENCHD_DB setting is ignored | @owner | DATA | open |  |
| DATA-P3-002 | P3 | No optimistic locking or version preconditions on mutations; a late /finish can overwrite a reaped run's terminal status | @owner | DATA | open |  |
| DATA-P3-003 | P3 | Hard deletes with no soft-delete/tombstone and no audit fields on any table | @owner | DATA | open |  |
| DET-P3-001 | P3 | [DEP] No Dependabot configuration | @owner | DET | open |  |
| DET-P3-002 | P3 | [DEP] trivy not installed (dependency vuln scan skipped) | @owner | DET | open |  |
| DET-P3-004 | P3 | [SEC] gitleaks not installed (secret scan skipped) | @owner | DET | open |  |
| DOC-P3-001 | P3 | README 'Presets' table lists 11 presets but the GUI/TUI/web ship 13 - it omits 'Stabilized full soak (15 min)' and 'Graphics only (FurMark/Valley)' | @owner | DOC | open |  |
| DOC-P3-002 | P3 | AGENTS.md points to `update_ct.py`, which does not exist in the repository | @owner | DOC | open |  |
| DOC-P3-003 | P3 | No CONTRIBUTING/SECURITY/CHANGELOG or PR/issue templates, and no operator troubleshooting/rollback/incident runbook | @owner | DOC | open |  |
| DR-P3-001 | P3 | No DR runbook and no infrastructure-config backup; deployment is imperative/manual | @owner | DR | open |  |
| EVOL-P3-001 | P3 | Command kinds are a hardcoded tuple; clients cannot advertise command capability and silently fail unknown kinds | @owner | EVOL | open |  |
| EVOL-P3-002 | P3 | Vendored LibreHardwareMonitor binaries are git-ignored, so the app bundle is not reproducible from a clone despite docs claiming otherwise | @owner | EVOL | open |  |
| EVOL-P3-003 | P3 | No package structure; shared code is a 2.5k-line flat module imported via sys.path insertion | @owner | EVOL | open |  |
| FEAT-P3-001 | P3 | README preset table lists 11 of 13 presets | @owner | FEAT | open |  |
| FEAT-P3-002 | P3 | README release claim is stale | @owner | FEAT | open |  |
| FEAT-P3-003 | P3 | CONTROL_PLANE command-support matrix is stale | @owner | FEAT | open |  |
| FEAT-P3-004 | P3 | Committed audit finding CI-P3-001 contradicts the tree | @owner | FEAT | open |  |
| FEAT-P3-005 | P3 | Documented test command fails on stock Windows Python | @owner | FEAT | open |  |
| FEAT-P3-006 | P3 | Working tree diverges from the recorded commit | @owner | FEAT | open |  |
| FILE-P3-001 | P3 | Artifact metadata sha256 is client-supplied and never recomputed or verified on download | @owner | FILE | open |  |
| FILE-P3-002 | P3 | No per-artifact deletion, retention, or versioning; artifacts are purged only by deleting the whole run | @owner | FILE | open |  |
| FILE-P3-003 | P3 | Missing negative/authorization tests for the file surface and wildcard CORS on authenticated downloads | @owner | FILE | open |  |
| HYGIENE-P3-001 | P3 | Large monolithic modules with no internal split (benchreport.py 2,811 lines; app.js 1,822) | @owner | HYGIENE | open |  |
| HYGIENE-P3-002 | P3 | No CHANGELOG or ADRs; release notes are implicit in commit subjects | @owner | HYGIENE | open |  |
| HYGIENE-P3-003 | P3 | No type annotations and 238 broad `except Exception` handlers across the Python codebase | @owner | HYGIENE | open |  |
| INFRA-P3-001 | P3 | Live launcher exports BENCHD_INSECURE and BENCH_AGENT_NAME that nothing consumes (env name drift) | @owner | INFRA | open |  |
| INFRA-P3-002 | P3 | Environment-specific deploy values (container id 108, IP 192.168.222.188/24) are hard-coded in docs with no inventory, and a prior audit recorded a different address | @owner | INFRA | open |  |
| INV-P3-001 | P3 | Missing GitHub governance metadata | @owner | INV | open |  |
| INV-P3-002 | P3 | Large committed binary assets | @owner | INV | open |  |
| INV-P3-003 | P3 | Committed audit artifacts pinned to an old commit | @owner | INV | open |  |
| IR-P3-001 | P3 | Prior audit findings are all still marked open and were never re-verified, so the same incident class recurs | @owner | IR | open |  |
| MOB-P3-001 | P3 | No PWA surface at all: no manifest, icons, service worker, install prompt, or offline fallback | @owner | MOB | open |  |
| MOB-P3-002 | P3 | Fixed/sticky chrome ignores safe-area insets (notch, home indicator) | @owner | MOB | open |  |
| MOB-P3-003 | P3 | No mobile/responsive test coverage; the suite is source-string matching only | @owner | MOB | open |  |
| NOTIF-P3-001 | P3 | In-app SSE notification bus silently drops events when a subscriber queue fills | @owner | NOTIF | open |  |
| OBS-P3-001 | P3 | No audit log of operator / destructive command issuance | @owner | OBS | open |  |
| OBS-P3-002 | P3 | No incident runbook, escalation path, or on-call checklist | @owner | OBS | open |  |
| OBS-P3-003 | P3 | Release marker not bound in the documented copy-deploy; /health can report 0.0.0+unknown | @owner | OBS | open |  |
| ORCH-P3-001 | P3 | Deterministic finding DET-P3-002 is dropped from the aggregate | @owner | ORCH | open |  |
| ORCH-P3-002 | P3 | Published run was never reconciled after later commits fixed two findings | @owner | ORCH | open |  |
| PERF-P3-001 | P3 | Static dashboard assets are served with Cache-Control: no-store and no validators, so they are re-downloaded on every load | @owner | PERF | open |  |
| PERF-P3-002 | P3 | History and Fleet silently cap at 300/500 runs and ignore the server's total count | @owner | PERF | open |  |
| PRIV-P3-001 | P3 | Operator token is handled via URL query string and browser localStorage | @owner | PRIV | open |  |
| PRIV-P3-002 | P3 | No privacy/compliance documentation: data classification, retention policy, vendor/processor inventory, consent; secrets baked into public ISOs | @owner | PRIV | open |  |
| REL-P3-001 | P3 | No known-issues track and no breaking-change record; there is nothing to seed release notes from | @owner | REL | open |  |
| RES-P3-001 | P3 | Command queue is at-most-once with no DLQ/expiry; a fetched-but-unacked command is dropped, and a queued command never expires | @owner | RES | open |  |
| RES-P3-002 | P3 | Control-plane client has no retry/backoff/circuit-breaker; registration retries forever and telemetry is dropped on failure | @owner | RES | open |  |
| RES-P3-003 | P3 | HTTP server sets no read/connection timeout; a declared-but-unsent body pins a handler thread indefinitely | @owner | RES | open |  |
| SBOM-P3-001 | P3 | Live ISO package set is version-unpinned, so the shipped image is neither reproducible nor fully inventoried | @owner | SBOM | open |  |
| SC-P3-001 | P3 | ISO build trusts an unpinned third-party repo and an unpinned Docker base; no SBOM/provenance/checksums for app bundles | @owner | SC | open |  |
| SEARCH-P3-001 | P3 | History 'search' is client-side only, over a capped 300-row page - not server-side | @owner | SEARCH | open |  |
| SEARCH-P3-002 | P3 | Missing indexes on hot filter paths and no documented index ownership | @owner | SEARCH | open |  |
| SEC-P3-001 | P3 | Static-handler path-prefix check can be bypassed by a sibling dir | @owner | SEC | open |  |
| SECRET-P3-001 | P3 | Control-plane token exposed in URL query string and browser localStorage | @owner | SECRET | open |  |
| SECRET-P3-002 | P3 | Inconsistent token comparison and an unused BENCHD_INSECURE key | @owner | SECRET | open |  |
| SECRET-P3-003 | P3 | Per-runner API key stored in cleartext; 0600 chmod is a no-op on Windows | @owner | SECRET | open |  |
| TEST-P3-001 | P3 | The suite silently skips whole test groups, so lost coverage does not fail the run | @owner | TEST | open |  |
| TEST-P3-002 | P3 | Wall-clock/sleep based assertions make the suite flake-prone | @owner | TEST | open |  |
| TEST-P3-003 | P3 | No coverage measurement and no statement of what 'RESULT: PASS' does not cover | @owner | TEST | open |  |
| USE-P3-001 | P3 | Deleting a schedule is immediate with no confirmation, unlike every other destructive control | @owner | USE | open |  |
| USE-P3-002 | P3 | No completion notification for long runs; the only signal is the browser tab title | @owner | USE | open |  |
| USE-P3-003 | P3 | Compare gives no empty state, and with a single finished run it compares the run with itself and presents the 0% deltas as a comparison | @owner | USE | open |  |
| USE-P3-004 | P3 | README release/version strings are stale and mutually inconsistent with VERSION | @owner | USE | open |  |
| UX-P3-001 | P3 | No prefers-reduced-motion or prefers-color-scheme support; theme is fixed dark | @owner | UX | open |  |
| UX-P3-002 | P3 | Offline runner cards dimmed with opacity .55 drops muted metadata below AA contrast | @owner | UX | open |  |
| UX-P3-003 | P3 | No accessibility or visual-regression tooling or tests for any UI surface | @owner | UX | open |  |
