#!/usr/bin/env bash
#
# Create a dated, compressed snapshot of the entire project — including
# db.sqlite3, .env, and all image folders — and move it into backups_history/.
#
# Usage:  ./make_backup.sh

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="$(basename "$PROJECT_DIR")"
PARENT_DIR="$(dirname "$PROJECT_DIR")"
BACKUP_DIR="$PROJECT_DIR/backups_history"
TIMESTAMP="$(date +%Y-%m-%d_%H%M)"
ARCHIVE_NAME="alasadi_catalog_backup_${TIMESTAMP}.tar.gz"

# Build the archive in /tmp first so tar isn't writing into the directory it's
# reading from (avoids "file changed as we read it" warnings and self-inclusion).
TMP_ARCHIVE="/tmp/${ARCHIVE_NAME}"

mkdir -p "$BACKUP_DIR"

echo "Creating backup: ${ARCHIVE_NAME}"
echo "  From: ${PROJECT_DIR}"
echo "  To:   ${BACKUP_DIR}"

# --exclude paths are relative to the -C directory (the project's parent),
# so they need the project-name prefix. '__pycache__' with no slash matches
# at any depth — covers the nested ones inside every Django app.
tar -czf "$TMP_ARCHIVE" \
    -C "$PARENT_DIR" \
    --exclude="${PROJECT_NAME}/venv" \
    --exclude="${PROJECT_NAME}/backups_history" \
    --exclude='__pycache__' \
    "$PROJECT_NAME"

FINAL_PATH="$BACKUP_DIR/$ARCHIVE_NAME"
mv "$TMP_ARCHIVE" "$FINAL_PATH"

SIZE="$(du -h "$FINAL_PATH" | awk '{print $1}')"
echo "Done. Archive: $FINAL_PATH ($SIZE)"
