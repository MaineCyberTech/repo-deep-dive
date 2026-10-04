#!/usr/bin/env bash
# Revoke an overlay agent: remove its [Peer] block from the conf, sync, drop the
# registry row, and delete any server-generated client key/config.
#   lab-audit-revoke-agent.sh <name>
set -euo pipefail

IFACE="${IFACE:-wgaudit0}"
DIR="/etc/wireguard/${IFACE}"
CONF="/etc/wireguard/${IFACE}.conf"
CLIENTS="$DIR/clients"
REGISTRY="$DIR/peers.tsv"

NAME="${1:?usage: revoke-agent.sh <name>}"
[ "$(id -u)" -eq 0 ] || { echo "run as root" >&2; exit 1; }
if ! [[ "$NAME" =~ ^[A-Za-z0-9_.-]{1,32}$ ]]; then
  echo "ERROR: invalid agent name '$NAME' (allowed: [A-Za-z0-9_.-]{1,32})" >&2
  exit 2
fi
[ -f "$CONF" ] || { echo "overlay conf missing: $CONF" >&2; exit 1; }

REG_PUB=""
if [ -f "$REGISTRY" ]; then
  REG_PUB="$(awk -F'\t' -v n="$NAME" '$1==n{print $3}' "$REGISTRY" | head -1)"
fi

# Remove the peer block identified by the "# agent: <name>" comment and/or the
# registry public key. Never removes the [Interface] block or the lab peer.
cp -a "$CONF" "$CONF.bak-$(date -u +%Y%m%dT%H%M%SZ)"
tmp="$(mktemp)"
awk -v n="$NAME" -v p="$REG_PUB" '
  BEGIN { RS=""; ORS="\n\n" }
  {
    drop = 0
    if (index($0, "[Peer]") > 0) {
      if (index($0, "# agent: " n) > 0) drop = 1
      else if (p != "" && index($0, p) > 0) drop = 1
    }
    if (!drop) print
  }
' "$CONF" > "$tmp"
install -m 600 "$tmp" "$CONF"
rm -f "$tmp"
wg syncconf "$IFACE" <(wg-quick strip "$IFACE")

if [ -f "$REGISTRY" ]; then
  rtmp="$(mktemp)"
  awk -F'\t' -v n="$NAME" '$1!=n' "$REGISTRY" > "$rtmp"
  install -m 600 "$rtmp" "$REGISTRY"
  rm -f "$rtmp"
fi

rm -f "$CLIENTS/$NAME.key" "$CLIENTS/$NAME.conf"
echo "REVOKED=$NAME"
