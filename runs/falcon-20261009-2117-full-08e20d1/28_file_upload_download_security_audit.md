# 28_file_upload_download_security_audit — Prompt 28 - File Upload and Download Security Audit

- Run: `falcon-20261009-2117-full-08e20d1`
- Target: `falcon` @ `08e20d1` (branch `main`)
- Domain: `28_file_upload_download_security_audit.md` (area FILE, prompt)

## Verification Performed

## Audit Metadata

- Audit name: repo-deep-dive
- Run: falcon-20261009-2117-full-08e20d1
- Repository: falcon
- Branch: main (origin/main)
- Commit SHA: `08e20d1a77900dcc0c0a8a3fd16ae8d203d9d65d`
- Generated at: 2026-10-09T21:43:44Z
- Auditor: repo-deep-dive full-domain subagent (read-only, no mutation)
- Area code: FILE
- Determination: **Not applicable as a first-party file upload/download security domain; no findings.** A full inventory of file-adjacent surfaces and why each is out of scope or covered elsewhere is below.

## Scope

The prompt asks for upload components, download endpoints, document routes, attachments, storage buckets, public/private files, signed URLs, metadata, MIME/extension/size validation, content scanning hooks, previews, exports, tenant scoping, revocation, deletion/versioning, audit logs, retention, CDN/cache, and tests. This repository is a self-hosted network-monitoring lab (Docker Compose + bootstrap/validation scripts + docs); it contains **no first-party application with a user file surface**. The audit therefore (a) proves the absence of first-party upload/download code, (b) inventories the file-adjacent surfaces that do exist, and (c) states which of the prompt's special checks are genuinely N/A versus tracked under other domains.

## Evidence Reviewed

| Surface | Evidence | Why it is not a first-party file surface |
|---|---|---|
| HTTP handlers in the repo | `automation/vpn/enroll-service.py` (JSON API: GET /health, POST /enroll), `automation/alerting/ntfy_relay.py` (webhook receiver) | neither accepts multipart/file bodies; no download routes; no static file serving |
| Web frameworks | grep for Flask/Django/FastAPI/`@app.route`/multipart handlers across `*.py` | only the two stdlib `BaseHTTPRequestHandler` services above; no web app |
| Signed URLs / presign | grep for `presign`, `signed[_ -]?url`, `upload`, `attachment`, `multipart` | only backup/ops scripts match (`80-offsite-backup.sh`, `85-backup-job.sh`, `r2_cold_copy.sh`, `build_review_package.sh`); no user-facing URL signing |
| ntfy file attachments | `config/ntfy/server.yml` (no `attachment-cache-dir`); live container config identical | attachments are disabled by config; ntfy exposes no file endpoint |
| DFIR-IRIS case management | `compose/mct/iris-web/docker-compose.yml` + `docker-compose.base.yml` (digest-pinned images, `iris-downloads` volume, nginx on 127.0.0.1) | third-party app (ghcr.io/dfir-iris); its upload/download validation code is **not in this repo**; deployment-level review only (public route Access-gated; store retention gap tracked under SEARCH/DATA) |
| Offsite backup uploads | `bootstrap/80-offsite-backup.sh` (rclone, `--s3-no-check-bucket`, delta upload-state, size verification, fail-closed inventory), `automation/validation/r2_cold_copy.sh` | internal machine-to-machine transfers, not user file upload/download; credentials read from `/srv/falcon/secrets`, never argv/logged |
| Review-package delivery | `automation/validation/build_review_package.sh`, `verify_delivery.sh`, `PACKAGE_MANIFEST.sha256` | artifact build/integrity (SHA-256 manifest verification), not a runtime file service |
| Wazuh indexer snapshots | `bootstrap/86-wazuh-indexer-backup.sh`, `automation/validation/wazuh_indexer_backup.sh` | internal snapshot-to-S3 path |
| Exports | `automation/validation/export_monitor_metrics.sh` (textfile metrics), `docs/audits/...` artifacts | metrics/text artifacts, not downloadable user documents |

## Verification Performed

| Check | Command / artifact | Result |
|---|---|---|
| First-party upload/download code | `grep -rliE '\b(upload|multipart|attachment|signed[_ -]?url|presign)'` over code/config (excluding vendored/mct reporting) | no application file handlers; only backup/ops scripts |
| HTTP services accept files | read `enroll-service.py`, `ntfy_relay.py` | JSON bodies only; no multipart, no file writes from requests (enroll writes `wg0.conf`, relay writes a bounded spool of JSON payloads) |
| ntfy attachments disabled | `config/ntfy/server.yml` + live `docker exec falcon-central-ntfy-1 cat /etc/ntfy/server.yml` | no `attachment-cache-dir`; identical files |
| IRIS public exposure | `curl https://iris.mainecybertech.us` | 302 -> Cloudflare Access (gated); nginx bound to 127.0.0.1 in the repo compose |
| IRIS store | live `docker volume inspect` + `du` | `iris-web_iris-downloads` 4 KiB, `server_data` 20 KiB, DB 78 MiB; no retention policy (RETENTION_MATRIX.md:43, tracked as a data-retention gap) |
| Backup upload controls | read `80-offsite-backup.sh` (S3 key least privilege, delta state, full size verification) | fail-closed, verified; no placeholder uploads |
| Delivery integrity | `verify_delivery.sh` (manifest `sha256sum -c` before archiving) | SHA-256 manifest verification is the file-integrity control |

## Executive Summary

There is no first-party file upload, download, preview, attachment, or signed-URL surface in this repository, so the domain's special checks (public buckets for private data, signed URL lifetime, SVG/script/PDF risks, cross-tenant file tests, MIME/extension/size validation, content scanning hooks) are not applicable to first-party code. The file-adjacent surfaces that do exist are (1) the third-party DFIR-IRIS case application, whose upload/download code lives outside this repo - the deployment is digest-pinned in `compose/mct/iris-web/`, its nginx binds to loopback, and its public route is Cloudflare Access-gated; its store has no retention (tracked under the SEARCH retention finding and the DATA owner backlog); (2) internal backup/offsite transfers, which are authenticated, fail-closed, and size-verified; (3) the review-package build/verify chain, which uses SHA-256 manifests; and (4) ntfy, whose file attachments are disabled. The prior run reached the same N/A determination; nothing at `08e20d1` changes it. No findings are emitted.

## Findings

_No findings in this domain._ The adjacent issues that surfaced during this review are tracked under their owning domains: IRIS store retention (SEARCH-P2-001 / DATA owner backlog), live-vs-pinned IRIS images (`ghcr.io/dfir-iris/iriswebapp_app:latest` running vs digest pins in the repo - container/supply-chain domains).

## Prior-Run Comparison (falcon-20261005-full-main-e267ce1)

- Prior `28_file_upload_download_security_audit` was also N/A with zero findings ("no user-facing file upload/download surface; evidence artifacts are captured by trusted tooling"). This run re-verified the determination with a broader inventory (including IRIS and the backup/review chains) and keeps findings empty.
- No prior FILE finding IDs exist to reconcile.

## Limitations

- Third-party IRIS upload/download validation (MIME checks, size limits, malware scanning, path traversal) cannot be audited from this repository because the application source is not included; only the deployment configuration and store were reviewed. A separate IRIS-image review would be required.
- The live IRIS deployment at `/opt/iris-web` is outside the repo and currently runs floating `latest` tags; that drift is noted for the container/supply-chain domains rather than audited here.
- Backup destination lifecycle (Spaces/R2 bucket policies, object-lock, CDN/cache behavior) is owner-side and was not exercised; repo-side upload integrity controls were reviewed statically.

## Findings

_No findings in this domain._
