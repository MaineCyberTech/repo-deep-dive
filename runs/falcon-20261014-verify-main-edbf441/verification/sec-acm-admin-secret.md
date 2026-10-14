# Post-merge verification re-audit — SEC / ACM / ADMIN / SECRET findings

- Repo: `/home/user/falcon-build` @ `edbf441` (`edbf441d03cfba1f2a2e923a94021e1cbab0c338`, main, clean), re-checked 2026-10-14.
- Original run: `falcon-20261011-0416-full-f5cb7c9`; previous verification: `3623d2e` (2026-10-12), report `97_verification_sec-acm-admin-secret.md`.
- Scope: 16 findings (`scope-97.json`): ACM-P2-001/003, ACM-P3-001/002, ADMIN-P2-001/002/003, SEC-P2-001/002/004, SEC-P3-004/005, SECRET-P2-001/002, SECRET-P3-001/002.
- Method: read-only repo inspection at `edbf441`; live read-only checks (origin curl probes, sudo/docker read-only, nftables, Wazuh agent config, central OpenSearch audit query, Cloudflare zone API GETs, DO-watcher read-only SSH to the independent site host, GitHub Actions run logs). No secret values are reproduced anywhere in this report or its notes.

Result: **4 verified-fixed, 4 partially-fixed, 8 open, 0 owner-accepted, 0 regressed.**

## Summary table

| ID | Sev | Audit status | Verdict | Key evidence |
|---|---|---|---|---|
| ACM-P2-001 | P2 | partially-fixed | partially-fixed | Live `/srv/falcon/secrets/vpn_enroll.token` still 1 bare line (fields=1, 49 B, 0600 root, mtime 2026-09-28); 0 per-device bindings (clients dir empty); closure check still has no bare-token test (`automation/validation/enrollment_closure_check.sh:84-93`); decision log issuance "NOT activated" (`ledgers/decision_log.md:271`); expiry mechanism itself works (SEC-P2-004) |
| ACM-P2-003 | P2 | verified-fixed | verified-fixed | Deployed == repo `enroll-service.py` (cmp + sha256 `cdd4c671…`); closure timer ran 2026-10-14 00:00Z; `falcon_enrollment_deployed_match 1` in the live textfile; drift rule `bootstrap/90-alerting.sh:687-689` |
| ADMIN-P2-001 | P2 | open | open | Origin probes 2026-10-14: falcon→302 `/login`, `/dash`→302 app login, iris→302 `/dashboard`, soc→302 `/app/login`; only `/ntop`→401 basic auth; R-15 unchanged and still cites "ntfy basic auth" (`ledgers/risk_register.md:18`) |
| ADMIN-P2-002 | P2 | open | partially-fixed | DO watcher enforcement check live + passing (deployed hash `239d3a4c…` == repo, cron \*/5, 3199 "posture ok" lines, falcon/iris/soc→302 Cloudflare Access); external-smoke at `ee4be3f` now explicitly reachability-only + summary aligned ("the DO watcher does"); residual: enroll accepted on 404 by both checks |
| ADMIN-P2-003 | P2 | open | partially-fixed | Traefik log rotation now LIVE (`/etc/logrotate.d/falcon-traefik`: daily/50M/keep 7/copytruncate; access.log 128 KB + .1/.2.gz/.3.gz, the 79.5 MB unrotated file gone) but not codified in the repo and no `maxSize` in `config/traefik/traefik.yml:30-32`; container logs still not shipped (Wazuh agent localfiles journald/audit/active-responses/dpkg; `config/vector/aggregator.yaml` sources syslog_tcp/edge_ingest/internal_metrics); OSD REST audit live (`security-auditlog-2026.10.13` = 10,700) |
| SEC-P2-001 | P2 | open | open | `ntfy-auth` dead config removed (`config/traefik/dynamic.yml:26-28`; live bind-mounted config identical) — that part closed; no origin auth on grafana/dash/iris/soc/enroll (routers `dynamic.yml:89-135` carry only sec-headers+public-rate-limit); full-tree grep: no `Cf-Access-Jwt`/forwardAuth handling anywhere |
| SEC-P2-002 | P2 | open | open | Rate limit keys on `CF-Connecting-IP` (`dynamic.yml:36-43`, live) — that part fixed; residual unchanged: no login-path middleware, enroll limiter still fleet-wide behind Traefik (`enroll-service.py:17-19,48-52`), no per-account lockout on OSD/Wazuh/IRIS |
| SEC-P2-004 | P2 | verified-fixed | verified-fixed | Same evidence as ACM-P2-003; public `enroll…/health` → 200 and origin `/health` → 200 (ingress + service live); expiry parsing/403 at `automation/vpn/enroll-service.py:84-108` |
| SECRET-P2-001 | P2 | open | partially-fixed | Register now 9/20 resolved (2 ROTATED + 7 DONE with E-VM101-DECOMMISSION-20260927; `check_rotation_register.py` = 20 items/9 rotated/11 pending; commit `52a5ccc`); 11 owner-console rows pending; vendored estate unchanged: 23 files under `mct/scripts`+`mct/deploy-scripts` source stores wholesale, 20 with `set -a`, `env_key.sh` 0× in `mct/`; separate hygiene rotation `f82f82f` (2 creds, capture redacted) |
| SECRET-P2-002 | P2 | verified-fixed | verified-fixed | Live `check_owner_env.py --strict` = 11 keys/expected 11/0600/0 unknown/0 missing/0 malformed → PASS exit 0; validator wired `ci/validate.py:670-729` and CI runs it (`.github/workflows/validate.yml:121`); `pi_password` documented in `.env.example:22`, `OWNER_ENV_INVENTORY.md:50-53` (11 keys), commit `1b14231` |
| ACM-P3-001 | P3 | open | open | Still no consolidated matrix artifact (find finds none outside `docs/audits/`/evidence); knowledge still spread over the same 4 docs; no commit/decision in `3623d2e..edbf441` addresses it |
| ACM-P3-002 | P3 | open | open | CF API 2026-10-14: falcon app `a8bb98c6` = 2× allow-domain, **no** bypass; soc `adfd5945` + iris `88aec22b` = bypass `142.105.190.25/32` + allow; dead apps `falcon-dash`/`falcon-ntfy` still exist; `dash.falcon.mainecybertech.us` still a proxied CNAME (public TLS handshake fails, no route); `ACCESS_AND_ACCOUNTS.md:126-130` still claims every app carries a bypass |
| SEC-P3-004 | P3 | open | open | Live nft input chain has the client-peer drop for 10.99.0.20/.21/.22 on tcp 9443/15140/15141 (`config/nftables/falcon.nft:33`; `/etc/nftables.conf` sha256 `91fe36ef…` == repo) but syslog/NetFlow accepts (514/1514/1515/2055) remain peer-unrestricted; `PORT_PROTOCOL_MATRIX.md:107-111` still says the residual "is resolved at the config level" |
| SEC-P3-005 | P3 | verified-fixed | verified-fixed | Live: central OSD `opensearch_security.cookie.secure: true` (repo `config/central/opensearch_dashboards.yml:5`), Wazuh dashboard true (`automation/wazuh/multi-node/config/wazuh_dashboard/opensearch_dashboards.yml:16`), Grafana `GF_SECURITY_COOKIE_SECURE=true` (`compose/central/docker-compose.yml:210`) |
| SECRET-P3-001 | P3 | open | open | Register rows 13/18 carry the consolidated path (now DONE) but row 19 still just "IRIS `.env`" (`CREDENTIAL_ROTATION_REGISTER.md:38`); vendored checklist rows 13/16/18/19/20 still name `/opt/mct-security-stack/...` (`mct/runbooks/credential-rotation-checklist.md:42-49`); live old paths absent, `/srv/falcon/secrets/{mct,iris-web}.env` present (0600) |
| SECRET-P3-002 | P3 | open | open | `OWNER_DECISIONS.json` OD-04 = PENDING (`:36`); `BREAK_GLASS_CUSTODY.md:5-8` records PENDING; no custodian/sealed-credential/rehearsal row in `ledgers/decision_log.md`; unchanged since 3623d2e |

## Per-finding detail

### ACM-P2-001 — Shared client-VPN enrollment token still live; per-device lifecycle unused — partially-fixed

Live token structure (2026-10-14, read-only): `/srv/falcon/secrets/vpn_enroll.token` = 1 line, 49 bytes, `fields=1` (bare shared token; value never read), mode 0600 root:root, mtime 2026-09-28 02:10Z — unchanged since the audit. `/srv/falcon/secrets/wireguard/clients/` is empty (0 per-device `.enroll-token` files, 0 bindings). The closure check still has no bare/shared-token or expiry test — §5 (`enrollment_closure_check.sh:84-93`) only asserts deployed-vs-repo equality (the SEC-P2-004 fix). The decision log records the issuance for the three live client peers (samsung, desktop-mi54lft, desktop-h3addu8) as "prepared … **NOT activated**" (`ledgers/decision_log.md:271`, 2026-10-11T18:12Z), and no later enroll-related decision row exists (grep of 2026-10-13/14 entries: none). The remediation mechanism itself is live and enforced (per-device `<name>:<token>:<expiry>` with 403 on expiry — verified under SEC-P2-004), so the finding is partially fixed: only the owner-gated issuance/rotation + the closure-check bare-token test remain.

### ACM-P2-003 — Deployed enrollment service expiry enforcement (deployed-artifact binding) — verified-fixed

`cmp -s /opt/falcon/vpn-enroll/enroll-service.py automation/vpn/enroll-service.py` matches; sha256 both `cdd4c671d537fe661ac7…` (repo file at `edbf441`). The daily closure timer is active and last ran 2026-10-14 00:00Z; the live textfile `/srv/falcon/textfile/falcon_enrollment_closure.prom` carries `falcon_enrollment_deployed_match 1` and `falcon_enrollment_public_activity 0`. Drift alert rule `falcon-enrollment-deployed-drift` is present (`bootstrap/90-alerting.sh:687-689`). Residuals noted before (version string still `falcon-vpn-enroll/1.1`, no expired-binding pruning tool) are unchanged but not the finding's core.

### ADMIN-P2-001 — Consoles exposed through public routers without origin authentication — open

Loopback origin probes 2026-10-14 (Host-resolved to 127.0.0.1, read-only):
`falcon.mainecybertech.us/` → 302 `https://falcon.mainecybertech.us/login`; `/dash/` → 302 `/dash/app/login`; `/ntop` → 401 `WWW-Authenticate: Basic realm="traefik"` (only origin control); `iris.mainecybertech.us/` → 302 `/dashboard`; `soc.mainecybertech.us/` → 302 `/app/login`. Console routers carry only `sec-headers, public-rate-limit` (`config/traefik/dynamic.yml:89-135`; the live Traefik container bind-mounts this exact file). R-15 is unchanged and still OPEN with the stale mitigation text "ntfy basic auth" (`ledgers/risk_register.md:18`; no commit touched the file in `3623d2e..edbf441`).

### ADMIN-P2-002 — Access-posture gate accepted reachability; no automated enforcement check — partially-fixed

The enforcement gap is closed at `edbf441`: the independent site-host watcher is deployed and passing — read-only SSH 2026-10-14: deployed `/opt/falcon-watcher/watch.sh` sha256 `239d3a4cd222…` == repo, cron `*/5`, log tail `posture ok: https://falcon… -> 302 (Cloudflare Access)`, same for iris/soc, `enroll -> 404`, posture state `ok`, 3199 "posture ok" lines total. The lab-side `external-smoke.yml` (commit `ee4be3f`) is now explicitly reachability-only with a corrected job summary ("iris/soc: reachable (the lab vantage cannot assert Access; the DO watcher does)"); latest run 38446409098 (2026-10-13) succeeded and logs `OK … -> 302 (owner-IP bypass: origin reachable; Access enforcement NOT asserted from this vantage)`. Residual (concrete): `check_token`/the watcher still accept 404 for enroll (`external-smoke.yml:47-54`; watcher `watch.sh:83-86`), so a dead enroll ingress could pass — mitigated in practice today: public `enroll…/health` → 200 proves the ingress+service live.

### ADMIN-P2-003 — No centralized actor-level audit for Grafana/ntfy/IRIS admin actions — partially-fixed

Traefik access-log rotation was added live on 2026-10-12 (`ee4be3f` era; decision log 2026-10-12T20:35Z): `/etc/logrotate.d/falcon-traefik` present (daily, maxsize 50M, rotate 7, copytruncate), and it is working — `/srv/falcon/traefik-logs/access.log` is 128 KB with `.1` (4.6 MB), `.2.gz`, `.3.gz`; the 79.5 MB unrotated file is gone. However the logrotate config is **not codified in the repo** (no logrotate file in the tree; `config/traefik/traefik.yml:30-32` has no `maxSize`), so a rebuild would lose it. Unchanged residuals: no container-log source in the Wazuh agent (live localfiles: journald, audit, active-responses, dpkg + df/netstat/last commands) nor in `config/vector/aggregator.yaml` (live sources: syslog_tcp, edge_ingest, internal_metrics); Grafana OSS/ntfy/IRIS admin actions have no durable central audit. OSD REST audit remains live (central OpenSearch `security-auditlog-2026.10.14` = 262; 2026-10-13 = 10,700 docs) — the only central piece.

### SEC-P2-001 — No origin authentication; ntfy-auth dead config — open

The dead-config half stays closed: `config/traefik/dynamic.yml:26-28` carries only the removal comment, and the live container config (bind-mounted from the repo tree) contains no `ntfy-auth` middleware. The primary issue is unchanged: no origin-side authentication on grafana/dash/iris/soc/enroll (routers at `dynamic.yml:89-135` carry only `sec-headers, public-rate-limit`; only `/ntop` has `falcon-basic-auth`), and a full-tree grep finds no `Cf-Access-Jwt-Assertion`/forwardAuth handling anywhere, so the origin cannot distinguish Access-authenticated from bypassed requests. No relevant commits in `3623d2e..edbf441`.

### SEC-P2-002 — Rate-limit keying fixed; no per-account limits on auth endpoints — open

Fixed part (predates 3623d2e, unchanged): `public-rate-limit` keys on `CF-Connecting-IP` (`dynamic.yml:36-43`; verified in the live container config). Residual unchanged: no login-path-specific middleware, the enrollment service's own limiter collapses to one fleet-wide bucket behind Traefik (documented in `automation/vpn/enroll-service.py:17-19`; `RATE_WINDOW_SECONDS/RATE_MAX` at `:48-52`), and OSD/Wazuh/IRIS still have no per-account lockout. Residual risk is unchanged since 3623d2e, so the finding stays open.

### SEC-P2-004 — Stale deployed enrollment build — verified-fixed

Deployed == repo (see ACM-P2-003 for hashes and the live `falcon_enrollment_deployed_match 1`). The documented issuance flow is enforceable: the deployed service contains the `<name>:<token>:<expiry>` parsing and 403-on-expiry logic (`automation/vpn/enroll-service.py:84-108`). Live ingress/service check: `https://enroll.mainecybertech.us/health` → 200 public and → 200 at the origin (loopback). Closure check §5 asserts the deployed hash; drift alert rule exists. No regression.

### SECRET-P2-001 — Inherited credential estate; vendored scripts source stores wholesale — partially-fixed

Rotation materially advanced since 3623d2e (commit `52a5ccc`, decision log 2026-10-12T23:30Z): register rows 10/13/14/15/16/18/20 marked DONE with capture E-VM101-DECOMMISSION-20260927 (retired systems; dormant credentials), rows 1-2 ROTATED. `check_rotation_register.py` at `edbf441`: `20 items, 9 rotated, 11 pending`, PASS. The 11 pending are the owner-console/host rows (3,4,5,6,7,8,9,11,12,17,19 — DO Spaces, VT, PVE, Security Onion, CF tunnel token, IRIS admin/API, VM 103). The vendored-estate half is unchanged: 23 files under `mct/scripts`+`mct/deploy-scripts` source credential stores wholesale, 20 use `set -a`, and `automation/validation/lib/env_key.sh` is used 0× in `mct/`. Separately, the `f82f82f` hygiene rotation (OPENSEARCH_HEALTHCHECK_PASSWORD + VECTOR_WRITER_PW, capture redacted in place, `ledgers/redactions.md:38`, sweep clean) is recorded but is not one of the 20 register rows.

### SECRET-P2-002 — Owner credential file / validator gate — verified-fixed

Live read-only run at `edbf441` (validator from the clean tree): `owner_env_keys=11 expected=11 mode=0600 duplicates=0 unknown=0 malformed=0 missing=0 result=PASS (warnings=0)`, exit 0. The validator is wired into the gate (`ci/validate.py:670-729`, registered in CHECKS; CI runs `python3 ci/validate.py` at `.github/workflows/validate.yml:121`) and the regression suite runs via `check_shell_tests`. Inventory/doc drift fixed by `1b14231`: `.env.example:22` documents `pi_password`; `OWNER_ENV_INVENTORY.md:50-53` now records 11 keys / PASS (2026-10-13); the validator INVENTORY matches the live key set (11/11). Cosmetic residual only: the `OWNER_ENV_INVENTORY.md` "CI wiring (proposed)" heading (`:56`) is stale wording now that the check is wired.

### ACM-P3-001 — No consolidated access-control matrix — open

No consolidated artifact exists at `edbf441`: a tree-wide find for `*access*matrix*`/`*access_control*` returns only audit-run copies (`docs/audits/...`) and an unrelated evidence capture; the four distributed sources (`PORT_PROTOCOL_MATRIX.md`, `ACCESS_AND_ACCOUNTS.md`, `IDENTITY_AND_SECRETS.md`, `TRUST_BOUNDARIES.md`) are unchanged in `3623d2e..edbf441` and no commit/decision addresses the consolidation.

### ACM-P3-002 — Documented Access policy state vs live behavior — open

Read-only Cloudflare zone API 2026-10-14: `falcon` app `a8bb98c6…` = two identical `allow-mainecybertech.us` policies, **no bypass**; `soc` `adfd5945…` and `iris` `88aec22b…` = `bypass-owner-public-ip` `142.105.190.25/32` + allow-domain; dead apps `falcon-dash` (`e38a7d5b…`) and `falcon-ntfy` (`d4921e2e…`) still exist with allow-domain policies. DNS: `dash.falcon.mainecybertech.us` is still a proxied CNAME to the tunnel (public probe: TLS handshake failure — no route), and `ACCESS_AND_ACCOUNTS.md:126-130` still documents the old state ("Each carries … plus a bypass-owner-public-ip policy"). No change since 3623d2e.

### SEC-P3-004 — wg0 has no peer-class separation — open

Live (2026-10-14): `/etc/nftables.conf` sha256 `91fe36ef…` == repo `config/nftables/falcon.nft`; the live input chain carries the first-match client-peer drop for `10.99.0.20/.21/.22` on tcp 9443/15140/15141 (`falcon.nft:33`) and `wg show wg0 peers` = 8 peers including the 3 client endpoints (AllowedIPs .20/.21/.22). The syslog/NetFlow accepts are still peer-unrestricted (`falcon.nft:36-37`: tcp 514/1514/1515, udp 514/2055 accept for any `iifname "wg0"`), so a client peer can still reach them, and `PORT_PROTOCOL_MATRIX.md:107-111` still states the residual "is resolved at the config level" without the peer-class/syslog caveat.

### SEC-P3-005 — Console session cookies not Secure — verified-fixed

Live at `edbf441`: central OSD container config has `opensearch_security.cookie.secure: true` (bind-mounted from repo `config/central/opensearch_dashboards.yml:5`); Wazuh dashboard has `opensearch_security.cookie.secure: true` (`automation/wazuh/multi-node/config/wazuh_dashboard/opensearch_dashboards.yml:16`); Grafana env `GF_SECURITY_COOKIE_SECURE=true` (`compose/central/docker-compose.yml:210`). Repo codification and live state agree; no regression.

### SECRET-P3-001 — Register/live-store paths stale for IRIS and the MCT stack — open

Register rows 13 and 18 now name the consolidated `/srv/falcon/secrets/mct.env` (and were marked DONE in `52a5ccc`), but row 19 still reads only "IRIS `.env`" (`CREDENTIAL_ROTATION_REGISTER.md:38`), and the vendored checklist rows 13/16/18/19/20 still name `/opt/mct-security-stack/.env` / `.../iris-web/.env` (`mct/runbooks/credential-rotation-checklist.md:42-49`; file unchanged in the range). Live `rotation_status.py --live` (sudo, read-only): the old paths are absent; `/srv/falcon/secrets/mct.env` and `/srv/falcon/secrets/iris-web.env` are present (0600, mtime 2026-09-28) — so `--live` verification for the affected rows still cannot be produced from these register/checklist paths.

### SECRET-P3-002 — Break-glass custody procedural only (OD-04 pending) — open

`docs/phase0/OWNER_DECISIONS.json` OD-04 status `PENDING`, value null (`:36`); `docs/security/BREAK_GLASS_CUSTODY.md:5-8` records OD-04 as PENDING and the only emergency path today is root via sudo with the value in `/home/user/.env` / `capture.env` (file-mode only); the custody/tabletop checklist is unchecked and `ledgers/decision_log.md` contains no custodian/sealed-credential/rehearsal row (grep). Unchanged since 3623d2e.

## New findings

none (no new repo defects found while verifying this scope). Two non-finding observations, both already captured as residuals above: (1) the live-only Traefik logrotate config is not codified in the repo (rebuild would lose it — folded into ADMIN-P2-003); (2) `OWNER_ENV_INVENTORY.md:56` still says "CI wiring (proposed)" although the check is wired (cosmetic, folded into SECRET-P2-002).
