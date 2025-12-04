#!/bin/bash
# Setup script for Universal ERP development environment
# Usage: ./setup.sh

set -e

echo "========================================="
echo "  Universal ERP Development Setup"
echo "========================================="

# Check prerequisites
echo "Checking prerequisites..."

check_command() {
  if ! command -v $1 &> /dev/null; then
    echo "Error: $1 is not installed"
    exit 1
  fi
  echo "✓ $1 found"
}

check_command docker
check_command docker-compose
check_command python3
check_command node
check_command npm

# Create environment file if not exists
if [ ! -f .env ]; then
  echo "Creating .env file from template..."
  cp .env.example .env
  echo "Please edit .env file with your configuration"
fi

# Build Docker images
echo ""
echo "Building Docker images..."
docker-compose build

# Start infrastructure services
echo ""
echo "Starting infrastructure services..."
docker-compose up -d db redis rabbitmq

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 15

# Setup backend
echo ""
echo "Setting up backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi

# Activate virtual environment and install dependencies
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run migrations for each service
echo "Running database migrations..."
for service in auth_service inventory_service sales_service purchasing_service finance_service hr_service; do
  echo "  - $service"
  cd services/$service
  python manage.py migrate
  cd ../..
done

# Create superuser
echo ""
read -p "Create superuser? (yes/no): " CREATE_SUPERUSER
if [ "$CREATE_SUPERUSER" == "yes" ]; then
  cd services/auth_service
  python manage.py createsuperuser
  cd ../..
fi

cd ..

# Setup frontend web
echo ""
echo "Setting up frontend web..."
cd frontend/web
npm install
cd ../..

# Setup frontend mobile
echo ""
echo "Setting up frontend mobile..."
cd frontend/mobile
npm install
cd ../..

echo ""
echo "========================================="
echo "  Setup completed successfully!"
echo "========================================="
echo ""
echo "To start development:"
echo "  Backend:  cd backend && source venv/bin/activate && python manage.py runserver"
echo "  Frontend: cd frontend/web && npm run dev"
echo "  Mobile:   cd frontend/mobile && npx expo start"
echo ""
echo "Or use Docker Compose:"
echo "  docker-compose up"
echo ""
