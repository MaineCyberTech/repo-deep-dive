# Follow-up register

Owner/Target/Status columns drive tools/collect_findings.py enrichment.

| ID | Severity | Title | Owner | Target | Status | Post-audit note |
|---|---|---|---|---|---|---|
| FINAL-P0-001 | P0 | Production-readiness claim is unsupportable at this commit (release integrity) |  |  | immediate | partially-fixed |
| HYG-P0-001 | P0 | Publication digest and closeout declare commits that do not match the audited tree |  |  | immediate | partially-fixed |
| HYG-P0-002 | P0 | The mandated publication-chain verifier could not be reproduced and the chain is not bound to HEAD |  |  | immediate | partially-fixed |
| OBS-P0-001 | P0 | Prometheus scrapes only 3 targets; nearly all `falcon_*` signals hinge on the node-exporter textfile collector |  |  | immediate | partially-fixed |
| API-P1-001 | P1 | Cross-repo pairing contract cannot be verified in this environment |  |  | this week | open |
| ARCH-P1-001 | P1 | Single-host concentration: host loss is total pipeline loss |  |  | this week | open |
| ARCH-P1-002 | P1 | Abort-marker contract is self-contradictory and normal failure exits leave no marker |  |  | immediate | open |
| CI-P1-001 | P1 | CI tool downloads did not fail fast |  |  | this week | verified-fixed |
| CI-P1-002 | P1 | Branch protection and required checks are not enforced server-side |  |  | this week | owner-accepted |
| DATA-P1-001 | P1 | Wazuh and IRIS data have no retention (unbounded index growth) |  |  | this week | open |
| EXEC-P1-001 | P1 | Lab "GO" can be misread as a production approval |  |  | this week | open |
| FINAL-P1-001 | P1 | Operational resilience remains incomplete across the backup lifecycle |  |  | this week | open |
| HYG-P1-001 | P1 | Committed `review-package/` is a stale snapshot duplicate of the source tree |  |  | this week | open |
| HYG-P1-002 | P1 | Secret-scanner path allowlist was not separator-portable |  |  | this week | verified-fixed |
| OBS-P1-001 | P1 | Alert expressions mix `bool` and raw comparison forms with no linter |  |  | this week | partially-fixed |
| OBS-P1-002 | P1 | Duplicate/overlapping rules and a self-contradictory firing-proof coverage total |  |  | this week | partially-fixed |
| OBS-P1-003 | P1 | Relay failure counter is all-or-nothing; partial-path degradation is caught only by the weekly canary |  |  | this week | open |
| SEC-P1-001 | P1 | OpenCanary publishes six decoy services on all interfaces |  |  | this week | open |
| SEC-P1-002 | P1 | Blanket `iifname "wg0" accept` grants every WireGuard peer host-wide access |  |  | this week | open |
| SEC-P1-003 | P1 | Owner-directed open-inbound override state is contradictory across records |  |  | this week | partially-fixed |
| SUPPLY-P1-001 | P1 | Container digest gate scope hole: vendored `mct/compose` and `automation/wazuh` are ungated |  |  | this week | open |
| SUPPLY-P1-002 | P1 | Vulnerability scanning is not gated and coverage is partial |  |  | this week | open |
| TEST-P1-001 | P1 | Repo-local test ledger points at an out-of-repo, pre-rename lab tree |  |  | this week | open |
| TEST-P1-002 | P1 | The full gate does not complete within a short bounded run and shell suites are not executable off a bash host |  |  | this week | open |
| API-P2-001 | P2 | Enrollment API tokens have no expiry field |  |  | this month | open |
| API-P2-002 | P2 | Ingest contract relies on a shared secret header, not request signing or idempotency keys |  |  | this month | open |
| ARCH-P2-001 | P2 | Declared container hardening lags the running containers |  |  | this month | open |
| ARCH-P2-002 | P2 | Wazuh and vendored MCT stacks run tag-only images outside pin/SBOM scope |  |  | this month | open |
| ARCH-P2-003 | P2 | Live ingest authentication is a shared secret header, not mTLS |  |  | this month | open |
| ARCH-P2-005 | P2 | Only the backup job installs the abort trap; other long-running jobs lack it |  |  | this week | open |
| CI-P2-001 | P2 | `ci/validate.py` did not implement the evidence-index verification its docstring promises |  |  | this month | verified-fixed |
| CI-P2-002 | P2 | Auto-merge workflow holds `contents: write` with no environment protection |  |  | this month | open |
| DATA-P2-001 | P2 | Index template and `event_time` ownership are split with no consistency check |  |  | this month | open |
| FEAT-P2-001 | P2 | Vendored MCT services are present in Compose while the subtree policy calls the tree archive-only |  |  | this month | open |
| FEAT-P2-002 | P2 | Backup/offsite delivery is single-attempt with no retry, backoff, or dead-letter |  |  | this week | open |
| HYG-P2-001 | P2 | Large generated SBOM/vulnerability JSON committed (39 files, up to ~122 KB each) |  |  | this month | open |
| INV-P2-001 | P2 | Repository is majority generated/derived content with no in-repo regeneration or drift check |  |  | this month | open |
| SEC-P2-001 | P2 | Public-facing routers have no origin authentication; `ntfy-auth` is dead config |  |  | this month | open |
| SEC-P2-002 | P2 | Cloudflare API token is passed on the `curl` command line |  |  | this month | open |
| SUPPLY-P2-001 | P2 | `.gitleaks.toml` allowlists are broader than the documented classified set |  |  | this month | open |
| SUPPLY-P2-002 | P2 | Image lock freshness is not gated |  |  | this month | open |
| TEST-P2-001 | P2 | No backup/offsite/restore end-to-end test runs in the standard gate |  |  | this month | open |
| CI-P3-001 | P3 | Local and CI shellcheck semantics diverged |  |  | this quarter | verified-fixed |
| INV-P3-001 | P3 | Legacy host-absolute evidence paths require manual rewrite to resolve in a clone |  |  | this quarter | open |
| SEC-P3-001 | P3 | Default-deny `forward`/`output` policies are inert at the managed-table level |  |  | this quarter | open |
| SUPPLY-P3-001 | P3 | `pins/verify-digests.sh` compares only the first RepoDigest entry |  |  | this quarter | open |
