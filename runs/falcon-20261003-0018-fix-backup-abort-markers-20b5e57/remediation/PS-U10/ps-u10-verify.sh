#!/usr/bin/env bash
# PS-U10 targeted verification - OBS-P1-001/002/003 observability guards.
# Positive run + negative controls; raw output and exit codes only, no fabrication.
set -u
cd /srv/work/falcon

echo "# PS-U10 targeted verification - alert-rule linter + per-path relay guard"
echo "commit: $(git rev-parse HEAD)"
echo "branch: $(git rev-parse --abbrev-ref HEAD)"
echo

echo "## 1. alert_rule_lint_test.sh (positive)"
bash automation/validation/tests/alert_rule_lint_test.sh
echo "LINT_EXIT=$?"
echo

echo "## 2. remediation_guards_test.sh (positive)"
bash automation/validation/tests/remediation_guards_test.sh
echo "GUARDS_EXIT=$?"
echo

echo "## 3. negative control: planted duplicate rule UID must be rejected"
cp bootstrap/90-alerting.sh /tmp/90-alerting.psu10.bak
printf '\nwrite_rule "falcon-relay-path-failures" \\\n  "Duplicated uid" \x27falcon_some_metric > 0\x27 "5m" "warning" \\\n  "planted duplicate"\n' >> bootstrap/90-alerting.sh
bash automation/validation/tests/alert_rule_lint_test.sh
echo "NEG_DUP_LINT_EXIT=$?"
cp /tmp/90-alerting.psu10.bak bootstrap/90-alerting.sh
echo

echo "## 4. negative control: missing per-path relay rule must be rejected"
grep -v 'falcon-relay-path-failures' /tmp/90-alerting.psu10.bak > bootstrap/90-alerting.sh
bash automation/validation/tests/remediation_guards_test.sh
echo "NEG_GUARD_EXIT=$?"
cp /tmp/90-alerting.psu10.bak bootstrap/90-alerting.sh
rm -f /tmp/90-alerting.psu10.bak
echo

echo "## 5. restore check (must be clean against the committed branch)"
git status --short -- bootstrap/90-alerting.sh automation/validation/tests/remediation_guards_test.sh automation/validation/tests/alert_rule_lint_test.sh
echo "restore_clean_exit=$?"
echo

echo "## 6. Prometheus rule-file check (Grafana-provisioned rules; promtool N/A)"
if [ -d config/prometheus/rules ]; then
  if command -v promtool >/dev/null 2>&1; then
    for f in config/prometheus/rules/*.yml; do promtool check rules "$f"; echo "promtool_$f=$?"; done
  else
    echo "promtool: not installed"
  fi
else
  echo "no config/prometheus/rules directory; alert rules are Grafana-provisioned via API (no promtool artifact)"
fi
echo
echo "TARGETED_DONE"
