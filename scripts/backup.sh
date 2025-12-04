#!/bin/bash
# Backup script for Universal ERP
# Usage: ./backup.sh

set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/erp/backups/$TIMESTAMP"
S3_BUCKET=${S3_BACKUP_BUCKET:-"erp-backups"}

echo "========================================="
echo "  Universal ERP Backup"
echo "  Timestamp: $TIMESTAMP"
echo "========================================="

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup PostgreSQL database
echo "Backing up PostgreSQL database..."
docker-compose exec -T db pg_dump -U $POSTGRES_USER $POSTGRES_DB | gzip > "$BACKUP_DIR/database.sql.gz"

# Backup Redis data
echo "Backing up Redis data..."
docker-compose exec -T redis redis-cli BGSAVE
sleep 5
docker cp $(docker-compose ps -q redis):/data/dump.rdb "$BACKUP_DIR/redis.rdb"

# Backup uploaded files
echo "Backing up uploaded files..."
if [ -d "/opt/erp/media" ]; then
  tar -czf "$BACKUP_DIR/media.tar.gz" -C /opt/erp media
fi

# Backup configuration files
echo "Backing up configuration files..."
cp /opt/erp/.env "$BACKUP_DIR/.env"
cp /opt/erp/docker-compose*.yml "$BACKUP_DIR/"

# Create backup manifest
echo "Creating backup manifest..."
cat > "$BACKUP_DIR/manifest.json" << EOF
{
  "timestamp": "$TIMESTAMP",
  "type": "full",
  "components": {
    "database": "database.sql.gz",
    "redis": "redis.rdb",
    "media": "media.tar.gz",
    "config": ".env"
  },
  "created_at": "$(date -Iseconds)"
}
EOF

# Upload to S3 (if AWS CLI is configured)
if command -v aws &> /dev/null; then
  echo "Uploading backup to S3..."
  aws s3 sync "$BACKUP_DIR" "s3://$S3_BUCKET/$TIMESTAMP/"
  echo "Backup uploaded to s3://$S3_BUCKET/$TIMESTAMP/"
fi

# Clean up old local backups (keep last 7 days)
echo "Cleaning up old backups..."
find /opt/erp/backups -maxdepth 1 -type d -mtime +7 -exec rm -rf {} \;

echo "========================================="
echo "  Backup completed successfully!"
echo "  Location: $BACKUP_DIR"
echo "========================================="
