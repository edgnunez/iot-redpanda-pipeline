#!/usr/bin/env bash
# Creates the pipeline's service accounts and their least-privilege ACLs.
# Safe to re-run: existing users get their password synced from .env,
# and re-creating an existing ACL has no effect.
# Connection settings (RPK_BROKERS, RPK_ADMIN_HOSTS, RPK_USER, RPK_PASS)
# come from environment variables set in docker-compose.yml
set -euo pipefail

TOPIC="classroom-temperatures"

upsert_user() {
  local name="$1" password="$2"
  local existing
  existing="$(rpk security user list)"
  if awk 'NR>1 {print $1}' <<< "$existing" | grep -qx "$name"; then
    echo "User $name exists; syncing password from .env"
    rpk security user update "$name" --new-password "$password" --mechanism SCRAM-SHA-256
  else
    echo "Creating user $name"
    rpk security user create "$name" -p "$password" --mechanism SCRAM-SHA-256
  fi
}

upsert_user sensor	"$SENSOR_PASSWORD"
upsert_user dashboard	"$DASHBOARD_PASSWORD"
upsert_user db-writer	"$DB_WRITER_PASSWORD"

# sensor: produce only
rpk security acl create --allow-principal User:sensor \
  --operation write,describe --topic "$TOPIC"

# dashboard: consume only, in its own consumer group
rpk security acl create --allow-principal User:dashboard \
  --operation read,describe --topic "$TOPIC"
rpk security acl create --allow-principal User:dashboard \
  --operation read --group iot-dashboard-group

# db-writer: consume only, in its own consumer group
rpk security acl create --allow-principal User:db-writer \
  --operation read,describe --topic "$TOPIC"
rpk security acl create --allow-principal User:db-writer \
  --operation read --group db-writer-group

echo "Security setup complete"