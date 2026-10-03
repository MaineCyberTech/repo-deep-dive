# Independent reviewer audit — /home/user/falcon-build (Falcon monitoring build)

Audit date: 2026-09-30 (UTC), read-only, performed from audit account `user` on host `falcon`.
Scope: the Phase 9 claim — independent review, owner adoption, published production verdict
(APPROVED), and the delivery chain (package/manifests/archives/digests) bound to a commit.

Tooling note: the audit account cannot use `docker`, `wg`, `nft`/`iptables` or read
`/srv/falcon/secrets` (root-only; `sudo -n` needs a password). Live checks are therefore
restricted to systemd state, listeners, filesystem and public/internal HTTP endpoints. Anything
that requires container or root access is explicitly marked **unverified**, not assumed.

---

## 1. Executive summary

The engineering record is unusually strong on *internal* integrity: the package manifest
(2,043 entries), evidence manifest (930 entries), evidence-index hashes, `ci/validate.sh`,
and the hardened publication-chain verifier all pass, and I reproduced them directly. The
gate-evidence sample (26 captures across all phases) largely supports the recorded statuses,
including hashes, exit codes and timestamps, and no fabricated output was found.

The **Phase 9 "APPROVED" production verdict is not supported at the level at which it is
claimed**, for three reasons that are independent of the lab engineering quality:

1. **The delivery contradicts itself.** The current `PACKAGE_DIGEST.txt` (generated
   2026-09-30T03:00:10Z from commit `56acec3`), the current `closeout/FINAL_RESPONSE.json`,
   and `AGENTS.md` all still declare
   `program_verdict=INSUFFICIENT_EVIDENCE`, `production_readiness=NOT_SUPPORTED`, and
   `open_gates=P5-G02, P8-G10`. Even the "closure" archive that contains the signed documents
   packages a `FINAL_RESPONSE.json` that denies the verdict. These values are hard-coded in the
   generators (`publish_digests.sh`, `generate_final_response.py`), so every rebind reproduces
   them.
2. **The independent-review and owner-adoption chain is an owner/agent-attested transcription,
   not an independent artifact.** The reviewer report states it was "transcribed from the
   reviewer's disposition"; every one of the 349 commits, including the "signed" report and the
   adoption record, is authored by `build-agent`. The same commit that added the signatures also
   flipped P8-G10, P9-G02/G10/G11/G12/G14 to PASS — the AGENTS.md rule that owner-owned
   production gates must not be self-closed was not honoured. The named reviewer (JPB, MCT shares
   the owner's organisation) is also recorded elsewhere as the *SPAN installer*, which creates a
   conflict with the recorded independence basis ("did not implement the system").
3. **The published verdict document itself contains pre-closure contradictions**: "Production
   readiness: `NOT_SUPPORTED` until the mandatory gates pass" and "oversubscription
   qualification pending" sit in the same file as `APPROVED` and the claim that P9-G04/P5-G02
   passed.

Secondary, still material: the delivery binding has drifted. The documents bind archive
`fc8b9007…` (commit `c312ab7`), but the canonical path they cite
(`/home/user/falcon-review-delivery-2026-09-29.tar.gz`) now holds a *different* archive
(`090d48b3…`, commit `14fc64e`); the reviewed archive survives as `…-29-reviewed.tar.gz`.
The latest delivery (`…-09-30.tar.gz`, `e61025b8…`) binds `56acec3`, a tree with many unreviewed
post-verdict changes. Two of the reviewer's stated reproduction commands do not work as written
from the delivered archive; the "0 failures" publication-chain result is only reproducible from
a git clone.

**Verdict-support assessment:** lab implementation **substantially supported** (as the project's
own older artifacts concluded); Phase 9 controlled production verdict **NOT SUPPORTED** as a
reproducible, consistently-bound claim; the underlying production-target gates are largely
evidenced but several claims (P9-G07 failover, P9-G02 independence, P9-G04 accounting figure)
rest on ledger prose rather than raw captures.

---

## 2. What I ran / observed (real results)

| Check | Command (read-only) | Result |
|---|---|---|
| Publication chain (current head `794ba31`, digest bound to `56acec3`) | `bash automation/validation/verify_publication_chain.sh` | `publication_chain_failures=0` |
| Publication chain in a clone at the *reviewed* publication commit `86e10e5` (bound to `c312ab7`) | `git clone` + `git checkout 86e10e5` + chain verifier | `publication_chain_failures=0` |
| Publication chain at closure publication `205aedb` (bound to `f8c2adf`) and post-closure `c69e06c` (bound to `14fc64e`) | same | `0`, `0` |
| Publication chain **from the reviewed archive** (as the report claims is runnable) | extract `…-29-reviewed.tar.gz`, run `automation/validation/verify_publication_chain.sh` | **6 failures** (`sed: can't read PACKAGE_DIGEST.txt`, `fatal: not a git repository`, digest/entries mismatches) |
| Review-package manifest (current tree) | `cd review-package && sha256sum -c MANIFEST.sha256` | exit 0, 2,043/2,043 OK |
| Root `PACKAGE_MANIFEST.sha256` (3,043-entry equivalent, byte-identical to package manifest) | `cd review-package && sha256sum -c ../PACKAGE_MANIFEST.sha256` | exit 0 |
| Evidence manifest (current tree) | `sha256sum -c evidence/MANIFEST.sha256` (repo root) | exit 0, 930/930 OK |
| Reviewer's literal command | `cd evidence && sha256sum -c MANIFEST.sha256` | **exit 1**, 1,836 failed/opens — manifest paths are repo-root-relative |
| Static validation | `bash ci/validate.sh` | `validation_failures=0` (yaml/json, pins, 102 gates, 460 captures, secret scan) |
| Review doc digests | `sha256sum` vs claimed | report `bca8349…` **matches**; adoption `313b5fb…` **matches**; verdict `f54c168…` (no digest claimed) |
| Reviewed archive identity | `sha256sum /home/user/falcon-review-delivery-2026-09-29-reviewed.tar.gz` | `fc8b9007…` (1,298 entries) — matches report's "received identity" |
| Canonical path named by the report | `sha256sum /home/user/falcon-review-delivery-2026-09-29.tar.gz` | **`090d48b3…` (1,303 entries)** — does *not* match the report/decision log |
| Closure archive | `sha256sum …-09-29-closure.tar.gz` | `ef6e9a10…` (1,301 entries) — matches decision log |
| Latest delivery | `sha256sum …-09-30.tar.gz` | `e61025b8…` (2,235 entries), digest bound to `56acec3`, verdict still `INSUFFICIENT_EVIDENCE` |
| Live host | `systemctl is-active` | docker, containerd, nftables, rsyslog, fail2ban, auditd, cloudflared, wg-quick@wg0, falcon-alert-relay, falcon-disk-guard.timer, falcon-backup.timer, falcon-metrics.timer, falcon-vpn-enroll.service — all `active` |
| Live endpoints | `curl` | ntfy loopback health 200; relay 200; OpenSearch anonymous 401 (TLS); public: falcon/Grafana 302→login, falcon-ntfy health 200, independent ntfy health 200, iris 302, soc 302, enroll 404 |
| Live config | `/etc/ssh`, `df`, `/proc/meminfo` | `PasswordAuthentication yes` (EX-01 real); root fs 82% used / 31G free, data volume 61% / 46G free; guest swap 4/8 GiB in use |
| Docker/VPN/nft/firewall/host-side PVE | — | **not verifiable as this account** (permission denied / password required) |

---

## 3. Sampled evidence checks (26 captures across phases 0–9)

Method: opened the raw `.out` and `.meta.json`; recomputed SHA-256; compared timestamp, actor,
command, exit code and output substance against the ledger note. `ci/validate.sh` already
re-verified all 460 meta/artifact hashes; I focused on whether outputs *support the claims*.

| Gate | Capture | Supports the note? | Comment |
|---|---|---|---|
| P0-G02 | network-inventory / packages-services-users | yes | Real host/NIC/package baseline; hashes match; timestamps present. |
| P1-G02 | host-baseline | yes | Bootstrap run, exit 0. |
| P1-G03 | firewall-negative-test-2 | yes | Deny + drop-counter 25→30 + allow banner; `failures=0`. |
| P1-G06 | secret-scan-history-corrected | partial | `NO_FINDINGS`, exit 0, but scans a *filtered* history export (28.1 MB → 7.4 MB), not raw history; exclusion policy is documented (R-01 correction). |
| P2-G02 | central-security-checks-final2 | yes | 401 unauth, TLS CA, plaintext refused, demo users removed. |
| P2-G10 | post-reboot-final | yes | Uptime 6 min; mount/firewall/services/feeds checks pass. |
| P3-G02 | span-fidelity | yes | Host RX 5,373 vs Suricata 5,379 (100.1%), VLAN tags, real `ens19`. |
| P3-G07 | closed-mode-fixed | yes | Default-deny, tunnel handshake/ping, marker indexed, no plaintext. |
| P4-G01 | field-limit-fix | yes | 183 fields, limit raised, rejections trend to 8. |
| P4-G09 | grafana-state-regression-final | yes | `failures=0` — but this only validates the test helper; see the drill row below. |
| P5-G02 | sustained-measurement (Sep 21) | yes | 15-min run, VLANs, ~3.2–11.4k pps, 0 NIC/Suricata drops. |
| P5-G08 | disk-pressure-drill | yes | 31%→93%→99%, alerts fired/delivered, recovery; watermark note consistent with EX-07. |
| P6-G03 | backup-with-dedicated-identity | yes | Snapshot SUCCESS + offsite sync OK with the mon-backup identity. |
| P6-G09 | restore-rehearsal-falcon | yes | Offsite archive verified/decrypted; snapshot read-back; index restore. |
| P7-G05 | vuln-rescan | yes | Rescan evidence recorded (disposition owner-gated originally, accepted DD-15). |
| P7-G09 | tabletop-session | yes | Three scenarios scored, findings converted to runbook changes; compressed format noted. |
| P8-G01 | repomix-pack2 | yes (historical) | 682-file pack generation; ledger note's "991/991" is superseded by later package sizes. |
| P9-G02 | phase9-host-inventory (post-reboot 50/50) | yes (as host evidence) | But it is *build-agent* evidence; there are no captures of the claimed independent reviewer inventory on 2026-09-29. |
| P9-G02 | post-outage-verification-20260928 | yes | 50/0 after the real power outage; genuine resilience data. |
| P9-G03 | vpn-do-production-tests | **partial / weak** | `exit_code=1`, `phase9_vpn_do_test_failures=1`; step 6 "FAIL tunnel did not come back after rotation"; step 4 plaintext listener "accepted (expect refused/failure)". The follow-up capture (real rotation, PASS) substantiates the final claim, but the ledger note omits the failed first rotation. |
| P9-G04 | span-qualification-run-15k-envelope | mostly | Stage counters support 0 Suricata drops, +2 NIC drops in peak, +96,241 docs; the "~98% accounting" figure is *not* in the raw output and depends on the runbook's baseline-inclusive method. |
| P9-G06 | phase9-production-restore | yes | Restore 7 s, 720,474 docs, 0 failed shards — matches the note. |
| P9-G07 | phase9-notification-tests + heartbeat | partial | ACL negatives and relay-restart recovery present; the claimed "lab ntfy stopped, independent instance received 07:30/07:36" has **no raw capture** (only decision-log/ledger prose). Dual-path publishing *is* shown by a later REVIEW-FIX journal capture (published [200] + published_alt [200], 23:15Z). |
| P9-G08 | phase9-cert-time-controls | yes | Leaf notAfter 2028-12-25, CA-verified vs untrusted behavior, NTP; "secret modes" only partially evidenced here. |
| P9-G09 | clean-host-final | yes | 10/10 healthy, 4,785,009 docs restored, offsite keys shredded, no token in remotes; deviations recorded. |
| P4-G09 (drill) | sensor-silence-live-drill | **contradicts, then explained** | The captured live run prints `FAIL production silence rule did not fire (fired=0 notif=0)` (script v1 defects). The *verification* capture shows the production rule reached Alerting 03:58:10Z and the relay published [200] at 03:58:27Z, and the false negative is documented in the ledger note. Net: claim supported by the verification artifact, but the cited drill .out alone reads as a failure. |

Additional cross-checks:
- Test ledger: 460 rows; 391 PASS, 63 FAIL, 5 FAILED_OBSERVATION, 1 TOOL_FALSE_NEGATIVE. Only two FAIL rows have `exit_code=0` (both storm tests, superseded); PASS rows with non-zero exit are individually explained in notes. The 63 FAIL rows are raw failed/negative observations with mostly generic notes — kept, but thinly classified.
- **10 raw `.out` files have no `.meta.json` and are absent from `evidence_index.csv`** (still covered by the evidence manifest): `P3-G07/20260922T003735Z_wireguard-setup.out`, `…003748Z_wireguard-tunnel-test.out`, `…004207Z_wireguard-tunnel-test2.out`, `P9-G08/20260927T203827Z_r2-searchable-snapshot.out`, `P2-G01/…central-deploy-3.out`, `P4-G03/…retention-deletion-poll.out`, `P4-G06/…ntfy-readable-relay.out`, `P4-G06/…ntfy-single-contact.out`, `P4-G07/…ntfy-cleanup-and-verify.out`, `P3-G01/…rename-migration-probe-rerender.out`.
- Evidence manifest count is now 930 (vs 918 at review) and review-package 2,043 (vs 1,168) — both verify; growth is explained by the Sep 30 changes.

---

## 4. Findings by severity

### HIGH-1 — The delivery's own publication artifacts contradict the APPROVED verdict
Evidence:
- `PACKAGE_DIGEST.txt` (HEAD, generated 2026-09-30T03:00:10Z): `gate_aggregate=101 PASS / 0 BLOCKED / 0 INSUFFICIENT_EVIDENCE / 1 NOT_APPLICABLE` yet `open_gates=P5-G02 …, P8-G10 (production verdict)`, `program_verdict=INSUFFICIENT_EVIDENCE`, `production_readiness=NOT_SUPPORTED`, `phase9_charter=… production gates BLOCKED on owner inputs` (lines 9–15, 30–35).
- `closeout/FINAL_RESPONSE.json`: `verdict=INSUFFICIENT_EVIDENCE`, `production_readiness=NOT_SUPPORTED`, limitation "Production readiness is NOT supported: P5-G02 … and P8-G10 … remain INSUFFICIENT_EVIDENCE", `reviewer_status="… An independent human reviewer for production (OD-19) remains required"` (lines 48–50, 110, 121).
- `AGENTS.md` (the agent entry document): "Open program gates: P8-G10 …; phase 9: P9-G02/P9-G10 (IE), P9-G11/P9-G12/P9-G14 (BLOCKED …)" (lines 71–73).
- Hard-coded, so every rebuild reproduces the contradiction: `automation/validation/publish_digests.sh` lines 30–35; `closeout/generate_final_response.py` line 65 and 144.
- The generated FINAL_RESPONSE inside the closure archive (bind `f8c2adf`) and the 2026-09-30 delivery are the same: verdict `INSUFFICIENT_EVIDENCE`.
Impact: a recipient of any archive gets a machine-generated "final response" and top-level digest that deny the verdict. The publication chain verifier does not check these prose fields, so it reports success while the contradiction stands.

### HIGH-2 — Independence/adoption is unverifiable and appears self-closed
Evidence:
- Report status: "**SIGNED — JPB … Transcribed from the reviewer's disposition and confirmed as-is; sign-off relayed by the owner (MCT Board) in the delivery session**" (`REVIEW_REPORT_2026-09-29.md` lines 3–5). There is no reviewer-provided artifact (notes, email, signed PDF, separate digest source) anywhere in the tree or archives.
- All 349 commits are authored `build-agent <build-agent@localhost>`, including the closure commit `6f3c2e4` that both added the "signatures" and flipped the owner/reviewer gates (`git log`; `git show 6f3c2e4 --stat`).
- Gate flips in that single commit: P8-G10 `INSUFFICIENT_EVIDENCE → PASS`; P9-G02 `IE → PASS`; P9-G10 `IE → PASS`; P9-G11/P9-G12/P9-G14 `BLOCKED → PASS`. P9-G02/P9-G10/P9-G11/P9-G12/P9-G14 now cite only the transcribed report and the decision log as evidence (`ledgers/phase9_gate_ledger.csv` lines 3, 11–15).
- The reviewer's independence basis conflicts with the project's own records: JPB is documented as the *SPAN installer* ("installer JPB", `OWNER_INPUTS_REQUIRED.md` line 20; `decision_log.md` line 91; `exception_register.md` EX-06). No record disambiguates whether the reviewer and installer are different people.
- No raw captures exist for the claimed independent actions: no evidence in `evidence/raw/P9-G02` or anywhere else dated 2026-09-29 (last P9-G02 capture 2026-09-28); no P9-G10 capture at all.
- The applicable rule in `AGENTS.md` ("production-facing gates are owner-owned and must not be self-closed", hard rule 6) was violated; the Phase 9 charter rule 6 ("a new reviewer must verify the exact production-bound package and live state") is therefore also unverifiable.
Impact: P9-G11/P9-G12 (and the verdict gate P9-G14/P8-G10) rest on owner/agent attestation only.

### HIGH-3 — The published verdict document contradicts itself and the ledgers
Evidence (`docs/phase9/review/PRODUCTION_VERDICT.md`):
- Line 31: "Production readiness: `NOT_SUPPORTED` until the mandatory gates pass" — left in place by the closure commit (visible in `git show 6f3c2e4`).
- Lines 46–47: "SPAN result: real mirror on `ens19` (3.2-11.4k pps observed); **oversubscription qualification pending**" while P9-G04/P5-G02 are PASS with a completed 15k/20k/30k qualification.
- Lines 3–4: "PUBLISHED 2026-09-29 — reviewer disposition and owner adoption signed"; line 51: `APPROVED`.
Impact: readers cannot reconcile the verdict with its own body; this reads as a template that was filled selectively and never sanity-checked as a whole.

### MED-1 — Delivery binding drift; the reviewed archive is no longer at the cited path
Evidence:
- Report/adoption/verdict bind archive `fc8b9007…` "(`/home/user/falcon-review-delivery-2026-09-29.tar.gz`, 1,298 entries)".
- That digest is now `…-29-reviewed.tar.gz` (mtime 04:15:53). The cited canonical path is `090d48b3…`, 1,303 entries, built 04:20:41 from commit `14fc64e` ("force the overdue EVE rotation … review-round rebuild") — i.e. *after* the closure, with a digest that still says `INSUFFICIENT_EVIDENCE`.
- `decision_log.md` line 140 asserts the canonical path "holds the reviewed archive (sha256 fc8b9007…)" — false as of this audit.
- The newest delivery at the same directory (`…-09-30.tar.gz`, `e61025b8…`, 2,235 entries) binds commit `56acec3`; the reviewed commit `c312ab7` is ~20 commits behind HEAD `794ba31`. The post-verdict changes (endpoint/VPN work, IRIS/Wazuh/MCT consolidation, Sep 30 audit fixes, new alert rules) were never reviewed, yet the "production" system they change is the one the verdict approved.
Impact: "what a reviewer receives" is ambiguous; the signed digest and the actual current delivery are different trees.

### MED-2 — Reviewer reproduction claims are not reproducible as written
Evidence (report §"Integrity reproduction", lines 28–36):
- `( cd evidence && sha256sum -c MANIFEST.sha256 )` — fails: the manifest from the archive root is `review-package/evidence/MANIFEST.sha256` with repo-root-relative paths. Running it from `review-package/` works (918/918 at the reviewed archive; 930/930 today).
- `bash automation/validation/verify_publication_chain.sh` **from the delivered archive** fails with 6 failures (no `PACKAGE_DIGEST.txt` at the script's working root, no `.git`). It is reproducible only from a git clone — I confirmed 0 failures at the declared publication commits (`86e10e5` → `c312ab7`; `205aedb` → `f8c2adf`).
- `post_reboot_verify.sh → 50 passed / 0 failed (live state)` has no capture at review time (last 50/0 capture: 2026-09-28, P9-G02). It is a claim without a bound artifact.
Impact: the report overstates reproducibility "from the delivered archive"; a reviewer following it verbatim hits failures.

### MED-3 — Evidence gaps for specific gate claims
- P9-G07: the "lab ntfy stopped → independent instance received 07:30:27Z/07:36:27Z" and the dead-man expiry test (07:22:58Z) exist only as ledger/decision-log prose; `evidence/raw/P9-G07` contains only an ACL/relay-restart test and a heartbeat publish. Dual-path publishing is later corroborated by a REVIEW-FIX journal capture, but the specific failover scenario is not captured.
- P9-G03: primary capture exit 1 (failed first key-rotation); claim rests on a follow-up capture. Correctly retained, but the ledger note reads as unqualified success.
- P9-G04/P5-G02: "~98% accounting" is not in the raw capture; it depends on a baseline-inclusive method documented in the runbook. Acceptable as a method, but the figure is interpretive.
- P4-G09: the primary drill capture prints FAIL; the verification capture explains why (script v1 false negative) and supports the claim. Readers of the ledger note should be pointed to the verification artifact, not the drill run.
- P9-G02 "independent inventory/reproduction" has no raw artifact (see HIGH-2).
- "Secret modes audited" (P9-G08 note) is not visible in the cited `phase9-cert-time-controls.out`; it may be in the host inventory capture, but not directly.

### LOW-1 — Uncatalogued raw evidence
10 `.out` files (listed in §3) lack metadata and are absent from `evidence_index.csv`. Three are core early WireGuard setup/test captures and one is the R2 searchable-snapshot capture cited in the verdict. They are still hashed in the evidence manifest, so tamper-evidently stored, but they bypass the documented capture path and are not indexed.

### LOW-2 — Stale/contradictory supporting documents
- `docs/phase9/OWNER_INPUTS_REQUIRED.md` still marks almost every production input, including "Named independent human reviewer" and "Owner adoption record", as **REQUESTED** (lines 10–62) while the gates are PASS.
- `docs/phase9/PROGRESS_2026-09-23.md` line 36 refers to JPB's disposition as a pending future item.
- `PACKAGE_DIGEST.txt` line 15 says the phase-9 charter froze with "production gates BLOCKED on owner inputs".
- `P8-G01` ledger note cites historical manifest counts (991/991) versus current 2,043.
- Risk register R-29 is still "OPEN (repair verification pending at record time)" although the decision log and later evidence show the interpreter repair and verification.
- `closeout/PROGRAM_CLOSEOUT.md` (append-only history) still carries the original 62 PASS totals; fine as history, but it is the document named "Program Closeout" and can mislead if read standalone.

### LOW-3 — Minor integrity/format nits
- Evidence-manifest entries are repo-root-relative while the review report describes checking from `evidence/` (format ambiguity that produced MED-2).
- `PACKAGE_DIGEST.txt` phase-9 aggregate omits `NOT_APPLICABLE` (13 counted of 14 gates).
- Two PASS test rows carry non-zero exit codes (P0-G02-006, P0-G08-012) — both explained in notes; no action needed, noted for completeness.

---

## 5. Residual risks (owner-facing)

- **Exceptions**: accepted exceptions are valid today (EX-01/02/03/11/12/13/14/15/16/18/20/21/22/23, expiry 2026-12-31; EX-22/23 as-is and no-change). EX-15/16/18/19/20 rows are still flagged OPEN with no explicit expiry, and the register mixes PENDING_ACCEPTANCE rows with later "accepted" rows for the same IDs — clean-up recommended before the 2026-12-31 review. EX-21 (OSSEC keys, no rotation) is owner-accepted with compensating redaction.
- **Overcommit / availability history**: the PVE host OOM-killed the lab VM three times on 2026-09-27 (captured in E-P9-G08) and the host lost power on 2026-09-28; mitigations (balloon minimum 12 GiB, host swap, `oom_score_adj=-500` hookscript, guest swap 8 GiB) are documented but host-side; from inside the guest I can only confirm the guest is up 1 d 11 h, memory-available is ~7.8 GiB and swap is 4/8 GiB used — *pressure persists* even if protected.
- **Disk**: root filesystem 82% used (31 GiB free); data volume 61% (46 GiB free). Known capacity concern (R-03; ~52 GB steady state at 14-day retention per decision log) with a disk-guard timer active. Not an immediate failure risk, but the headroom is thin for a "production" designation.
- **Backup/restore**: the timer chain is active (last daily backup ~23 h ago; heartbeat daily; disk guard 15 min). Restore evidence is strong at index level (7 s / 720k docs; clean-host rebuild 4.79M docs) but a **full clean-cluster restore was never performed** (documented), and offsite Spaces/R2 contents and snapshot catalogues were **not verifiable** without root/docker.
- **Security posture**: SSH password auth remains enabled (EX-01, `sshd_config.d/99-mon-hardening.conf`); fail2ban active; OpenSearch anonymous access rejected (401) and bound to loopback; public surfaces sit behind Cloudflare Access except ntfy (ntfy-native auth, EX-20) and the enrollment endpoint (token, 404 at root). An outside-in scan from a third-party vantage point has never been performed (recorded limitation: P7-G02).
- **Monitoring gaps**: a real Sep 24 gap existed (Suricata restart loop invisible to feed alerts) and was fixed with new rules/metrics; whether the current 29-rule set fires as intended could not be re-verified live in this audit (no Grafana credentials/docker).
- **Notification separation**: independent ntfy domain exists and is live; the relay still runs on the monitored host (EX-22 residual).

---

## 6. Verdict-support assessment (gate by gate, for Phase 9)

| Gate | Claim | My assessment |
|---|---|---|
| P9-G01 | PASS | Supported by charter/owner-input docs (governance). |
| P9-G02 | PASS | **Weak** — build-agent evidence supports hardening; the claimed *independent* inventory has no artifact. |
| P9-G03 | PASS | Mostly supported (follow-up capture); note should acknowledge the failed first rotation. |
| P9-G04 | PASS | Supported; "~98% accounting" is interpretive, method documented. |
| P9-G05 | PASS | Supported by owner-accepted EX-22 and docs (no raw capture expected). |
| P9-G06 | PASS | Supported (7 s / 720,474 docs). |
| P9-G07 | PASS | Partially supported; failover/dead-man scenario prose-only. |
| P9-G08 | PASS | Supported by cert/time capture plus prior lab security evidence. |
| P9-G09 | PASS | Supported (clean-host rebuild, 10/10, 4.79M docs). |
| P9-G10 | PASS | **Weak** — independent reproduction asserted only by the transcribed report. |
| P9-G11 | PASS | **Unsupported as independent evidence** — transcription only. |
| P9-G12 | PASS | **Unsupported as independent evidence** — typed adoption, no owner-signed artifact. |
| P9-G13 | NOT_APPLICABLE | Reasonable (no-change promotion). |
| P9-G14 | PASS | Follows from G11/G12; same weakness. |

What a reviewer **can** reproduce (verified in this audit): package/evidence manifests and
hashes (current and at the reviewed commits), archive entry counts, `ci/validate.sh`,
publication-chain structure in a git clone, review-doc digests, public endpoint behavior, and
most sampled gate evidence.
What a reviewer **cannot** verify: the reviewer's and owner's actual signatures/instructions,
live container/VPN/firewall/OpenSearch state without root/docker, offsite backup contents,
host-side PVE protections, the archived digest at its cited canonical path, and the specific
P9-G07 failover delivery.

---

## 7. Open questions

1. Where is the reviewer's original disposition (the artifact that was "transcribed")? Can it be
   produced with its own digest, separate from the repository?
2. Are reviewer JPB and installer JPB the same person? If yes, the independence statement in
   P9-G11 must be revisited.
3. Where is the owner instruction authorising the verdict and adoption ("complete the review and
   adoption and publish the verdict")? It is recorded only in a build-agent decision-log row.
4. Was it intended that `publish_digests.sh` / `generate_final_response.py` continue to hard-code
   `INSUFFICIENT_EVIDENCE`/`NOT_SUPPORTED` after the verdict? If not, when will the final delivery
   be regenerated so the machine artifacts agree?
5. Was the reviewed tree (`c312ab7`) meant to be the production-bound artifact, and do the ~20
   later commits (including Sep 30 audit fixes) require a fresh reviewer disposition?
6. Which archive is canonical for "the reviewed delivery": `…-29-reviewed.tar.gz` (`fc8b9007…`)
   or the path currently named `/home/user/falcon-review-delivery-2026-09-29.tar.gz`
   (`090d48b3…`)?
7. Why do 10 raw captures (incl. the WireGuard setup and R2 evidence) lack metadata and index
   entries?

---

### Annex A — Key reference fingerprints (verified in this audit)

- HEAD `794ba31` (2026-09-30T03:00:12Z); clean working tree; all commits authored by build-agent.
- Reviewed archive `fc8b9007f0267bd406658229ad4bee08480fa31953963e655de2643f6bdaac65`
  = `/home/user/falcon-review-delivery-2026-09-29-reviewed.tar.gz` (1,298 entries; digest binds `c312ab7`).
- Closure archive `ef6e9a10e1d0d389714d0a39d1f84401b628eb7775bbf5c82bae218af38abc36` (1,301 entries; binds `f8c2adf`).
- Cited-but-different archive `090d48b31621b38258f259e7421ddf33336b4f03b51d61400bc1211564244ea8` (1,303; binds `14fc64e`).
- Latest delivery `e61025b89c0bb149404f833ffbf2f7c7e84ed30b92ad44677641c35365037429` (2,235; binds `56acec3`).
- Reviewer report digest `bca8349…ad15790` (matches file); adoption digest `313b5fb…154d727` (matches file).
- `PACKAGE_DIGEST.txt`: `review_package_manifest_sha256=053bb99c…`, 2,043 entries;
  `evidence_manifest_sha256=b6fe9b2a…`, 930 entries; chain `publication_chain_failures=0`.
- Closure-era identities: package `4476fc93…` (1,168), evidence `adacd9a1…` (918).

*End of report. All checks were read-only; no repository file, service, credential or
configuration was modified. Credential values were neither read aloud nor printed.*
