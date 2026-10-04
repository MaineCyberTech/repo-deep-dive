#!/usr/bin/env bash
# One-command lab-overlay setup for a NEW agent / server / workstation.
#
# Generates its own keypair, registers the PUBLIC key through the scoped `labvpn`
# identity, installs the tunnel, adds friendly names and verifies the lab. The private
# key never leaves this machine.
#
#   LABVPN_KEY=/path/to/labvpn_key  lab-audit-bootstrap.sh [name] [endpoint-host]
#
# Env: LABVPN_KEY (required), LAB_ENDPOINT_HOST, LAB_ENDPOINT_USER, IFACE, NO_HOSTS
# Exit 0 = connected and verified. Non-zero = could not set up (caller should run work
# LOCALLY instead - see tools/lab-vpn/lab-audit-run.sh).
set -euo pipefail

IFACE="${IFACE:-lab-audit}"
RAWNAME="${1:-$(hostname -s 2>/dev/null || echo agent)}"
NAME="$(printf '%s' "$RAWNAME" | tr 'A-Z' 'a-z' | tr -cd 'a-z0-9_.-' | cut -c1-32)"
[ -n "$NAME" ] || NAME="agent"
HOST="${LAB_ENDPOINT_HOST:-${2:-138.197.105.82}}"
USER="${LAB_ENDPOINT_USER:-labvpn}"
KEY="${LABVPN_KEY:-$HOME/.ssh/labvpn}"
HERE="$(cd "$(dirname "$0")" && pwd)"
SUDO=""; [ "$(id -u)" -ne 0 ] && SUDO="sudo"

die() { echo "[bootstrap] ERROR: $*" >&2; exit 1; }

command -v ssh >/dev/null 2>&1 || die "ssh not found"
[ -f "$KEY" ] || die "scoped key not found at '$KEY' (set LABVPN_KEY to the labvpn private key)"

if ! command -v wg >/dev/null 2>&1; then
  echo "[bootstrap] installing wireguard-tools"
  if command -v apt-get >/dev/null; then $SUDO apt-get update -qq && $SUDO apt-get install -y -qq wireguard-tools
  elif command -v dnf >/dev/null; then $SUDO dnf install -y -q wireguard-tools
  elif command -v brew >/dev/null; then brew install wireguard-tools
  else die "install wireguard-tools manually"; fi
fi

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
umask 077
wg genkey > "$TMP/priv"; wg pubkey < "$TMP/priv" > "$TMP/pub"

echo "[bootstrap] registering peer '$NAME' via $USER@$HOST"
set +e
OUT="$(ssh -i "$KEY" -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=12 \
      "$USER@$HOST" "add-agent $NAME $(cat "$TMP/pub")" 2>"$TMP/err")"
RC=$?
set -e
if [ "$RC" -ne 0 ]; then
  echo "[bootstrap] registration failed:"; sed 's/^/    /' "$TMP/err" >&2
  die "lab endpoint unreachable or key rejected (run work locally instead)"
fi
printf '%s\n' "$OUT"

srv="$(printf '%s\n' "$OUT" | sed -n 's/^SERVER_PUB=//p' | tail -1)"
ep="$(printf '%s\n' "$OUT" | sed -n 's/^ENDPOINT=//p' | tail -1)"
ip="$(printf '%s\n' "$OUT" | sed -n 's/^AGENT_IP=//p' | tail -1)"
[ -n "$srv" ] && [ -n "$ep" ] && [ -n "$ip" ] || die "unexpected registration response"

CONF="$TMP/$NAME.conf"
cat > "$CONF" <<EOF
[Interface]
PrivateKey = $(cat "$TMP/priv")
Address = ${ip}/24

[Peer]
PublicKey = ${srv}
Endpoint = ${ep}
AllowedIPs = 10.250.0.0/24, 172.23.128.0/20
PersistentKeepalive = 25
EOF

echo "[bootstrap] bringing up '$IFACE' and verifying"
exec bash "$HERE/lab-audit-connect.sh" "$CONF" "$IFACE"
