#!/usr/bin/env bash
# Seamless lab access VIA GitHub Actions.
#
# GitHub secrets (the scoped labvpn key, the lab API token) are WRITE-ONLY: an external
# agent/server cannot read them back with `gh`. So instead of copying secrets around, this
# helper routes the work through GitHub Actions, which already holds them:
#
#   onboard <name>   dispatch lab-agent-onboard.yml, download the client config, connect.
#                    The generated private key stays on THIS machine (a local keypair is
#                    sent as a public key), so no lab secret is handled locally.
#   run --repo <r> --command "<cmd>"
#                    dispatch lab-tests.yml to run the command on the lab's self-hosted
#                    runner (secrets injected by GitHub), and fall back to LOCAL execution
#                    if the lab/runner is unavailable.
#   status           show recent lab workflow runs.
#
# Auth: `gh auth status` must be logged in (repo scope). Override the pack repo with GH_REPO.
# Env: LAB_RUNNER (default edge-builder), GH_LAB_TIMEOUT (default 1800), IFACE.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PACK_REPO="${GH_REPO:-MaineCyberTech/repo-deep-dive}"
WF_ONBOARD="lab-agent-onboard.yml"
WF_LABTESTS="lab-tests.yml"
RUNNER="${LAB_RUNNER:-edge-builder}"

need_gh() {
  command -v gh >/dev/null 2>&1 || { echo "[gh-lab] gh CLI not found" >&2; return 1; }
  gh auth status >/dev/null 2>&1 || { echo "[gh-lab] not logged in (run: gh auth login)" >&2; return 1; }
}
latest_run() {
  gh run list -R "$PACK_REPO" --workflow="$1" --limit 1 --json databaseId --jq '.[0].databaseId' 2>/dev/null
}
wait_run() {
  local id="$1" to="${2:-1800}"
  [ -n "$id" ] && [ "$id" != "null" ] || return 1
  if command -v timeout >/dev/null 2>&1; then
    timeout "$to" gh run watch "$id" -R "$PACK_REPO" --exit-status --interval 10 >/dev/null 2>&1
  else
    gh run watch "$id" -R "$PACK_REPO" --exit-status --interval 10 >/dev/null 2>&1
  fi
}

onboard() {
  local name="${1:?usage: lab-audit-gh.sh onboard <name>}"
  need_gh || return 1
  command -v wg >/dev/null 2>&1 || { echo "[gh-lab] wireguard-tools required locally for keygen" >&2; return 1; }
  local tmp; tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' RETURN
  wg genkey > "$tmp/priv"; wg pubkey < "$tmp/priv" > "$tmp/pub"
  echo "[gh-lab] dispatching onboarding for '$name'"
  gh workflow run "$WF_ONBOARD" -R "$PACK_REPO" -f agent_name="$name" \
     -f agent_public_key="$(cat "$tmp/pub")" >/dev/null || return 1
  sleep 6
  local id; id="$(latest_run "$WF_ONBOARD")"
  echo "[gh-lab] waiting for run $id"
  wait_run "$id" "${GH_LAB_TIMEOUT:-1800}" || { echo "[gh-lab] onboarding failed/timed out (run $id)"; return 1; }
  gh run download "$id" -R "$PACK_REPO" -n "lab-audit-$name" -D "$tmp/art" >/dev/null \
    || { echo "[gh-lab] could not download artifact"; return 1; }
  local art conf
  art="$(find "$tmp/art" -name '*.conf' | head -1)"
  [ -n "$art" ] || { echo "[gh-lab] no config in artifact"; return 1; }
  conf="$tmp/$name.conf"
  sed "s|^PrivateKey = .*|PrivateKey = $(cat "$tmp/priv")|" "$art" > "$conf"
  chmod 600 "$conf"
  echo "[gh-lab] bringing up the tunnel and verifying"
  bash "$HERE/lab-audit-connect.sh" "$conf" "${IFACE:-lab-audit}"
}

run_cmd() {
  local repo="" cmd="" ref="" cwd=""
  while [ $# -gt 0 ]; do
    case "$1" in
      --repo) repo="${2:?}"; shift 2 ;;
      --command) cmd="${2:?}"; shift 2 ;;
      --ref) ref="${2:-}"; shift 2 ;;
      --cwd) cwd="${2:?}"; shift 2 ;;
      *) echo "unknown argument: $1" >&2; return 2 ;;
    esac
  done
  [ -n "$cmd" ] || { echo "usage: run --repo <repo> --command \"<cmd>\" [--ref <ref>]" >&2; return 2; }
  if need_gh && [ -n "$repo" ]; then
    echo "[gh-lab] dispatching lab-tests (runner=$RUNNER) for $repo"
    gh workflow run "$WF_LABTESTS" -R "$PACK_REPO" -f repo="$repo" -f ref="$ref" \
       -f command="$cmd" -f runner="$RUNNER" >/dev/null 2>&1
    sleep 6
    local id; id="$(latest_run "$WF_LABTESTS")"
    echo "[gh-lab] run $id"
    if wait_run "$id" "${GH_LAB_TIMEOUT:-1800}"; then
      gh run view "$id" -R "$PACK_REPO" --log 2>/dev/null | tail -n 20
      return 0
    fi
    echo "[gh-lab] lab dispatch unavailable (offline runner / failure); falling back to LOCAL"
  fi
  bash "$HERE/lab-audit-run.sh" --no-autosetup ${cwd:+--cwd "$cwd"} --command "$cmd"
}

case "${1:-}" in
  onboard) shift; onboard "$@" ;;
  run) shift; run_cmd "$@" ;;
  status)
    need_gh || exit 1
    gh run list -R "$PACK_REPO" --limit 8 \
      --json displayTitle,name,status,conclusion,createdAt \
      --template '{{range .}}{{.createdAt}}  {{.name}}  {{.status}}/{{.conclusion}}  {{.displayTitle}}{{"\n"}}{{end}}' ;;
  *) echo "usage: lab-audit-gh.sh onboard <name> | run --repo <r> --command \"<cmd>\" [--runner <r>] | status" >&2; exit 2 ;;
esac
