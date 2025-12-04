# Universal ERP - Setup Script for Windows
# Run this script to set up the development environment

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Universal ERP - Development Setup" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot

# Check Python
Write-Host "`nChecking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Check Node.js
Write-Host "`nChecking Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "Found: Node.js $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

# Setup Backend
Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "  Setting up Backend" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

Set-Location "$ProjectRoot\backend"

# Create virtual environment
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "$ProjectRoot\backend\venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements.txt

# Setup Frontend Web
Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "  Setting up Frontend Web" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

Set-Location "$ProjectRoot\frontend\web"
Write-Host "Installing npm dependencies..." -ForegroundColor Yellow
npm install

# Setup Frontend Mobile
Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "  Setting up Frontend Mobile" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

Set-Location "$ProjectRoot\frontend\mobile"
Write-Host "Installing npm dependencies..." -ForegroundColor Yellow
npm install

# Create .env file if not exists
Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "  Creating environment files" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

Set-Location $ProjectRoot
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env file from .env.example" -ForegroundColor Green
    Write-Host "Please update .env with your configuration" -ForegroundColor Yellow
}

Write-Host "`n=========================================" -ForegroundColor Green
Write-Host "  Setup completed successfully!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Update .env file with your configuration"
Write-Host "2. Start Docker containers: docker-compose up -d"
Write-Host "3. Run migrations: cd backend && python manage.py migrate"
Write-Host "4. Start backend: cd backend && python manage.py runserver"
Write-Host "5. Start frontend web: cd frontend/web && npm run dev"
Write-Host "6. Start frontend mobile: cd frontend/mobile && npx expo start"
