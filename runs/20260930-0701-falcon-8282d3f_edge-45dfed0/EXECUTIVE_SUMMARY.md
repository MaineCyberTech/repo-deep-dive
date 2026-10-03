# Executive Summary — Falcon Lab Audit (full-domain run)

**Run:** `20260930-0701-falcon-8282d3f_edge-45dfed0` · **Date:** 2026-09-30 · **Repos:** `falcon-build` @ `8282d3f` (delivered package `3ac6cd4`) and `falcon-edge-build` @ `45dfed0` (moved to `f1c5def` mid-run)

**Bottom line: the lab works, the evidence culture is real, and the release claim is not.** The audit opinion is **GO WITH CONDITIONS** for continuing lab operations, with a hard, time-boxed condition set. The production-readiness claim cannot be relied on at these commits until the release binding, the credential exposure, and the dead-monitor blind spots are fixed. Full detail: `RELEASE_GATE.md`; technical report: `23_executive_summary_release_gate.md`; machine counts: `findings.json`.

## What was audited

This is the first full-domain audit of the falcon lab: 45 source reports (central `falcon-build`, edge `falcon-edge-build`, the shared live host, and the shared delivery directory) plus five cross-cutting lenses (new developer, independent reviewer, integration, live operations, security adversary). It is read-only and evidence-based: every headline claim below is reproduced from artifacts at the recorded commits, not taken on trust. The run also checked the six P0s and 90 findings from the prior lens run (`20260930-0320`) for closure.

**Scale:** 264 findings — **13 × P0, 80 × P1, 131 × P2, 40 × P3** across 36 areas.

**What the audit verified directly (read-only):** the gate aggregate (101 PASS + 1 N/A), the review package (2,067/2,067), the publication chain (0 failures), the edge manifest signature (VALID) and artifact hashes, the pairing mismatch, the verdict-vs-delivery mismatch, the hardcoded closeout response, the committed credential literals with the scanner returning clean, the enrollment→operator and update-apply chains (sandbox reproductions), and live pipeline health (lag, deliveries, disks).

**What it could not verify in the audit role:** container internals, effective firewall/VPN state, root-owned logs and archives, offsite object listings, phone-side delivery, and GitHub server settings — all marked `unverified` in the source reports.

## Headline results by domain

| Area | Verdict |
|---|---|
| Operations (live pipeline) | **Mostly healthy.** Feeds flow with ~2 s lag and 0 drops; alerts deliver on two independent ntfy instances; the daily backup ran; the manual offsite re-run succeeded (1,723 files); the edge sensor is enrolled and reporting. |
| Evidence mechanics | **Genuinely strong.** Manifests recompute (2,067/2,067), the publication-chain verifier reports 0 failures, failures are kept in ledgers, and no fabricated output was found. |
| Approval / release binding | **Broken.** The APPROVED verdict was produced against a different package (`c312ab7`, 1,168 entries) than the one delivered (`3ac6cd4`, 2,067 entries). The reviewed archive itself carries a digest saying `INSUFFICIENT_EVIDENCE`, and `FINAL_RESPONSE.json` hardcodes the opposite of the published verdict. |
| Independent review | **Not independently evidenced.** The "reviewer disposition" is a transcription written by the implementing agent; its digest hashes that transcription file, and the only named person is recorded elsewhere as the system installer. |
| Edge release / pairing | **Does not verify.** The release manifest's checksum sidecar and the central pairing pin name digests that match neither the manifest nor each other; the signed manifest is rewritten in place under a fixed name; nothing checks the pin. |
| Secrets | **Confirmed exposure.** Integration credentials ship in the repo, the review package, and the 2026-09-30 delivery archive while the secret scanner reports clean; the edge CA, operator key, and update-signing seed sit unencrypted in the shared delivery directory; device credentials are baked into images. |
| Monitoring of the monitoring | **Blind in the ways that matter.** The dead-man heartbeat bypasses the alert relay, total-host loss waits up to ~26 h (the 28 Sep outage produced no external notice), stale metrics read healthy, offsite backup failures have no alert, and the edge fleet has metrics but zero alerts. |
| Edge security | **Two reproduced chains.** A single-use enrollment token becomes fleet-wide operator authority in three API calls; the root update path accepts unsigned, agent-written input, including symlink tar members. |
| Backup / recovery | **Partly proven.** Restores and clean-host rebuilds were proven on 23 Sep; offsite retention deletes by stale inventories, the new-services backup has no passing post-fix evidence, and edge PKI/DB backup is local-only. |
| Capacity | **Constrained.** Root filesystem is ~3 GB from its warning threshold with no reclaim plan; the data volume's first signal is a disk guard that has never run. |
| Docs / onboarding | **Drifting.** README/AGENTS describe a pre-closure world; the README quick start fails at step 1 in the delivered tree; there is no document that declares which status artifact is authoritative. |
| Edge fleet / hardware | **Well evidenced.** Pi 3B, RTL8812BU attached and proven, thermal/power within envelope, signed manifest hashes verify; the update swap is not power-loss safe and there is no OS/rollback path. |

## The 11 P0 findings (release-blocking)

| # | ID | What it means in plain English |
|---|---|---|
| 1 | **API-P0-001** | Live-looking integration credentials were committed into the published Wazuh config and shipped in the delivery archive; the scanner cannot see XML-tag credentials. |
| 2 | **EVID-P0-001** | The approval binds a superseded package, and the gate flips plus the "signed" approvals were published in a single agent commit. |
| 3 | **EVID-P0-002** | The independent reviewer is a transcription; the named reviewer is recorded as the installer. |
| 4 | **INV-P0-001** | The edge release manifest digest chain is broken: pin, sidecar, and actual file all disagree. |
| 5 | **INV-P0-002** | Verdict artifacts bind a superseded package, and `FINAL_RESPONSE.json` contradicts `PACKAGE_DIGEST.txt` at HEAD (hardcoded). |
| 6 | **LIVE-P0-001** | The monitoring stack cannot announce its own death: dead-man is relay-blind, total loss waits up to 26 h, stale monitors read healthy. |
| 7 | **LIVE-P0-002** | The green backup screen hides a stale offsite tier; the recovery evidence is uncommitted. |
| 8 | **RES-P0-001** | Offsite backup failures remain invisible to alerting. |
| 9 | **RES-P0-002** | A relay-only alert-path failure is invisible to the dead-man. |
| 10 | **REV-P0-001** | The release approval binds a superseded package; the reviewed archive itself carries a denying digest. |
| 11 | **XREPO-P0-001** | The pairing pin does not verify against the edge release manifest. |

Themes: **binding** (2, 4, 5, 10, 11), **detection** (6, 8, 9), **backup truth** (7, 8), **secrets** (1).

## Strengths worth protecting

- **Evidence discipline is sincere and unusual.** Manifests verify, the publication chain passes, failures are retained rather than rewritten, and the edge review is substantive and honest about its limits (77 PASS / 8 BLOCKED / 3 IE).
- **The review → adoption → verdict separation is the right operating model.** It fails on artifacts and provenance, not on design; fixing it means producing the missing artifacts, not replacing the process.
- **The live monitoring pipeline works** and the core feeds, alerting (dual path), dashboards, and local backups are real, not aspirational.
- **The edge program is disciplined:** 163 automated checks, a validly signed release manifest whose artifact hashes verify, genuine hardware/thermal/power evidence, and working update rejection for a broken bundle.
- **Security foundations are above average for a lab:** default-deny firewall, digest-pinned images, SHA-pinned actions, root-only secret store, single-use tokens, mTLS, and an append-only redaction ledger.
- **Both repos now have real CI**, and the fixes that landed today (offsite, WireGuard persistence) were verified by re-run and a regression check.

## What improved since the prior run

- **Offsite backup:** the `.env` quoting bug was fixed and a manual re-run succeeded (1,723 files, 07:37–07:43Z); the data volume also stabilised (~45–48 GB free).
- **WireGuard:** a bootstrap re-run now preserves the edge peer, with a regression check (the R-30 class problem).
- **Alert noise:** the TLS-silence rule window was tuned to 6 h.
- **Verdict derivation:** `publish_digests.sh` no longer hardcodes `APPROVED`.
- **Edge release tests:** the phase-10 consistency defect is genuinely fixed and green at the current commit.
- **New-services backup:** a missing item now fails the run (`d0f4aaf`).
- **CI:** edge CI expanded (QEMU boot smoke, upstream drift); the edge dashboard was adopted.

**But:** of the prior run's six P0s, **none is verified fixed** (five partially fixed, one still open), and the open P0 set has grown from 6 to 11 as the full-domain sweep looked at places the lens run did not (credentials, pairing, dead-man, backup truth, release chain).

## Owner checklist (the decisions only you can make)

| # | Decision / action | Why it blocks closure | Where recorded |
|---|---|---|---|
| 1 | Disambiguate JPB or appoint a different independent reviewer; record a reviewer-produced disposition | The independence claim cannot close without it | Report 41 / REV lens |
| 2 | Approve or reject edge alert-rule deployment (D-007) | The edge path stays silent without it | XREPO/INTG/OBS findings |
| 3 | Confirm key custody for `backup_enc.key`, the edge CA, and the signing seed | Recovery and fleet trust depend on it | DR-P1-004, SECRET-P1-003 |
| 4 | Approve root reclaim, the data-volume warning band, and a guard drill | Capacity is the nearest operational risk | PERF-P1-001/002, LIVE-P1-001 |
| 5 | Set the total-loss detection target | The current ~26 h window is not a real-time alarm | RES-P1-001, OBS-P1-001 |
| 6 | Record branch-protection acceptance or change the GitHub plan | Required checks stay advisory | Report 34, R-012 |

## What must happen next

**Owner decisions (critical path):** the six items in the owner checklist above — they are the gate's longest lead time.

**Engineering sequence (same day → this month):**
1. **Same day:** rotate the exposed Wazuh credentials; redact with recorded hashes; rebuild the package and delivery; make the scanner catch XML-tag/64-hex credentials.
2. **This week:** re-review/rebind the approval to the delivered package with one derived verdict; freeze the edge release and regenerate the sidecar, pin, and a CI pin verifier; commit the offsite recovery evidence; add offsite/new-services metrics and rules; add the relay canary and monitor-freshness rules.
3. **This month:** close the edge trust ladder (CSR subject pinning, separate operator issuance, symlink-safe/signed root apply, crash-safe update, cert-bound ingest) and deploy scoped edge alerts; fix retention/reclaim; run a verification-only pass and publish `docs/CURRENT_STATE.md`.

The detailed conditions, their finding IDs, and their done-when checks are in `RELEASE_GATE.md`. The audit does not revoke or grant the program's existing verdict; it states the deltas and the reconciliation path, which remains the program's own review/adoption flow.

## How to read this run

- `RELEASE_GATE.md` — the audit opinion and conditions.
- `23_executive_summary_release_gate.md` — the full synthesis with verification results and per-audit verdicts.
- `findings.json` and the risk/backlog tables in this report — machine-readable counts (264 total).
- Domain reports `01`–`44` and `lens_*.md` — evidence and per-finding detail.
- Prior run: `/home/user/repo-deep-dive/runs/20260930-0320-falcon-794ba31_edge-2b5bc8b/`.

**Method and limits:** read-only throughout; live observations were read-only snapshots and probes; reproductions ran in `/tmp` sandboxes or clean clones; secrets are referenced by path/type only. Not verifiable in the audit role: root-owned logs, container internals, effective firewall state, offsite object listings, and GitHub server settings — all marked `unverified` in the source reports.
