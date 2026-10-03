# Suggested Tooling

Read-only, self-hosted, or free tools that pair with the pack's prompts. Nothing here is required, installed, or run automatically — pick what fits the environment's license policy (the falcon lab prefers license-free).

## Pack-internal toolchain (runs anywhere, stdlib-only)

| Tool | Wave | Purpose |
|---|---|---|
| `tools/repo_inventory.py <repo>` | 0 | Repo-agnostic inventory (stacks, routes, migrations, workflows, containers) for prompt `01` on new repos |
| `tools/new_run.py --run {run}` | 0 | Scaffold a valid run folder (INDEX skeleton + seed manifest); refuses non-empty dirs |
| `tools/run_toolchain.py <run> [--write]` | 4 | One-command chain: check → collect → score → dashboard → diff → CSV (read-only by default) |
| `tools/check_run.sh <run>` | 3–4 | Run validation; must print `PASS` (includes duplicate-ID gate) |
| `tools/collect_findings.py <run> --write` | 4 | Normalize findings to `findings.json` (validates against `schemas/findings.schema.json`) |
| `tools/risk_score.py <run> [--write]` | 4 | Advisory 0–100 score + `GO / GO WITH CONDITIONS / NO-GO` suggestion; never overrides the gate |
| `tools/render_dashboard.py <run> [--write]` | 4 | `dashboard.md` + `dashboard.html` + `pr_comment.md` from findings |
| `tools/diff_runs.py <old> <new>` | verify | Run-to-run delta |
| `tools/findings_to_csv.py <run>` | 4 | Tracker export |
| `ci/audit.yml` | CI | GitHub example: lint → validate → score → P0 gate → artifacts |
| `docs/AUTOMATION_GUIDE.md` | all | Portable grep/glob/read check recipes for any repo layout |

## External tools

| Area | Prompt(s) | Tools | Notes |
|---|---|---|---|
| Secret scanning | 11, 38 | gitleaks, trufflehog (OSS) | Tree + history scans; record exits and dispositions |
| Dependency risk | 11, 35 | osv-scanner, pip-audit, npm audit | Map to lockfiles; record versions |
| SBOM | 35 | syft, cdxgen | CycloneDX output; attach to releases |
| License policy | 35 | licensee, scancode-toolkit | Enforce in CI, not just docs |
| Container security | 36 | trivy, grype, docker-bench-security | Image and runtime checks |
| IaC / config | 12, 36 | checkov, kube-bench | Drift and misconfiguration checks |
| CI hygiene | 10, 34 | actionlint, zizmor | Workflow linting |
| Test coverage | 09 | coverage.py, c8 | Tie quality claims to numbers |
| Dead-man / uptime | 13, 14 | Uptime Kuma, healthchecks (self-hosted) | Must live outside the monitored stack |
| Backup verification | 32 | restic check, rclone check, borg check | Prove restores, not just runs |
| Evidence hashing | 00, 41 | sha256sum, b3sum | Capture manifests |
| Live snapshot | run manifest | `tools/live_snapshot.sh` | Read-only host-state capture |

## Ground rules

- Tools are **suggested**; the pack never installs or runs tooling automatically.
- Prefer tools that can run read-only and produce artifacts that can be hashed.
- A tool result is evidence only when it is captured with its command, version, and output.
