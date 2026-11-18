# 38_env_secret_rotation — Prompt 38 - Environment and Secret Rotation Audit

- Run: `bench-test-20261013-0819-full-main-b916709`
- Target: `bench-test` @ `b916709` (branch `main`)
- Domain: `38_env_secret_rotation.md` (area SECRET, prompt)

## Verification Performed

# 38_env_secret_rotation - 38_env_secret_rotation.md

Domain subagent `38_env_secret_rotation` (area SECRET), read-only audit of `C:\temp\bench-test`.

## Checks / Evidence

- **P1 - Shared operator/join token is baked into public app release bundles** (confidence: High)
  - `.github/workflows/build-app.yml:59-64 - build step sets env BENCH_BAKE_AGENT_CONF: ${{ secrets.BENCH_AGENT_CONF }}`
  - `packaging/build_app.py:66-84 - write_agent_conf() writes the secret content to <bundle>/bench-agent.conf; docstring line 70-72 admits CI passes the secret so a downloaded app auto-registers and the app releases are public (world-readable)`
  - `bench/benchreport.py:138-152 - the agent/GUI/TUI load (server, token) from <toolkit>/bench-agent.conf baked into the bundle`
  - `server/benchd.py:14-26 - the single BENCHD_TOKEN is BOTH the join/registration token AND the operator API bearer`
  - `README.md:158-163 - README instructs baking BENCH_AGENT_CONF into bundles and warns the token is world-readable`
  - Impact: Anyone who downloads the public app release gets the control-plane token. In this app that token is the operator bearer (server/benchd.py:15,26), so it grants full control-plane access: registering runners, reading all run/telemetry data, and issuing privileged commands (update/exec/shell/reboot - benchd.py:1223-1225). The README's suggested mitigation ('use a limited, rotatable token') is unsupported by the code, which has no limited/runner-only registration token.
  - Recommendation: Do not bake a shared operator token into public artifacts. Introduce a distinct, runner-scoped bootstrap/registration token (accepted only by POST /api/v1/register, unable to act as operator), or have the bundle ship empty and prompt for config. If a token must ship, generate a per-build token and document its immediate revocation.
- **P1 - Write-capable GitHub PAT is baked into the public live-USB ISO** (confidence: High)
  - `.github/workflows/build-iso.yml:62-71 - CI writes secrets.BENCH_UPLOAD_CONF to live/private/bench-upload.conf`
  - `live/Build-LiveUSB.sh:127-132 - installs it as /etc/bench-upload.conf with mode 600 into the squashfs image`
  - `bench/upload.py:10-16 - config format documents GITHUB_TOKEN=github_pat_xxx with 'Contents: Read/Write'`
  - `README.md:357-363 and AGENTS.md:176-182 - state ISO releases are public downloads and the token is world-readable; rotate if a stick is shared`
  - Impact: The ISO is attached to public GitHub releases (build-iso.yml:114-125). File mode 600 is meaningless inside a read-only squashfs that anyone can unsquashfs. The contained fine-grained PAT has Contents: Read/Write on the target repo, so an attacker can push arbitrary commits/results to the repository.
  - Recommendation: Never bake a long-lived write PAT into a public image. Upload results via a short-lived token, a GitHub App installation token minted at boot, or a dedicated results-only repository with minimum scope; otherwise ship the ISO with no upload credentials and have the operator drop bench-upload.conf on BENCHDATA. Document and test revocation of the baked PAT.
- **P2 - Placeholder token 'change-me' is accepted silently; no token strength/startup validation** (confidence: High)
  - `server/benchd.conf.example:6 - BENCHD_TOKEN=change-me`
  - `live/airootfs/etc/bench-agent.conf.example:11 - BENCHD_TOKEN=change-me`
  - `server/benchd.py:1413-1415 - find_token() returns any non-empty value from --token/$BENCHD_TOKEN/conf without validation`
  - `server/benchd.py:1430,1439-1441 - Handler.token is set to whatever was found; the only warning fires when the token is absent, not when it is a known placeholder`
  - Impact: An operator copying the example verbatim gets a well-known, guessable operator token, and the server reports 'token+login' as if correctly configured. There is no length/entropy check, so a weak token is accepted without warning. There is also no runtime env validation for BENCHD_SERVER/token on the client side beyond a truthiness check (bench/agent.py:412-413).
  - Recommendation: Refuse to start (or hard-fail) when BENCHD_TOKEN is a known placeholder (change-me, changeme, test, empty) or is shorter than a minimum length; log a clear remediation. Add a unit test asserting weak tokens are rejected.
- **P2 - No secret rotation / revocation / break-glass runbook or inventory** (confidence: High)
  - `grep -ri 'rotat|revok|break.?glass|secret_rotation|emergency' across *.md returned only advisory sentences: README.md:162, README.md:362, AGENTS.md:181`
  - `docs/ contains CONTROL_PLANE.md, DATA.md, METHODOLOGY.md, FUTURE_WORK.md, PHASE_TIMINGS.md - no secret rotation runbook`
  - `Prompt 38 required companion artifacts secret_rotation_runbook.md, environment variable inventory, secret classification, emergency revocation plan - none present`
  - Impact: The two tokens above (control-plane join/operator token, GitHub write PAT) have no documented rotation cadence, no revocation steps, and no evidence of ever being rotated. A leaked ISO/bundle token cannot be promptly revoked because the procedure is undocumented, and there is no inventory of which credentials exist or where they are baked.
  - Recommendation: Add docs/secret_rotation_runbook.md containing: an environment-variable/secret inventory, classification (operator token, runner key, GitHub PAT, OpenAI/LLM key if any), the exact rotation + revocation commands (request runner key re-issue; regenerate PAT; rebuild + re-release artifacts), a break-glass procedure, and a tested validation step. Track rotation dates/artifacts per the extended checks.
- **P3 - Control-plane token exposed in URL query string and browser localStorage** (confidence: Medium)
  - `server/benchd.py:15 - operators authenticate as bearer (API/CLI) or ?token= (web UI/SSE)`
  - `server/benchd.py:578-579 - query-string token is accepted for any endpoint`
  - `server/web/app.js:101 - TOKEN read from location.search ?token=`
  - `server/web/app.js:171 - token persisted to localStorage('benchd_token')`
  - `server/web/app.js:179,1582-1583 - EventSource and download links embed ?token=`
  - `server/benchd.py:518-524 - server log redacts token= (acknowledges the query-string risk)`
  - Impact: A long-lived operator token placed in a URL leaks to browser history, Referer headers, bookmarks, and any reverse proxy that does not redact it, and it is readable by any same-origin JS via localStorage (the server also sets Access-Control-Allow-Origin: * on every response - benchd.py:533).
  - Recommendation: Prefer a short-lived, HttpOnly session cookie established via a login POST, and use bearer headers for API calls. If query tokens are unavoidable for EventSource/downloads, mint separate short-TTL stream tokens scoped to read-only and avoid writing the operator token to persistent storage.
- **P3 - Inconsistent token comparison and an unused BENCHD_INSECURE key** (confidence: Medium)
  - `server/benchd.py:576 - bearer compared with secrets.compare_digest`
  - `server/benchd.py:578 - query-string token compared with '=='`
  - `server/benchd.py:586,598 - runner bearer compared with '=='`
  - `live/airootfs/usr/local/bin/bench-agent-env:42 - BENCHD_INSECURE is parsed/exported but no other file reads it (git grep found only this occurrence)`
  - Impact: Mixed use of constant-time vs plain equality for token checks is an inconsistency; the practical timing risk is low but avoidable. BENCHD_INSECURE is advertised in the allowed-keys list yet is never consumed, so it silently does nothing - misleading operators about an insecure-TLS escape hatch.
  - Recommendation: Route every token comparison through secrets.compare_digest. Either implement BENCHD_INSECURE (with a loud warning) or remove it from the parser and docs to keep the naming/config set honest.
- **P3 - Per-runner API key stored in cleartext; 0600 chmod is a no-op on Windows** (confidence: Medium)
  - `bench/benchreport.py:341-342 - identity file ~/.config/bench-agent.json (or $BENCH_AGENT_IDENTITY)`
  - `bench/benchreport.py:355-374 - save_identity() writes {runner_id, api_key} as plain JSON, then os.chmod(p, 0o600) inside a try/except that swallows failures`
  - `server/benchd.py:1203,1217 - the server issues a per-runner api_key (secrets.token_urlsafe(32)) returned at registration`
  - Impact: On Windows os.chmod cannot enforce POSIX mode bits, so the runner key sits in a user-profile file with default ACLs; the toolkit targets Windows PowerShell hosts. Any local process/user able to read the profile can impersonate the runner (and, because the token is also the join token path, is handed further privilege).
  - Recommendation: Document the credential file location/type in the secret inventory, set an owner-only ACL on Windows (icacls), and consider storing the runner key in the OS keyring. Add a test/check that the identity file is not group/world-readable on POSIX.

## Verification Performed

Read-only source review of the target at commit `b916709`; the evidence above was
recorded by the domain subagent and normalized by `tools/full_domain.py` (mechanical
report body derived from that recorded findings JSON).

## Findings

| ID | Severity | Title |
|---|---|---|
| SECRET-P1-001 | P1 | Shared operator/join token is baked into public app release bundles |
| SECRET-P1-002 | P1 | Write-capable GitHub PAT is baked into the public live-USB ISO |
| SECRET-P2-001 | P2 | Placeholder token 'change-me' is accepted silently; no token strength/startup validation |
| SECRET-P2-002 | P2 | No secret rotation / revocation / break-glass runbook or inventory |
| SECRET-P3-001 | P3 | Control-plane token exposed in URL query string and browser localStorage |
| SECRET-P3-002 | P3 | Inconsistent token comparison and an unused BENCHD_INSECURE key |
| SECRET-P3-003 | P3 | Per-runner API key stored in cleartext; 0600 chmod is a no-op on Windows |
