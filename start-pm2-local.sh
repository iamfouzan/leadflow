#!/bin/bash
# ===============================================
# Start LeadFlow with PM2 (Local Development)
# ===============================================
# This script starts the application with PM2 for local testing

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

# Check if PM2 is installed
if ! command -v pm2 &> /dev/null; then
    warning "PM2 is not installed. Installing PM2..."
    npm install -g pm2
    log "✓ PM2 installed"
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    warning "Virtual environment not found. Creating..."
    python3 -m venv venv
    log "✓ Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if ! python -c "import fastapi" &> /dev/null; then
    log "Installing dependencies..."
    if command -v uv &> /dev/null; then
        uv pip install -r requirements.txt
    else
        pip install -r requirements.txt
    fi
    log "✓ Dependencies installed"
fi

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env.local
        warning "Created .env.local from .env.example"
        warning "Please update .env.local with your configuration"
        exit 1
    else
        warning ".env.local not found. Please create it."
        exit 1
    fi
fi

# Create local ecosystem config
cat > ecosystem.local.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'leadflow-dev',
    script: 'uvicorn',
    args: 'app.main:app --reload --host 0.0.0.0 --port 8000',
    interpreter: './venv/bin/python',
    instances: 1,
    exec_mode: 'fork',
    autorestart: true,
    watch: false,
    max_memory_restart: '500M',
    env: {
      ENVIRONMENT: 'local',
      PYTHONUNBUFFERED: '1'
    },
    error_file: './logs/error.log',
    out_file: './logs/out.log',
    log_file: './logs/combined.log',
    time: true,
    merge_logs: true
  }]
};
EOF

# Create logs directory
mkdir -p logs

# Stop existing PM2 process
pm2 delete leadflow-dev 2>/dev/null || true

# Start with PM2
log "Starting LeadFlow with PM2..."
pm2 start ecosystem.local.config.js

# Show status
pm2 status

log "=========================================="
log "Application started successfully!"
log "=========================================="
log "  API: http://localhost:8000"
log "  Docs: http://localhost:8000/docs"
log "  Health: http://localhost:8000/health"
log "=========================================="
log "PM2 Commands:"
log "  View logs: pm2 logs leadflow-dev"
log "  Monitor: pm2 monit"
log "  Restart: pm2 restart leadflow-dev"
log "  Stop: pm2 stop leadflow-dev"
log "=========================================="
