#!/bin/bash
# Restore script for Universal ERP
# Usage: ./restore.sh [backup_timestamp]

set -e

BACKUP_TIMESTAMP=${1:-$(ls -t /opt/erp/backups | head -1)}
BACKUP_DIR="/opt/erp/backups/$BACKUP_TIMESTAMP"

if [ ! -d "$BACKUP_DIR" ]; then
  echo "Backup directory not found: $BACKUP_DIR"
  echo "Available backups:"
  ls -la /opt/erp/backups
  exit 1
fi

echo "========================================="
echo "  Universal ERP Restore"
echo "  Backup: $BACKUP_TIMESTAMP"
echo "========================================="

read -p "This will overwrite current data. Are you sure? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
  echo "Restore cancelled."
  exit 0
fi

# Stop services
echo "Stopping services..."
docker-compose down

# Restore database
if [ -f "$BACKUP_DIR/database.sql.gz" ]; then
  echo "Restoring database..."
  docker-compose up -d db
  sleep 10
  gunzip -c "$BACKUP_DIR/database.sql.gz" | docker-compose exec -T db psql -U $POSTGRES_USER $POSTGRES_DB
fi

# Restore Redis
if [ -f "$BACKUP_DIR/redis.rdb" ]; then
  echo "Restoring Redis data..."
  docker-compose up -d redis
  docker cp "$BACKUP_DIR/redis.rdb" $(docker-compose ps -q redis):/data/dump.rdb
  docker-compose restart redis
fi

# Restore media files
if [ -f "$BACKUP_DIR/media.tar.gz" ]; then
  echo "Restoring media files..."
  rm -rf /opt/erp/media
  tar -xzf "$BACKUP_DIR/media.tar.gz" -C /opt/erp
fi

# Start all services
echo "Starting all services..."
docker-compose up -d

# Wait for services
sleep 30

# Health check
echo "Running health check..."
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/api/health/)
if [ "$HEALTH_STATUS" != "200" ]; then
  echo "Health check failed! Check logs for errors."
  docker-compose logs --tail=50
  exit 1
fi

echo "========================================="
echo "  Restore completed successfully!"
echo "========================================="
