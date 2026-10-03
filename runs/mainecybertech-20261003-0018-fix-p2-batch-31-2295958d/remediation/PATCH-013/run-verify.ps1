$ErrorActionPreference = 'Continue'
$log = 'C:\temp\proxmox-vm\audits\runs\mainecybertech\20261003-0018-fix-p2-batch-31-2295958d\remediation\PATCH-013\verify.log'
$lab = 'C:\temp\proxmox-vm\scripts\lab-run.ps1'
Remove-Item $log -Force -ErrorAction SilentlyContinue

function Log($text) { Add-Content -Path $log -Value $text }

Log "PATCH-013 verification - mainecybertech - run 20261003-0018-fix-p2-batch-31-2295958d"
Log "Findings: HYG-P2-001/002, INV-P2-002, INV-P3-002, SUPPLY-P3-002, CI-P2-002, CI-P3-001,"
Log "          TEST-P2-002, TEST-P3-001, DATA-P2-001/002, ARCH-P2-001/003, OBS-P2-002/003,"
Log "          OBS-P3-001, SEC-P3-001/002"
Log "Repo: C:\temp\mainecybertech"
Log "Base: origin/fix/p2-batch-31 @ 11746adcbea50d313162cea6eb42a59358a17d29 (audit ran at stale 2295958d)"
Log "Lab: Proxmox ci-runner (172.23.128.51) via lab-sync.ps1 / lab-run.ps1"
Log ""

function Run-Lab($label, $cmd) {
  Log "=== $label ==="
  Log "COMMAND: $cmd"
  $out = & $lab -Repo mainecybertech -Command $cmd 2>&1 | Out-String
  $code = $LASTEXITCODE
  Log ($out.TrimEnd())
  Log "EXIT: $code"
  Log ""
}

Log "--- Reproduction at base (before fix) ---"
Log "Verified on the current base (11746adc) before editing:"
Log "  SEC-P3-001  X-XSS-Protection + style-src 'unsafe-inline' present in security-headers.ts"
Log "  SEC-P3-002  webhooks.ts compared clientState with !== (no constant-time compare)"
Log "  DATA-P2-002 orphan-cleanup.ts issued one .in(storage_path, paths) with up to 10k keys"
Log "  TEST-P2-002 no route-mount authorization guard test existed"
Log "  TEST-P3-001 api thresholds 30/50/55/58, web 38/38/45/46"
Log "  SUPPLY-P3-002 supabase/.temp/.../env/docker.env present on disk; no CI guard stopped tracked secrets"
Log "  CI-P2-002 terraform-do.yml manual-dispatch only (no scheduled drift plan)"
Log "  INV-P3-002 AGENTS.md/review.md hard-coded C:\\temp\\mainecybertech-portal"
Log "  INV-P2-002 docs bootstrap SQL had no historical/don't-edit header"
Log "  ARCH-P2-001/OBS-P3-001 no single-host recovery / failure-mode runbooks"
Log "  OBS-P2-002 no committed SLO/dashboard definitions"
Log "  DATA-P2-001 already fixed at base (encrypted_pii written by profiles.ts + backfill; generate-db-types --check in CI)"
Log "  ARCH-P2-003 already fixed at base (prometheus alerting block + alertmanager service + tmpl)"
Log ""

Run-Lab "install dependencies" 'corepack pnpm install --frozen-lockfile'
Run-Lab "api typecheck" 'corepack pnpm --filter api typecheck'
Run-Lab "worker typecheck" 'corepack pnpm --filter worker typecheck'
Run-Lab "api test + coverage thresholds (TEST-P3-001)" 'corepack pnpm --filter api test:coverage'
Run-Lab "web test + coverage thresholds (TEST-P3-001)" 'corepack pnpm --filter web test:coverage'
Run-Lab "worker test (DATA-P2-002)" 'corepack pnpm --filter worker test'
Run-Lab "docs links" 'node scripts/check-docs-links.mjs'
Run-Lab "docs counts" 'node scripts/check-docs-counts.mjs'
Run-Lab "generated DB types current (DATA-P2-001)" 'node scripts/generate-db-types.js --check'
Run-Lab "review.md mirror in sync (INV-P3-002)" 'node scripts/sync-review-md.mjs --check'
Run-Lab "actionlint test.yml (SUPPLY-P3-002 guard)" 'actionlint .github/workflows/test.yml'
Run-Lab "actionlint terraform-do.yml syntax/expressions (CI-P2-002)" 'actionlint -shellcheck= .github/workflows/terraform-do.yml && actionlint -shellcheck= .github/workflows/test.yml && echo ACTIONLINT_SYNTAX_OK'
Log "NOTE: bare 'actionlint .github/workflows/terraform-do.yml' exits 1 on four PRE-EXISTING"
Log "      SC2086 shellcheck info findings (lines 57/232/272; base 11746adc also fails identically)."
Log "      No workflow actionlint runs in CI; this change adds no new findings. Proof below."
Log ""
Run-Lab "actionlint terraform-do.yml at base (pre-existing findings, expected exit 1)" 'git show 11746adc:.github/workflows/terraform-do.yml > /tmp/base-terraform-do.yml && actionlint /tmp/base-terraform-do.yml; echo base_actionlint_exit:$?'
Run-Lab "yq parse SLO dashboard JSON (OBS-P2-002)" 'yq -e . /srv/work/mainecybertech/infra/digitalocean/dashboards/mct-overview.json > /dev/null && echo dashboard_json_ok'
Run-Lab "secret-files guard (SUPPLY-P3-002, pass + fail-closed proof)" 'bash /tmp/patch013-guard.sh'
Run-Lab "gitleaks on changed files (secret gate)" 'bash /tmp/patch013-gitleaks.sh'
