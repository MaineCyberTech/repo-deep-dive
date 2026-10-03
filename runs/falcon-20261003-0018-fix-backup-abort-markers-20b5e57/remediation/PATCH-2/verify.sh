#!/usr/bin/env bash
# PATCH-2 (ARCH-P2-005) verification. Run on the ci-runner in /srv/work/falcon at the
# patched commit. Captures every command's raw output and exit code.
set -u
cd /srv/work/falcon

echo "== PATCH-2 verification (ARCH-P2-005) =="
echo "host:   ci-runner"
echo "branch: $(git rev-parse --abbrev-ref HEAD)"
echo "head:   $(git rev-parse --short HEAD)"
echo "dirty:  $(git status --porcelain | wc -l) path(s)"
echo

echo '$ FALCON_EVIDENCE_OPTIONAL=1 python3 ci/validate.py'
FALCON_EVIDENCE_OPTIONAL=1 python3 ci/validate.py
echo "VALIDATE_EXIT=$?"
echo

echo '$ bash automation/validation/tests/abort_marker_test.sh'
bash automation/validation/tests/abort_marker_test.sh
echo "ABORT_TEST_EXIT=$?"
echo

echo '$ bash automation/validation/tests/offsite_backup_reuse_test.sh'
bash automation/validation/tests/offsite_backup_reuse_test.sh
echo "OFFSITE_REUSE_EXIT=$?"
echo

echo '$ bash automation/validation/tests/offsite_upload_delta_test.sh'
bash automation/validation/tests/offsite_upload_delta_test.sh
echo "OFFSITE_DELTA_EXIT=$?"
echo

echo '$ bash automation/validation/tests/wazuh_indexer_backup_test.sh'
bash automation/validation/tests/wazuh_indexer_backup_test.sh
echo "WAZUH_TEST_EXIT=$?"
echo

echo '$ shellcheck --severity=warning automation/validation/r2_cold_copy.sh automation/validation/wazuh_indexer_backup.sh automation/validation/tests/abort_marker_test.sh automation/validation/tests/wazuh_indexer_backup_test.sh'
shellcheck --severity=warning automation/validation/r2_cold_copy.sh automation/validation/wazuh_indexer_backup.sh automation/validation/tests/abort_marker_test.sh automation/validation/tests/wazuh_indexer_backup_test.sh
echo "SHELLCHECK_EXIT=$?"
echo

echo '$ gitleaks detect --no-git --redact --source .'
gitleaks detect --no-git --redact --source .
echo "GITLEAKS_EXIT=$?"
