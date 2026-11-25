#!/bin/bash
set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

if [ -f /vagrant/.env ]; then
  set -a
  # shellcheck disable=SC1091
  source /vagrant/.env
  set +a
fi

echo "Provisioning billing-vm..."
apt-get update
apt-get install -y curl python3 python3-pip python3-venv postgresql postgresql-contrib rabbitmq-server

systemctl enable postgresql
systemctl start postgresql

cd /tmp
if [ "${BILLING_DB_USER}" = "postgres" ]; then
  sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD '${BILLING_DB_PASSWORD}';"
else
  if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='${BILLING_DB_USER}'" | grep -q 1; then
    sudo -u postgres psql -c "CREATE USER \"${BILLING_DB_USER}\" WITH PASSWORD '${BILLING_DB_PASSWORD}';"
  else
    sudo -u postgres psql -c "ALTER USER \"${BILLING_DB_USER}\" WITH PASSWORD '${BILLING_DB_PASSWORD}';"
  fi
fi

if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='${BILLING_DB_NAME}'" | grep -q 1; then
  sudo -u postgres psql -c "CREATE DATABASE \"${BILLING_DB_NAME}\" OWNER \"${BILLING_DB_USER}\";"
fi

systemctl enable rabbitmq-server
systemctl start rabbitmq-server
rabbitmq-plugins enable rabbitmq_management >/dev/null 2>&1 || true

if rabbitmqctl list_users | awk '{print $1}' | grep -qx "${RABBITMQ_USER}"; then
  rabbitmqctl change_password "${RABBITMQ_USER}" "${RABBITMQ_PASSWORD}"
else
  rabbitmqctl add_user "${RABBITMQ_USER}" "${RABBITMQ_PASSWORD}"
fi
rabbitmqctl set_user_tags "${RABBITMQ_USER}" administrator
rabbitmqctl set_permissions -p "${RABBITMQ_VHOST}" "${RABBITMQ_USER}" ".*" ".*" ".*"

if ! command -v pm2 >/dev/null 2>&1; then
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
  apt-get install -y nodejs
  npm install -g pm2
fi

mkdir -p /opt/venvs
python3 -m venv /opt/venvs/billing-app
/opt/venvs/billing-app/bin/pip install --upgrade pip
/opt/venvs/billing-app/bin/pip install -r /vagrant/srcs/billing-app/requirements.txt

pm2 delete billing_app >/dev/null 2>&1 || true
pm2 start /vagrant/srcs/billing-app/server.py \
  --name billing_app \
  --interpreter /opt/venvs/billing-app/bin/python3 \
  --cwd /vagrant/srcs/billing-app
pm2 save
pm2 startup systemd -u root --hp /root >/dev/null 2>&1 || true

echo "billing-vm provisioning completed."
