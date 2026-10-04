# Follow-up register

Owner/Target/Status columns drive tools/collect_findings.py enrichment.

| ID | Severity | Title | Owner | Target | Status | Post-audit note |
|---|---|---|---|---|---|---|
| FINAL-P0-001 | P0 | Production-readiness claim is unsupportable at this commit (release integrity) |  |  | verified-fixed | re-audit 2026-10-04: closed |
| HYG-P0-001 | P0 | Publication digest and closeout declare commits that do not match the audited tree |  |  | verified-fixed | re-audit 2026-10-04: closed |
| HYG-P0-002 | P0 | The mandated publication-chain verifier could not be reproduced and the chain is not bound to HEAD |  |  | verified-fixed | re-audit 2026-10-04: closed |
| OBS-P0-001 | P0 | Prometheus scrapes only 3 targets; nearly all `falcon_*` signals hinge on the node-exporter textfile collector |  |  | still-open | re-audit 2026-10-04: still-open |
| API-P1-001 | P1 | Cross-repo pairing contract cannot be verified in this environment |  |  | still-open | re-audit 2026-10-04: still-open |
| ARCH-P1-001 | P1 | Single-host concentration: host loss is total pipeline loss |  |  | still-open | re-audit 2026-10-04: still-open |
| ARCH-P1-002 | P1 | Abort-marker contract is self-contradictory and normal failure exits leave no marker |  |  | verified-fixed | re-audit 2026-10-04: closed |
| CI-P1-001 | P1 | CI tool downloads did not fail fast |  |  | verified-fixed | re-audit 2026-10-04: closed |
| CI-P1-002 | P1 | Branch protection and required checks are not enforced server-side |  |  | owner-accepted | re-audit 2026-10-04: still-open (owner-accepted; plan-gated) |
| DATA-P1-001 | P1 | Wazuh and IRIS data have no retention (unbounded index growth) |  |  | still-open | re-audit 2026-10-04: still-open |
| EXEC-P1-001 | P1 | Lab "GO" can be misread as a production approval |  |  | verified-fixed | re-audit 2026-10-04: closed |
| FINAL-P1-001 | P1 | Operational resilience remains incomplete across the backup lifecycle |  |  | still-open | re-audit 2026-10-04: still-open |
| HYG-P1-001 | P1 | Committed `review-package/` is a stale snapshot duplicate of the source tree |  |  | still-open | re-audit 2026-10-04: still-open |
| HYG-P1-002 | P1 | Secret-scanner path allowlist was not separator-portable |  |  | verified-fixed | re-audit 2026-10-04: closed |
| OBS-P1-001 | P1 | Alert expressions mix `bool` and raw comparison forms with no linter |  |  | verified-fixed | re-audit 2026-10-04: closed |
| OBS-P1-002 | P1 | Duplicate/overlapping rules and a self-contradictory firing-proof coverage total |  |  | verified-fixed | re-audit 2026-10-04: closed |
| OBS-P1-003 | P1 | Relay failure counter is all-or-nothing; partial-path degradation is caught only by the weekly canary |  |  | verified-fixed | re-audit 2026-10-04: closed |
| SEC-P1-001 | P1 | OpenCanary publishes six decoy services on all interfaces |  |  | verified-fixed | re-audit 2026-10-04: closed |
| SEC-P1-002 | P1 | Blanket `iifname "wg0" accept` grants every WireGuard peer host-wide access |  |  | verified-fixed | re-audit 2026-10-04: closed |
| SEC-P1-003 | P1 | Owner-directed open-inbound override state is contradictory across records |  |  | verified-fixed | re-audit 2026-10-04: closed |
| SUPPLY-P1-001 | P1 | Container digest gate scope hole: vendored `mct/compose` and `automation/wazuh` are ungated |  |  | verified-fixed | re-audit 2026-10-04: closed |
| SUPPLY-P1-002 | P1 | Vulnerability scanning is not gated and coverage is partial |  |  | verified-fixed | re-audit 2026-10-04: closed |
| TEST-P1-001 | P1 | Repo-local test ledger points at an out-of-repo, pre-rename lab tree |  |  | verified-fixed | re-audit 2026-10-04: closed |
| TEST-P1-002 | P1 | The full gate does not complete within a short bounded run and shell suites are not executable off a bash host |  |  | verified-fixed | re-audit 2026-10-04: closed |
| API-P2-001 | P2 | Enrollment API tokens have no expiry field |  |  | verified-fixed | re-audit 2026-10-04: closed |
| API-P2-002 | P2 | Ingest contract relies on a shared secret header, not request signing or idempotency keys |  |  | partially-fixed | remediation PS-U01 open c04c0068c182b7d61521978f154f5ac33ae42c2a https://github.com/MaineCyberTech/falcon/pull/21 |
| ARCH-P2-001 | P2 | Declared container hardening lags the running containers |  |  | partially-fixed | remediation PS-U02 open 41cd5a1e65e22f7ef1e957605bb0f0df2755328d https://github.com/MaineCyberTech/falcon/pull/22 |
| ARCH-P2-002 | P2 | Wazuh and vendored MCT stacks run tag-only images outside pin/SBOM scope |  |  | partially-fixed | remediation PS-U02 open 41cd5a1e65e22f7ef1e957605bb0f0df2755328d https://github.com/MaineCyberTech/falcon/pull/22 |
| ARCH-P2-003 | P2 | Live ingest authentication is a shared secret header, not mTLS |  |  | partially-fixed | remediation PS-U02 open 41cd5a1e65e22f7ef1e957605bb0f0df2755328d https://github.com/MaineCyberTech/falcon/pull/22 |
| ARCH-P2-005 | P2 | Only the backup job installs the abort trap; other long-running jobs lack it |  |  | verified-fixed | re-audit 2026-10-04: closed |
| CI-P2-001 | P2 | `ci/validate.py` did not implement the evidence-index verification its docstring promises |  |  | verified-fixed | verified-fixed at base; PS-U03 added an offline regression guard (375c4fb) |
| CI-P2-002 | P2 | Auto-merge workflow holds `contents: write` with no environment protection |  |  | still-open | re-audit 2026-10-04: still-open |
| DATA-P2-001 | P2 | Index template and `event_time` ownership are split with no consistency check |  |  | verified-fixed | re-audit 2026-10-04: closed |
| FEAT-P2-001 | P2 | Vendored MCT services are present in Compose while the subtree policy calls the tree archive-only |  |  | partially-fixed | remediation PS-U06 open f19acdbbb7670673446fa86df51f0e3374cd3057 https://github.com/MaineCyberTech/falcon/pull/33 |
| FEAT-P2-002 | P2 | Backup/offsite delivery is single-attempt with no retry, backoff, or dead-letter |  |  | verified-fixed | re-audit 2026-10-04: closed |
| HYG-P2-001 | P2 | Large generated SBOM/vulnerability JSON committed (39 files, up to ~122 KB each) |  |  | partially-fixed | remediation PS-U08 open 3a200c9fe33c51c97a9e348fc5f32c846344a72b https://github.com/MaineCyberTech/falcon/pull/26 |
| INV-P2-001 | P2 | Repository is majority generated/derived content with no in-repo regeneration or drift check |  |  | partially-fixed | remediation PS-U09 open e31523a59c945126e1b3e1e6ea9e630559292812 https://github.com/MaineCyberTech/falcon/pull/32 |
| SEC-P2-001 | P2 | Public-facing routers have no origin authentication; `ntfy-auth` is dead config |  |  | still-open | re-audit 2026-10-04: still-open |
| SEC-P2-002 | P2 | Cloudflare API token is passed on the `curl` command line |  |  | verified-fixed | re-audit 2026-10-04: closed |
| SUPPLY-P2-001 | P2 | `.gitleaks.toml` allowlists are broader than the documented classified set |  |  | verified-fixed | re-audit 2026-10-04: closed |
| SUPPLY-P2-002 | P2 | Image lock freshness is not gated |  |  | verified-fixed | re-audit 2026-10-04: closed |
| TEST-P2-001 | P2 | No backup/offsite/restore end-to-end test runs in the standard gate |  |  | verified-fixed | re-audit 2026-10-04: closed |
| CI-P3-001 | P3 | Local and CI shellcheck semantics diverged |  |  | verified-fixed | verified-fixed at base; PS-U03 added an offline regression guard (375c4fb) |
| INV-P3-001 | P3 | Legacy host-absolute evidence paths require manual rewrite to resolve in a clone |  |  | partially-fixed | remediation PS-U09 open e31523a59c945126e1b3e1e6ea9e630559292812 https://github.com/MaineCyberTech/falcon/pull/32 |
| SEC-P3-001 | P3 | Default-deny `forward`/`output` policies are inert at the managed-table level |  |  | verified-fixed | re-audit 2026-10-04: closed |
| SUPPLY-P3-001 | P3 | `pins/verify-digests.sh` compares only the first RepoDigest entry |  |  | verified-fixed | re-audit 2026-10-04: closed |
