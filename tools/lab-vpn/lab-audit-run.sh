#!/usr/bin/env bash
# Run a repo command on the LAB when it is reachable, otherwise LOCALLY.
#
# This is the graceful-degradation entry point: on a new agent/server it will try to set
# the lab connection up (via lab-audit-bootstrap.sh) and dispatch there; if the lab cannot
# be used it runs the same command locally, so work still gets done.
#
#   lab-audit-run.sh --repo <name> --command "<cmd>" [--cwd <dir>] [--no-autosetup]
#
# Env: LAB_API_TOKEN (required for the lab path), LAB_API_URL, LABVPN_KEY,
#      LAB_ENDPOINT_HOST, LAB_ENDPOINT_USER, IFACE
# Exit code mirrors the command (lab or local).
set -uo pipefail

REPO=""; CMD=""; CWD=""; AUTOSETUP=1
while [ $# -gt 0 ]; do
  case "$1" in
    --repo) REPO="${2:?}"; shift 2 ;;
    --command) CMD="${2:?}"; shift 2 ;;
    --cwd) CWD="${2:?}"; shift 2 ;;
    --no-autosetup) AUTOSETUP=0; shift ;;
    -h|--help) grep -E '^#( |$)' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done
[ -n "$CMD" ] || { echo "usage: lab-audit-run.sh --repo <name> --command \"<cmd>\" [--cwd <dir>]" >&2; exit 2; }

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
HERE="$(cd "$(dirname "$0")" && pwd)"
KEY="${LABVPN_KEY:-$HOME/.ssh/labvpn}"
# Lab API base: explicit LAB_API_URL wins, then lab #1, then lab #2 (testnuc,
# the current host since the 2026-10 lab move).
URL="${LAB_API_URL:-}"
if [ -z "$URL" ]; then
  for candidate in http://172.23.128.51:8722 http://192.168.222.201:8722; do
    if curl -fsS -m5 "$candidate/health" >/dev/null 2>&1; then URL="$candidate"; break; fi
  done
  URL="${URL:-http://172.23.128.51:8722}"
fi
TOKEN="${LAB_API_TOKEN:-}"

lab_ok() { bash "$HERE/lab-audit-preflight.sh" --mode local --no-pack >/tmp/lr-pre.log 2>&1; }

mode=local
if [ -n "$TOKEN" ]; then
  if ! lab_ok && [ "$AUTOSETUP" = 1 ] && [ -f "$KEY" ]; then
    echo "[lab-audit-run] lab not reachable; attempting to set up the connection"
    bash "$HERE/lab-audit-bootstrap.sh" >/tmp/lr-bootstrap.log 2>&1 || true
  fi
  lab_ok && mode=lab
fi

if [ "$mode" = lab ]; then
  echo "[lab-audit-run] MODE=lab repo=$REPO"
  python3 "$ROOT/tools/lab_runner.py" --url "$URL" --token "$TOKEN" \
    ${REPO:+--repo "$REPO"} --command "$CMD"
  rc=$?
  if [ "$rc" -ge 2 ]; then
    echo "[lab-audit-run] lab dispatch failed (rc=$rc); falling back to LOCAL"
  else
    exit "$rc"   # 0/1 = real remote result
  fi
fi

cd "${CWD:-$ROOT}" || exit 2
echo "[lab-audit-run] MODE=local (lab unavailable) cwd=$PWD"
bash -o pipefail -c "$CMD"
