# 28_file_upload_download_security_audit — Prompt 28 - File Upload and Download Security Audit

- Run: `buddy-20261005-full-master-adcf767`
- Target: `buddy` @ `adcf767` (branch `master`)
- Domain: `28_file_upload_download_security_audit.md` (area FILE, prompt)

## Verification Performed

No file upload/download. The only file-like feature is save export/import (`lib/storage/indexeddb.ts`): import is size-limited (MAX_IMPORT_LENGTH = 1,000,000 chars), JSON-parsed, and fully validated via `validateSave` before use. The export direction has a Unicode bug, filed here as FILE-P2-001.

## Findings

| ID | Severity | Title |
|---|---|---|
| FILE-P2-001 | P2 | Save export uses btoa and can throw on non-Latin-1 content |
