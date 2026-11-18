# 12_infra_deployment_environment_drift — Prompt 12 - Infrastructure, Deployment, and Environment Drift Audit

- Run: `bench-test-20261013-0819-full-main-b916709`
- Target: `bench-test` @ `b916709` (branch `main`)
- Domain: `12_infra_deployment_environment_drift.md` (area INFRA, prompt)

## Verification Performed

# 12_infra_deployment_environment_drift - 12_infra_deployment_environment_drift.md

Domain subagent `12_infra_deployment_environment_drift` (area INFRA), read-only audit of `C:\temp\bench-test`.

## Checks / Evidence

- **P1 - benchd fails open: with no BENCHD_TOKEN it serves the full operator API unauthenticated (reproduced)** (confidence: High)
  - `server/benchd.py:1413-1415 - find_token() returns None when there is no --token flag, no $BENCHD_TOKEN and no BENCHD_TOKEN= in server/benchd.conf, ~/.config/benchd.conf or /etc/benchd.conf`
  - `server/benchd.py:572-580 - _is_operator() returns True unconditionally when self.token is None; _runner_ok() (582-591) and _caller() (593-600) likewise treat a missing token as fully authorised`
  - `server/benchd.py:1440-1441 - a missing token only prints 'WARNING: no BENCHD_TOKEN set - anyone can register/control' before serve_forever(); startup is never blocked`
  - `server/benchd.service:11 - ExecStart has no --token and relies entirely on /etc/benchd.conf existing; server/benchd.service:11 binds 0.0.0.0`
  - `Reproduced at commit 60ab90eb: `python server/benchd.py --host 127.0.0.1 --port 8899 --db <tmp>` then, with NO Authorization header, GET /api/v1/runners -> 200 {"runners": []}, GET /api/v1/state -> 200, POST /api/v1/register -> 200 {"runner_id":"...","api_key":"..."} (an anonymous caller was issued a runner key)`
  - `tests/harness.py:26,62 - the suite always injects token='test-token', so the no-token path is never tested`
  - Impact: Any host that can reach port 8722 (the service binds 0.0.0.0) gets the whole control plane: read all run history/telemetry/artifacts, register runners, and issue start/stop/update/exec/shell/shutdown/reboot commands. A single missing or misnamed config file turns the lab fleet into an open remote-control endpoint with no error surfaced.
  - Recommendation: Fail closed: if no token is resolved, refuse to start unless an explicit --insecure/--no-auth flag is passed (and bind to 127.0.0.1 in that mode). Document BENCHD_TOKEN as mandatory and add a systemd ExecStartPre or unit condition that the token file exists. Add a test that the server refuses to open when the token is unset.
- **P1 - The shared operator token is baked into publicly downloadable app bundles and the live ISO, and it is the same token that grants operator control** (confidence: High)
  - `.github/workflows/build-app.yml:59-64 - CI passes BENCH_BAKE_AGENT_CONF: ${{ secrets.BENCH_AGENT_CONF }} into packaging/build_app.py`
  - `packaging/build_app.py:66-84 - write_agent_conf() writes that content to bench-agent.conf inside each bundle; README.md:158-163 states the app releases are public so the token is world-readable`
  - `.github/workflows/build-iso.yml:73-82 - the same BENCH_AGENT_CONF secret is written to live/private/bench-agent.conf and baked into /etc/bench-agent.conf of the released ISO`
  - `server/benchd.py:24-27,100 - BENCHD_TOKEN is documented as both the 'join/registration token + operator API bearer'`
  - `server/benchd.py:573-580 - _is_operator() accepts any bearer equal to the shared token; server/benchd.py:1178-1180 also lets that token adopt any existing runner row`
  - `README.md:162-163 acknowledges the exposure but only advises 'use a limited, rotatable one'; benchd.py has no runner-only vs operator-only token split, so a limited token does not exist`
  - Impact: Because the baked value is the join token and the join token is the operator bearer, anyone who downloads a public release zip or the ISO obtains full fleet operator rights - reading all history/telemetry and issuing exec/shell/shutdown/reboot to every runner. The documented mitigation (a limited token) is not implementable with the current single-token model.
  - Recommendation: Introduce a distinct, registration-only token that cannot authenticate as an operator, and bake only that into public artifacts (or omit credentials from public builds entirely). Rotate the current BENCHD_TOKEN. Document clearly that any token shipped in a public release must be non-operator.
- **P2 - Documented BENCHD_DB config key is never read; DB path is hard-coded and has no backup/retention** (confidence: High)
  - `server/benchd.conf.example:8-9 - documents '# BENCHD_DB=/var/lib/benchd/benchd.sqlite' as where the SQLite DB lives`
  - `server/benchd.py:50 - DEFAULT_DB = os.path.join(HERE, 'data', 'benchd.sqlite') (fixed under the code dir)`
  - `server/benchd.py:1402-1415 - find_conf_value()/find_token() only ever look up 'BENCHD_TOKEN'; nothing reads BENCHD_DB`
  - `server/benchd.py:1422 - --db defaults to DEFAULT_DB; there is no BENCHD_DB fallback`
  - `grep for BENCHD_DB across the repository returns exactly one hit (the example file)`
  - Impact: An operator who follows the example and sets BENCHD_DB gets no effect and no warning - the DB silently stays at server/data/benchd.sqlite (i.e. under /opt/bench-test when deployed per docs/CONTROL_PLANE.md, and inside the container's 4 GiB rootfs). The DB holds all history and is WAL-mode with no documented backup, retention or vacuum runbook.
  - Recommendation: Either honour BENCHD_DB in find_conf_value()/main() or remove the key from the example. Add a documented backup/retention procedure (e.g. sqlite3 .backup + vacuum) and a data-path note to the deploy section.
- **P2 - Operator token is transported in URLs and kept in browser localStorage; no TLS/reverse proxy exists in the repo** (confidence: High)
  - `server/benchd.py:578 - _is_operator() accepts ?token=<shared token> as an alternative to a bearer header`
  - `server/web/app.js:101 - TOKEN = new URLSearchParams(location.search).get('token') || localStorage.getItem('benchd_token') || ''`
  - `docs/CONTROL_PLANE.md:206-207 - documents ?token= for SSE/EventSource and file downloads 'because headers cannot be set'`
  - `docs/CONTROL_PLANE.md:210 - 'Put a TLS reverse proxy in front if it is ever exposed beyond the lab' - advice only; no proxy/TLS config is shipped`
  - `server/benchd.py:515-525 - benchd redacts token= in its OWN log lines, but any upstream reverse proxy / access log / browser history will keep the query string`
  - Impact: The shared fleet secret is placed in URLs: it lands in proxy/access logs, browser history and (for SSE/download links) potentially Referer; over plain HTTP on the LAN/overlay it is also sniffable. A leaked URL is equivalent to the operator token.
  - Recommendation: Prefer an Authorization header for API calls and a short-lived, single-purpose stream/download ticket instead of the long-lived token in the URL; ship an example TLS reverse-proxy config (or terminate TLS in the app) and state that ?token= is for a trusted loopback/proxy only.
- **P2 - benchd systemd unit runs as root on 0.0.0.0 with no User/CapabilityBoundingSet and no readiness probe** (confidence: High)
  - `server/benchd.service:11 - ExecStart=/usr/bin/python3 /opt/bench-test/server/benchd.py --host 0.0.0.0 --port 8722`
  - `server/benchd.service:15-18 - hardening is limited to NoNewPrivileges, PrivateTmp, ProtectSystem=full, ProtectHome; there is no User=, DynamicUser=, CapabilityBoundingSet= or ProtectKernelTunables`
  - `docs/CONTROL_PLANE.md:208 - states 'Bind to the LAN/lab address only', contradicting the unit's 0.0.0.0 bind`
  - `server/benchd.py:629-634 - the only health signal is an unauthenticated GET /health (liveness); the unit has no ExecStartPre/health gate and the deploy doc adds none`
  - Impact: The control plane - the process that can exec/reboot every runner - runs as root with full capabilities, so any RCE in the stdlib HTTP handler or SQLite path is a full container compromise; combined with the 0.0.0.0 bind and no TLS, exposure is broader than the docs claim. Operators also have no documented readiness check beyond hitting /health by hand.
  - Recommendation: Add User=/Group= (or DynamicUser=yes) plus CapabilityBoundingSet= and RestrictAddressFamilies; bind to the specific LAN/overlay address in the unit rather than 0.0.0.0; document /health as the readiness probe and (optionally) add an ExecStartPost/WatchdogSec.
- **P2 - Deployment is an unversioned manual pct snippet that does not ship VERSION or write a commit stamp, breaking the fleet staleness comparison** (confidence: Medium)
  - `docs/CONTROL_PLANE.md:172-185 - the entire deploy is hand-run `pct create/push/exec` commands against container 108; no script exists in the repo (glob for deploy*.sh / Makefile / Dockerfile returns nothing)`
  - `docs/CONTROL_PLANE.md:178-179 - only benchd.py + web/ + unit are pushed; VERSION is not copied`
  - `server/benchd.py:267-282 - server_version() reads VERSION and returns '0.0.0+unknown' when it is absent`
  - `server/benchd.py:233-264 - server_git() falls back to a .deployed-commit / .bench-version stamp, but the deploy snippet never writes one`
  - `docs/CONTROL_PLANE.md:226-230 relies on this server-side identity so the fleet view can flag which runners are behind`
  - Impact: A deployment done exactly as documented reports version 0.0.0+unknown and an empty git commit, so /health, /state and the Fleet 'stale' comparison cannot tell what the control plane is running; drift between the deployed server and main is invisible. There is also no rollback path for the server (only the live-USB A/B slot mechanism exists).
  - Recommendation: Add a small deploy script (checked in) that copies the needed files, writes VERSION and a .deployed-commit/.bench-version stamp, and records the commit; document a rollback (keep the previous copy + stamp). Assert the stamp in deployment verification.
- **P3 - Live launcher exports BENCHD_INSECURE and BENCH_AGENT_NAME that nothing consumes (env name drift)** (confidence: High)
  - `live/airootfs/usr/local/bin/bench-agent-env:41-47 - the parser accepts and exports BENCHD_SERVER, BENCHD_TOKEN, BENCHD_INSECURE, BENCH_AGENT_NAME, BENCH_AGENT_INSTANCE`
  - `bench/benchreport.py:158-159 - load_conf() only reads BENCHD_SERVER and BENCHD_TOKEN; no code anywhere reads BENCHD_INSECURE or BENCH_AGENT_NAME (grep across the repo returns no other hits)`
  - `live/airootfs/etc/bench-agent.conf.example:10-11 and README.md:299-302 document only BENCHD_SERVER/BENCHD_TOKEN, so an operator cannot discover the other two keys anyway`
  - Impact: Two accepted config keys are dead. An operator who sets BENCHD_INSECURE expecting to control TLS/http behaviour (or BENCH_AGENT_NAME to name the runner) gets silence; there is no http-vs-https/INSECURE handling in the client at all, so TLS enforcement cannot be configured. This is documentation/code drift that misleads operators.
  - Recommendation: Remove the unused keys from bench-agent-env's allow-list, or implement them (e.g. reject non-local http unless BENCHD_INSECURE=1, and honour BENCH_AGENT_NAME as the runner name). Document whichever set is real in one env matrix.
- **P3 - Environment-specific deploy values (container id 108, IP 192.168.222.188/24) are hard-coded in docs with no inventory, and a prior audit recorded a different address** (confidence: Medium)
  - `docs/CONTROL_PLANE.md:174-177 - pct create 108 ... ip=192.168.222.188/24,gw=192.168.222.1 and --password '...' are fixed literals in the runbook`
  - `docs/CONTROL_PLANE.md:42 - separately refers to the lab box as 172.23.128.0/20 (the WireGuard overlay), a third address space`
  - `docs/audits/repo-deep-dive/20261007-1731-main-4ecee97/lens_focused_security_supply_chain_ci.md:45 - a prior audit states the control plane was reachable at 192.168.222.201:8722, not .188`
  - `No environment inventory / environment matrix file exists in the repo (glob for *inventory*/*matrix* under docs/ returns none)`
  - Impact: Operators cannot tell which host/address/container is the real control plane from the repository; the runbook's fixed values will silently conflict with an existing container or the actual deployed address. The required 'environment inventory / environment matrix' artifacts are absent, so drift between documented and live configuration is undetectable.
  - Recommendation: Move the deploy values into a checked-in, parameterised deploy script/config (or a template) and add an environment inventory + environment matrix doc listing host, address, port, container id, DB path and secret source; keep the example IP clearly marked as an example.

## Verification Performed

Read-only source review of the target at commit `b916709`; the evidence above was
recorded by the domain subagent and normalized by `tools/full_domain.py` (mechanical
report body derived from that recorded findings JSON).

## Findings

| ID | Severity | Title |
|---|---|---|
| INFRA-P1-001 | P1 | benchd fails open: with no BENCHD_TOKEN it serves the full operator API unauthenticated (reproduced) |
| INFRA-P1-002 | P1 | The shared operator token is baked into publicly downloadable app bundles and the live ISO, and it is the same token that grants operator control |
| INFRA-P2-001 | P2 | Documented BENCHD_DB config key is never read; DB path is hard-coded and has no backup/retention |
| INFRA-P2-002 | P2 | Operator token is transported in URLs and kept in browser localStorage; no TLS/reverse proxy exists in the repo |
| INFRA-P2-003 | P2 | benchd systemd unit runs as root on 0.0.0.0 with no User/CapabilityBoundingSet and no readiness probe |
| INFRA-P2-004 | P2 | Deployment is an unversioned manual pct snippet that does not ship VERSION or write a commit stamp, breaking the fleet staleness comparison |
| INFRA-P3-001 | P3 | Live launcher exports BENCHD_INSECURE and BENCH_AGENT_NAME that nothing consumes (env name drift) |
| INFRA-P3-002 | P3 | Environment-specific deploy values (container id 108, IP 192.168.222.188/24) are hard-coded in docs with no inventory, and a prior audit recorded a different address |
