#!/usr/bin/env bash
# Idempotent installer for the SCOPED, non-root labvpn identity on the PUBLIC
# endpoint. Creates a system user whose only capability is add/list/revoke
# overlay peers and read a generated client config, via a forced SSH command.
#
# Run as root on the endpoint (138.197.105.82). Companion source scripts must be
# in the same directory as this file (default) or $SRC_DIR.
#
#   lab-audit-scoped-deploy.sh
#
# It never prints the labvpn private key; it only reports the key file path.
set -euo pipefail

SRC="${SRC_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
LAN=labvpn
LGROUP=labvpn
LUSER="${LABVPN_USER:-$LAN}"
LHOME="${LABVPN_HOME:-/var/lib/labvpn}"
LIB="${LABVPN_LIB:-/usr/local/lib/labvpn}"
WRAPPER="${LABVPN_WRAPPER:-/usr/local/bin/labvpn-run}"
# NOTE: a literal /usr/sbin/nologin shell cannot be used for an account that
# relies on an SSH forced command: sshd executes the forced command *through*
# the account's login shell, so nologin aborts it. We install a dedicated,
# non-interactive placeholder shell that ignores all arguments and always execs
# the forced-command wrapper. See /usr/local/bin/labvpn-shell.
LOGIN_SHELL="${LABVPN_SHELL:-/usr/local/bin/labvpn-shell}"
WRAPPER_SHELL="/usr/local/bin/labvpn-shell"
KEY="${LABVPN_KEY:-/root/labvpn_ed25519}"
SUDOERS="/etc/sudoers.d/labvpn"
WG_DIR="${WG_DIR:-/etc/wireguard/wgaudit0}"
CONF="${WG_DIR}.conf"
PEERS="$WG_DIR/peers.tsv"
DROPIN_DIR="/etc/systemd/system/wg-quick@wgaudit0.service.d"
DROPIN="$DROPIN_DIR/restart.conf"

log() { echo "[labvpn-deploy] $*"; }
die() { echo "ERROR: $*" >&2; exit 1; }

[ "$(id -u)" -eq 0 ] || die "run as root"

# ---- source files -----------------------------------------------------------
for s in lab-audit-add-agent.sh lab-audit-list-agents.sh lab-audit-revoke-agent.sh lab-audit-verify.sh labvpn-run.sh; do
  [ -f "$SRC/$s" ] || die "missing source file: $SRC/$s"
done
[ -f "$CONF" ] || die "overlay conf missing: $CONF (run lab-audit-endpoint.sh ensure first)"

# ---- restricted login shell -------------------------------------------------
# sshd executes the authorized_keys forced command *through* the account's login
# shell, so a literal /usr/sbin/nologin would abort it. Install a non-interactive
# placeholder shell that ignores all arguments and always execs the wrapper.
shtmp="$(mktemp)"
cat > "$shtmp" <<EOS
#!/bin/sh
# Non-interactive placeholder shell for $LUSER. Ignores all arguments and always
# hands off to the forced-command wrapper. Do not use interactively.
exec $WRAPPER
EOS
install -m 0755 -o root -g root "$shtmp" "$WRAPPER_SHELL"
rm -f "$shtmp"
grep -qxF "$WRAPPER_SHELL" /etc/shells || echo "$WRAPPER_SHELL" >> /etc/shells
log "installed restricted shell $WRAPPER_SHELL"

# ---- system user ------------------------------------------------------------
if id "$LUSER" >/dev/null 2>&1; then
  log "user $LUSER already exists"
  usermod --shell "$LOGIN_SHELL" "$LUSER"
else
  useradd --system --create-home --home-dir "$LHOME" --shell "$LOGIN_SHELL" "$LUSER"
  log "created system user $LUSER (restricted shell $LOGIN_SHELL)"
fi
# system account: primary group only, no supplementary groups
if id -nG "$LUSER" | tr ' ' '\n' | grep -qvx "$(id -gn "$LUSER")"; then
  log "WARN: $LUSER has supplementary groups: $(id -nG "$LUSER")"
fi
install -d -m 0755 -o "$LUSER" -g "$LGROUP" "$LHOME"

# ---- directories and library scripts ---------------------------------------
install -d -m 0755 -o root -g root "$LIB"
install -d -m 0700 -o root -g root "$WG_DIR/clients"

install -m 0755 -o root -g root "$SRC/lab-audit-add-agent.sh"    "$LIB/add-agent.sh"
install -m 0755 -o root -g root "$SRC/lab-audit-list-agents.sh"  "$LIB/list-agents.sh"
install -m 0755 -o root -g root "$SRC/lab-audit-revoke-agent.sh" "$LIB/revoke-agent.sh"
install -m 0755 -o root -g root "$SRC/lab-audit-verify.sh"       "$LIB/verify.sh"

# get-client.sh is generated here so the deploy is self-contained.
gctmp="$(mktemp)"
cat > "$gctmp" <<'EOS'
#!/usr/bin/env bash
# Return the server-generated client config for a peer, if one exists.
set -euo pipefail
IFACE="${IFACE:-wgaudit0}"
NAME="${1:?usage: get-client.sh <name>}"
[ "$(id -u)" -eq 0 ] || { echo "run as root" >&2; exit 1; }
if ! [[ "$NAME" =~ ^[A-Za-z0-9_.-]{1,32}$ ]]; then
  echo "ERROR: invalid agent name '$NAME'" >&2
  exit 2
fi
F="/etc/wireguard/${IFACE}/clients/${NAME}.conf"
[ -f "$F" ] || { echo "ERROR: no client config for '$NAME' (peer may have supplied its own key)" >&2; exit 1; }
cat "$F"
EOS
install -m 0755 -o root -g root "$gctmp" "$LIB/get-client.sh"
rm -f "$gctmp"

install -m 0755 -o root -g root "$SRC/labvpn-run.sh" "$WRAPPER"

# ---- registry ---------------------------------------------------------------
if [ ! -f "$PEERS" ]; then
  : > "$PEERS"
  log "created registry $PEERS"
fi
chmod 600 "$PEERS"; chown root:root "$PEERS"

# ---- sudoers (validate before install) --------------------------------------
stmp="$(mktemp)"
cat > "$stmp" <<EOS
# Scoped labvpn identity (managed by tools/lab-vpn/lab-audit-scoped-deploy.sh)
${LUSER} ALL=(root) NOPASSWD: ${LIB}/add-agent.sh *, ${LIB}/list-agents.sh, ${LIB}/revoke-agent.sh *, ${LIB}/verify.sh, ${LIB}/verify.sh *, ${LIB}/get-client.sh *
EOS
visudo -cf "$stmp" >/dev/null || { rm -f "$stmp"; die "sudoers validation (visudo -cf) failed"; }
install -m 0440 -o root -g root "$stmp" "$SUDOERS"
rm -f "$stmp"
log "installed sudoers $SUDOERS (visudo validated)"

# ---- key + authorized_keys --------------------------------------------------
if [ ! -f "$KEY" ]; then
  ssh-keygen -t ed25519 -N '' -C labvpn -f "$KEY" >/dev/null
  log "generated keypair $KEY"
else
  log "keypair $KEY already exists"
fi
[ -f "$KEY.pub" ] || die "missing public key $KEY.pub"
PUB="$(awk '{print $1" "$2}' "$KEY.pub")"

install -d -m 0700 -o "$LUSER" -g "$LGROUP" "$LHOME/.ssh"
printf 'command="%s",no-port-forwarding,no-agent-forwarding,no-X11-forwarding,no-pty,no-user-rc %s labvpn\n' \
  "$WRAPPER" "$PUB" > "$LHOME/.ssh/authorized_keys"
chown "$LUSER:$LGROUP" "$LHOME/.ssh/authorized_keys"
chmod 0600 "$LHOME/.ssh/authorized_keys"

# ---- systemd: drop stale invalid drop-in ------------------------------------
# wg-quick@.service is Type=oneshot, for which systemd rejects Restart=; the old
# Restart=always drop-in made the unit "bad-setting" and it would not start.
# Remove it if present. Do NOT recreate it.
if [ -e "$DROPIN" ]; then
  rm -f "$DROPIN"
  log "removed stale/invalid systemd drop-in $DROPIN (Restart= is invalid for Type=oneshot)"
else
  log "no systemd drop-in needed (wg-quick@.service is Type=oneshot)"
fi

# ---- backward-compat copies to /root ---------------------------------------
install -m 0755 "$LIB/add-agent.sh"    /root/add-agent.sh
install -m 0755 "$LIB/list-agents.sh"  /root/list-agents.sh
install -m 0755 "$LIB/revoke-agent.sh" /root/revoke-agent.sh
install -m 0755 "$LIB/verify.sh"       /root/verify.sh
install -m 0755 "$LIB/get-client.sh"   /root/get-client.sh
for s in lab-audit-add-agent.sh lab-audit-list-agents.sh lab-audit-revoke-agent.sh lab-audit-verify.sh labvpn-run.sh lab-audit-scoped-deploy.sh; do
  [ "$SRC/$s" = "/root/$s" ] || cp -f "$SRC/$s" "/root/$s"
done

log "reloading systemd"
systemctl daemon-reload

# ---- summary ----------------------------------------------------------------
echo
echo "=== labvpn scoped identity deployed ==="
echo "user              : $LUSER (restricted shell $WRAPPER_SHELL, home $LHOME)"
echo "library scripts   : $LIB/{add-agent,list-agents,revoke-agent,verify,get-client}.sh"
echo "forced-command    : $WRAPPER"
echo "sudoers           : $SUDOERS (0440, visudo validated)"
echo "authorized_keys   : $LHOME/.ssh/authorized_keys (0600, forced command)"
echo "registry          : $PEERS (0600)"
echo "systemd drop-in   : none (Type=oneshot; RemainAfterExit=yes)"
echo "enforced checks   : visudo -c:"
visudo -c 2>&1 | sed 's/^/                    /' || true
echo "LABVPN_PRIVATE_KEY_FILE=$KEY"
