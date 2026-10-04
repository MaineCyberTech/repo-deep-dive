#!/usr/bin/env bash
set -euo pipefail
RUN=/mnt/c/temp/proxmox-vm/audits/runs/repo-deep-dive/20261003-0018-main-7bac320
cd /mnt/c/temp/repo-deep-dive
python3 tools/remediation_status.py "$RUN" \
  --patch-set PS-011 \
  --state open \
  --commit fd9cf670164dba78f5a9fee8635da9c7d95f5725 \
  --pr https://github.com/MaineCyberTech/repo-deep-dive/pull/10
python3 tools/normalize_register.py "$RUN"
