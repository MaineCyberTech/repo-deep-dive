# 28_file_upload_download_security_audit — Prompt 28 - File Upload and Download Security Audit

- Run: `bench-test-20261013-0819-full-main-b916709`
- Target: `bench-test` @ `b916709` (branch `main`)
- Domain: `28_file_upload_download_security_audit.md` (area FILE, prompt)

## Verification Performed

# 28_file_upload_download_security_audit - 28_file_upload_download_security_audit.md

Domain subagent `28_file_upload_download_security_audit` (area FILE), read-only audit of `C:\temp\bench-test`.

## Checks / Evidence

- **P2 - iso_fetch reports ok:true and acks "done" even when the ISO checksum is missing or mismatched** (confidence: High)
  - `bench/benchreport.py:1762 - `ok = (want is None) or (want == got)`: a SHA256SUMS file that contains no `*.iso` line leaves `want` as None, which is scored as a pass (falsely `verified: True`), even though nothing was verified.`
  - `bench/benchreport.py:1765 - iso_fetch always returns `"ok": True` whenever the download itself did not throw, including the case where the sums check produced `verified: False`.`
  - `bench/agent.py:315 - `self.rep.ack(cid, "done" if res.get("ok") else "failed", res)`: because `ok` stays True on a checksum mismatch, the operator-facing command is reported DONE while the image is actually unverified.`
  - `tests/test_update.py:200-202 - the suite only asserts `verified is False` for a mismatch and never asserts `ok` is False; there is no test for a SHA256SUMS asset whose lines do not name the ISO.`
  - `bench/benchreport.py:1752-1764 - when the release has no SHA256SUMS asset at all, `ok` stays None (unverified) yet the return value at :1765 is still `"ok": True`.`
  - Impact: The only integrity gate on a multi-GB ISO download is advisory instead of enforced. After a tampered or truncated release asset, or a SHA256SUMS format the parser does not understand, the runner still reports success, so an operator may flash an unverified image to a live USB. A false `verified: True` claim is worse than no check because it invites misplaced trust.
  - Recommendation: Make verification strict and fail closed: if SHA256SUMS is present but has no matching `.iso` line, set `verified=False`; if `verified` is not exactly True, return `ok: False` (or `status: "unverified"`) so the agent acks the command `failed`. Also compare every `.iso` sum, not just the last matching line. Add tests for (a) missing ISO line, (b) missing SHA256SUMS asset, (c) mismatch -> command acks failed.
- **P2 - Artifact upload has no MIME/extension/size validation, no content-scanning hook, and no per-run quota** (confidence: High)
  - `server/benchd.py:1131-1142 - `POST /api/v1/runs/<id>/artifact` accepts an arbitrary `name` string, an arbitrary `kind`, and base64 `content`, and inserts it into the `artifacts` table with no validation of type, extension, or content.`
  - `server/benchd.py:55 - the only size limit is the whole-request `MAX_BODY = 24 * 1024 * 1024`; nothing caps the per-artifact size beyond that or the number/total bytes of artifacts per run.`
  - `server/benchd.py:1140-1141 - `len(raw)` and `b.get("sha256")` are stored as-is; there is no scanner/AV hook and no allowlist for the crafted `name`.`
  - `server/benchd.py:905-906 - on download the Content-Type is a whitelist (`json`/`text`, else `application/octet-stream`), which is a genuine mitigation: an uploaded blob cannot be served back as HTML/SVG.`
  - Impact: Any holder of a runner key (scoped to its own run) or the shared operator token can persist arbitrary binary blobs into the server's SQLite database with no scanning and no quota. Repeated 24 MiB uploads can exhaust the control plane's disk and bloat the database, and there is no place to plug in content inspection if untrusted files are ever accepted.
  - Recommendation: Validate uploads: allowlist `kind`/extensions (json/text/png/csv), enforce a smaller per-artifact and per-run byte/count quota with a clear 413, reject invalid base64 instead of storing it, and document that no malware scanning is performed (or add a pluggable scan hook that blocks on a positive result).
- **P2 - All file downloads are authorized by one static shared token carried in the query string, with no expiry, rotation, or revocation** (confidence: High)
  - `server/benchd.py:572-580 - `_is_operator` accepts `?token=<shared>` in addition to the bearer, and gates every `/api/...` GET that includes artifact and telemetry.csv downloads (server/benchd.py:645-648).`
  - `server/web/app.js:1582-1583 - the dashboard builds download links as `/api/v1/runs/<id>/telemetry.csv?token=...` and `/api/v1/runs/<id>/artifact/<name>?token=...`, putting the shared token in URLs.`
  - `server/benchd.py:1438-1441 - the token is a single process-lifetime value; there is no TTL, rotation, or per-download grant, and if it is unset the plane starts `OPEN (no token)`.`
  - `docs/CONTROL_PLANE.md:204-207 - documents `?token=` for the SSE stream and file downloads at the shared join-token level.`
  - `server/benchd.py:523-524 - logs are scrubbed of `token=`, but the value still reaches browser history, screenshots, and any upstream proxy/Referer.`
  - Impact: There is no time-limited ('signed URL') capability for downloads. A single leaked operator token grants permanent, unrevocable access to every run, artifact, and telemetry export; the token also cannot be rotated for one user without restarting the control plane with a new value for everyone.
  - Recommendation: Issue short-lived, single-purpose download tokens (or short-lived signed links) instead of reusing the shared token in the query string; prefer the `Authorization` header where possible; add `Referrer-Policy: no-referrer` on downloads; support token rotation/revocation and refuse to start in an unauthenticated mode outside loopback.
- **P3 - Artifact metadata sha256 is client-supplied and never recomputed or verified on download** (confidence: High)
  - `server/benchd.py:1140-1141 - the artifact INSERT stores `b.get("sha256")` verbatim alongside `content`; the server never recomputes the digest with `hashlib`.`
  - `server/benchd.py:901-913 - `_artifact_download` base64-decodes `content` and streams it; the stored `sha256` is never compared against the bytes actually served.`
  - `bench/benchreport.py:582-588 - the runner's `artifact()` helper posts only name/kind/content (no sha256).`
  - `server/import_results.py:211-213 - the backfill importer also posts only name/kind/content, so the recorded digest column is effectively unpopulated.`
  - Impact: The artifacts table advertises an integrity field (sha256) that is attacker/caller-controlled and never checked, so a corrupted or tampered artifact is served with no detection, and downstream consumers cannot trust the recorded digest.
  - Recommendation: Compute sha256 server-side on receipt; reject the upload if a client-supplied digest disagrees; return the server-computed digest in the run detail and verify it on download.
- **P3 - No per-artifact deletion, retention, or versioning; artifacts are purged only by deleting the whole run** (confidence: High)
  - `server/benchd.py:126-129 - the `artifacts` schema has no version, expiry, or soft-delete columns.`
  - `server/benchd.py:665-672 - the only delete path is `DELETE /api/v1/runs/<id>`, which drops phases/telemetry/events/artifacts for that run; there is no artifact-level DELETE route in the dispatch (server/benchd.py:653-681).`
  - `docs/CONTROL_PLANE.md:96-97 and :277 - the docs present downloads as read-only and list richer artifact browsing as a future item.`
  - Impact: Sensitive run artifacts are retained indefinitely and cannot be selectively removed or superseded, so a single bad or secret-bearing upload can only be eliminated by destroying the entire run's history; there is no version history to trace which artifact a report used.
  - Recommendation: Add `DELETE /api/v1/runs/<id>/artifact/<name>` (operator-scoped), an optional retention/TTL policy, and a read API that surfaces version/created time; document the retention behavior.
- **P3 - Missing negative/authorization tests for the file surface and wildcard CORS on authenticated downloads** (confidence: High)
  - `tests/test_control_plane.py:190-204 - cross-runner isolation tests cover writes only; none asserts that a runner key cannot GET another run's artifact or telemetry.csv (reads are gated only by operator token in code at server/benchd.py:645).`
  - `tests/test_control_plane.py:161-171,217-225 - artifact coverage is a happy-path round-trip (json + binary); there is no test for an oversized artifact, invalid base64, a hostile `name`/`kind`, or the 24 MiB body cap being enforced at runtime.`
  - `tests/test_control_plane.py:148-152 - the containment and MAX_BODY checks are source-string assertions, not behavioral tests.`
  - `server/benchd.py:533 - every response, including artifact/telemetry downloads, sets `Access-Control-Allow-Origin: *`.`
  - Impact: A future change that widens read access to artifacts, breaks the upload size cap, or lets a runner read another run's files would not be caught by the suite; `ACAO:*` lets any web origin read downloaded data when it can attach a valid token, which widens the blast radius of the query-string token.
  - Recommendation: Add tests that (a) a runner key is denied 403/404 on another run's artifact and telemetry.csv, (b) an over-cap Content-Length is refused before buffering, and (c) invalid base64/hostile names are rejected. Scope `Access-Control-Allow-Origin` to the dashboard origin rather than `*`.

## Verification Performed

Read-only source review of the target at commit `b916709`; the evidence above was
recorded by the domain subagent and normalized by `tools/full_domain.py` (mechanical
report body derived from that recorded findings JSON).

## Findings

| ID | Severity | Title |
|---|---|---|
| FILE-P2-001 | P2 | iso_fetch reports ok:true and acks "done" even when the ISO checksum is missing or mismatched |
| FILE-P2-002 | P2 | Artifact upload has no MIME/extension/size validation, no content-scanning hook, and no per-run quota |
| FILE-P2-003 | P2 | All file downloads are authorized by one static shared token carried in the query string, with no expiry, rotation, or revocation |
| FILE-P3-001 | P3 | Artifact metadata sha256 is client-supplied and never recomputed or verified on download |
| FILE-P3-002 | P3 | No per-artifact deletion, retention, or versioning; artifacts are purged only by deleting the whole run |
| FILE-P3-003 | P3 | Missing negative/authorization tests for the file surface and wildcard CORS on authenticated downloads |
