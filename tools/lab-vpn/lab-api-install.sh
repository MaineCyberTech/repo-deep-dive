#!/bin/bash
# Install/refresh the lab job API inside a lab guest. Run as root in the guest.
# Expects the server already copied to /root/lab_api_server.py (see deploy-lab-api.sh).
set -e

install -d /etc/lab-api /var/lib/lab-repos
install -m 0755 /root/lab_api_server.py /usr/local/bin/lab_api_server.py

if [ ! -s /etc/lab-api/env ]; then
  TOK="$(openssl rand -hex 32)"
  cat > /etc/lab-api/env <<EOF
LAB_API_TOKEN=$TOK
LAB_API_ROOT=/var/lib/lab-repos
LAB_API_BIND=0.0.0.0
LAB_API_PORT=8722
EOF
  chmod 600 /etc/lab-api/env
fi

cat > /etc/systemd/system/lab-api.service <<'UNIT'
[Unit]
Description=Lab job API (repo-deep-dive)
After=network-online.target
Wants=network-online.target

[Service]
EnvironmentFile=/etc/lab-api/env
ExecStart=/usr/bin/python3 /usr/local/bin/lab_api_server.py
Restart=on-failure
RestartSec=2
User=root

[Install]
WantedBy=multi-user.target
UNIT

systemctl daemon-reload
systemctl enable lab-api >/dev/null 2>&1 || true
systemctl restart lab-api
sleep 1
echo -n "active: "; systemctl is-active lab-api
echo "TOKEN=$(grep '^LAB_API_TOKEN' /etc/lab-api/env | cut -d= -f2)"
echo -n "health: "; curl -fsS http://127.0.0.1:8722/health; echo
echo -n "ip: "; hostname -I
