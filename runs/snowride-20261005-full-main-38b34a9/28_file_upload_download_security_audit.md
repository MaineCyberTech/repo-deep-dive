# 28_file_upload_download_security_audit — Prompt 28 - File Upload and Download Security Audit

- Run: `snowride-20261005-full-main-38b34a9`
- Target: `snowride` @ `38b34a9` (branch `main`)
- Domain: `28_file_upload_download_security_audit.md` (area FILE, prompt)

## Verification Performed

Replay object store reviewed: content-addressed keys, upload read-back checksum verification, per-read download checksum, expiry-bound signed URLs (300s) with policy re-evaluated on every access, and a 4/64 concurrency/queue limiter (replayStore.ts:1-130). Residual: the application does not enforce a maximum replay byte size; it relies on the storage/RPC path and the bucket policy.

## Findings

| ID | Severity | Title |
|---|---|---|
| FILE-P3-001 | P3 | No application-layer maximum replay size bound |
