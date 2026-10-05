#!/usr/bin/env bash
# Preflight gate for audit/remediation work.
#
# Verifies that lab access is SET UP and TESTED before work is dispatched. It separates
# "the lab is genuinely down" from "my local access is down":
#
#   1. Lab state is checked REMOTELY and independently of the local overlay (via the scoped
#      `labvpn` identity running `health` on the endpoint). This is the source of truth.
#   2. A LOCAL attempt (bring the overlay up) is made ONLY when the lab is confirmed down
#      (or cannot be classified), never when the lab is up.
#
# Modes:
#   --mode local  (default) PASS requires this machine to reach the lab (local overlay).
#   --mode lab              PASS requires the lab itself to be up (dispatching to the lab,
#                           e.g. CI self-hosted runners) — local overlay not required.
#
#   lab-audit-preflight.sh [--mode local|lab] [--conf <client.conf>] [--iface <name>]
#                          [--no-pack] [--remote-key <keyfile>] [--host H] [--user U]
#
# On success writes tools/lab-vpn/.lab-ready.json (gitignored).
# Exit 0 = ready (RESULT: PASS). Exit 1 = not ready (RESULT: FAIL). Exit 2 = usage error.

set -uo pipefail

IFACE="${IFACE:-lab-audit}"
CONF=""; DO_PACK=1; MODE=local
REMOTE_KEY="${LABVPN_KEY:-}"
HOST="${LAB_ENDPOINT_HOST:-138.197.105.82}"
USER="${LAB_ENDPOINT_USER:-labvpn}"
while [ $# -gt 0 ]; do
  case "$1" in
    --mode) MODE="${2:?}"; shift 2 ;;
    --conf) CONF="${2:?}"; shift 2 ;;
    --iface) IFACE="${2:?}"; shift 2 ;;
    --no-pack) DO_PACK=0; shift ;;
    --remote-key) REMOTE_KEY="${2:?}"; shift 2 ;;
    --host) HOST="${2:?}"; shift 2 ;;
    --user) USER="${2:?}"; shift 2 ;;
    -h|--help) grep -E '^#( |$)' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done
case "$MODE" in local|lab) ;; *) echo "--mode must be local or lab" >&2; exit 2 ;; esac
[ -z "$REMOTE_KEY" ] && [ -f "$HOME/.ssh/labvpn" ] && REMOTE_KEY="$HOME/.ssh/labvpn"

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"; cd "$ROOT" || exit 2
HERE="$(cd "$(dirname "$0")" && pwd)"
SUDO=""; [ "$(id -u)" -ne 0 ] && SUDO="sudo"
fail=0
pass() { echo "PASS $*"; }
bad()  { echo "FAIL $*"; fail=1; }
note() { echo "-- $*"; }

echo "== lab audit preflight (mode=$MODE iface=$IFACE) =="

# --- 1) Lab state: remote, independent of the local overlay -------------------
remote_state=unknown
if [ -n "$REMOTE_KEY" ] && [ -f "$REMOTE_KEY" ] && command -v ssh >/dev/null 2>&1; then
  out="$(timeout 25 ssh -i "$REMOTE_KEY" -o BatchMode=yes -o ConnectTimeout=10 \
        -o StrictHostKeyChecking=accept-new "$USER@$HOST" health 2>/dev/null || true)"
  if printf '%s' "$out" | grep -q 'RESULT: PASS'; then remote_state=up; else remote_state=down; fi
  note "remote endpoint health: $remote_state"
else
  note "no scoped endpoint key (pass --remote-key / set LABVPN_KEY); lab state inferred locally"
fi

# --- 2) Local access ----------------------------------------------------------
overlay_up=0; ip link show "$IFACE" >/dev/null 2>&1 && overlay_up=1
local_reach=0
check_local() {
  local ok=1
  if [ "$overlay_up" != 1 ]; then return 1; fi
  if command -v wg >/dev/null 2>&1; then
    local hs age
    hs="$(wg show "$IFACE" latest-handshakes 2>/dev/null | awk '{print $2}' | sort -n | tail -1 || true)"
    if [ -z "${hs:-}" ] || [ "$hs" = "0" ]; then return 1; fi
    age=$(( $(date +%s) - hs )); [ "$age" -gt 300 ] && return 1
  fi
  ping -c2 -W2 10.250.0.1 >/dev/null 2>&1 || ok=0
  # Either lab group counts; the lab moved hosts in 2026-10 (docs/LAB_VPN.md).
  local lab_ok=0
  if ping -c2 -W2 172.23.128.50 >/dev/null 2>&1 \
    && ping -c2 -W2 172.23.128.51 >/dev/null 2>&1 \
    && ping -c2 -W2 172.23.128.52 >/dev/null 2>&1 \
    && curl -fsS -m8 http://172.23.128.51:8722/health >/dev/null 2>&1; then
    lab_ok=1
  fi
  if ping -c2 -W2 192.168.222.222 >/dev/null 2>&1 \
    && ping -c2 -W2 192.168.222.201 >/dev/null 2>&1 \
    && ping -c2 -W2 192.168.222.202 >/dev/null 2>&1 \
    && ping -c2 -W2 192.168.222.203 >/dev/null 2>&1; then
    lab_ok=1
  fi
  [ "$lab_ok" -eq 1 ] || ok=0
  return $(( ok == 1 ? 0 : 1 ))
}
check_local && local_reach=1
note "local overlay reachable: $local_reach"

# --- 3) Classify, and only attempt locally when the lab is confirmed down -----
lab_state=""
if [ "$remote_state" = up ]; then
  if [ "$MODE" = lab ] || [ "$local_reach" = 1 ]; then
    lab_state=ready
  else
    lab_state=lab_up_local_down
  fi
elif [ "$remote_state" = down ]; then
  # Lab confirmed down via the endpoint path: now a LOCAL attempt is warranted
  # (the lab may still be reachable directly from here).
  note "lab confirmed down remotely; attempting local connection"
  if [ "$local_reach" != 1 ] && [ -n "$CONF" ] && [ -f "$CONF" ]; then
    bash "$HERE/lab-audit-connect.sh" "$CONF" "$IFACE" >/tmp/preflight-connect.log 2>&1 || true
    overlay_up=1; check_local && local_reach=1
  fi
  if [ "$local_reach" = 1 ]; then lab_state=ready_local_only; else lab_state=lab_down; fi
else
  # Unknown remote state: establish local access to confirm (a local attempt).
  if [ "$local_reach" != 1 ] && [ -n "$CONF" ] && [ -f "$CONF" ]; then
    bash "$HERE/lab-audit-connect.sh" "$CONF" "$IFACE" >/tmp/preflight-connect.log 2>&1 || true
    overlay_up=1; check_local && local_reach=1
  fi
  if [ "$local_reach" = 1 ]; then lab_state=ready_local_only; else lab_state=unknown; fi
fi
note "lab state: $lab_state"

# --- 4) Fail closed with tailored guidance -----------------------------------
case "$lab_state" in
  ready)
    pass "lab is up and access is verified (mode=$MODE)" ;;
  ready_local_only)
    pass "lab reachable from here (local only; endpoint health said '$remote_state')" ;;
  lab_up_local_down)
    bad "lab is UP, but LOCAL access is not set up — fix local access, do NOT rebuild the lab"
    echo "   -> onboard (GitHub 'Lab agent onboarding') then:"
    echo "      bash tools/lab-vpn/lab-audit-connect.sh <name>.conf" ;;
  lab_down)
    bad "lab is GENUINELY DOWN (endpoint health failed and it is not reachable locally)"
    echo "   -> do NOT dispatch to the lab; run work LOCALLY via:"
    echo "      bash tools/lab-vpn/lab-audit-run.sh --repo <repo> --command \"<cmd>\"" ;;
  unknown)
    bad "cannot confirm lab state (no remote key and no local access)"
    echo "   -> set up the connection: LABVPN_KEY=<labvpn key> bash tools/lab-vpn/lab-audit-bootstrap.sh"
    echo "      or run work LOCALLY via: bash tools/lab-vpn/lab-audit-run.sh --repo <repo> --command \"<cmd>\"" ;;
esac

# --- 5) Pack health ----------------------------------------------------------
if [ "$DO_PACK" -eq 1 ]; then
  if bash tools/lint_pack.sh >/tmp/preflight-lint.log 2>&1; then pass "pack lint"
  else bad "pack lint (tail below)"; tail -n 5 /tmp/preflight-lint.log; fi
fi

echo "== result =="
if [ "$fail" -eq 0 ]; then
  # Store the stamp OUTSIDE the pack tree (in .git) so it can never affect PACK_DIGEST.
  GITDIR="$(git rev-parse --git-dir 2>/dev/null || true)"
  STAMP="${GITDIR:-$HERE}/lab-audit-ready.json"
  cat > "$STAMP" <<EOF
{
  "ready": true,
  "lab_state": "$lab_state",
  "mode": "$MODE",
  "at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "iface": "$IFACE",
  "commit": "$(git rev-parse --short HEAD 2>/dev/null || echo unknown)",
  "endpoint": "$HOST:51900"
}
EOF
  echo "RESULT: PASS - safe to start audit/remediation work"
  echo "stamp: $STAMP"
  exit 0
fi
echo "RESULT: FAIL - do NOT start audit/remediation work"
exit 1
