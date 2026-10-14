# Post-merge verification re-audit — PRIV / IR / REL / EVOL findings

- Repo: `/home/user/falcon-build` @ `edbf441d03cfba1f2a2e923a94021e1cbab0c338` (`edbf441`, branch `main`, working tree clean; `git ls-remote origin main` = `edbf441`).
- Date: 2026-10-14 (~00:30–01:00Z). Previous verification: `3623d2e` (2026-10-12), report `96_verification_priv-ir-rel-evol.md`.
- Original run: `falcon-20261011-0416-full-f5cb7c9` (126 findings); scope = the 18 PRIV/IR/REL/EVOL findings in `scope-96.json`.
- Method: read-only inspection at `edbf441` (`git show`/grep), read-only `ci/validate.py` subset runs (`compose-pins, compose-digests, shared-tooling, sbom-licenses, publication-equality`), live read-only checks (Wazuh indexer ISM policies via `docker exec` curl, systemd socket state, IRIS retention review, `boot_order_check.sh` / `boot_check_readonly.sh`), and read-only cross-checks of the edge repo (`/home/user/falcon-edge-build` @ `8182b12`; pinned worktree `/home/user/falcon-edge-pinned` @ `bb75403`).
- Substantive owner work since `3623d2e`: `b90498d` (owner defaults: shared-tooling lock+check, vendored pin gate, merge-safe identity apply), `ee4be3f` (ISM retention codified), `11623a1` (edge pairing pin → 0.2.0), `ce76ef0` (live tree reconciled, deployed edge rules committed).

## Summary table

| ID | Sev | Audit status | Verdict | Key evidence |
|---|---|---|---|---|
| EVOL-P1-001 | P1 | owner-accepted | **partially-fixed** | Falcon side implemented (`automation/shared-tooling.lock`, `shared_tooling_check.sh`, wired at `ci/validate.py:623-635,730`; live PASS; `decision_log.md:278`); residual: edge repo (8182b12 / bb75403) still has no lock/check and its `capture.sh` still diverges (sha `1284e0ec` vs locked `13a3bfe8`; still reads `/home/user/.env`, `PIPESTATUS[0]` bug, no `falcon-` topic redaction) |
| EVOL-P1-002 | P1 | owner-accepted | **verified-fixed** | `check_compose_pins()` now covers `mct/compose` + `automation/wazuh` with expiring waivers (`ci/validate.py:116-165`; live `compose image pinning` PASS; waivers `review_by 2026-12-31`); owner decision `decision_log.md:278`; residual: `VENDORING.md:3-4` still "proposed", blanket `*` waivers, upstream commit deferred |
| PRIV-P1-001 | P1 | owner-accepted | **verified-fixed** | Live ISM re-check: `wazuh-retention` 90 d + template, **18** alerts indices managed; `wazuh-monitoring-retention` 30 d incl. statistics template; policies now codified (`automation/wazuh/ism_retention_apply.sh`); IRIS review live 0 past-window (`RETENTION_MATRIX.md:23-31,47`); owner decision `decision_log.md:271` |
| EVOL-P2-001 | P2 | open | **verified-fixed** | Merge-safe carry-over implemented (`bootstrap/60-central-deploy.sh:204-231`; owner default `decision_log.md:278`); residual: no undeclared-user fixture, `EVOLUTION_GUIDE.md:290,320` still says "runtime follow-up / not done here" |
| IR-P2-001 | P2 | open | **open** | No facilitated tabletop: `TABLETOP_PACKAGE.md:3`, `records/README.md:3-6`, `records/TABLETOP_KIT.md:3` — owner-gated |
| IR-P2-002 | P2 | open | **open** | `ESCALATION_CONTACTS_TEMPLATE.md` all 13 roles × 6 fields OWNER-INPUT, §3 verification log empty; `OWNER_ACTIONS.md` A8 pending — owner-gated |
| IR-P2-003 | P2 | open | **partially-fixed** | Oct 10–11 record persists (`decision_log.md:268`); still no monthly recurrence review, no dedicated postmortem (`INCIDENT_RESPONSE.md` §9 format unused); Oct-12 CF incident is a decision-log row only |
| IR-P2-004 | P2 | open | **partially-fixed** | Unit fix + correction persist; `VPN.md:193` now "fixed 2026-10-11 (FreeBind; the 2026-09-30 ordering fix did not survive the reboot)"; sockets active since 2026-10-11 05:04:53Z; boot-order check 17/17 PASS; residual: no reboot since the fix (boot 2026-10-11 02:27Z), `post_reboot_verify.sh:106` comment still "2026-09-30 fix", boot-path-evidence doctrine unrecorded |
| PRIV-P2-001 | P2 | verified-fixed | **verified-fixed** | Boundary persists (`DATA_GOVERNANCE.md:56-63`); stale "owner decision pending" fixed (:62 now cites the 2026-10-11 365 d decision); residual: `MCT_CONSOLIDATION.md` still lacks the privacy cross-reference |
| PRIV-P2-003 | P2 | open | **open** | Verdict still binds `c312ab7` / 1,168 entries (`:14-26`), readiness `NOT_SUPPORTED` (`:37`), 28-rule note (`:46`); C1 OPEN (`CURRENT_STATE.md:53`, `C1_REVIEW_REPORT.md` unsigned); consistency test still verdict-fields only; cycle note cites superseded `e74fd7b`/3,834 (current `c045e78`/3,910) |
| REL-P2-001 | P2 | open | **open** | No deploy manifest / deployed-commit record (grep → none); `VERSION` 2026.10.11; tag `v2026.10.11` now **90** commits behind HEAD; live tree clean at `edbf441` == GitHub main; no deployed identity in `CHANGELOG.md` |
| REL-P2-002 | P2 | verified-fixed | **verified-fixed** | `PACKAGE_MANIFEST.sha256` == `review-package/MANIFEST.sha256` (both `80a089be…`, 3,910 entries); live `publication equality` PASS; `publish_digests.sh` copies on bind |
| EVOL-P3-002 | P3 | verified-fixed | **verified-fixed** | Owner acceptance persists (`decision_log.md:271`); §9 substitute intact (`EVOLUTION_GUIDE.md:342-362`); residual: backlog table `:291` lacks the acceptance marker |
| IR-P2-005 | P3 | verified-fixed | **verified-fixed** | Record persists (`decision_log.md:268`; `CHANGELOG.md:19`); `boot_check_readonly.sh` re-run 52/0 and `boot_order_check.sh` 17/17; residual: still no evidence capture for the 59/0 run |
| PRIV-P3-001 | P3 | open | **open** | Wording fixed (`DATA_FLOW_AND_CLASSIFICATION.md:4`); owner/legal inputs still open (`DATA_GOVERNANCE.md:47-54`; `OWNER_ACTIONS.md` A6/C3) — owner-gated |
| REL-P3-001 | P3 | open | **open** | `CHANGELOG.md` still ends at the 2026.10.11 window; no generator/automation wired (grep `automation/ ci/ .github/` → none); the 2026-10-12/13 windows are undocumented again |
| REL-P3-002 | P3 | verified-fixed | **verified-fixed** | `VERSION` 2026.10.11 + annotated tag `v2026.10.11` (de09889 → dff362c) persist; `BRANCH_PROTECTION.md:59` matches; residual: no tag/bump for the 2026-10-12/13 deliveries |
| REL-P3-003 | P3 | open | **open** | Packaged `review-package/closeout/FINAL_RESPONSE.json` names `0ea8969` vs declared `c045e78` (digest); working-tree closeout names `c045e78`; `verify_delivery.sh` still has no packaged-closeout assertion |

Totals: **8 verified-fixed, 3 partially-fixed, 7 open, 0 owner-accepted, 0 regressed.**

## Per-finding detail

### EVOL-P1-001 — Cross-repo shared tooling drift / no pin-hash enforcement — partially-fixed
- Falcon side is now implemented (owner default 2026-10-12, `decision_log.md:278`): `automation/shared-tooling.lock` (6 files with sha256) and `automation/validation/shared_tooling_check.sh` exist; the check is wired into `ci/validate.py:623-635` and registered at `:730`. Live run: `PASS shared tooling (matches automation/shared-tooling.lock)`.
- The cross-repo half is **not** in place. The edge repo `/home/user/falcon-edge-build` @ `8182b12` (and the pinned `bb75403` tree) has no `automation/shared-tooling.lock` and no `shared_tooling_check.sh` (`find` and `git log --all -- automation/shared-tooling.lock` → empty). The lock's own comment claims "falcon-edge-build vendors the same lock" — not true at these commits.
- The documented asymmetric security fix still stands on the edge side: edge `automation/evidence/capture.sh` sha `1284e0ec…` vs locked falcon `13a3bfe8…`; it still falls back to `/home/user/.env` (`SUDO_ENV_FILE:-/home/user/.env`), still records the password feed's exit code (`RC=${PIPESTATUS[0]}` — the bug falcon fixed on 2026-10-01), and still lacks the `falcon-` ntfy-topic redaction (`mon-` only). Edge `ci/secret_scan.py` sha `25921245…` remains a parallel implementation vs the locked falcon `automation/validation/secret_scan.py` `232779ec…`.
- `docs/architecture/SHARED_TOOLING_POLICY.md:1-3` still says "proposed … Nothing was implemented cross-repo"; no intentional-fork allowlist file exists (the lock carries only the shared set).
- What changed since 3623d2e: falcon-side option B landed and passes; the edge side has not adopted it yet.

### EVOL-P1-002 — MCT vendoring policy not enforced; pin gate blind to mct/compose — verified-fixed
- The pin gate is no longer blind: `ci/validate.py` `check_compose_pins()` now globs `compose/**`, `mct/compose/**` and `automation/wazuh/**` (`:116-165`), with explicit expiring `compose_pin` waivers from `pins/supply-chain-waivers.json` (roots `mct/compose` and `automation/wazuh`, `review_by 2026-12-31`). Live run: `PASS compose image pinning`; `compose-digests` also PASS.
- Owner decision recorded: `decision_log.md:278` ("pin gate now covers mct/compose + automation/wazuh with the owner-visible expiring compose_pin waivers").
- Residuals: `mct/VENDORING.md:3-4` still reads "policy proposed 2026-10-01; owner decision pending"; the waivers are blanket `ref:*` per root, so the 29 existing unpinned refs keep passing until 2026-12-31; the upstream commit is still unrecorded (deferred to the next import); E-2a subtree-fate wording is not recorded in the vendoring doc.
- What changed since 3623d2e: the CI blind spot was closed by `b90498d` and verified live.

### PRIV-P1-001 — Wazuh/IRIS retention (owner-gated) — verified-fixed
- Owner decision + implementation persist (2026-10-11): `RETENTION_MATRIX.md:23-31` (alerts 90 d, monitoring/statistics 30 d), `:47` (IRIS 365 d), `decision_log.md:271`.
- Live re-check (2026-10-14, read-only): ISM policies `wazuh-retention` (90 d, `ism_template` on `wazuh-alerts-4.x-*`) and `wazuh-monitoring-retention` (30 d, template `wazuh-monitoring-*` + `wazuh-statistics-*`) present; **18** `wazuh-alerts-4.x-*` indices, all managed by `wazuh-retention` (the template keeps auto-attaching daily indices — was 16 on 2026-10-12).
- Reproducibility gap (NF-3 from 2026-10-12) is closed: `automation/wazuh/ism_retention_apply.sh` re-declares both policies idempotently and re-attaches existing indices (`ee4be3f`).
- IRIS: `automation/validation/iris_retention_review.sh` live run → "past-window cases: 0".
- Residual: no accelerated deletion test per class for the Wazuh estate (deletion not exercised), unchanged.

### EVOL-P2-001 — OpenSearch identity apply not merge-safe — verified-fixed
- `bootstrap/60-central-deploy.sh:204-231`: before the securityadmin apply, the script reads `/_plugins/_security/api/internalusers`, filters out the declared set, and appends every ad-hoc user (hash + backend/security roles) to `internal_users.yml`, so a re-run merges instead of replacing (R-28 hazard).
- Owner decision recorded: `decision_log.md:278` ("merge-safe - the securityadmin apply now carries over ad-hoc internal users").
- Residuals: no undeclared-user fixture/regression test was added (the audit asked for one); `EVOLUTION_GUIDE.md:290` ("merge-safe apply is a runtime follow-up") and `:320-322` ("Recommended follow-up (runtime, not done here)") are stale; the carry-over is best-effort — if the internalusers GET fails the script silently falls back to replace (no fail-loud path).
- What changed since 3623d2e: code fix + owner decision landed; the doc/test residuals are new in the sense that they now contradict the fix.

### IR-P2-001 — No facilitated tabletop exercise — open
- Unchanged: `docs/phase9/exercises/TABLETOP_PACKAGE.md:3` "no facilitated exercise has been run against it"; `records/README.md:3-6` "no exercise has been run and no record exists here yet"; `records/TABLETOP_KIT.md:3` "IR-P0-001 remains OPEN". `records/` contains only the README and the kit — no session record.
- Owner-gated (owner + responder + independent reviewer); Scenario 5 remains paper-only.

### IR-P2-002 — Escalation contacts placeholders — open
- Unchanged: `docs/security/ESCALATION_CONTACTS_TEMPLATE.md` §2 has 13 roles × 6 fields all `OWNER-INPUT` (23 occurrences in the file), §3 verification log empty; values must stay out of the repo. `OWNER_ACTIONS.md` A8 still pending.
- Owner-gated; no decision-log entry collecting the contacts.

### IR-P2-003 — Recurring incidents lack post-incident review — partially-fixed
- The Oct 10–11 record persists: `decision_log.md:268` (2026-10-11T05:55Z) covers the kernel reboot + socket outage, the offsite upload-state truncation and the root-LV guard loop, with follow-ups. This part of the finding is fixed.
- Still absent: any monthly recurrence review of incident/alert history; any dedicated postmortem in the expected format (`docs/phase9/INCIDENT_2026-09-23_PYTHON_INTERPRETER.md` is still the only one; `INCIDENT_RESPONSE.md` §9 close-out unused). The later incidents (2026-10-12 CF API/token incident, 2026-10-13 WZ-VOLUME/triage) are compact decision-log rows only, no captures for the incident review itself.
- What changed since 3623d2e: nothing material; the residual is the same.

### IR-P2-004 — Previous-fix verification failed (boot ordering) — partially-fixed
- Unit fix persists: `config/systemd/falcon-wazuh-agent-proxy.socket` / `...-enroll-proxy.socket` (FreeBind, ordering removed); live: both sockets `active` with `ActiveEnterTimestamp=Sun 2026-10-11 05:04:53 UTC`, `WantedBy=multi-user.target`. `boot_order_check.sh` → 17/17 PASS.
- Record/doc correction landed: `decision_log.md:268` ("the 2026-09-30 fix never survived a reboot") and `docs/runbooks/VPN.md:193` now reads "fixed 2026-10-11 (FreeBind; the 2026-09-30 ordering fix did not survive the reboot)" — the 2026-10-12 residual is fixed.
- Residuals: no reboot since the fix (host boot 2026-10-11 02:27:44Z, uptime 2 d 22 h), so the boot path itself is still unproven; `automation/validation/post_reboot_verify.sh:106` comment still describes it as the "2026-09-30 fix"; the "require boot-path evidence for verified claims" doctrine is not recorded anywhere (grep → none).

### PRIV-P2-001 — Vendored MCT privacy-classification boundary — verified-fixed
- Fix persists: `docs/privacy/DATA_GOVERNANCE.md:56-63` "Vendored third-party layer (PRIV-P2-001, 2026-10-11)" — vendored `mct/` is tooling/docs only; a revived stack processing client data needs its own classification + retention entry + privacy review first.
- The stale "owner decision pending" residual is fixed: `:62` now reads "The live IRIS instance is covered by its own retention entry (owner decision 2026-10-11: 365 d; see RETENTION_MATRIX.md)".
- Residual (unchanged): `docs/runbooks/MCT_CONSOLIDATION.md` still has no privacy cross-reference (grep → no `PRIV`/privacy refs).

### PRIV-P2-003 — Production verdict binds a superseded package / contradictory readiness — open
- Unchanged: `PRODUCTION_VERDICT.md` identity block still `c312ab7` / 1,168 entries (`:14-26`), readiness `NOT_SUPPORTED` (`:37`), state note "28 alert rules" (`:46`; live catalogue now 94). The publication-cycle note (`:8-12`) is an annotation and now itself cites a superseded cycle (`e74fd7b`/3,834 vs current `c045e78`/3,910 in `PACKAGE_DIGEST.txt`).
- C1 remains OPEN (`CURRENT_STATE.md:53`); `C1_REVIEW_REPORT.md` is still an unsigned template (Name `_(JPB)_`, blank fields); `OWNER_ACTIONS.md` A1/A2/A3 pending. The C1 binder gained a "current delivery (2026-10-13)" pointer (`d1e1e92`) — helpful, but no rebind.
- `automation/validation/tests/digest_verdict_consistency_test.sh` still compares digest ↔ closeout verdict/readiness/open-gates only (not the verdict binding fields).
- Owner/reviewer-gated: JPB disposition + owner adoption, then regenerate/rebind.

### REL-P2-001 — Deployment not bound to any release — open
- Still no deploy manifest / deployed-commit record: grep for "deploy manifest|deployed commit|deployed-commit" across `docs/ ledgers/ automation/ ci/` → none; `CHANGELOG.md` does not state the deployed identity.
- `VERSION` = `2026.10.11`; the only tag `v2026.10.11` (tag object `de09889` → commit `dff362c`, 2026-10-11) is now **90** commits behind HEAD (`git rev-list --count v2026.10.11..edbf441`; was 29 on 2026-10-12).
- The live-tree leg holds: `/home/user/falcon-build` is clean at `edbf441` and `git ls-remote origin main` = `edbf441` (the 2026-10-12 NF-1 concurrent-edit condition is resolved by `ce76ef0`).

### REL-P2-002 — Published manifest stale — verified-fixed
- `sha256sum PACKAGE_MANIFEST.sha256 review-package/MANIFEST.sha256` → both `80a089bec48e…` (3,910 entries). Live check: `PASS publication equality (digest<->closeout<->manifest)`. The copy-on-bind behavior (`verify_delivery.sh` step 2b) is unchanged and exercised by every rebind since.
- No regression.

### EVOL-P3-002 — No feature flags; additive-deploy substitute — verified-fixed
- Owner acceptance persists: `decision_log.md:271` "EVOL-P3-002 additive-deploy substitute accepted"; the substitute is intact at `EVOLUTION_GUIDE.md:342-362` (§9).
- Residual (cosmetic, unchanged): the backlog table `EVOLUTION_GUIDE.md:291` still reads "documented in §9" without an acceptance marker.

### IR-P2-005 — Reboot maintenance record / post-reboot verification — verified-fixed
- Record persists: `decision_log.md:268` (reboot 02:25–02:27Z; post-reboot verification 59/0) and `CHANGELOG.md:19`.
- Current read-only re-runs: `boot_check_readonly.sh --quiet` → 52 passed / 0 failed; `boot_order_check.sh` → 17/17 PASS.
- Residual (NF-2 from 2026-10-12, unchanged): no evidence capture for the 59/0 run — `ledgers/evidence_index.csv` has no 2026-10-11 boot captures (only the two 21:20Z credential-rotation captures for that date).

### PRIV-P3-001 — Owner/legal privacy inputs and "synthetic-only" wording — open
- Wording fixed: `docs/architecture/DATA_FLOW_AND_CLASSIFICATION.md:4` records the authorization (owner's own lab/site traffic, metadata-first, 2026-10-11).
- Still open: entity/DPA/jurisdiction inputs and the owner-device telemetry scope (`docs/privacy/DATA_GOVERNANCE.md:47-54`); `OWNER_ACTIONS.md` A6 (line 35) and C3 (line 74) pending — owner/legal-gated.

### REL-P3-001 — No CHANGELOG/release-notes generator; window undocumented — open
- `CHANGELOG.md` exists and covers 2026.10.04–08, 10.09–10, 10.11 (last touched `e094473`, 2026-10-11) — but the 2026-10-12 and 2026-10-13 windows (owner defaults, CI watchdog, WZ-VOLUME, edge pin rebind, ISO builder, rebinds) are undocumented again.
- No generator/automation wired: grep for "changelog"/"release notes" in `automation/`, `ci/`, `.github/` → none; maintenance is manual.

### REL-P3-002 — Releases not versioned — verified-fixed
- `VERSION` = `2026.10.11` and annotated tag `v2026.10.11` (de09889 → dff362c) exist at `edbf441`; `docs/security/BRANCH_PROTECTION.md:59` ("releases are tags on `main`") still matches reality.
- Residual: no new tag or VERSION bump for the many 2026-10-12/13 rebinds; the tag lag grew 29 → 90 commits (tracked under REL-P2-001).

### REL-P3-003 — Packaged closeout bound to the previous cycle — open
- Unchanged and re-confirmed: `PACKAGE_DIGEST.txt` declares `DELIVERED_PACKAGE_COMMIT=c045e78…`; the packaged `review-package/closeout/FINAL_RESPONSE.json` (sha `bf125ed5…`, matching the published manifest entry) names `0ea8969…` (the previous cycle), while the working-tree `closeout/FINAL_RESPONSE.json` (sha `89a6b806…`) names `c045e78…`.
- `automation/validation/verify_delivery.sh` still has no assertion that the packaged closeout names the declared commit (read end-to-end, 65 lines); `check_publication_equality.py` reads the working-tree closeout. The structural lag (package built before the closeout is regenerated) persists.

## Cross-cutting checks requested in the focus

- **Edge 0.2.0 handover / pairing pin** (`11623a1`): verified — `docs/edge/EDGE_RELEASE_PIN.md` now pins `falcon-edge-release-manifest-20261013-bb75403.json` (0.2.0, commit `bb75403`, signature keyId `5ea52faf9cf6ee97`), rollback target the 2026-10-02 manifest; the live pinned worktree is at `bb75403`; `decision_log.md` 2026-10-13T23:40Z records `verify_edge_pin.py` PASS and `pair_state_check.sh` failures=0. No in-scope REL/EVOL finding is pairing-bound (the REL residuals are publication/deploy-identity ones).
- **IRIS admin/API rotations**: still owner-gated — `docs/security/CREDENTIAL_ROTATION_REGISTER.md` rows 11 (IRIS admin), 12 (IRIS API) and 19 (IRIS DB/secret key) remain `PENDING`/OWNER-console; rows 1–2 `ROTATED` (2026-10-11), retired-system rows `DONE`. The only IRIS token-rotation runbook is the vendored `mct/runbooks/iris_token_rotation_runbook.md`, which still targets the decommissioned VM101 and the retired Shuffle stack (see NF-2).
- **Owner-gated items vs registers**: E-1/C7 (EVOL-P1-001), E-2 (EVOL-P1-002) and E-4a (EVOL-P2-001) are now recorded via the owner-defaults row `decision_log.md:278`; C1/A1–A3, A6, C3, A8, IRIS rows 11/12/19 remain pending.

## New findings

**NF-1 [P3][PRIV/DATA] The 2026-10-13 AP-exposure detection is not covered by any privacy or retention document in this repository.**
The deployed edge rule `EdgeSensorNewApDetected` (`config/prometheus/edge-alerts.yaml:373-385`, committed from the edge source in `ce76ef0`) fires on `falcon_edge_sensor_capture_new_aps_24h`, and the edge-side `automation/validation/ap_watch.py` (lab host, `/srv/falcon/edge-catalog/unknown_aps.json`, `falcon-ap-watch.timer`) extracts the raw BSSID and SSID of every AP seen by the sensors — including third-party/neighbouring APs — for comparison against the owner's UniFi allowlist. No falcon privacy doc covers this class: `docs/privacy/DATA_GOVERNANCE.md` data classes list only "Edge fleet telemetry" (sensor_id/site/state/tunnel/health); `docs/runbooks/RETENTION_MATRIX.md` has no Kismet/AP store row; `docs/architecture/DATA_FLOW_AND_CLASSIFICATION.md` has no wireless stream; grep for kismet/ssid/bssid/wireless across `docs/privacy/` and the retention matrix → nothing. The edge repo's own `docs/runbooks/data-retention.md` (windows approved 2026-10-12) also has no AP/Kismet row. Additionally, the rule's `runbook: docs/runbooks/exposure-monitoring.md` reference does not exist in this repo (the file exists only in `falcon-edge-build`), so a falcon-side responder cannot follow it. Recommendation: add the AP-observation class (raw BSSID/SSID, metadata-only rationale, retention window) to `DATA_GOVERNANCE.md` + `RETENTION_MATRIX.md` and the edge retention table, and either vendor/copy the exposure-monitoring runbook or annotate the mirror's runbook path.

**NF-2 [P3][IR/SEC] The only IRIS token-rotation runbook is vendored and stale (retired host/services).**
`mct/runbooks/iris_token_rotation_runbook.md` (vendored MCT content) instructs the operator to log in to `https://192.168.222.149:8443` (VM101, decommissioned 2026-09-27) and to rotate the Docker Swarm secret `iris-shuffle-env` for `shuffle-tools` — Shuffle was retired with VM101. There is no first-party IRIS token-rotation procedure: `docs/security/INHERITED_CREDENTIAL_ROTATION.md` §5 is a one-line ask that also says "update Shuffle workflow headers", and the live tracking is the owner-console register rows 11/12/19 (PENDING). The live IRIS runs at `/opt/iris-web` on the lab host with no Shuffle consumer. Recommendation: add a short first-party IRIS admin/API rotation procedure (IRIS UI + `/srv/falcon/secrets/iris-web.env` / the API key store) and mark the vendored runbook as historical.
