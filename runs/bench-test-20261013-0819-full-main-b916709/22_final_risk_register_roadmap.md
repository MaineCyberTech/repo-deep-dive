# 22_final_risk_register_roadmap — Prompt 22 - Final Risk Register, Roadmap, and Patch Plan

- Run: `bench-test-20261013-0819-full-main-b916709`
- Target: `bench-test` @ `b916709` (branch `main`)
- Domain: `22_final_risk_register_roadmap.md` (area FINAL, prompt)

## Verification Performed

# 22_final_risk_register_roadmap - 22_final_risk_register_roadmap.md

Domain subagent `22_final_risk_register_roadmap` (area FINAL), read-only audit of `C:\temp\bench-test`.

## Checks / Evidence

- **P0 - One shared operator/join token is baked into public app bundles and the live ISO, so any release download yields fleet-wide remote code execution (merged across 10 domains)** (confidence: High)
  - `server/benchd.py:26 - BENCHD_TOKEN is documented as 'join/registration token + operator API bearer'; one secret serves the runner join tier and the highest operator tier`
  - `server/benchd.py:572-580 - _is_operator() accepts that same token as the operator bearer on every privileged route (no scopes, no read-only tier)`
  - `server/benchd.py:1220-1232 - operator-only commands include exec/shell (arbitrary command; run via subprocess shell=True at bench/benchreport.py:811-843, root on the live USB), iso_write/iso_write_slot (raw device write), reboot, shutdown`
  - `.github/workflows/build-app.yml:59-64 - BENCH_BAKE_AGENT_CONF: ${{ secrets.BENCH_AGENT_CONF }} is fed into the public app-bundle build`
  - `packaging/build_app.py:66-84 - write_agent_conf() writes the server URL + BENCHD_TOKEN into every bundle (docstring states the releases are public)`
  - `.github/workflows/build-iso.yml:73-82 - the same BENCH_AGENT_CONF secret is written to live/private/bench-agent.conf and baked into /etc/bench-agent.conf of the published ISO`
  - `README.md:158-163 - states each public app release carries the control-plane token and that it is world-readable, advising only 'use a limited, rotatable one' (no limited token exists)`
  - `docs/CONTROL_PLANE.md:204-207 - documents that operators use this shared join token as bearer or ?token=, with no separate operator credential`
  - `Merged duplicates: INV-P1-001, ARCH-P1-001, SEC-P0-001, ACM-P1-001, ADMIN-P1-001, SC-P1-002, CTR-P1-001, INFRA-P1-002, SECRET-P1-001, CHAIN-P0-001`
  - Impact: An outsider needs only a public release asset (bench-app-*.zip or the live ISO) to read the embedded token and use it as the operator bearer against the LAN-bound control plane: arbitrary command execution on every registered runner (root on the live USB), reboots/power-off, raw block-device writes, and read/delete of all run data. The README's mitigation is unimplementable because there is no non-operator token.
  - Recommendation: Split the credential model: (1) a registration-only enrollment token accepted solely by POST /api/v1/register; (2) operator credentials (ideally per-user, hashed at rest) for commands/schedules/deletes; (3) never bake the operator token into any distributable artifact - bake only the enrollment token or nothing. Make the server refuse operator actions for enrollment-token bearers. Rotate the currently published BENCHD_TOKEN and treat it as compromised. Add a build-time guard that fails the app/ISO build if a shipped file matches the operator-token or GITHUB_TOKEN pattern.
- **P0 - A write-capable GitHub PAT is baked into the publicly downloadable live ISO, and runners auto-pull code from main, turning repo write into fleet code execution (merged across 4 domains)** (confidence: High)
  - `.github/workflows/build-iso.yml:62-71 - the workflow writes secrets.BENCH_UPLOAD_CONF into live/private/bench-upload.conf before the ISO build ('upload credentials baked into the image')`
  - `live/Build-LiveUSB.sh:127-133 - installs that file into the image as /etc/bench-upload.conf (mode 600) inside the airootfs squashfs`
  - `bench/upload.py:10-16 - the documented config shape is GITHUB_TOKEN=github_pat_xxx, a fine-grained PAT with 'Contents: Read/Write' to GITHUB_REPO`
  - `.github/workflows/build-iso.yml:114-124 - the built ISO parts are attached to a public GitHub release via softprops/action-gh-release`
  - `bench/benchreport.py:1435-1472 and bench/agent.py:417-421 - the agent auto-updates at startup and restarts into pulled code; bench/agent.py:260-261 handles 'update' as git pull --ff-only; update_toolkit's sha256 is optional (bench/benchreport.py:1345)`
  - `results/bench-live-linux-20261011-135440/upload.log:1 - a shipped ISO carried the baked PAT and used it to write results to MaineCyberTech/bench-test@main`
  - `Merged duplicates: SC-P0-001, CI-P1-001, SECRET-P1-002, CHAIN-P1-003`
  - Impact: Anyone who downloads the public ISO can extract a live token with write access to the source repository. The next runner start (or any later build) then executes code pushed to main, giving fleet-wide code execution, backdoored releases, and poisoned build artifacts without touching the control plane. This is the composition of the CI-to-production supply-chain chain.
  - Recommendation: Never bake a write-capable PAT into a distributable artifact. Have the uploader authenticate with a dedicated least-privilege identity (scoped GitHub App / deploy key behind an environment protection rule) or upload to a store that cannot influence what runners execute. Make the update sha256 mandatory (not optional), pin runner updates to signed releases/commits, and disable auto_update by default. Rotate the currently baked PAT out of band and assume it is compromised; extend the live/Build-LiveUSB.sh leak guard to cover airootfs credential files.
- **P1 - Control plane fails open: with no BENCHD_TOKEN it serves the full operator API unauthenticated while bound to 0.0.0.0 (reproduced across 4 domains)** (confidence: High)
  - `server/benchd.py:572-574, 582-584, 593-596 - _is_operator(), _runner_ok() and _caller() all return True/unrestricted when self.token is None`
  - `server/benchd.py:1413-1415 - find_token() returns None when there is no --token flag, no $BENCHD_TOKEN, and no BENCHD_TOKEN in the searched conf files`
  - `server/benchd.py:1440-1441 - a missing token only prints a WARNING; serve_forever() starts regardless`
  - `server/benchd.service:11 - ExecStart binds 0.0.0.0:8722 with no --token and relies entirely on /etc/benchd.conf existing`
  - `Reproduced (INFRA domain at commit 60ab90eb, in-process server): with no Authorization header, GET /api/v1/runners -> 200, GET /api/v1/state -> 200, POST /api/v1/register -> 200 (an anonymous caller was issued a runner key)`
  - `tests/harness.py:26,62 - the suite always injects token='test-token', so the no-token fail-open path is never tested`
  - `Merged duplicates: SEC-P1-002, INFRA-P1-001, ACM-P2-004, ADMIN-P2-005 (and the RLS-equivalent report RL-S observation)`
  - Impact: A single missing, empty, or misnamed config file silently exposes the whole fleet on the network: read all history/telemetry/artifacts, register runners, and issue start/stop/update/exec/shell/shutdown/reboot. No error is surfaced, so the operator believes the system is protected.
  - Recommendation: Fail closed: refuse to start (or bind loopback only) unless BENCHD_TOKEN is set and non-default; reject the 'change-me' placeholder from benchd.conf.example. Require an explicit --allow-anonymous/--insecure flag for local development, log the effective bind/auth mode on startup, and add a systemd ExecStartPre/condition that the token file exists. Add a test that the server refuses to open when the token is unset.
- **P1 - Any enrolled runner can take over another runner's identity via unproven machine_id adoption and be handed that runner's api_key (merged across 5 domains)** (confidence: High)
  - `server/benchd.py:1190-1197 - when no runner_id is supplied, the row is adopted by SELECT ... WHERE machine_id=? AND kind=? AND COALESCE(instance,'')=? with no proof of ownership`
  - `server/benchd.py:1198-1200 and :1217 - on adoption the response returns the matched row's api_key to the caller`
  - `server/benchd.py:1163-1189 - the ownership guard added in commit a3dc49b8 applies only to an explicit runner_id; the machine_id branch is deliberately left unguarded (comment lines 1180-1185)`
  - `server/benchd.py:688-689 - the POST gate admits any valid runner bearer (_runner_ok), so a merely-registered runner can reach /register with an arbitrary machine_id`
  - `tests/test_control_plane.py:46-68 - tests cover runner_id takeover but never machine_id-based key recovery`
  - `Reproduced (ACM/ADMIN/API/CHAIN domains): an attacker runner re-registers with the victim's machine_id and receives HTTP 200 with the victim's runner_id AND api_key; the stolen key then drains the victim's queued commands (including operator exec payloads)`
  - `Merged duplicates: SEC-P1-003, API-P1-001, ACM-P1-002, ADMIN-P1-002, CHAIN-P1-002`
  - Impact: Identity resolution relies on a forgeable, client-supplied attribute (DMI uuid / MachineGuid / /etc/machine-id). One runner can impersonate another, steal its key, read/answer its operator commands, and forge or delete its runs/telemetry/logs/artifacts - corrupting fleet data and hiding real commands. The in-code comment claims this takeover class is closed, so reviewers would treat the fleet as safe when it is not.
  - Recommendation: Require proof of ownership on the machine_id branch exactly as for runner_id (the row's own api_key as bearer/body, or the operator credential); otherwise mint a new row. Never echo an existing api_key on an adoption the caller did not prove. For ephemeral live sticks, use a per-machine one-time enrollment token or require operator adoption. Add a regression test mirroring tests/test_control_plane.py:46-68 but claiming machine_id.
- **P1 - No CI test/lint/secret gate, while the release workflow self-modifies main and auto-tags with no approval (merged across 5 domains)** (confidence: High)
  - `git ls-files .github/workflows -> only build-app.yml, build-iso.yml, release.yml; no test workflow exists`
  - `grep of .github for run_all|pytest|py_compile|gitleaks|actionlint -> no matches; AGENTS.md:164-174 makes `python tests/run_all.py` mandatory by policy only ('Never commit with a failing suite')`
  - `.github/workflows/release.yml:22-23,25-26 - triggers on push to main with permissions: contents: write`
  - `.github/workflows/release.yml:81-94,96-107 - rewrites VERSION, commits as 'bench-test release bot', runs git push straight to main, then creates and pushes a tag; no environment/approval gate and no documented break-glass path`
  - `deterministic.json [SUPPLY] - 9 GitHub Action refs are pinned to mutable tags, not commit SHAs (build-app.yml:39,41,87,96,100,104; build-iso.yml:56,116; release.yml:36)`
  - `Merged duplicates: TEST-P1-001, TEST-P2-001, CI-P1-002, CI-P2-004, CI-P2-003, BP-P1-001, BP-P1-002, BP-P2-002, BP-P2-004, AI-P1-001, DET [SUPPLY]`
  - Impact: Every merge to the default branch lands with zero automated test, compile, shell-syntax, or secret-scan verification, and release.yml then auto-publishes a tag and public artifacts. The documented pre-commit gate is advisory only, so a red or malicious change can reach a release unopposed.
  - Recommendation: Add a pinned `.github/workflows/ci.yml` running on pull_request and push to main: `python tests/run_all.py`, `python -m py_compile bench/*.py server/*.py packaging/*.py`, and `bash -n` over bench/*.sh + live/*.sh, on ubuntu-latest and windows-latest, plus gitleaks/actionlint. Pin all actions to commit SHAs. Enable it as a required status check on protected main and make release/build workflows depend on it. Move the automated VERSION commit/tag behind a protected `environment: release` with reviewers, and document the branch model and break-glass procedure.
- **P1 - Data lifecycle is unmanaged: run delete leaves logs behind (reproduced), telemetry/artifacts have no retention, and there is no backup, restore, or incident plan (merged across 6 domains)** (confidence: High)
  - `server/benchd.py:665-672 - DELETE /api/v1/runs/<id> deletes phases, telemetry, events and artifacts but NOT logs; no FOREIGN KEY/cascade exists (SCHEMA at server/benchd.py:94-143)`
  - `server/benchd.py:802-807 - GET /api/v1/runs/<id>/logs serves logs WHERE run_id=? without checking the run exists`
  - `Reproduced (DATA/SEARCH/API/FEAT domains at HEAD): after DELETE -> 200 and GET run -> 404, GET /api/v1/runs/<id>/logs -> 200 still returning the stored lines (row counts: runs=0, logs=2); docs/CONTROL_PLANE.md:132 documents the route as 'delete a run (+data)'`
  - `server/benchd.py:94-143, 653-681 - telemetry/logs/events/artifacts have no TTL, cap, rollup or scheduled prune; the only bulk delete is manual`
  - `docs/CONTROL_PLANE.md:254 documents '~1 row/second per active run' while telemetry arrives at 4 Hz (README.md:55, docs/PHASE_TIMINGS.md:182), and the documented host is a 1-vCPU / 4 GiB LXC rootfs (docs/CONTROL_PLANE.md:174-175)`
  - `.gitignore:27 excludes server/data/, and no script/timer snapshots server/data/benchd.sqlite (DEFAULT_DB, server/benchd.py:50); server/import_results.py:2-14 is a one-way backfill, so the DB cannot be reconstituted and no restore is ever exercised`
  - `git ls-files filtered for incident|runbook|postmortem|oncall|disaster|breach -> zero matches; no DR/IR documentation exists`
  - `Merged duplicates: DATA-P1-001 (+P2-001/002/003), SEARCH-P1-001 (+P2-001/002), API-P2-004, FEAT-P2-001, PERF-P1-001, PRIV-P2-004/005, ARCH-P3-006, DR-P1-001, DR-P1-002 (+P2s), IR-P1-001 (+P2-003), RES-P2-002, 32_backup_restore_drill / 33_incident_tabletop_exercise`
  - Impact: Operator deletion silently fails to remove console logs (which can contain tokens/secrets echoed by exec/benchmark output) and they stay retrievable forever. Unbounded growth fills the 4 GiB rootfs with no warning, after which SQLite writes fail and the control plane silently stops recording. There is no backup, no rehearsed restore, and no incident/DR runbook, so a node loss destroys all fleet history and there is no measured RTO.
  - Recommendation: Add a single explicit list of every run-scoped table to the delete path (or FK ON DELETE CASCADE with PRAGMA foreign_keys=ON), and fix the docs. Add a retention policy (keep N days/runs, downsample old telemetry, store artifacts on the filesystem with the DB holding a path), a scheduled VACUUM, and DB-bytes/rootfs-free warning bands on /health. Add a documented scheduled backup using the SQLite online-backup API and a restore runbook + test (backup, delete, restore, assert row counts + artifact sha256). Write docs/INCIDENT_RESPONSE.md (SEV scale, roles, containment, comms, postmortem).
- **P1 - The most destructive operation fails open on integrity checks, and third-party code is fetched and executed without verification; no SBOM or license inventory exists (merged across 4 domains)** (confidence: High)
  - `bench/benchreport.py:1750-1765 - iso_fetch returns {"ok": True, ...} unconditionally; `verified` is computed but never converts a mismatch into a failure, and a missing SHA256SUMS asset yields verified=None with ok:True`
  - `bench/agent.py:295-315 - _update_and_ack acks 'done' whenever res.get('ok'), so a mismatched/corrupt ISO is staged for iso_write / iso_write_slot`
  - `tests/test_update.py:200-202 - the test asserts `verified is False` but never `ok is False`, enshrining the fail-open path`
  - `bench/Get-Sensors.ps1:13-22 and bench/Sample-Sensors.ps1:37-64 - download the mutable LibreHardwareMonitor 'latest' zip and Add-Type-load its DLL in-process with no pin, hash, or signature check`
  - `bench/Install-GpuFanCurve.ps1:30-62 - downloads nvfancontrol with no hash/signature verification, then registers the extracted executable as a highest-privilege logon task`
  - `packaging/build_app.py:163-179 - the bundle ships tools/lhm (LibreHardwareMonitorLib.dll + ~35 transitive .NET DLLs), but tools/lhm is untracked (.gitignore:22-23) and ships with no license/attribution; no SBOM is produced for the app bundles or the ISO (no sbom|cyclonedx|spdx|syft matches)`
  - `Merged duplicates: RES-P1-001, FILE-P2-001, SC-P1-003 (+SC-P2-001), SBOM-P1-001, SBOM-P1-002, SBOM-P2-001, 35_sbom_license_policy, 36_container_runtime_security`
  - Impact: The integrity check that exists to protect the toolkit's most destructive write (flashing an ISO to a stick / A-B slot) is advisory: a corrupted or tampered image is accepted and acked 'done' with no unverified flag. Sensor/fan features load mutable upstream code into elevated processes on every managed workstation, so a compromised upstream release yields arbitrary code execution with no detection path. Releases redistribute third-party components with no inventory or license text, so 'what is in release X?' and CVE matching are impossible.
  - Recommendation: Make the ISO verdict binding: return ok:False on sha256 mismatch, fail closed when SHA256SUMS is absent, have the agent treat verified=False as failed, and assert ok is False in tests. Pin exact third-party releases and verify a committed SHA-256/Authenticode signature before Expand-Archive/Add-Type or task registration; fail closed on mismatch. Add an SBOM step (e.g. syft/CycloneDX) plus a NOTICE/license file to both build workflows, and a CI check that every bundled binary has a license entry.
- **P1 - ~10,000 generated result files (~55 MB, with machine PII) are committed to a public repo despite a results/ ignore rule (merged across 6 domains)** (confidence: High)
  - `git ls-files results/ -> 10,299 tracked files at HEAD 60ab90eb (~55 MB); .gitignore:2 lists results/ but a gitignore rule never untracks already-committed files`
  - `HYGIENE-P1-001 measured 9,555 tracked result files (~55.1 MB) at commit b9167095; the count rose to 10,299 at HEAD - the two domains' figures are both correct at their respective commits and must be reconciled to one commit stamp (see report)`
  - `Duplicate nested results/results/ tree committed (116 files across 3 runs): INV-P2-002, HYGIENE-P2-002`
  - `examples/omarchy-20261009/runs-index.jsonl:1 - tracked example embeds '/home/user/Projects/bench-test/.venv/bin/python' and a host name; examples/pl8a1v6-20261006/*.nvenc.json:2 - embeds 'C:\\Users\\Admin\\...\\ffmpeg.exe'`
  - `results/bench-live-linux-20261011-135440/.../sys-info.log:1 - committed run log embeds full host inventory (CPU/GPU/disk models, NIC state); AN-P2-001 records a committed example exposing a real GPU serial plus MAC/IP`
  - `README.md:357-363 - explains that the repository and its ISO releases are public, so committed hostnames/usernames are world-readable (and cannot be un-published)`
  - `deterministic.json [PORT] P2 - CRLF is committed for 11 files (all under results/), and AGENTS.md:110-113 requires LF + exec bits, so the committed tree already violates the pack's own hygiene rules`
  - `Merged duplicates: HYGIENE-P1-001, HYGIENE-P2-002, HYGIENE-P2-004, INV-P2-001, INV-P2-002, INV-P3-001, PRIV-P1-001, PRIV-P2-002, AN-P2-001, AN-P2-002, DET [PORT], 18_privacy_compliance_data_governance, 21_repo_hygiene_maintainability`
  - Impact: Every clone/fetch carries tens of MB of generated output and machine fingerprints, and the ignore rule gives a false sense of safety so the tracked set keeps growing. Because the repo/releases are public, embedded usernames (Admin), absolute home paths, hostnames, NIC/MAC and GPU serials permanently disclose and correlate user/machine identities. Diffs, blame and merges are dominated by artifacts rather than code.
  - Recommendation: Untrack the generated tree (`git rm -r --cached results/`), keep the .gitignore entry, and publish run output as CI/release artifacts (or a separate results repo/branch) instead of on main; add a CI guard that fails if a PR stages files under results/. Add a redaction pass (basename/relative paths only; strip usernames, absolute home paths, hostnames, serials, MACs) before output is written, and scrub the committed examples/results. Reconcile the count and CRLF state against one commit stamp.

## Verification Performed

Read-only source review of the target at commit `b916709`; the evidence above was
recorded by the domain subagent and normalized by `tools/full_domain.py` (mechanical
report body derived from that recorded findings JSON).

## Findings

| ID | Severity | Title |
|---|---|---|
| FINAL-P0-001 | P0 | One shared operator/join token is baked into public app bundles and the live ISO, so any release download yields fleet-wide remote code execution (merged across 10 domains) |
| FINAL-P0-002 | P0 | A write-capable GitHub PAT is baked into the publicly downloadable live ISO, and runners auto-pull code from main, turning repo write into fleet code execution (merged across 4 domains) |
| FINAL-P1-001 | P1 | Control plane fails open: with no BENCHD_TOKEN it serves the full operator API unauthenticated while bound to 0.0.0.0 (reproduced across 4 domains) |
| FINAL-P1-002 | P1 | Any enrolled runner can take over another runner's identity via unproven machine_id adoption and be handed that runner's api_key (merged across 5 domains) |
| FINAL-P1-003 | P1 | No CI test/lint/secret gate, while the release workflow self-modifies main and auto-tags with no approval (merged across 5 domains) |
| FINAL-P1-004 | P1 | Data lifecycle is unmanaged: run delete leaves logs behind (reproduced), telemetry/artifacts have no retention, and there is no backup, restore, or incident plan (merged across 6 domains) |
| FINAL-P1-005 | P1 | The most destructive operation fails open on integrity checks, and third-party code is fetched and executed without verification; no SBOM or license inventory exists (merged across 4 domains) |
| FINAL-P1-006 | P1 | ~10,000 generated result files (~55 MB, with machine PII) are committed to a public repo despite a results/ ignore rule (merged across 6 domains) |
