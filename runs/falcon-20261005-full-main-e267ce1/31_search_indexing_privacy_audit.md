# 31_search_indexing_privacy_audit — Prompt 31 - Search, Indexing, and Privacy Audit

- Run: `falcon-20261005-full-main-e267ce1`
- Target: `falcon` @ `e267ce1` (branch `main`)
- Domain: `31_search_indexing_privacy_audit.md` (area SEARCH, prompt)

## Verification Performed

Domain subagent produced 1 finding(s) at the bound commit; machine IDs assigned by tools/full_domain.py.

## Findings

| ID | Severity | Title |
|---|---|---|
| SEARCH-P2-001 | P2 | Search/index retention is enforced only for falcon-eve; Wazuh/IRIS indices grow unbounded |
