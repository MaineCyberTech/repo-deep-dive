# Follow-up register

| Finding | Severity | Title | Owner | Target | Status | Note |
|---|---|---|---|---|---|---|
| CI-P1-001 | P1 | P1 secret gate in the org scan is inert: it matches 'SEC-' IDs but deterministic findings are namespaced 'DET-' | @owner | CI | verified-fixed | merged repo-deep-dive#15 @ abdf75d |
| SEC-P2-001 | P2 | PAT embedded in git clone URL in three workflows (contradicts the hardened extraheader pattern) | @owner | SEC | verified-fixed | merged repo-deep-dive#17 @ 7a2aa6e |
| CI-P2-001 | P2 | verify-remediation executes arbitrary commands from a PR-controllable plan on the self-hosted lab runner | @owner | CI | verified-fixed | merged repo-deep-dive#18 @ ec3d0c2 |
| SUPPLY-P2-001 | P2 | 15 GitHub Action refs are tag-pinned (@v4/@v5), not commit-SHA pinned | @owner | SUPPLY | regressed | REGRESSED: #19 pin reverted by repo-deep-dive#33 @ 2626a84 and repo-deep-dive#35 @ 04aec9e; re-pinned in this PR #PRNUM. |
| SUPPLY-P2-002 | P2 | Two large third-party binaries are committed into an archived run with no checksum record | @owner | SUPPLY | verified-fixed | merged repo-deep-dive#20 @ b881482 |
| SEC-P2-002 | P2 | publish_audit.py publishes findings/reports to the pack and a target-repo PR without a secret scan | @owner | SEC | verified-fixed | merged repo-deep-dive#21 @ 870bd9c |
| CI-P3-001 | P3 | The changed-run gate enforces only P0 and only on pull_request; pushes to main skip it | @owner | CI | verified-fixed | merged repo-deep-dive#33 @ 2626a84 |
| PORT-P3-001 | P3 | 35 tracked shell scripts carry mode 100644 (no exec bit) | @owner | PORT | verified-fixed | merged repo-deep-dive#24 @ e4403c8 |
| CI-P3-002 | P3 | actionlint reports shellcheck SC2015/SC2018 notes in four workflows | @owner | CI | verified-fixed | merged repo-deep-dive#26 @ 508b580 |
| CONF-P3-001 | P3 | gitleaks generic-api-key hits in shipped runs/ artifacts are false positives; allowlist does not cover them | @owner | CONF | open | Confirm the remaining seven hits and allowlist the known-safe run paths in .gitleaks.toml (e.g. `runs/.*/(diff\.patch\|pr |
| CONF-P3-002 | P3 | secrets: inherit passes every repo/org secret into the reusable lab-preflight workflow | @owner | CONF | verified-fixed | merged repo-deep-dive#27 @ 161de65 |
| CI-P3-003 | P3 | lab-tests.yml interpolates a dispatch input directly into a shell command on the lab runner | @owner | CI | verified-fixed | merged repo-deep-dive#29 @ 877e248 |
