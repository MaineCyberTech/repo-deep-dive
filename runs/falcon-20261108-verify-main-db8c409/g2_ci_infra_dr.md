# G2 fresh verify — CI / supply / infra / DR — falcon @ `db8c409` (2026-11-08)

- Run: `falcon-20261108-verify-main-db8c409`
- Target: `MaineCyberTech/falcon` @ `db8c40970083a98e50dbae8038971ec2ac6bc252` — main@db8c409 (2026-11-08).
- Scope: CI, BP, SC, SBOM, CTR, SECRET, DET, RES, DR, IR, OBS, PERF. `EVOL-P1-001` is outside G2 and was skipped.
- Method: repository evidence at the commit + read-only live checks from the independent site host (Falcon Console API, host endpoint, DO watcher log/state, public HTTPS HEADs, local deterministic checks). No mutations; no secrets printed. CI repository-settings APIs and lab-host SSH were not available from this host.

## Verdict summary

| Verdict | Count |
|---|---:|
| verified-fixed | 20 |
| partially-fixed | 16 |
| open | 17 |
| regressed | 2 |
| owner-accepted | 1 |
| **total** | **56** (53 re-checked + 3 new) |

New: **0 P0 / 0 P1 / 2 P2 / 1 P3**. Regressions: **2**.

| Area | Total | Fixed | Partial | Open | Regressed | Accepted |
|---|---:|---:|---:|---:|---:|---:|
| CI | 8 | 3 | 2 | 2 | 1 | 0 |
| BP | 2 | 1 | 0 | 1 | 0 | 0 |
| SC | 3 | 2 | 1 | 0 | 0 | 0 |
| SBOM | 3 | 1 | 2 | 0 | 0 | 0 |
| CTR | 3 | 0 | 2 | 1 | 0 | 0 |
| SECRET | 4 | 1 | 1 | 2 | 0 | 0 |
| DET | 4 | 0 | 0 | 3 | 0 | 1 |
| RES | 5 | 2 | 1 | 2 | 0 | 0 |
| DR | 5 | 1 | 2 | 2 | 0 | 0 |
| IR | 5 | 2 | 1 | 2 | 0 | 0 |
| OBS | 5 | 2 | 1 | 1 | 1 | 0 |
| PERF | 9 | 5 | 3 | 1 | 0 | 0 |

## Regressions

### CI-P2-002 — Independent Access-posture check stuck failing after the Kestrel cutover

- verified-fixed -> **regressed** (P2)
- Evidence: automation/alerting/do_watcher/watch.sh:67; live /var/log/falcon-watcher.log; /var/lib/falcon-watcher/posture=alerted
- Impact: The accepted independent proof of public auth enforcement is dead; repeated failures are suppressed by the 'already alerted' state, and external-smoke accepts any 302 as an owner bypass.

### OBS-P2-001 — Alert catalogue drifted to 94 while the script provisions 95

- verified-fixed -> **regressed** (P2)
- Evidence: bootstrap/90-alerting.sh:636-638; docs/phase9/ALERT_CATALOGUE.yaml (94 ids); README.md:33; docs/CURRENT_STATE.md:169
- Impact: The catalogue no longer describes the deployed rule set; the missing rule is falcon-edge-spool-unretained, and the existing drift test cannot see script-only rules.

## New findings

### CI-P2-004 — CI installs cryptography/PyJWT by bare version with no hashes or Dependabot coverage

- Severity: **P2**; status: open (new).
- Evidence: .github/workflows/validate.yml:50-54; ci/requirements-ci.txt; .github/dependabot.yml:9-15

### DR-P2-004 — Offsite verification passes vacuously on an empty or unexpectedly tiny snapshot repository

- Severity: **P2**; status: open (new).
- Evidence: bootstrap/80-offsite-backup.sh:286-289,305-312,408-414,570-575,659-665; automation/validation/offsite_verify_all.py:78-92

### OBS-P3-001 — Console Prometheus-backed sections are blank after the 2026-11-05 reboot

- Severity: **P3**; status: open (new).
- Evidence: config/systemd/falcon-console.service:4-5; automation/console/resolve_sources.sh; console/metrics.py:179-204; live /console/api/v1/capacity

## Status by area

### CI

| ID | Sev | Previous | Status | Evidence | Disposition |
|---|---|---|---|---|---|
| CI-P2-001 | P2 | partially-fixed | **partially-fixed** | `.github/workflows/dependabot-merge.yml:17-19`, `.github/workflows/dependabot-merge.yml:49-54`, `.github/workflows/dependabot-merge.yml:28-31` | Partially fixed: head pin present (dependabot-merge.yml:54); write scopes and env-less job unchanged. No code regression. |
| CI-P2-002 | P2 | verified-fixed | **regressed** | `automation/alerting/do_watcher/watch.sh:63-71`, `.github/workflows/external-smoke.yml:5-12`, `docs/runbooks/SSO.md:1-12` | Regression. Live evidence 2026-11-08: public 302 -> idp.mainecybertech.us; watch.sh sha256 matches /opt/falcon-watcher/watch.sh; posture=alerted. |
| CI-P2-003 | P2 | partially-fixed | **partially-fixed** | `.github/workflows/validate.yml:17-18`, `.github/workflows/external-smoke.yml:20-21`, `.github/workflows/dependabot-merge.yml:17-19` | Partially fixed; live settings were not re-checkable offline this pass. No repo-side change since edbf441. |
| CI-P2-004 | P2 | new | **open** | `.github/workflows/validate.yml:50-54`, `ci/requirements-ci.txt:1-8`, `.github/dependabot.yml:9-15` | New 2026-11-08. Severity P2 (supply chain on a self-hosted runner), not a runtime credential exposure. |
| CI-P3-001 | P3 | verified-fixed | **verified-fixed** | `config/systemd/falcon-ci-watchdog.timer:1-12`, `.github/workflows/validate.yml:31-32`, live | Verified fixed. |
| CI-P3-002 | P3 | verified-fixed | **verified-fixed** | `.github/workflows:1-3`, live | Verified fixed; live API not re-queried this pass. |
| CI-P3-003 | P3 | verified-fixed | **verified-fixed** | `docs/security/CI_CD_INCIDENT_PLAYBOOK.md:266-279`, `.github/workflows/validate.yml:47-116` | Verified fixed. |
| CI-P3-004 | P3 | open | **open** | `README.md:122`, `REPOSITORY.md:53`, `.github/workflows:1-3` | Open; no change since edbf441. |

### BP

| ID | Sev | Previous | Status | Evidence | Disposition |
|---|---|---|---|---|---|
| BP-P2-001 | P2 | verified-fixed | **verified-fixed** | `.github/CODEOWNERS:1-14`, live | Verified fixed; live API not re-queried this pass. |
| BP-P3-001 | P3 | open | **open** | `.github/workflows/dependabot-merge.yml:43-57`, `docs/security/BRANCH_PROTECTION.md:93-104`, `ledgers/decision_log.md:269` | Open; no evidence of an exercise since edbf441. |

### SC

| ID | Sev | Previous | Status | Evidence | Disposition |
|---|---|---|---|---|---|
| SC-P2-002 | P2 | partially-fixed | **partially-fixed** | `docs/security/CREDENTIAL_ROTATION_REGISTER.md:12-13`, `docs/security/CREDENTIAL_ROTATION_REGISTER.md:16-40`, `docs/security/INHERITED_CREDENTIAL_ROTATION.md:20,76-79` | Partially fixed; no progress since edbf441 (still 9 rotated / 11 pending). |
| SC-P3-001 | P3 | verified-fixed | **verified-fixed** | `automation/validation/publish_digests.sh:14-20`, `PACKAGE_DIGEST.txt:6-7`, live | Verified fixed. |
| SC-P3-002 | P3 | verified-fixed | **verified-fixed** | `.github/dependabot.yml:1-15`, live | Verified fixed; live API not re-queried this pass. |

### SBOM

| ID | Sev | Previous | Status | Evidence | Disposition |
|---|---|---|---|---|---|
| SBOM-P2-001 | P2 | partially-fixed | **partially-fixed** | `sbom/SBOM_MANIFEST.sha256.sig:1-3`, `ci/validate.py:605-616`, `ci/validate.py:704-733` | Partially fixed; core signing/license controls are live, binding/decision-record residual remains. |
| SBOM-P3-001 | P3 | open | **verified-fixed** | `automation/validation/build_review_package.sh:39-53`, `review-package/MANIFEST.sha256:sbom/`, `docs/security/SBOM_COVERAGE_AND_PROVENANCE.md:174` | Verified fixed (status flip from open). |
| SBOM-P3-002 | P3 | open | **partially-fixed** | `docs/security/SBOM_COVERAGE_AND_PROVENANCE.md:82-83`, `docs/security/SBOM_COVERAGE_AND_PROVENANCE.md:88-91`, `docs/security/SBOM_COVERAGE_AND_PROVENANCE.md:175` | Partially fixed; correction exists but the contradictory text remains. |

### CTR

| ID | Sev | Previous | Status | Evidence | Disposition |
|---|---|---|---|---|---|
| CTR-P2-001 | P2 | open | **partially-fixed** | `compose/mct/docker-compose.opencanary.yml:30-42`, `compose/mct/iris-web/docker-compose.hardening.yml:1-58`, `automation/wazuh/multi-node/docker-compose.hardening.yml:1-80` | Partially fixed (was open at edbf441): repo overlays + live healthchecks landed 2026-10-14/15; default-path and cap_drop/non-root gaps remain. |
| CTR-P3-001 | P3 | open | **partially-fixed** | `mct/compose/docker-compose.shuffle.yml:48-53,90-93`, `pins/supply-chain-waivers.json:1-20`, `mct/compose/VENDOR_MANIFEST.sha256:1-5` | Partially fixed; remaining unpinned refs are owner-accepted for the archive-only tree until 2026-12-31. |
| CTR-P3-002 | P3 | open | **open** | `compose/central/opensearch-s3.Dockerfile:1-4`, `bootstrap/60-central-deploy.sh:53-69` | Open; no change. |

### SECRET

| ID | Sev | Previous | Status | Evidence | Disposition |
|---|---|---|---|---|---|
| SECRET-P2-001 | P2 | partially-fixed | **partially-fixed** | `docs/security/CREDENTIAL_ROTATION_REGISTER.md:12-40`, `automation/validation/check_rotation_register.py:1-20`, `mct/scripts/full-stack-healthcheck.sh:16` | Partially fixed; unchanged since edbf441. |
| SECRET-P2-002 | P2 | verified-fixed | **verified-fixed** | `ci/validate.py:736-753`, `.env.example:16-22`, `docs/security/OWNER_ENV_INVENTORY.md:47-53` | Verified fixed (repo + prior live); live re-check not possible from this host. |
| SECRET-P3-001 | P3 | open | **open** | `docs/security/CREDENTIAL_ROTATION_REGISTER.md:38`, `mct/runbooks/credential-rotation-checklist.md:42-49`, `docs/security/CREDENTIAL_ROTATION_REGISTER.md:32-37` | Open; unchanged. |
| SECRET-P3-002 | P3 | open | **open** | `docs/security/BREAK_GLASS_CUSTODY.md:5-8`, `docs/phase0/OWNER_DECISIONS.json:33-36`, `ledgers/decision_log.md:1-366` | Open; owner-gated. |

### DET

| ID | Sev | Previous | Status | Evidence | Disposition |
|---|---|---|---|---|---|
| DET-P2-001 | P2 | open | **open** | `evidence/raw/REVIEW-FIX/20261013T053408Z_ci-p3-002-stale-workflow-cleanup.out:1-12`, `.gitattributes:32-34`, `automation/validation/pack_fidelity.py:43` | Open as a policy edge; not a code defect. The file is unchanged since f23ecff. |
| DET-P3-002 | P3 | open | **open** | `.github/workflows/validate.yml:99-108`, `automation/validation/gitleaks_history_check.sh:20-35`, live | Open (environmental); CI coverage intact. |
| DET-P3-003 | P3 | open | **owner-accepted** | `mct/compose/docker-compose.shuffle.yml:1-30`, `mct/compose/docker-compose.greenbone.yml:1-80`, `automation/wazuh/multi-node/generate-indexer-certs.yml:1-10` | Owner-accepted (was open). Count is 30 refs at HEAD vs 29 at edbf441; all covered by the same waivers. |
| DET-P3-004 | P3 | open | **open** | `.github/workflows/validate.yml:99-119`, live | Open (environmental/CI coverage). |

### RES

| ID | Sev | Previous | Status | Evidence | Disposition |
|---|---|---|---|---|---|
| RES-P1-002 | P1 | verified-fixed | **verified-fixed** | `automation/validation/disk_guard.sh:23-27`, `bootstrap/85-backup-job.sh:68-76`, live | Verified fixed with live evidence. |
| RES-P2-002 | P1 | verified-fixed | **verified-fixed** | `config/systemd/falcon-wazuh-agent-proxy.socket:10-16`, `config/systemd/falcon-wazuh-enroll-proxy.socket:10-16`, `automation/validation/boot_order_check.sh:38-58` | Verified fixed with post-fix boot evidence. |
| RES-P2-001 | P2 | open | **partially-fixed** | `docs/phase5/PERFORMANCE_ENVELOPE.md:6-16`, `compose/mct/iris-web/docker-compose.hardening.yml:1-58`, `automation/wazuh/multi-node/docker-compose.hardening.yml:1-80` | Partially fixed (was open): caps codified + envelope refreshed; pressure and budget residual remain. |
| RES-P3-001 | P3 | open | **open** | `automation/validation/tests/:1-1`, `automation/validation/tests/checks_platform_test.sh:1-20` | Open; unchanged. |
| RES-P3-002 | P3 | open | **open** | `automation/validation/post_reboot_verify.sh:1-3`, `config/systemd/:1-1`, `docs/runbooks/OPERATOR_START_HERE.md:102` | Open; recurrence of the IR-P2-005 class after a new boot. |

### DR

| ID | Sev | Previous | Status | Evidence | Disposition |
|---|---|---|---|---|---|
| DR-P1-002 | P1 | partially-fixed | **partially-fixed** | `bootstrap/80-offsite-backup.sh:286-289`, `bootstrap/80-offsite-backup.sh:305-312`, `bootstrap/80-offsite-backup.sh:408-414` | Partially fixed; live RPO currently met, code fail-closed gap remains. This is the scoped P1 called out by the task. |
| DR-P2-002 | P2 | partially-fixed | **partially-fixed** | `bootstrap/85-backup-job.sh:98-107`, `config/systemd/falcon-backup.service:6-8`, `bootstrap/80-offsite-backup.sh:500-501` | Partially fixed; ongoing writes encrypted, historical plaintext/SSE residual remains. |
| DR-P2-003 | P2 | partially-fixed | **verified-fixed** | `automation/validation/backup_new_services.sh:42-45`, `docs/phase7/runbooks/RESTORE.md:350`, `docs/runbooks/RETENTION_MATRIX.md:50` | Verified fixed (status flip from partially-fixed); residual fail-soft is tracked in the note. |
| DR-P2-004 | P2 | new | **open** | `bootstrap/80-offsite-backup.sh:286-289`, `bootstrap/80-offsite-backup.sh:305-312`, `bootstrap/80-offsite-backup.sh:570-575` | New 2026-11-08. P2 defense-in-depth; the original path trigger is fixed and live backups are healthy. The empty-repo case is the demonstrable vacuous pass. |
| DR-P3-001 | P3 | open | **open** | `automation/validation/restore_assertion.sh:1-114`, `ci/validate.py:445-459`, `config/systemd/:1-1` | Open; unchanged. |

### IR

| ID | Sev | Previous | Status | Evidence | Disposition |
|---|---|---|---|---|---|
| IR-P2-001 | P2 | open | **open** | `docs/phase9/exercises/TABLETOP_PACKAGE.md:3`, `docs/phase9/exercises/records/README.md:3-6`, `docs/phase9/exercises/records/TABLETOP_KIT.md:3` | Open; owner-gated. |
| IR-P2-002 | P2 | open | **open** | `docs/security/ESCALATION_CONTACTS_TEMPLATE.md:12-22,26-40`, `docs/security/ESCALATION_CONTACTS_TEMPLATE.md:42-46`, `docs/phase9/OWNER_ACTIONS.md:37` | Open; owner-gated. |
| IR-P2-003 | P2 | partially-fixed | **partially-fixed** | `ledgers/decision_log.md:268`, `docs/phase7/runbooks/INCIDENT_RESPONSE.md:274-279`, `docs/phase9/INCIDENT_2026-09-23_PYTHON_INTERPRETER.md:1-20` | Partially fixed; records exist, PIR/monthly review absent. |
| IR-P2-004 | P2 | partially-fixed | **verified-fixed** | `docs/runbooks/VPN.md:203`, `automation/validation/post_reboot_verify.sh:106-108`, `automation/validation/boot_check_readonly.sh:88` | Verified fixed (status flip); cosmetic comment residual. |
| IR-P2-005 | P3 | verified-fixed | **verified-fixed** | `ledgers/decision_log.md:268`, `CHANGELOG.md:64` | Verified fixed; no capture artifact residual. |

### OBS

| ID | Sev | Previous | Status | Evidence | Disposition |
|---|---|---|---|---|---|
| OBS-P2-001 | P2 | verified-fixed | **regressed** | `bootstrap/90-alerting.sh:636-638`, `docs/phase9/ALERT_CATALOGUE.yaml:1-6`, `README.md:33` | Regression. Counts verified 2026-11-08: script unique ids=95, catalogue ids=94, diff={falcon-edge-spool-unretained}. |
| OBS-P2-002 | P2 | partially-fixed | **partially-fixed** | `automation/validation/disk_guard.sh:31-34,110-122`, `bootstrap/90-alerting.sh:438-440`, `bootstrap/90-alerting.sh:148` | Partially fixed; no regression. |
| OBS-P2-003 | P2 | verified-fixed | **verified-fixed** | `automation/validation/export_monitor_metrics.sh:96-102`, `automation/validation/export_monitor_metrics.sh:567-569` | Verified fixed. |
| OBS-P2-004 | P2 | verified-fixed | **verified-fixed** | `automation/validation/export_monitor_metrics.sh:110-112,564-566`, `bootstrap/90-alerting.sh:701-707`, `config/checks/00-platform.yaml:13-17` | Verified fixed; runtime-bound residual tracked in DR-P1-002. |
| OBS-P3-001 | P3 | new | **open** | `config/systemd/falcon-console.service:4-5`, `automation/console/resolve_sources.sh:1-26`, `console/metrics.py:179-204` | New 2026-11-08. P3 operator-console degradation; Grafana/alerting remain the authoritative surfaces. |

### PERF

| ID | Sev | Previous | Status | Evidence | Disposition |
|---|---|---|---|---|---|
| PERF-P1-002 | P1 | verified-fixed | **verified-fixed** | `automation/validation/disk_guard.sh:23-27`, `bootstrap/90-alerting.sh:563-570,689-691`, live | Verified fixed with live evidence. |
| PERF-P2-001 | P2 | open | **partially-fixed** | `docs/phase5/PERFORMANCE_ENVELOPE.md:6-16`, `compose/mct/iris-web/docker-compose.hardening.yml:1-58`, `automation/wazuh/multi-node/docker-compose.hardening.yml:1-80` | Partially fixed (was open). |
| PERF-P2-002 | P2 | verified-fixed | **verified-fixed** | `automation/validation/disk_guard.sh:23-25`, `bootstrap/90-alerting.sh:559-561`, `docs/runbooks/CAPACITY_AND_TELEMETRY.md:39-50` | Verified fixed. |
| PERF-P2-006 | P2 | verified-fixed | **verified-fixed** | `docs/runbooks/CAPACITY_AND_TELEMETRY.md:45`, `automation/wazuh/migration/README.md:17-19`, `ledgers/decision_log.md:324` | Verified fixed; live archive not re-checked. |
| PERF-P2-007 | P2 | verified-fixed | **verified-fixed** | `bootstrap/90-alerting.sh:563-570`, `bootstrap/90-alerting.sh:689-691`, live | Verified fixed. |
| PERF-P3-001 | P3 | open | **partially-fixed** | `docs/phase5/PERFORMANCE_ENVELOPE.md:6-16`, `docs/architecture/STORAGE_CAPACITY_MODEL.md:7-21`, `docs/runbooks/CAPACITY_AND_TELEMETRY.md:75-81` | Partially fixed; envelope only. |
| PERF-P3-002 | P3 | open | **open** | `config/systemd/falcon-metrics.timer:6`, `automation/validation/export_monitor_metrics.sh:206-233`, `automation/validation/export_monitor_metrics.sh:50-59` | Open; cadence is 120 s (not 60 s), but the budget gap remains. |
| PERF-P3-008 | P3 | verified-fixed | **verified-fixed** | `.github/workflows/validate.yml:43-45`, `.github/workflows/validate.yml:56-61` | Verified fixed. |
| PERF-P3-009 | P3 | open | **partially-fixed** | `automation/validation/disk_guard.sh:69-87`, `bootstrap/90-alerting.sh:636-638`, `automation/validation/edge_spool_metrics.sh:1-28` | Partially fixed (was open): retention + rule added 2026-10-14; consumer/meaning residual. |

## Finding notes

### CI

**CI-P2-001 (P2, partially-fixed) — Auto-merge workflow holds contents:write with no environment protection**

- Prior: partially-fixed. The workflow still declares contents:write and pull-requests:write, runs on the self-hosted lab runner and has no GitHub environment/required reviewers. The TOCTOU half is fixed: it resolves headRefOid and merges with --match-head-commit. The label gate remains the only human disposition.
- Remediation: Reduce the token to the scopes gh pr merge/list/view actually need; add an environment with required reviewers when the plan permits, or convert the merge to an owner-run dispatch; exercise the label gate once and capture both skip and merge behavior.
- Verify note: Partially fixed: head pin present (dependabot-merge.yml:54); write scopes and env-less job unchanged. No code regression.

**CI-P2-002 (P2, regressed) — Independent Access-posture check no longer matches the live identity gate and is stuck in 'alerted'**

- Prior: verified-fixed. The accepted Access-enforcement control (DO watcher) still requires a Cloudflare Access challenge. After the 2026-11-05 Kestrel/Authentik cutover all three public hostnames redirect to idp.mainecybertech.us, so the watcher has logged 595 failures and remains in the 'alerted' state; repeated failures are suppressed. external-smoke accepts any 302 as an owner-IP bypass, so neither check now asserts the live gate. This is a regression of the CI-P2-002 closure.
- Remediation: Update watch.sh to accept the Kestrel/Authentik IdP redirect (and/or assert that an unauthenticated request cannot reach the app), reset the posture state, export a falcon_watcher_posture metric and alert on repeated failures; update external-smoke's summary/comment; add a synthetic negative test; record the Kestrel cutover in the decision log/maintenance window.
- Verify note: Regression. Live evidence 2026-11-08: public 302 -> idp.mainecybertech.us; watch.sh sha256 matches /opt/falcon-watcher/watch.sh; posture=alerted.

**CI-P2-003 (P2, partially-fixed) — Repository Actions settings remain partly permissive**

- Prior: partially-fixed. The dangerous default (write token / Actions can approve PRs) was fixed live on 2026-10-12. The remaining settings are allowed_actions='all' and sha_pinning_required=false. All three committed workflows declare their own permissions, so the residual is latent rather than currently exercised.
- Remediation: Set allowed_actions=selected and sha_pinning_required=true (or record a dated owner acceptance); add an API-settings inventory check so drift is visible.
- Verify note: Partially fixed; live settings were not re-checkable offline this pass. No repo-side change since edbf441.

**CI-P2-004 (P2, open) — CI installs two Python shell-test dependencies by bare version with no hashes or update path**

- Prior: new. The validate job runs on a self-hosted lab runner and installs cryptography 41.0.7 and PyJWT 2.7.0 from PyPI by version only. The install is not hash-pinned and is not covered by Dependabot, so a compromised or vulnerable release is neither integrity-checked nor automatically updated. The two packages are imported by console_test.sh in the shell-test suite.
- Remediation: Add both packages (current versions) to ci/requirements-ci.txt with --hash entries, install with --require-hashes, and let Dependabot cover the requirements file; re-run the shell tests.
- Verify note: New 2026-11-08. Severity P2 (supply chain on a self-hosted runner), not a runtime credential exposure.

**CI-P3-001 (P3, verified-fixed) — Hosted-runner fallback is gone and scheduled/queued CI failures are watched**

- Prior: verified-fixed. The dead hosted-runner fallback is removed; the watchdog runs every 15 minutes and exports falcon_ci_* metrics; fork PRs are skipped with a visible 'skipped' state.
- Remediation: None; keep the watchdog metric and alert coverage.
- Verify note: Verified fixed.

**CI-P3-002 (P3, verified-fixed) — Stale workflow registrations no longer exist**

- Prior: verified-fixed. The three orphan registrations were retired; the repository tree contains exactly three workflow files.
- Remediation: None; optionally add an API-vs-tree inventory assertion.
- Verify note: Verified fixed; live API not re-queried this pass.

**CI-P3-003 (P3, verified-fixed) — CI/CD incident playbook section 8 matches the pinned-tool state**

- Prior: verified-fixed. The playbook no longer claims only gitleaks is pinned or that validate was never exercised; it points at CI_TOOL_PINS.md and captured runs.
- Remediation: None for the pin text; see CI-P2-004 for the two inline Python installs that are not hashed.
- Verify note: Verified fixed.

**CI-P3-004 (P3, open) — Review package is still documented as a CI/release artifact but no CI job builds it**

- Prior: open. No workflow builds, attests or publishes the review package; the delivery remains a manual lab build bound by committed manifests. README still carries the stronger claim.
- Remediation: Either add a CI/release job that builds and uploads the package with attestations, or correct README to the manual lab-build path and link the manifest binding.
- Verify note: Open; no change since edbf441.

### BP

**BP-P2-001 (P2, verified-fixed) — CODEOWNERS resolves to the owner account**

- Prior: verified-fixed. Every CODEOWNERS entry resolves to the owner user account. Branch protection remains plan-blocked, so CODEOWNERS is advisory.
- Remediation: None; revisit if the owner account changes or a team is created.
- Verify note: Verified fixed; live API not re-queried this pass.

**BP-P3-001 (P3, open) — Dependabot auto-merge compensating control still has never been exercised**

- Prior: open. The label exists and gh is now installed on the lab runners, but no Dependabot PR has ever been opened or merged. The skip-without-label, merge-with-label and broken-gh failure modes remain unexercised.
- Remediation: Stage a Dependabot PR (or a fixture) and capture both behaviors; record the exercise date in the enforcement matrix.
- Verify note: Open; no evidence of an exercise since edbf441.

### SC

**SC-P2-002 (P2, partially-fixed) — Inherited credential estate is still partly unrotated and 20 vendored scripts source credential files wholesale**

- Prior: partially-fixed. The register has advanced to 9/20 (2 ROTATED + 7 DONE), but 11 owner-console rotations remain. Twenty tracked mct/scripts + mct/deploy-scripts files still combine set -a with a wholesale credential source; env_key.sh is used 0 times under mct/. The documentation still says 28 scripts and the register header still says 20/20 PENDING.
- Remediation: Execute the 11 owner rotations with name-only captures; migrate the 20 vendored scripts to single-key reads at the next MCT import or an owner-approved patch wave; correct the counts and header.
- Verify note: Partially fixed; no progress since edbf441 (still 9 rotated / 11 pending).

**SC-P3-001 (P3, verified-fixed) — Published package manifest equals the bound review-package manifest**

- Prior: verified-fixed. The shipped root manifest is byte-identical to the declared package manifest and the digest binds the same hash.
- Remediation: None; keep publish_digests.sh in the publication flow.
- Verify note: Verified fixed.

**SC-P3-002 (P3, verified-fixed) — Dependabot security updates are enabled**

- Prior: verified-fixed. Automated security-fix PRs are enabled at the repository level; the pip ecosystem covers ci/requirements-ci.txt.
- Remediation: None; see CI-P2-004 for the two inline CI packages outside the requirements file.
- Verify note: Verified fixed; live API not re-queried this pass.

### SBOM

**SBOM-P2-001 (P2, partially-fixed) — SBOM signature and license gate exist, but the manifest hash is not bound into PACKAGE_DIGEST**

- Prior: partially-fixed. The SBOM manifest signature verifies (ssh-keygen check-novalidate = Good) and the license allow-list gate runs in CI. The manifest hash is still not bound in PACKAGE_DIGEST.txt, D1 remains 'OWNER DECISION REQUIRED', and the publication verifier's 'signed archive' wording still overstates what it checks.
- Remediation: Add sbom_manifest_sha256 to PACKAGE_DIGEST.txt and bind it in publish_digests.sh; record D1 as implemented; reword the signed-archive check as SHA-256-only unless a signature is verified.
- Verify note: Partially fixed; core signing/license controls are live, binding/decision-record residual remains.

**SBOM-P3-001 (P3, verified-fixed) — Review package now ships the SBOM set**

- Prior: open. The delivered package manifest contains the SBOM/vuln set; a pack-only reviewer can inspect it.
- Remediation: None; keep the package rebuild and manifest rebind in the publication flow.
- Verify note: Verified fixed (status flip from open).

**SBOM-P3-002 (P3, partially-fixed) — SBOM enforcement document still contradicts the CI gate**

- Prior: open. The document contains an append-only correction but the original 'stays off' paragraph and D3 remain stale; a reader can still conclude the vulnerability gate is disabled. The live gate passes with all 25 images scanned and no pending waivers.
- Remediation: Append-only update the 2026-10-02 paragraph and D3 to the 2026-10-15 state (25/25 scanned, no pending waivers); keep the correction trail.
- Verify note: Partially fixed; correction exists but the contradictory text remains.

### CTR

**CTR-P2-001 (P2, partially-fixed) — Adopted stacks now have hardening overlays and healthchecks, but not the full baseline**

- Prior: open. Healthchecks and no-new-privileges are now codified for IRIS/Wazuh/OpenCanary and the forwarder carries --user/--cap-drop/health-cmd. The overlays are opt-in -f files, not the default compose path or a deploy-script argument; cap_drop and non-root users remain absent on the adopted IRIS/Wazuh services. The live healthcheck checks are green.
- Remediation: Wire the hardening overlays into the deployment path (default compose invocation or deploy script), add cap_drop/non-root where supported, and add a compose-config test asserting every adopted service has a healthcheck and no-new-privileges.
- Verify note: Partially fixed (was open at edbf441): repo overlays + live healthchecks landed 2026-10-14/15; default-path and cap_drop/non-root gaps remain.

**CTR-P3-001 (P3, partially-fixed) — Vendored MCT compose no longer mounts docker.sock but still carries unpinned refs under a blanket waiver**

- Prior: open. The host-root-equivalent docker.sock mounts are removed. The vendored tree still contains unpinned/floating image refs, now explicitly archive-only and covered by the owner-visible expiring waiver; the vendor manifest is checked in CI.
- Remediation: Keep the socket mounts off; keep the waiver scoped/expiring; record the archive-only acceptance in the exception register.
- Verify note: Partially fixed; remaining unpinned refs are owner-accepted for the archive-only tree until 2026-12-31.

**CTR-P3-002 (P3, open) — Local OpenSearch image installs the S3 plugin as root with no artifact checksum; rebuild mismatch is warn-only**

- Prior: open. The plugin install is not pinned to the recorded artifact hash and runs as root in the build layer. A rebuild that differs from the pinned local image only logs a warning.
- Remediation: Download the plugin zip, verify sha256 060a1bef..., install from the verified local file, and make a rebuild/digest mismatch fail closed (or require an explicit override).
- Verify note: Open; no change.

### SECRET

**SECRET-P2-001 (P2, partially-fixed) — Inherited credential estate is still 11/20 pending; vendored scripts still source stores wholesale**

- Prior: partially-fixed. Nine of twenty credential classes are dispositioned (2 ROTATED + 7 DONE), eleven owner-console rotations remain. Twenty vendored scripts still export whole credential files into their process environment; env_key.sh has zero uses under mct/.
- Remediation: Owner executes the 11 rotations with name-only captures; migrate the vendored scripts to single-key reads; correct the doc count.
- Verify note: Partially fixed; unchanged since edbf441.

**SECRET-P2-002 (P2, verified-fixed) — Owner-env validator is wired into the gate**

- Prior: verified-fixed. The validator is wired into ci/validate.py and the documented key set matches the live owner file as of the last live verification. The current verify host has no /home/user/.env, so the live check was skipped here.
- Remediation: None; keep the validator in the gate and refresh the inventory when a key is added.
- Verify note: Verified fixed (repo + prior live); live re-check not possible from this host.

**SECRET-P3-001 (P3, open) — Rotation register and vendored checklist still name pre-consolidation IRIS/MCT paths**

- Prior: open. The consolidated live stores are /srv/falcon/secrets/{mct,iris-web}.env, but the register row 19 and the vendored checklist still name the old /opt paths, so --live verification of those rows cannot be produced as written.
- Remediation: Annotate row 19 and the vendored checklist with the consolidated store paths (or a migration note); keep the vendored file unchanged per VENDORING P2 if that is the policy.
- Verify note: Open; unchanged.

**SECRET-P3-002 (P3, open) — Break-glass custody is still procedural only (OD-04 pending)**

- Prior: open. The procedure (custodians, sealed value, two-person rule, post-use rotation, annual review) is written but unchecked; no custodian, sealed credential or rehearsal is recorded.
- Remediation: Owner names custodians, seals the credential outside the host, runs the tabletop, and records the decision row.
- Verify note: Open; owner-gated.

### DET

**DET-P2-001 (P2, open) — [PORT] CRLF committed for 1 file (raw evidence capture; policy edge)**

- Prior: open. The only CRLF blob is a raw evidence capture that the line-ending policy intentionally exempts (*.out -text). It has no CI or execution impact; the machine lens will keep flagging it until a dated waiver is recorded.
- Remediation: Record a dated waiver in the audit register (or normalize the capture and re-hash/re-index it, which is not worth doing for a byte-exact capture).
- Verify note: Open as a policy edge; not a code defect. The file is unchanged since f23ecff.

**DET-P3-002 (P3, open) — [SEC] gitleaks is not installed on the host running the deterministic lens**

- Prior: open. CI has gitleaks coverage, but the host-side deterministic lens still reports the secret scan skipped because the binary is absent. This is an environment gap, not a repository regression.
- Remediation: Install the pinned gitleaks binary in the deterministic job image, or record the host-side skip as expected in the lens configuration.
- Verify note: Open (environmental); CI coverage intact.

**DET-P3-003 (P3, owner-accepted) — [SUPPLY] 30 container image refs without a digest pin (vendored/archive-only trees)**

- Prior: open. The unpinned refs are confined to the archive-only vendored MCT tree and a generation-only Wazuh helper. The owner decision (2026-10-15) accepts this state under an expiring waiver; the vendor-drift manifest and digest gates still pass.
- Remediation: Keep the waiver visible and expiring; re-evaluate at the next MCT import or before 2026-12-31; do not deploy the vendored tree.
- Verify note: Owner-accepted (was open). Count is 30 refs at HEAD vs 29 at edbf441; all covered by the same waivers.

**DET-P3-004 (P3, open) — [SUPPLY] hadolint is not installed and CI has no Dockerfile lint step**

- Prior: open. Dockerfile lint remains a coverage gap. The two Dockerfiles in the tree (OpenSearch S3 build, plus vendored) are not linted in CI.
- Remediation: Install hadolint in CI (pinned SHA-256) and lint compose/central/opensearch-s3.Dockerfile and any tracked Dockerfiles.
- Verify note: Open (environmental/CI coverage).

### RES

**RES-P1-002 (P1, verified-fixed) — Root LV is above the disk-guard threshold; guard/alert state is healthy**

- Prior: verified-fixed. Root free was 38.8 GB at 06:35Z, comfortably above the 20 GiB guard threshold; no root/disk alert is active. The earlier 19.6 GiB incident condition is not present.
- Remediation: None; keep the capacity watch and the keep-2 policy.
- Verify note: Verified fixed with live evidence.

**RES-P2-002 (P1, verified-fixed) — Wazuh VPN proxy socket boot race is fixed and has survived a boot**

- Prior: verified-fixed. The sockets use IP_FREEBIND and multi-user.target, and the live listener check is green after the 2026-11-05 boot. The historical sockets.target ordering cycle is gone.
- Remediation: None; keep the boot-order check wired into post_reboot_verify.sh.
- Verify note: Verified fixed with post-fix boot evidence.

**RES-P2-001 (P2, partially-fixed) — Host memory/swap pressure improved but remains; capacity budget is still not codified**

- Prior: open. Live memory available is 42.5% and swap 59.8%, below the alert bars; no OOM since 2026-10-09. The memory caps are now codified in the hardening overlays and the envelope has a current refresh section, but there is still no host-sized memory budget and the pressure is real.
- Remediation: Add a measured per-service memory budget for the 16.9 GB host, keep the caps in the default deploy path, and re-measure after a week.
- Verify note: Partially fixed (was open): caps codified + envelope refreshed; pressure and budget residual remain.

**RES-P3-001 (P3, open) — Failure-injection coverage still omits the failure modes that actually occurred**

- Prior: open. The suite still lacks bounded injections for aggregator OOM, host memory pressure, boot-order/socket failure and root-LV exhaustion - the four classes that hit the lab in 2026-10/11.
- Remediation: Add one bounded injection per class, each asserting detection and recovery and recording a stamp.
- Verify note: Open; unchanged.

**RES-P3-002 (P3, open) — Post-reboot verification is still manual and the 2026-11-05 boot has no record**

- Prior: open. There is no boot-time post-reboot verification unit. A host boot on 2026-11-05 22:50Z (after the Kestrel cutover window) has no decision-log/maintenance-window row and no captured post-reboot check.
- Remediation: Wire post_reboot_verify.sh (or a bounded read-only subset) to a boot-time oneshot and record the result; add a maintenance-window/decision-log row for the Kestrel cutover and the boot.
- Verify note: Open; recurrence of the IR-P2-005 class after a new boot.

### DR

**DR-P1-002 (P1, partially-fixed) — Offsite upload-state truncation class is still not fail-closed; live RPO is currently met**

- Prior: partially-fixed. The live nightly path is healthy (all backup/offsite/DLQ checks green at 2026-11-08T06:43Z) and the original symlink path is fixed. The hardening asked for in the finding is still absent: an empty/shrunk enumeration can be persisted as state, a missing repository returns success, an empty inventory makes the sample verification vacuous, and the oneshot service has no runtime bound (the stuck-activating rule waits 8h).
- Remediation: Refuse to persist an empty state or a state that shrinks by more than a threshold; fail when the local repository has fewer than a minimum number of files; bound falcon-backup.service with RuntimeMaxSec/TimeoutStartSec; add an offline test for the empty/shrunk cases.
- Verify note: Partially fixed; live RPO currently met, code fail-closed gap remains. This is the scoped P1 called out by the task.

**DR-P2-002 (P2, partially-fixed) — Nightly offsite is encrypted, but historical plaintext bulk objects remain and SSE is not set**

- Prior: partially-fixed. The nightly bulk upload now goes through the rclone crypt remote and was verified end-to-end on 2026-10-13. The pre-migration plaintext objects are still in the bucket (the runbook's step 4 is owner-gated), no bucket/object SSE is configured, and a manual 80 run without OFFSITE_CRYPT still writes plaintext.
- Remediation: Complete the owner-approved plaintext retirement; enable SSE on the bucket/objects as defense in depth; make OFFSITE_CRYPT=1 the script default or refuse plaintext without an explicit override; add a decrypt-from-escrow drill.
- Verify note: Partially fixed; ongoing writes encrypted, historical plaintext/SSE residual remains.

**DR-P2-003 (P2, verified-fixed) — IRIS case database is dumped daily and shipped encrypted offsite**

- Prior: partially-fixed. The IRIS database is included in the daily new-services archive, retained locally for 7 days and shipped encrypted offsite; the coverage matrix and RESTORE.md now agree. Residual: pg_dump is fail-soft and the critical-item gate does not explicitly require the .iris-db file.
- Remediation: Add the .iris-db-<stamp>.sql entry to the critical-item check (or fail the archive when pg_dump produced nothing) and record a restore drill using the dump.
- Verify note: Verified fixed (status flip from partially-fixed); residual fail-soft is tracked in the note.

**DR-P2-004 (P2, open) — Offsite verification passes vacuously on an empty or unexpectedly tiny snapshot repository**

- Prior: new. A present-but-empty or unexpectedly tiny local snapshot repository produces a clean offsite verification: the sample loop has zero iterations and offsite_verify_all.py reports total=0/mismatched=0 PASS. The upload state is then replaced with the empty enumeration and the success stamp advances. upload_repo_delta also returns success when the directory is missing, leaving the caller to fail later; the 2026-10-10 incident was caught by a later download failure, not by a fail-closed minimum-size check.
- Remediation: Fail when the local repository has fewer than a minimum file count (or shrinks more than a configured fraction); make a missing repo a hard failure for both targets; assert total>0 before verification and before writing state; add an offline test for empty/missing/shrunk repositories.
- Verify note: New 2026-11-08. P2 defense-in-depth; the original path trigger is fixed and live backups are healthy. The empty-repo case is the demonstrable vacuous pass.

**DR-P3-001 (P3, open) — Scheduled end-to-end live restore assertion is still absent**

- Prior: open. The offline assertion runs in CI, but no systemd timer runs a live restore/drill and the last live rehearsal remains 2026-10-01.
- Remediation: Add a monthly timer that runs the offline assertion plus a bounded live rehearsal with a success stamp and staleness rule.
- Verify note: Open; unchanged.

### IR

**IR-P2-001 (P2, open) — No facilitated tabletop exercise has been run**

- Prior: open. The 10-scenario catalogue and Scenario 5 kit exist, but no facilitated session or signed record exists. Scenario 5 (total monitoring/alerting loss) remains unexercised.
- Remediation: Schedule and record a facilitated owner + responder + independent reviewer session, starting with Scenario 5; measure out-of-band latency; repeat quarterly.
- Verify note: Open; owner-gated.

**IR-P2-002 (P2, open) — Escalation contacts remain placeholders**

- Prior: open. Every escalation role/contact/out-of-band field is still OWNER-INPUT and the verification log is empty. The documented path cannot be followed by a second responder.
- Remediation: Fill the contact table in owner custody, verify at least one out-of-band channel end to end, and record the verification log.
- Verify note: Open; owner-gated.

**IR-P2-003 (P2, partially-fixed) — Recurring incidents still lack post-incident review**

- Prior: partially-fixed. Incident rows are kept in the decision log, but there is still no dedicated post-incident review for the recurring events (Oct 20 power outage, Nov 2 outage, Nov 5 Kestrel cutover/reboot) and no monthly recurrence review. The 2026-09-23 postmortem remains the only full example.
- Remediation: Run and record a post-incident review for each material event (timeline, root cause, impact, follow-ups); add a monthly recurrence review of incident/alert history.
- Verify note: Partially fixed; records exist, PIR/monthly review absent.

**IR-P2-004 (P2, verified-fixed) — Wazuh proxy boot-order fix has now survived a boot; the stale comment is cosmetic**

- Prior: partially-fixed. The 2026-10-11 FreeBind fix has now survived a host boot (2026-11-05) and the live listener check is green; the runbook correction is in place. The only residual is the stale 2026-09-30 comment in post_reboot_verify.sh/boot_check_readonly.sh and the lack of a captured boot-order run for this boot.
- Remediation: Correct the two stale comments and capture a boot-order check on the next reboot.
- Verify note: Verified fixed (status flip); cosmetic comment residual.

**IR-P2-005 (P3, verified-fixed) — The 2026-10-11 reboot/post-reboot verification is recorded**

- Prior: verified-fixed. The Oct 11 reboot, the socket outage and the root-LV loop are recorded with the 59/0 post-reboot result. Residual: no dedicated evidence capture for the 59/0 run.
- Remediation: Capture the next post-reboot run; use the same record format.
- Verify note: Verified fixed; no capture artifact residual.

### OBS

**OBS-P2-001 (P2, regressed) — Alert catalogue/README/CURRENT_STATE drifted again: script has 95 rules, catalogue has 94**

- Prior: verified-fixed. The script provisions 95 unique rules but the catalogue, README and CURRENT_STATE all say 94; the missing id is falcon-edge-spool-unretained. The 2026-10-14 drift check still cannot see it because it compares README to the catalogue rather than the script to the catalogue. This is a regression of the verified-fixed status at edbf441.
- Remediation: Regenerate the catalogue (95 ids) and the counts, and add a script-vs-catalogue id set comparison to the drift test so a future rule cannot land without the catalogue.
- Verify note: Regression. Counts verified 2026-11-08: script unique ids=95, catalogue ids=94, diff={falcon-edge-spool-unretained}.

**OBS-P2-002 (P2, partially-fixed) — Alert noise is improved but repeat/reboot tuning remains**

- Prior: partially-fixed. The disk-guard root storm is over and the guard now throttles persistent conditions to 6 h. The Suricata restart rule is still not reboot-aware, repeat_interval remains 4 h, and the documented 7-day noise accounting has not been re-run.
- Remediation: Make the Suricata rule reboot-aware (or annotate planned reboots), re-tune repeat_interval/grouping, and re-run the 7-day accounting.
- Verify note: Partially fixed; no regression.

**OBS-P2-003 (P2, verified-fixed) — Benign edge_ingest HTTP rejections are excluded from the data-loss signal**

- Prior: verified-fixed. The exclusion and separate metric are intact; no discarded-events alert has fired since 2026-10-11.
- Remediation: None.
- Verify note: Verified fixed.

**OBS-P2-004 (P2, verified-fixed) — Stuck/failed backup runs and generic systemd unit failure are visible**

- Prior: verified-fixed. The backup unit state metric and both rules are live; the check engine adds a generic systemd failed-units check. The backup/stuck checks are green.
- Remediation: Add RuntimeMaxSec to falcon-backup.service (see DR-P1-002 residual).
- Verify note: Verified fixed; runtime-bound residual tracked in DR-P1-002.

**OBS-P3-001 (P3, open) — Console Prometheus-backed sections are blank after the 2026-11-05 reboot**

- Prior: new. The console's Prometheus-backed capacity/pipeline/infrastructure/trends sections are empty while the textfile/OpenSearch-backed checks and security counts still work. The service resolves container IPs only at start and has no Docker dependency; that design is consistent with a stale/empty Prometheus URL after a container recreate or start-order change. The exact root cause was not observable without lab-host access. Grafana and the alert rules are unaffected.
- Remediation: Resolve the source URLs at each request or on a short timer (or use a stable Docker DNS/published endpoint); add After/Requires docker.service; export a console source-freshness metric and alert on it.
- Verify note: New 2026-11-08. P3 operator-console degradation; Grafana/alerting remain the authoritative surfaces.

### PERF

**PERF-P1-002 (P1, verified-fixed) — Root LV incident condition is cleared; guard and projection rules are healthy**

- Prior: verified-fixed. The live root LV is above the guard threshold and no disk alert is active. The 2026-10-11 regression is not present.
- Remediation: None; keep the capacity watch.
- Verify note: Verified fixed with live evidence.

**PERF-P2-001 (P2, partially-fixed) — Memory/swap pressure remains; caps and envelope were refreshed**

- Prior: open. Caps are now codified and the envelope has a current refresh, but live memory available (42.5%) and swap (59.8%) show persistent pressure and there is no host-sized memory budget.
- Remediation: Add a measured per-service budget for the 16.9 GB host and keep the caps in the default deploy path.
- Verify note: Partially fixed (was open).

**PERF-P2-002 (P2, verified-fixed) — Data-LV guard/alert thresholds sit above the OpenSearch watermarks**

- Prior: verified-fixed. The guard acts at 24 GiB free and the warning at 30 GiB, both before the 224 GiB volume's flood-stage watermark; the documentation matches.
- Remediation: None.
- Verify note: Verified fixed.

**PERF-P2-006 (P2, verified-fixed) — Stale migration bundle is archived off the root LV with a review date**

- Prior: verified-fixed. The 21.7 GiB bundle was moved to /srv/falcon/archive/wz-migration (cmp-verified) and has a 2027-01-31 review date; it is off the root LV. No live re-check of the archive was possible from this host.
- Remediation: Keep the review date; decide retention at 2027-01-31.
- Verify note: Verified fixed; live archive not re-checked.

**PERF-P2-007 (P2, verified-fixed) — Projection and root-free rules now cover the actual constraint**

- Prior: verified-fixed. The projection rules use a 24 h window and the root-free rule evaluates the guard's own 20 GiB threshold; all three checks are green.
- Remediation: None.
- Verify note: Verified fixed.

**PERF-P3-001 (P3, partially-fixed) — Performance envelope refreshed, but the capacity model, unit costs and budgets are stale**

- Prior: open. The operating envelope has a 2026-10-14 refresh section, but the storage model still describes the Phase-0 74/60 GiB plan, the cost register has no unit costs, and no ingest-lag/snapshot/exporter/root-free budgets exist.
- Remediation: Refresh STORAGE_CAPACITY_MODEL to the current 171 GiB root/224 GiB data layout; fill the unit-cost/budget cells; add the missing performance budgets.
- Verify note: Partially fixed; envelope only.

**PERF-P3-002 (P3, open) — Whole-cluster monitoring queries still run every 120 s with no exporter runtime budget**

- Prior: open. The exporter still runs whole-cluster aggregations on the single-node cluster every 120 s and publishes no self-runtime metric or budget.
- Remediation: Publish the exporter duration/query cost and add a budget alert; consider narrowing the whole-index latest query.
- Verify note: Open; cadence is 120 s (not 60 s), but the budget gap remains.

**PERF-P3-008 (P3, verified-fixed) — CI tool and Python dependency caching is in place**

- Prior: verified-fixed. The validate workflow caches pip and the pinned tool tarballs; the cache steps are still present.
- Remediation: None.
- Verify note: Verified fixed.

**PERF-P3-009 (P3, partially-fixed) — Edge spool now has 7-day retention, but its data-loss meaning and consumer remain unverified**

- Prior: open. The spool is now bounded centrally (7 days) and a not-pruned rule exists; no live consumer of the spool is configured and the purge counter's data-loss meaning is still unverified. The new rule is also the source of the OBS-P2-001 catalogue drift.
- Remediation: Confirm whether an edge-side consumer exists; if not, retire the spool or document it as dead-letter; keep the retention/rule.
- Verify note: Partially fixed (was open): retention + rule added 2026-10-14; consumer/meaning residual.

## Live evidence used (2026-11-08, read-only)

| Check | Observation |
|---|---|
| Host disk | `/` 183.3 GB total, 38.85 GB free (74.3% used); `/srv/falcon` 82.85 GB free (60.6% used) |
| Host memory | 42.5% available (7.18 GB of 16.9 GB); textfile swap 59.83% |
| Host uptime | 200,710 s at 06:35Z -> boot 2026-11-05 22:50Z |
| Backup/offsite | `Backup stale`, `Offsite backup stale`, `Offsite backup retries exhausted`, `Backup unit failed`, `Backup run stuck activating` all **ok** |
| Disk checks | `Disk space low`, `Disk space critical`, `Root volume free space low`, `Root disk projected full`, `Data volume free space low`, `Data volume projected full` all **ok** |
| Wazuh proxy | `Wazuh VPN proxy listener down` **ok** after the 2026-11-05 boot |
| Containers | `Container healthcheck failing`, `Container unhealthy`, `Container configuration drift` **ok** |
| Console | `/console/api/v1/overview` warning `prometheus queries returned no data`; capacity fields null; pipeline/infrastructure/trends empty |
| DO watcher | Public hostnames 302 -> `https://idp.mainecybertech.us/...`; 595 posture failures; `posture` state `alerted`; every run logs `posture already alerted` |
| Package binding | `PACKAGE_MANIFEST.sha256` == `review-package/MANIFEST.sha256` == `fd9ee76a...`; 4,394 entries; digest equal |
| SBOM | `sbom_hashes.sh verify` PASS (52 artifacts, signed ed25519); coverage 25/25 scanned, 0 pending; license gate PASS; manifest freshness 24d |
| Rotation | `check_rotation_register.py` -> 20 items, 9 rotated/DONE, 11 pending |
| Deterministic | `ci/validate.py --only compose-pins/compose-digests/vendor-drift/secret-scan/shellcheck/sbom-licenses/sbom-freshness/lock-age` all PASS in this environment |

## Notable status flips since edbf441

- **CI-P2-002 -> regressed**: the DO watcher still requires a Cloudflare Access redirect; the live gate is Kestrel/Authentik. The accepted independent enforcement check is dead and stuck in 'alerted'.
- **OBS-P2-001 -> regressed**: 95 provisioned rules vs 94 catalogue/README/CURRENT_STATE; the new falcon-edge-spool-unretained rule is the missing id.
- **SBOM-P3-001 -> verified-fixed**: the review package now ships the SBOM set (56 sbom entries, 25 cdx.json).
- **DR-P2-003 -> verified-fixed**: IRIS pg_dump is daily, shipped encrypted offsite, and RESTORE.md/RETENTION_MATRIX agree; residual fail-soft tracked.
- **IR-P2-004 -> verified-fixed**: the FreeBind fix has survived the 2026-11-05 boot and the live listener check is green; stale comment remains.
- **CTR-P2-001 -> partially-fixed**: hardening overlays + live healthchecks landed 2026-10-14/15; default-path/cap_drop/non-root gaps remain.
- **DET-P3-003 -> owner-accepted**: 30 unpinned refs are confined to the archive-only vendored trees under the expiring 2026-12-31 waiver.

## Limitations

- No SSH/lab-host filesystem or systemd/Docker access from this verify host; live state was read through the Falcon Console API, the DO watcher, and public HTTPS only.
- GitHub repository-settings APIs (`allowed_actions`, `sha_pinning_required`, `automated-security-fixes`, CODEOWNERS errors) were not reachable; those rows carry the last live observation and are marked accordingly.
- `EVOL-P1-001` is outside G2 and was not re-verified. `EVOL-P1-002` / pin-gate coverage was spot-checked only through the compose/vendor gates.
- No secrets, credential values, tokens or full redirect query strings are reproduced in this report.

