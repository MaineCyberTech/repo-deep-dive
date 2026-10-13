# Deterministic checks — deterministic

Machine checks (no LLM). Findings use the `DET` area.

## Findings

| ID | Title | Severity |
|---|---|---|
| DET-P3-001 | [DEP] No Dependabot configuration | P3 |
| DET-P3-002 | [DEP] trivy not installed (dependency vuln scan skipped) | P3 |
| DET-P2-003 | [PORT] CRLF committed for 11 file(s) (index has CRLF) | P2 |
| DET-P3-004 | [SEC] gitleaks not installed (secret scan skipped) | P3 |
| DET-P2-005 | [SUPPLY] 9 GitHub Action ref(s) not pinned to a commit SHA | P2 |

## Detail

### Finding ID: DET-P3-001 - [DEP] No Dependabot configuration

Add `.github/dependabot.yml` for dependency updates.


### Finding ID: DET-P3-002 - [DEP] trivy not installed (dependency vuln scan skipped)

Install trivy to enable the --deep dependency vulnerability scan.


### Finding ID: DET-P2-003 - [PORT] CRLF committed for 11 file(s) (index has CRLF)

Committed line endings are CRLF, which breaks Linux CI (shell scripts, hash checks). Add `.gitattributes` with `* text=auto eol=lf`, then renormalize (`git add --renormalize .`).

- `results/bench-live-linux-20261013-012449/bench-live-linux-20261013-013426-logs/gfx-glmark2.log`
- `results/bench-live-linux-20261013-023910/bench-live-linux-20261013-013426-logs/gfx-glmark2.log`
- `results/bench-live-linux-20261013-035221/bench-live-linux-20261013-013426-logs/gfx-glmark2.log`
- `results/bench-live-linux-20261013-041741/bench-live-linux-20261013-013426-logs/gfx-glmark2.log`
- `results/bench-live-linux-20261013-041959/bench-live-linux-20261013-013426-logs/gfx-glmark2.log`
- `results/bench-live-linux-20261013-044325/bench-live-linux-20261013-013426-logs/gfx-glmark2.log`
- `results/bench-live-linux-20261013-044800/bench-live-linux-20261013-013426-logs/gfx-glmark2.log`
- `results/bench-live-linux-20261013-044901/bench-live-linux-20261013-013426-logs/gfx-glmark2.log`
- `results/bench-live-linux-20261013-054216/bench-live-linux-20261013-013426-logs/gfx-glmark2.log`
- `results/bench-live-linux-20261013-055818/bench-live-linux-20261013-013426-logs/gfx-glmark2.log`
- `results/bench-live-linux-20261013-073159/bench-live-linux-20261013-013426-logs/gfx-glmark2.log`

### Finding ID: DET-P3-004 - [SEC] gitleaks not installed (secret scan skipped)

Install gitleaks in CI to enable the secret scan.


### Finding ID: DET-P2-005 - [SUPPLY] 9 GitHub Action ref(s) not pinned to a commit SHA

Pin `uses:` to a full 40-hex commit SHA (supply-chain hardening).

- `build-app.yml:39 actions/checkout@v4`
- `build-app.yml:41 actions/setup-python@v5`
- `build-app.yml:87 actions/upload-artifact@v4`
- `build-app.yml:96 actions/checkout@v4`
- `build-app.yml:100 actions/download-artifact@v4`
- `build-app.yml:104 softprops/action-gh-release@v2`
- `build-iso.yml:56 actions/checkout@v4`
- `build-iso.yml:116 softprops/action-gh-release@v2`
- `release.yml:36 actions/checkout@v4`
