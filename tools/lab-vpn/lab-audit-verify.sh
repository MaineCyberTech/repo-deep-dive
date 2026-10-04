#!/usr/bin/env bash
# Overlay health check. Prints PASS/FAIL per check and RESULT: PASS|FAIL.
#   lab-audit-verify.sh [--role endpoint|lab|client]
# Env: IFACE ENDPOINT_IP LAB_HOSTS LAB_API
set -uo pipefail

ROLE=endpoint
while [ $# -gt 0 ]; do
  case "$1" in
    --role)   ROLE="${2:-}"; shift 2 ;;
    --role=*) ROLE="${1#*=}"; shift ;;
    *)        echo "usage: verify.sh [--role endpoint|lab|client]" >&2; exit 2 ;;
  esac
done
case "$ROLE" in endpoint|lab|client) ;; *) echo "invalid role '$ROLE'" >&2; exit 2 ;; esac

IFACE="${IFACE:-wgaudit0}"
ENDPOINT_IP="${ENDPOINT_IP:-10.250.0.1}"
LAB_HOSTS="${LAB_HOSTS:-172.23.128.50 172.23.128.51 172.23.128.52}"
LAB_API="${LAB_API:-http://172.23.128.51:8722/health}"
STALE=300
fail=0

check() { # label rc
  if [ "$2" -eq 0 ]; then echo "PASS $1"; else echo "FAIL $1"; fail=1; fi
}

echo "== lab-audit verify (role=$ROLE iface=$IFACE) =="

# 1. interface up
if ip link show "$IFACE" >/dev/null 2>&1 && wg show "$IFACE" >/dev/null 2>&1; then
  check "interface $IFACE up" 0
else
  check "interface $IFACE up" 1
fi

# 2. newest handshake fresh within STALE
now="$(date -u +%s)"
newest="$(wg show "$IFACE" dump 2>/dev/null | awk 'NR>1 && $5+0>m {m=$5+0} END{print m+0}')"
if [ -z "${newest:-}" ] || [ "${newest:-0}" = "0" ]; then
  check "newest handshake present" 1
  echo "  (no handshake recorded)"
else
  age=$(( now - newest ))
  [ "$age" -lt 0 ] && age=0
  if [ "$age" -le "$STALE" ]; then
    check "newest handshake fresh (${age}s <= ${STALE}s)" 0
  else
    check "newest handshake fresh (${age}s > ${STALE}s stale)" 1
  fi
fi

# 3. reachability of endpoint + lab hosts
for ip in $ENDPOINT_IP $LAB_HOSTS; do
  if ping -c1 -W2 "$ip" >/dev/null 2>&1; then check "ping $ip" 0; else check "ping $ip" 1; fi
done

# 4. lab management API
if curl -fsS -m6 "$LAB_API" >/dev/null 2>&1; then check "curl $LAB_API" 0; else check "curl $LAB_API" 1; fi

if [ "$fail" -eq 0 ]; then
  echo "RESULT: PASS"
  exit 0
else
  echo "RESULT: FAIL"
  exit 1
fi
