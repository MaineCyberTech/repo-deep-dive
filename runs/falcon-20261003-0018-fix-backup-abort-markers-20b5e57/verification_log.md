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
