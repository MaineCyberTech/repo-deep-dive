#!/usr/bin/env bash
# bootstrap-runner.sh — register and run ONE ephemeral GitHub Actions runner.
#
# Scaffold. For a single just-in-time runner (CI job, demo, one-shot re-provision).
# For elastic scale use Actions Runner Controller (ARC): see arc-values.yaml and
# README.md in this directory.
#
# The registration token is short-lived (~1h) and is supplied via the
# environment — never written to disk:
#
#   RUNNER_TOKEN=<registration-token> ./bootstrap-runner.sh
#
# Environment:
#   RUNNER_TOKEN     required  org/repo runner registration token
#   RUNNER_SCOPE     org|repo  (default: org)
#   RUNNER_ORG       default: MaineCyberTech
#   RUNNER_REPO      required for RUNNER_SCOPE=repo
#   RUNNER_NAME      default: "<hostname>-ephemeral"
#   RUNNER_LABELS    default: "self-hosted,linux,x64,lab,ephemeral"
#   RUNNER_VERSION   default: 2.319.1
#   RUNNER_DIR       default: /opt/actions-runner
#
# Note: an *ephemeral* runner deregisters itself after a single job. A systemd
# service therefore cannot silently re-register with an expired token; use a
# fresh token/JIT config per boot, or ARC (recommended).
set -euo pipefail

RUNNER_SCOPE="${RUNNER_SCOPE:-org}"
RUNNER_ORG="${RUNNER_ORG:-MaineCyberTech}"
RUNNER_REPO="${RUNNER_REPO:-}"
RUNNER_NAME="${RUNNER_NAME:-$(hostname)-ephemeral}"
RUNNER_LABELS="${RUNNER_LABELS:-self-hosted,linux,x64,lab,ephemeral}"
RUNNER_VERSION="${RUNNER_VERSION:-2.319.1}"
RUNNER_DIR="${RUNNER_DIR:-/opt/actions-runner}"
RUNNER_TOKEN="${RUNNER_TOKEN:-}"

log() { printf '[bootstrap-runner] %s\n' "$*"; }
die() { printf '[bootstrap-runner] error: %s\n' "$*" >&2; exit 1; }

[ -n "$RUNNER_TOKEN" ] || die "RUNNER_TOKEN is required (pass it via the environment; do not commit it)"
command -v curl >/dev/null 2>&1 || die "curl is required"
command -v tar  >/dev/null 2>&1 || die "tar is required"

case "$(uname -m)" in
  x86_64) RUNNER_ARCH=x64 ;;
  aarch64|arm64) RUNNER_ARCH=arm64 ;;
  *) die "unsupported architecture: $(uname -m)" ;;
esac

case "$RUNNER_SCOPE" in
  org)  RUNNER_URL="https://github.com/${RUNNER_ORG}" ;;
  repo) [ -n "$RUNNER_REPO" ] || die "RUNNER_REPO is required when RUNNER_SCOPE=repo"
        RUNNER_URL="https://github.com/${RUNNER_ORG}/${RUNNER_REPO}" ;;
  *) die "RUNNER_SCOPE must be org or repo (got: $RUNNER_SCOPE)" ;;
esac

if [ "$(id -u)" -ne 0 ]; then
  die "run as root (or via sudo) to install the runner under ${RUNNER_DIR}"
fi

mkdir -p "$RUNNER_DIR"

if [ ! -x "$RUNNER_DIR/config.sh" ]; then
  tarball="/tmp/actions-runner-${RUNNER_VERSION}-${RUNNER_ARCH}.tar.gz"
  url="https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-${RUNNER_ARCH}-${RUNNER_VERSION}.tar.gz"
  log "downloading runner v${RUNNER_VERSION} (${RUNNER_ARCH})"
  curl -fsSL "$url" -o "$tarball"
  tar -xzf "$tarball" -C "$RUNNER_DIR"
  rm -f "$tarball"
fi

log "registering ephemeral runner '${RUNNER_NAME}' against ${RUNNER_URL}"
(
  cd "$RUNNER_DIR"
  ./config.sh \
    --unattended \
    --ephemeral \
    --replace \
    --name "$RUNNER_NAME" \
    --labels "$RUNNER_LABELS" \
    --work "_work" \
    --url "$RUNNER_URL" \
    --token "$RUNNER_TOKEN"
)

log "starting runner (it will exit and de-register after a single job)"
exec "$RUNNER_DIR/run.sh"
