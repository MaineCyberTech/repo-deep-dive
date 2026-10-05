#!/usr/bin/env bash
# Overlay health check. Prints PASS/FAIL per check and RESULT: PASS|FAIL.
#   lab-audit-verify.sh [--role endpoint|lab|client]
# Env: IFACE ENDPOINT_IP LAB1_HOSTS LAB1_API LAB2_HOSTS LAB2_API
#      (LAB_HOSTS / LAB_API remain as lab #1 aliases)
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
# Multi-lab: lab #1 (legacy Proxmox, 172.23.128.0/20) and lab #2 (testnuc,
# 192.168.222.0/24 — the current host). The check passes when the endpoint AND
# at least one lab group (all its hosts, plus its API when set) is reachable,
# so a retired or powered-off lab cannot block the gate. Override with
# LAB1_*/LAB2_*.
LAB1_HOSTS="${LAB1_HOSTS:-${LAB_HOSTS:-172.23.128.50 172.23.128.51 172.23.128.52}}"
LAB1_API="${LAB1_API:-${LAB_API:-http://172.23.128.51:8722/health}}"
LAB2_HOSTS="${LAB2_HOSTS:-192.168.222.222 192.168.222.201 192.168.222.202 192.168.222.203}"
LAB2_API="${LAB2_API:-}"
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

# 3. endpoint reachability
if ping -c1 -W2 "$ENDPOINT_IP" >/dev/null 2>&1; then check "ping $ENDPOINT_IP" 0; else check "ping $ENDPOINT_IP" 1; fi

# 4. lab reachability — a group is up when every host answers and its API
#    (when configured) responds. At least one group must be up.
lab_group_ok() { # hosts api
  local ok=1 ip
  for ip in $1; do ping -c1 -W2 "$ip" >/dev/null 2>&1 || ok=0; done
  if [ -n "${2:-}" ]; then curl -fsS -m6 "$2" >/dev/null 2>&1 || ok=0; fi
  [ "$ok" -eq 1 ]
}
lab1_ok=0; lab_group_ok "$LAB1_HOSTS" "$LAB1_API" && lab1_ok=1
lab2_ok=0; lab_group_ok "$LAB2_HOSTS" "$LAB2_API" && lab2_ok=1
if [ "$lab1_ok" -eq 1 ]; then
  echo "PASS lab #1 reachable ($LAB1_HOSTS${LAB1_API:+ + api})"
else
  echo "INFO lab #1 unreachable ($LAB1_HOSTS${LAB1_API:+ + api})"
fi
if [ "$lab2_ok" -eq 1 ]; then
  echo "PASS lab #2 reachable ($LAB2_HOSTS${LAB2_API:+ + api})"
else
  echo "INFO lab #2 unreachable ($LAB2_HOSTS${LAB2_API:+ + api})"
fi
check "at least one lab reachable" $(( (lab1_ok + lab2_ok) > 0 ? 0 : 1 ))

if [ "$fail" -eq 0 ]; then
  echo "RESULT: PASS"
  exit 0
else
  echo "RESULT: FAIL"
  exit 1
fi
