# Roadmap

- GIT-P3-001 (P3) - No repository LICENSE file (deterministic real)
- PORT-P3-001 (P3) - Four tracked shell scripts lack the executable bit (deterministic real, impact limited)
- PORT-P3-002 (P3) - False positive: '14 CRLF files' are intentional byte-exact evidence (*.out -text)
- SEC-P3-001 (P3) - False positive: gitleaks generic-api-key hits are allowlisted public/identifier values
- AUTH-P2-001 (P2) - Device mTLS private key is group-readable (0640), contradicting its documented 0600
- SEC-P2-001 (P2) - mTLS clients never verify the control-plane hostname
- CI-P2-001 (P2) - bake-image interpolates secrets directly into shell script text
- CI-P2-002 (P2) - Branch protection / required checks cannot be enforced; main is only advisory-gated
- SUPPLY-P2-001 (P2) - Shipped sensor image auto-applies signed updates without a per-update human gate
- SUPPLY-P3-001 (P3) - Dependabot watches only GitHub Actions, not hash-pinned dev dependencies
- SEC-P3-002 (P3) - Lab tooling disables SSH host-key and TLS verification
- CI-P3-001 (P3) - Documentation overstates the dependabot-merge gate specificity
- SEC-P3-003 (P3) - No step-by-step emergency rotation procedure for the CA key / signing seed
- CONF-P3-001 (P3) - Lab configs ship permissive defaults (TOFU enrollment; control plane binds all interfaces)
