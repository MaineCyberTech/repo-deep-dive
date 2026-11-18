# Post-merge verification re-audit — falcon @ `edbf441` (2026-10-14)

- Run: `falcon-20261014-verify-main-edbf441`
- Target: `MaineCyberTech/falcon` @ `edbf441d03cfba1f2a2e923a94021e1cbab0c338` (main, clean tree), 2026-10-14.
- Original run: `falcon-20261011-0416-full-f5cb7c9` (126 findings).
- Previous verification: `falcon-20261012-verify-main-3623d2e` @ `3623d2e` (2026-10-12).
- Method: machine deterministic pass (`lens_deterministic.md`) + eight themed LLM verification
  reports (`90..97_verification_*.md`); repo inspection at `edbf441` plus read-only live checks
  (docker/systemctl/journalctl, Prometheus/Grafana read APIs, textfile metrics, GitHub API).
  No mutations; secrets never reproduced.

## Verdict summary

| Verdict | Count |
|---|---:|
| verified-fixed | 49 |
| partially-fixed | 26 |
| open | 49 |
| owner-accepted | 2 |
| **regressed** | **1** |
| total | 127 (126 re-checked + 1 new machine finding) |

Per-finding verdicts and evidence: `verification_log.md`. Registers: `risk_register.md`,
`follow_up_register.md`.

## Notable status flips since `3623d2e`

- **CI-P3-001 / CI-P3-002 → verified-fixed** (`f23ecff`): fork PRs are skipped (no hosted
  fallback), the CI watchdog timer is live with `falcon_ci_*` metrics, and the three stale
  workflow registrations are gone.
- **WH-P1-001 → partially-fixed**: disk buffer + end-to-end acks + bounded retry are live and in
  main; `automation/vector/dlq_replay.sh` is live-tested. Residual: non-retriable sink rejects
  have no capture/replay (vector 0.58 lacks `reroute_dropped`).
- **PERF-P2-007 → verified-fixed**: both projection rules evaluate over `[24h]` (repo + live).
- **WZ-VOLUME wave**: `falcon_wazuh_alerts_5m` / high-severity are indexer-sourced with runtime
  creds (live 606 vs independent 601); the volume-drop rule and the 94-rule catalogue are synced;
  the per-feed freeze has a documented silence to 2026-10-20 (forwarder repoint still open).
- **EVOL-P1-002 → verified-fixed** (pin gate covers `mct/compose` + `automation/wazuh` with
  expiring waivers); **EVOL-P1-001 → partially-fixed** (edge side still has no lock/check).
- **SECRET-P2-002 / SECRET-P2-006 / ACM-P2-003 / SEC-P3-005 → verified-fixed** (owner-env
  validator wired + live PASS; deployed enrollment service matches the repo; secure cookies live).
- **INV-P3-002 → regressed** (see below).

## Regressions

- **INV-P3-002 (P3) — regressed**: the fresh repomix (`e62348a`) again ships an unresolved entry
  in `PACK_NOT_INCLUDED.txt` — `evidence/raw/REVIEW-FIX/20261001T202630Z_sec-p3-001-gitleaks-tree.out
  → not-in-pack (unexpected; investigate)`. Repomix drops the file as binary because of ANSI
  escapes (the 2026-10-11 fix `5e8b262` addressed exactly this; the regenerated pack at `e62348a`
  reintroduced it). Disposition: either strip the ANSI escapes from the capture (needs the
  evidence manifest + capture-meta hash updates and a redactions-ledger row) or record a dated
  waiver. No P0/P1 regressions.

## New findings

| ID | Sev | Finding | Evidence |
|---|---|---|---|
Observations (not defects): the data-LV capacity projection is genuinely firing (fired
2026-10-13T22:39Z, ~64 GB free / 70 % used — owner capacity watch); the DO site host disk is at
86.1 % and rising (already covered by its rule).

DET-P2-001 (P2, machine) — one committed CRLF evidence blob
(`…20261013T053408Z_ci-p3-002-stale-workflow-cleanup.out`, mixed CRLF/LF, hash-bound in
`evidence/MANIFEST.sha256:2280`). The `.gitattributes` policy intentionally exempts raw captures
(`*.out -text`); assessed as a low-impact policy edge — recommend a recorded waiver rather than
renormalizing (which would break the manifest hash). Details in `lens_deterministic.md` and
report 93 N-1.
| NEW-1 (CI/BP) | P2 | The Dependabot sweep still runs where `gh` is missing: latest sweep run `38399605845` (edge-builder, 2026-10-13T12:45Z) logs `gh: command not found` → "no open dependabot PRs", exit 0. The label gate and pinned merge remain non-functional on that runner; `BRANCH_PROTECTION.md:84-86` still asserts the gate is live. Fix: install `gh` on the `lab` runners or fail closed / use REST calls. | report 91 NEW-1 |
| NEW-2 / INV-P3-002 | P3 | `PACK_NOT_INCLUDED.txt` unresolved pack entry (the regression above). | reports 91 NEW-2, 93 |
| NEW-1 (DATA/DR) | P3 | `offsite_crypt.key` has no off-host escrow attestation (`CUSTODY_ATTESTATION.md` covers only `backup_enc.key`; OD-04 pending) while it now protects the only maintained offsite copy. Must be resolved before the runbook's step 4 (retire plaintext) proceeds. | report 92 NEW-1 |
| NEW-A (CI/TEST) | P3 | The dedicated SEC-001 gitleaks curl-allowlist step is a guaranteed SKIP: `validate.yml:107-110` points `GITLEAKS_BIN` at `$RUNNER_TEMP/gitleaks` while the binary lives in `$HOME/.cache/falcon-ci-tools/gitleaks`. Coverage survives only via the shell-suite gate. Fix: point the variable at the cached binary. | report 94 NEW-A |
| NF-1 (PRIV/DATA) | P3 | The 2026-10-13 AP-exposure detection (raw BSSID/SSID of neighbouring APs; `EdgeSensorNewApDetected`) is not covered by any falcon privacy/retention document; the rule's referenced runbook exists only in the edge repo. | report 96 NF-1 |
| NF-2 (IR/SEC) | P3 | The only IRIS token-rotation runbook is vendored and stale (targets the decommissioned VM101/retired Shuffle); no first-party procedure. | report 96 NF-2 |
| N-2 (DOC) | P3 | `RELEASE_PACK_VERIFICATION.md:81` / `CI_GOVERNANCE_RECONCILIATION.md:63` still describe the now-wired pack fidelity as open/partial; the notes file lacks a verdict header. | report 93 N-2 |
| N-3 (doctrine) | P3 | `EVOLUTION_GUIDE.md:89` still omits the declared-manifest exception; the `check_publication_equality.py` fail-open skip path is untested. | report 93 N-3 |

Observations (not defects): the data-LV capacity projection is genuinely firing (fired
2026-10-13T22:39Z, ~64 GB free / 70 % used — owner capacity watch); the DO site host disk is at
86.1 % and rising (already covered by its rule).

## Gate

**GO WITH CONDITIONS** — 0 P0; no P1 regressions; the regressed/new items above are P2/P3 and
tracked in the registers; owner-gated residuals (rotations, retention, EVOL, C1) recorded.
