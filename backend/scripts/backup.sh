#!/usr/bin/env bash
# ============================================
# Backup database (pg_dump) - run on the server
# Usage: ./scripts/backup.sh
# Backups are stored in ./backups/ with a timestamp.
# ============================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${BACKUP_DIR:-$BACKEND_DIR/backups}"
mkdir -p "$BACKUP_DIR"

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

STAMP="$(date +%Y%m%d_%H%M%S)"
OUTFILE="$BACKUP_DIR/pharmacy_backup_$STAMP.sql"

echo "Backing up: $DATABASE_URL -> $OUTFILE"
pg_dump --no-owner --no-privileges "$DATABASE_URL" > "$OUTFILE"
echo "Backup imekamilika: $OUTFILE"
echo "Kumbuka: songa faili hii nje ya server (kwenye mazingira salama)."