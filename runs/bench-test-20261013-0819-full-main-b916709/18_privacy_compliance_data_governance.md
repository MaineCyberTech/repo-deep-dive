# 18_privacy_compliance_data_governance — Prompt 18 - Privacy, Compliance, and Data Governance Audit

- Run: `bench-test-20261013-0819-full-main-b916709`
- Target: `bench-test` @ `b916709` (branch `main`)
- Domain: `18_privacy_compliance_data_governance.md` (area PRIV, prompt)

## Verification Performed

# 18_privacy_compliance_data_governance - 18_privacy_compliance_data_governance.md

Domain subagent `18_privacy_compliance_data_governance` (area PRIV), read-only audit of `C:\temp\bench-test`.

## Checks / Evidence

- **P1 - Unredacted hostnames and absolute home paths (usernames) committed to the public repository** (confidence: High)
  - `examples/omarchy-20261009/runs-index.jsonl:1 - tracked example embeds "python": "/home/user/Projects/bench-test/.venv/bin/python" and an absolute "report" path, plus host "omarchy"`
  - `examples/pl8a1v6-20261006/DESKTOP-PL8A1V6-20261006-101905.nvenc.json:2 - tracked example embeds "ffmpeg": "C:\\Users\\Admin\\AppData\\Local\\Microsoft\\WinGet\\...\\ffmpeg.exe"`
  - `examples/omarchy-20261009/omarchy-linux-20261009-013222.md:5 - published markdown repeats the /home/user/Projects/bench-test path`
  - `results/bench-live-linux-20261011-205857/bench-live-linux-20261011-205857-logs/_furmark_log.txt:6 - tracked run log records the same /home/user/Projects/bench-test path and the machine's home directory`
  - `.gitignore:2-5 - results/ and *.log are ignored, but these artifacts are tracked (force-added); commit 83c168cc 'bench: bench-live-linux-20261013-080711 (744 files)' shows run output being committed`
  - `README.md:357-363 - the repo explains that the repo and ISO releases are public, so hostnames/usernames in committed artifacts are world-readable`
  - Impact: Run artifacts users are told to keep and share embed the operator's Windows username (Admin), absolute home paths, and machine hostnames. Because the repository and releases are public, this permanently discloses user/machine identifiers and directory layout that can be used to fingerprint and correlate a person/machine, and it cannot be un-published once pushed.
  - Recommendation: Scrub committed examples/results of usernames, absolute home paths and hostnames (keep only basename/relative paths), add a redaction pass before output is written, and stop force-adding run output under results/ — keep it git-ignored.
- **P2 - Collectors capture stable hardware identifiers and PII with no redaction mode, and the uploader publishes the whole results directory to public GitHub** (confidence: High)
  - `bench/Get-SystemInfo.ps1:10 - captures $env:COMPUTERNAME as the host name`
  - `bench/Get-SystemInfo.ps1:36 - captures DIMM "serial" (SerialNumber)`
  - `bench/Get-SystemInfo.ps1:49 - captures GPU serial and uuid via nvidia-smi`
  - `bench/Get-SystemInfo.ps1:87 - captures NIC "mac" and IPv4 addresses`
  - `bench/Get-EnvInfo.ps1:54-55 - captures startup commands and DNS servers; :41-45 captures Defender/TPM/BitLocker security posture`
  - `bench/linux_info.py:73,79 - captures GPU uuid and other GPU users' compute processes at run start`
  - `bench/upload.py:186-203 - walks the entire results directory and commits every file (INLINE_EXTS includes .log/.json/.jsonl) to the configured public repo via the GitHub API`
  - `docs/audits/repo-deep-dive/20261007-1731-main-4ecee97/follow_up_register.md:8 - prior finding DATA-P2-001 (hardware identifiers + PII, no redaction) is still marked open`
  - Impact: Each run produces device-unique serials, UUIDs, MAC/IP addresses, hostname, software/startup inventory and security posture (Defender/BitLocker/TPM). There is no -Anonymize/redact switch, and the normal workflow uploads the raw directory to a public GitHub repo, so publishing a result leaks machine-identifying and operating-environment data.
  - Recommendation: Add a redaction mode (drop/hash serials, UUIDs, MACs, IPs, usernames, startup commands, DNS) and make it the default for shareable output; document the sensitive fields; default the uploader to redacted output unless explicitly overridden.
- **P2 - No attributable audit trail for privileged/admin actions (shared operator token, commands record no actor)** (confidence: High)
  - `server/benchd.py:119-122 - commands table has id/runner_id/run_id/kind/payload/status/timestamps/result but no actor/operator column`
  - `server/benchd.py:1228 - command insert records no identity`
  - `server/benchd.py:572-580 - _is_operator accepts a single shared BENCHD_TOKEN as bearer or ?token=; there is no per-user identity`
  - `server/benchd.py:653-680 - DELETE run/runner/schedule are gated only by the shared operator token and leave no actor record`
  - `docs/CONTROL_PLANE.md:275 - roadmap still lists 'Operator logins (per-user accounts) instead of the shared join token'`
  - Impact: Destructive and high-impact commands (shutdown, reboot, exec/shell, iso_write, iso_write_slot, run/runner delete) can be issued by anyone holding the shared token, and nothing records who did it. There is no way to answer 'who rebooted this box / ran this shell / deleted this run' — a governance and incident-response gap.
  - Recommendation: Record an actor (per-user id or at least a named/rotatable operator key id + source IP) on command and delete operations, persist an append-only admin audit log, expose it read-only, and implement the per-user operator accounts already on the roadmap.
- **P2 - Deletion is incomplete: deleting a run leaves its console logs, and deleting a runner leaves its runs/telemetry/inventory** (confidence: High)
  - `server/benchd.py:665-672 - DELETE /runs/<id> purges phases, telemetry, events, artifacts and the run row, but not the 'logs' table`
  - `server/benchd.py:116-118 - the logs table (run console lines, which can contain paths/commands) is part of the schema`
  - `server/benchd.py:673-680 - DELETE /runners/<id> removes only commands, schedules and the runner row; the runner's historical runs, telemetry, logs and system inventory remain`
  - `tests/test_control_plane.py:321-325 - the delete test only asserts GET /runs/<id> returns 404; it does not assert logs/telemetry are gone`
  - Impact: A 'delete' that a subject or operator relies on for erasure does not actually remove all personal/device data: run console logs survive run deletion, and a whole machine's run history and inventory survive runner deletion. This breaks deletion/export promises and leaves stale identifiable data.
  - Recommendation: Delete the run's logs too, and cascade runner deletion to its runs (phases/telemetry/events/artifacts/logs); extend the tests to assert rows are gone, not just that the endpoint 404s.
- **P2 - No retention or scheduled-purge policy for telemetry, logs, artifacts and the SQLite database** (confidence: High)
  - `server/benchd.py:1388-1398 - scheduler_loop only reaps stale runs, ephemeral runners and dropped commands; there is no age-based deletion or retention pass`
  - `server/benchd.py:94-143 - schema defines telemetry/logs/artifacts with no TTL or created-at purge support`
  - `docs/CONTROL_PLANE.md:254 - 'SQLite uses WAL; the DB grows ~1 row/second per active run' with no documented retention limit`
  - `grep for retention|prune|purge|vacuum in server/benchd.py and docs/ returns no retention mechanism (only the reapers)`
  - Impact: Run telemetry (4 Hz rows), console logs, artifacts and full inventories accumulate indefinitely with no defined retention period, no archival, and no deletion schedule. There is no documented data-lifecycle rule for operators or auditors to rely on.
  - Recommendation: Document a retention policy per data type (e.g. telemetry N days, logs/artifacts N days) and implement a scheduled purge (configurable), running VACUUM/periodic checkpoint; surface retained volume in the UI.
- **P2 - Per-runner API keys are stored in plaintext in SQLite and looked up by direct comparison** (confidence: High)
  - `server/benchd.py:98 - runners.api_key is a plain TEXT column`
  - `server/benchd.py:1203 - keys are generated with secrets.token_urlsafe(32) and stored verbatim (:1204-1214)`
  - `server/benchd.py:570 - _runner_from_bearer looks a runner up by 'SELECT * FROM runners WHERE api_key=?', i.e. the raw key is the lookup key`
  - `server/benchd.py:211-212 / docs/CONTROL_PLANE.md:211-212 - server/data (the SQLite db) is git-ignored but is a plain file on the lab box, backed up/copied by deploy steps`
  - Impact: Auth records (long-lived per-runner API keys that authorize run writes and command acknowledgement) are recoverable in cleartext from any copy of the database or backup. A read of the db (or a backup) hands over every runner credential, and there is no rotation/invalidation lifecycle.
  - Recommendation: Store only a salted hash of each API key and compare hashes, add key rotation/revocation, and document the credential lifecycle. Even in a lab, avoid storing recoverable runner credentials.
- **P3 - Operator token is handled via URL query string and browser localStorage** (confidence: Medium)
  - `server/web/app.js:101 - TOKEN is read from ?token= or localStorage.getItem('benchd_token')`
  - `server/web/app.js:171 - token written to localStorage`
  - `server/web/app.js:179,1582 - token appended to the SSE stream and telemetry/artifact download URLs as ?token=`
  - `server/benchd.py:518-524 - benchd redacts token= in its own log lines, acknowledging the query-string exposure, but a reverse proxy/browser history would still capture it`
  - Impact: The operator credential can leak through browser history, referrer headers, bookmarks and any intermediary proxy/access log. Anyone who obtains the token gains full operator control (including shutdown/reboot/exec).
  - Recommendation: Prefer a short-lived token exchange / header-based auth, avoid long-lived secrets in query strings and localStorage, and document proxy log-redaction requirements if ?token= must stay for downloads.
- **P3 - No privacy/compliance documentation: data classification, retention policy, vendor/processor inventory, consent; secrets baked into public ISOs** (confidence: High)
  - `docs/ contains METHODOLOGY/CONTROL_PLANE/DATA/PHASE_TIMINGS/FUTURE_WORK only - no privacy policy, data-classification, retention or DPA/processor doc (docs/ listing)`
  - `README.md:357-363 and docs/CONTROL_PLANE.md:202-212 - the only data-governance guidance is 'bind to the LAN; tokens are git-ignored'`
  - `.github/workflows/build-iso.yml:64-82 - BENCH_UPLOAD_CONF (GitHub PAT) and BENCH_AGENT_CONF (control-plane token) are written into the image; README.md:162 documents the token is world-readable in public releases`
  - `bench/net_bench.py:95-97 - data is sent to third-party Cloudflare speed endpoints; bench/upload.py:31 - GitHub API; bench/bootstrap.py:48-49 - python-build-standalone downloads`
  - `No cookie or consent handling exists (no document.cookie usage in server/web/); the dashboard is a LAN tool, so cookie/consent flows are Not Applicable`
  - Impact: There is no documented data inventory, retention/erasure policy, or third-party processor list, and credentials for external services are shipped in publicly downloadable artifacts. Without these documents operators cannot answer privacy/compliance questions, and the baked credentials are an ongoing exposure if a stick leaves the lab.
  - Recommendation: Add a data-classification inventory and retention/erasure policy, a vendor/processor inventory (Cloudflare, GitHub, python-build-standalone, PyTorch/onnxruntime indexes, LibreHardwareMonitor mirror, Ollama), and a control-readiness note. Stop baking long-lived tokens into public ISOs or make bundling strictly opt-in with forced rotation.

## Verification Performed

Read-only source review of the target at commit `b916709`; the evidence above was
recorded by the domain subagent and normalized by `tools/full_domain.py` (mechanical
report body derived from that recorded findings JSON).

## Findings

| ID | Severity | Title |
|---|---|---|
| PRIV-P1-001 | P1 | Unredacted hostnames and absolute home paths (usernames) committed to the public repository |
| PRIV-P2-001 | P2 | Collectors capture stable hardware identifiers and PII with no redaction mode, and the uploader publishes the whole results directory to public GitHub |
| PRIV-P2-002 | P2 | No attributable audit trail for privileged/admin actions (shared operator token, commands record no actor) |
| PRIV-P2-003 | P2 | Deletion is incomplete: deleting a run leaves its console logs, and deleting a runner leaves its runs/telemetry/inventory |
| PRIV-P2-004 | P2 | No retention or scheduled-purge policy for telemetry, logs, artifacts and the SQLite database |
| PRIV-P2-005 | P2 | Per-runner API keys are stored in plaintext in SQLite and looked up by direct comparison |
| PRIV-P3-001 | P3 | Operator token is handled via URL query string and browser localStorage |
| PRIV-P3-002 | P3 | No privacy/compliance documentation: data classification, retention policy, vendor/processor inventory, consent; secrets baked into public ISOs |
