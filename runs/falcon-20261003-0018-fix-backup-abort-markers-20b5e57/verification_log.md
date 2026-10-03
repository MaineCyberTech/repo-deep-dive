# Verification log

| When | Patch set | State | Finding status | Evidence | Note |
|---|---|---|---|---|---|
| 2026-10-03T05:52:31Z | PATCH-4 | open | partially-fixed | ee883646a6cb9b08b14d24bbcb72f185150de959 | independent heartbeat publish + scrape-absence rule; scrape additions already on main 65e18f1 |
| 2026-10-03T05:58:09Z | PATCH-6 | open | partially-fixed | c8c86d14fd016959125a0dc0835b68a06b1f1a79 | digest+closeout rebound to 8e4c20c; CI publication-equality gate added; verify_publication_chain.sh exit 0 |
| 2026-10-03T06:04:47Z | PATCH-4 | open | partially-fixed | https://github.com/MaineCyberTech/falcon/pull/14 |  |
| 2026-10-03T06:04:47Z | PATCH-6 | open | partially-fixed | https://github.com/MaineCyberTech/falcon/pull/15 |  |
| 2026-10-03T06:06:15Z | PATCH-4 | open | partially-fixed | https://github.com/MaineCyberTech/falcon/pull/14 |  |
| 2026-10-03T06:06:15Z | PATCH-6 | open | partially-fixed | https://github.com/MaineCyberTech/falcon/pull/15 |  |
| 2026-10-03T06:26:40Z | PATCH-8 | open | partially-fixed | https://github.com/MaineCyberTech/falcon/pull/16 |  |
| 2026-10-03T11:45:45Z | PATCH-5 | open | partially-fixed | 5c6c537857a6d0de7ec2b58a26356c72dad0d284 https://github.com/MaineCyberTech/falcon/pull/17 |  |
| 2026-10-03T11:58:33Z | PATCH-1 | open | partially-fixed | 7a67d906de819e80a49f890dce693ecd595f8920 https://github.com/MaineCyberTech/falcon/pull/18 |  |
| 2026-10-03T12:03:45Z | PATCH-7 | closed | still-open |  | BLOCKED: owner retention decision required (OWNER_ACTIONS C1; no default for IRIS; Wazuh indexer is a separate cluster). No PR opened - a guessed window would be unverifiable/no-op. See remediation/PATCH-7/blocked.md. |
| 2026-10-03T12:14:00Z | PATCH-2 | open | partially-fixed | 38c18ef75ab115a5e6bce550bec49f2bb11bfa47 https://github.com/MaineCyberTech/falcon/pull/19 |  |
| 2026-10-03T12:26:33Z | PATCH-3 | open | partially-fixed | 2e049a94d5af532c67f452176e88f0f4c90a34ff https://github.com/MaineCyberTech/falcon/pull/20 |  |
| 2026-10-03T14:23:46Z | PS-U01 | open | partially-fixed | c04c0068c182b7d61521978f154f5ac33ae42c2a https://github.com/MaineCyberTech/falcon/pull/21 | API-P2-001 fixed (token expiry, 18/18 offline tests, validate.py 0); API-P1-001/API-P2-002 deferred (edge session/PKI) - see PR body |
| 2026-10-03T14:38:06Z | PS-U02 | open | partially-fixed | 41cd5a1e65e22f7ef1e957605bb0f0df2755328d https://github.com/MaineCyberTech/falcon/pull/22 |  |
| 2026-10-03T14:38:17Z | PS-U02 | open | partially-fixed | 41cd5a1e65e22f7ef1e957605bb0f0df2755328d https://github.com/MaineCyberTech/falcon/pull/22 | ARCH-P2-002 partially fixed (vendored Wazuh flow-relay aligned to locked/SBOM python:3.12-alpine; 4/4 offline checks, validate.py 0); ARCH-P2-002 residual + ARCH-P1-001/ARCH-P2-001/ARCH-P2-003 deferred (SUPPLY-P1-001, ops, edge PKI) - see PR body. |
| 2026-10-03T14:48:34Z | PS-U03 | open | partially-fixed | 375c4fb13d5ff24b2fa1df2d48565e9ec11f2124 https://github.com/MaineCyberTech/falcon/pull/23 | CI-P2-002 partially-fixed (repo-local compensating controls guarded offline; protected-environment residual deferred to owner/plan); CI-P1-001/CI-P2-001/CI-P3-001 verified-fixed at base; CI-P1-002 owner-accepted (plan-gated) |
| 2026-10-03T14:59:21Z | PS-U05 | open | partially-fixed | 4529dbdb966a639a79d46d85c3d32de9ae865925 https://github.com/MaineCyberTech/falcon/pull/24 |  |
| 2026-10-03T15:06:59Z | PS-U07 | open | partially-fixed | a981b7b449ba48bf755ce9e9c0b17f1a94178e28 https://github.com/MaineCyberTech/falcon/pull/25 | PS-U07 catch-all: extended the abort trap to r2_cold_copy.sh and wazuh_indexer_backup.sh (FINAL-P1-001 / ARCH-P2-005); offline abort_marker_test extended; lab ci/validate.py exit 0; gitleaks clean. Retention (DATA-P1-001) deferred to owner decision. |
| 2026-10-03T15:21:01Z | PS-U08 | open | partially-fixed | 3a200c9fe33c51c97a9e348fc5f32c846344a72b https://github.com/MaineCyberTech/falcon/pull/26 | HYG-P1-001/HYG-P2-001 partially-fixed (wired the existing digest-binding + SBOM-hash tooling into ci/validate.py; lab gate exit 0, negative controls fail closed, gitleaks clean); structural removal/rebind deferred to owner/PATCH-6. HYG-P1-002 verified-fixed at base (unchanged). |
| 2026-10-03T15:29:11Z | PS-U10 | open | partially-fixed | aef63addacb79888c0d540257a8b0470115c3102 https://github.com/MaineCyberTech/falcon/pull/27 |  |
| 2026-10-03T15:47:46Z | PS-U13 | open | partially-fixed | ed2f739a05030a860b06f9f4e58b58d054fd28ca https://github.com/MaineCyberTech/falcon/pull/28 | PS-U13 draft PR (ledger provenance guard, --fast subset, offsite backup e2e) |
| 2026-10-03T15:54:55Z | PS-U11 | open | partially-fixed | 1127bf6015f6026c7f930032fe969dbebe320b52 https://github.com/MaineCyberTech/falcon/pull/29 | SEC-P2-002 fixed (token off curl argv via --config -); SEC-P3-001 clarified (forward/output not default-deny; DOCKER-USER is); SEC-P2-001 left open for owner decision on public-router origin auth. |
| 2026-10-03T16:04:25Z | PS-U12 | open | partially-fixed | 5f9cf9a304fba3ecd82dfee951e8d299c9a93f15 https://github.com/MaineCyberTech/falcon/pull/30 |  |
| 2026-10-03T16:15:48Z | PS-U04 | open | partially-fixed | eee84c8ec4a69f5614a7b0b267231a14a1ff65f5 https://github.com/MaineCyberTech/falcon/pull/31 |  |
| 2026-10-03T16:26:20Z | PS-U09 | open | partially-fixed | e31523a59c945126e1b3e1e6ea9e630559292812 https://github.com/MaineCyberTech/falcon/pull/32 |  |
| 2026-10-03T16:33:34Z | PS-U06 | open | partially-fixed | f19acdbbb7670673446fa86df51f0e3374cd3057 https://github.com/MaineCyberTech/falcon/pull/33 |  |
