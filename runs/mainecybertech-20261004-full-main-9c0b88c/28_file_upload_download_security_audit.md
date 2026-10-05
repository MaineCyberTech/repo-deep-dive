# 28_file_upload_download_security_audit — Prompt 28 - File Upload and Download Security Audit

- Run: `mainecybertech-20261004-full-main-9c0b88c`
- Target: `mainecybertech` @ `9c0b88c` (branch `main`)
- Domain: `28_file_upload_download_security_audit.md` (area FILE, prompt)

## Verification Performed

Reconciliation full-domain pass at main `9c0b88c` (2026-10-04). Baseline findings were carried from the repository's committed audit corpus and re-bound to this run: the `a97425d` verification ledger (ancestor of main, so its verified-fixed statuses hold here), the `178b91c` main-tip focused run, and the `20261002-0344` full run for domains the later ledgers did not cover. Each row cites its provenance. Machine deterministic checks are recorded in `lens_deterministic.md`.

## Findings

| ID | Severity | Title |
|---|---|---|
| FILE-P1-001 | P1 | Public file-request upload is permission-gated and unreachable for anonymous uploaders |
| FILE-P1-002 | P1 | File-request uploads have no tenant-scoped path and no download path; orphan cleanup will delete them |
| FILE-P1-003 | P1 | Document version history objects are deleted at replace and by orphan cleanup |
| FILE-P2-001 | P2 | `avatars` bucket is used by code but declared nowhere with no storage RLS policy |
| FILE-P2-002 | P2 | Free-form `storageBucket`/`storagePath` on create/update allows signing arbitrary in-bucket objects |
| FILE-P2-003 | P2 | No content/AV scanning and no bucket-level MIME/size limits on the documents bucket |
| FILE-P2-004 | P2 | No backup or restore path for uploaded objects (durability for files) |
| FILE-P2-005 | P2 | Content sniffing does not cover Office, archive, text/JSON, or polyglot payloads |
| FILE-P2-006 | P2 | CSV exports do not neutralize formula injection and default to all rows when `organization_id` is omitted |
| FILE-P3-001 | P3 | Share endpoint has no per-token rate limit |
| FILE-P3-002 | P3 | Client logo accept list still advertises SVG that the server rejects |
| FILE-P3-003 | P3 | Documentation drift on file types and size limits; no documents/upload runbook |
