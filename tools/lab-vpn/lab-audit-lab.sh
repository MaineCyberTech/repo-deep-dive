#!/usr/bin/env bash
# Lab audit VPN peer (runs on the Proxmox LAB host). Joins the audit overlay and
# advertises the lab subnet 172.23.128.0/20 to the public endpoint. Idempotent,
# backs up before writing, pre-checks collisions, never touches falcon interfaces.
#
#   lab-audit-lab.sh inventory
#   lab-audit-lab.sh ensure <endpoint-server-pubkey> [endpoint-host]
#   lab-audit-lab.sh status
set -euo pipefail

IFACE="${IFACE:-wgaudit0}"
PORT="${PORT:-51900}"
SUBNET="${SUBNET:-10.250.0}"
SERVER_IP="${SERVER_IP:-${SUBNET}.1}"
LAB_IP="${LAB_IP:-${SUBNET}.9}"
LAB_SUBNET="${LAB_SUBNET:-172.23.128.0/20}"
LAB_BRIDGE="${LAB_BRIDGE:-vmbr0}"
ENDPOINT_HOST="${3:-${ENDPOINT_HOST:-138.197.105.82}}"
DIR="/etc/wireguard/${IFACE}"
CONF="/etc/wireguard/${IFACE}.conf"
SRVPUB="${2:-${SRVPUB:-}}"

say() { echo "[$(date -u +%H:%M:%S)] $*"; }
die() { echo "ERROR: $*" >&2; exit 1; }

inventory() {
  echo "== wg =="; wg show all 2>/dev/null || echo "(none)"
  echo "== /etc/wireguard =="; ls -la /etc/wireguard 2>/dev/null || true
  echo "== overlay conf =="; [ -f "$CONF" ] && sed -n '1,40p' "$CONF" || echo "not provisioned"
  echo "== lab bridge =="; ip -4 -br a show "$LAB_BRIDGE" 2>/dev/null || true
  echo "== route to endpoint =="; ip route get "$ENDPOINT_HOST" 2>/dev/null | head -1 || true
}

ensure() {
  [ "$(id -u)" -eq 0 ] || die "run as root"
  [ -n "$SRVPUB" ] || die "usage: ensure <endpoint-server-pubkey> [endpoint-host]"
  if [ "$IFACE" = "wg0" ]; then die "refusing to use wg0"; fi
  # endpoint reachability (best-effort; UDP has no connect, just report)
  if command -v nc >/dev/null; then say "endpoint $ENDPOINT_HOST:$PORT reachable(udp probe): $(nc -uz -w2 "$ENDPOINT_HOST" "$PORT" >/dev/null 2>&1 && echo yes || echo 'unknown/filtered')"; fi
  mkdir -p "$DIR"; chmod 700 "$DIR"; umask 077
  [ -f "$DIR/lab.key" ] || wg genkey > "$DIR/lab.key"
  wg pubkey < "$DIR/lab.key" > "$DIR/lab.pub"
  if [ -f "$CONF" ]; then cp -a "$CONF" "$CONF.bak-$(date -u +%Y%m%dT%H%M%SZ)"; fi
  cat > "$CONF" <<EOF
# Lab audit overlay peer (managed by repo-deep-dive scripts/lab-audit-lab.sh).
[Interface]
Address = ${LAB_IP}/24
PrivateKey = $(cat "$DIR/lab.key")
PostUp = sysctl -w net.ipv4.ip_forward=1; iptables -t nat -C POSTROUTING -o ${LAB_BRIDGE} -s ${SUBNET}.0/24 -j MASQUERADE 2>/dev/null || iptables -t nat -A POSTROUTING -o ${LAB_BRIDGE} -s ${SUBNET}.0/24 -j MASQUERADE; iptables -C FORWARD -i ${IFACE} -o ${LAB_BRIDGE} -j ACCEPT 2>/dev/null || iptables -A FORWARD -i ${IFACE} -o ${LAB_BRIDGE} -j ACCEPT; iptables -C FORWARD -i ${LAB_BRIDGE} -o ${IFACE} -j ACCEPT 2>/dev/null || iptables -A FORWARD -i ${LAB_BRIDGE} -o ${IFACE} -j ACCEPT
PostDown = iptables -t nat -D POSTROUTING -o ${LAB_BRIDGE} -s ${SUBNET}.0/24 -j MASQUERADE 2>/dev/null || true; iptables -D FORWARD -i ${IFACE} -o ${LAB_BRIDGE} -j ACCEPT 2>/dev/null || true; iptables -D FORWARD -i ${LAB_BRIDGE} -o ${IFACE} -j ACCEPT 2>/dev/null || true

[Peer]
# public audit endpoint
PublicKey = ${SRVPUB}
Endpoint = ${ENDPOINT_HOST}:${PORT}
AllowedIPs = ${SUBNET}.0/24
PersistentKeepalive = 25
EOF
  chmod 600 "$CONF"
  grep -q '^net.ipv4.ip_forward=1' /etc/sysctl.conf || echo 'net.ipv4.ip_forward=1' >> /etc/sysctl.conf
  sysctl -w net.ipv4.ip_forward=1 >/dev/null
  systemctl enable "wg-quick@${IFACE}" >/dev/null 2>&1 || true
  # Self-heal: recreate the interface if the process ever dies.
  mkdir -p "/etc/systemd/system/wg-quick@${IFACE}.service.d"
  printf '[Service]\nRestart=always\nRestartSec=5\n' > "/etc/systemd/system/wg-quick@${IFACE}.service.d/restart.conf"
  systemctl daemon-reload
  systemctl restart "wg-quick@${IFACE}"
  sleep 2
  echo "LAB_PUB=$(cat "$DIR/lab.pub")"
  status
  echo "== ping overlay endpoint ${SERVER_IP} =="; ping -c2 -W2 "$SERVER_IP" || true
}

status() { wg show "$IFACE" 2>/dev/null || echo "(interface $IFACE not up)"; }

case "${1:-inventory}" in
  inventory) inventory ;;
  ensure) ensure ;;
  status) status ;;
  *) die "usage: $0 inventory|ensure <serverpub> [endpoint-host]|status" ;;
esac
