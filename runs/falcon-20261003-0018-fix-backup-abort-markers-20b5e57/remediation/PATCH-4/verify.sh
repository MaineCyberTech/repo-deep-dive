#!/usr/bin/env bash
# PATCH-4 verification (run under WSL). Records nothing here; caller tees to verify.log.
set -u
cd /mnt/c/temp/falcon || exit 1
echo "=== git HEAD ==="; git rev-parse HEAD
echo "=== bash -n changed scripts ==="
bash -n automation/validation/heartbeat.sh && echo "heartbeat.sh syntax OK"
bash -n bootstrap/90-alerting.sh && echo "90-alerting.sh syntax OK"
bash -n automation/validation/tests/heartbeat_independence_test.sh && echo "test syntax OK"
echo "=== heartbeat independence test ==="
bash automation/validation/tests/heartbeat_independence_test.sh; echo "heartbeat_test_exit=$?"
echo "=== ci/validate.py --only parsers,shell-syntax,shell-tests ==="
FALCON_EVIDENCE_OPTIONAL=1 python3 ci/validate.py --only parsers,shell-syntax,shell-tests
echo "ci_targeted_exit=$?"
