# 31_search_indexing_privacy_audit — Prompt 31 - Search, Indexing, and Privacy Audit

- Run: `mainecybertech-20261004-full-main-9c0b88c`
- Target: `mainecybertech` @ `9c0b88c` (branch `main`)
- Domain: `31_search_indexing_privacy_audit.md` (area SEARCH, prompt)

## Verification Performed

Reconciliation full-domain pass at main `9c0b88c` (2026-10-04). Baseline findings were carried from the repository's committed audit corpus and re-bound to this run: the `a97425d` verification ledger (ancestor of main, so its verified-fixed statuses hold here), the `178b91c` main-tip focused run, and the `20261002-0344` full run for domains the later ledgers did not cover. Each row cites its provenance. Machine deterministic checks are recorded in `lens_deterministic.md`.

## Findings

| ID | Severity | Title |
|---|---|---|
| SEARCH-P1-001 | P1 | `sanitizeSearchTerm` does not strip PostgREST `.` operator separators |
| SEARCH-P1-002 | P1 | Admin global search exposes profile PII and never tenant-scopes the organizations query |
| SEARCH-P2-001 | P2 | Raw search terms persisted in plaintext `audit_logs.metadata` |
| SEARCH-P2-002 | P2 | Portal search omits documents despite SDK and documentation contract |
| SEARCH-P2-003 | P2 | Admin search UI silently discards the documents result set |
| SEARCH-P2-004 | P2 | No search pagination or result counts; hard 5-result ceiling |
| SEARCH-P2-005 | P2 | Search query analytics metric is dead and the analytics summary RPC is missing |
| SEARCH-P2-006 | P2 | Prefix/wildcard mismatch: no btree on prefix columns and no full-text (`tsvector`) search |
| SEARCH-P2-007 | P2 | Typeahead calls full search endpoints without rate limiting or a dedicated autocomplete surface |
| SEARCH-P3-001 | P3 | Soft-delete columns are defined but never used by queries or deletes |
| SEARCH-P3-002 | P3 | Search module documentation is stale relative to the code |
