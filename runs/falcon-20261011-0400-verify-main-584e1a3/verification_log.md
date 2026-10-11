# Verification log - post-merge re-audit

- Repo: `MaineCyberTech/falcon` @ `584e1a3` (main; remediation PRs #49-#54 merged)
- Original run: `falcon-20261009-2117-full-08e20d1`
- Procedure: `runbooks/POST_MERGE_REAUDIT.md`
- Date: 2026-10-11

## Method

1. Machine re-audit: `tools/deterministic_checks.py /home/user/falcon-build --run falcon --deep`
   at the merged tree: 5 DET findings, no P0/P1 regressions; the one new item (exec bit) fixed
   by PR #52.
2. Three independent verification agents re-checked the reconciled findings against the merged
   commit and the live host (read-only); full reports under `verification/group-a.md` (-b, -c).
3. New findings were remediated in-flight: proxy sockets restored + alerted (PR #53),
   publication rebound (chain 0 failures), tunnel ingress v13 with enroll restored (PR #54).

## Finding-by-finding result (reconciled + new)

| ID | Severity | Status | Evidence |
|---|---|---|---|
| SEC-P1-001 / INFRA-P1-001 / CHAIN-P1-001 | P1 | verified-fixed | live per-port wg0 set; nftables.conf == repo (sha f6b18722); peers handshaking |
| ARCH-P1-002 | P1 | verified-fixed | tree clean; HEAD == remote main; #49 ancestor |
| CI-P1-001 | P1 | owner-accepted | runner hardening owner-gated (unchanged) |
| ARCH-P1-003 / RES-P1-001 / PERF-P1-001 | P1 | verified-fixed | aggregator 1G; RestartCount 0; no OOM lines since 2026-10-09T22:29Z |
| PERF-P1-002 / DR-P3-002 | P1/P3 | verified-fixed | guard watches both LVs; keep-3 retention; Oct 11 pruned snap-20261007 |
| OBS-P1-001 / PERF-P2-003 / PERF-P2-005 | P1/P2 | verified-fixed | drop counter + all-component sums exported; both rules live |
| OBS-P0-001 / FEAT-P2-002 | P1/P2 | verified-fixed | live Grafana 86 rules |
| DR-P2-001 | P2 | verified-fixed | no watermark overrides; defaults + single-node enable |
| WH-P1-001 | P1 | partially-fixed | detection closed; DLQ/replay residual |
| NOTIF-P1-001 | P1 | verified-fixed | internal-only lab ntfy; v13; watcher local read OK |
| DR-P1-001 / INFRA-P2-003 | P1/P2 | verified-fixed | retry+alert; Oct 10/11 runs succeeded; offsite real-path fix (#51) |
| DOC-P2-002 / OBS-P2-001 | P2 | verified-fixed | drift 28/0; lint 85/85/85 |
| HYGIENE-P2-001 | P2 | still-open | 39 files / 29.6 MB committed SBOM/vuln JSON |
| INFRA-P1-002 (new) | P1 | verified-fixed | sockets restored/enabled; boot check 17/0; DO agent online; alert rule live |
| CI-P2-004 (new) | P2 | verified-fixed | publication rebound; CI green on the rebind commit |
| INFRA-P1-003 (new) | P1 | verified-fixed | tunnel v13; enroll byte-identical to the service |
| INFRA-P2-004 (new) | P2 | verified-fixed | v13 applied + documented; remote-vs-repo drift check = follow-up |
