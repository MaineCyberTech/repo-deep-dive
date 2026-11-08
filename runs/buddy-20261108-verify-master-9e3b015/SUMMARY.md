# Buddy verify summary — master@9e3b015 (2026-11-08)

Re-verification of the Oct 5 audit's actionable findings plus new issues in touched areas.

## Counts

| Status | Count |
|---|---:|
| verified-fixed | 2 |
| partially-fixed | 0 |
| open | 47 |
| regressed | 1 |
| owner-accepted | 1 |
| **total** | **51** |

## P1

- **ARCH-P1-001** (owner-accepted) — Client is fully authoritative: no server trust boundary exists
- **BP-P1-001** (open) — master is unprotected: no required PR, review, or status checks
- **BP-P1-002** (open) — The `release` environment required by release.yml does not exist
- **CI-P1-001** (regressed) — CI is failing on master at the audited commit
- **SC-P1-001** (open) — Next.js 15.5.27 carries a critical RCE advisory and a high DoS advisory

## New findings

