#!/usr/bin/env bash
# Connect a developer/agent workstation to the lab audit overlay and verify the lab.
#   lab-audit-connect.sh <client.conf> [iface-name]
# Works on Linux/macOS/WSL. (Windows: import the .conf in the WireGuard app.)
set -euo pipefail
CONF_IN="${1:?usage: lab-audit-connect.sh <client.conf> [iface]}"
IFACE="${2:-lab-audit}"
DEST="/etc/wireguard/${IFACE}.conf"

say() { echo "[lab-audit] $*"; }
SUDO=""; [ "$(id -u)" -ne 0 ] && SUDO="sudo"

say "installing wireguard-tools (if missing)"
if ! command -v wg-quick >/dev/null; then
  if command -v apt-get >/dev/null; then $SUDO apt-get install -y -qq wireguard-tools
  elif command -v dnf >/dev/null; then $SUDO dnf install -y -q wireguard-tools
  elif command -v brew >/dev/null; then brew install wireguard-tools
  else echo "install wireguard-tools manually" >&2; fi
fi

say "installing config $DEST"
$SUDO mkdir -p /etc/wireguard
$SUDO cp "$CONF_IN" "$DEST"; $SUDO chmod 600 "$DEST"
$SUDO wg-quick down "$IFACE" >/dev/null 2>&1 || true
$SUDO wg-quick up "$IFACE"
sleep 2

echo "== wg show =="; $SUDO wg show "$IFACE"
echo "== checks =="
for ip in 10.250.0.1 172.23.128.50 172.23.128.51 172.23.128.52; do
  if ping -c2 -W2 "$ip" >/dev/null 2>&1; then echo "PASS ping $ip"; else echo "FAIL ping $ip"; fi
done
if curl -s -m6 http://172.23.128.51:8722/health >/dev/null 2>&1; then echo "PASS lab API (ci-runner:8722)"; else echo "WARN lab API not reachable (may need the lab up)"; fi
echo "[lab-audit] connected. Tear down with: $SUDO wg-quick down $IFACE"
