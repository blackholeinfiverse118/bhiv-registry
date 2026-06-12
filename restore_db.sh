#!/bin/bash
# BHIV Registry -- Database Restore Script
#
# Restores the registry database from a backup file.
#
# Usage: ./restore_db.sh backups/bhiv_registry_YYYYMMDD_HHMMSS.sql

set -e

if [ -z "$1" ]; then
  echo "Usage: ./restore_db.sh <backup_file>"
  exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
  echo "Backup file not found: $BACKUP_FILE"
  exit 1
fi

echo "Restoring from: $BACKUP_FILE"
echo "WARNING: This will overwrite the current database."
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  exit 1
fi

cat "$BACKUP_FILE" | docker compose exec -T db psql -U bhiv -d bhiv_registry

echo "Restore complete."