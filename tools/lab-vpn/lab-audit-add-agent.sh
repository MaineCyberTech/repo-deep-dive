#!/usr/bin/env bash
# Add an audit agent/developer to the overlay and emit a client config.
# Run on the PUBLIC endpoint (droplet). Idempotent per agent name.
#   lab-audit-add-agent.sh <name> [endpoint-host] [agent-subnet-ip]
#
# Preferred (agent keeps its own private key): the agent runs `wg genkey` locally and
# passes its PUBLIC key here, so no private key is ever generated or stored on the server:
#   AGENT_PUBKEY='<base64 pubkey>' lab-audit-add-agent.sh <name> [endpoint-host] [ip]
# Otherwise the endpoint generates the keypair and stores it under DIR/clients/.
set -euo pipefail
IFACE="${IFACE:-wgaudit0}"
PORT="${PORT:-51900}"
SUBNET="${SUBNET:-10.250.0}"
DIR="/etc/wireguard/${IFACE}"
CONF="/etc/wireguard/${IFACE}.conf"
CLIENTS="$DIR/clients"
NAME="${1:?usage: add-agent.sh <name> [endpoint-host] [ip]}"
EPHOST="${2:-$(curl -s -m5 https://api.ipify.org || echo 138.197.105.82)}"
IP="${3:-}"
AGENT_PUBKEY="${AGENT_PUBKEY:-}"

[ "$(id -u)" -eq 0 ] || { echo "run as root" >&2; exit 1; }
[ -f "$CONF" ] || { echo "overlay not provisioned; run lab-audit-endpoint.sh ensure" >&2; exit 1; }
mkdir -p "$CLIENTS"; chmod 700 "$CLIENTS"; umask 077

if [ -n "$AGENT_PUBKEY" ]; then
  # Agent-generated keypair: only the public key is known here.
  PUB="$AGENT_PUBKEY"
  KEY=""
else
  KEY="$CLIENTS/$NAME.key"
  [ -f "$KEY" ] || wg genkey > "$KEY"
  PUB=$(wg pubkey < "$KEY")
fi

# Allocate an address if not provided.
if [ -z "$IP" ]; then
  if grep -q "$PUB" "$CONF"; then
    IP=$(awk -v p="$PUB" '$1=="PublicKey"{k=$3} k==p && $1=="AllowedIPs"{print $3}' "$CONF" | head -1 | cut -d/ -f1)
  fi
fi
if [ -z "$IP" ]; then
  used=$(grep -oE "^AllowedIPs = ${SUBNET}\.[0-9]+" "$CONF" 2>/dev/null | grep -oE '[0-9]+$' | sort -n | tail -1)
  n=$(( ${used:-9} + 1 )); [ "$n" -lt 10 ] && n=10
  IP="${SUBNET}.${n}"
fi

if ! grep -q "$PUB" "$CONF"; then
  cp -a "$CONF" "$CONF.bak-$(date -u +%Y%m%dT%H%M%SZ)"
  printf '\n[Peer]\n# agent: %s\nPublicKey = %s\nAllowedIPs = %s/32\n' "$NAME" "$PUB" "$IP" >> "$CONF"
  wg syncconf "$IFACE" <(wg-quick strip "$IFACE")
fi

if [ -n "$KEY" ]; then
  CLIENT="$CLIENTS/$NAME.conf"
  cat > "$CLIENT" <<EOF
[Interface]
PrivateKey = $(cat "$KEY")
Address = ${IP}/24

[Peer]
PublicKey = $(cat "$DIR/server.pub")
Endpoint = ${EPHOST}:${PORT}
AllowedIPs = ${SUBNET}.0/24, 172.23.128.0/20
PersistentKeepalive = 25
EOF
  chmod 600 "$CLIENT"
  echo "CLIENT_CONF=$CLIENT"
  echo "CLIENT_PRIVATE_KEY=included-on-server"
else
  # Agent holds the private key; emit only the non-secret connection parameters.
  echo "CLIENT_CONF=(agent-supplied public key; no private key stored)"
  echo "CLIENT_PRIVATE_KEY=local-to-agent"
fi
echo "AGENT=$NAME"
echo "AGENT_IP=$IP"
echo "SERVER_PUB=$(cat "$DIR/server.pub")"
echo "ENDPOINT=${EPHOST}:${PORT}"
