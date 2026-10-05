# Deterministic checks — deterministic

Machine checks (no LLM). Findings use the `DET` area.

## Findings

| ID | Title | Severity |
|---|---|---|
| DET-P2-001 | [PORT] 20 evidence/ files committed with mixed line endings | P2 |
| DET-P3-001 | [SUPPLY] 2 container images without a digest pin | P3 |

## Detail

### Finding ID: DET-P2-001 - [PORT] 20 evidence/ files committed with mixed line endings



- `python3 tools/deterministic_checks.py /var/lib/lab-repos/snowride`
- `.gitattributes: `evidence/** -text` (byte-exact, hash-pinned)`
- `git ls-files --eol | grep '^i/crlf' -> 1 file; i/mixed -> 20`

### Finding ID: DET-P3-001 - [SUPPLY] 2 container images without a digest pin



- `infra/compose/docker-compose.yml:12 image: snowride-web:certified`
- `infra/compose/docker-compose.yml:78 image: snowride-realtime:certified`
