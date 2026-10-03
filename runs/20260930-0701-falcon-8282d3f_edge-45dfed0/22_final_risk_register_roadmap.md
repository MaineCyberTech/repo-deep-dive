# Final Risk Register, Roadmap, and Patch Plan

## Audit Metadata
- Audit name: repo-deep-dive (`falcon-lab` profile, pack v1.2.1, full-domain) · Run: `20260930-0701-falcon-8282d3f_edge-45dfed0`
- Repositories: `falcon-build` @ `8282d3f` (`main`, clean at run start) · `falcon-edge-build` @ `45dfed0` (`main`, dirty — in-flight CI work)
- Live host: shared lab host, read-only snapshot `live_snapshot.txt` (2026-09-30T07:01:55Z); delivery dir `/home/user/falcon-edge-delivery`
- Generated at: 2026-09-30T16:05Z · Auditor: prompt-22 synthesis subagent (read-only) · Area code: FINAL
- Output path: `docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/22_final_risk_register_roadmap.md`
- Companion artifacts: `risk_register.md` (256 rows), `roadmap.md`, `patch_plan.md`, `findings.json`, `audit_manifest.json`
- Scope limitations: synthesis from run reports + targeted read-only checks; no new source code review; edge repo at `45dfed0` (in-flight `f1c5def` noted by reports); no live mutation; secrets never printed (paths/types only); severity/owner/effort inherited from each finding's source section.

## Scope
Reviewed all 48 run reports (43 domain/adapted + 5 lens), the 256-finding `findings.json`, prior-run comparison (90 findings, run `20260930-0320`), duplicate/cross-reference relationships, severity/status aggregation, owners/effort/dependencies, quick wins, 7/30/60/90-day windows, patch sets, validation commands, and accepted/deferred risks. The 10 not-applicable prompts (`04`, `05`, `17`, `25`–`29`, `37`, `39`) were reviewed for exclusion handling only. Not reviewed: third-party internals, out-of-repo Cloudflare/Grafana/DO configuration beyond cited evidence, physical hardware beyond reported bake/probe evidence, and any implementation. No finding was closed by this report.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `findings.json` | machine artifact | Authoritative 256-finding set | Reconciled 1:1 to the register |
| `audit_manifest.json` | machine artifact | Scope, N/A list, counts, wiring/verification | `verification.mode=false`; counts match |
| 43 domain reports (`01`–`44`) | reports | Per-domain evidence | P0/P1 sections cross-checked |
| 5 lens reports | reports | Operator/reviewer/security/integration views; reproduced chains | Cross-referenced rather than re-filed |
| Prior run `20260930-0320` register/roadmap | reports | Stale-row and duplicate detection | Statuses re-verified at current commits |
| `live_snapshot.txt` | snapshot | Live state (disk, timers, containers, ports) | Read-only, 2026-09-30T07:01Z |
| `follow_up_register.md` | artifact (sibling synthesis) | Post-audit tracking | Statuses are assertions, not closure |
| Delivery dirs / `git status` | live evidence | Backup, secret and evidence binding | Read-only checks |
## Verification Performed

| Ref | Check | Result | Notes |
|---|---|---|---|
| V1 | Recount `findings.json`; compare with manifest | **Supported** | 256 = 11 + 74 + 131 + 40 = manifest counts; 10 N/A prompts (`04`, `05`, `17`, `25`–`29`, `37`, `39`) excluded and stated |
| V2 | 1:1 register reconciliation | **Supported** | 256 rows; severity filters give 11/74/131/40 |
| V3 | Trace every register row to its source section | **Partially supported** | 250/256 impact and 252/256 fix fields parsed; 8 compact sections read manually; all rows cite `report §id` |
| V4 | Run `python3 ci/validate.py` at HEAD with the run folder present | **Reproduced failure** | exit 1 — secret scan `long_hex` ×3 on report lines (commit SHAs); corroborates `CI-P2-001`, `HYGIENE-P2-001`, `REV-P2-002` |
| V5 | Edge `ledgers/risk_register.md` duplicate-ID check | **Reproduced** | Two `R-008` and two `R-009` rows; `R-011` cites "R-008 resolved" ambiguously (`INV-P2-001`) |
| V6 | `git status` evidence-binding check (falcon) | **Reproduced** | Modified 0-byte offsite capture; untracked meta + `docs/audits/` — matches `LIVE-P0-002`/`RES-P0-001` |
| V7 | Verification-mode state | **Unsupported to close** | `verification.mode=false`, `fixedFindings=[]` — no finding is `verified-fixed` |
| V8 | Prior-run status re-check | **Supported (still-open)** | Multiple prior P1s open at these commits (lens R6: `REV-P1-004/005`, `REV-P2-007`, `REV-P3-010/011`, `INTG-P1-003`) |
| V9 | Aggregate arithmetic | **Partially supported** | Phase-9 aggregate omits `NOT_APPLICABLE` (`EVID-P2-001`); findings/digest counts otherwise reconcile |
## Executive Summary
The evidence surface is unusually complete: every finding traces to a named file/line/command, the lenses reproduced the two most dangerous chains, and the 256-finding set reconciles (48 reports; 10 N/A prompts stated; lenses cross-referenced rather than inflating counts). That strength is also the finding. The program's instrument of record does not bind the bytes it claims: approval and verdict artifacts disagree with the delivered digest and reviewed archive, and live credentials were shipped through a scanner blind to them. Two release-blocking chains are open — approval/binding (`EVID-P0-001/002`, `INV-P0-002`, `REV-P0-001`, `XREPO-P0-001`, `INV-P0-001`) and credential exposure/scanner blindness (`API-P0-001`, `EVID-P1-004`, `SC-P1-001`). The live system's last lines of defence are blind to their own failure: relay-blind alerting with up to ~26 h host-loss detection (`LIVE-P0-001`, `RES-P0-002`) and a backup gauge that proves only the local snapshot (`LIVE-P0-002`, `RES-P0-001`) — both already realized (2026-09-28, 2026-09-30). Next actions: freeze releases and close patch set 1; fix the identity/trust ladder (set 2); stand up detectors with firing proofs (sets 1/4/6); make the run artifacts pass the mandated gate (set 3); refresh stale entry docs (set 5).

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Findings set | `findings.json` | Machine-readable findings | 256, reconciled | Medium | No owner/effort/status/cluster fields |
| Register | `risk_register.md` | All rows with owner/effort | This run | Low | Condensed from sources |
| Roadmap | `roadmap.md` | P0–P3 + deferred | This run | Low | All IDs referenced |
| Patch plan | `patch_plan.md` | 7 sets + validation + DoD | This run | Low | Explicit membership |
| Summaries | `EXECUTIVE_SUMMARY.md`, `RELEASE_GATE.md`, `23_…` | Audience views | Sibling agents | — | Cross-read only |
| Follow-up register | `follow_up_register.md` | Post-audit tracking | Exists | Medium | Statuses unverified (V7) |
| Run manifest | `audit_manifest.json` | Scope/wiring/verification | `verification.mode=false` | Medium | No closure pass |
| Pack tooling | `/home/user/repo-deep-dive/tools/` | Validation/collection scripts | Present in pack | Low | Referenced by `INDEX.md` |
## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| All previous reports | 3 | 48 reports; all prompts covered or N/A | Stale status lines; run folder fails gate (V4) | Sets 3/5/7 |
| P0/P1 risks | 2 | 11 P0 + 74 P1, reproduced chains | No closure artifacts; approval unreproducible | Set 1 first |
| Duplicate findings | 4 | Cross-reference discipline; clusters identifiable | No machine clustering | Add `cluster`/`canonical` |
| Cross-cutting themes | 4 | Consistent themes across reports | Manual synthesis | Keep cluster map current |
| Quick wins | 4 | 113 S-effort findings with exact files | Unscheduled | Execute in sets 1/5 |
| 7/30/60/90-day plans | 4 | `roadmap.md` windows for all IDs | Owner sign-off pending | Confirm at M1 |
| Patch sets | 4 | 7 sets, 256 IDs assigned once, DoD | Not reviewed/merged | Owner sign-off on set 1 |
| Validation commands | 3 | Chain/delivery verifiers + drills | Gate failing; no firing proofs | Sets 1/3/6 |
| Owners/effort/deps | 4 | falcon 122, edge 59, both 44, owner 18, falcon/ops 13; S 113, M 113, S/M 26, M/L 2, L 2 | `both` accountability unclear | Name one owner per item |
| Accepted/deferred risks | 2 | EX register + prose acceptances | Unreconciled; verdict cites missing rows | Set 7 + owner review |
## Detailed Review
Per-item scope detail is in `risk_register.md` (rows), `roadmap.md` (windows) and `patch_plan.md` (changes/tests/docs).

| Item in scope | Evidence | What it does / current state | Gap | Recommended improvement | Suggested tests / docs |
|---|---|---|---|---|---|
| All reports | 48 reports; `findings.json` | One 256-finding set; domains file, lenses consolidate | No clustering/derivation | Generate register from findings | Reconciliation test; update `INDEX.md` |
| P0/P1 risks | 11 P0 + 74 P1 rows; lenses R1–R6 | Release blockers + live detector gaps; token→operator→root reproduced | No closure artifacts | Patch sets 1–2 under freeze | Chain equality; escalation negatives |
| Duplicate findings | Appendix clusters | 86/256 share root causes | No canonical IDs | Merge at fix time per cluster | Cluster uniqueness test |
| Cross-cutting themes | Themes below | Binding, secrets, blindness, ladder, stale docs | No theme owner | Theme owners in review | Drift checks; firing proofs |
| Quick wins | 113 S findings | High trust payoff, small diffs | Unscheduled | Batch in sets 1/5 | Per-finding validation |
| 7/30/60/90-day plans | `roadmap.md` | All IDs windowed; dependencies noted | Owner acceptance | Enforce dependency order | Milestones M1–M5 |
| Patch sets | `patch_plan.md` | 7 sets, explicit membership, DoD | PR process not wired | One PR per set | Per-set validation |
| Validation commands | V4 + drill list | Machine checks + manual drills | Gate red; no proofs | Validation Plan steps 1–10 | Captures per drill |
| Owners/effort/deps | Register summaries | All 256 mapped | `both` items can stall | Name accountable owner at M1 | Decision-log entries |
| Accepted/deferred risks | EX register; OD-17 mismatch | Keeps accepted risk visible | Not reconciled | Reconcile + expiry review | Register-vs-verdict diff |
## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| FINAL-001 | All reports aggregated | `findings.json`; 48 reports | One authoritative set | No machine clustering | P2 | Derive register from source |
| FINAL-002 | P0/P1 release blockers | 11 P0 + 74 P1 | Evidence-backed, reproduced | No closure artifacts | P0 | Set 1 freeze + rebind |
| FINAL-003 | Duplicate findings | Appendix clusters | Cross-reference discipline | No canonical IDs | P2 | Add cluster fields |
| FINAL-004 | Cross-cutting themes | Detailed Review table | Report-level narratives | No theme owner | P2 | Theme owners |
| FINAL-005 | Quick wins | 113 S-effort findings | Listed | Unscheduled | P3 | Execute sets 1/5 |
| FINAL-006 | 7/30/60/90-day plans | `roadmap.md` | Full ID coverage | Owner sign-off | P2 | Confirm at M1 |
| FINAL-007 | Patch sets | `patch_plan.md` | Membership + DoD | PR process | P2 | One PR per set |
| FINAL-008 | Validation commands | V4 failure; drills | Machine + manual checks | Gate red; no firing proofs | P1 | Fix gate; capture proofs |
| FINAL-009 | Owners/effort/deps | Register summaries | All mapped | `both` accountability | P2 | Single owner per item |
| FINAL-010 | Accepted/deferred risks | EX register; OD-17 | Prose + register | Unreconciled | P1 | Reconcile + expiry review |
## Findings

### Finding ID: FINAL-P0-001 - The release cannot be approved or delivered on current evidence
- Severity: P0 · Confidence: High · Area: FINAL (aggregate)
- Evidence: 11 P0s in `findings.json`; `EVID-P0-001`/`INV-P0-002`/`REV-P0-001` (approval binds superseded package; `PACKAGE_DIGEST.txt` vs `FINAL_RESPONSE.json` disagree); `API-P0-001` (credential literals delivered, scanner blind); `INV-P0-001`/`XREPO-P0-001` (pin/sidecar/manifest disagree).
- What is happening: approval/binding integrity and credential exposure are open simultaneously, alongside unmonitored live defence paths.
- Why it matters: any consumer of the verdict or package is misinformed; any release inherits the failure.
- User/business impact: unearned approval; credential-compromise surface. Security/privacy/reliability impact: governance and confidentiality failure.
- Recommended fix: freeze; execute patch set 1 (rotate/redact → rebuild → rebind); close set 2 identity prerequisites before re-review.
- Suggested validation: `verify_publication_chain.sh` = 0 failures; CI equality verdict↔digest↔packet; scanner negatives; drill alerts. · owner (approval) + falcon (artifacts) · Effort: M · Dependencies: set 2 rotation/custody · Status: open

### Finding ID: FINAL-P0-002 - Live protection cannot detect its own failure
- Severity: P0 · Confidence: High · Area: FINAL (live operations aggregate)
- Evidence: `LIVE-P0-001`/`RES-P0-002`/`OBS-P1-001` (relay-blind heartbeat; 26 h watcher; stale monitors healthy); `LIVE-P0-002`/`RES-P0-001`/`DR-P1-001` (offsite failure invisible; recovery evidence uncommitted — V6); realized 2026-09-28 and 2026-09-30.
- What is happening: the monitoring and backup paths lack detectors exactly at their own failure points.
- Why it matters: security events during alerting outages are missed; host loss during silent offsite outages loses the delta.
- User/business impact: hours-to-a-day MTTD (realized); overstated recoverability. Security/privacy/reliability impact: alerting and data-protection assurance failure.
- Recommended fix: independent-instance canary + freshness rules; offsite/new-services gauges + 36 h rules; commit recovery evidence; drill both.
- Suggested validation: stop relay 15 min → canary; force offsite failure → one alert per path. · falcon/ops (+ owner threshold) · Effort: M · Dependencies: DO/offsite access · Status: open

### Finding ID: FINAL-P1-001 - Machine-readable findings lack register/roadmap classification fields
- Severity: P1 · Confidence: High · Area: FINAL (tooling)
- Evidence: `findings.json` = `{id, severity, title, report, line}`; synthesis parsed 48 reports to derive impact/fix/owner/effort (V3).
- What is happening: status/owner/effort/impact live only in prose; every aggregate re-derives them.
- Why it matters: registers drift; automation cannot filter or assign. Impact: manual cost and drift risk per re-run.
- Recommended fix: emit `status`, `owner`, `effort`, `impact`, `cluster`/`canonical` from the collector.
- Suggested validation: register generated with zero manual overrides; schema test. · Owner: falcon · Effort: S · Status: open

### Finding ID: FINAL-P1-002 - Stale-but-open statuses persist across prior findings and registers
- Severity: P1 · Confidence: High · Area: FINAL (status integrity)
- Evidence: `REV-P2-003` (prior edge P1 fixes absent at current commit); lens R6 still-open list; `INV-P2-001` duplicate R-008/R-009 (V5); `EVID-P2-003` unreconciled exception/contradiction registers.
- What is happening: register/doc statuses are not reconciled against code and current evidence.
- Why it matters: operators/agents act on wrong state; "resolved" claims are ambiguous. Impact: rework; missed risk.
- Recommended fix: append-only reconciliation rows with current-commit evidence; disambiguate IDs; close loop in `follow_up_register.md`.
- Suggested validation: status-vs-code test for security findings; duplicate-ID check. · Owner: falcon + edge · Effort: M · Status: still-open

### Finding ID: FINAL-P1-003 - The audit run artifacts currently fail the repository's mandated gate
- Severity: P1 · Confidence: High · Area: FINAL (run hygiene)
- Evidence: V4 reproduced — `ci/validate.py` exit 1 with 3 `long_hex` hits on report lines; `git status` shows untracked `docs/audits/`; corroborates `CI-P2-001`, `HYGIENE-P2-001`, `REV-P2-002`.
- What is happening: writing a run in-tree makes the gate red (long SHAs read as secrets); run-folder lifecycle undefined.
- Why it matters: "`ci/validate.sh` must pass" cannot hold while audits live in-tree. Impact: blocked commits; noisy gate.
- Recommended fix: define run-folder lifecycle (gated exclusion or out-of-tree runs); tighten scanner allowlists to digest lines.
- Suggested validation: gate passes with the run folder present; negative test still catches a real 64-hex secret. · Owner: falcon · Effort: S · Status: open

### Finding ID: FINAL-P1-004 - No verification pass has run; no finding can be closed yet
- Severity: P1 · Confidence: High · Area: FINAL (closure integrity)
- Evidence: manifest `verification.mode=false`, `fixedFindings=[]`, `verificationLog=null`; `wiring.gateMutation=none`; `follow_up_register.md` is assertion-based.
- What is happening: findings exist without closure evidence. Why it matters: the shared rules forbid closing without an artifact at the then-current commit.
- Impact: readers may treat follow-up notes as closure. Recommended fix: schedule verification-only passes per patch set; populate the manifest block.
- Suggested validation: each closed finding cites a capture at the current commit. · Owner: owner + falcon · Effort: M · Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Release approved for unreviewed bytes | P0 | High (already true) | Governance failure | EVID-P0-001, REV-P0-001 | Set 1 rebind/re-review |
| Credential abuse from shipped literals | P0 | Medium-High | Account/cluster compromise | API-P0-001, EVID-P1-004 | Rotate + scanner fix |
| Silent alert-path death | P0 | Medium | Missed pages | LIVE-P0-001, RES-P0-002 | Canary + freshness rules |
| Silent offsite staleness | P0 | Medium (realized) | Data-protection loss | LIVE-P0-002, RES-P0-001 | Gauges + 36 h rules |
| Token→operator→root escalation | P1 | Medium | Fleet-wide control | SEC-P1-001/002, ADV-P1-001 | Set 2 identity/root fixes |
| Edge fleet unalertable; update not crash-safe | P1 | Medium | Fleet blindness | RES-P1-003, FLEET-P1-002 | Deploy rules; A/B rollback |
| Capacity exhaustion | P1 | Medium | Platform outage | PERF-P1-001/002, LIVE-P1-001 | Reclaim + warning band |
| Stale docs drive wrong response | P1 | High | Prolonged outage | INFRA-P1-001, LIVE-P1-002 | Non-root runbook walk |
## Recommendations

### Immediate / Release Blocking
- Freeze releases; execute patch set 1 (`API-P0-001`, `EVID-P0-001/002`, `INV-P0-001/002`, `REV-P0-001`, `XREPO-P0-001`, `LIVE-P0-001/002`, `RES-P0-001/002`).
- Rotate/redact credentials before any rebuild, then rebind verdict ↔ digest ↔ shipped archive; no new manifest/verdict until the chain verifier is 0 failures.

### This Week
- Set 2 core identity: `SEC-P1-001/002`, `API-P1-001`, `CTR-P1-002`, `ACM-P1-001/002`, `ADV-P1-001`, custody `SECRET-P1-001/002/003`.
- Records closures in set 1: `EVID-P1-001/002`, `REV-P1-001/002`, `INV-P1-001`, `FEAT-P1-001/002`.
- Detectors + gate repair: `LIVE-P0-001/002`, `RES-P0-001/002`, `OBS-P1-001`–`005`, `BP-P1-001`, `CI-P2-001/002`, `HYGIENE-P2-001`, `TEST-P2-001/002`.

### This Month
- All P2 sets (131 findings) in dependency order: deploy-path controls (`DATA-P1-001`, `INV-P1-002`) → detectors (`OBS-P2-*`, `DQ-P2-*`, `RES-P2-*`) → docs/drift (`DOC-P2-*`, `INFRA-P2-*`, `ND-P2-*`); owner decisions: detection target, offsite key custody, edge secrets encrypt-or-accept, Wazuh indexer snapshots.

### Later / Platform Evolution
- Second-node decision (`ARCH-P1-001`, EX-22); edge packaging + migrations (`XREPO-P2-004`, `EVOL-P2-003`); joint release gate (`INTG-P1-002`); DQ scorecard ownership/event-time fidelity (`DQ-P2-004/005`); license gate + exceptions (`SBOM-P1-001`, EX-11/EX-12); verification-only closure pass + synthesis re-run.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Regenerate `FINAL_RESPONSE.json` from the digest source (`EVID-P1-002`, `FEAT-P1-002`) | Removes shipped contradiction | `closeout/generate_final_response.py` | Equality test |
| Refresh README/AGENTS current-state + edge status lines (`DOC-P1-001`, `INV-P1-001`, `EVID-P1-003`, `DOC-P1-002`) | First-read truth; stops false planning | `README.md`, `AGENTS.md`, `progress_ledger.md`, edge status docs | Docs/gate check |
| Fix pin/sidecar (`INV-P0-001`, `XREPO-P0-001`, `FLEET-P1-001`) | Restores traceability | `EDGE_RELEASE_PIN.md`, manifest + `.sha256` | `sha256sum -c` |
| Offsite last-success metric + rule (`RES-P0-001`, `OBS-P1-002`) | Detects realized failure class | `80-offsite-backup.sh`, `90-alerting.sh` | Forced-failure drill |
| Scanner XML-tag patterns (`SC-P1-001`, `API-P0-001`) | Closes false negatives | `secret_scan.py` | Injected fixture |
## Hardening Backlog

| Backlog item | Priority | Owner | Effort | Dependency |
|---|---|---|---|---|
| Single verdict source + CI equality (`REV-P1-002`, `EVID-P2-001`) | P1 | falcon | S | set 1 |
| Enrollment subject constraint (`SEC-P1-001`, `API-P1-001`) | P1 | edge | M | none |
| Root apply signature/safe extraction (`SEC-P1-002`, `CTR-P1-002`) | P1 | edge | M | none |
| Alert/backup detectors + firing proofs (`RES-P0-001/002`) | P1 | falcon/ops | M | DO/offsite access |
| Branch protection (`BP-P1-001`) | P1 | owner | S | admin access |
| Edge alerting + crash-safe update (`RES-P1-003`, `FLEET-P1-002`) | P1 | both | M | D-007; P7-G05 |
| Digest pinning + license gate (`INV-P1-002`, `SBOM-P1-001`) | P2 | falcon | M | registry access |
| Retention observability (`DATA-P1-001`, `DQ-P2-007`) | P2 | falcon | M | deploy path |
| Non-root runbooks + blind-ops (`LIVE-P1-002`, `IR-P1-001`) | P2 | falcon | M | none |
| Capacity reclaim + warning band (`PERF-P1-001/002`) | P2 | falcon/ops | M | maintenance window |
| Verification-only closure pass (`FINAL-P1-004`) | P2 | owner | M | sets 1–6 |
## Suggested Tests

| Class | Tests |
|---|---|
| Unit | `purge_expired()` mixed cutoff; CSR `CN=operator`; `destroyKeys`; pagination `limit=-1`; idempotency replay; scanner XML/64-hex fixtures |
| Integration | token→renew→operator negative; forged apply request; symlink tar; revoked-cert ingest; spoofed `sensor_id`; edge silence vs RETIRED |
| E2E/drills | stop relay 15 min; stop heartbeat; stop each timer/exporter; force offsite failure; guard reclaim; scratch restore incl. edge PKI; QEMU power-cut during apply |
| CI | protected-branch negative; unpinned-image negative; route parity; license gate; run-folder gate test; register↔findings reconciliation |
| Regression | digest equality; package-vs-tree diff; aggregate sums incl. N/A; duplicate risk-ID check |
| Manual | non-root read-only runbook walk; reproduce review commands from the delivered archive |
## Suggested Documentation Updates
- `README.md`, `AGENTS.md`, `ledgers/progress_ledger.md` — generated current-state block (`DOC-P1-001`, `INV-P1-001`, `EVID-P1-003`); `docs/edge/EDGE_RELEASE_PIN.md` + verifier — reproducible pairing (`INV-P0-001`, `XREPO-P0-001`).
- `docs/runbooks/*` + new `BLIND_OPERATIONS` — role-annotated, non-root executable (`LIVE-P1-002`, `INFRA-P1-001`); `docs/architecture/PORT_PROTOCOL_MATRIX.md` — live binds (`INFRA-P2-001`, `ARCH-P1-003`).
- `ledgers/redactions.md`, `contradiction_ledger.md`, `exception_register.md` — reconciliation rows (`EVID-P1-004`, `EVID-P2-003`); edge onboarding/quick start + secrets map (`DOC-P1-002`, `DOC-P2-003`, `ND-P2-005`).

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Owner-accepted total-host-loss detection target? | Sets watcher threshold/alert budget | Owner decision record (`RES-P1-001`) |
| Was JPB installer, reviewer, or both? | Decides need for a different reviewer | Reviewer disposition (`EVID-P0-002`) |
| Who owns Wazuh indexer snapshots; any owner-side job? | P1 vs accepted gap | Owner confirmation/job config (`DATA-P1-002`) |
| Who holds the offsite backup key? | Restore feasibility | Key-custody attestation (`DR-P1-004`) |
| Edge secrets: encrypt + offsite or accept? | Fleet trust loss risk | Decision + exception row (`DR-P1-005`) |
| Does Grafana notify on `execErrState: Error`, and does the DO watcher see lab ntfy via tunnel or copy? | Blind-failure path; dead-man correctness | Config/sanctioned test; out-of-repo watcher source (`OBS-P1-003`, `RES-P0-002`) |
| License/exception authority for the license-free amendment? | Gate cannot be enforced otherwise | Policy + exception rows (`SBOM-P1-001`) |
## Appendix

### Duplicate clusters (canonical fix map)

| Cluster | Members (canonical first) | Merge note |
|---|---|---|
| Release manifest/pin chain | `INV-P0-001`, `XREPO-P0-001`, `FLEET-P1-001`, `XREPO-P1-001`, `SBOM-P2-001`, `XREPO-P1-004`, `FLEET-P2-003`, `SBOM-P2-004` | One versioned-manifest fix |
| Approval/verdict binding | `EVID-P0-001`, `INV-P0-002`, `REV-P0-001`, `EVID-P1-001/002`, `REV-P1-002`, `FEAT-P1-002`, `HYGIENE-P2-003`, `AI-P2-003`, `DOC-P2-004`, `PRIV-P2-003` | One verdict source |
| Reviewer independence | `EVID-P0-002`, `REV-P1-001`, `AI-P1-002`, `XREPO-P2-002` | One reviewer artifact |
| Secrets + scanner | `API-P0-001`, `EVID-P1-004`, `SC-P1-001`, `SC-P2-001`, `SECRET-P1-003`, `XREPO-P1-003`, `SECRET-P2-004`–`007`, `SEC-P2-004`, `PRIV-P1-002`, `PRIV-P2-001` | Rotate + scanner + custody |
| Identity ladder | `SEC-P1-001`, `API-P1-001`, `ACM-P1-001`, `ADV-P1-001`, `ACM-P1-002`, `SEC-P2-003`, `FLEET-P2-005`, `ADV-P3-001` | Subject then lifecycle |
| Root execution trust | `SEC-P1-002`, `CTR-P1-002`, `CTR-P1-001`, `ARCH-P1-002`, `XREPO-P2-004`, `ARCH-P2-002` | Signature + pinned artifact |
| Alert-path blindness + peer visibility | `LIVE-P0-001`, `RES-P0-002`, `OBS-P1-001/003/005`, `RES-P1-001/002/006`, `NOTIF-P1-001/002`, `IR-P1-001`, `NOTIF-P2-003` | Canary + freshness family; export all peers |
| Backup truth | `LIVE-P0-002`, `RES-P0-001`, `DR-P1-001`–`005`, `OBS-P1-002`, `DATA-P1-002`, `RES-P1-004`, `DR-P2-001/002`, `FEAT-P2-001` | Gauges + verification + custody |
| Edge path unjoined | `RES-P1-003`, `OBS-P1-004`, `INTG-P1-001`, `XREPO-P1-002`, `LIVE-P1-003`, `FLEET-P1-002` | Deploy rules + crash-safe update |
| Capacity | `PERF-P1-001/002`, `LIVE-P1-001`, `RES-P1-005`, `PERF-P2-001/002` | Reclaim + warning band |
| Retention/data-loss bugs | `DATA-P1-001/003`, `RES-P2-002`, `TEST-P2-003`, `DQ-P2-007`, `DATA-P2-005`, `SEARCH-P2-001`, `DATA-P3-007` | Cutoff fix + retention deploy |
| Stale status/docs | `DOC-P1-001`–`003`, `INV-P1-001`, `ND-P1-001`, `FEAT-P1-001`, `EVID-P1-003`, `AI-P1-001`, `DOC-P2-001`–`004`, `INFRA-P1-001`, `LIVE-P1-002` | Generated current-state block |
| Peer/freshness visibility | `OBS-P1-005`, `RES-P1-006`, `RES-P1-002` | Export all peers + freshness rules |
### Count reconciliation and method
- Counts: `findings.json` 264 = P0 13 + P1 80 + P2 131 + P3 40 = `audit_manifest.findings.bySeverity`; `risk_register.md` 264 rows (severity filters 13/80/131/40).
- N/A: 10 prompts (`04`, `05`, `17`, `25`–`29`, `37`, `39`) excluded from counts and stated here; excluded findings: none.
- Method: rows machine-extracted from source sections, hand-corrected for the 11 P0 rows and 6 compact/malformed sections; owners normalized to `falcon`, `edge`, `both`, `falcon/ops`, `owner`; effort to S/M/L (ranges kept); all 264 findings assigned to exactly one patch set (256 domain/lens + 8 synthesis) (explicit membership in `patch_plan.md`). No repository, ledger, gate or live system was modified; only this run directory was written.
