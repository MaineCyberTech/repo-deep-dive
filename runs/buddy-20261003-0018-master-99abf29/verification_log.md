# Verification log

| When | Patch set | State | Finding status | Evidence | Note |
|---|---|---|---|---|---|
| 2026-10-03T06:26:57Z | PS-04 | open | partially-fixed | ec824fcd696ec5d4018862b0ef8dfd165f3a1a3f | draft PR opened by remediation runner |
| 2026-10-03T06:42:05Z | PS-01 | draft | partially-fixed | 2d9cb592d95c025cddf60d42010ea6ebf1dda98a | CI gate + Dependabot + CODEOWNERS + coverage thresholds; draft PR #3 awaiting human review |
| 2026-10-03T06:42:45Z | PS-01 | open | partially-fixed | 2d9cb592d95c025cddf60d42010ea6ebf1dda98a |  |
| 2026-10-03T06:49:49Z | PS-03 | open | partially-fixed | 96c3e6650dc345dd699c6e5825fa9505810c0cb3 |  |
| 2026-10-03T07:07:03Z | PS-06 | open | partially-fixed | 25149bb33e65634820179eac3ca4f9c2ce956e5a | draft PR opened by remediation runner; lab lint/typecheck/test green (124 tests), gitleaks clean |
| 2026-10-03T07:14:47Z | PS-02 | open | partially-fixed | 594dcddb50ca2b6f7b5053e4833e1d324a444250 | draft PR opened by remediation runner; LICENSE all-rights-reserved placeholder + NOTICE + docs provenance; lab lint/test green (109 tests), gitleaks clean; target license is an open question |
| 2026-10-03T07:15:26Z | PS-02 | open | partially-fixed | 594dcddb50ca2b6f7b5053e4833e1d324a444250 |  |
| 2026-10-03T07:20:59Z | PS-U01 | open | partially-fixed | 4c2cc7caee7437fe9a179c7d5b87c6c35a1e0b88 | Documented guest-only client-authoritative trust model + doc test; server trust boundary deferred (future platform work). Draft PR #7. |
| 2026-10-03T07:25:32Z | PS-U02 | open | partially-fixed | 2f04de62b80cecf69e4ad52e06c297bd553044c0 |  |
| 2026-10-03T07:32:23Z | PS-U03 | open | partially-fixed | 50c65a028dcc35a168524e3f69859af999bafef4 |  |
| 2026-10-03T07:36:48Z | PS-05 | open | partially-fixed | 742c3d335ce14826eb6147952899f43e922c7f21 | hygiene + deterministic generation; draft PR #10; lab lint/typecheck/test green (110 tests), gitleaks clean |
| 2026-10-03T07:54:43Z | PS-07 | open | partially-fixed | de0cae1f170e567502cc99ee6509f9f6c68afed9 | draft PR #11; error boundary + build id + self-hosted fonts + security headers + versioned SW cache; lab lint/typecheck/test 112, build, header/gitleaks green; API-P2-001 deferred to PS-08 |
| 2026-10-03T08:02:40Z | PS-08 | open | partially-fixed | f31ebd44f3e616d74013e3702cd4d50bfe43835b | PS-08 supply-chain + inventory hardening; draft PR #12; lab lint/typecheck/test 109 green, CycloneDX SBOM 17 components, gitleaks clean; npm audit non-clean (3 prod advisories) triaged to Dependabot/Next upgrade; API-P2-001 deferred (no server); INV-P2-002 run inventory.json corrected. |
| 2026-10-03T08:09:05Z | PS-09 | open | partially-fixed | ac9b9e9391035270795ec0eda6dcf9c8072024b5 |  |
| 2026-10-03T08:21:23Z | PS-U04 | open | partially-fixed | e1c0555ccb451c3dd006c27ff8b581bc802002e3 | RTL component tests + fake-indexeddb persistence tests; lab npm ci/lint/typecheck/test green (139 tests), gitleaks clean; draft PR awaiting review. |
