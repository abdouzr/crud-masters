#!/bin/bash
set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

if [ -f /vagrant/.env ]; then
  set -a
  # shellcheck disable=SC1091
  source /vagrant/.env
  set +a
fi

echo "Provisioning inventory-vm..."
apt-get update
apt-get install -y curl python3 python3-pip python3-venv postgresql postgresql-contrib

systemctl enable postgresql
systemctl start postgresql

cd /tmp
if [ "${INVENTORY_DB_USER}" = "postgres" ]; then
  sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD '${INVENTORY_DB_PASSWORD}';"
else
  if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='${INVENTORY_DB_USER}'" | grep -q 1; then
    sudo -u postgres psql -c "CREATE USER \"${INVENTORY_DB_USER}\" WITH PASSWORD '${INVENTORY_DB_PASSWORD}';"
  else
    sudo -u postgres psql -c "ALTER USER \"${INVENTORY_DB_USER}\" WITH PASSWORD '${INVENTORY_DB_PASSWORD}';"
  fi
fi

if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='${INVENTORY_DB_NAME}'" | grep -q 1; then
  sudo -u postgres psql -c "CREATE DATABASE \"${INVENTORY_DB_NAME}\" OWNER \"${INVENTORY_DB_USER}\";"
fi

if ! command -v pm2 >/dev/null 2>&1; then
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
  apt-get install -y nodejs
  npm install -g pm2
fi

mkdir -p /opt/venvs
python3 -m venv /opt/venvs/inventory-app
/opt/venvs/inventory-app/bin/pip install --upgrade pip
/opt/venvs/inventory-app/bin/pip install -r /vagrant/srcs/inventory-app/requirements.txt

pm2 delete inventory_app >/dev/null 2>&1 || true
pm2 start /vagrant/srcs/inventory-app/server.py \
  --name inventory_app \
  --interpreter /opt/venvs/inventory-app/bin/python3 \
  --cwd /vagrant/srcs/inventory-app
pm2 save
pm2 startup systemd -u root --hp /root >/dev/null 2>&1 || true

echo "inventory-vm provisioning completed."
