# Follow-up register

Owner/Target/Status columns drive tools/collect_findings.py enrichment.

| ID | Severity | Title | Owner | Target | Status | Post-audit note |
|---|---|---|---|---|---|---|
| FINAL-P0-001 | P0 | Production-readiness claim is unsupportable at this commit (release integrity) |  |  | partially-fixed | partially-fixed |
| HYG-P0-001 | P0 | Publication digest and closeout declare commits that do not match the audited tree |  |  | partially-fixed | partially-fixed |
| HYG-P0-002 | P0 | The mandated publication-chain verifier could not be reproduced and the chain is not bound to HEAD |  |  | partially-fixed | partially-fixed |
| OBS-P0-001 | P0 | Prometheus scrapes only 3 targets; nearly all `falcon_*` signals hinge on the node-exporter textfile collector |  |  | partially-fixed | partially-fixed |
| API-P1-001 | P1 | Cross-repo pairing contract cannot be verified in this environment |  |  | partially-fixed | remediation PS-U01 open c04c0068c182b7d61521978f154f5ac33ae42c2a https://github.com/MaineCyberTech/falcon/pull/21 |
| ARCH-P1-001 | P1 | Single-host concentration: host loss is total pipeline loss |  |  | partially-fixed | remediation PS-U02 open 41cd5a1e65e22f7ef1e957605bb0f0df2755328d https://github.com/MaineCyberTech/falcon/pull/22 |
| ARCH-P1-002 | P1 | Abort-marker contract is self-contradictory and normal failure exits leave no marker |  |  | partially-fixed | remediation PATCH-1 open 7a67d906de819e80a49f890dce693ecd595f8920 https://github.com/MaineCyberTech/falcon/pull/18 |
| CI-P1-001 | P1 | CI tool downloads did not fail fast |  |  | verified-fixed | verified-fixed at base; PS-U03 added an offline regression guard (375c4fb) |
| CI-P1-002 | P1 | Branch protection and required checks are not enforced server-side |  |  | owner-accepted | owner-accepted (plan-gated); PS-U03 records it as unchanged |
| DATA-P1-001 | P1 | Wazuh and IRIS data have no retention (unbounded index growth) |  |  | still-open | remediation PATCH-7 closed |
| EXEC-P1-001 | P1 | Lab "GO" can be misread as a production approval |  |  | partially-fixed | remediation PS-U05 open 4529dbdb966a639a79d46d85c3d32de9ae865925 https://github.com/MaineCyberTech/falcon/pull/24 |
| FINAL-P1-001 | P1 | Operational resilience remains incomplete across the backup lifecycle |  |  | partially-fixed | remediation PS-U07 open a981b7b449ba48bf755ce9e9c0b17f1a94178e28 https://github.com/MaineCyberTech/falcon/pull/25 |
| HYG-P1-001 | P1 | Committed `review-package/` is a stale snapshot duplicate of the source tree |  |  | partially-fixed | remediation PS-U08 open 3a200c9fe33c51c97a9e348fc5f32c846344a72b https://github.com/MaineCyberTech/falcon/pull/26 |
| HYG-P1-002 | P1 | Secret-scanner path allowlist was not separator-portable |  |  | verified-fixed | verified-fixed at base; PS-U08 confirmed at origin/main (unchanged) |
| OBS-P1-001 | P1 | Alert expressions mix `bool` and raw comparison forms with no linter |  |  | partially-fixed | remediation PS-U10 open aef63addacb79888c0d540257a8b0470115c3102 https://github.com/MaineCyberTech/falcon/pull/27 |
| OBS-P1-002 | P1 | Duplicate/overlapping rules and a self-contradictory firing-proof coverage total |  |  | partially-fixed | remediation PS-U10 open aef63addacb79888c0d540257a8b0470115c3102 https://github.com/MaineCyberTech/falcon/pull/27 |
| OBS-P1-003 | P1 | Relay failure counter is all-or-nothing; partial-path degradation is caught only by the weekly canary |  |  | partially-fixed | remediation PS-U10 open aef63addacb79888c0d540257a8b0470115c3102 https://github.com/MaineCyberTech/falcon/pull/27 |
| SEC-P1-001 | P1 | OpenCanary publishes six decoy services on all interfaces |  |  | partially-fixed | open |
| SEC-P1-002 | P1 | Blanket `iifname "wg0" accept` grants every WireGuard peer host-wide access |  |  | partially-fixed | open |
| SEC-P1-003 | P1 | Owner-directed open-inbound override state is contradictory across records |  |  | partially-fixed | partially-fixed |
| SUPPLY-P1-001 | P1 | Container digest gate scope hole: vendored `mct/compose` and `automation/wazuh` are ungated |  |  | partially-fixed | remediation PATCH-5 open 5c6c537857a6d0de7ec2b58a26356c72dad0d284 https://github.com/MaineCyberTech/falcon/pull/17 |
| SUPPLY-P1-002 | P1 | Vulnerability scanning is not gated and coverage is partial |  |  | partially-fixed | remediation PATCH-5 open 5c6c537857a6d0de7ec2b58a26356c72dad0d284 https://github.com/MaineCyberTech/falcon/pull/17 |
| TEST-P1-001 | P1 | Repo-local test ledger points at an out-of-repo, pre-rename lab tree |  |  | partially-fixed | remediation PS-U13 open ed2f739a05030a860b06f9f4e58b58d054fd28ca https://github.com/MaineCyberTech/falcon/pull/28 |
| TEST-P1-002 | P1 | The full gate does not complete within a short bounded run and shell suites are not executable off a bash host |  |  | partially-fixed | remediation PS-U13 open ed2f739a05030a860b06f9f4e58b58d054fd28ca https://github.com/MaineCyberTech/falcon/pull/28 |
| API-P2-001 | P2 | Enrollment API tokens have no expiry field |  |  | partially-fixed | remediation PS-U01 open c04c0068c182b7d61521978f154f5ac33ae42c2a https://github.com/MaineCyberTech/falcon/pull/21 |
| API-P2-002 | P2 | Ingest contract relies on a shared secret header, not request signing or idempotency keys |  |  | partially-fixed | remediation PS-U01 open c04c0068c182b7d61521978f154f5ac33ae42c2a https://github.com/MaineCyberTech/falcon/pull/21 |
| ARCH-P2-001 | P2 | Declared container hardening lags the running containers |  |  | partially-fixed | remediation PS-U02 open 41cd5a1e65e22f7ef1e957605bb0f0df2755328d https://github.com/MaineCyberTech/falcon/pull/22 |
| ARCH-P2-002 | P2 | Wazuh and vendored MCT stacks run tag-only images outside pin/SBOM scope |  |  | partially-fixed | remediation PS-U02 open 41cd5a1e65e22f7ef1e957605bb0f0df2755328d https://github.com/MaineCyberTech/falcon/pull/22 |
| ARCH-P2-003 | P2 | Live ingest authentication is a shared secret header, not mTLS |  |  | partially-fixed | remediation PS-U02 open 41cd5a1e65e22f7ef1e957605bb0f0df2755328d https://github.com/MaineCyberTech/falcon/pull/22 |
| ARCH-P2-005 | P2 | Only the backup job installs the abort trap; other long-running jobs lack it |  |  | partially-fixed | remediation PATCH-2 open 38c18ef75ab115a5e6bce550bec49f2bb11bfa47 https://github.com/MaineCyberTech/falcon/pull/19 |
| CI-P2-001 | P2 | `ci/validate.py` did not implement the evidence-index verification its docstring promises |  |  | verified-fixed | verified-fixed at base; PS-U03 added an offline regression guard (375c4fb) |
| CI-P2-002 | P2 | Auto-merge workflow holds `contents: write` with no environment protection |  |  | partially-fixed | remediation PS-U03 open 375c4fb13d5ff24b2fa1df2d48565e9ec11f2124 https://github.com/MaineCyberTech/falcon/pull/23 |
| DATA-P2-001 | P2 | Index template and `event_time` ownership are split with no consistency check |  |  | partially-fixed | remediation PS-U04 open eee84c8ec4a69f5614a7b0b267231a14a1ff65f5 https://github.com/MaineCyberTech/falcon/pull/31 |
| FEAT-P2-001 | P2 | Vendored MCT services are present in Compose while the subtree policy calls the tree archive-only |  |  | partially-fixed | remediation PS-U06 open f19acdbbb7670673446fa86df51f0e3374cd3057 https://github.com/MaineCyberTech/falcon/pull/33 |
| FEAT-P2-002 | P2 | Backup/offsite delivery is single-attempt with no retry, backoff, or dead-letter |  |  | partially-fixed | remediation PATCH-3 open 2e049a94d5af532c67f452176e88f0f4c90a34ff https://github.com/MaineCyberTech/falcon/pull/20 |
| HYG-P2-001 | P2 | Large generated SBOM/vulnerability JSON committed (39 files, up to ~122 KB each) |  |  | partially-fixed | remediation PS-U08 open 3a200c9fe33c51c97a9e348fc5f32c846344a72b https://github.com/MaineCyberTech/falcon/pull/26 |
| INV-P2-001 | P2 | Repository is majority generated/derived content with no in-repo regeneration or drift check |  |  | partially-fixed | remediation PS-U09 open e31523a59c945126e1b3e1e6ea9e630559292812 https://github.com/MaineCyberTech/falcon/pull/32 |
| SEC-P2-001 | P2 | Public-facing routers have no origin authentication; `ntfy-auth` is dead config |  |  | partially-fixed | remediation PS-U11 open 1127bf6015f6026c7f930032fe969dbebe320b52 https://github.com/MaineCyberTech/falcon/pull/29 |
| SEC-P2-002 | P2 | Cloudflare API token is passed on the `curl` command line |  |  | partially-fixed | remediation PS-U11 open 1127bf6015f6026c7f930032fe969dbebe320b52 https://github.com/MaineCyberTech/falcon/pull/29 |
| SUPPLY-P2-001 | P2 | `.gitleaks.toml` allowlists are broader than the documented classified set |  |  | partially-fixed | remediation PS-U12 open 5f9cf9a304fba3ecd82dfee951e8d299c9a93f15 https://github.com/MaineCyberTech/falcon/pull/30 |
| SUPPLY-P2-002 | P2 | Image lock freshness is not gated |  |  | partially-fixed | remediation PS-U12 open 5f9cf9a304fba3ecd82dfee951e8d299c9a93f15 https://github.com/MaineCyberTech/falcon/pull/30 |
| TEST-P2-001 | P2 | No backup/offsite/restore end-to-end test runs in the standard gate |  |  | partially-fixed | remediation PS-U13 open ed2f739a05030a860b06f9f4e58b58d054fd28ca https://github.com/MaineCyberTech/falcon/pull/28 |
| CI-P3-001 | P3 | Local and CI shellcheck semantics diverged |  |  | verified-fixed | verified-fixed at base; PS-U03 added an offline regression guard (375c4fb) |
| INV-P3-001 | P3 | Legacy host-absolute evidence paths require manual rewrite to resolve in a clone |  |  | partially-fixed | remediation PS-U09 open e31523a59c945126e1b3e1e6ea9e630559292812 https://github.com/MaineCyberTech/falcon/pull/32 |
| SEC-P3-001 | P3 | Default-deny `forward`/`output` policies are inert at the managed-table level |  |  | partially-fixed | remediation PS-U11 open 1127bf6015f6026c7f930032fe969dbebe320b52 https://github.com/MaineCyberTech/falcon/pull/29 |
| SUPPLY-P3-001 | P3 | `pins/verify-digests.sh` compares only the first RepoDigest entry |  |  | partially-fixed | remediation PS-U12 open 5f9cf9a304fba3ecd82dfee951e8d299c9a93f15 https://github.com/MaineCyberTech/falcon/pull/30 |
