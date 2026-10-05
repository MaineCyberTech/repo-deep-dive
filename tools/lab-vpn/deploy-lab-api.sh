#!/usr/bin/env bash
# Deploy/refresh the lab job API into a Proxmox guest. Run on the Proxmox host as root.
#
#   deploy-lab-api.sh <vmid> [path-to-lab_api_server.py]
#
# Copies tools/lab_api_server.py + lab-api-install.sh into the guest and runs the
# installer. Idempotent: re-running refreshes the server and unit but keeps the token.
#
# After deploying, set the GitHub variable/secret on the consuming repo:
#   gh variable set LAB_API_URL  -R <org>/<repo> -b "http://<guest-ip>:8722"
#   gh secret   set LAB_API_TOKEN -R <org>/<repo> -b "<TOKEN printed above>"
set -euo pipefail

VMID="${1:?usage: deploy-lab-api.sh <vmid> [server.py]}"
HERE="$(cd "$(dirname "$0")" && pwd)"
SRV="${2:-$HERE/../lab_api_server.py}"

[ -f "$SRV" ] || { echo "server not found: $SRV" >&2; exit 1; }
[ -f "$HERE/lab-api-install.sh" ] || { echo "installer not found: $HERE/lab-api-install.sh" >&2; exit 1; }
command -v pct >/dev/null || { echo "run this on a Proxmox host (pct not found)" >&2; exit 1; }

pct push "$VMID" "$SRV" /root/lab_api_server.py
pct push "$VMID" "$HERE/lab-api-install.sh" /root/lab-api-install.sh
pct exec "$VMID" -- bash /root/lab-api-install.sh
