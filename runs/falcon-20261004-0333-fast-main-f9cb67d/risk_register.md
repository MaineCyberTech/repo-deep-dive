# Follow-up register

Run: `falcon-20261004-0333-fast-main-f9cb67d` · Target: `falcon` @ `f9cb67d` · Profile: base

Register mirrored 1:1 with `risk_register.md` so `tools/check_run.sh` passes.

| Finding | Severity | Title | Owner | Target | Status | Note |
|---|---|---|---|---|---|---|
| CI-P2-001 | P2 | Branch protection and required checks are plan-gated, so `validate` is advisory | @owner | CI | owner-accepted | Owner-accepted with compensating controls (CODEOWNERS, PR template, doctrine). Carried from focused run CI-P2-001 / 20261003 CI-P1-002. |
| CI-P2-002 | P2 | Auto-merge workflow holds broad write scope and merges without pinning the checked commit | @ci | CI | open | Carried from focused run CI-P3-001 / 20261003 CI-P2-002; still present at f9cb67d. |
| SC-P2-001 | P2 | Dependabot covers only GitHub Actions; Python CI deps and container images are unmanaged | @supply | SC | open | Carried from focused run DEP-P2-001; still present at f9cb67d. |
| SC-P2-002 | P2 | Release and SBOM artifacts are integrity-checked but unsigned (SLSA ~0-1) | @supply | SC | open | Carried from focused run SUPPLY-P2-001; still present at f9cb67d. |
| SEC-P2-001 | P2 | Public-facing routers rely only on Cloudflare Access; `ntfy-auth` is dead config | @security | SEC | open | Carried from focused run SEC-P2-001; not yet fixed at f9cb67d. |
| SEC-P2-002 | P2 | All 20 inherited credentials remain PENDING rotation; 28 vendored scripts source credential files wholesale | @security | SEC | open | Tooling (rotation_status.py) added earlier; rotation execution itself remains outstanding. |
| DET-P3-001 | P3 | [DEP] trivy not installed (dependency vuln scan skipped) | @owner | DET | open |  |
| DET-P3-002 | P3 | [GIT] No LICENSE file | @owner | DET | open |  |
| DET-P3-003 | P3 | [SUPPLY] 58 container image(s) without a digest pin | @owner | DET | open |  |
| DET-P3-004 | P3 | [SUPPLY] hadolint not installed (Dockerfile lint skipped) | @owner | DET | open |  |
| SC-P3-001 | P3 | Vendored mct/compose images are unpinned under a blanket waiver | @supply | SC | open | Carried from focused run SUPPLY-P3-001 / DET-P3-007; still present at f9cb67d. |
| SC-P3-002 | P3 | Vulnerability scan coverage for 12 images is stale/pending, gated only by expiring waivers | @supply | SC | open | Carried from focused run SUPPLY-P3-002; still present at f9cb67d. |
| SC-P3-003 | P3 | Image/SBOM-component license allow/deny gate is not enforced | @supply | SC | open | Carried from focused run SUPPLY-P3-003; still present at f9cb67d. |
