# 28_file_upload_download_security_audit — Prompt 28 - File Upload and Download Security Audit

- Run: `falcon-20261011-0416-full-f5cb7c9`
- Target: `falcon` @ `f5cb7c9` (branch `main`)
- Domain: `28_file_upload_download_security_audit.md` (area FILE, prompt)

## Verification Performed

## Audit Metadata

- Audit name: repo-deep-dive
- Run: falcon-20261011-0416-full-f5cb7c9
- Repository: falcon
- Branch: main (origin/main)
- Commit SHA: `f5cb7c96cacefb2e8b1dedc1f15e633d9072264b`
- Generated at: 2026-10-11T04:45:00Z
- Auditor: repo-deep-dive full-domain subagent (read-only; live lab host vantage)
- Area code: FILE
- Output path (intended): docs/audits/repo-deep-dive/falcon-20261011-0416-full-f5cb7c9/28_file_upload_download_security_audit.md
- Determination: **Not applicable as a first-party file upload/download security domain; no findings.** An updated inventory of the file-adjacent surfaces and why each is out of scope or covered elsewhere follows.

## Scope

Reviewed: every first-party HTTP handler in the tree (`automation/vpn/enroll-service.py`, `automation/alerting/ntfy_relay.py`, the test double `automation/validation/tests/ntfy_relay_auth_test.py`), all `*.py`/`*.sh`/`*.yml` first-party code for multipart/presign/signed-URL/attachment/upload/download primitives, the only deployed third-party file surface (DFIR-IRIS case management, `compose/mct/iris-web/`), and the storage/retention of that surface.

Not reviewed / not assessable from this repository: the DFIR-IRIS application source itself (not vendored; digest-pinned images only), the ntfy mobile app, and the owner-side Spaces/R2 bucket contents beyond the repository's own scripts. No upload, download or preview flow exists in first-party code, so MIME/extension/size validation, content-scanning hooks, signed URLs, revocation and CDN/cache items are N/A rather than missing.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `automation/vpn/enroll-service.py:28-29,165-178` | code | the only first-party HTTP service | JSON only: `GET /health`, `POST /enroll` (token/name/pubkey); no multipart, no file body, no download route |
| `automation/alerting/ntfy_relay.py` | code | Grafana webhook receiver | JSON POST body only; publishes text; no file handling |
| `automation/validation/tests/ntfy_relay_auth_test.py` | test | offline HTTP test double | stdlib handler; not deployed |
| grep `multipart|presign|signed[_ -]?url|attachment|send_file|Content-Disposition|upload` over first-party `automation/ bootstrap/ config/ compose/ ci/` | search | proves absence of first-party upload/download code | only ops/backup matches (`export_monitor_metrics.sh` upload-state read, `backup_e2e_test.sh` comment, `build_review_package.sh` comment, `phase4_data_checks.sh` comment) |
| grep `BaseHTTPRequestHandler|http.server|Flask|FastAPI|Django|@app.route` | search | proves there is no web framework / app | only the two stdlib services above |
| `compose/mct/iris-web/docker-compose.yml:18-75`, `docker-compose.base.yml` | deploy | adopted third-party case-management file surface | digest-pinned images (`iriswebapp_app@sha256:d7d23026…`, `db@sha256:081ad194…`, `nginx@sha256:887b1eb8…`); volumes `iris-downloads`, `server_data`, `db_data`, `user_templates` |
| live IRIS volumes + containers | live | current state of the only file store | downloads 4.0K, server_data 20K, db_data 78M, user_templates 4.0K; `iriswebapp_app`/`worker`/`nginx`/`db`/`rabbitmq` up |
| live Cloudflare Access apps + policy | live | public reachability of the IRIS file surface | app `iris.mainecybertech.us` exists; policy `bypass-owner-public-ip` (142.105.190.25/32) + `allow-owner-domain`; `https://iris.mainecybertech.us/` (owner-IP vantage) lands on the IRIS login page, not the Access login |

## Verification Performed

| Check | Command / artifact | Result |
|---|---|---|
| First-party upload/download surface | grep over first-party code (above) | none; only JSON handlers exist |
| First-party HTTP bodies | read `enroll-service.py`, `ntfy_relay.py` | JSON only; no file reads/writes from requests |
| IRIS file volumes live | `docker volume inspect` + `du -sh` | downloads 4.0K / server_data 20K / db_data 78M / user_templates 4.0K - no active case files |
| IRIS images pinned | `compose/mct/iris-web/docker-compose.yml:34,41,47,54` | all four images digest-pinned (in `pins/images.lock` scope per `ci/validate.py`) |
| Public IRIS reachability | `curl -sL https://iris.mainecybertech.us/` | redirects to the IRIS login (`/login`); Cloudflare Access app exists but the lab egress IP is on its bypass policy (documented ADMIN/CHAIN issue, not a file-domain gap) |
| Repo is clean at the audited SHA | `git rev-parse HEAD` in `/home/user/falcon-build` | `f5cb7c9…`; `git status --porcelain` empty (0 dirty files) |

## Executive Summary

The repository still has **no first-party file upload, download, preview, export or signed-URL surface**. It is a self-hosted monitoring lab: two stdlib JSON services, systemd timers, Docker Compose stacks and validation scripts. All file movement in the tree is operational (backups, snapshot repositories, evidence packaging), which is covered by the DR/SEARCH domains, not a user file surface. The only deployed file-handling application is the adopted DFIR-IRIS case manager, whose application code is not in this repository; its repo-side deployment is digest-pinned and its file volumes are effectively empty (a few KB + a 78 MB database). There are no FILE findings; the special checks (public buckets, signed-URL lifetime, SVG/script/PDF risk, cross-tenant file tests) are N/A for first-party code. One observation for the owning domains: the public IRIS route is gated by Cloudflare Access except for the owner egress IP (bypass policy) - the IRIS login is then the only barrier.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Enrollment service | `automation/vpn/enroll-service.py` | issue WireGuard peer configs | JSON API only (`/health`, `/enroll`) | none (file-domain) | token-protected; no file bodies |
| Alert relay | `automation/alerting/ntfy_relay.py` | Grafana webhook -> ntfy | JSON POST only | none (file-domain) | text messages, bounded spool file (ops) |
| IRIS case manager | `compose/mct/iris-web/` | DFIR case store + file uploads/downloads | deployed, digest-pinned; volumes nearly empty | third-party controls not in repo | see NOTIF/SEARCH/ADMIN for exposure/retention |
| Backup/offsite scripts | `bootstrap/80-offsite-backup.sh`, `85-backup-job.sh` | snapshot/config/offsite file movement | operational, covered by DR/SEARCH | n/a | not a user file surface |
| Evidence packaging | `automation/validation/build_review_package.sh`, `pack_fidelity.py` | audit artifact hashing | operational | n/a | not a user file surface |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Upload components | N/A | no first-party upload code | none | none |
| Download endpoints | N/A | no first-party download routes | none | none |
| Document routes | N/A | no document routes | none | none |
| Attachments | N/A | IRIS attachments only, third-party | not repo-assessable | track under IRIS/ADMIN if case files are used |
| Storage buckets | N/A | only R2/Spaces backup buckets (SEARCH/DR) | owner-side lifecycle | see SEARCH |
| Public/private files | N/A | no first-party file store | none | none |
| Signed URLs | N/A | no presign code anywhere | none | none |
| Metadata | N/A | no file metadata model | none | none |
| MIME/extension/size validation | N/A | no upload path | none | none |
| Content scanning hooks | N/A | no upload path | none | none |
| Image/PDF/document previews | N/A | none | none | none |
| Exports | N/A | no user export feature | none | none |

## Findings

None. The domain is not applicable as a first-party file surface at this commit.

## Prior-Run Comparison (falcon-20261009-2117-full-08e20d1)

- The prior run reached the same determination (no findings, evidenced N/A). Re-verified at `f5cb7c9`: same handler set (no new HTTP/file code landed in #49-#54), IRIS deployment unchanged (digest pins identical), IRIS file volumes still nearly empty.
- No prior FILE finding IDs exist to reconcile.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| IRIS case-file handling (third-party) is not covered by repo controls (MIME/size/AV) | Low (file domain) | Low while volumes are empty | case-data handling risk if IRIS is used for real cases | `compose/mct/iris-web/docker-compose.yml`; live volume sizes | owner decision: document IRIS upload policy when case files are introduced |

## Recommendations

### Immediate / Release Blocking
None.

### This Week
None.

### This Month
- If IRIS is to hold real case files, record an owner decision on upload policy (size/MIME/AV scanning, retention) in `docs/privacy/DATA_GOVERNANCE.md`/`docs/runbooks/`.

### Later / Platform Evolution
- Keep the "no first-party file surface" property explicit in `REPOSITORY.md` so future audits can re-verify quickly.

## Suggested Tests

- A CI guard test asserting that any new first-party HTTP handler accepting a file body (multipart/content-disposition) must ship with validation tests (cheap grep-level guard).

## Suggested Documentation Updates

- Optional: add a one-line "file surfaces" note to `REPOSITORY.md` pointing at IRIS as the only third-party file surface.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Will IRIS be used for real case files (currently empty volumes)? | determines whether upload validation/retention become real requirements | owner statement; IRIS config/usage |

## Limitations

- IRIS application internals (upload validation, storage ACLs) are not in the repository and were not assessed; only the deployment (images, volumes, exposure) was.
- No upload/download request was exercised against any live endpoint (read-only audit; there is no first-party endpoint to exercise).

## Findings

_No findings in this domain._
