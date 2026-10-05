# Deterministic checks — deterministic

Machine checks (no LLM). Findings use the `DET` area.

## Findings

| ID | Title | Severity |
|---|---|---|
| DET-P3-001 | [DEP] trivy not installed (dependency vuln scan skipped) | P3 |
| DET-P2-002 | [PORT] 2 tracked shell script(s) without the exec bit | P2 |

## Detail

### Finding ID: DET-P3-001 - [DEP] trivy not installed (dependency vuln scan skipped)

Install trivy to enable the --deep dependency vulnerability scan.


### Finding ID: DET-P2-002 - [PORT] 2 tracked shell script(s) without the exec bit

`./script.sh` fails on Linux; set `git update-index --chmod=+x`. Transfers from Windows drop the bit.

- `tools/lab-vpn/deploy-lab-api.sh`
- `tools/lab-vpn/lab-api-install.sh`
