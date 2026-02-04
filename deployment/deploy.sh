#!/bin/bash
# ===============================================
# LeadFlow Deployment Script (PM2 Version)
# ===============================================
# This script deploys the application on AWS EC2 using PM2

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="leadflow"
APP_DIR="/opt/leadflow"
BACKUP_DIR="/opt/leadflow-backups"
LOG_FILE="/var/log/leadflow-deploy.log"
VENV_DIR="$APP_DIR/venv"

# Functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    error "Please run as root (use sudo)"
fi

log "=========================================="
log "Starting LeadFlow Deployment (PM2)"
log "=========================================="

# Step 1: Check prerequisites
log "Step 1: Checking prerequisites..."
command -v python3 >/dev/null 2>&1 || error "Python 3 is not installed"
command -v pm2 >/dev/null 2>&1 || error "PM2 is not installed"
command -v psql >/dev/null 2>&1 || error "PostgreSQL is not installed"
command -v redis-cli >/dev/null 2>&1 || error "Redis is not installed"
command -v nginx >/dev/null 2>&1 || error "Nginx is not installed"
log "✓ Prerequisites satisfied"

# Step 2: Check services status
log "Step 2: Checking services status..."
systemctl is-active --quiet postgresql || error "PostgreSQL is not running"
systemctl is-active --quiet redis-server || error "Redis is not running"
log "✓ All services are running"

# Step 3: Create backup directory
log "Step 3: Creating backup directory..."
mkdir -p "$BACKUP_DIR"
log "✓ Backup directory created"

# Step 4: Backup existing deployment (if exists)
if [ -d "$APP_DIR" ]; then
    log "Step 4: Backing up existing deployment..."
    BACKUP_NAME="leadflow-backup-$(date +%Y%m%d-%H%M%S).tar.gz"
    tar -czf "$BACKUP_DIR/$BACKUP_NAME" -C "$(dirname $APP_DIR)" "$(basename $APP_DIR)" \
        --exclude='venv' --exclude='__pycache__' --exclude='*.pyc' --exclude='.git'
    log "✓ Backup created: $BACKUP_NAME"
else
    log "Step 4: No existing deployment found, skipping backup"
fi

# Step 5: Create application directory
log "Step 5: Setting up application directory..."
mkdir -p "$APP_DIR"
cd "$APP_DIR"
log "✓ Application directory ready"

# Step 6: Pull latest code (if git is configured)
if [ -d ".git" ]; then
    log "Step 6: Pulling latest code from repository..."
    git fetch origin
    git reset --hard origin/main
    log "✓ Code updated from repository"
else
    log "Step 6: No git repository found, skipping pull"
    warning "Make sure to copy your application files to $APP_DIR"
fi

# Step 7: Check environment file
log "Step 7: Checking environment configuration..."
if [ ! -f "$APP_DIR/.env.production" ]; then
    error ".env.production file not found! Please create it from .env.production.example"
fi

# Create symlink for production env
ln -sf .env.production .env.local
log "✓ Environment file configured"

# Step 8: Set up Python virtual environment
log "Step 8: Setting up Python virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    log "✓ Virtual environment created"
else
    log "✓ Virtual environment already exists"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Step 9: Install UV if not present
log "Step 9: Checking UV installation..."
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
    log "✓ UV installed"
else
    log "✓ UV already available"
fi

# Step 10: Install/Update Python dependencies
log "Step 10: Installing Python dependencies..."
if command -v uv &> /dev/null; then
    uv pip install -r requirements.txt
    log "✓ Dependencies installed with UV (fast!)"
else
    pip install -r requirements.txt
    log "✓ Dependencies installed with pip"
fi

# Step 11: Run database migrations
log "Step 11: Running database migrations..."
alembic upgrade head || error "Migration failed"
log "✓ Migrations completed"

# Step 12: Update Nginx configuration
log "Step 12: Updating Nginx configuration..."
if [ -f "nginx/nginx.conf" ]; then
    cp nginx/nginx.conf /etc/nginx/nginx.conf
    nginx -t || error "Nginx configuration test failed"
    systemctl reload nginx
    log "✓ Nginx configuration updated"
else
    warning "Nginx configuration file not found, skipping"
fi

# Step 13: Stop existing PM2 processes (if any)
log "Step 13: Stopping existing PM2 processes..."
pm2 stop ecosystem.config.js || log "No existing processes to stop"
pm2 delete ecosystem.config.js || log "No existing processes to delete"
log "✓ Existing processes stopped"

# Step 14: Start application with PM2
log "Step 14: Starting application with PM2..."
pm2 start ecosystem.config.js --env production
pm2 save
log "✓ Application started with PM2"

# Step 15: Wait for application to be ready
log "Step 15: Waiting for application to be healthy..."
sleep 10

# Check health endpoint
for i in {1..30}; do
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        log "✓ Application is healthy"
        break
    fi
    if [ $i -eq 30 ]; then
        error "Application failed to start properly. Check logs with: pm2 logs"
    fi
    sleep 2
done

# Step 16: Show status
log "Step 16: Deployment status..."
pm2 status
pm2 info leadflow-api

log "=========================================="
log "Deployment completed successfully!"
log "=========================================="
log "Application Details:"
log "  Application URL: http://$(curl -s ifconfig.me):8000"
log "  API Documentation: http://$(curl -s ifconfig.me):8000/docs"
log "  Health Check: http://$(curl -s ifconfig.me):8000/health"
log "=========================================="
log "PM2 Commands:"
log "  View logs: pm2 logs leadflow-api"
log "  Restart app: pm2 restart leadflow-api"
log "  Stop app: pm2 stop leadflow-api"
log "  Monitor: pm2 monit"
log "  Status: pm2 status"
log "=========================================="
log "Services Status:"
log "  PostgreSQL: $(systemctl is-active postgresql)"
log "  Redis: $(systemctl is-active redis-server)"
log "  Nginx: $(systemctl is-active nginx)"
log "  PM2: $(pm2 list | grep leadflow-api | awk '{print $12}')"
log "=========================================="
