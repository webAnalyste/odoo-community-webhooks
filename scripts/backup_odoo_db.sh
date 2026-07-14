#!/bin/bash
# =============================================================================
# BACKUP ODOO DB → S3
# Installé sur le VPS dans /opt/odoo/backup_odoo_db.sh
# Cron (toutes les 12h) :
#   0 2,14 * * * /opt/odoo/backup_odoo_db.sh >> /var/log/backup_odoo.log 2>&1
# =============================================================================

set -e

# Load .env file if present (never committed — copy .env.example → .env and fill in)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/.env" ]; then
    set -o allexport
    # shellcheck source=/dev/null
    source "$SCRIPT_DIR/.env"
    set +o allexport
fi

# --- CONFIGURATION -----------------------------------------------------------
PG_CONTAINER="postgresql-gm7iq81galclkuzhm0bnwbxu"
PG_USER="fscan"
PG_DB="odoo"
# PG_PASSWORD, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY loaded from .env / env

S3_BUCKET="wa-odoo"
S3_PREFIX="data/coolify/odoo/db_backup"
RETENTION_DAYS=15

export AWS_DEFAULT_REGION="eu-west-3"
# -----------------------------------------------------------------------------

DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="odoo_db_${DATE}.dump"
TMPFILE="/tmp/${FILENAME}"

echo "=== Backup Odoo DB — $(date) ==="

# 1. pg_dump dans le container PostgreSQL
echo "[1/3] pg_dump..."
docker exec -e PGPASSWORD="$PG_PASSWORD" "$PG_CONTAINER" \
    pg_dump -U "$PG_USER" -Fc "$PG_DB" -f "/var/lib/postgresql/data/${FILENAME}"
docker cp "$PG_CONTAINER:/var/lib/postgresql/data/${FILENAME}" "$TMPFILE"
docker exec "$PG_CONTAINER" rm -f "/var/lib/postgresql/data/${FILENAME}"
echo "      Taille : $(du -sh $TMPFILE | cut -f1)"

# 2. Upload S3
echo "[2/3] Upload S3..."
aws s3 cp "$TMPFILE" "s3://${S3_BUCKET}/${S3_PREFIX}/${FILENAME}"
rm -f "$TMPFILE"
echo "      OK : s3://${S3_BUCKET}/${S3_PREFIX}/${FILENAME}"

# 3. Rétention
echo "[3/3] Rétention ${RETENTION_DAYS} jours..."
CUTOFF=$(date -d "${RETENTION_DAYS} days ago" +%Y-%m-%dT%H:%M:%S)
aws s3 ls "s3://${S3_BUCKET}/${S3_PREFIX}/" | while read -r line; do
    FDATE=$(echo "$line" | awk '{print $1"T"$2}')
    FNAME=$(echo "$line" | awk '{print $4}')
    if [[ "$FNAME" == odoo_db_*.dump ]] && [[ "$FDATE" < "$CUTOFF" ]]; then
        aws s3 rm "s3://${S3_BUCKET}/${S3_PREFIX}/${FNAME}"
        echo "      Supprimé : $FNAME"
    fi
done

echo "=== Backup terminé : ${FILENAME} ==="
