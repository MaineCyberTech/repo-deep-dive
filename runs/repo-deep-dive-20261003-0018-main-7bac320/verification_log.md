# Verification log

| When | Patch set | State | Finding status | Evidence | Note |
|---|---|---|---|---|---|
| 2026-10-03T12:39:56Z | PS-002 | open | partially-fixed | 979777da9e758ed595b81c8c236201882994dd07 https://github.com/MaineCyberTech/repo-deep-dive/pull/1 |  |
| 2026-10-03T14:01:10Z | PS-003 | open | partially-fixed | e03c1168a4fb99e1f6ab49fa0d9f224d82150e31 https://github.com/MaineCyberTech/repo-deep-dive/pull/2 |  |
| 2026-10-03T14:23:09Z | PS-009 | open | partially-fixed | c7f59f8c375b9bf649ce6b452352ede37fd8a10b https://github.com/MaineCyberTech/repo-deep-dive/pull/4 |  |
| 2026-10-03T14:41:56Z | PS-006 | open | partially-fixed | 20f7a3d47f6f1dc4ecf8e2f9d5dae1d35cffec8c https://github.com/MaineCyberTech/repo-deep-dive/pull/6 |  |
| 2026-10-03T14:53:03Z | PS-007 | open | partially-fixed | c661a6c8d71381345cf0662183fbba453f229fe3 https://github.com/MaineCyberTech/repo-deep-dive/pull/7 |  |
| 2026-10-03T15:05:16Z | PS-008 | open | partially-fixed | 50c3d2407193923cc9acfbfb8c015f6f226e9e98 https://github.com/MaineCyberTech/repo-deep-dive/pull/8 |  |
| 2026-10-03T15:27:29Z | PS-011 | open | partially-fixed | fd9cf670164dba78f5a9fee8635da9c7d95f5725 https://github.com/MaineCyberTech/repo-deep-dive/pull/10 |  |
| 2026-10-03T16:36:09Z | PS-004 | open | partially-fixed | ca641962f156f8320923e555ce1b8374f695b06a https://github.com/MaineCyberTech/repo-deep-dive/pull/3 |  |
| 2026-10-03T16:36:09Z | PS-005 | open | partially-fixed | c07a49a4b1a0001b5d6f38b4b2504d9a1a2c5289 https://github.com/MaineCyberTech/repo-deep-dive/pull/5 |  |
| 2026-10-03T16:36:10Z | PS-010 | open | partially-fixed | bfbb0e005880f28e77892650a548e9817dd78924 https://github.com/MaineCyberTech/repo-deep-dive/pull/9 |  |
| 2026-10-04T17:31:36Z | RDD-SUPPLY-REPIN | open | regressed | 7893e39 https://github.com/MaineCyberTech/repo-deep-dive/pull/39 | SUPPLY-P1-001 regression (PR #33/#35). Every external `uses:` in `.github/workflows/*.yml` + `ci/audit.yml` re-pinned to full commit SHAs; see docs/SUPPLY_CHAIN.md. |
