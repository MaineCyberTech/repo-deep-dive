# Patch plan

## CHAIN-P0-001 — Single shared secret is both the runner join token and the operator bearer, and it is baked into public app bundles / live ISOs -> anyone who downloads a release gets fleet-wide remote code execution (exec/shell) on every runner

Split the credential: keep a dedicated, narrowly scoped enrollment token for /register and issue per-runner API keys (already implemented) that CANNOT reach operator routes; require a separate operator secret (preferably per-user accounts) for /commands, schedules and deletes. Do not bake the operator token into any distributable artifact - bake only the enrollment token, and have the server refuse operator actions for enrollment-token bearers. Rotate the currently baked BENCHD_TOKEN and treat any distributed token as compromised.

## EXEC-P0-001 — Release gate = NO-GO: 3 unresolved P0s, all about one shared operator secret baked into public artifacts

Do not grant the current gate. Introduce a registration-only token that cannot act as operator, never bake an operator/PAT credential into any public artifact, rotate all currently shipped credentials (assume compromised), then re-run the gate.

## FINAL-P0-001 — One shared operator/join token is baked into public app bundles and the live ISO, so any release download yields fleet-wide remote code execution (merged across 10 domains)

Split the credential model: (1) a registration-only enrollment token accepted solely by POST /api/v1/register; (2) operator credentials (ideally per-user, hashed at rest) for commands/schedules/deletes; (3) never bake the operator token into any distributable artifact - bake only the enrollment token or nothing. Make the server refuse operator actions for enrollment-token bearers. Rotate the currently published BENCHD_TOKEN and treat it as compromised. Add a build-time guard that fails the app/ISO build if a shipped file matches the operator-token or GITHUB_TOKEN pattern.

## FINAL-P0-002 — A write-capable GitHub PAT is baked into the publicly downloadable live ISO, and runners auto-pull code from main, turning repo write into fleet code execution (merged across 4 domains)

Never bake a write-capable PAT into a distributable artifact. Have the uploader authenticate with a dedicated least-privilege identity (scoped GitHub App / deploy key behind an environment protection rule) or upload to a store that cannot influence what runners execute. Make the update sha256 mandatory (not optional), pin runner updates to signed releases/commits, and disable auto_update by default. Rotate the currently baked PAT out of band and assume it is compromised; extend the live/Build-LiveUSB.sh leak guard to cover airootfs credential files.

## SC-P0-001 — GitHub PAT with Contents:Read/Write is baked into the publicly-downloadable live ISO

Do not bake the GitHub PAT. Make upload credentials per-stick (BENCHDATA bench-upload.conf) or issue a short-lived, least-privilege, per-build token scoped to a separate upload-only repo/path. Rotate the currently-baked token out of band and assume it is compromised. Add a build-time assertion that fails the ISO build if any /etc/*.conf in airootfs contains GITHUB_TOKEN/AUTHORIZATION, and extend the live/Build-LiveUSB.sh leak guard to cover airootfs credentials, not just the toolkit copy.

## SEC-P0-001 — Operator token (and a repo-write GitHub PAT) baked into public release artifacts

Split the credential model: issue a limited, non-operator registration token for runners/UI and never bake the operator token into any released artifact. Move BENCH_UPLOAD_CONF out of the image (fetch at runtime or use a GitHub App with short-lived tokens). Rotate every token/PAT already published. Add a CI guard that fails the app/ISO build and the release step if any shipped file matches a known operator-token or GITHUB_TOKEN pattern.

## ACM-P1-001 — Shared join token is the full operator credential and is baked into public releases

Split the credential model: (1) a distinct, rotatable *registration/join* token that only authorises POST /register (least privilege); (2) operator tokens (ideally per-user, hashed at rest, see roadmap docs/CONTROL_PLANE.md:273-277) for control actions; (3) never bake the operator token into public artifacts - bake only the registration token, or use a per-runner enrolment code. Add a read-only viewer role for the dashboard. Document the role matrix.

## ACM-P1-002 — machine_id adoption hands out another runner's API key

Require proof of ownership for machine_id adoption exactly as for explicit runner_id (the row's existing api_key as body/bearer, or the operator token), OR make machine_id unforgeable (e.g. server-issued enrolment secret per runner, or a signed challenge). Add a regression test asserting a different runner's key cannot be recovered by claiming its machine_id.

## ADMIN-P1-001 — Shared all-powerful operator token is distributed to every runner

Split the secrets: a registration-only join token that runners use to obtain a scoped api_key, and a separate operator credential. Never persist the operator secret on runner machines. Move to per-user operator accounts with roles/scopes (the documented roadmap item) and support rotation.

## ADMIN-P1-002 — Runner identity takeover via machine_id

Require proof when adopting an existing row: bind machine_id to the key that first registered it, require the operator token (or a per-machine secret) to adopt a row the caller did not create, and never echo an existing api_key on an adoption the caller did not prove ownership of. Add a regression test mirroring tests/test_control_plane.py:46-71 but claiming machine_id instead of runner_id.

## AI-P1-001 — Test suite is documented as mandatory but no CI gate runs it, so an agent can land a red change on main

Add a required `.github/workflows/ci.yml` that runs on pull_request and push to main: `python tests/run_all.py`, `python -m py_compile bench/*.py server/*.py`, and `bash -n` on the shell scripts (mirroring AGENTS.md:166-170), on both ubuntu-latest and windows-latest. Mark it a required status check on main and make release.yml depend on it (`needs:` / workflow_run) so a red suite cannot produce a tag or bundles.

## API-P1-001 — POST /api/v1/register gives away another runner's api_key via unproven machine_id adoption

Require proof of ownership for machine_id-based adoption too: only adopt a row when the request already presents that row's api_key (or the operator token); otherwise mint a new row. Add the missing test (mirror tests/test_control_plane.py:49-61 but steal via machine_id instead of runner_id).

## ARCH-P1-001 — Single shared token is both the join credential and an all-powerful operator credential, and is shipped in public artifacts

Split credentials by role: a read-only/viewer token for dashboards and CI-baked agent configs, a separate operator token never shipped in artifacts, and per-runner keys (already present) for agents. Do not bake the operator token into public bundles/ISOs. Keep exec/shell/iso_write/reboot behind the operator tier and require explicit confirmation. Rotate the currently published token.

## BP-P1-001 — No test/CI workflow exists, so no required status check can gate merges to main

Add a pinned CI workflow (`.github/workflows/ci.yml`) that runs `python tests/run_all.py`, `python -m py_compile bench/*.py server/*.py` and `bash -n` on the shell scripts, then enable it (and any PSScriptAnalyzer/gitleaks jobs) as required status checks on the protected main branch.

## BP-P1-002 — Release workflow writes directly to main and cuts tags with no approval or documented bypass

Decide the branch model explicitly and document it (main/develop/release/hotfix + break-glass). Move the release mutation behind a protected `environment: release` with required reviewers (or grant a narrowly-scoped, audited bypass actor), and document how the automated VERSION commit reconciles with required reviews.

## CHAIN-P1-001 — Runner identity takeover via /register machine_id adoption: any authenticated runner can claim another runner's row and is handed that row's api_key (the runner_id path was fixed, the machine_id path was not)

Require proof of ownership on the machine_id branch too: only adopt an existing machine_id row when the request presents that row's own api_key as bearer/body (as the runner_id branch now does), or gate adoption behind the operator credential. For a live stick with no persisted config, enroll with a per-machine one-time token or require operator adoption. Add tests mirroring tests/test_control_plane.py:46-68 for the machine_id path.

## CHAIN-P1-002 — A Contents:Read/Write GitHub PAT is baked into the public live ISO and every runner auto-pulls code from main at startup -> repo write access becomes code execution on the whole fleet (CI-to-production / supply-chain chain)

Never bake a write-capable PAT into a distributable artifact. Give the uploader a dedicated identity with the least privilege it needs (and a scoped, revocable GitHub App / deploy key with an environment protection rule), or upload to a branch/artifact store that cannot influence what runners execute. Pin runner updates to signed releases or an explicit commit + required sha256 (make the sha256 mandatory, not optional) and disable auto_update by default.

## CI-P1-001 — Build workflows bake live credentials into public release artifacts

Do not bake long-lived credentials into published artifacts. Provision config at first boot/registration (or fetch a short-lived, per-device token from the control plane after install), keep the ISO/app releases private if they must carry secrets, and rotate BENCH_AGENT_CONF/BENCH_UPLOAD_CONF. If baking is unavoidable short-term, restrict the PAT to a dedicated, non-default branch/path and add explicit rotation runbook steps.

## CI-P1-002 — No test/lint/secret-scan CI gate; nothing runs on pull_request

Add `.github/workflows/ci.yml` triggered on `pull_request` and `push` that runs the documented commands (`python tests/run_all.py`, `python -m py_compile bench/*.py server/*.py`, `bash -n bench/Run-LinuxBench.sh live/Build-LiveUSB.sh live/airootfs/usr/local/bin/bench-*`) plus gitleaks and actionlint, with all actions pinned to commit SHAs. Make it a required status check on main.

## CTR-P1-001 — Control-plane and upload bearer tokens are baked into the publicly downloadable live ISO image

Stop baking long-lived tokens into the image. Ship a one-time enrollment token (or per-stick credential generated on first boot and exchanged for a short-lived key), inject BENCH_AGENT_CONF at runtime from a mounted config, and add an automatic rotation/deletion step for the build secret after the release. At minimum, gate ISO publishing on a truncated/least-privilege token and document a mandatory rotation on every public release.

## DATA-P1-001 — DELETE /api/v1/runs/<id> does not delete the run's logs; they stay orphaned in the DB and remain readable

Add 'logs' (and any commands rows keyed by run_id) to the delete loop, or add FOREIGN KEY(run_id) REFERENCES runs(id) ON DELETE CASCADE with PRAGMA foreign_keys=ON. Add a regression test that deletes a run and asserts zero rows remain in every run-scoped table (phases, telemetry, logs, events, artifacts) and that GET /runs/<id>/logs returns 404.

## DR-P1-001 — No backup of the control-plane SQLite database, which is the single system of record

Add a documented, scheduled backup of benchd.sqlite using the online-backup API (sqlite3 '.backup' or VACUUM INTO) rather than a raw cp of a WAL database, writing timestamped copies off the host; ship a systemd timer + a small stdlib script (e.g. server/backup_benchd.sh/.py), set a retention count, and reference it from docs/CONTROL_PLANE.md. Add an integrity check (PRAGMA integrity_check) on the backup.

## DR-P1-002 — Restore is never exercised: no restore script, runbook, or test; the only import path cannot rebuild the DB

Write docs/DR_RUNBOOK.md with an explicit backup->restore procedure, add a `restore_benchd` step (drop-in replacement DB + service restart), and add a test (e.g. tests/test_backup.py) that backs up a populated test DB, deletes it, restores it, and asserts row counts + an artifact sha256 match. Record the last real restore date in the runbook or a status file so 'not exercised' can never silently persist.

## EXEC-P1-001 — Cross-domain convergence: a single shared BENCHD_TOKEN serves both the low-trust join tier and the highest-privilege operator tier

Treat credential-model split as the top remediation: per-role tokens (viewer / operator never shipped, registration-only for runners), per-runner API keys (already exist) that cannot reach operator routes, per-user operator accounts, and key expiry/rotation/revocation.

## EXEC-P1-002 — Runner identity takeover via POST /register machine_id adoption is unfixed and gives an attacker another runner's API key

Require proof of ownership (the row's own api_key or the operator credential) on the machine_id branch, exactly as the runner_id branch now does; add the missing regression test.

## EXEC-P1-003 — No CI test/quality gate: main merges and auto-releases land with zero automated verification

Add a required ci.yml (pull_request + push) running tests/run_all.py, py_compile and bash -n on ubuntu + windows, plus gitleaks/actionlint with actions pinned to SHAs; gate release.yml/build-* on it.

## EXEC-P1-004 — Disaster recovery is absent: the single SQLite system of record has no backup, no restore, and no exercise

Add a scheduled online-API backup (sqlite3 .backup / VACUUM INTO) with retention off-host, a restore script + runbook, and a test that backs up, deletes, restores and asserts row counts and an artifact hash.

## FINAL-P1-001 — Control plane fails open: with no BENCHD_TOKEN it serves the full operator API unauthenticated while bound to 0.0.0.0 (reproduced across 4 domains)

Fail closed: refuse to start (or bind loopback only) unless BENCHD_TOKEN is set and non-default; reject the 'change-me' placeholder from benchd.conf.example. Require an explicit --allow-anonymous/--insecure flag for local development, log the effective bind/auth mode on startup, and add a systemd ExecStartPre/condition that the token file exists. Add a test that the server refuses to open when the token is unset.

## FINAL-P1-002 — Any enrolled runner can take over another runner's identity via unproven machine_id adoption and be handed that runner's api_key (merged across 5 domains)

Require proof of ownership on the machine_id branch exactly as for runner_id (the row's own api_key as bearer/body, or the operator credential); otherwise mint a new row. Never echo an existing api_key on an adoption the caller did not prove. For ephemeral live sticks, use a per-machine one-time enrollment token or require operator adoption. Add a regression test mirroring tests/test_control_plane.py:46-68 but claiming machine_id.

## FINAL-P1-003 — No CI test/lint/secret gate, while the release workflow self-modifies main and auto-tags with no approval (merged across 5 domains)

Add a pinned `.github/workflows/ci.yml` running on pull_request and push to main: `python tests/run_all.py`, `python -m py_compile bench/*.py server/*.py packaging/*.py`, and `bash -n` over bench/*.sh + live/*.sh, on ubuntu-latest and windows-latest, plus gitleaks/actionlint. Pin all actions to commit SHAs. Enable it as a required status check on protected main and make release/build workflows depend on it. Move the automated VERSION commit/tag behind a protected `environment: release` with reviewers, and document the branch model and break-glass procedure.

## FINAL-P1-004 — Data lifecycle is unmanaged: run delete leaves logs behind (reproduced), telemetry/artifacts have no retention, and there is no backup, restore, or incident plan (merged across 6 domains)

Add a single explicit list of every run-scoped table to the delete path (or FK ON DELETE CASCADE with PRAGMA foreign_keys=ON), and fix the docs. Add a retention policy (keep N days/runs, downsample old telemetry, store artifacts on the filesystem with the DB holding a path), a scheduled VACUUM, and DB-bytes/rootfs-free warning bands on /health. Add a documented scheduled backup using the SQLite online-backup API and a restore runbook + test (backup, delete, restore, assert row counts + artifact sha256). Write docs/INCIDENT_RESPONSE.md (SEV scale, roles, containment, comms, postmortem).

## FINAL-P1-005 — The most destructive operation fails open on integrity checks, and third-party code is fetched and executed without verification; no SBOM or license inventory exists (merged across 4 domains)

Make the ISO verdict binding: return ok:False on sha256 mismatch, fail closed when SHA256SUMS is absent, have the agent treat verified=False as failed, and assert ok is False in tests. Pin exact third-party releases and verify a committed SHA-256/Authenticode signature before Expand-Archive/Add-Type or task registration; fail closed on mismatch. Add an SBOM step (e.g. syft/CycloneDX) plus a NOTICE/license file to both build workflows, and a CI check that every bundled binary has a license entry.

## FINAL-P1-006 — ~10,000 generated result files (~55 MB, with machine PII) are committed to a public repo despite a results/ ignore rule (merged across 6 domains)

Untrack the generated tree (`git rm -r --cached results/`), keep the .gitignore entry, and publish run output as CI/release artifacts (or a separate results repo/branch) instead of on main; add a CI guard that fails if a PR stages files under results/. Add a redaction pass (basename/relative paths only; strip usernames, absolute home paths, hostnames, serials, MACs) before output is written, and scrub the committed examples/results. Reconcile the count and CRLF state against one commit stamp.

## HYGIENE-P1-001 — 9,555 generated result files (~55 MB) committed under results/

Untrack the generated tree (`git rm -r --cached results/`), keep the `.gitignore` entry, and publish run output as CI/release artifacts (or a separate results repo/branch) instead of on main. Add a CI guard that fails if a PR stages files under `results/`. Keep only the small curated set already mirrored in `examples/`.

## INFRA-P1-001 — benchd fails open: with no BENCHD_TOKEN it serves the full operator API unauthenticated (reproduced)

Fail closed: if no token is resolved, refuse to start unless an explicit --insecure/--no-auth flag is passed (and bind to 127.0.0.1 in that mode). Document BENCHD_TOKEN as mandatory and add a systemd ExecStartPre or unit condition that the token file exists. Add a test that the server refuses to open when the token is unset.

## INFRA-P1-002 — The shared operator token is baked into publicly downloadable app bundles and the live ISO, and it is the same token that grants operator control

Introduce a distinct, registration-only token that cannot authenticate as an operator, and bake only that into public artifacts (or omit credentials from public builds entirely). Rotate the current BENCHD_TOKEN. Document clearly that any token shipped in a public release must be non-operator.

## INV-P1-001 — Shared control-plane token baked into public releases

Never bake a token with operator/web-UI scope into a public artifact. Issue per-runner API keys at first registration (server side), bake only a low-privilege enrolment token or a one-time claim code, scope the baked credential to runner-registration only, and add a CI gate that fails if BENCH_BAKE_AGENT_CONF contains the operator token. Document the required token scopes in docs/CONTROL_PLANE.md.

## IR-P1-001 — No incident-response documentation, severity taxonomy, roles, or postmortem process exists anywhere in the repository

Add docs/INCIDENT_RESPONSE.md defining severity (SEV1-4), roles (incident commander/comms/scribe), containment/escalation, and a comms + blameless-postmortem template; link it from README and AGENTS.md and run the scenarios in this report as a tabletop.

## PERF-P1-001 — Unbounded SQLite growth: telemetry/logs/events/artifacts have no retention, cap, or capacity signal

Add a retention policy (keep N days / N runs per host, downsample older telemetry to 1/N rows, drop console bodies > horizon), store artifacts on the filesystem with the DB holding only a path, run a scheduled VACUUM/incremental_vacuum, and expose DB bytes + row counts + rootfs free on /health with documented warn/critical thresholds.

## PERF-P1-002 — Web dashboard re-fetches 300 full run rows and an unbounded /trends scan on every refresh tick

Fetch per tab only when it is activated/visible; add pagination to History and a LIMIT/host-filter to /trends (and/or a cached materialized trends table refreshed at write time); keep /runs list responses to light fields and fetch summary/detail lazily; slow the heartbeat-driven refresh (e.g. do not publish an SSE event on every heartbeat).

## PRIV-P1-001 — Unredacted hostnames and absolute home paths (usernames) committed to the public repository

Scrub committed examples/results of usernames, absolute home paths and hostnames (keep only basename/relative paths), add a redaction pass before output is written, and stop force-adding run output under results/ — keep it git-ignored.

## REL-P1-001 — No CHANGELOG and no release notes are generated for version tags; release.yml only cuts a bare tag

Add a `CHANGELOG.md` in Keep a Changelog format and make `release.yml` create a GitHub Release for the `vX.Y.Z` tag with a generated body (conventional-commit grouping: feat/fix/perf/breaking/CVE), plus a lint that fails if VERSION was bumped without a changelog entry. Exclude `bench:` commits from generation.

## RES-P1-001 — iso_fetch returns ok=True even when SHA256SUMS verification fails, so a bad ISO is accepted for a destructive write

Make the verdict binding: on `verified is False` return `{"ok": False, "error": "sha256 mismatch (expected %s, got %s)"}`, and fail closed when SHA256SUMS is absent (require an expected hash). Have agent/_update_and_ack treat `verified is False` as failed, and update tests/test_update.py to assert `ok` is False on mismatch.

## SBOM-P1-001 — No SBOM is produced for either shipped artifact set (PyInstaller app bundles and the live ISO)

Add an SBOM step to both build workflows (e.g. syft/CycloneDX) over the built artifacts (pip freeze of the runner venv, the bundle contents, and the pacman package list) and attach the SBOM (plus its sha256) to the same release as the artifact; keep it alongside SHA256SUMS so SBOM and binary bind to the same build.

## SBOM-P1-002 — Third-party binary LibreHardwareMonitor is redistributed in release bundles with no tracked license/attribution (MPL-2.0 compliance gap)

Track the vendored LHM tree (or pin+hash the exact upstream release), record each component's name/version/license in a third-party NOTICE/attribution file shipped in the bundle, and add a CI check that fails if a bundled binary has no corresponding license entry. Reconcile the proprietary LICENSE with the OSS components actually distributed.

## SC-P1-001 — Control-plane operator token is baked into public app bundles

Stop baking BENCHD_TOKEN into public artifacts; ship an empty bench-agent.conf.example and require per-host enrollment, or issue a dedicated low-privilege runner-enrollment key that cannot act as the operator token. Rotate the baked token and remove the token from already-published bundles.

## SC-P1-002 — Third-party binaries are downloaded and executed without integrity verification (LibreHardwareMonitor 'latest', nvfancontrol)

Pin an exact release and verify a committed SHA-256 (or Authenticode/MSIX signature) before Expand-Archive/Add-Type; fail closed on mismatch. Do the same for nvfancontrol before registering the logon task. Add a test that asserts each download URL is version-pinned and paired with a hash.

## SEARCH-P1-001 — Deleting a run does not delete its console logs; they stay retrievable by run id

Add 'logs' to the delete table list in server/benchd.py (and make it a single explicit list of every run-scoped table so future tables cannot be missed); optionally delete orphaned logs defensively. Update docs/CONTROL_PLANE.md:132 to state exactly which tables are removed. Add a regression test asserting GET /api/v1/runs/<id>/logs returns 404 (or empty) after the run is deleted.

## SEC-P1-001 — Fail-open authentication when no token is configured

Fail closed: refuse to start (or bind loopback only) unless BENCHD_TOKEN is set and non-default; reject the 'change-me' placeholder from benchd.conf.example. Require an explicit --allow-anonymous flag for local development, and log the effective host/bind mode on startup.

## SEC-P1-002 — /api/v1/register discloses other runners' API keys

Never return an existing api_key from /register. Honor an explicit runner_id or a machine_id match only when the request presents the matching api_key (compare with secrets.compare_digest) or the operator token. Rotate keys after the fix and add a regression test that a second runner's key cannot adopt the first runner's row.

## SECRET-P1-001 — Shared operator/join token is baked into public app release bundles

Do not bake a shared operator token into public artifacts. Introduce a distinct, runner-scoped bootstrap/registration token (accepted only by POST /api/v1/register, unable to act as operator), or have the bundle ship empty and prompt for config. If a token must ship, generate a per-build token and document its immediate revocation.

## SECRET-P1-002 — Write-capable GitHub PAT is baked into the public live-USB ISO

Never bake a long-lived write PAT into a public image. Upload results via a short-lived token, a GitHub App installation token minted at boot, or a dedicated results-only repository with minimum scope; otherwise ship the ISO with no upload credentials and have the operator drop bench-upload.conf on BENCHDATA. Document and test revocation of the baked PAT.

## TEST-P1-001 — No CI job runs the test suite or any compile/lint gate

Add .github/workflows/ci.yml on push/PR running on ubuntu-latest + windows-latest: `python tests/run_all.py`, `python -m py_compile bench/*.py server/*.py packaging/*.py`, and `bash -n` over bench/*.sh + live/*.sh. Make it a required status check on main and add `needs: ci` to release.yml, build-iso.yml and build-app.yml.

## ACM-P2-001 — No lifecycle for runner API keys or the operator token: no expiry, rotation, or per-key revocation; keys stored in plaintext

Add key metadata (created/last-used/expiry), a rotate endpoint that issues a new key and invalidates the old, and a revoke-key endpoint that keeps the runner row. Store only a hash of the key. Add the same for operator tokens (multiple named tokens with scopes). Document the lifecycle.

## ACM-P2-002 — Control plane fails open: with no BENCHD_TOKEN every request is a full operator (RCE/reboot/delete), and the shipped unit binds 0.0.0.0

Refuse to start (or bind loopback only and refuse network registration) when BENCHD_TOKEN is unset unless an explicit `--allow-open` flag is passed; make the systemd unit require the conf file (e.g. EnvironmentFile= and a ConditionPathExists). Add a test for the no-token path.

## ACM-P2-003 — No credential lifecycle (expiry/rotation/revocation); keys plaintext

Add an audit table (ts, actor token label/IP, method, route, resource id, action, outcome) and write to it for every state-changing API call, command issuance and delete; expose it read-only in the dashboard. Tie actor identity to named operator tokens when the roadmap per-user logins land.

## ACM-P2-004 — Fail-open when no token is set, on a 0.0.0.0 unit

Issue short-lived, purpose-scoped download/stream tickets instead of the operator token in URLs; drop the `Access-Control-Allow-Origin: *` wildcard (or restrict it to configured origins); keep credentials in the Authorization header where possible. Document that the token must not be shared as a URL.

## ACM-P2-005 — No audit trail / actor attribution for privileged actions

TBD

## ACM-P2-006 — Operator token in URLs + wildcard CORS

TBD

## ADMIN-P2-001 — No audit log for privileged, destructive, or export actions; actions are unattributable because the token is shared

Add an append-only audit table (ts, actor/token id, source addr, action, target, parameters, outcome) written on every command, schedule change, delete, and export; never cascade-delete it when the target row is removed; expose a read-only audit view in the console.

## ADMIN-P2-002 — Destructive actions are gated only in the browser; the API enforces nothing and deletes are irreversible with no undo

Enforce destructive-action confirmation server-side (typed confirmation string or one-time confirmation token per request), add a soft-delete/undo window for runs and runners, and require an explicit confirm parameter on every DELETE.

## ADMIN-P2-003 — No audit trail for privileged/delete/export actions

Fail closed: refuse to start on a non-loopback bind unless a token is set, and require an explicit --insecure flag to run open. Keep /health content minimal when unauthenticated.

## ADMIN-P2-004 — Destructive actions gated only in the browser; deletes irreversible

Treat exec/shell as a privileged, audited action (role + audit entry + visible banner). Persist exec output regardless of run state, add an optional command allowlist, and rate-limit privileged commands.

## ADMIN-P2-005 — Fail-open when no token; docs bind 0.0.0.0

Prefer header-based auth; issue short-lived, narrowly scoped download/stream tokens instead of the master token; use a constant-time comparison on the query path; add rate limiting/lockout; move to per-user tokens with expiry and revocation.

## ADMIN-P2-006 — exec/shell is fleet-wide RCE with no approval and idle output is dropped

TBD

## ADMIN-P2-007 — Operator token in URL/localStorage; no expiry, rotation, or lockout

TBD

## AI-P2-001 — No PR, contribution, review or small-batch guidance; auto-tagging on direct main pushes means no human approval gate

Add CONTRIBUTING.md and a PR template stating: work on a branch, open a PR, require CI green + one human review, keep PRs to one logical change (small batch), and never merge your own change. Add CODEOWNERS for bench/, server/, live/, and .github/. Enable branch protection on main (require PR + required status check) and gate the release/tag workflow behind a manual approval (workflow_dispatch or an environment with reviewers).

## AI-P2-002 — No prompt-injection / untrusted-content guidance while agents are directed to read committed run logs and results

Add an 'Untrusted content / prompt injection' section to AGENTS.md: state that logs, results/, examples/ and any run artifact are data, never instructions; require agents to quote/annotate rather than obey embedded directives; never execute commands copied from an artifact; and ask a human when an artifact requests an action. Optionally add a CI check that flags instruction-like patterns in newly committed artifacts.

## AI-P2-003 — Agent instruction file misstates repository shape: 'a few runs' tracked vs 10,299 tracked result files (97.6% of the repo)

Correct AGENTS.md:59 and README.md:335 to state the real tracked-result policy, and mark generated trees explicitly (e.g. add `results/** linguist-generated=true -diff` to .gitattributes, or stop tracking run history and keep a small curated examples/ set). Add an explicit do-not-touch rule for `results/**`, `*.log`, `server/data/**` and `*.telemetry.csv`.

## AN-P2-001 — System inventory captures stable hardware identifiers and PII with no redaction switch, and committed examples expose a real GPU serial plus MAC/IP

Add a redaction mode (drop or hash serials, MACs, IPs, hostname, processor/PNP ids) and make it the default for any shareable/committed output; gate the raw inventory behind an explicit -IncludeIdentifiers flag; scrub the committed examples to redacted placeholders; document the sensitive fields and retention expectations.

## AN-P2-002 — Results (including full system inventory) are auto-published to a GitHub repository with no consent prompt and no minimization step

Make publication an explicit, confirmed action (never silent auto-upload), run a mandatory redaction/minimization pass before any upload, require a private destination by default, show the exact file/field set being published, and document consent/retention for uploaded data.

## AN-P2-003 — Control plane stores client IP, hostname and a persistent machine_id in SQLite with no retention or deletion policy

Define and document a retention policy (e.g. keep telemetry for N days, purge logs/artifacts after M) and implement a scheduled prune; document that addr is a client IP and consider not persisting it (or hashing it) unless needed; add a purge/export command for operator data-subject requests.

## API-P2-001 — Write endpoints perform no body validation: malformed JSON is treated as success

Raise a 400 from _body() on parse failure and on a non-object top level; validate required types per route (str for level/message/stream, list of dicts/floats for samples, numeric seq/ts) and return 400 with a structured error instead of catching the exception into a 500.

## API-P2-002 — Run creation is not idempotent: a repeated client-supplied run id returns 500 and leaks the DB schema

Make POST /api/v1/runs upsert/return-existing on a repeated id (INSERT ... ON CONFLICT(id) DO NOTHING then read back, returning 200 with the existing run_id), and have the reporter send a client-generated id so retries are idempotent.

## API-P2-003 — DELETE /api/v1/runs/<id> leaves the run's log rows orphaned; the doc contract says '+data'

Add 'logs' to the delete loop (server/benchd.py:668); optionally add a foreign-key/ON DELETE CASCADE or a periodic orphan sweep, and reconcile the run detail/logs queries. Update docs/CONTROL_PLANE.md:132 or make it true.

## API-P2-004 — Realtime SSE fan-out silently drops events once a subscriber's queue fills (no backpressure, no metric)

Count drops (per-subscriber) and expose them (e.g. a 'lagged' SSE event or /metrics counter); either coalesce telemetry into the latest-only value for slow subscribers, or close/resync a lagging stream with an explicit 'resync' event so the client refetches /state.

## ARCH-P2-001 — Single-node control plane with local SQLite and in-memory bus (SPOF, no backup)

State the accepted RPO/RTO for a lab tool and back it with a scheduled `sqlite3 data/benchd.sqlite '.backup'` to a second volume (systemd timer), plus a documented restore step. If redundancy is ever required, make the scheduler a single leader and move the bus to a shared store.

## ARCH-P2-002 — Realtime SSE drops events silently and cannot resume

Add a monotonic per-run sequence and SSE `id:`, honour Last-Event-ID to replay from the store, and on overflow drop-oldest while counting and surfacing skipped events (e.g. a 'gap' event that forces a resnapshot).

## ARCH-P2-003 — Operator token in URLs, logged in full, and wildcard CORS

Redact query tokens in log_message; pass the token in the Authorization header or a cookie for the UI instead of the URL; restrict Access-Control-Allow-Origin to the dashboard origin (or drop CORS entirely) rather than '*'. Prefer short-lived download URLs over long-lived tokens in links.

## BP-P2-001 — Secret-bearing public-release workflows run with no environment approval gate

Attach a protected GitHub `environment` (required reviewers + deployment branch/tag rules) to the release/attach jobs in build-iso.yml and build-app.yml so secret exposure requires approval; prefer short-lived, rotatable, least-privilege tokens and consider not baking them for public releases at all.

## BP-P2-002 — No Dependabot and all third-party actions are referenced by mutable tags

Add `.github/dependabot.yml` (github-actions ecosystem, weekly) and pin every `uses:` to a full commit SHA with a Dependabot-maintained version comment; make the Dependabot PRs pass the CI check added for the P1 no-CI finding.

## BP-P2-003 — No documented branch/release/hotfix model or break-glass process

Add a short docs/BRANCHING.md (or CONTRIBUTING.md) that names the branches (main/release/hotfix or a documented main-only model), the required checks and review count, tag/release authority, and a break-glass procedure (who may merge/tag without review, how it is recorded and back-filled).

## CHAIN-P2-001 — The operator/exec chains are effectively silent: no audit trail or alerting for command issuance, no operator identity (single shared token), and exec output is dropped when no run is active

Add a server-side audit event for every command issuance and every exec/shell/iso_write/reboot (actor, runner, kind, payload hash, timestamp) exposed in the dashboard and emitted to the log; retain exec output out-of-band from runs; add alerting for destructive command kinds and for repeated failed auth. Per-user operator accounts (currently Roadmap) are required for real attribution.

## CI-P2-001 — Actions pinned to mutable tags, not commit SHAs

Pin every `uses:` to a full 40-char commit SHA with a trailing `# vX.Y.Z` comment, and add Dependabot (`github-actions` ecosystem) to keep pins fresh. Least-privilege: reduce `contents: write` to job level and only where the release/tag step needs it.

## CI-P2-002 — release.yml self-pushes to main with contents:write and no environment/reviewer gate

Gate the push/tag job behind a protected GitHub Environment with required reviewers, scope the token to the minimum (or use a dedicated deploy key), prefer opening a PR for the VERSION bump instead of committing to main, and document branch-protection exceptions for the release bot explicitly.

## CI-P2-003 — runner_labels input allows arbitrary/self-hosted runners; secrets inline in shell

Constrain `runner_labels` to an allowlist check (or a `choice` input) and reject `self-hosted` for secret-bearing jobs unless the runner is explicitly trusted. Pass secrets via `env:` and reference `$BENCH_UPLOAD_CONF` in the script; never interpolate `secrets.*` into `run:` text.

## CI-P2-004 — No Dependabot/secret scanning/SBOM/CODEOWNERS; branch protection undocumented

Enable Dependabot (pip + github-actions), GitHub secret scanning + push protection, and CodeQL/code scanning; add a `.github/CODEOWNERS` for `.github/**`, `live/**`, and `packaging/**`; and add a short `docs/CI.md` listing the required status checks and branch-protection policy.

## CTR-P2-001 — CI ISO build runs a --privileged container with the host repository bind-mounted read-write

Drop --privileged; grant only the capabilities actually needed (CAP_SYS_ADMIN + loop/mount for mkarchiso) and use a scoped /dev/loop* passthrough, or run the build on the dedicated Arch runner (build_native path) exclusively. Mount the source read-only and copy into a container-local scratch dir instead of writing back into $REPO; pin the base image by digest (see separate finding).

## CTR-P2-002 — Unpinned mutable base image tag (archlinux:latest) in the build container

Pin the base image by digest (e.g. archlinux@sha256:...) in live/ci-build.sh, or publish a controlled builder image and reference its digest; record the digest in the build log/artifact metadata. Combine with the least-privilege change above.

## CTR-P2-003 — bench-agent service runs unsandboxed with no runtime hardening profile while executing control-plane shell commands

Add a systemd hardening block to server/bench-agent.service: User=/DynamicUser where feasible, NoNewPrivileges=true, ProtectSystem=strict + ReadWritePaths for the results/work dirs, ProtectHome, PrivateTmp, PrivateDevices (GPU paths need /dev/nvidia* so scope carefully), ProtectKernelTunables/Modules, RestrictSUIDSGID, SystemCallFilter=@system-service, and a CapabilityBoundingSet=~. Run exec jobs in a dedicated, least-privilege worker. Mirror the same profile for the live-USB units.

## DATA-P2-001 — No retention or aging policy for telemetry, logs, events or artifacts - the SQLite database grows without bound

Add a retention job (e.g. keep N days of telemetry/logs, or cap rows per run) with an explicit owner, expose the window via config (e.g. BENCHD_RETENTION_DAYS), document the policy in docs/CONTROL_PLANE.md/deployment notes, and add a boundary test that seeds mixed fresh/expired rows and asserts only expired rows are removed.

## DATA-P2-002 — Schema declares no foreign keys and never enables FK enforcement (PRAGMA foreign_keys = 0)

Add FOREIGN KEY(run_id) REFERENCES runs(id) ON DELETE CASCADE (and runner_id references where applicable) and set PRAGMA foreign_keys=ON immediately after connecting. Add a test that inserts a child row, deletes the parent, and asserts the child is gone.

## DATA-P2-003 — Migrations are best-effort additive ALTERs with no schema version tracking, rollback, or drift detection

Introduce a schema_migrations table (or use PRAGMA user_version) with ordered, idempotent steps and a recorded version; add a startup check that compares table_info/index_list against SCHEMA and logs drift; document the rollback/restore procedure and cover migrations with a test that opens a v(N-1) fixture DB.

## DATA-P2-004 — Phase writes use a non-atomic check-then-insert with no UNIQUE(run_id, seq), so concurrent or replayed posts can create duplicate phase rows

Add a UNIQUE(run_id, seq) constraint (or make (run_id, seq) the primary key) and replace the SELECT-then-INSERT with 'INSERT ... ON CONFLICT(run_id, seq) DO UPDATE SET status=?, t1=?, detail=?'. Add a test that posts the same seq concurrently and asserts exactly one row.

## DET-P2-003 — [PORT] CRLF committed for 11 file(s) (index has CRLF)

Committed line endings are CRLF, which breaks Linux CI (shell scripts, hash checks). Add `.gitattributes` with `* text=auto eol=lf`, then renormalize (`git add --renormalize .`).

## DET-P2-005 — [SUPPLY] 9 GitHub Action ref(s) not pinned to a commit SHA

Pin `uses:` to a full 40-hex commit SHA (supply-chain hardening).

## DOC-P2-001 — Documented test command (`python tests/run_all.py`) fails on Windows: needs `windows-curses`, which the docs never say

In README.md (Tests) and AGENTS.md (Testing), either use the venv interpreter (`.venv\Scripts\python.exe tests/run_all.py`) or explicitly add `pip install windows-curses` for Windows; make tests/test_presets.py import tui.py with a guard/soft-skip when curses is unavailable; add a CI workflow that runs `tests/run_all.py` on windows-latest and ubuntu-latest so the claim is enforced rather than asserted.

## DOC-P2-002 — README release/version is stale and self-contradictory (v1.1.0 vs VERSION 1.11.5 vs the 1.11.3 written directly below it)

Make the README state the current release from the tag/VERSION (or generate it), and reconcile the inline 1.11.3 examples; keep all three consistent in one place. Add a docs test (or reuse tests/test_version.py) that asserts the README's release string matches VERSION.

## DOC-P2-003 — docs/PHASE_TIMINGS.md reports the same preset on the same machine as both ~11.5 min and ~14.1 min, contradicting itself

Pick the current measured value for the live stick and use it in both places (line 13 and the line-83 row); note the pre/post-trim numbers are historical only if they must remain. Add the measurement date/commit next to the totals.

## DOC-P2-004 — LICENSE declares the repo PROPRIETARY AND CONFIDENTIAL while README instructs the public to clone and download its public releases

Decide the licensing model and make README and LICENSE agree: either make the repo private and point README to an internal-use license, or ship a real OSS license and drop the 'CONFIDENTIAL' text. Reconcile the README 'Security'/'License' wording either way.

## DR-P2-001 — Destructive deletes purge run data irreversibly with no snapshot, soft-delete, or confirmation

Make destructive deletes take a snapshot to a trash/backup location first (or implement soft-delete with a deleted_at column and a retention purge), require an explicit confirm flag / typed confirmation for bulk operations, and print the backup path on success. Have --reset archive rather than drop.

## DR-P2-002 — Schema has no version record and migrations are additive-only with no rollback path (bad-migration drill impossible)

Introduce a schema_version table and numbered, forward+reverse migrations (or document 'additive-only' as an explicit, tested constraint), add a test that opens an old-schema DB and migrates it, and add a documented rollback/restore step to the DR runbook. Bind each migration to the app commit that introduced it.

## DR-P2-003 — Secrets have no backup/recovery or rotation procedure (per-runner keys live only in the DB)

Document token/key backup, storage and rotation in the DR runbook (e.g. keep the operator token in a password manager / sealed secret, back it up separately from the DB), add a re-issue/regenerate path for the operator token, and note how runner keys are recovered after a DB restore.

## DR-P2-004 — No encryption at rest for the database, artifacts, or (hypothetical) backups

Document an at-rest encryption requirement for the control-plane host/volume (full-disk/LUKS), or move secrets out of the DB (env/sealed file); if encrypted backups are added, specify the key handling and test a decrypt-on-restore. Note the base64 limitation explicitly (it is encoding, not encryption).

## EVOL-P2-001 — Adding a benchmark module/phase requires editing 6+ hardcoded lists; there is no registry or module template

Make benchreport.GROUPS (or a small JSON registry: name/label/platform/runner-flag) the single source of truth and have supported_groups(), agent.DEFAULT_GROUPS, gui._ALL_G, tui.GROUPS, run_win skip flags, app.js and Run-LinuxBench.sh derive from it. Add a bench/PHASE_TEMPLATE.md plus a unit test that fails when a group is present in the registry but not selectable end-to-end (registry -> runner flag -> server capabilities -> dashboard toggle).

## EVOL-P2-002 — No CI workflow runs the test suite, so platform changes are merged unverified

Add .github/workflows/test.yml running on push+PR: `python tests/run_all.py`, `python -m py_compile bench/*.py server/*.py` and `bash -n bench/Run-LinuxBench.sh live/Build-LiveUSB.sh live/airootfs/usr/local/bin/bench-*` on both ubuntu-latest and windows-latest; make it a required status check and have build-iso/build-app `needs:` it.

## EVOL-P2-003 — Schema 'migration' is unversioned, additive-only column checks run on every startup

Introduce `PRAGMA user_version` (or a schema_migrations table) with an ordered list of idempotent migration callables, run each once inside a transaction, and assert the expected version at startup. Add tests/test_migrations.py that builds a v(N) DB, migrates to v(N+1), and asserts data is preserved. Document the policy (append-only columns, rename = new column + backfill).

## EVOL-P2-004 — Authorization is a hardcoded two-tier boolean checked per handler; no role/permission model to extend

Add a central `authorize(principal, action, resource)` policy (backed by a roles/permissions table once accounts exist) and route every check through it. Keep the shared token as the bootstrap admin role. Add tests asserting each command kind and each UI route requires an explicit capability so a new endpoint cannot default to open.

## EVOL-P2-005 — Telemetry/summary metric catalogue is duplicated across Python and JavaScript with no single source of truth

Define the metric catalogue once (e.g. a JSON/registry consumed by benchreport, benchd and the web build) and generate METRICS, DASH_FIELDS and SERIES/STAT_ORDER from it. Extend the existing parity test to assert every METRICS/DASH_FIELDS/SERIES key belongs to the same catalogue and every sampler column is covered.

## EXEC-P2-001 — Evidence binding gap: the run is pinned to b916709 but the working tree advanced 5 commits and findings reproduce at 60ab90eb/72c18734

Re-pin the run to the exact audit commit (or explicitly declare the observed tree), regenerate artifacts at one commit, and record that commit in EXECUTIVE_SUMMARY.md / RELEASE_GATE.md and the manifest.

## EXEC-P2-002 — Published-artifact and privacy hygiene: ~9.5k generated files are tracked on a public repo with host/user identifiers

git rm -r --cached results/, keep the ignore rule, publish run output as CI artifacts, add a CI guard that fails on staged results/, and scrub committed examples of usernames/absolute paths/hostnames.

## FEAT-P2-001 — Deleting a run orphans its logs rows

Add `logs` (and `commands` WHERE run_id) to the purge loop in `do_DELETE`, or add an FK with `ON DELETE CASCADE` plus `PRAGMA foreign_keys=ON`. Extend test_control_plane's delete case to assert `GET /runs/<id>/logs` and the `logs` table are empty after DELETE. Reconcile CONTROL_PLANE.md:132 with the resulting behaviour.

## FILE-P2-001 — iso_fetch reports ok:true and acks "done" even when the ISO checksum is missing or mismatched

Make verification strict and fail closed: if SHA256SUMS is present but has no matching `.iso` line, set `verified=False`; if `verified` is not exactly True, return `ok: False` (or `status: "unverified"`) so the agent acks the command `failed`. Also compare every `.iso` sum, not just the last matching line. Add tests for (a) missing ISO line, (b) missing SHA256SUMS asset, (c) mismatch -> command acks failed.

## FILE-P2-002 — Artifact upload has no MIME/extension/size validation, no content-scanning hook, and no per-run quota

Validate uploads: allowlist `kind`/extensions (json/text/png/csv), enforce a smaller per-artifact and per-run byte/count quota with a clear 413, reject invalid base64 instead of storing it, and document that no malware scanning is performed (or add a pluggable scan hook that blocks on a positive result).

## FILE-P2-003 — All file downloads are authorized by one static shared token carried in the query string, with no expiry, rotation, or revocation

Issue short-lived, single-purpose download tokens (or short-lived signed links) instead of reusing the shared token in the query string; prefer the `Authorization` header where possible; add `Referrer-Policy: no-referrer` on downloads; support token rotation/revocation and refuse to start in an unauthenticated mode outside loopback.

## HYGIENE-P2-001 — History is 94% auto-generated `bench:` commits

Stop the per-file auto-commit push to main; batch/park run output outside main (artifact upload, dedicated branch, or results repo). If runs must be recorded in git, use a single squashed commit per run and exclude it from release/version derivation. Document the mechanism in AGENTS.md.

## HYGIENE-P2-002 — Duplicate nested `results/results/` tree

Delete the nested `results/results/` tree, and fix/guard the collector so it refuses to create a `results/results` path (e.g. resolve the output dir against the repo root and assert it does not already end in results/). Add a lint/test that fails if `results/results` exists.

## HYGIENE-P2-003 — README release drift (v1.1.0 vs VERSION 1.11.3)

Replace the hard-coded README release string with either the current value kept in lockstep by release.yml, or a pointer that renders `VERSION`/`git describe`. Add a doc check that fails when README's release token disagrees with VERSION.

## HYGIENE-P2-004 — Stdlib-only test suite fails on Windows system Python

Decouple the parity test from curses: make bench/tui.py import curses lazily (inside the TUI entry point) or expose PRESETS without importing curses, and/or skip test_presets' TUI leg gracefully on `except ImportError` with a clear message. Document the windows-curses prerequisite in AGENTS.md and bootstrap it in tests/harness.py.

## INFRA-P2-001 — Documented BENCHD_DB config key is never read; DB path is hard-coded and has no backup/retention

Either honour BENCHD_DB in find_conf_value()/main() or remove the key from the example. Add a documented backup/retention procedure (e.g. sqlite3 .backup + vacuum) and a data-path note to the deploy section.

## INFRA-P2-002 — Operator token is transported in URLs and kept in browser localStorage; no TLS/reverse proxy exists in the repo

Prefer an Authorization header for API calls and a short-lived, single-purpose stream/download ticket instead of the long-lived token in the URL; ship an example TLS reverse-proxy config (or terminate TLS in the app) and state that ?token= is for a trusted loopback/proxy only.

## INFRA-P2-003 — benchd systemd unit runs as root on 0.0.0.0 with no User/CapabilityBoundingSet and no readiness probe

Add User=/Group= (or DynamicUser=yes) plus CapabilityBoundingSet= and RestrictAddressFamilies; bind to the specific LAN/overlay address in the unit rather than 0.0.0.0; document /health as the readiness probe and (optionally) add an ExecStartPost/WatchdogSec.

## INFRA-P2-004 — Deployment is an unversioned manual pct snippet that does not ship VERSION or write a commit stamp, breaking the fleet staleness comparison

Add a small deploy script (checked in) that copies the needed files, writes VERSION and a .deployed-commit/.bench-version stamp, and records the commit; document a rollback (keep the previous copy + stamp). Assert the stamp in deployment verification.

## INV-P2-001 — Generated run output committed en masse

Decide one policy: keep at most a small curated set of reference runs under examples/ (already the home of 'real result sets'), and `git rm -r --cached results/` the rest. Add a CI guard (e.g. a workflow step that fails if any new file under results/ is added). If a handful of runs must stay for history, move them to examples/ where the 'evidence is part of the review' rule in .gitignore:4-5 already applies.

## INV-P2-002 — Recursively nested/duplicated result trees committed

Make collection idempotent: copy only the newly created run directory(ies), not the whole results tree; skip/replace a destination that already exists; and never collect a directory that already contains collected output. Add a regression test that runs the collector twice and asserts the tree does not nest, and add a CI check that rejects paths matching results/results/ or runs nested inside runs.

## INV-P2-003 — No dependency manifest or lockfile

Add a requirements.txt (or pyproject.toml) declaring the declared deps and a constraints/lock file pinning exact versions used for measurement runs. Have bench/bootstrap.py install from the locked set, and have CI install from it so the packaged bundles and the repo agree. Document any intentionally unpinned GPU wheel source.

## INV-P2-004 — README version stale vs VERSION and tags

Update README.md:12/15/17 to the current release line, or (better) replace hard-coded numbers with a note pointing at VERSION and the release workflow so the README cannot drift. Add a CI check that fails if README's advertised version does not match VERSION.

## IR-P2-001 — No monitoring or alerting: failures are only visible when a human watches the web dashboard

Add a Prometheus text /metrics endpoint plus alert rules (runner offline > 60s, run failed, GPU over-temp/throttle bit set, server disk < 10%, DB size/inode growth), or at minimum a webhook/email fired on run-failed and runner-offline events; add a heartbeat watch that alerts if benchd itself stops.

## IR-P2-002 — No backup or restore procedure for the control-plane SQLite database (all fleet history, artifacts and per-runner keys)

Ship a backup script using `sqlite3 data/benchd.sqlite '.backup'` on a schedule with retention, document a tested restore runbook and RPO/RTO, and record the last successful restore test as evidence; add an alert on backup failure.

## IR-P2-003 — No operator audit log: privileged commands and destructive deletes carry no actor identity or durable trail

Add an append-only audit table (ts, actor, source address, action kind, target runner/run, payload summary, result) written by every operator-only route, retain it independently of run deletion, and implement per-user operator accounts (roadmap) so the actor is identifiable.

## IR-P2-004 — No data-breach or vulnerability-disclosure process, while a public repo bakes a world-readable operator token into ISO/app artifacts

Add SECURITY.md (private disclosure contact/SLA) and a breach-response checklist including mandatory token + per-runner-key rotation, artifact/DB impact assessment, and post-rotation verification; reference it from README/AGENTS.md.

## MOB-P2-001 — Primary tab bar cannot fit a phone: it is a non-wrapping flex row with no horizontal scroll

Give `.tabs` `overflow-x:auto; -webkit-overflow-scrolling:touch` (mirroring the existing `.rtabs` rule at style.css:209) and/or a `@media (max-width:520px)` rule that shrinks tab padding and allows wrapping. Verify with a 360px browser viewport.

## MOB-P2-002 — Fixed multi-column grids never collapse on phones, forcing horizontal overflow or unreadable cells

Add `@media (max-width:600px)` rules collapsing `.grid2` and `.gauges` to a single column (and `.grid` to `minmax(0,1fr)`), matching the existing `.fgrid` collapse at style.css:281. Keep `.tablecard{overflow:auto}` for per-card table scroll.

## MOB-P2-003 — Interactive controls are below the 44x44px minimum touch target

Add a coarse-pointer/narrow-width media query raising button and row padding (e.g. `@media (max-width:600px){button{padding:11px 14px} th,td{padding:12px}}`) so targets reach >=44px.

## MOB-P2-004 — Header and filter bars clip or overflow on narrow screens instead of wrapping

Add `flex-wrap:wrap` to `.filters` and to the header children (or drop `overflow:hidden` and let the header wrap/scroll on narrow widths). Validate at 360px.

## NOTIF-P2-001 — No out-of-band alert/notification delivery for critical health verdicts

Add a small, opt-in notification sink to the control plane (stdlib only): a configurable webhook/ntfy/SMTP sink invoked by benchd when a finished run's summary.verdicts contains level 'bad' (or 'warn' above a threshold) and by reap_stale_runs when a run is marked failed. Keep it disabled by default, document the config key, redact the endpoint secret, and record a delivery-attempt row for audit. If out-of-band delivery is deliberately out of scope, state that explicitly in CONTROL_PLANE.md rather than listing alerting only as roadmap.

## OBS-P2-001 — No alerting or uptime monitoring for the control plane or for failed runs

Add an external uptime probe for GET /health (e.g. a systemd timer or an off-box check) plus a minimal alert path: on run status -> failed (or control-plane restart) emit to a webhook/email and record a row in an 'alerts' table; add OnFailure= to server/benchd.service. Document the alert contract.

## OBS-P2-002 — No structured logging and no request IDs / correlation IDs

Emit JSON log lines with at least ts, level, event, request_id (server-generated X-Request-Id echoed in the response) and run_id/runner_id where known; add a small log helper and use it in log_message and the exception paths. Keep the text mode behind a flag if needed.

## OBS-P2-003 — Server-side errors are swallowed; no error tracking or stack traces

Add an error-logging path (traceback + request id + route) for the 500 branches and for unexpected exceptions in the scheduler loop; persist error events so they can be listed. Reserve the events table or add a 'server_errors' table.

## OBS-P2-004 — /health conflates liveness and readiness and performs a DB query plus a network call

Split into /livez (process only, no I/O) and /readyz (checks SQLite read+write, web dir, and optionally cached latest_git without a live network call); keep /health as a public informational endpoint but make the probe path cheap and side-effect free.

## OBS-P2-005 — No runtime/service metrics and no monitoring-of-the-monitoring

Expose a real metrics endpoint (Prometheus text format is fine, stdlib-only) with request count/latency by route+status, SSE subscribers, commands queued/sent/failed, runs running/failed, DB size/WAL size and last scheduler tick age; add freshness gauges for the runner population and an external check that the alerting path end-to-end works.

## ORCH-P2-001 — Published audit run uses two conflicting finding-ID schemes

Adopt one ID scheme (the per-area AREA-SEVERITY-NNN form used in findings.json) and regenerate every section heading, the summary table, and the registers from findings.json so all artifacts share identical IDs; add a check that headings and JSON ids match.

## ORCH-P2-002 — risk_register.md is a verbatim copy of follow_up_register.md

Replace risk_register.md with a genuine aggregation (category, severity, likelihood, impact, evidence, mitigation) derived from findings.json, and keep follow_up_register.md as the owner/target/status tracker so the two have distinct purposes.

## ORCH-P2-003 — Run INDEX and audit_manifest.json omit the deterministic lens artifacts

List lens_deterministic.md and deterministic-findings.json in both INDEX.md and audit_manifest.json scope.reports; if any artifact is intentionally excluded from the aggregate, record it explicitly as excluded.

## PERF-P2-001 — Per-run detail, stats and CSV endpoints load and re-parse every telemetry row on the request thread

Push downsampling/aggregation into SQL (or cache the finished stats/derived dict on run finish), SELECT only needed columns, parse extra JSON once, and stream the CSV with an iterator instead of building it in memory.

## PERF-P2-002 — Realtime path scales by unbounded threads and broadcasts whole telemetry batches to every subscriber

Cap concurrent SSE clients and total worker threads; coalesce telemetry to latest-value-per-series for slow subscribers and emit an explicit 'resync' event (with a dropped-event counter) instead of silent loss; enable HTTP/1.1 keep-alive; consider a single fan-out writer.

## PERF-P2-003 — CI rebuilds a multi-GB ISO and both app bundles on every bench/** or live/** push with no dependency caching

Narrow the push triggers (build the ISO only for live/** / build-graph changes, or on manual dispatch), add actions/cache for the pip/torch download and PyInstaller work dirs, cache the Torch venv between runs on self-hosted runners, and avoid bundling the entire stdlib.

## PERF-P2-004 — Heartbeat/liveness path performs a blocking GitHub compare call with an 8 s timeout, longer than the runner's 6 s client timeout

Decouple enrichment from the heartbeat response (compute toolkit status in the background / cache per runner), lower the GitHub timeout below the runner timeout (e.g. 2-3 s), return immediately on cache miss, and make BENCH_OFFLINE the default when no token is configured so the call is skipped by design.

## PRIV-P2-001 — Collectors capture stable hardware identifiers and PII with no redaction mode, and the uploader publishes the whole results directory to public GitHub

Add a redaction mode (drop/hash serials, UUIDs, MACs, IPs, usernames, startup commands, DNS) and make it the default for shareable output; document the sensitive fields; default the uploader to redacted output unless explicitly overridden.

## PRIV-P2-002 — No attributable audit trail for privileged/admin actions (shared operator token, commands record no actor)

Record an actor (per-user id or at least a named/rotatable operator key id + source IP) on command and delete operations, persist an append-only admin audit log, expose it read-only, and implement the per-user operator accounts already on the roadmap.

## PRIV-P2-003 — Deletion is incomplete: deleting a run leaves its console logs, and deleting a runner leaves its runs/telemetry/inventory

Delete the run's logs too, and cascade runner deletion to its runs (phases/telemetry/events/artifacts/logs); extend the tests to assert rows are gone, not just that the endpoint 404s.

## PRIV-P2-004 — No retention or scheduled-purge policy for telemetry, logs, artifacts and the SQLite database

Document a retention policy per data type (e.g. telemetry N days, logs/artifacts N days) and implement a scheduled purge (configurable), running VACUUM/periodic checkpoint; surface retained volume in the UI.

## PRIV-P2-005 — Per-runner API keys are stored in plaintext in SQLite and looked up by direct comparison

Store only a salted hash of each API key and compare hashes, add key rotation/revocation, and document the credential lifecycle. Even in a lab, avoid storing recoverable runner credentials.

## REL-P2-001 — README's release/version strings are stale and self-contradictory, so the shipped docs disagree with VERSION

Make README derive the release from VERSION/`git describe` at release time (release.yml already rewrites VERSION) or link to the tag, and add a docs check that fails when README's release token disagrees with VERSION.

## REL-P2-002 — Release artifacts are tagged by workflow run number, not by version or commit, so notes cannot be tied to a build

Name release tags by version + short commit (e.g. `app-<version>-<sha7>` / `iso-<variant>-<version>-<sha7>`), or attach the app/ISO assets to the version tag's release. Record VERSION + commit SHA in the release body and in bench-version.txt.

## REL-P2-003 — Changelog input is unenforced: no PR/issue templates or CONTRIBUTING, and commit subjects are 94% auto-generated noise

Add PULL_REQUEST_TEMPLATE with a 'release note / breaking change / operator action' checklist and commitlint (conventional commits). In release.yml, exclude `bench:` subjects from generation and read an explicit `docs/CHANGELOG.d/` fragment set so a release's notes are authored, not inferred.

## REL-P2-004 — No upgrade/rollback notes are possible: schema changes are unversioned additive ALTERs and the deploy does not ship VERSION

Add a CHANGELOG 'Upgrade' and 'Rollback' section per release; record `schema_version`/`PRAGMA user_version` in `_migrate()` and provide a documented down path; copy VERSION in the deploy step so the running build is identifiable; add a backup step before upgrade.

## REL-P2-005 — Release notes carry no generation metadata (commit/version/date), and the repo's only release-note-like artifact is a one-line verdict

Stamp every generated notes/changelog artifact with VERSION, full commit SHA, branch and generation date (header block), and add a 'regenerate release notes' command. Include a template so the artifact set (notes + changelog + release body + upgrade/rollback) is reproducible.

## REL-P2-006 — No separate user/admin/operator/security note tracks; operator-mandated changes (token handling, exec/shell, deletes) have no release channel

Adopt a release-notes template with distinct sections: User-visible, Breaking changes, Operator actions, Security fixes (CVE-style), Migrations, Rollback, Known issues. Require the operator-action and security sections to be non-empty when the diff touches server/benchd.py auth, command handling or deletes.

## RES-P2-001 — A completed run is recorded as 'failed' and its summary lost when the final finish post fails (no retry/idempotency)

Retry finish with bounded backoff and persist the pending summary locally (replay at next start, or a spool the agent/pump drains); use a stable run id so finish is idempotent; add a distinct status (e.g. 'interrupted' + reason) for reaped runs so a lost finish is not reported as a runner failure.

## RES-P2-002 — Backfill importer is not idempotent (re-running duplicates every run) and --reset deletes all history

Derive a stable run id from source path + host + start timestamp (the server already honours a supplied id) and make the import an upsert; scope --reset to imported runs or require an explicit confirm/target instead of deleting all runs.

## RES-P2-003 — agent 'start' has a TOCTOU race that can run two benchmark batteries concurrently on one machine

Set a 'starting' flag synchronously under a lock before spawning (clear it on failure), reject a second start while one is pending, and have the server mark the runner busy when a start command is issued (not only when /runs is created).

## RES-P2-004 — Documented rollback paths (A/B slot auto-revert, live toolkit self-update) are never exercised, and a bad toolkit update has no rollback

Add a lab test (or at least a grubenv/bench-slot unit test) that flips a slot and confirms the revert after 3 attempts; keep the previous toolkit copy and add a startup health check with automatic revert (or `live_update.py toolkit --rollback`). Record the last exercise in the runbook.

## SBOM-P2-001 — No package manifest or lockfile anywhere; dependencies are installed unpinned at runtime, so no reproducible dependency set exists to inventory

Commit a pinned, hash-pinned dependency set (constraints.txt / requirements.lock with --require-hashes) for the runtime and build deps; have bootstrap.py and ci-build.sh install from it (--require-hashes); pin the Arch package set (or record resolved versions) so the ISO is reproducible. This lockfile then becomes the SBOM source of truth.

## SBOM-P2-002 — GitHub Actions dependencies are mutable major tags and there is no Dependabot, dependency-review or vulnerability scanning

Pin every action to a full commit SHA (with a comment naming the version); add .github/dependabot.yml for github-actions + pip, and enable GitHub dependency-review on PRs (or an equivalent license/vuln gate) so a PR adding a dependency fails on a disallowed license or a known CVE.

## SBOM-P2-003 — No release provenance: no build attestation/signing, and app/ISO release tags are run-number based rather than commit-bound

Emit a provenance attestation (actions/attest-build-provenance or slsa-github-generator) for the ISO and the app zips, sign release assets (sigstore/cosign), and publish checksums for the app bundle too. Tag app/ISO releases with the commit (or include and sign the commit SHA) instead of relying on run_number.

## SBOM-P2-004 — No license policy, allow/deny list, CI license gate or exception process

Add a docs/license-policy.md with an explicit allow/deny list (and a documented exception process with owner + expiry), and enforce it in CI with a license scanner (e.g. pip-licenses / licensecheck / a dependency-review license gate) that fails on a deny-list license or an allow-listed-but-unnoticed change.

## SC-P2-001 — No dependency manifest or lockfile; compute deps are pip-installed unpinned, sometimes with an extra index

Introduce a pinned, hashed requirements lockfile (e.g. pip-tools/uv with --require-hashes) for the compute deps, use it in bootstrap.py, ci-build.sh and the PowerShell runners, drop --extra-index-url in favour of one allow-listed index, and add Dependabot/Renovate to keep it current. Add a CI job that installs strictly from the lock.

## SC-P2-002 — GitHub Actions are pinned to mutable major tags and there is no dependency automation or dependency-review/license gate

Pin every `uses:` to a full commit SHA (keep the tag in a comment) and enable Dependabot for github-actions + pip, with a dependency-review action and a license allow-list gate on PRs. Add .github/CODEOWNERS and SECURITY.md.

## SC-P2-003 — bootstrap.py extracts a downloaded tarball without a safe extraction filter and its integrity check fails open

Pin the exact asset name and a hard-coded SHA-256 in the source (do not fetch the .sha256 over the same channel), fail closed on mismatch, and extract with tarfile.extractall(root, filter='data') (or an explicit member allow-list) after validating member paths.

## SEARCH-P2-001 — No retention policy or cleanup job for logs, telemetry, artifacts or events - run data is kept forever

Define per-table retention (e.g. logs/telemetry 30-90 days, artifacts 90 days) in config, add a periodic prune task to the scheduler loop, document owner + retention per table in docs/DATA.md or docs/CONTROL_PLANE.md, and expose a manual purge endpoint. Add a test that a row past its retention window is removed by the prune pass.

## SEARCH-P2-002 — Deleting a runner orphans its runs, telemetry, logs and artifacts

On runner delete, cascade to the runner's runs via the same run-delete path (which must also delete logs, per the P1 fix), or explicitly document and provide a separate purge command. Add a test that deleting a runner removes its runs and their run-scoped rows.

## SEARCH-P2-003 — Shared operator token is accepted in the URL query string and compared non-constant-time

Prefer a short-lived signed URL or an httpOnly cookie for SSE/downloads instead of ?token=; if query auth must stay, compare with secrets.compare_digest and document the leak surface. Consider rotating the token and adding per-user operator logins (already on the roadmap at docs/CONTROL_PLANE.md:275).

## SEC-P2-001 — Operator token in the URL query + cleartext logs over HTTP

Stop accepting the operator token in the URL: use a short-lived, single-use ticket for the SSE stream and downloads. Redact query strings in log_message(). Require TLS (or enforce a TLS-terminating proxy in front) before the control plane is reachable over a LAN, and document that requirement as a hard prerequisite rather than an option.

## SEC-P2-002 — Wildcard CORS on authenticated endpoints and SSE

Restrict Access-Control-Allow-Origin to the known dashboard origin(s), or remove the header entirely and serve the dashboard same-origin. Drop the wildcard from the OPTIONS preflight and validate the Origin header for state-changing requests.

## SEC-P2-003 — No rate limiting or lockout

Add per-credential and per-source-IP rate limits with exponential backoff and a temporary lockout on repeated auth failures; throttle /api/v1/register separately; return 429 and surface an operator-visible alert. Add tests that hammer the auth endpoints and assert throttling.

## SEC-P2-004 — Unbounded request body (DoS)

Enforce a hard body cap (reject larger with 413 before reading), set socket read timeouts, and limit concurrent connections. NOTE: an uncommitted local modification in the working tree (server/benchd.py, MAX_BODY = 24 MiB) already addresses this at b9167095's HEAD; confirm the deployed copy includes it before treating as fixed.

## SECRET-P2-001 — Placeholder token 'change-me' is accepted silently; no token strength/startup validation

Refuse to start (or hard-fail) when BENCHD_TOKEN is a known placeholder (change-me, changeme, test, empty) or is shorter than a minimum length; log a clear remediation. Add a unit test asserting weak tokens are rejected.

## SECRET-P2-002 — No secret rotation / revocation / break-glass runbook or inventory

Add docs/secret_rotation_runbook.md containing: an environment-variable/secret inventory, classification (operator token, runner key, GitHub PAT, OpenAI/LLM key if any), the exact rotation + revocation commands (request runner key re-issue; regenerate PAT; rebuild + re-release artifacts), a break-glass procedure, and a tested validation step. Track rotation dates/artifacts per the extended checks.

## TEST-P2-001 — Releases, tags and public ISO/app artifacts are published with no test or smoke verification of the artifact

Gate tag/build jobs on the CI test job (`needs: ci`) and add a post-build smoke step (e.g. run `bench/agent.py --self-test` against the built bundle, and boot/verify the ISO image's SHA256SUMS + a headless start) before the release asset is attached.

## TEST-P2-002 — Documented test command fails on Windows: suite needs third-party windows-curses but is described as stdlib-only

Either guard the tui/curses import in tests/test_presets.py (skip cleanly when curses is unavailable) or document that the suite must run under the bootstrapped .venv (which installs windows-curses); correct the 'stdlib only' wording in harness.py/AGENTS.md.

## TEST-P2-003 — The 23 PowerShell battery scripts and the web dashboard are only validated by substring assertions, never executed or linted

Add a PowerShell parse/lint gate (PSScriptAnalyzer, or `pwsh -NoProfile -Command '[void][scriptblock]::Create((Get-Content -Raw <file>))'` at minimum) and a JS syntax/lint step (node --check on app.js) to CI; add at least one execution smoke of the PowerShell battery entry point on a windows runner.

## USE-P2-001 — Control-plane commands report success on enqueue and never surface the runner's ack, so a rejected start/stop/exec looks successful

Render command lifecycle in the UI: subscribe to the `command` SSE event and toast/log on status `failed` (including `result.error`), show a per-runner pending/queued indicator on the Start/Stop/Update buttons, and disable Start while the runner reports `busy`. Optionally add a small per-runner 'last command: <kind> <status>' line sourced from the same event.

## USE-P2-002 — Web Start-run form has no input validation; blank/zero/negative durations and sizes are sent silently

Add `min`/`max`/`step` to the numeric inputs, validate the whole form in the `#mGo` handler (reject blank/NaN/out-of-range with an inline error next to the field, and block the submit), and mirror the GUI's sane ranges. Optionally have `extra_runner_args`/the runners reject non-positive values.

## USE-P2-003 — GUI 'Clean up environment' deletes the cached runner interpreter with no confirmation and no in-run guard

Gate `clean_env()` with `if self.running: return self._set_status('a run is in progress', WARN)`, and add a confirm dialog naming what will be deleted (cache path, size) before calling `bootstrap.clean()`.

## USE-P2-004 — Remote terminal / ad-hoc exec is only offered while a run is live, so idle runners cannot be diagnosed from the dashboard

Expose a terminal independent of run state - either always render the exec form in the focus view (routing output to the runner's stream rather than a run), or add a 'run command…' action to the runner card that opens a modal and streams the result.

## UX-P2-001 — Web dashboard's primary interactions are mouse-only (runner cards, sortable headers, table rows)

Render the clickable panels/rows/headers as real `<button>`/`<a>` or add tabindex=0 + role=button/row and an Enter/Space keydown handler; add aria-sort to the sorted `<th>`.

## UX-P2-002 — Modal dialog has no dialog semantics, no focus trap, and no focus restore

Add role="dialog" aria-modal="true" aria-labelledby to #modalbox, trap Tab within the modal while open, and restore focus to the invoking control on close.

## UX-P2-003 — No ARIA anywhere in the web dashboard; tab strip and live SSE updates are not exposed to assistive tech

Add tablist/tab/tabpanel roles with aria-selected and roving tabindex, and mark the live summary/console regions aria-live="polite" (console log off or aria-live="off").

## UX-P2-004 — Canvas charts have no accessible alternative and their tooltips are pointer-only

Give each canvas role="img" with an aria-label summarising the series, and provide an accessible data table or a focusable legend listing the values (chartLegendHTML already computes the range).

## UX-P2-005 — Tk GUI suppresses the keyboard focus indicator and has no keyboard accelerators

Remove `focusthickness=0` and set a visible `focuscolor` (e.g. ACCENT); add keyboard accelerators for start/stop/collect.

## ACM-P3-001 — Inconsistent constant-time credential comparison (bearer uses compare_digest; ?token=, _runner_ok and _caller use ==)

Route every credential comparison through a single constant-time helper (secrets.compare_digest); add a lint/test that forbids '== self.token'.

## ACM-P3-007 — Inconsistent constant-time token comparison

TBD

## ADMIN-P3-001 — Inconsistent confirmation for destructive console actions (schedule delete has none)

Use one shared confirmation component for every destructive action, and require typed confirmation for fleet-scale operations (delete runner with history, iso_write).

## ADMIN-P3-008 — Inconsistent confirmation (schedule delete has none)

TBD

## AI-P3-001 — README release/version text is stale and contradicts VERSION, which agents are told is the single source of truth

Generate the version string in README from VERSION (or remove the hardcoded release number and point to VERSION/releases), and add a small test/check that fails when README's release line disagrees with VERSION.

## AI-P3-002 — Secrets guidance names only the ISO workflow, omitting that build-app.yml bakes the same world-readable token into public app bundles

Update AGENTS.md Security to list every public artifact that carries the baked token (build-iso.yml ISOs and build-app.yml bundles) and the rotation obligation for each; cross-link README.md:158-163. Consider a single 'baked secret inventory' doc and a check that the secret name only appears in approved workflows.

## AN-P3-001 — No privacy/analytics governance artifacts (vendor list, consent, do-not-track, retention docs) and no privacy tests

Add docs/PRIVACY.md (data inventory: fields, purpose, storage, retention, third-party endpoints, opt-out) and a vendor/endpoint list; document consent for upload; add a unit test asserting the redaction mode strips serials/MAC/IP and that no shareable path emits identifiers without redaction.

## API-P3-001 — Error responses leak internal exception type and message; invalid client input returns 500 instead of 4xx

Keep {"error": <generic message>} for 5xx and log the exception server-side; map validation failures to 400/422 explicitly (see the body-validation finding) so the error contract is stable and non-leaky.

## API-P3-002 — No rate limiting or request throttling on any endpoint; /health is unauthenticated

Add a simple per-client token-bucket (or at least a max rows/s and max queued-write cap) for write routes, and reduce /health to a bare liveness/version or gate the git/latest/runners fields behind auth.

## API-P3-003 — No machine-readable API contract (OpenAPI/schema); the prose contract already drifts from the handlers

Add a checked-in OpenAPI (or a route table generated from the handler) plus a contract test that asserts every implemented route appears in it; validate schedule kind against the allowed set; document POST /runs/<id>/log and the actual delete semantics.

## ARCH-P3-001 — Documented topology drifts from code (dashboard commands; iso_write BENCHDATA guard)

Make docs/CONTROL_PLANE.md and README.md match the code (or vice versa). Keep one authoritative command-support matrix derived from the handlers, and either keep the BENCHDATA guard on live systems or correct the README to state the actual behaviour.

## ARCH-P3-002 — Telemetry/logs/events have no retention or pruning

Add a retention pass to scheduler_loop (age- and/or size-based) that prunes telemetry/logs/events and runs VACUUM, and document the expected growth budget and the manual cleanup command.

## BP-P3-001 — No CODEOWNERS file

Add `.github/CODEOWNERS` assigning the workflow/CI files, server/benchd.py and packaging/release paths to maintainers, and enable 'Require review from Code Owners' in the branch rules alongside the required checks.

## BP-P3-002 — No pull-request template or contributing guide

Add `.github/PULL_REQUEST_TEMPLATE.md` listing the test command, the AGENTS.md ground rules, and a 'no secrets / no CRLF .sh' confirmation; reference it from a short CONTRIBUTING.md.

## CHAIN-P3-001 — Unauthenticated /health discloses deployment identity and fleet size, and every API response sets Access-Control-Allow-Origin: *

Keep /health minimal (liveness only) or require the operator credential for version/git/latest/runner-count; reflect CORS only for known dashboard origins instead of '*'.

## CI-P3-001 — Release tags do not map to a commit

Name release tags with the version (and short SHA) instead of the run number, e.g. `iso-<version>-<gpu>`, and add an attestation (e.g. actions/attest-build-provenance) so each asset is bound to the exact commit.

## CTR-P3-001 — LXC deployment binds the control plane to 0.0.0.0 despite documented 'LAN/lab address only' posture

Have the unit bind the documented lab address (or make host configurable via /etc/benchd.conf and default to the overlay address), or add a firewall rule. Document that the 0.0.0.0 bind is intentional only when a host firewall/reverse proxy constrains it; refuse to start when no token is set.

## DATA-P3-001 — Request bodies are not validated as JSON objects (non-object body returns 500 + internal exception), and the documented BENCHD_DB setting is ignored

Validate that _body() returns a dict (else 400) and consider per-route required-field checks; either implement BENCHD_DB via env/conf or remove it from benchd.conf.example; extend the malformed-input test to cover bodies (list/string/null/number) as well as query strings.

## DATA-P3-002 — No optimistic locking or version preconditions on mutations; a late /finish can overwrite a reaped run's terminal status

Guard /finish with 'WHERE id=? AND status="running"' (or add a monotonic version column and require If-Match), reject/flag a finish for an already-terminal run, and add a test that drives the reaper-then-finish ordering and asserts the run does not resurrect.

## DATA-P3-003 — Hard deletes with no soft-delete/tombstone and no audit fields on any table

Add deleted_at (+ optional deleted_by) and soft-delete filtering for runs, or write an append-only deletion journal; add created/updated metadata to mutable tables; document and test a backup/restore procedure so deletions are recoverable.

## DET-P3-001 — [DEP] No Dependabot configuration

Add `.github/dependabot.yml` for dependency updates.

## DET-P3-002 — [DEP] trivy not installed (dependency vuln scan skipped)

Install trivy to enable the --deep dependency vulnerability scan.

## DET-P3-004 — [SEC] gitleaks not installed (secret scan skipped)

Install gitleaks in CI to enable the secret scan.

## DOC-P3-001 — README 'Presets' table lists 11 presets but the GUI/TUI/web ship 13 - it omits 'Stabilized full soak (15 min)' and 'Graphics only (FurMark/Valley)'

Add the two missing rows to the Presets table to match gui.py/tui.py/app.js/test_presets.py, and note the source of truth for the list.

## DOC-P3-002 — AGENTS.md points to `update_ct.py`, which does not exist in the repository

Either add the deploy/update script under server/ (referenced by docs/CONTROL_PLANE.md's Deployment section) or correct the reference to the actual mechanism, and add the `.deployed-commit`/`.bench-version` stamp step it describes.

## DOC-P3-003 — No CONTRIBUTING/SECURITY/CHANGELOG or PR/issue templates, and no operator troubleshooting/rollback/incident runbook

Add CONTRIBUTING.md (contribution flow + coding standards distilled from AGENTS.md), SECURITY.md (private reporting), CHANGELOG.md (or point to release notes), .github/ PR + issue templates, and docs/RUNBOOK.md covering control-plane deploy/rollback, live-USB recovery, and incident triage.

## DR-P3-001 — No DR runbook and no infrastructure-config backup; deployment is imperative/manual

Version the deploy as code (a small script or Ansible playbook that also writes .deployed-commit/VERSION), include /etc/benchd.conf content as a sealed secret or template, and add docs/DR_RUNBOOK.md stating RPO/RTO, the backup schedule/retention, the restore steps, the validation checklist, and the last-tested date.

## EVOL-P3-001 — Command kinds are a hardcoded tuple; clients cannot advertise command capability and silently fail unknown kinds

Move command kinds into one registry (kind -> payload schema) shared by the server, and advertise supported kinds in registration capabilities so the UI can disable unsupported actions. Add a test that every kind in the registry is handled by at least the agent and that capabilities cover it.

## EVOL-P3-002 — Vendored LibreHardwareMonitor binaries are git-ignored, so the app bundle is not reproducible from a clone despite docs claiming otherwise

Un-ignore tools/lhm (e.g. `!tools/lhm/**` with the DLLs pinned and checksummed) or add an explicit, version-pinned fetch+verify step to build-app.yml and build_app.py. Make build_app.py fail or warn loudly when have_lhm is false, and correct AGENTS.md/docs to match whichever policy is chosen.

## EVOL-P3-003 — No package structure; shared code is a 2.5k-line flat module imported via sys.path insertion

Introduce a `bench` package (`bench/__init__.py`, e.g. bench/config.py, bench/telemetry.py, bench/summary.py, bench/client.py) and re-export the current names so existing importers keep working; add a lint that forbids new sys.path hacks. This is a prerequisite for the module-registry work above.

## FEAT-P3-001 — README preset table lists 11 of 13 presets

Update README.md:210-220 to list all 13 presets (or generate the table from `gui.PRESETS` in CI). Add 'Graphics only (FurMark/Valley)' to the docs and note it in the Dashboards/Updates sections.

## FEAT-P3-002 — README release claim is stale

Either stop hard-coding the release in README (reference `VERSION`), or have release.yml update README.md alongside VERSION in the same commit. Reconcile the current text to 1.11.3.

## FEAT-P3-003 — CONTROL_PLANE command-support matrix is stale

Rewrite docs/CONTROL_PLANE.md:139-142 to match gui.py/_remote_command and tui.py/_apply_remote: dashboards implement start/stop/fan_curve/shutdown/reboot, update/update_toolkit/iso_*, restart, and exec/shell; only power_limit is unsupported. Add a parity test if practical.

## FEAT-P3-004 — Committed audit finding CI-P3-001 contradicts the tree

Mark CI-P3-001 as `verified-fixed` in the follow-up register / roadmap with the workflow paths as the closing artifact, or annotate that it is bounded to commit 4ecee97. Add a lint/CI check that flags audit claims whose evidence paths no longer match the tree.

## FEAT-P3-005 — Documented test command fails on stock Windows Python

State the exact command (the bootstrapped `.venv`, which contains `windows-curses`) in README/AGENTS.md, and/or make `tests/run_all.py` skip/fake the curses import when `import curses` fails, reporting a clear 'SKIP (needs windows-curses)' instead of a crash.

## FEAT-P3-006 — Working tree diverges from the recorded commit

Audit a clean checkout pinned to the commit (or record the working-tree hashes), and land the in-flight changes so the branch tip equals the tree under review. Report the tree hash alongside every finding that cites server/benchd.py or import_results.py.

## FILE-P3-001 — Artifact metadata sha256 is client-supplied and never recomputed or verified on download

Compute sha256 server-side on receipt; reject the upload if a client-supplied digest disagrees; return the server-computed digest in the run detail and verify it on download.

## FILE-P3-002 — No per-artifact deletion, retention, or versioning; artifacts are purged only by deleting the whole run

Add `DELETE /api/v1/runs/<id>/artifact/<name>` (operator-scoped), an optional retention/TTL policy, and a read API that surfaces version/created time; document the retention behavior.

## FILE-P3-003 — Missing negative/authorization tests for the file surface and wildcard CORS on authenticated downloads

Add tests that (a) a runner key is denied 403/404 on another run's artifact and telemetry.csv, (b) an over-cap Content-Length is refused before buffering, and (c) invalid base64/hostile names are rejected. Scope `Access-Control-Allow-Origin` to the dashboard origin rather than `*`.

## HYGIENE-P3-001 — Large monolithic modules with no internal split (benchreport.py 2,811 lines; app.js 1,822)

Split benchreport.py into focused modules (fields/aliases, http client, csv parsing, report rendering) re-exported from benchreport for compatibility; do the same for the web dashboard JS. Keep the stdlib-only constraint and run tests/test_reporting.py after the split.

## HYGIENE-P3-002 — No CHANGELOG or ADRs; release notes are implicit in commit subjects

Add a CHANGELOG.md (Keep a Changelog format) updated at release time, and a docs/adr/ (or docs/decisions/) directory for load-bearing choices such as stdlib-only, single-writer telemetry, and fail-soft control plane.

## HYGIENE-P3-003 — No type annotations and 238 broad `except Exception` handlers across the Python codebase

Adopt gradual typing (annotate public functions in benchreport.py, *_bench.py, benchd.py; keep runtime stdlib-only), and narrow broad handlers outside the documented fail-soft code paths. Route output through a tiny stdlib logging helper so verbosity/level can be controlled consistently.

## INFRA-P3-001 — Live launcher exports BENCHD_INSECURE and BENCH_AGENT_NAME that nothing consumes (env name drift)

Remove the unused keys from bench-agent-env's allow-list, or implement them (e.g. reject non-local http unless BENCHD_INSECURE=1, and honour BENCH_AGENT_NAME as the runner name). Document whichever set is real in one env matrix.

## INFRA-P3-002 — Environment-specific deploy values (container id 108, IP 192.168.222.188/24) are hard-coded in docs with no inventory, and a prior audit recorded a different address

Move the deploy values into a checked-in, parameterised deploy script/config (or a template) and add an environment inventory + environment matrix doc listing host, address, port, container id, DB path and secret source; keep the example IP clearly marked as an example.

## INV-P3-001 — Missing GitHub governance metadata

Add .github/CODEOWNERS, a SECURITY.md with a disclosure contact, .github/dependabot.yml covering pip and GitHub Actions, and PR/issue templates. The release workflow already generates versions; add a CHANGELOG section or generate release notes from the tag.

## INV-P3-002 — Large committed binary assets

Downscale/compress example screenshots (e.g. to WebP at review resolution) or attach them to releases instead of committing them; document where live/keys/omarchy.gpg comes from and when it expires. Optionally enable Git LFS for intentionally-kept large binaries.

## INV-P3-003 — Committed audit artifacts pinned to an old commit

Either move prior audit outputs out of the source tree, or add a README/index note that they are a point-in-time snapshot at 4ecee97, plus the exact regeneration command and a staleness marker. Prefer keeping only narrative reports in-tree and publishing machine-readable findings as build/release artifacts.

## IR-P3-001 — Prior audit findings are all still marked open and were never re-verified, so the same incident class recurs

Add re-verification dates and closure evidence to the follow-up register, pin LibreHardwareMonitor to a specific release with a committed SHA-256 verified before Expand-Archive/Add-Type (fail closed), and add a regression test asserting the pinned URL/hash so the finding cannot silently reopen.

## MOB-P3-001 — No PWA surface at all: no manifest, icons, service worker, install prompt, or offline fallback

Either (a) deliberately document 'web UI is a desktop-only live console; no PWA/offline support' in docs/CONTROL_PLANE.md, or (b) add a minimal manifest (name, icons, `display:standalone`, `theme-color`) plus a service worker with a cache-first app shell and a network-fallback offline page, noting it only works over HTTPS/localhost. Track the decision so it is not silently assumed.

## MOB-P3-002 — Fixed/sticky chrome ignores safe-area insets (notch, home indicator)

Add `viewport-fit=cover` and pad the sticky/fixed chrome with `env(safe-area-inset-*)` (e.g. `padding-top:calc(14px + env(safe-area-inset-top))` on `.topbar`, `padding-bottom` on `.toast`).

## MOB-P3-003 — No mobile/responsive test coverage; the suite is source-string matching only

Add a lightweight responsive smoke test (Playwright/`playwright.config` with 375x812 and 320x568 viewports) asserting `document.documentElement.scrollWidth <= innerWidth` at each width, plus a check that the tab bar has no overflow. If a browser dep is undesirable, add a CSS-lint assertion that `.tabs`/`.filters` retain `overflow-x`/`flex-wrap`.

## NOTIF-P3-001 — In-app SSE notification bus silently drops events when a subscriber queue fills

Track drops per subscriber (increment a counter on put_nowait failure) and either (a) send a 'resync' SSE event telling the client to refetch /state, or (b) disconnect the lagging subscriber so the browser's reconnect+snapshot path restores consistency. Add a unit test that fills a subscriber queue and asserts the drop is surfaced, not swallowed.

## OBS-P3-001 — No audit log of operator / destructive command issuance

Append-only audit log (table or file) recording ts, source addr, command kind, target runner, payload digest and operator/session identifier for every issued command and every delete; never cascade-delete audit rows with the runner.

## OBS-P3-002 — No incident runbook, escalation path, or on-call checklist

Add docs/INCIDENT_RUNBOOK.md with detection (which dashboard/endpoint shows it), triage, immediate actions and recovery for: control plane down, runner offline mid-run, failed/unknown run, stuck/reaped command, disk/WAL full, over-temp/throttle/TDR; link it from CONTROL_PLANE.md.

## OBS-P3-003 — Release marker not bound in the documented copy-deploy; /health can report 0.0.0+unknown

Either push VERSION in the deploy, or write a .deployed-commit/.bench-version stamp (containing version+commit) as part of the deploy, and document it; assert it in a test that /health reports a non-unknown version for a copy deploy. Reconcile AGENTS.md:204.

## ORCH-P3-001 — Deterministic finding DET-P3-002 is dropped from the aggregate

Either merge DET-P3-002 into the aggregate or list it under an explicit 'excluded / superseded' note in findings.json and INDEX.md, and record the merge rule used.

## ORCH-P3-002 — Published run was never reconciled after later commits fixed two findings

Add a reconciliation pass that updates each finding's status to verified-fixed (with the fixing commit as artifact) or still-open, and record the reconciliation date/commit in INDEX.md.

## PERF-P3-001 — Static dashboard assets are served with Cache-Control: no-store and no validators, so they are re-downloaded on every load

Serve static assets with Cache-Control: max-age plus ETag/Last-Modified and honour If-None-Match/If-Modified-Since (304), and gzip the JS/CSS; keep no-store only for API/SSE responses.

## PERF-P3-002 — History and Fleet silently cap at 300/500 runs and ignore the server's total count

Add a 'load older' / infinite-scroll control using the existing limit/offset API and display the server total (e.g. 'showing 300 of N'); surface a warning when results are truncated.

## PRIV-P3-001 — Operator token is handled via URL query string and browser localStorage

Prefer a short-lived token exchange / header-based auth, avoid long-lived secrets in query strings and localStorage, and document proxy log-redaction requirements if ?token= must stay for downloads.

## PRIV-P3-002 — No privacy/compliance documentation: data classification, retention policy, vendor/processor inventory, consent; secrets baked into public ISOs

Add a data-classification inventory and retention/erasure policy, a vendor/processor inventory (Cloudflare, GitHub, python-build-standalone, PyTorch/onnxruntime indexes, LibreHardwareMonitor mirror, Ollama), and a control-readiness note. Stop baking long-lived tokens into public ISOs or make bundling strictly opt-in with forced rotation.

## REL-P3-001 — No known-issues track and no breaking-change record; there is nothing to seed release notes from

Add a `KNOWN_ISSUES.md` (or a CHANGELOG 'Known issues' section) seeded from the current audit findings, and require a breaking-change entry (with migration note) for any change to the API/token model, schema or command kinds.

## RES-P3-001 — Command queue is at-most-once with no DLQ/expiry; a fetched-but-unacked command is dropped, and a queued command never expires

Add command expiry/TTL for time-sensitive kinds, surface a dead-letter view and allow replay, and only mark a command 'sent' with an in-flight lease that is re-queued once if it expires (ack remains the durable completion signal).

## RES-P3-002 — Control-plane client has no retry/backoff/circuit-breaker; registration retries forever and telemetry is dropped on failure

Add bounded retries with exponential backoff + jitter for control-plane writes, a small bounded local spool so telemetry/logs survive a short outage, and a registration backoff cap with an operator-visible 'cannot authenticate / server unreachable' state instead of an infinite fixed-interval loop.

## RES-P3-003 — HTTP server sets no read/connection timeout; a declared-but-unsent body pins a handler thread indefinitely

Set Handler.timeout (e.g. 30 s) and/or SO_RCVTIMEO, read the body with a deadline, bound concurrent connections, and return 408 on timeout; correct the MAX_BODY comment to reflect that it only guards oversized declarations.

## SBOM-P3-001 — Live ISO package set is version-unpinned, so the shipped image is neither reproducible nor fully inventoried

Emit the resolved package list with versions (pacman -Q / -Qe) into the release assets alongside the SBOM, and pin to a dated snapshot/archive mirror (or commit a lock) so an ISO build is reproducible.

## SC-P3-001 — ISO build trusts an unpinned third-party repo and an unpinned Docker base; no SBOM/provenance/checksums for app bundles

Pin the container base by digest, use `pacman -Syu` in a versioned build, document and review the omarchy-repo trust decision (or vendor/pin the 580xx packages), and add an SBOM (e.g. Syft) plus SHA256SUMS for the app bundles and a signature/attestation (cosign/SLSA) on release assets. Add a license-report gate.

## SEARCH-P3-001 — History 'search' is client-side only, over a capped 300-row page - not server-side

Add server-side filtering (e.g. q= across label/host/status/preset, plus explicit field filters and stable pagination) with an index, or, if the client-side cap is intentional, document it in the UI and docs so operators know older runs are not searchable. Add a test that a run outside the first page is still findable by the server filter.

## SEARCH-P3-002 — Missing indexes on hot filter paths and no documented index ownership

Add indexes on runs(status), runs(host) and artifacts(run_id,name); document each index's owning query and retention alongside the table inventory (see the retention finding).

## SEC-P3-001 — Static-handler path-prefix check can be bypassed by a sibling dir

Compare resolved real paths, e.g. os.path.commonpath([os.path.realpath(full), os.path.realpath(root)]) == os.path.realpath(root) (an uncommitted local modification in the working tree already does this). Additionally allow-list served file extensions and keep only static assets under the web root.

## SECRET-P3-001 — Control-plane token exposed in URL query string and browser localStorage

Prefer a short-lived, HttpOnly session cookie established via a login POST, and use bearer headers for API calls. If query tokens are unavoidable for EventSource/downloads, mint separate short-TTL stream tokens scoped to read-only and avoid writing the operator token to persistent storage.

## SECRET-P3-002 — Inconsistent token comparison and an unused BENCHD_INSECURE key

Route every token comparison through secrets.compare_digest. Either implement BENCHD_INSECURE (with a loud warning) or remove it from the parser and docs to keep the naming/config set honest.

## SECRET-P3-003 — Per-runner API key stored in cleartext; 0600 chmod is a no-op on Windows

Document the credential file location/type in the secret inventory, set an owner-only ACL on Windows (icacls), and consider storing the runner key in the OS keyring. Add a test/check that the identity file is not group/world-readable on POSIX.

## TEST-P3-001 — The suite silently skips whole test groups, so lost coverage does not fail the run

Track skips explicitly and print a machine-readable skip total; fail (or at least exit non-zero under a BENCH_TEST_STRICT flag) when an expected group cannot run, so a provisioning gap is visible.

## TEST-P3-002 — Wall-clock/sleep based assertions make the suite flake-prone

Replace fixed sleeps with poll-until-timeout helpers that wait on the observed condition, and record a measured flake budget once the CI test job exists.

## TEST-P3-003 — No coverage measurement and no statement of what 'RESULT: PASS' does not cover

Add coverage.py with a threshold, wire the existing --self-test path into CI as an e2e smoke, and document a short 'what PASS excludes' note in README.md and AGENTS.md next to the Testing section.

## USE-P3-001 — Deleting a schedule is immediate with no confirmation, unlike every other destructive control

Wrap the delete in a `confirm()` naming the runner and cadence (as `forgetRunner`/`powerRunner` do), or require the same explicit checkbox used for ISO writes.

## USE-P3-002 — No completion notification for long runs; the only signal is the browser tab title

On a run transitioning out of `running`, raise a persistent toast and (with permission) a Web Notification with host, status and headline metric; keep a small 'unseen results' badge until the operator opens the run.

## USE-P3-003 — Compare gives no empty state, and with a single finished run it compares the run with itself and presents the 0% deltas as a comparison

Disable the compare button and show 'compare needs two finished runs' when fewer than two exist, and reject A === B with a clear message (or auto-pick a different B).

## USE-P3-004 — README release/version strings are stale and mutually inconsistent with VERSION

Replace the hardcoded README version numbers with the release line only (or generate that block), and add a test/lint that fails when a version literal in README.md disagrees with VERSION.

## UX-P3-001 — No prefers-reduced-motion or prefers-color-scheme support; theme is fixed dark

Add `@media (prefers-reduced-motion: reduce)` to stop the pulse/transition animations, and honour `prefers-color-scheme` (or provide a theme toggle) for a light palette.

## UX-P3-002 — Offline runner cards dimmed with opacity .55 drops muted metadata below AA contrast

Dim with a lighter overlay/opacity (or a lighter muted token) so dimmed text stays >=4.5:1, or keep offline state as a badge rather than reducing overall opacity.

## UX-P3-003 — No accessibility or visual-regression tooling or tests for any UI surface

Add a browser-based check (Playwright + axe-core) over the served dashboard, assert tab/focus/keyboard behaviour, and add a Lighthouse/axe CI job; include reduced-motion and a keyboard-only smoke run.

