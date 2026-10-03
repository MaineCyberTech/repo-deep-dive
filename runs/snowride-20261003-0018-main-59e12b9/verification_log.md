# Verification log

| When | Patch set | State | Finding status | Evidence | Note |
|---|---|---|---|---|---|
| 2026-10-03T06:50:16Z | P1-1 | open | partially-fixed | 5f4ee0bec7f431eec904ee112d6a136cd6c6d5ab | Draft PR #7; de-hardcoded release identity + crypto-attested owner signature; verify.log clean worktree 5f4ee0b |
| 2026-10-03T06:51:02Z | P1-1 | open | partially-fixed | 5f4ee0bec7f431eec904ee112d6a136cd6c6d5ab |  |
| 2026-10-03T07:01:20Z | P1-2 | open | partially-fixed | 54c60700ef0cf5daf9d6069f059025497bfd4d50 |  |
| 2026-10-03T07:01:33Z | P1-2 | open | partially-fixed | 54c60700ef0cf5daf9d6069f059025497bfd4d50 | Draft PR #8: branch protection declared as code + consistency test in foundation; live GitHub protection remains operator action (token lacks administration:read) |
| 2026-10-03T07:16:29Z | P1-3 | open | partially-fixed | d61c968a1a5166b65204abbe6bf62559bcd9cd1c | Draft PR #9: generate CycloneDX SBOM in foundation + upload commit-bound artifact (sbom-<sha>); actions pinned to SHAs; verify.log clean LF worktree d61c968 |
| 2026-10-03T07:25:35Z | P1-4 | open | partially-fixed | 030d22511a87af1345ca39089d244c4e85ae1d30 | incident runbook documents signals/thresholds/escalation/rollback/drill; committed schedule still open |
| 2026-10-03T07:45:42Z | PS-U01 | open | partially-fixed | e656a3b42fd0b7e5cbb312a4442479624685d7b2 |  |
| 2026-10-03T07:56:00Z | PS-U02 | open | partially-fixed | 4360dbfe2b23eb95dcfa789181573997d76141a7 |  |
| 2026-10-03T08:09:14Z | PS-U03 | open | partially-fixed | cfd5d00adc9f3c01db21640c891edf7256a12f5a |  |
| 2026-10-03T08:25:08Z | PS-U04 | open | partially-fixed | dcdceca659ac8ecfce6eed5a80d6ea58fbf8d13 | remediation PS-U04 draft PR #14 at dcdceca; DB suites + manifest verified on ci-runner |
| 2026-10-03T08:32:18Z | PS-U05 | open | partially-fixed | 3e9e56c273160ef9a3d63259d7052e57635e8caf | remediation PS-U05 draft PR #15 at 3e9e56c: in-repo release-gate record (docs/RELEASE_GATE.md) makes the conditional gate + blocking conditions explicit; verified-fixed gated on P1-1..P1-4 + fresh attestation |
| 2026-10-03T08:40:11Z | PS-U06 | open | partially-fixed | 97211d66cc3ccde3cfb4df0539808d0d6d833d66 | PS-U06 draft PR #16 open |
| 2026-10-03T08:46:10Z | PS-U07 | open | partially-fixed | 6fa559685cd1e9a20508f3cce4f3b345a24a0088 | PS-U07 draft PR #17: versioned reliability controls + RPO/RTO + per-release backup/alert/rollback drills (docs/runbooks/RELIABILITY_DRILLS.md); verified-fixed gated on captured drill evidence at the released commit and the OBS-P1-001 committed schedule |
| 2026-10-03T09:07:51Z | PS-U08 | open | partially-fixed | dcea60b19dac6a3f98c145a68ba74e13361a3526 | PS-U08 catch-all: backup runbook, .gitattributes, CHANGELOG, repomix gitignore; HYG-P2-001 deferred |
| 2026-10-03T09:18:55Z | PS-U09 | open | partially-fixed | 8f369a62f019bf8a0527908e9e61307f931fa6e9 https://github.com/MaineCyberTech/snowride/pull/19 |  |
| 2026-10-03T09:39:01Z | PS-U10 | open | partially-fixed | 7c61d27cea59c1b5e5004fb1f14172d1e76e8e32 https://github.com/MaineCyberTech/snowride/pull/20 |  |
| 2026-10-03T09:54:07Z | PS-U11 | open | partially-fixed | 559170d011b0f11a6be3566760c320043e7f53e9 https://github.com/MaineCyberTech/snowride/pull/21 |  |
| 2026-10-03T10:08:37Z | PS-U12 | open | partially-fixed | b1c0f21781607084626789ba95d587444de83b64 https://github.com/MaineCyberTech/snowride/pull/22 | license enforcement merge-gating (verified with negative probe); audit/signature/dependabot partial with recorded open questions |
| 2026-10-03T10:22:39Z | PS-U13 | open | partially-fixed | a7fb4a6270774ad588f68184fa4a21cd5d61565c https://github.com/MaineCyberTech/snowride/pull/23 | coverage thresholds+artifact, firefox/webkit projects, test:unit fix, verify-all format:check; TEST-P2-003 xref PS-U04 #14 |
