#!/usr/bin/env bash
# live_snapshot.sh — read-only live-state snapshot for falcon-lab audit run manifests.
#
# READ-ONLY GUARANTEE: this script only queries state (systemd, ss, df, free, uptime,
# unauthenticated local HTTP probes, journal tail). It does not restart, reconfigure,
# deploy, or write anywhere except the optional output file. It never prints credentials.
#
# Usage: tools/live_snapshot.sh [output-file]
set -euo pipefail

OUT="${1:-}"
if [[ -n "$OUT" ]]; then
  mkdir -p "$(dirname "$OUT")"
  exec > >(tee "$OUT") 2>&1
fi

echo "# Live snapshot — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "# host: $(hostname) · user: $(id -un) · mode: read-only capture"
echo

echo "## Uptime / load"
uptime || true
echo

echo "## Memory"
free -h || true
echo

echo "## Disk"
df -h / /srv/falcon 2>/dev/null || df -h / || true
echo

echo "## Failed systemd units"
systemctl --failed --no-pager 2>/dev/null || echo "(unavailable)"
echo

echo "## Falcon-related units"
systemctl list-units --all --no-pager 2>/dev/null | grep -i falcon || echo "(none visible to this account)"
echo

echo "## Falcon-related timers"
systemctl list-timers --all --no-pager 2>/dev/null | grep -i falcon || echo "(none visible to this account)"
echo

echo "## Listening sockets (first 60)"
ss -lntu 2>/dev/null | head -60 || echo "(unavailable)"
echo

echo "## WireGuard"
wg show 2>/dev/null || echo "(unavailable: permission or not installed)"
echo

echo "## Docker (expected unavailable for the audit account)"
docker ps --format '{{.Names}}\t{{.Status}}' 2>/dev/null | head -40 || echo "(unavailable)"
echo

echo "## Local HTTP probes (unauthenticated)"
for url in "http://127.0.0.1:2586/v1/health" "http://127.0.0.1:9200" "https://127.0.0.1/"; do
  code="$(curl -sk -o /dev/null -m 3 -w '%{http_code}' "$url" 2>/dev/null || echo ERR)"
  echo "  $url -> $code"
done
echo

echo "## Journal errors (last 20, if readable)"
journalctl -p err -n 20 --no-pager 2>/dev/null || echo "(unavailable)"
echo
echo "# end of snapshot"
