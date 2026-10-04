#!/usr/bin/env bash
# Add (or upsert) an audit agent/developer on the overlay and emit a client config.
# Runs on the PUBLIC endpoint. Idempotent per agent name.
#
#   lab-audit-add-agent.sh <name> [public-key] [ip]
#
# Preferred (agent keeps its own private key): pass the agent's PUBLIC key so no
# private key is ever generated or stored on the server:
#   AGENT_PUBKEY='<base64 pubkey>' lab-audit-add-agent.sh <name> [ip]
# Otherwise the endpoint generates the keypair and stores it under DIR/clients/.
#
# Env overrides: AGENT_PUBKEY EPHOST IFACE PORT SUBNET
set -euo pipefail

IFACE="${IFACE:-wgaudit0}"
PORT="${PORT:-51900}"
SUBNET="${SUBNET:-10.250.0}"
DIR="/etc/wireguard/${IFACE}"
CONF="/etc/wireguard/${IFACE}.conf"
CLIENTS="$DIR/clients"
REGISTRY="$DIR/peers.tsv"

NAME="${1:?usage: add-agent.sh <name> [public-key] [ip]}"
PUB_ARG="${2:-}"
IP_ARG="${3:-}"

[ "$(id -u)" -eq 0 ] || { echo "run as root" >&2; exit 1; }

# ---- validation -------------------------------------------------------------
if ! [[ "$NAME" =~ ^[A-Za-z0-9_.-]{1,32}$ ]]; then
  echo "ERROR: invalid agent name '$NAME' (allowed: [A-Za-z0-9_.-]{1,32})" >&2
  exit 2
fi
AGENT_PUBKEY="${PUB_ARG:-${AGENT_PUBKEY:-}}"
if [ -n "$AGENT_PUBKEY" ] && ! [[ "$AGENT_PUBKEY" =~ ^[A-Za-z0-9+/]{42,44}=?$ ]]; then
  echo "ERROR: invalid public key" >&2
  exit 2
fi
if [ -n "$IP_ARG" ] && ! [[ "$IP_ARG" =~ ^[0-9]{1,3}(\.[0-9]{1,3}){3}$ ]]; then
  echo "ERROR: invalid ip '$IP_ARG'" >&2
  exit 2
fi

[ -f "$CONF" ] || { echo "overlay not provisioned; run lab-audit-endpoint.sh ensure" >&2; exit 1; }
[ -f "$DIR/server.pub" ] || { echo "missing $DIR/server.pub" >&2; exit 1; }

mkdir -p "$CLIENTS"; chmod 700 "$CLIENTS"; umask 077
[ -f "$REGISTRY" ] || : > "$REGISTRY"
chmod 600 "$REGISTRY"

EPHOST="${EPHOST:-$(curl -s -m5 https://api.ipify.org 2>/dev/null || true)}"
[ -n "$EPHOST" ] || EPHOST="138.197.105.82"

# ---- key material -----------------------------------------------------------
if [ -n "$AGENT_PUBKEY" ]; then
  # Agent-generated keypair: only the public key is known here.
  PUB="$AGENT_PUBKEY"
  KEY=""
else
  KEY="$CLIENTS/$NAME.key"
  [ -f "$KEY" ] || wg genkey > "$KEY"
  chmod 600 "$KEY"
  PUB="$(wg pubkey < "$KEY")"
fi

# ---- address allocation -----------------------------------------------------
# Order: explicit ip > existing registry entry for name > pubkey already in conf
#        > next free (scan conf AllowedIPs AND registry, max+1, min .10).
ip_in_registry() { awk -F'\t' -v n="$NAME" '$1==n{print $2}' "$REGISTRY" | head -1; }
ip_in_conf() {
  awk -v p="$PUB" '
    $1=="PublicKey" { pk=$3 }
    $1=="AllowedIPs" && pk==p { print $3 }
  ' "$CONF" | head -1 | cut -d/ -f1
}

IP=""
[ -n "$IP_ARG" ] && IP="$IP_ARG"
[ -z "$IP" ] && IP="$(ip_in_registry || true)"
[ -z "$IP" ] && IP="$(ip_in_conf || true)"
if [ -z "$IP" ]; then
  max_conf="$(grep -oE "AllowedIPs = ${SUBNET}\.[0-9]+" "$CONF" 2>/dev/null | grep -oE '[0-9]+$' | sort -n | tail -1 || true)"
  max_reg="$(awk -F'\t' -v s="${SUBNET}." '$2 ~ ("^" s "[0-9]+$" ){ n=split($2,a,"."); print a[n] }' "$REGISTRY" 2>/dev/null | sort -n | tail -1 || true)"
  used=0
  [ -n "${max_conf:-}" ] && [ "$max_conf" -gt "$used" ] && used="$max_conf"
  [ -n "${max_reg:-}" ] && [ "$max_reg" -gt "$used" ] && used="$max_reg"
  n=$(( used + 1 )); [ "$n" -lt 10 ] && n=10
  IP="${SUBNET}.${n}"
fi

# ---- add peer to conf only if its public key is absent ----------------------
if ! grep -qF "$PUB" "$CONF"; then
  cp -a "$CONF" "$CONF.bak-$(date -u +%Y%m%dT%H%M%SZ)"
  printf '\n[Peer]\n# agent: %s\nPublicKey = %s\nAllowedIPs = %s/32\n' "$NAME" "$PUB" "$IP" >> "$CONF"
  wg syncconf "$IFACE" <(wg-quick strip "$IFACE")
  echo "PEER_ADDED=$NAME" >&2
fi

# ---- registry upsert (tab separated: name, ip, pubkey, added-UTC) -----------
tmp="$(mktemp)"
awk -F'\t' -v n="$NAME" '$1!=n' "$REGISTRY" > "$tmp"
printf '%s\t%s\t%s\t%s\n' "$NAME" "$IP" "$PUB" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$tmp"
install -m 600 "$tmp" "$REGISTRY"
rm -f "$tmp"

# ---- client config ----------------------------------------------------------
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
  echo "CLIENT_PRIVATE_KEY=local-to-agent"
fi
echo "AGENT=$NAME"
echo "AGENT_IP=$IP"
echo "SERVER_PUB=$(cat "$DIR/server.pub")"
echo "ENDPOINT=${EPHOST}:${PORT}"
