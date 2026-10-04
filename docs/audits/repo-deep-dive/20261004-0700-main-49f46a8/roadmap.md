# Roadmap

- CI-P1-001 (P1) - P1 secret gate in the org scan is inert: it matches 'SEC-' IDs but deterministic findings are namespaced 'DET-'
- SEC-P2-001 (P2) - PAT embedded in git clone URL in three workflows (contradicts the hardened extraheader pattern)
- CI-P2-001 (P2) - verify-remediation executes arbitrary commands from a PR-controllable plan on the self-hosted lab runner
- SUPPLY-P2-001 (P2) - 15 GitHub Action refs are tag-pinned (@v4/@v5), not commit-SHA pinned
- SUPPLY-P2-002 (P2) - Two large third-party binaries are committed into an archived run with no checksum record
- SEC-P2-002 (P2) - publish_audit.py publishes findings/reports to the pack and a target-repo PR without a secret scan
- CI-P3-001 (P3) - The changed-run gate enforces only P0 and only on pull_request; pushes to main skip it
- PORT-P3-001 (P3) - 35 tracked shell scripts carry mode 100644 (no exec bit)
- CI-P3-002 (P3) - actionlint reports shellcheck SC2015/SC2018 notes in four workflows
- CONF-P3-001 (P3) - gitleaks generic-api-key hits in shipped runs/ artifacts are false positives; allowlist does not cover them
- CONF-P3-002 (P3) - secrets: inherit passes every repo/org secret into the reusable lab-preflight workflow
- CI-P3-003 (P3) - lab-tests.yml interpolates a dispatch input directly into a shell command on the lab runner
