# Independent Review — Falcon Edge Sensor (lab)

Reviewer: independent review subagent (not the implementer).
Review window: 2026-09-30 ~03:19Z → 03:40Z (UTC). All work read-only.
Repository reviewed: `/home/user/falcon-edge-build` (HEAD `cfaf09d` at review start; HEAD had moved to
`96c3e08` by review end — see §2 timeline). Delivery dir: `/home/user/falcon-edge-delivery/`.
Device: not touched; all device claims were checked against raw captures plus read-only host-side
observations of the live control plane / exporter / enrolled sensor.

**This review is evidence-first and adversarial.** I sampled 40+ gate/evidence rows across all ten
phases, recomputed the release hashes and signature myself, ran the validators and the test suite,
checked a clean checkout, and reviewed the agent/control-plane/deploy code for real security issues.

---

## Executive summary

| Area | Verdict |
|---|---|
| Evidence integrity (index, hashes, no fabrication) | **HOLDS** — 296/296 indexed captures hash-verified by me at review start (index grew to 298 during the review; validators passed at both points); >40 raw files opened and cross-checked against gate notes; failures and incident windows retained, not hidden |
| CI / validators | `ci/validate.sh` **ALL PASS** at `cfaf09d` and at `96c3e08` (worktree + clean clone); **but `tests/phase10/test_ledger_matches_response` FAILS at `96c3e08`** (`62 != 63`) — the current HEAD is not internally consistent |
| Signed release manifest | **VERIFIED** — sidecar digest OK; 31/31 artifacts SHA-256 + size match; ed25519 signature VALID, keyId `5ea52faf9cf6ee97` matches |
| CycloneDX SBOM | **VERIFIED** — parses, spec 1.5, exactly 714 components (711 deb + 2 application + 1 OS), lab7 image digest embedded, manifest digest matches |
| lab7 image | **INDEPENDENTLY VERIFIED** — `image/verify-pi-image.sh` run by me: 45 PASS / 0 FAIL, sha256 matches `a81b1ff4…` |
| Review package | Verifies internally (756 entries, no caches/outputs, secret scan clean) — but is **incomplete and stale** (missing image pipeline scripts; predates lab7/manifest/phase-9 results) |
| Code/security | **Two significant design weaknesses** found (operator privilege escalation; update-apply root trust), plus several medium/low issues |
| Gate honesty | Mostly good; specific claims challenged (P4-G02 owner flash, P9-G04 approval, stale final response, stale notes). No fabricated results found |
| **Overall** | **CONDITIONAL_PASS for the lab review gates; production readiness remains `INSUFFICIENT_EVIDENCE`.** Conditions listed in §9 |

---

## 1. Scope and method

1. Read AGENTS.md, REPOSITORY.md, all ledgers (`gate_ledger.csv`, `decision_log.md`,
   `exception_register.md`, `contradiction_ledger.md`, `risk_register.md`, `progress_ledger.md`,
   `test_execution.csv`), `closeout/*` and every `docs/phase*/CLOSEOUT.md`/`TEST_PLAN.md`, and the
   pack's acceptance policy (read-only input at `/home/user/Prompts/falcon-edge-sensor-prompt-pack/`).
2. Opened raw `.out` files and `.meta.json` for 40+ evidence IDs and compared them against the
   recorded gate status/notes; listed the weak and unsupported claims (§5).
3. Recomputed every release digest; verified the signature with the in-repo verifier
   (`falcon_common.signing`/`ed25519`); verified the SBOM; verified the review package with the
   in-repo verifier and diffed its contents against `git archive 3101bf0`.
4. Ran `ci/validate.sh`, `ci/check_evidence.py` (normal and `--strict`), `ci/check_decisions.py`,
   the full unittest suite, `tests/phase10`, `automation/evidence/manifest.sh check`, and the
   image verifier (read-only loop mounts, cleaned up — verified no leftovers).
5. Reviewed `src/falcon_control/*`, `src/falcon_agent/*`, `src/falcon_common/*`, `deploy/*`,
   `image/overlay/usr/local/sbin/*`, and the validation/deploy scripts. Reproduced the CSR-subject
   signing behavior in an isolated throwaway CA under `/tmp/opencode/cn-test` (no live mutation).
6. Read-only live checks: control-plane health/sensor list (operator cert), systemd timers,
   node-exporter textfile metrics, host firewall (via `sudo -S` stdin; no mutations).

Boundaries honoured: no repo writes/commits, no service changes, no release/sign flows, no device
mutation, no secret values in this report. Credentials were read only to (a) authenticate read-only
API/system checks and (b) cross-check that repository/history contents do not contain them.

---

## 2. Validators and automated checks — exact results

| # | Command (read-only) | Result |
|---|---|---|
| 1 | `bash ci/validate.sh` @ `cfaf09d` (start of review) | **ALL PASS** — json/yaml, openapi (16 paths/16 ops/30 schemas), models, schemas, decision register, 88-gate ledger, evidence (296 captures + 1 in-progress WARN), secret scan 831 files clean |
| 2 | `python3 -m unittest discover -s tests` @ `cfaf09d` | **Ran 161 tests — OK** (91.5 s) |
| 3 | `python3 ci/check_evidence.py --strict` @ `cfaf09d` | FAIL on one orphan: `evidence/raw/P9-G04/20260930T023848Z_…final.out` (then a 0-byte in-flight capture; see §5/F-06 and note below) |
| 4 | `python3 ci/check_decisions.py` | PASS — 19 decisions, all required areas covered |
| 5 | `bash automation/evidence/manifest.sh check` | PASS — every evidence file matches `evidence/MANIFEST.sha256` |
| 6 | Clean checkout `git archive cfaf09d` → `bash ci/validate.sh` in `/tmp/opencode/audit-head` | **ALL PASS** (F2 absolute-path defect is genuinely fixed; a clean clone at an arbitrary path verifies its own files) |
| 7 | Clean checkout `git archive 96c3e08` → `bash ci/validate.sh` in `/tmp/opencode/audit-head2` | **ALL PASS** — 298 captures verified, secret scan 832 files clean |
| 8 | Same clean archive → full suite | **Ran 161 tests — FAILED (failures=1)**: `test_ledger_matches_response: 62 != 63` |
| 9 | Same clean archive → `tests/phase10` isolated | 7 OK, 1 FAIL (`AssertionError: 62 != 63 : PASS`) — see F-03 |
| 10 | Secret cross-check of full git history (all 84 commits) with the repo's own patterns + the live `.env` values | No private keys, no token values, no `.env` credential values. Matches are expected: PEM header literals in code/allowlist; synthetic negative-test topics; WireGuard **public** keys in early onboarding captures; the wifi SSID and a public Cloudflare hostname appear (not secrets) |

**Timeline / moving target (important).** The repository was **actively being worked on by another
session during this review**:

| UTC | Event |
|---|---|
| ~02:56 | HEAD `cfaf09d` (state when my review started; checks 1–6 above) |
| ~03:29–03:33 | New commits `ced99b3`, `2b5bc8b`, `96c3e08` appeared; `96c3e08` flipped **P9-G04 BLOCKED→PASS** after the 10/10 hard-reset run completed |
| ~03:33 | HEAD `96c3e08`; a new untracked in-flight capture `evidence/raw/P7-G06/20260930T033309Z_recovery-quarantine-drill.out` |
| ~03:37 | `closeout/FINAL_RESPONSE.json` still says 62 PASS while the ledger now says 63 → check 9 fails |

So the "living snapshot" is real, and any statement here is timestamped. At the time of writing,
the current HEAD fails its own phase-10 consistency test (F-03).

---

## 3. Release verification (recomputed from scratch)

Manifest: `/home/user/falcon-edge-delivery/falcon-edge-release-manifest-20260930.json`
(self-consistent: sidecar `9c1021e9…` equals the file hash).

| Check | Method | Result |
|---|---|---|
| Listed artifacts | parse manifest, hash + stat each file | **31/31 SHA-256 and size match**, 0 missing, 0 mismatched |
| Unlisted files on disk | set difference | `falcon-agent-0.1.1-lab.tar.gz` (created 01:50, after the 01:19 signing — F-13/F11-open), root-only secrets backup `.tar.gz` (unreadable to builder; its `.sha256` is listed), manifest + sidecar (self-exclusion), `falcon-logs/` dir |
| ed25519 signature | `falcon_common.signing.verify` over canonical payload, public key derived from `/home/user/falcon-edge-secrets/signing.seed` (0600, never printed) | **VALID**; derived keyId `5ea52faf9cf6ee97` == claimed keyId. No **published** public key exists in the delivery set (F-13) |
| SBOM digest | sha256 vs manifest `sbom.sha256` | matches `e137ad48…` |
| SBOM content | parse | CycloneDX 1.5, `components=714` (711 `pkg:deb` + `falcon-agent`/`falcon-control-plane` + Debian OS), no duplicate names, lab7 image digest in `metadata.component.hashes`, packages collected from the live card (`falcon:packagesSource=ssh`) |
| lab7 image | `.sha256` sidecar + `image/verify-pi-image.sh --expected-sha256` (root, read-only loops) | sha256 `a81b1ff4…` matches; **45 PASS / 0 FAIL / IMAGE VERIFY OK**; loop devices and temp dir cleaned up after |
| Review package `…-20260930003438-3101bf0.tar.gz` | sidecar sha256; in-repo verifier (extract, `sha256sum -c MANIFEST.sha256`, exclusions, secret scan) | sidecar matches; **756 manifest entries verified; no caches; no `image/out`; secret scan 736 files clean; REVIEW PACKAGE OK** |
| Review package completeness | diff vs `git archive 3101bf0` | 1 extra (its own `MANIFEST.sha256`), 8 repo files absent, **0 content mismatches**: `.gitignore`, `evidence/MANIFEST.sha256`, `falcon.pub.pem` (later removed), and **`image/build-pi-image.sh`, `image/verify-pi-image.sh`, `image/enable-unit-in-image.sh`, `image/replace-file-in-image.sh`, `image/validate-nm-profiles.sh`** — the Pi-image pipeline the P4/P10 image claims rest on (F-04) |

There is no separately signed 2026-09-29 manifest; the single signed manifest (2026-09-30) covers
the lab5/lab6 (09-29) and lab7 (09-30) images and their SBOMs/credentials/keys. That matches the
documented release story, but the naming should be stated plainly to recipients.

---

## 4. Sampled gate/evidence checks (40+ gates)

"OK" = I opened the referenced raw `.out` and it supports the recorded status/note.
"Partial" = content supports the core claim but not every phrase in the note.

| Gate | Evidence opened | What the raw capture shows | Verdict |
|---|---|---|---|
| P0-G02 | E-P0-G02-245 | Pi 3B Rev 1.2 `a22082`, 4 cores, 905 MiB, Debian 13/kernel 6.18.50, 32 GB card 04/2022, hashed MACs, wlan1 NetGear A6150 `0846:9055`, services active, `throttled=0x0`, WG peer/route | OK |
| P0-G07 | E-P0-G07-005/006 | redaction self-test + negative/guard tests all PASS | OK |
| P1-G02 | E-P1-G02-012 | lint PASS (14/14/28 at that time; current contract 16/16/30, note refreshed) | OK |
| P1-G05 | E-P1-G05-010 | clock UTC, `System clock synchronized: yes`, NTP active | OK |
| P1-G06 | E-P1-G06-013 | tooling ran; index 11 entries, 0 integrity failures — **but the capture ends `validation: FAILURES PRESENT`** because it flagged itself as an orphan; note says "integrity verified" | Weak citation (F-08) |
| P1-G07 | E-P1-G07-014 | 10 negative checks PASS | OK |
| P2-G01 | E-P2-G01-015 | 3 token-lifecycle tests OK | OK |
| P2-G02 | E-P2-G02-016 | 10 identity/renewal tests OK | OK |
| P2-G03 | E-P2-G03-017 | live mTLS walkthrough: enroll 201, replay 401, heartbeat 202, desired-state signature verified, ACTIVE, port closed on stop, restart persistence | OK |
| P2-G05 | E-P2-G05-019 | 2 desired-state tests OK | OK |
| P2-G07 | E-P2-G07-021 | 36 tests OK | OK |
| P3-G01 | E-P3-G01-022 | hardened unit shown; non-root actor; state/key 0600 | OK |
| P3-G04 | E-P3-G04-025 | 10 queue tests OK | OK |
| P3-G06 | E-P3-G06-027 | 15 directive-verification tests OK | OK |
| P3-G07 | E-P3-G07-028 | 79 tests OK + live agent walkthrough OK | OK |
| P4-G01 | E-P4-G01-282 | lab7 bake output + sha256 + truncated verify (`tail -3`); **45/45 independently reproduced by me** | Claim true; capture weak (F-09) |
| P4-G02 | E-P4-G02-030/031 + EDGE-ONBOARD-062..070 | preflight 9/9 (retry after CP start) + media guards + dry-run. Cited captures are the **image bake/verify/onboard**, not the owner flash or the first boot | **Partial — F-05** |
| P4-G06 | E-P7-G01-243 | SWITCH_SLOT signed/sequenced, slot marker A→B in `lab-simulated` mode, cursor advanced; real slot switch deferred to P7-G05 | OK (disclosed) |
| P4-G07 | E-P4-G07-038 | 95 tests OK + live deploy walkthrough `walkthrough_rc=0` (guard refusals included) | OK |
| P5-G01 | E-P5-G01-158/159/160 | multi-user default, avahi off, sysctls, getty kept, agent active | OK |
| P5-G02 | E-P5-G02-164/166 | zram 905M before the rpi-swap fix; reset/start yields 452M zstd `[SWAP]` prio 100 | OK |
| P5-G03 | E-P5-G03-167 | `wdctl` 30s, Runtime 30s/Reboot 5min drop-in, agent active | OK |
| P5-G04 | E-P5-G04-169/170/171 | default-deny + allowlists, port80 drop / port22 allow; LAN SSH transient then `lan-ssh-ok` ×2; 171 ends in a JSONDecodeError traceback with exit 0 | OK with F-10 (unexplained traceback retained) |
| P5-G05 | E-P5-G05-176/177 | no bootloader EEPROM, `rpi-eeprom-update` refuses, no tryboot markers | OK |
| P5-G06 | E-P5-G06-172 | journald caps + coredumps off applied | OK |
| P5-G07 | E-P5-G07-173/174/175 | cold boot: tunnel 13 s, zram/tmpfs/watchdog/nftables persist, 0 failed units, agent ACTIVE seq 60, post-reboot negatives pass; **undervoltage 0x50005 at that time** (resolved later, R-011) | OK |
| P6-G01 | E-P6-G01-190 | EVE alert:4/dns:4/flow:1060, RSS 54.2 MiB, no pcap; pre-fix rule parse error retained | OK |
| P6-G02 | E-P6-G02-202/203/204 | payload/packet stripped; 90 s outage buffered, 179 records delivered | OK |
| P6-G03 | E-P6-G03-208/209/210 | JSON 5-tuple + AS mapping; spool 0644 after `files_umask 022` | OK |
| P6-G04 | E-P6-G04-263/264 + conclusion | websocket deadlock + legacy TCP never connects (helper alive 4, wlan1 stays managed), source disabled, no pcap, guardrails intact | Blocked state is honest; vendor-failure conclusion is the implementer's interpretation |
| P6-G05 | E-P0-G02-245, E-P9-G05-289, E-P6-G04-218 | adapter identity + monitor-mode 10/10 + 0 wifi errors + power 0x0 | Claim OK; citations still omit removal/station evidence (F-11) |
| P6-G07 | E-P6-G07 + P6-G02/203/204/189 | profile-validator suite + device negatives (payload removal, outage, invalid config) | OK |
| P7-G01/G02 | E-P7-G01-243 | signed manifest offered and recorded t+60 s with heartbeat `update` field; fallback after TTL | OK |
| P7-G06 | E-P7-G06-047 | 3 recovery/quarantine tests OK (new live drill was in-flight during this review) | OK |
| P7-G07 | E-P7-G07-244 | 60 s-TTL manifest served then aged out; heartbeat reverts to valid manifest | OK |
| P8-G01 | E-P8-G01-246/255 | exporter against live DB; 61 `falcon_edge_*` series, scrape error 0, lifecycle metric | OK (also confirmed live) |
| P8-G02 | E-P8-G02-262 | 5 `edge_capture_*` live series (17,261 pkts / 0 drops / age 14 s) | OK (also confirmed live) |
| P8-G03 | E-P8-G03-248 | revoked sensors excluded by fixed selector; stale ACTIVE residue disclosed | OK |
| P8-G04 | E-P8-G04-266 | pre/post fingerprints, `notAfter` +30 d, old cert 403, heartbeat 202, cooldown | OK |
| P8-G06 | E-P8-G06-249 | three tabletop runbooks walked against the live device | OK |
| P9-G01 | E-P9-G01-250 | storage 12% used, card CID, read/write speeds, disk trend | OK |
| P9-G02 | E-P9-G02-288 | offered 1,201,233; NIC delta 1,250,917; Suricata delta 1,250,942 (Δ25); 0 engine drops; 1 NIC drop; 2-min duration declared | OK with declared deviation |
| P9-G03 | E-P9-G03-285/286 | 120 samples/7198 s; temp ≤73.6, mem ≤36.8%, throttled 0x0 all samples; **2 service incident windows (suricata 00:35–00:36, vector 01:02–01:04) retained** | OK (incidents disclosed) |
| P9-G04 | E-P9-G04-290/292 (failed), E-P9-G04-298 (10/10) | attempts 1 failed at reset 1/10; the final run completed 10/10 to ACTIVE with 0 fs errors **during this review** | Result OK; gate flip process issue (F-06) |
| P9-G05 | E-P9-G05-289 | monitor enter/leave 10/10, 0 kernel errors, power 0x0 | OK |
| P10-G02 | E-P10-G02-291/292 + v3 | replication v3 at `e898220`: suite OK, evidence PASS 295, validate ALL PASS, package verified; **independently re-run by me at HEAD: validate PASS, but phase-10 test now fails** (F-03) | OK for F1–F3; superseded by F-03 |
| P10-G05 | E-P10-G05-280/281 | 31-artifact signed manifest + lab7 SBOM | OK |

Additional systematic checks (my own, not gate-specific):

* Re-hashed **all 296 indexed evidence entries** from the CSV → 0 missing, 0 mismatches.
* Gate evidence refs: 88 gates; every strict `E-*` reference resolves except two free-form strings
  (`E-P8-G04`, `E-EDGE-ONBOARD`), consistent with the prior review.
* `ledgers/test_execution.csv`: 296 rows, 287 PASS / **9 FAIL retained** (superseded attempts and
  the P9-G04 failures) — the failed observations are kept, as the doctrine requires.
* Gate counts recomputed from the CSV: at `cfaf09d` **62/0/10/16** (matches the response);
  at `96c3e08` **63/0/9/16** (response not updated → F-03).

---

## 5. Findings by severity

### F-01 — HIGH — Sensor enrollment can be turned into full operator access (CSR subject + CN trust)
**Evidence:** `src/falcon_control/service.py:196-203` (`_resolve_identity`: any CA-signed cert with
`CN=operator` and an unmapped fingerprint becomes the operator role); `src/falcon_control/pki.py:30-59`
(`issue_cert` signs the submitted CSR verbatim — no subject constraints, no extension file);
`service.py:333` (enrollment signs `data["csrPem"]`), `service.py:399` (renewal signs a fresh CSR and
replaces the stored fingerprint).
**Reproduced (isolated, no live mutation):** in `/tmp/opencode/cn-test`, `pki.issue_cert` signed a
CSR with `subject=O=Maine Cyber Tech, CN=operator` unchanged, and the identity resolver returned
`role=operator` for a certificate whose fingerprint is not mapped to a sensor.
**Attack chain (in lab terms):** anyone holding a bootstrap token (e.g., a leaked pre-baked 7-day
claim token, or an operator-issued token) submits an enrollment CSR whose subject is
`CN=operator`; the returned certificate is initially treated as a sensor (fingerprint lookup wins),
but *one renewal* moves the fingerprint to a new certificate and un-maps the `CN=operator` one —
which then authenticates as **operator** (issue tokens/updates/directives, quarantine/revoke
sensors, read the fleet) until it expires. No operator credential is needed.
**Impact:** privilege escalation from device/enrollment-token holder to fleet operator; in
production this is the control plane's root of fleet authority. The same weakness exists for any
CA-signed certificate whose subject is `operator`.
**Recommended fix:** pin sensor certs to fixed subjects (e.g., use the sensor id, generated
server-side, and ignore/override the CSR subject), and authenticate the operator role by something
unforgeable from enrollment (separate intermediate CA / EKU `clientAuth`+`O=operators` policy /
certificate extensions), never by an attacker-supplied CN string. Reopen P2-G02/P2-G03 gates after
the change (signing/identity change reopens affected gates per the pack).

### F-02 — HIGH — The privileged update-apply path trusts an unprivileged, agent-writable request
**Evidence:** `deploy/falcon-update-apply.path` triggers on
`/var/lib/falcon-agent/updates/apply-request.json` (written by the unprivileged `falcon-agent`);
`deploy/falcon-update-apply.service` runs `falcon-apply-update.sh` **as root**;
`image/overlay/usr/local/sbin/falcon-apply-update.sh:37-45` reads `path` and `sha256` from that file;
`:66-72` hashes the file the attacker named; `:76-80` extracts the tarball with
`tarfile.extractall()` (default `fully_trusted` on the device's Python 3.x; only absolute paths and
`..` names are rejected — symlink-member traversal is not); `:90-96` moves the extracted
`falcon_agent/` over `/opt/falcon-edge/src/falcon_agent` and restarts the agent service.
**Impact:** any compromise of the agent process (which is exactly the boundary updates must guard)
yields root code execution: craft a tarball, write your own digest into the request file, let the
path unit trigger the root service. The signed-manifest verification happens only agent-side
(`runner.py:444-521`), so it does not protect the root transaction.
**Recommended fix:** root-side verification (root reads the signed manifest / pinned digest from
root-owned state), constrain `path` to the agent updates dir, `tarfile.extractall(filter="data")`,
verify member types, and treat the request as untrusted input. Add a negative test for a forged
request/path and for symlink/device members. Record as a risk with a rollback note.

### F-03 — HIGH — `FINAL_RESPONSE.json` is materially stale/self-contradictory, and the current HEAD fails the phase-10 consistency test
**Evidence:** `closeout/FINAL_RESPONSE.json` at `96c3e08`:
`commit: "6cad6ec…"` (many commits behind) and `commit_note` says "phases 5-6 in progress";
`labeled_scopes.device_implementation` still says "NOT_EXECUTED: no Raspberry Pi or adapters are
attached; phases 5, 6, 9 … are BLOCKED" while the ledger has 63 PASS including device gates;
`open_gates_summary` still lists P0-G02, P4-G01/G02/G06, P5-G01..G07, P6-G01..G07, P7-G04,
P8-G01/G02/G03/G06, P9-G01..G07 as open; `next_steps_for_owner` still says "attach the Pi" and
"authorize the privileged deployment" after the device was executed and the observability
deployment is live. Counts now disagree with the ledger: response `62 PASS` vs ledger `63` after
`96c3e08` flipped P9-G04 → `tests/phase10/test_ledger_matches_response` **FAILS** in a clean
archive of HEAD (`AssertionError: 62 != 63 : PASS`).
**Impact:** the primary machine-readable closeout artifact misrepresents program state and fails
the program's own consistency test — precisely the failure mode the previous review's F4/C-101
raised, whose remediation `C-106` marks "F4 … remediated". That resolution is overstated: commit
`8fd38b1` changed `device_implementation`, `limitations` and `generated_utc` only; it did not
rewrite the authored scope/open-gate text or the commit field (diff checked).
**Recommended fix:** regenerate the authored fields from the ledger at the current HEAD, re-run
phase-10 + validate, and amend C-101/C-106 accordingly (append-only). Do not present the response
as reconciled until it passes its own test.

### F-04 — MEDIUM — The review package is incomplete (missing the image pipeline) and stale
**Evidence:** `git archive 3101bf0` vs the extracted package: 0 content mismatches but the package
lacks `image/build-pi-image.sh`, `image/verify-pi-image.sh`, `image/enable-unit-in-image.sh`,
`image/replace-file-in-image.sh`, `image/validate-nm-profiles.sh` (the staging list in
`automation/validation/build_review_package.sh` still enumerates only the early buckets). The
package (00:34, `3101bf0`) predates the lab7 image, the 31-artifact manifest/SBOM rebuild, the
phase-9 measurements, the update-apply path, and the remediation commits.
**Impact:** a reviewer holding only the package cannot reproduce the P4-G01/G02 image verification
(the very 45/45 claim this review independently reproduced only because the full repository was
present), and reviews a two-and-a-half-hour-old tree.
**Recommended fix:** extend the staging list to the whole `image/` source (excluding `image/out`),
rebuild the package from the current HEAD, and state package contents limits in the P10-G01 note.

### F-05 — MEDIUM — P4-G02's "owner flash + first boot" PASS is not supported by its cited evidence
**Evidence:** gate row P4-G02 cites EDGE-ONBOARD-062..070, which are the **lab-side** bake,
image-verify, onboarding and service-list captures (06:05–06:23, 2026-09-29); the phase-4 closeout
amendment says "the owner's physical flash on **Windows/Raspberry Pi Imager** and the first boot to
enrollment", and the gate note says "now evidenced, not pending". No capture, meta or owner
decision anywhere in the repo records the Windows/Imager flash (grep found the phrase only in the
two authored texts). The actual first-boot-to-ACTIVE chain exists but is **not cited**:
E-EDGE-ONBOARD-138..143 (bootstrap claims consumed, lab5 enrolled, sensor ACTIVE at 20:55,
2026-09-29).
**Impact:** an owner-side action is asserted as "evidenced" without evidence; the citation set is
wrong for the claim. (The device did boot and enroll — that part is supported by other captures.)
**Recommended fix:** cite E-EDGE-ONBOARD-138..143 for the first boot/enrollment, and record the
owner flash as an explicit owner attestation (or a session record) rather than a capture claim.

### F-06 — MEDIUM — P9-G04 was flipped to PASS during this review without recorded owner approval, inconsistent with P9-G06
**Evidence:** `ledgers/gate_ledger.csv` P9-G04 now `PASS` citing E-P9-G04-298 (10/10 forced resets,
commit `96c3e08`, authored by the implementer). `closeout/OWNER_ACTIONS.md` §2 asks the owner to
"approve the approximation [hard resets] or perform the physical cuts", and `docs/phase9/TEST_PLAN.md`
still says the run is a "lab approximation; physical cuts owner-side". No owner decision entry
exists after D-008. Meanwhile P9-G06 (72 h soak) correctly stays `BLOCKED` pending owner approval
of its alternative. Also note the two earlier attempts (E-P9-G04-290/292, both failing at reset
1/10) remain indexed — good — but the gate note does not mention them.
**Impact:** a hardware/endurance gate closed without the requested owner disposition; the same
substitution is treated as PASS in one gate and approval-blocked in another.
**Recommended fix:** either record the owner's approval of the hard-reset approximation (decision
log) or return P9-G04 to `BLOCKED`/`INSUFFICIENT_EVIDENCE`; mention the failed attempts in the note.

### F-07 — MEDIUM — The agent does not verify the control plane's hostname, and one CA issues both sides
**Evidence:** `src/falcon_common/x509tools.py:113` unconditionally sets
`ctx.check_hostname = False` ("hostname policy is the caller's") and no caller re-enables it
(agent `client.py` uses this context for all API traffic); `server_ssl_context` uses
`CERT_OPTIONAL`; the single lab CA (`pki.py`) issues both the server certificate and sensor
certificates without EKU separation.
**Impact:** an attacker holding **any** CA-signed certificate (e.g., an enrolled sensor key) could
impersonate the control plane to another agent if they can get on-path (WireGuard makes that
hard, and the CA is lab-only — hence MEDIUM, not HIGH). A production design should pin the server
identity (hostname/SAN) and separate server/client issuance profiles.
**Recommended fix:** enable hostname/SAN verification against the configured control-plane name,
add EKU separation in the PKI, and document the trust model.

### F-08 — LOW — P1-G06's PASS cites a capture that ends in a failing validation
**Evidence:** E-P1-G06-013 contains `FAIL raw artifact without metadata …`
`validation: FAILURES PRESENT` (it detected itself as an in-flight orphan), while the gate note
says "integrity verified". The tooling has since been changed to WARN for in-progress captures and
current runs are green (verified in §2), so this is a citation/annotation defect, not a false gate.
**Fix:** annotate the gate (append-only) with a current green run reference.

### F-09 — LOW — P4-G01 lab7 "45/45" evidence is truncated (`tail -3`) though the claim is true
**Evidence:** `evidence/raw/P4-G01/20260930T011338Z_lab7-bake-and-verify.out` shows only the last
verifier line + `IMAGE VERIFY OK`; the meta records the command as `… | tail -3`. I re-ran the
verifier independently: **45 PASS / 0 FAIL**. **Fix:** capture the full verifier output on the
next image build; the current claim stands on my reproduction.

### F-10 — LOW — P5-G04 raw negatives contain an unexplained traceback (F9 from the prior review, unresolved)
`E-P5-G04-171` ends with a Python `JSONDecodeError` traceback although the session's exit code is 0;
the LAN-SSH timeout transient in 169 is real and was later `lan-ssh-ok` (170), but the ledger's
"documented in the capture" phrasing overstates what the raw files contain. The gate outcome still
holds (negatives pre/post reboot). **Fix:** add an interpretation note and/or fix the tolerant helper.

### F-11 — LOW — Stale notes/citations that the F7/F8 remediation did not catch
* P8-G03 note says "8 rules"; `config/prometheus/edge-alerts.yaml` now has **10** (capture-drop and
  queue-age rules added).
* P10-G07 note says "130 tests" (capture) while the current suite is 161.
* P10-G05 note says "lab6 image digest embedded"; the embedded digest is lab7.
* P6-G05 citations still do not include the adapter-removal/station-mode captures (the claim is
  true from other indexed captures).
**Fix:** append-only note refresh.

### F-12 — LOW — `falcon_edge_sensor_pending_directives` counts expired directives forever
`automation/observability/fleet_metrics.py:61-62` counts `directives WHERE consumed_at IS NULL`;
`store.consume_directive()` (`store.py:323-326`) is **never called**, so the gauge is cumulative
and includes expired rows — live value is 2 for the sensor although both stored directives expired
at 00:13/00:14 on 2026-09-30 (read-only DB check). No alert uses the metric (dashboard-only today).
**Fix:** filter `expires_at > now` in the exporter (and/or have the agent ack directives).

### F-13 — LOW — Release verification is not self-contained, and the agent bundle is unmanaged
The signed manifest does not publish the ed25519 **public key** (no `.pub` artifact anywhere in the
delivery dir), so an independent verifier cannot check the signature from the release set alone —
I could only verify it because the secret store (seed) was present. The `falcon-agent-0.1.1-lab.tar.gz`
update bundle (created after signing, and used by the live update drill) is still not in the signed
manifest (prior review F11 open).
**Fix:** publish `signing.pub.pem` + keyId next to the manifest; rebuild/re-sign the manifest over
the complete delivery set (minus self-references) at the next release.

### F-14 — LOW — Delivery/secret hygiene
The delivery dir contains private SSH keys, credential files, and **unencrypted secrets backups**
(CA key + signing seed + DB; one root-owned 0600, one user-owned 0600). Their hashes are in the
signed manifest. R-007 covers the card; the backup practice should be explicitly risk-accepted or
encrypted. Also a 0-byte root-owned `control.db` residue sits in the secrets dir.

### F-15 — LOW — Capture wrapper exports the whole credential file into the captured command's environment
`automation/evidence/capture.sh:63-75` sources `/home/user/.env` with `set -a` before the `--sudo`
capture, so every credential is exported into the child's environment (the redaction statement
says "credential material is supplied via stdin only"). Practical leak risk is low (sudo resets
env; the wrapper doesn't dump env), but the statement is imprecise and a command that prints its
environment would leak. **Fix:** pass only the needed variable to `sudo -S` via a subshell.

### F-16 — INFO — Minor code/hygiene items
`src/falcon_control/pki.py:98-107` defines `client_ssl_context` twice; `http_server._dispatch`
parses `Content-Length` without validation (a malformed header can raise before the handler);
`parse_iso` on heartbeat fields can raise on schema-passing-but-malformed values; the risk register
has **duplicate IDs R-008/R-009** and the exception register EX-001 is stale (the Pi has since
been attached and executed most hardware gates).

---

## 6. Code/security review notes (beyond the findings)

* **Control plane authn/authz** — route table + role checks are sound in structure: public
  healthz, operator routes, sensor routes with path/identity matching (mismatch quarantines the
  presenting identity), bootstrap-token route, and the Vector ingest route documented as
  certificate-only. Idempotency keys are validated (16–128 chars) and replayed only on body-hash
  equality; heartbeat sequencing + clock-skew ≈ 5 min; config blocked in quarantine/revoked states.
  All SQL is parameterized. Weak points: the operator role derivation (F-01), `CERT_OPTIONAL` at
  TLS (by design for bootstrap) and no rate limiting (lab-grade, disclosed).
* **Agent** — signed-artifact verification (signature, keyId, expiry, revision/sequence
  monotonicity) is well-structured and negative-tested; update downloads verify digest+size
  (hostname-checked HTTPS) before staging; rotation commits only on success with cooldown and a
  renewal-due fallback. The trust boundary failure is at the privileged apply step (F-02).
* **Deployment** — units are least-privilege for the agent (`ProtectSystem=strict`,
  `ReadWritePaths`, capability-empty, memory/CPU bounds); the control plane unit is similarly
  confined. Alert-rule deployment is correctly gated (dry-run default; "not additive" warning;
  rollback printed) and left undeployed pending an owner decision — consistent with D-007.
* **Secret handling** — good: no secret values in the repo worktree or in history (my scans),
  keys/certs 0600/0640 as designed, capture redaction works for the common patterns; the noted
  exceptions are F-13/F-14/F-15 and the recorded public-key occurrences in early onboarding
  evidence (public keys only).
* **Kismet block** — the large, consistent negative evidence set supports "cannot bind the source
  with this vendor build on this platform"; the gate is correctly left BLOCKED. I did not
  independently reproduce the helper deadlock (would require device mutation).

---

## 7. Gate-support assessment

**Verified as supported by real evidence (spot-checked):** P0-G02, P0-G07, P1-G02/05/07, P2-G01/02/03/05,
P3-G01/04/06/07, P4-G01 (independently re-verified), P4-G06 (lab-simulated, disclosed), P4-G07,
P5-G01..G07, P6-G01/02/03/05/07, P6-G04 (blocked, honest), P7-G01/02/06/07, P8-G01..G06,
P9-G01/02/03/05, P10-G05, P10-G07 (software).

**Challenged / conditional:** P4-G02 (F-05), P9-G04 (F-06), P1-G06 (F-08), P4-G01 citation (F-09),
P6-G05 citations (F-11), P10-G01 (stale/incomplete package — its current status is already
`INSUFFICIENT_EVIDENCE`, correctly), P10-G02 (fixed F1–F3 verified, but see F-03), P10-G03
(remediation overstated — F-03/F-04).

**Blocked gates (current HEAD):** P6-G04 (Kismet), P6-G06 (MT7612U), P7-G05 (A/B boot),
P9-G05 (MT7612U/reviewer), P9-G06 (72 h soak), P9-G07 (device negatives), P10-G02 (clean system),
P10-G04 (owner acceptance), P10-G06 (production change) — all appear genuinely blocked, with
prepared artifacts and honest notes. No gate is claimed PASS while unexecuted, with the P4-G02 and
P9-G04 caveats above.

**What the implementer got right:** append-only discipline is real (failure attempts, incident
windows, and superseded captures are retained and indexed); the device-evidence chain is
consistent; the lab/not-production framing is repeatedly stated; the previous review's F1/F2/F3
remediation is genuine (I re-ran it); no fabricated results were found.

---

## 8. Residual risks an independent reviewer should still challenge

1. **Production crypto**: pure-Python Ed25519 (not constant-time), one signing key for desired
   state/directives/release manifest, lab CA with no EKU separation; no HSM; key custody is a file
   in a user secrets dir.
2. **Fleet authority single point**: F-01 means token issuance/consumption is not an adequate
   boundary for operator authority; F-02 means the update mechanism's root step trusts the
   component being updated.
3. **Unfinished hardware certification**: MT7612U (production candidate) untested; Kismet wireless
   capture unexecuted (so the wireless metadata row of the capture-quality contract has no device
   data); A/B boot impossible on 3B (reflash-based recovery only); 72 h soak not run; the
   packet-drop budget ran 2 min (declared) and the single 10k pps point was aligned, not the
   15-minute certification.
4. **Divergence between the live card and the reflash artifact**: the live Pi runs newer code
   (cert auto-renewal, Suricata stats profile, update apply path) than lab7 (the update apply path
   is not in any image, per OWNER_ACTIONS §8). "lab7 matches the live card's code" is true only for
   the earlier build-outs, not the update path.
5. **Reviewability**: the released review package lacks the image tooling (F-04) and the manifest
   does not carry the public key (F-13); a third party cannot currently reproduce or verify the
   release end-to-end from the delivered set alone.
6. **Observability**: alert rules remain undeployed by decision; one live metric
   (`pending_directives`) is wrong (F-12); stale-retired sensors are cleaned but the DB still
   carries historical test sensors.

---

## 9. Conditions to close the review gates (suggested dispositions)

| Gate | Suggested disposition | Conditions |
|---|---|---|
| P0-G08 … P9-G08 closeouts | **CONDITIONAL_PASS** (as prior review) | Keep; append the P4-G02 citation fix and P9-G04 disposition |
| P10-G01 review package | **INSUFFICIENT_EVIDENCE** (unchanged) | Rebuild from current HEAD including the full `image/` source tree; re-verify |
| P10-G02 clean replication | **INSUFFICIENT_EVIDENCE** (as now) | Re-run at the final HEAD after F-03 is fixed; keep the clean-checkout caveat |
| P10-G03 finding remediation | **INSUFFICIENT_EVIDENCE** | Fix/remediate F-03 (final response), F-04, and the F-08–F-16 items, with evidence; then independent re-verification |
| P10-G05 release manifest/SBOM | **CONDITIONAL_PASS** | Publish the signing public key; re-sign over the complete delivery set (agent bundle); note the credentials in scope |
| P10-G08 program closeout | **CONDITIONAL_PASS** | Make `FINAL_RESPONSE.json` consistent and green at HEAD (F-03) |
| Production transition | **INSUFFICIENT_EVIDENCE** | Owner acceptance, production crypto/SBOM decisions, F-01/F-02 remediations, MT7612U certification, 72 h soak/owner alternative, alert-rule disposition |

---

## 10. Open questions (for the owner / implementer)

1. Was the P9-G04 hard-reset approximation approved by the owner anywhere outside the repository?
   If yes, archive the decision; if no, revert the gate to BLOCKED (F-06).
2. Was the card really flashed with Raspberry Pi Imager on Windows, and by whom/when? If it was
   done in-session on the lab host, the P4-G02 note and phase-4 amendment need an append-only
   correction (F-05).
3. Who is the ED-19 independent reviewer/acceptance authority? (All review gates are owner-blocked.)
4. Why does the review package staging list still exclude the Pi-image scripts — was that
   intentional, and what should a package-only reviewer do about P4-G01/G02? (F-04)
5. Where should downstream verifiers obtain the release signing public key? (F-13)
6. Should the owner accept the unencrypted secrets backups in the delivery dir, or require
   encryption/off-host storage? (F-14)

---

## Appendix A — Commands run (selected, read-only)

```
bash ci/validate.sh                          # @cfaf09d ALL PASS; @96c3e08 ALL PASS (1 in-progress WARN)
python3 -m unittest discover -s tests        # @cfaf09d OK 161; @96c3e08 clean archive FAILED (1: 62!=63)
python3 ci/check_evidence.py [--strict]      # PASS / FAIL on in-flight orphan (expected)
python3 ci/check_decisions.py …              # PASS
bash automation/evidence/manifest.sh check   # exit 0
git archive <commit> | tar -x -C /tmp/...    # clean-checkout replication (F2 verified)
sha256sum -c falcon-edge-release-manifest-20260930.json.sha256   # OK
python3 (manifest parse + hashlib loop)      # 31/31 artifacts OK
python3 (falcon_common.signing.verify)       # signature VALID, keyId match
python3 (CycloneDX parse)                    # 714 components, 711 deb, 0 dupes
bash image/verify-pi-image.sh --image lab7 --expected-sha256 …   # 45/45 PASS (via sudo -S stdin)
bash automation/validation/verify_review_package.sh …3101bf0…    # REVIEW PACKAGE OK (756 entries)
python3 (package vs git-archive diff)        # 8 source files missing, 0 mismatches
python3 (write-time evidence index re-hash)  # 296/296 OK
python3 (git history + live .env value scan) # no secrets in history/worktree
curl --cert operator.crt.pem … /api/v1/sensors                   # live sensor list (read-only)
systemctl is-active / list-timers, nft list ruleset, /srv metrics # live state (read-only)
```

## Appendix B — Artifact reference table

| Artifact | Value |
|---|---|
| Manifest | `falcon-edge-release-manifest-20260930.json` sha256 `9c1021e9…`, generated 2026-09-30T01:19:54Z, commit `14e7c70`, 31 artifacts |
| Signature | ed25519, keyId `5ea52faf9cf6ee97`, VALID |
| SBOM | `falcon-edge-sensor-2026.09.30-lab7-sbom.cdx.json` sha256 `e137ad48…`, 714 components |
| Image | `falcon-edge-sensor-2026.09.30-lab7-arm64.img.xz` sha256 `a81b1ff4…`, verify 45/45 |
| Review package | `…-20260930003438-3101bf0.tar.gz` sha256 `256d1ce6…`, 756 manifest entries, still pre-remediation/lab7 |
| Repo HEAD at review start / end | `cfaf09d` / `96c3e08` (moving; concurrent session) |

*All findings above are my own observations from the commands and files cited; anything I could not
run or reproduce is marked as such. The device was not touched.*
