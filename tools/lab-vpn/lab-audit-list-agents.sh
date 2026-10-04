#!/usr/bin/env bash
# List overlay agents from the registry, enriched with current handshake age.
# Columns: NAME IP PUBKEY ADDED HANDSHAKE
set -euo pipefail

IFACE="${IFACE:-wgaudit0}"
DIR="/etc/wireguard/${IFACE}"
REGISTRY="$DIR/peers.tsv"

if [ ! -s "$REGISTRY" ]; then
  echo "(no registry)"
  exit 0
fi

# pubkey -> latest-handshake epoch (wg dump peer field 5)
HS="$(wg show "$IFACE" dump 2>/dev/null | awk 'NR>1{print $1"\t"$5}')"
now="$(date -u +%s)"

printf '%-20s %-14s %-46s %-22s %s\n' NAME IP PUBKEY ADDED HANDSHAKE
awk -F'\t' 'NF>=3{print}' "$REGISTRY" | while IFS=$'\t' read -r name ip pub added _rest; do
  epoch="$(printf '%s\n' "$HS" | awk -F'\t' -v p="$pub" '$1==p{print $2}' | head -1)"
  if [ -z "${epoch:-}" ] || [ "${epoch:-0}" = "0" ]; then
    hs="none"
  else
    age=$(( now - epoch ))
    [ "$age" -lt 0 ] && age=0
    if [ "$age" -lt 60 ]; then hs="${age}s ago"
    elif [ "$age" -lt 3600 ]; then hs="$((age/60))m ago"
    else hs="$((age/3600))h ago"; fi
  fi
  printf '%-20s %-14s %-46s %-22s %s\n' "$name" "$ip" "$pub" "${added:-?}" "$hs"
done
