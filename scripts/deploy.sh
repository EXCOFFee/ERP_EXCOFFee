#!/bin/bash
# Deploy script for Universal ERP
# Usage: ./deploy.sh [environment]

set -e

ENVIRONMENT=${1:-production}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DEPLOY_DIR="/opt/erp"
BACKUP_DIR="/opt/erp/backups/$TIMESTAMP"

echo "========================================="
echo "  Universal ERP Deployment"
echo "  Environment: $ENVIRONMENT"
echo "  Timestamp: $TIMESTAMP"
echo "========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root or with sudo"
  exit 1
fi

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup current deployment
if [ -d "$DEPLOY_DIR/current" ]; then
  echo "Backing up current deployment..."
  cp -r "$DEPLOY_DIR/current" "$BACKUP_DIR/"
fi

# Pull latest code
echo "Pulling latest code..."
cd "$DEPLOY_DIR/repo"
git fetch origin
git checkout main
git pull origin main

# Build Docker images
echo "Building Docker images..."
docker-compose -f docker-compose.yml -f docker-compose.$ENVIRONMENT.yml build --no-cache

# Run database migrations
echo "Running database migrations..."
docker-compose -f docker-compose.yml -f docker-compose.$ENVIRONMENT.yml run --rm api python manage.py migrate

# Collect static files
echo "Collecting static files..."
docker-compose -f docker-compose.yml -f docker-compose.$ENVIRONMENT.yml run --rm api python manage.py collectstatic --noinput

# Stop old containers
echo "Stopping old containers..."
docker-compose -f docker-compose.yml -f docker-compose.$ENVIRONMENT.yml down

# Start new containers
echo "Starting new containers..."
docker-compose -f docker-compose.yml -f docker-compose.$ENVIRONMENT.yml up -d

# Wait for services to be healthy
echo "Waiting for services to be healthy..."
sleep 30

# Health check
echo "Running health check..."
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/api/health/)
if [ "$HEALTH_STATUS" != "200" ]; then
  echo "Health check failed! Rolling back..."
  docker-compose -f docker-compose.yml -f docker-compose.$ENVIRONMENT.yml down
  if [ -d "$BACKUP_DIR/current" ]; then
    cp -r "$BACKUP_DIR/current" "$DEPLOY_DIR/"
    docker-compose -f docker-compose.yml -f docker-compose.$ENVIRONMENT.yml up -d
  fi
  exit 1
fi

# Clean up old backups (keep last 5)
echo "Cleaning up old backups..."
cd "$DEPLOY_DIR/backups"
ls -t | tail -n +6 | xargs -r rm -rf

# Clean up Docker
echo "Cleaning up Docker..."
docker system prune -f

echo "========================================="
echo "  Deployment completed successfully!"
echo "========================================="
