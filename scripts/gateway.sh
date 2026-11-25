#!/bin/bash
set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

if [ -f /vagrant/.env ]; then
  set -a
  # shellcheck disable=SC1091
  source /vagrant/.env
  set +a
fi

echo "Provisioning gateway-vm..."
apt-get update
apt-get install -y curl python3 python3-pip python3-venv

if ! command -v pm2 >/dev/null 2>&1; then
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
  apt-get install -y nodejs
  npm install -g pm2
fi

mkdir -p /opt/venvs
python3 -m venv /opt/venvs/api-gateway-app
/opt/venvs/api-gateway-app/bin/pip install --upgrade pip
/opt/venvs/api-gateway-app/bin/pip install -r /vagrant/srcs/api-gateway-app/requirements.txt

pm2 delete api_gateway_app >/dev/null 2>&1 || true
pm2 start /vagrant/srcs/api-gateway-app/server.py \
  --name api_gateway_app \
  --interpreter /opt/venvs/api-gateway-app/bin/python3 \
  --cwd /vagrant/srcs/api-gateway-app
pm2 save
pm2 startup systemd -u root --hp /root >/dev/null 2>&1 || true

echo "gateway-vm provisioning completed."
