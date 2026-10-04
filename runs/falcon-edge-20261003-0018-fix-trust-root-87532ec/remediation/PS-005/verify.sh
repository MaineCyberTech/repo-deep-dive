#!/usr/bin/env bash
# PS-005 verification on edge-builder (falcon-edge).
cd "$HOME/ps005-falcon-edge" || exit 2
echo "PWD=$(pwd)"
echo

echo "## python3 -m pytest -q tests/phase2"
python3 -m pytest -q tests/phase2
echo "EXIT=$?"
echo

echo "## python3 -m pytest -q tests/phase10/test_ci_doc_drift.py"
python3 -m pytest -q tests/phase10/test_ci_doc_drift.py
echo "EXIT=$?"
echo

echo "## bash ci/validate.sh"
bash ci/validate.sh
echo "EXIT=$?"
echo

echo "## gitleaks detect --no-git --redact --source . -v"
gitleaks detect --no-git --redact --source . -v
echo "EXIT=$?"
