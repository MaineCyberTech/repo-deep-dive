# Follow-up register

| Finding | Severity | Title | Owner | Target | Status | Note |
|---|---|---|---|---|---|---|
| GIT-P3-001 | P3 | No repository LICENSE file (deterministic real) | @owner | GIT | open | Add an explicit LICENSE (and optional NOTICE) matching the intended distribution terms and reference it from README.md. |
| PORT-P3-001 | P3 | Four tracked shell scripts lack the executable bit (deterministic real, impact limited) | @owner | PORT | verified-fixed | merged falcon-edge#34 @ 73028d0 |
| PORT-P3-002 | P3 | False positive: '14 CRLF files' are intentional byte-exact evidence (*.out -text) | @owner | PORT | open | None for these files; keep the -text policy. Scope any future renormalization to text config/scripts only. |
| SEC-P3-001 | P3 | False positive: gitleaks generic-api-key hits are allowlisted public/identifier values | @owner | SEC | open | No change; keep the allowlist line-scoped so a real secret on another line still alerts. |
| AUTH-P2-001 | P2 | Device mTLS private key is group-readable (0640), contradicting its documented 0600 | @owner | AUTH | open | Keep the sensor identity key at 0600 and give Vector its own client certificate/identity; only widen the certificate (no |
| SEC-P2-001 | P2 | mTLS clients never verify the control-plane hostname | @owner | SEC | verified-fixed | merged falcon-edge#39 @ 5cd08c9 |
| CI-P2-001 | P2 | bake-image interpolates secrets directly into shell script text | @owner | CI | verified-fixed | merged falcon-edge#33 @ 0ee35df |
| CI-P2-002 | P2 | Branch protection / required checks cannot be enforced; main is only advisory-gated | @owner | CI | open | Upgrade to GitHub Pro/Team and apply the ready payload (BRANCH_PROTECTION.md:53-64); until then keep compensating contro |
| SUPPLY-P2-001 | P2 | Shipped sensor image auto-applies signed updates without a per-update human gate | @owner | SUPPLY | verified-fixed | merged falcon-edge#41 @ 3ae7e75 |
| SUPPLY-P3-001 | P3 | Dependabot watches only GitHub Actions, not hash-pinned dev dependencies | @owner | SUPPLY | verified-fixed | merged falcon-edge#35 @ 9dce2a5 |
| SEC-P3-002 | P3 | Lab tooling disables SSH host-key and TLS verification | @owner | SEC | open | Pin lab host keys via managed known_hosts and verify TLS with the lab CA, mirroring inventory_metrics.py. |
| CI-P3-001 | P3 | Documentation overstates the dependabot-merge gate specificity | @owner | CI | verified-fixed | merged falcon-edge#36 @ a169b7d |
| SEC-P3-003 | P3 | No step-by-step emergency rotation procedure for the CA key / signing seed | @owner | SEC | verified-fixed | merged falcon-edge#37 @ 5549903 |
| CONF-P3-001 | P3 | Lab configs ship permissive defaults (TOFU enrollment; control plane binds all interfaces) | @owner | CONF | verified-fixed | merged falcon-edge#38 @ f267647 |
