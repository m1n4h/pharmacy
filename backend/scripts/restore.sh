#!/usr/bin/env bash
# ============================================
# Restore database from a backup file
# Usage: ./scripts/restore.sh <backup_file.sql>
# WARNING: This DROPS and recreates all data in the database!
# ============================================
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: ./scripts/restore.sh <backup_file.sql>"
  exit 1
fi

BACKUP_FILE="$1"
if [ ! -f "$BACKUP_FILE" ]; then
  echo "ERROR: Faili la backup halipo: $BACKUP_FILE"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"

# Load DATABASE_URL from .env if set
if [ -f "$BACKEND_DIR/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  source "$BACKEND_DIR/.env"
  set +a
fi

if [ -z "${DATABASE_URL:-}" ]; then
  echo "ERROR: DATABASE_URL haijapatikana. Weka kwenye .env."
  exit 1
fi

echo "WARNING: Hii itaREPLACE data zote zilizopo kwenye database!"
read -r -p "Endelea? (andika 'restore' kuthibitisha): " CONFIRM
if [ "$CONFIRM" != "restore" ]; then
  echo "Imesitishwa."
  exit 1
fi

echo "Kurestore data kutoka: $BACKUP_FILE"
psql "$DATABASE_URL" < "$BACKUP_FILE"
echo "Restore imekamilika."