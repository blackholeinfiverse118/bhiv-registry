#!/bin/bash
# BHIV Registry -- Database Backup Script
#
# Creates a timestamped pg_dump of the registry database.
# Run manually or via cron for scheduled backups.
#
# Usage: ./backup_db.sh
# Output: backups/bhiv_registry_YYYYMMDD_HHMMSS.sql

set -e

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/bhiv_registry_${TIMESTAMP}.sql"

mkdir -p "$BACKUP_DIR"

echo "Creating backup: $BACKUP_FILE"

docker compose exec -T db pg_dump -U bhiv -d bhiv_registry > "$BACKUP_FILE"

echo "Backup complete: $BACKUP_FILE"

# Keep only the last 7 backups
cd "$BACKUP_DIR"
ls -t bhiv_registry_*.sql | tail -n +8 | xargs -r rm

echo "Old backups cleaned. Retaining last 7."