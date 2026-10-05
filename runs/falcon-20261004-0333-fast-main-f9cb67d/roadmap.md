# Roadmap

- CI-P2-001 (P2) — Branch protection and required checks are plan-gated, so `validate` is advisory
- CI-P2-002 (P2) — Auto-merge workflow holds broad write scope and merges without pinning the checked commit
- SC-P2-001 (P2) — Dependabot covers only GitHub Actions; Python CI deps and container images are unmanaged
- SC-P2-002 (P2) — Release and SBOM artifacts are integrity-checked but unsigned (SLSA ~0-1)
- SEC-P2-001 (P2) — Public-facing routers rely only on Cloudflare Access; `ntfy-auth` is dead config
- SEC-P2-002 (P2) — All 20 inherited credentials remain PENDING rotation; 28 vendored scripts source credential files wholesale
- DET-P3-001 (P3) — [DEP] trivy not installed (dependency vuln scan skipped)
- DET-P3-002 (P3) — [GIT] No LICENSE file
- DET-P3-003 (P3) — [SUPPLY] 58 container image(s) without a digest pin
- DET-P3-004 (P3) — [SUPPLY] hadolint not installed (Dockerfile lint skipped)
- SC-P3-001 (P3) — Vendored mct/compose images are unpinned under a blanket waiver
- SC-P3-002 (P3) — Vulnerability scan coverage for 12 images is stale/pending, gated only by expiring waivers
- SC-P3-003 (P3) — Image/SBOM-component license allow/deny gate is not enforced
