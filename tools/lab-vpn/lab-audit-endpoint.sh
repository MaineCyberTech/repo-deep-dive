#!/usr/bin/env bash
# Lab audit VPN endpoint (runs on the PUBLIC droplet mct-portal-dev).
#
# Creates a DEDICATED overlay interface for audit agents, separate from any existing
# WireGuard (e.g. the falcon telemetry wg0). It NEVER edits other interfaces, backs up
# before writing, and runs pre-checks (port/subnet/interface collisions).
#
#   lab-audit-endpoint.sh inventory      # read-only: report current state (default)
#   lab-audit-endpoint.sh ensure [labpub] # idempotently create/refresh the overlay
#   lab-audit-endpoint.sh status
#
# Env overrides: IFACE PORT SUBNET LAB_IP SERVER_IP
set -euo pipefail

IFACE="${IFACE:-wgaudit0}"
PORT="${PORT:-51900}"
SUBNET="${SUBNET:-10.250.0}"
SERVER_IP="${SERVER_IP:-${SUBNET}.1}"
LAB_IP="${LAB_IP:-${SUBNET}.9}"
WAN="${WAN:-eth0}"
DIR="/etc/wireguard/${IFACE}"
CONF="/etc/wireguard/${IFACE}.conf"
LABPUB="${2:-${LABPUB:-}}"

say() { echo "[$(date -u +%H:%M:%S)] $*"; }
die() { echo "ERROR: $*" >&2; exit 1; }

inventory() {
  echo "== interfaces =="; wg show all 2>/dev/null || echo "(none)"
  echo "== /etc/wireguard =="; ls -la /etc/wireguard 2>/dev/null
  echo "== this overlay =="
  if [ -f "$CONF" ]; then echo "conf: $CONF"; sed -n '1,40p' "$CONF"; else echo "not provisioned ($CONF)"; fi
  echo "== udp listeners =="; ss -lunp 2>/dev/null | grep -E "UNCONN|udp" || true
  echo "== routes on ${SUBNET}.0/24 =="; ip route | grep -E "${SUBNET}\." || echo "(none)"
  echo "== ufw =="; ufw status 2>/dev/null | head -20 || true
  echo "== public addr =="; ip -4 -br a show "$WAN" 2>/dev/null || ip -br a | head
}

precheck() {
  # Never touch a different interface's config.
  if [ -f "$CONF" ]; then say "existing overlay conf found (will back up before changes)"; fi
  # Port collision with a DIFFERENT service/interface.
  if ss -lunp 2>/dev/null | grep -qE ":${PORT}\b"; then
    if wg show "$IFACE" >/dev/null 2>&1; then
      say "port $PORT already held by our interface $IFACE (ok)"
    else
      die "UDP port $PORT is already in use by another service; choose PORT=..."
    fi
  fi
  # Subnet collision.
  if ip route | grep -qE "${SUBNET}\.0/24"; then
    if ip -4 -br a show "$IFACE" 2>/dev/null | grep -q "${SUBNET}\."; then
      say "subnet ${SUBNET}.0/24 already on $IFACE (ok)"
    else
      die "subnet ${SUBNET}.0/24 already routed elsewhere; choose SUBNET=..."
    fi
  fi
  # Refuse to clobber a pre-existing unrelated wg0 if we somehow target it.
  if [ "$IFACE" = "wg0" ]; then die "refusing to use wg0 (reserved for falcon telemetry)"; fi
}

ensure() {
  [ "$(id -u)" -eq 0 ] || die "run as root"
  precheck
  mkdir -p "$DIR"; chmod 700 "$DIR"
  umask 077
  [ -f "$DIR/server.key" ] || wg genkey > "$DIR/server.key"
  wg pubkey < "$DIR/server.key" > "$DIR/server.pub"

  if [ -f "$CONF" ]; then cp -a "$CONF" "$CONF.bak-$(date -u +%Y%m%dT%H%M%SZ)"; fi

  cat > "$CONF" <<EOF
# Lab audit overlay (managed by repo-deep-dive scripts/lab-audit-endpoint.sh).
# Dedicated interface; do not confuse with wg0 (falcon telemetry).
[Interface]
Address = ${SERVER_IP}/24
ListenPort = ${PORT}
PrivateKey = $(cat "$DIR/server.key")
PostUp = sysctl -w net.ipv4.ip_forward=1; iptables -C INPUT -p udp --dport ${PORT} -j ACCEPT 2>/dev/null || iptables -I INPUT -p udp --dport ${PORT} -j ACCEPT; iptables -t nat -C POSTROUTING -o ${WAN} -j MASQUERADE 2>/dev/null || iptables -t nat -A POSTROUTING -o ${WAN} -j MASQUERADE; iptables -C FORWARD -i ${IFACE} -j ACCEPT 2>/dev/null || iptables -A FORWARD -i ${IFACE} -j ACCEPT; iptables -C FORWARD -o ${IFACE} -j ACCEPT 2>/dev/null || iptables -A FORWARD -o ${IFACE} -j ACCEPT
PostDown = iptables -t nat -D POSTROUTING -o ${WAN} -j MASQUERADE 2>/dev/null || true; iptables -D FORWARD -i ${IFACE} -j ACCEPT 2>/dev/null || true; iptables -D FORWARD -o ${IFACE} -j ACCEPT 2>/dev/null || true
EOF
  if [ -n "$LABPUB" ]; then
    cat >> "$CONF" <<EOF

[Peer]
# lab (advertises ${LAB_SUBNET:-172.23.128.0/20})
PublicKey = ${LABPUB}
AllowedIPs = ${LAB_IP}/32, ${LAB_SUBNET:-172.23.128.0/20}
EOF
  else
    say "no LABPUB yet -> overlay has no lab peer; re-run 'ensure <labpub>' after the lab joins"
  fi
  chmod 600 "$CONF"

  grep -q '^net.ipv4.ip_forward=1' /etc/sysctl.conf || echo 'net.ipv4.ip_forward=1' >> /etc/sysctl.conf
  sysctl -w net.ipv4.ip_forward=1 >/dev/null
  ufw allow "${PORT}/udp" >/dev/null 2>&1 || true
  systemctl enable "wg-quick@${IFACE}" >/dev/null 2>&1 || true
  # wg-quick@.service is Type=oneshot; systemd rejects Restart= for oneshot units,
  # so a "Restart=always" drop-in makes the unit a bad-setting that refuses to start.
  # Remove any stale/invalid drop-in; the interface is kernel state kept alive by
  # RemainAfterExit=yes and is recreated on boot via `enable`.
  rm -f "/etc/systemd/system/wg-quick@${IFACE}.service.d/restart.conf"
  systemctl daemon-reload
  systemctl restart "wg-quick@${IFACE}"
  sleep 1
  echo "SERVER_PUB=$(cat "$DIR/server.pub")"
  echo "ENDPOINT=$(curl -s -m5 https://api.ipify.org || echo 138.197.105.82):${PORT}"
  status
}

status() { wg show "$IFACE" 2>/dev/null || echo "(interface $IFACE not up)"; }

case "${1:-inventory}" in
  inventory) inventory ;;
  ensure) ensure ;;
  status) status ;;
  *) die "usage: $0 inventory|ensure <labpub>|status" ;;
esac
