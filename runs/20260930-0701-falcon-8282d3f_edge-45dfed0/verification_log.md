# Verification Log — run `20260930-0701-falcon-8282d3f_edge-45dfed0`

Verification-only pass over the findings remediated on 2026-09-30, executed at the current commits (falcon `8282d3f` + this session's commits; edge `f2acd9c` + this session's commits). Method: artifact-backed re-checks (tests, validators, live captures) per the shared verification discipline. No finding is closed by assertion.

Status vocabulary: `verified-fixed` · `partially-fixed` · `still-open` · `regressed` · `owner-accepted`. Findings not listed here remain `open` as filed in `follow_up_register.md` (not re-assessed in this pass). Rows marked "(prior run)" are prior-run findings verified by the 2026-09-30 audit triage, kept here for traceability.

## Summary

| Status | Count |
|---|---:|
| verified-fixed | 48 |
| partially-fixed | 38 |
| regressed | 0 |
| owner-accepted | 0 (no new acceptances; prior exceptions unchanged) |

Counts are by finding ID in `follow_up_register.md` (some rows above cover a class of IDs).

## Verified findings

| Finding | Fix evidence (commit / capture) | Status | Notes |
|---|---|---|---|
| CI-P2-001 | `c11fa94`; E-REVIEW-FIX `20260930T162000Z`/`162151Z` audit-run-scanner-before/after | verified-fixed | `ci/validate.py` passes with the run folder in-tree |
| FINAL-P1-003 | `c11fa94`, `fa82005` | verified-fixed | Run-folder lifecycle: allowlisted for `long_hex`; run committed |
| SC-P1-001 | `f1f6f19`; E-REVIEW-FIX `20260930T164206Z` scanner-hardening-before/after; `101bae8` | partially-fixed | XML-tag + placeholder/pattern skips + hash-only allowlist; residual: history scan outside CI, gitleaks allowlists |
| RES-P0-001 | `3b616d6`, `fb3d6ca`; E-REVIEW-FIX `20260930T165608Z` alert-path-fixes-deploy, `165618Z` metrics | verified-fixed | Offsite success gauge + 36 h rule live; failure alert path verified |
| RES-P0-002 | `3b616d6`; E-REVIEW-FIX `165608Z`/`165618Z` | verified-fixed | Relay publish-failure metric + rule; relay liveness probed |
| OBS-P1-001 | `dbc7c6c`; E-REVIEW-FIX `165608Z` | partially-fixed | Watcher-stale rule (1 h) live; external DO-side dead-man improvements remain |
| OBS-P1-002 | `3b616d6`, `339f3ee`; E-REVIEW-FIX `165808Z` newservices-backup-verified | verified-fixed | Offsite + new-services gauges and rules; new-services verification fixed |
| OBS-P1-003 | `3b616d6`, `dbc7c6c` | partially-fixed | Exporter/probe/guard freshness, swap, scrape-error, relay metrics + rules live; external eval-plane dead-man remains |
| DR-P1-001 | `3b616d6`, `fb3d6ca`; `724302e` | verified-fixed | Offsite metric + committed recovery evidence |
| DR-P1-002 | `339f3ee`; E-REVIEW-FIX `165653Z` archive-inspect, `165729Z` critical-diagnose; `192021Z` pruner dry-run, `192257Z` cold-copy drill | partially-fixed | SIGPIPE check bug fixed; archive proven complete (219 entries); pruner retained-union + fail-closed implemented (live dry-run; first engagement at the next offsite run); residual: restore rehearsal |
| PERF-P1-001 | `d0d54ea`; E-REVIEW-FIX `183319Z` image-prune, `183444Z` projection rules | partially-fixed | ~1.2 GB reclaimed; 90% critical + projection rules live; volume-migration window remains |
| PERF-P1-002 | `d0d54ea`; E-REVIEW-FIX `183349Z` guard-drill | verified-fixed | 15 GiB band + 7-day projection + sanctioned drill (849 MB freed, alert fired); 7-day stability observation noted |
| LIVE-P0-001 | `3b616d6`, `dbc7c6c`, `d0d54ea` | verified-fixed | Relay/watcher/offsite blindness closed; periodic independent-instance canary (C4 stronger form) remains Three-path canary live 2026-09-30 (all 2xx); DO-side watcher threshold remains (OBS-P1-001). |
| LIVE-P0-002 | `3b616d6`, `339f3ee`, `fb3d6ca` | verified-fixed | Backup truth: gauges, rules, verification fix, committed evidence |
| API-P0-001 | `101bae8`; E-REVIEW-FIX `173315Z` vt-key-rotation-live (VT 200), `173408Z`/`173419Z` vt-key-scrub-* | partially-fixed | VT key rotated + repo/package scrubbed + scanner tightened; residual: Wazuh cluster keys, old-key revocation, rebuild/rebind (C1) Cluster key rotated + Shuffle key retired 2026-09-30 (live cluster re-formed; secrets stored; repo/package scrubbed); rebuild/rebind at C1. |
| FINAL-P0-001 | `aa35d96`, `29670b8`, `101bae8` | partially-fixed | Release chain: C3 done, C2 partial; approval re-review/rebind pending (C1) |
| FINAL-P0-002 | `3b616d6`, `dbc7c6c`, `d0d54ea` | partially-fixed | Live-protection detection largely closed; independent canary pending |
| EXEC-P1-001 | this pass; commits above | partially-fixed | Several prior P0s now verified-fixed; closure tracked in the register |
| EXEC-P1-002 | `4470ec6` owner_decisions.md | verified-fixed | Owner decisions D1–D8 recorded (owner-approved) |
| ND-P1-001 | `93ea9c6` (prior); agents' triage + validate | verified-fixed | Digest derivation from ledgers |
| DOC-P1-001 (class: AI-P1-001, INV-P1-001) | C8 pass; `docs/CURRENT_STATE.md` + AGENTS/README pointers | verified-fixed | Static open-gate lists replaced by the generated current-state page |
| FEAT-P1-001 | C8 pass; `docs/CURRENT_STATE.md` | partially-fixed | Status claims now have an authoritative page; remaining summary artifacts regenerate at C1 |
| INV-P0-001 | `aa35d96`, `29670b8`; E-REVIEW-FIX `171838Z` release-freeze | verified-fixed | C3: versioned manifest; pin verifies |
| INTG-P0-002 (prior run) | `5b9f232` (prior); `wg_peer_preservation_check.sh` | verified-fixed | Peer preservation verified at the 2026-09-30 audit; pin claim corrected |
| INTG-P1-001 | `ec59fc2`; E-REVIEW-FIX `171206Z` edge-monitoring-deploy, `171213Z` edge-cp-probe | verified-fixed | 5 scoped edge rules live; edge-cp probe 200 |
| XREPO-P0-001 | `aa35d96`, `29670b8`; E-REVIEW-FIX `171905Z` release-verify | verified-fixed | Pin resolves against the frozen release |
| EVID-P0-001 | `aa35d96`, `29670b8` | partially-fixed | Machine artifacts/rebind advanced; approval re-review pending (C1) |
| EVID-P0-002 | `4470ec6` (D1/D8 dispositions) | partially-fixed | Re-review path owner-approved; reviewer artifact is human (C1) |
| REV-P0-001 | `aa35d96`, `29670b8` | partially-fixed | Same as EVID-P0-001 |
| REV-P1-001 | `93ea9c6` (prior); C1 pending | partially-fixed | Digest derivation fixed; verdict-text regeneration at rebind |
| SEC-P1-001 | `ddd8d39`; E-REVIEW-FIX `182518Z` c6-security-verification, `182810Z` c6-r1-live-repro | verified-fixed | Server-pinned subjects; live CN=operator cert → 403 |
| SEC-P1-002 | `ddd8d39`; `182518Z` | verified-fixed | Ingest attributed to certificate identity |
| ACM-P1-001 | `ddd8d39`; `182745Z` c6-control-plane-restart | verified-fixed | Operator fingerprint recorded; operator cert 200 |
| ACM-P1-002 | `ddd8d39`; `182810Z` | verified-fixed | REVOKED/RETIRED enforcement live |
| ADV-P1-001 | `ddd8d39`; `182810Z` | verified-fixed | R1 fails closed (403) |
| ADV-P1-002 | `ddd8d39`, `aee70b4` | partially-fixed | Key custody encrypted; CA/key concentration mitigation recorded |
| CTR-P1-001 | `d013958`, `f1da279` | verified-fixed | Update path root-side verification |
| CTR-P1-002 | `d013958`, `f1da279`; `182518Z` | verified-fixed | Forged/symlink bundles rejected |
| FLEET-P1-001 | `aa35d96`; `171905Z` | verified-fixed | Manifest sidecar verifies; release frozen |
| FLEET-P1-002 | `d013958`, `f1da279`; `182518Z` | partially-fixed | Crash-safe swap + boot recovery implemented; device receives it at the next image bake; full A/B out of scope (hardware) |
| XREPO-P1-002 | `ec59fc2`; `171206Z` | verified-fixed | Edge rules deployed via the central Grafana path |
| OBS-P1-004 | `ec59fc2`; `171206Z` | verified-fixed | Same |
| XREPO-P1-003 | `aee70b4`, `f97bf9a`; `171215Z`, `171311Z` plaintext-retired | verified-fixed | Encrypted, out of the release surface, offsite-covered |
| DOC-P1-002 (also FLEET-P3-008) | C8 pass; edge README/REPOSITORY/AGENTS | verified-fixed | Hardware status lines corrected |
| SECRET-P1-003 | `aee70b4`, `f97bf9a`; `171215Z`, `171311Z` | verified-fixed | Encrypted backups; plaintext retired from the release surface |
| DR-P1-005 | `f97bf9a`; `171215Z` | partially-fixed | Edge PKI/DB offsite uploader in place; first scheduled upload + custody attestation pending |
| RES-P1-003 | `ec59fc2`, `f97bf9a` | partially-fixed | Edge alerts deployed; PKI offsite first upload pending |
| D2 (prior-run REV-P2-006) | `f2acd9c`; edge D-020 | verified-fixed | P9-G04 owner approval recorded |


## Batch mapping (register reconciliation)

The following current-run findings map to fixes verified above and were updated in `follow_up_register.md`:

- **verified-fixed**: API-P1-001, LIVE-P1-003, XREPO-P1-001, FINAL-P1-002, FINAL-P1-004
- **partially-fixed**: XREPO-P1-004, RES-P1-002, RES-P1-004, RES-P1-005, EVID-P1-002, EVID-P1-004, FEAT-P1-002, REV-P1-002, DOC-P2-004, ARCH-P1-001, CI-P2-002, DR-P1-004, NOTIF-P1-001, RES-P1-001, PRIV-P1-001, INV-P0-002


## Quick-win batch (2026-09-30, post-C8 pass)

- **verified-fixed**: OBS-P1-005, RES-P1-006, NOTIF-P1-002, PRIV-P1-002, DOC-P1-003, INFRA-P1-001, LIVE-P1-002, DATA-P1-001, DATA-P1-002, BP-P2-003, SBOM-P1-001, FINAL-P1-001
- **partially-fixed**: DR-P1-003 (uploader reuse live at the next offsite run; rehearsal breadth remains), BP-P1-001 (plan-gated: GitHub Pro required for branch protection; files/docs added), BP-P2-002 (CODEOWNERS/PR template added; required review not enforceable on Free)

## Residuals (recorded, not closed)

- **C1 (human)**: reviewer-produced artifact, JPB disambiguation, approval re-review/rebind — owner-approved path (D1/D8); no agent action closes it.
- **C2 (rotation)**: Wazuh cluster keys + ssl_manager_key; old VT key revocation in the VT console; repo/package rebuild + rebind at C1.
- **C4 (stronger form)**: a periodic canary arriving on the independent instance each cycle; DO-side watcher threshold/mutual check.
- **C5**: offsite pruner retained-union redesign; custody attestation + decrypt drill evidence for `backup_enc.key` (drill exercised; attestation pending).
- **C7**: Docker volume migration (~35 GB) ops window; 7-day free-space stability observation.
- **DR-P1-003**: duplicate snapshot/config per run; recoverability-window documentation; rehearsal breadth.
- **Edge device**: the running sensor executes the pre-fix apply script until the next image bake.
- **Scanner**: history scan outside CI; gitleaks allowlist review.

## Not re-assessed

All other findings in `follow_up_register.md` remain `open` as filed; the next verification pass (or the focused re-runs) covers them.

## Post-run follow-up — offsite efficiency and remote-integrity verification (2026-09-30 evening)

Beyond the C1-C8 reconciliation, the evening pass hardened the offsite backup path and closed
the DR-P1-002 blast radius:

- **Whole-repo re-upload -> local upload-state delta** (`bootstrap/80-offsite-backup.sh`): the
  Spaces key cannot list the bucket, so the uploader previously re-sent everything (~27 GB
  OpenSearch, 5.5 GB Wazuh) every run. The delta uploads only new/changed files; measured
  no-op run 2.8 s / 0 uploads; the Wazuh resume uploaded 1,722 files in 522 s.
- **Deploy incident + fixes**: the guard drill's snapshot deletion rewrote
  `index.latest`/`index-51` after the last successful upload; a naive seed then marked them
  uploaded. Fixed by (a) seeding only files that predate the last-success stamp and (b)
  requiring a real file object (`IsDir: false`) in the post-prune read-back.
- **Real remote loss found and restored (DR-P1-002 escalation)**: the pre-union prune had
  silently deleted 195 shared OpenSearch segment blobs (1.4 GB) plus the root index files;
  the 3-file sample never sampled them. A full size verification found them; they were forced
  back through the delta and restored. The full verification
  (`automation/validation/offsite_verify_all.py`) now runs at the end of every offsite run
  and fails the run before the success stamp (live PASS 23:22Z).
- **Host restart (22:34Z)**: interrupted the first full Wazuh upload; resumed with a
  presence-verified state (3,345/5,067 files already committed; 1,722 re-sent). The restart
  also exposed the WireGuard boot ordering cycle (VPN + proxy sockets down after every
  reboot) — fixed durably (sockets in `multi-user.target`, units now provisioned from
  `config/systemd/` by `bootstrap/95-wireguard.sh`).
- **Metrics exporter**: duplicate newest-EVE query removed (6.1 s -> 5.6 s per run).
- **Runtime review**: `docs/runbooks/RUNTIME_AND_SCHEDULE.md` (measured runtimes, schedule
  collision check, open recommendations).

Evidence: E-REVIEW-FIX `offsite-delta-seed/run`, `offsite-repair-stale` (interrupted),
`offsite-wazuh-presence-seed`, `offsite-finish-run`, `offsite-verify-all(-full)`,
`offsite-restore-missing`, `wg-boot-ordering-fix`, `wg-proxy-units-install`,
`metrics-exporter-before/after`; ledger row 2026-09-30T23:25Z.

- **Edge follow-up (2026-10-01)**: `DATA-P1-003`/`TEST-P2-003` fixed — `purge_expired()` cut at `now` (delete-all) while its count used `now - max_age`; the cut is now `now - max_age` for both, with a mixed-age boundary test that fails on the pre-fix code (evidence: queue-purge-mixed-before2/after, queue-full-suite 199 tests OK).
