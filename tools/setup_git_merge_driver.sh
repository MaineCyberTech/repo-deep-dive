#!/usr/bin/env bash
# setup_git_merge_driver.sh — enable the PACK_DIGEST.txt "ours" merge driver in
# this clone. Run once after cloning:
#
#   tools/setup_git_merge_driver.sh
#
# `merge=ours` is declared in .gitattributes, but `ours` is not a built-in Git
# merge driver — Git only honours it when `merge.ours.driver` is configured.
# Enabling it lets a merge keep the current branch's PACK_DIGEST.txt instead of
# stopping on a conflict; the push-to-main self-heal workflow then regenerates
# the authoritative digest. The setting is per-clone (Git config is not tracked).
set -euo pipefail
cd "$(dirname "$0")/.."

git config merge.ours.name "repo-deep-dive: keep one side for generated PACK_DIGEST.txt"
git config merge.ours.driver true
echo "configured merge.ours.driver=true (PACK_DIGEST.txt will merge to 'ours')"
