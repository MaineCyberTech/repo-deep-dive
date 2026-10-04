# Post-merge verification re-audit queue

Generated: 2026-10-04T05:21:42Z

Procedure: `runbooks/POST_MERGE_REAUDIT.md`. After the remediation PRs merged,
run the machine checks and a verification-mode LLM re-audit per repo.

| Repo | Findings | P0 | P1 | P2 | P3 | PRs merged | Re-audit |
|---|---:|---:|---:|---:|---:|---:|---|
| buddy | 40 | 0 | 11 | 24 | 5 | 13 | [ ] |
| chat | 65 | 1 | 26 | 31 | 7 | 28 | [ ] |
| falcon | 46 | 4 | 20 | 18 | 4 | 20 | [ ] |
| falcon-edge | 43 | 0 | 3 | 27 | 13 | 15 | [ ] |
| mainecybertech | 44 | 1 | 3 | 26 | 14 | 16 | [x] |
| repo-deep-dive | 41 | 0 | 9 | 20 | 12 | 10 | [ ] |
| snowride | 46 | 0 | 6 | 25 | 15 | 17 | [ ] |

Total: 7 repos, 119 PRs.

## Per-repo PR list

### buddy
- [x] https://github.com/MaineCyberTech/buddy/pull/10
- [x] https://github.com/MaineCyberTech/buddy/pull/11
- [x] https://github.com/MaineCyberTech/buddy/pull/12
- [x] https://github.com/MaineCyberTech/buddy/pull/13
- [x] https://github.com/MaineCyberTech/buddy/pull/14
- [x] https://github.com/MaineCyberTech/buddy/pull/2
- [x] https://github.com/MaineCyberTech/buddy/pull/3
- [x] https://github.com/MaineCyberTech/buddy/pull/4
- [x] https://github.com/MaineCyberTech/buddy/pull/5
- [x] https://github.com/MaineCyberTech/buddy/pull/6
- [x] https://github.com/MaineCyberTech/buddy/pull/7
- [x] https://github.com/MaineCyberTech/buddy/pull/8
- [x] https://github.com/MaineCyberTech/buddy/pull/9

### chat
- [x] https://github.com/MaineCyberTech/chat/pull/56
- [x] https://github.com/MaineCyberTech/chat/pull/57
- [x] https://github.com/MaineCyberTech/chat/pull/58
- [x] https://github.com/MaineCyberTech/chat/pull/60
- [x] https://github.com/MaineCyberTech/chat/pull/61
- [x] https://github.com/MaineCyberTech/chat/pull/62
- [x] https://github.com/MaineCyberTech/chat/pull/63
- [x] https://github.com/MaineCyberTech/chat/pull/64
- [x] https://github.com/MaineCyberTech/chat/pull/65
- [x] https://github.com/MaineCyberTech/chat/pull/66
- [x] https://github.com/MaineCyberTech/chat/pull/67
- [x] https://github.com/MaineCyberTech/chat/pull/68
- [x] https://github.com/MaineCyberTech/chat/pull/69
- [x] https://github.com/MaineCyberTech/chat/pull/70
- [x] https://github.com/MaineCyberTech/chat/pull/71
- [x] https://github.com/MaineCyberTech/chat/pull/72
- [x] https://github.com/MaineCyberTech/chat/pull/73
- [x] https://github.com/MaineCyberTech/chat/pull/74
- [x] https://github.com/MaineCyberTech/chat/pull/75
- [x] https://github.com/MaineCyberTech/chat/pull/76
- [x] https://github.com/MaineCyberTech/chat/pull/77
- [x] https://github.com/MaineCyberTech/chat/pull/78
- [x] https://github.com/MaineCyberTech/chat/pull/79
- [x] https://github.com/MaineCyberTech/chat/pull/80
- [x] https://github.com/MaineCyberTech/chat/pull/81
- [x] https://github.com/MaineCyberTech/chat/pull/82
- [x] https://github.com/MaineCyberTech/chat/pull/83
- [x] https://github.com/MaineCyberTech/chat/pull/84

### falcon
- [x] https://github.com/MaineCyberTech/falcon/pull/14
- [x] https://github.com/MaineCyberTech/falcon/pull/15
- [x] https://github.com/MaineCyberTech/falcon/pull/16
- [x] https://github.com/MaineCyberTech/falcon/pull/17
- [x] https://github.com/MaineCyberTech/falcon/pull/18
- [x] https://github.com/MaineCyberTech/falcon/pull/19
- [x] https://github.com/MaineCyberTech/falcon/pull/20
- [x] https://github.com/MaineCyberTech/falcon/pull/21
- [x] https://github.com/MaineCyberTech/falcon/pull/22
- [x] https://github.com/MaineCyberTech/falcon/pull/23
- [x] https://github.com/MaineCyberTech/falcon/pull/24
- [x] https://github.com/MaineCyberTech/falcon/pull/25
- [x] https://github.com/MaineCyberTech/falcon/pull/26
- [x] https://github.com/MaineCyberTech/falcon/pull/27
- [x] https://github.com/MaineCyberTech/falcon/pull/28
- [x] https://github.com/MaineCyberTech/falcon/pull/29
- [x] https://github.com/MaineCyberTech/falcon/pull/30
- [x] https://github.com/MaineCyberTech/falcon/pull/31
- [x] https://github.com/MaineCyberTech/falcon/pull/32
- [x] https://github.com/MaineCyberTech/falcon/pull/33

### falcon-edge
- [x] https://github.com/MaineCyberTech/falcon-edge/pull/17
- [x] https://github.com/MaineCyberTech/falcon-edge/pull/18
- [x] https://github.com/MaineCyberTech/falcon-edge/pull/19
- [x] https://github.com/MaineCyberTech/falcon-edge/pull/20
- [x] https://github.com/MaineCyberTech/falcon-edge/pull/21
- [x] https://github.com/MaineCyberTech/falcon-edge/pull/22
- [x] https://github.com/MaineCyberTech/falcon-edge/pull/23
- [x] https://github.com/MaineCyberTech/falcon-edge/pull/24
- [x] https://github.com/MaineCyberTech/falcon-edge/pull/25
- [x] https://github.com/MaineCyberTech/falcon-edge/pull/26
- [x] https://github.com/MaineCyberTech/falcon-edge/pull/27
- [x] https://github.com/MaineCyberTech/falcon-edge/pull/28
- [x] https://github.com/MaineCyberTech/falcon-edge/pull/29
- [x] https://github.com/MaineCyberTech/falcon-edge/pull/30
- [x] https://github.com/MaineCyberTech/falcon-edge/pull/31

### mainecybertech
- [x] https://github.com/MaineCyberTech/mainecybertech/pull/43
- [x] https://github.com/MaineCyberTech/mainecybertech/pull/53
- [x] https://github.com/MaineCyberTech/mainecybertech/pull/54
- [x] https://github.com/MaineCyberTech/mainecybertech/pull/55
- [x] https://github.com/MaineCyberTech/mainecybertech/pull/56
- [x] https://github.com/MaineCyberTech/mainecybertech/pull/57
- [x] https://github.com/MaineCyberTech/mainecybertech/pull/58
- [x] https://github.com/MaineCyberTech/mainecybertech/pull/59
- [x] https://github.com/MaineCyberTech/mainecybertech/pull/60
- [x] https://github.com/MaineCyberTech/mainecybertech/pull/61
- [x] https://github.com/MaineCyberTech/mainecybertech/pull/62
- [x] https://github.com/MaineCyberTech/mainecybertech/pull/63
- [x] https://github.com/MaineCyberTech/mainecybertech/pull/64
- [x] https://github.com/MaineCyberTech/mainecybertech/pull/65
- [x] https://github.com/MaineCyberTech/mainecybertech/pull/66
- [x] https://github.com/MaineCyberTech/mainecybertech/pull/67
- [x] https://github.com/MaineCyberTech/mainecybertech/pull/72 (integration of the stranded remediation onto develop)

**Re-audit 2026-10-04:** [mainecybertech-20261004-0840-verify-develop-a97425d](runs/mainecybertech-20261004-0840-verify-develop-a97425d/) — 34 verified-fixed / 9 partially-fixed / 1 still-open (`CI-P1-001` prod environment) / 0 regressed. The 16 remediation PRs had merged into `fix/p2-batch-31` after #32 landed it, so they were integrated to develop by PR #72 (merge `a97425db`); deploy run 37188587849 green, droplet healthy. Close-out remains conditional on the operator/owner items in the verification run's `roadmap.md`.

### repo-deep-dive
- [x] https://github.com/MaineCyberTech/repo-deep-dive/pull/1
- [x] https://github.com/MaineCyberTech/repo-deep-dive/pull/10
- [x] https://github.com/MaineCyberTech/repo-deep-dive/pull/2
- [x] https://github.com/MaineCyberTech/repo-deep-dive/pull/3
- [x] https://github.com/MaineCyberTech/repo-deep-dive/pull/4
- [x] https://github.com/MaineCyberTech/repo-deep-dive/pull/5
- [x] https://github.com/MaineCyberTech/repo-deep-dive/pull/6
- [x] https://github.com/MaineCyberTech/repo-deep-dive/pull/7
- [x] https://github.com/MaineCyberTech/repo-deep-dive/pull/8
- [x] https://github.com/MaineCyberTech/repo-deep-dive/pull/9

### snowride
- [x] https://github.com/MaineCyberTech/snowride/pull/10
- [x] https://github.com/MaineCyberTech/snowride/pull/11
- [x] https://github.com/MaineCyberTech/snowride/pull/12
- [x] https://github.com/MaineCyberTech/snowride/pull/13
- [x] https://github.com/MaineCyberTech/snowride/pull/14
- [x] https://github.com/MaineCyberTech/snowride/pull/15
- [x] https://github.com/MaineCyberTech/snowride/pull/16
- [x] https://github.com/MaineCyberTech/snowride/pull/17
- [x] https://github.com/MaineCyberTech/snowride/pull/18
- [x] https://github.com/MaineCyberTech/snowride/pull/19
- [x] https://github.com/MaineCyberTech/snowride/pull/20
- [x] https://github.com/MaineCyberTech/snowride/pull/21
- [x] https://github.com/MaineCyberTech/snowride/pull/22
- [x] https://github.com/MaineCyberTech/snowride/pull/23
- [x] https://github.com/MaineCyberTech/snowride/pull/7
- [x] https://github.com/MaineCyberTech/snowride/pull/8
- [x] https://github.com/MaineCyberTech/snowride/pull/9

## Post-merge checklist

1. Update the local clone to the default branch (`git fetch --prune origin`).
2. Re-run the machine checks: `tools/deterministic_checks.py <repo> --deep`; compare to the
   archived baseline and fail on new P0/P1.
3. Run the verification-mode LLM re-audit (see the runbook) and diff new vs original findings.
4. Reconcile merged sets to `verified-fixed` and refresh this queue.

---
*Generated by repo-deep-dive tools/reaudit_queue.py*
