$ErrorActionPreference = 'Continue'
$log = 'C:\temp\proxmox-vm\audits\runs\mainecybertech\20261003-0018-fix-p2-batch-31-2295958d\remediation\PATCH-012\verify.log'
$lab = 'C:\temp\proxmox-vm\scripts\lab-run.ps1'
Remove-Item $log -Force -ErrorAction SilentlyContinue

function Log($text) { Add-Content -Path $log -Value $text }

Log "PATCH-012 verification - mainecybertech - run 20261003-0018-fix-p2-batch-31-2295958d"
Log "Findings: SUPPLY-P2-001 (P2), INV-P2-001 (P2), HYG-P3-002 (P3) - license policy + generated-artifact freshness/tracking"
Log "Repo: C:\temp\mainecybertech"
Log "Base: origin/fix/p2-batch-31 @ 11746adcbea50d313162cea6eb42a59358a17d29"
Log "Lab: Proxmox ci-runner (172.23.128.51) via C:\temp\proxmox-vm\scripts\lab-sync.ps1 / lab-run.ps1"
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
Log "At base 11746adc: docs/LICENSE_POLICY.md and security/license-policy.json exist, and test.yml runs scripts/license-gate.mjs (SUPPLY-P2-001 enforcement landed previously)."
Log "Still open: licenses.json was tracked (b81d53f7) while .gitignore:63 lists it as a generated aggregate (added in bd086426 without 'git rm --cached'), and no CI freshness/untracked gate existed."
Log "Reproduction commands (on base):"
Log "  git ls-files licenses.json            -> licenses.json   (tracked)"
Log "  git check-ignore --no-index licenses.json -> .gitignore:63:licenses.json (ignored but tracked)"
Log "  git grep --check (freshness)          -> only generate-db-types.js --check / sync-review-md.mjs --check; no licenses.json check"
Log ""

Run-Lab "install dependencies" 'corepack pnpm install --frozen-lockfile'
Run-Lab "docs counts" 'node scripts/check-docs-counts.mjs'
Run-Lab "docs links" 'node scripts/check-docs-links.mjs'
Run-Lab "actionlint changed workflow" 'actionlint .github/workflows/test.yml'
Run-Lab "license collect + gate (test.yml steps)" 'node scripts/collect-licenses.mjs --out licenses.json && node scripts/license-gate.mjs licenses.json'
Run-Lab "new guard - artifacts untracked (expected pass)" 'bash /tmp/guard-check.sh'
Run-Lab "new guard - artifact re-introduced (expected fail/exit 1)" 'git add -f licenses.json; bash /tmp/guard-check.sh; echo guard_exit:$?; git rm --cached licenses.json >/dev/null; echo cleaned_index'

Log "=== gitleaks (changed files: .github/workflows/test.yml, docs/LICENSE_POLICY.md) ==="
Log "COMMAND: gitleaks detect --source=/tmp/scan012 --no-git --redact -v"
$gl = & $lab -Repo mainecybertech -Command 'mkdir -p /tmp/scan012; cp .github/workflows/test.yml docs/LICENSE_POLICY.md /tmp/scan012/; gitleaks detect --source=/tmp/scan012 --no-git --redact -v' 2>&1 | Out-String
$glcode = $LASTEXITCODE
Log ($gl.TrimEnd())
Log "EXIT: $glcode"
Log ""
Log "NOTE: corepack pnpm --filter api test not run - no application code changed (workflow + docs + untracking a generated aggregate only)."

Write-Host "verify.log written"
