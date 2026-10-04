# Post-merge verification re-audit queue

Generated: 2026-10-04T05:21:42Z

Procedure: `runbooks/POST_MERGE_REAUDIT.md`. After the remediation PRs merged,
run the machine checks and a verification-mode LLM re-audit per repo.

| Repo | Findings | P0 | P1 | P2 | P3 | PRs merged | Re-audit |
|---|---:|---:|---:|---:|---:|---:|---|
| buddy | 40 | 0 | 11 | 24 | 5 | 13 | [x] |
| chat | 65 | 1 | 26 | 31 | 7 | 28 | [x] |
| falcon | 46 | 4 | 20 | 18 | 4 | 20 | [x] |
| falcon-edge | 43 | 0 | 3 | 27 | 13 | 15 | [x] |
| mainecybertech | 44 | 1 | 3 | 26 | 14 | 16 | [x] |
| repo-deep-dive | 41 | 0 | 9 | 20 | 12 | 10 | [x] |
| snowride | 46 | 0 | 6 | 25 | 15 | 17 | [x] |

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

**Re-audit result (2026-10-04):** 8/11 P1 closed, 3 P1 still-open (`CI-P1-002`, `EXEC-P1-001`, `SUPPLY-P1-001`); P2 14/16 closed, P3 5/5 closed; 0 regressed. Owner-side residual: LICENSE still `PENDING`; branch protection unverifiable from a clone. [VERIFY](file:///C:/temp/reaudit/buddy/VERIFY.md)

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

**Re-audit result (2026-10-04):** P0 1/1 closed; P1 25/25 closed (the one still-open, `OBS-P1-001`, was fixed by #95); P2/P3 spot-checks 15/17 closed; 0 regressed. [VERIFY](file:///C:/temp/reaudit/chat/VERIFY.md)

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

**Re-audit result (2026-10-04):** P0 3/4 closed, 1 still-open (`OBS-P0-001`); P1 14/20 closed, 5 still-open + 1 owner-accepted (`CI-P1-002`); 0 regressed. Owner-side residual: branch protection plan-gated, single-host standby, retention decision, review-package. [VERIFY](file:///C:/temp/reaudit/falcon/VERIFY.md)

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

**Re-audit result (2026-10-04):** P1 3/3 closed (all one root cause); P2/P3 30/39 closed, 9 still-open; 0 regressed. Owner-side residual: `AUTH-001` (#40) held. [VERIFY](file:///C:/temp/reaudit/falcon-edge/VERIFY.md)

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

**Re-audit result (2026-10-04):** P0 closed (`DATA-P0-001`); P1 `SEC-P1-001` + `CI-P1-001` fixed by #83–#86 (prod boot requires `FIELD_ENCRYPTION_KEY`; required reviewers configured on `prod`/`prod-approval`), `FINAL-P1-001` still-open; `SEC-P2-002` worker SSRF fixed by #84; 0 regressed. The 16 remediation PRs had merged into `fix/p2-batch-31` after #32 landed it, so they were integrated to develop by PR #72 (merge `a97425db`); deploy run 37188587849 green. Earlier verification run [mainecybertech-20261004-0840-verify-develop-a97425d](runs/mainecybertech-20261004-0840-verify-develop-a97425d/) recorded 34 verified-fixed / 9 partially-fixed / 1 still-open before #83–#86. [VERIFY](file:///C:/temp/reaudit/mainecybertech/VERIFY.md)

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

**Re-audit result (2026-10-04):** P1 9/9 closed; the one regression (`SUPPLY-P1-001`, Actions pin reverted) was fixed by #39 (`7893e39`); 0 still-open, 0 regressed. [VERIFY](file:///C:/temp/reaudit/repo-deep-dive/VERIFY.md)

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

**Re-audit result (2026-10-04):** P1 5/6 closed — `SEC-P1-001` + `SUPPLY-P1-001` + `CI-P1-001` closed at HEAD; the `DATA-P1-001` migration-head regression and `OBS-P1-001` host-only schedule were fixed by #38 (`af7f796`/`ce3f639`); `FINAL-P1-001` (stale-identity + no signature-tamper CI gate) still-open; 0 remaining regressions. [VERIFY](file:///C:/temp/reaudit/snowride/VERIFY.md)

## Post-merge checklist

1. Update the local clone to the default branch (`git fetch --prune origin`).
2. Re-run the machine checks: `tools/deterministic_checks.py <repo> --deep`; compare to the
   archived baseline and fail on new P0/P1.
3. Run the verification-mode LLM re-audit (see the runbook) and diff new vs original findings.
4. Reconcile merged sets to `verified-fixed` and refresh this queue.

---
*Generated by repo-deep-dive tools/reaudit_queue.py*
