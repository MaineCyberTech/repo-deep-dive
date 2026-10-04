# Roadmap

- SUPPLY-P1-001 (P1) - Vulnerable runtime transitive dependency @grpc/grpc-js 1.14.4 with a non-blocking audit gate
- SUPPLY-P2-001 (P2) - GitHub Action upload-artifact@v4 not pinned to a commit SHA
- SUPPLY-P2-002 (P2) - Container base and CI service images not pinned by digest
- CI-P2-001 (P2) - Supply-chain license/vulnerability workflow is not a required branch-protection check
- PORT-P3-001 (P3) - Six tracked shell scripts lack the executable bit
- SEC-P3-001 (P3) - Secret scan allowlists whole files, masking future real secrets
- SEC-P3-002 (P3) - Metrics token compared non-constant-time and has no rotation path
- SECRET-P3-001 (P3) - Empty service-role key silently disables persistence; no committed rotation evidence
- CI-P3-001 (P3) - CODEOWNERS is a personal account; release/hotfix branch rules absent
- CONF-P3-001 (P3) - Residual CRLF files and hadolint DL3025 HEALTHCHECK warnings
