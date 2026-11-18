# Post-merge verification — PRIV / IR / REL / EVOL (18 findings)

- Repo: `/home/user/falcon-build` @ `3623d2e` (`publication: bind … declared commit d1e5e75`), local HEAD == GitHub `main` (`3623d2e`, API check) — commit-level binding holds.
- Live: same host (live lab). Checks run read-only on 2026-10-12 ~20:00–20:18Z (sudo via owner key; no secret values printed).
- Original run: `falcon-20261011-0416-full-f5cb7c9` (findings.json). Procedure: `runbooks/POST_MERGE_REAUDIT.md` §3.
- **Note:** the working tree was **not clean at check time** — a concurrent session is editing files live (dashboard/SBOM/CI; mtimes 19:59–20:18Z, after the last commit 19:45:43Z). Treated as in-flight work, not a regression of the audited fixes (see New findings NF-1).

## Summary

| ID | Sev | Audit status | Verdict | Key evidence |
|---|---|---|---|---|
| PRIV-P1-001 | P1 | owner-accepted | **closed** | Wazuh ISM `wazuh-retention` 90d + template live (16 alerts indices managed), `wazuh-monitoring-retention` 30d (3 managed); `RETENTION_MATRIX.md:19-31`; IRIS 365d + `iris_retention_review.sh` (live run 0 past-window); `decision_log.md:271` |
| PRIV-P2-001 | P2 | open | **closed** | `docs/privacy/DATA_GOVERNANCE.md:56-63` (vendored-layer privacy boundary, 2026-10-11). Residual: `MCT_CONSOLIDATION.md` not cross-referenced; line 63 "owner decision pending" stale |
| PRIV-P2-003 | P2 | open | **still-open** | `PRODUCTION_VERDICT.md:8-12` annotation only; readiness line still `NOT_SUPPORTED` (`:37`); C1 OPEN (`CURRENT_STATE.md:53`, `C1_REVIEW_REPORT.md` unsigned template); consistency test not extended (`tests/digest_verdict_consistency_test.sh:15-28`) |
| PRIV-P3-001 | P3 | open | **still-open** | Wording fixed at `DATA_FLOW_AND_CLASSIFICATION.md:4`; device/site scope + entity/DPA/jurisdiction inputs still open (`DATA_GOVERNANCE.md:47-54`; `OWNER_ACTIONS.md` A6/C3) — owner-gated |
| IR-P2-001 | P2 | open | **still-open** | No facilitated tabletop: `TABLETOP_PACKAGE.md:3`, `records/README.md:3-6`, `TABLETOP_KIT.md:3` — owner-gated |
| IR-P2-002 | P2 | open | **still-open** | `ESCALATION_CONTACTS_TEMPLATE.md:12-42` all OWNER-INPUT, verification log empty — owner-gated |
| IR-P2-003 | P2 | open | **still-open** | Oct 10–11 record landed (`decision_log.md:268`); monthly recurrence review absent; no dedicated postmortem/captures |
| IR-P2-004 | P2 | open | **still-open** | Unit fixed (FreeBind, `config/systemd/falcon-wazuh-agent-proxy.socket:1-17`; sockets active since 2026-10-11 05:04:53Z; boot-order check 17/17 PASS); correction logged (`decision_log.md:268`). Residual: `VPN.md:193` still "fixed 2026-09-30"; boot-path proof pending next reboot |
| IR-P2-005 | P3 | open | **closed** | Reboot + post-reboot verification recorded (`decision_log.md:268`, 59/0; `CHANGELOG.md:19`). Residual: no capture artifact (NF-2) |
| REL-P2-001 | P2 | open | **still-open** | VERSION + tag exist, but no deploy manifest / deployed-commit record; tag `v2026.10.11` is 29 commits behind live HEAD; release notes don't state the deployed identity |
| REL-P2-002 | P2 | verified-fixed | **closed** | `PACKAGE_MANIFEST.sha256` == `review-package/MANIFEST.sha256` (7e2526ae…, 3842 entries); `check_publication_equality.py` PASS |
| REL-P3-001 | P3 | still-open | **still-open** | `CHANGELOG.md` now documents 2026.10.04..11 (and later); no generator/automation wired |
| REL-P3-002 | P3 | open | **closed** | `VERSION` (2026.10.11) + annotated tag `v2026.10.11` (de09889 → dff362c) on GitHub; `BRANCH_PROTECTION.md:59` statement now matches |
| REL-P3-003 | P3 | open | **still-open** | Packaged closeout names 7e84045 (previous cycle) vs declared `DELIVERED_PACKAGE_COMMIT=d1e5e75`; `verify_delivery.sh` still has no packaged-closeout assertion |
| EVOL-P1-001 | P1 | owner-accepted | **still-open** | `SHARED_TOOLING_POLICY.md:1-3` still proposed; `automation/shared-tooling.lock` + `shared_tooling_check.sh` still absent; E-1/C7 unsigned — owner-gated |
| EVOL-P1-002 | P1 | owner-accepted | **still-open** | `mct/VENDORING.md:3-4` still proposed/pending; `ci/validate.py:112-140` `check_compose_pins()` still `compose/**` only; `mct/compose` covered only by waiver (`supply-chain-waivers.json`; live check: 0 findings / 37 waived) — owner-gated |
| EVOL-P2-001 | P2 | open | **still-open** | `bootstrap/60-central-deploy.sh:144,207` still replace-on-apply; `EVOLUTION_GUIDE.md:320-322` "not done here"; E-4a unsigned — owner-gated |
| EVOL-P3-002 | P3 | open | **closed** | Owner acceptance recorded: `decision_log.md:271` "EVOL-P3-002 additive-deploy substitute accepted" (§9 = `EVOLUTION_GUIDE.md:342-362`) |

Totals: **6 closed, 12 still-open, 0 regressed.**

## Per-finding detail

### PRIV-P1-001 — Wazuh/IRIS retention (owner-gated) → closed
- Owner decisions recorded and implemented (defaults 2026-10-11): `ledgers/decision_log.md:271`; `docs/runbooks/RETENTION_MATRIX.md:19-31` (alerts 90 d, monitoring 30 d) and `:47` (IRIS 365 d).
- Live Wazuh indexer (verified via `docker exec` curl against `https://127.0.0.1:9200`, creds from `/opt/wazuh-docker/multi-node/.env`, values not printed):
  - `wazuh-retention`: description "delete wazuh-alerts-4.x-* after 90 days (owner default 2026-10-11; template attaches future daily indices)"; transition `min_index_age=90d`; `ism_template` on `wazuh-alerts-4.x-*`; **16 managed alerts indices** (all sampled = `wazuh-retention`).
  - `wazuh-monitoring-retention`: 30 d; 3 managed indices. `wazuh-states-*` 14 managed; `security-auditlog-*` 38 managed; `wazuh-archives-14d` policy present (no archives indices exist).
- IRIS: `automation/validation/iris_retention_review.sh:1-18` (read-only); live run → "past-window cases: 0".
- Residuals: IRIS deletion is manual/approved by design; no accelerated deletion test per class for the Wazuh estate (central `retention_execution_test.sh` covers `falcon-*` only); the Wazuh policies are live-only (New finding NF-3).

### PRIV-P2-001 — vendored MCT privacy boundary → closed
- Fix in place: `docs/privacy/DATA_GOVERNANCE.md:56-63` — "Vendored third-party layer (PRIV-P2-001, 2026-10-11)": vendored `mct/` is tooling/docs only, no client/personal data; a revived stack processing client data needs its own classification + retention entry + privacy review first.
- Residuals (minor): `docs/runbooks/MCT_CONSOLIDATION.md` (deployment classification only, `:22-39`) was not given the privacy wording; `DATA_GOVERNANCE.md:63` still says IRIS "(owner decision pending)" although the decision was recorded 2026-10-11 (NF-4).

### PRIV-P2-003 — production verdict binding/readiness → still-open (owner/reviewer-gated)
- The verdict now carries a publication-cycle note (`PRODUCTION_VERDICT.md:8-12`) and the 2026-10-01 state reconciliation (`:60-67`) — but it is an annotation, not a rebind: the identity block still binds `c312ab7` / 1,168 entries (`:14-26`), readiness line still `NOT_SUPPORTED` (`:37`), state note cites 67 rules (live is 93).
- Current chain: `PACKAGE_DIGEST.txt:2-5` declares `d1e5e75`, 3842 entries, `production_readiness=APPROVED`; the note's own numbers (e74fd7b/3,834) are already superseded.
- C1 remains OPEN (`docs/CURRENT_STATE.md:53`); `C1_REVIEW_REPORT.md` is still an unsigned template (no name/disposition); `OWNER_ACTIONS.md` A1/A2/A3 pending.
- `tests/digest_verdict_consistency_test.sh:15-28` still compares digest ↔ FINAL_RESPONSE only (not verdict binding fields). PASS at current state.
- Owner ask: JPB reviewer disposition + owner adoption, then regenerate/rebind the verdict from the ledgers (C1).

### PRIV-P3-001 — privacy wording / owner-legal inputs → still-open (owner-gated)
- "Synthetic-only" wording fixed: `docs/architecture/DATA_FLOW_AND_CLASSIFICATION.md:4` now records the authorization (2026-10-11, owner's own lab/site traffic, metadata-first).
- Still open: the device/site scope and entity/DPA/jurisdiction inputs remain listed as owner/legal inputs (`docs/privacy/DATA_GOVERNANCE.md:47-54`); `OWNER_ACTIONS.md` A6 (line 35) and C3 (line 74).
- Owner ask: record the device/site scope + complete C3, or explicitly accept the lab-scope limitation.

### IR-P2-001 — tabletop exercise → still-open (owner-gated)
- Unchanged: `docs/phase9/exercises/TABLETOP_PACKAGE.md:3` "no facilitated exercise has been run"; `records/README.md:3-6` "no exercise has been run and no record exists here yet"; `records/TABLETOP_KIT.md:3` "IR-P0-001 remains OPEN".
- Owner ask: schedule + record a facilitated session (start with Scenario 5), measure out-of-band latency, sign/index, set the quarterly cadence.

### IR-P2-002 — escalation contacts → still-open (owner-gated)
- `docs/security/ESCALATION_CONTACTS_TEMPLATE.md:12-42`: all 13 roles × 6 fields OWNER-INPUT; §3 verification log empty. No decision-log entry collecting values (values must stay out of the repo).
- Owner ask: fill the contact table in owner custody; verify ≥1 out-of-band channel end-to-end; record the verification log.

### IR-P2-003 — Oct 10–11 post-incident review → still-open (partial)
- Landed: `ledgers/decision_log.md:268` (2026-10-11T05:55Z) records the kernel reboot (root cause: sockets.target ordering cycle; impact: listeners dead ~45 min), the offsite upload-state truncation (root cause pre-#51 path), and the root-LV guard loop, with follow-ups.
- Remaining: no monthly recurrence review of incident/alert history; the record is a compact decision-log entry (no dedicated postmortem with captured verification items per `docs/phase7/runbooks/INCIDENT_RESPONSE.md` §9 close-out checklist); no captures (NF-2).

### IR-P2-004 — boot-ordering previous-fix verification → still-open (partial)
- Unit fix: `config/systemd/falcon-wazuh-agent-proxy.socket:1-17` and the enroll socket — `FreeBind=yes`, wg ordering removed; live sockets `active since 2026-10-11 05:04:53Z`; `automation/validation/boot_order_check.sh` → 17/17 PASS; `post_reboot_verify.sh:98` runs it.
- Record correction: `ledgers/decision_log.md:268` — "the 2026-09-30 fix never survived a reboot".
- Remaining: `docs/runbooks/VPN.md:193` still carries the superseded "fixed 2026-09-30" wording; no real boot since the fix (RES-P2-002 note: "next reboot is the final proof"); the "require boot-path evidence for verified claims" doctrine is not recorded anywhere; `post_reboot_verify.sh:106-108` comment still describes the 2026-09-30 fix.

### IR-P2-005 — reboot maintenance record / post-reboot verification → closed
- Recorded: `ledgers/decision_log.md:268` (reboot 02:25–02:27Z, post-reboot verification 59 passed / 0 failed) and `CHANGELOG.md:19`. Current read-only check re-run: 52 passed / 0 failed (`automation/validation/boot_check_readonly.sh --quiet`).
- Residual: no evidence capture for the 59/0 run (NF-2); the window was recorded post-hoc (the runbook process exists: `CAPACITY_AND_TELEMETRY.md` §Maintenance windows).

### REL-P2-001 — deployment not bound to a release → still-open (partial)
- New: `VERSION` = `2026.10.11`; annotated tag `v2026.10.11` (tag object de09889 → commit dff362c, message "final bind dff362c (declared eb6a0d2)") present locally and on GitHub (`git/refs/tags/v2026.10.11` API).
- Still missing: no deploy manifest / deployed-commit record (grep "deploy manifest|deployed commit" in `docs/` → none); `CHANGELOG.md` states no deployed identity; the tag is **29 commits behind** live HEAD (`git rev-list --count dff362c..HEAD` = 29), so the deployment is not bound to the tag.
- Live tree == remote `main` at commit level (`HEAD` = GitHub main = 3623d2e); working tree had 1 uncommitted file at 20:08Z and 4 at 20:18Z (concurrent session, NF-1).

### REL-P2-002 — published manifest stale (was verified-fixed) → closed, re-verified
- `sha256sum PACKAGE_MANIFEST.sha256 review-package/MANIFEST.sha256` → identical (`7e2526ae…`); both 3,842 entries; `python3 automation/validation/check_publication_equality.py` → PASS; `publish_digests.sh:18` copies the declared manifest on every bind. No regression.

### REL-P3-001 — CHANGELOG/release notes → still-open (partial)
- `CHANGELOG.md` exists (31 lines) and documents the 2026.10.04–08, 10.09–10, and 10.11 windows — the undocumented-window gap is closed.
- No generator wired: no CHANGELOG/VERSION references in `automation/`, `ci/`, or `.github/`; maintenance is manual; no CI check keeps it current.

### REL-P3-002 — release versioning → closed
- `VERSION` + annotated tag `v2026.10.11` exist (`git tag -l`; GitHub tags API lists it); `BRANCH_PROTECTION.md:59` ("releases are tags on `main`") now matches reality.
- Residuals: tag lags HEAD by 29 commits; no decision-log entry records the tag creation or a tagging policy; binding artifacts still rewrite in place (`publish_digests.sh`), as before.

### REL-P3-003 — packaged closeout bound to previous cycle → still-open (unchanged)
- `PACKAGE_DIGEST.txt` declares `DELIVERED_PACKAGE_COMMIT=d1e5e75`; the **packaged** closeout `review-package/closeout/FINAL_RESPONSE.json` has `commit = 7e84045…` (the previous cycle; hash `bde855a6…` matches the declared manifest entry) while the working-tree closeout (`e4d3042f…`) names `d1e5e75`.
- `automation/validation/verify_delivery.sh:1-65` still has no assertion that the packaged closeout names the declared commit; the documented flow (`AGENTS.md` step 5) still builds the package before `generate_final_response.py`, so the lag is structural.
- Fix ask (unchanged): regenerate the closeout before the package build (or rebuild the manifest after), and fail `verify_delivery.sh` on a packaged-closeout/declared-commit mismatch.

### EVOL-P1-001 — shared tooling → still-open (owner-gated)
- `docs/architecture/SHARED_TOOLING_POLICY.md:1-3` still "proposed 2026-10-01 … Nothing was implemented cross-repo"; `automation/shared-tooling.lock` and `automation/validation/shared_tooling_check.sh` still absent (`ls` fails).
- E-1/C7 still unsigned (`OWNER_ACTIONS.md:78`; `docs/OWNER_DECISION_PACKAGE_2026-10-02.md:17`).
- Owner ask: record E-1/C7; implement option B (pin + cross-repo hash check) with the intentional-fork allowlist.

### EVOL-P1-002 — MCT vendoring pin enforcement → still-open (owner-gated)
- `mct/VENDORING.md:3-4` still "policy proposed 2026-10-01; owner decision pending".
- `ci/validate.py:112-140` `check_compose_pins()` still globs `compose/**` only (blind to `mct/compose`); `check_compose_digests()` (`:142-160`) covers `mct/compose` but passes only via the waiver `pins/supply-chain-waivers.json` (root `mct/compose`, `*`, review_by 2026-12-31). Live re-run: `compose_digest_findings=0`, `compose_digest_waived=37`.
- Owner ask: decide E-2a/E-2b; implement VENDORING P4 (pin coverage or archive-only enforcement).

### EVOL-P2-001 — OpenSearch identity apply not merge-safe → still-open (owner-gated)
- `bootstrap/60-central-deploy.sh:144` documents the REPLACE behavior; `:207` runs the securityadmin apply. `EVOLUTION_GUIDE.md:313-322` still says "Recommended follow-up (runtime, not done here)"; E-4a unsigned (`OWNER_DECISION_PACKAGE_2026-10-02.md:98-102`).
- Owner ask: record E-4a; make the apply merge-safe or fail loud on undeclared users + add the fixture.

### EVOL-P3-002 — feature flags / additive-deploy substitute → closed
- Owner acceptance recorded: `ledgers/decision_log.md:271` — "EVOL-P3-002 additive-deploy substitute accepted" (2026-10-11 owner defaults). The substitute is documented in `EVOLUTION_GUIDE.md:342-362` (§9).
- Residual (cosmetic): the guide's backlog table (`:291`) still reads "documented in §9" without the acceptance marker.

## New findings

**NF-1 [P3][REL/INV] Live tree not clean at verification time (concurrent in-flight changes).**
At 20:08Z `git status --porcelain` showed 1 modified file; at 20:18Z it showed 4: `config/grafana/dashboards/edge-fleet-overview.json` (mtime 19:59:39Z; 24 panels vs 7 committed; semantically equal to the live Grafana dashboard `falcon-edge-fleet`, updated 2026-10-12T20:00:01Z), `.github/workflows/external-smoke.yml`, `automation/validation/sbom_hashes.sh`, `docs/security/SBOM_COVERAGE_AND_PROVENANCE.md` (mtimes 20:17–20:18Z). All post-date the last commit (19:45:43Z) and match a concurrent active session (in-flight files in `/tmp/opencode`). This breaks REL-P2-001's "live tree == remote main" property while uncommitted; whichever agent owns the changes must commit them (and rebind) or revert. Evidence: `git status --porcelain`; `stat`; Grafana API diff.

**NF-2 [P3][IR/EVID] No evidence captures for the 2026-10-11 post-reboot verification / PR #55 batch.**
`ledgers/decision_log.md:268` records "post_reboot_verify.sh 59/0" with no capture ID; `evidence/raw/` has no 2026-10-11 captures before 21:20Z (`find evidence -newermt '2026-10-11 05:00' ! -newermt '2026-10-11 06:30'` → none); `ledgers/evidence_index.csv` and `evidence/MANIFEST.sha256` list only the two 21:20Z credential-rotation captures for that date. The doctrine (`AGENTS.md` standard flow; `INCIDENT_RESPONSE.md` §10) expects captured commands/results. Recommendation: capture (or re-run and capture) the read-only boot checks and attach them to the record.

**NF-3 [P3][PRIV/DATA] Wazuh indexer retention is live-only (not reproducible from the repo).**
`wazuh-retention` (90 d) and `wazuh-monitoring-retention` (30 d) exist only on the live cluster (applied via API/console 2026-10-11, description "owner default 2026-10-11"); no repo script/config declares them (grep for `wazuh-retention`/`wazuh-monitoring-retention` → only `RETENTION_MATRIX.md` and the decision log; the central `config/opensearch/*.json` declarations have no Wazuh-indexer equivalent). The vendored `mct/runbooks/index-retention-policy.md:7-9` documents the upstream 30 d alerts policy — stale vs live 90 d. A rebuild/re-import would lose the owner-decided retention. Recommendation: add an idempotent provisioning script (or declared policy JSON + bootstrap step) for the Wazuh indexer ISM policies.

**NF-4 [P3][PRIV/DOC] Stale "owner decision pending" for IRIS retention.**
`docs/privacy/DATA_GOVERNANCE.md:63` says the live IRIS retention entry is "(owner decision pending)", but the owner decided 365 d on 2026-10-11 (`RETENTION_MATRIX.md:47`; `decision_log.md:271`). One-line correction needed.
