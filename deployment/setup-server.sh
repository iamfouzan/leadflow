#!/bin/bash
# ===============================================
# AWS EC2 Server Setup Script (PM2 Deployment)
# ===============================================
# Run this script on a fresh Ubuntu/Debian EC2 instance

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
    exit 1
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    error "Please run as root (use sudo)"
fi

log "=========================================="
log "Setting up LeadFlow Server on AWS EC2 (PM2)"
log "=========================================="

# Update system
log "Step 1: Updating system packages..."
apt-get update -y
apt-get upgrade -y
log "✓ System updated"

# Install essential tools
log "Step 2: Installing essential tools..."
apt-get install -y \
    curl \
    wget \
    git \
    vim \
    htop \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    build-essential \
    libssl-dev \
    libffi-dev
log "✓ Essential tools installed"

# Install Python 3.11+
log "Step 3: Installing Python 3.11..."
apt-get install -y software-properties-common
add-apt-repository -y ppa:deadsnakes/ppa
apt-get update -y
apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip
# Set Python 3.11 as default python3
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
log "✓ Python 3.11 installed"

# Install PostgreSQL 15
log "Step 4: Installing PostgreSQL 15..."
if ! command -v psql &> /dev/null; then
    # Add PostgreSQL repository
    curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /usr/share/keyrings/postgresql-keyring.gpg
    echo "deb [signed-by=/usr/share/keyrings/postgresql-keyring.gpg] http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" | tee /etc/apt/sources.list.d/pgdg.list
    
    apt-get update -y
    apt-get install -y postgresql-15 postgresql-contrib-15
    
    systemctl start postgresql
    systemctl enable postgresql
    
    log "✓ PostgreSQL 15 installed"
else
    log "✓ PostgreSQL already installed"
fi

# Install Redis
log "Step 5: Installing Redis..."
if ! command -v redis-cli &> /dev/null; then
    apt-get install -y redis-server
    
    # Configure Redis for production
    sed -i 's/^supervised no/supervised systemd/' /etc/redis/redis.conf
    sed -i 's/^bind 127.0.0.1 ::1/bind 127.0.0.1/' /etc/redis/redis.conf
    
    systemctl restart redis-server
    systemctl enable redis-server
    
    log "✓ Redis installed and configured"
else
    log "✓ Redis already installed"
fi

# Install Node.js (required for PM2)
log "Step 6: Installing Node.js LTS..."
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_lts.x | bash -
    apt-get install -y nodejs
    log "✓ Node.js installed: $(node --version)"
else
    log "✓ Node.js already installed: $(node --version)"
fi

# Install PM2
log "Step 7: Installing PM2..."
if ! command -v pm2 &> /dev/null; then
    npm install -g pm2
    
    # Configure PM2 startup script
    pm2 startup systemd -u root --hp /root
    
    log "✓ PM2 installed: $(pm2 --version)"
else
    log "✓ PM2 already installed: $(pm2 --version)"
fi

# Install UV (fast Python package manager)
log "Step 8: Installing UV..."
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
    echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
    log "✓ UV installed"
else
    log "✓ UV already installed"
fi

# Create application directory
log "Step 9: Creating application directory..."
mkdir -p /opt/leadflow
mkdir -p /opt/leadflow-backups
mkdir -p /var/log/leadflow
chown -R root:root /opt/leadflow
chown -R root:root /var/log/leadflow
log "✓ Directories created"

# Install Nginx (for reverse proxy)
log "Step 10: Installing Nginx..."
if ! command -v nginx &> /dev/null; then
    apt-get install -y nginx
    systemctl enable nginx
    log "✓ Nginx installed"
else
    log "✓ Nginx already installed"
fi

# Install Certbot for SSL (Let's Encrypt)
log "Step 11: Installing Certbot for SSL..."
apt-get install -y certbot python3-certbot-nginx
log "✓ Certbot installed"

# Configure firewall
log "Step 12: Configuring UFW firewall..."
ufw --force enable
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
log "✓ Firewall configured"

# Install monitoring tools
log "Step 13: Installing monitoring tools..."
apt-get install -y \
    net-tools \
    iotop \
    iftop \
    sysstat
log "✓ Monitoring tools installed"

# Configure swap (recommended for t2.micro/small instances)
log "Step 14: Configuring swap space..."
if [ ! -f /swapfile ]; then
    fallocate -l 2G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
    log "✓ 2GB swap space created"
else
    log "✓ Swap already configured"
fi

# Set up log rotation
log "Step 15: Setting up log rotation..."
cat > /etc/logrotate.d/leadflow << 'EOF'
/var/log/leadflow/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 root root
    sharedscripts
    postrotate
        pm2 reloadLogs
    endscript
}
EOF
log "✓ Log rotation configured"

# Install AWS CLI (for backups to S3)
log "Step 16: Installing AWS CLI..."
if ! command -v aws &> /dev/null; then
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip awscliv2.zip
    ./aws/install
    rm -rf aws awscliv2.zip
    log "✓ AWS CLI installed"
else
    log "✓ AWS CLI already installed"
fi

# Configure PostgreSQL
log "Step 17: Configuring PostgreSQL..."
sudo -u postgres psql << 'EOSQL'
-- Create database and user
CREATE DATABASE service_marketplace;
CREATE USER leadflow WITH ENCRYPTED PASSWORD 'changeme_strong_password';
GRANT ALL PRIVILEGES ON DATABASE service_marketplace TO leadflow;

-- Grant schema privileges
\c service_marketplace
GRANT ALL ON SCHEMA public TO leadflow;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO leadflow;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO leadflow;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO leadflow;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO leadflow;
EOSQL
log "✓ PostgreSQL database configured"
warning "⚠️  Remember to change the default PostgreSQL password!"

# Configure Redis password (optional but recommended)
log "Step 18: Securing Redis..."
REDIS_PASSWORD=$(openssl rand -hex 32)
echo "requirepass $REDIS_PASSWORD" >> /etc/redis/redis.conf
systemctl restart redis-server
echo "Redis Password: $REDIS_PASSWORD" > /root/.redis_password
chmod 600 /root/.redis_password
log "✓ Redis secured with password"
warning "⚠️  Redis password saved to /root/.redis_password"

# Create backup script
log "Step 19: Creating backup script..."
cat > /opt/leadflow-backups/backup.sh << 'EOF'
#!/bin/bash
# Backup script for LeadFlow (PM2 version)

BACKUP_DIR="/opt/leadflow-backups"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
APP_DIR="/opt/leadflow"

# Backup database
PGPASSWORD="changeme_strong_password" pg_dump -U leadflow -h localhost service_marketplace | gzip > "$BACKUP_DIR/db-backup-$TIMESTAMP.sql.gz"

# Backup application files
tar -czf "$BACKUP_DIR/app-backup-$TIMESTAMP.tar.gz" -C "$APP_DIR" --exclude='venv' --exclude='__pycache__' --exclude='*.pyc' .

# Upload to S3 (if configured)
# aws s3 cp "$BACKUP_DIR/db-backup-$TIMESTAMP.sql.gz" s3://your-bucket/backups/
# aws s3 cp "$BACKUP_DIR/app-backup-$TIMESTAMP.tar.gz" s3://your-bucket/backups/

# Delete backups older than 7 days
find "$BACKUP_DIR" -name "*.gz" -mtime +7 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $TIMESTAMP"
EOF

chmod +x /opt/leadflow-backups/backup.sh
log "✓ Backup script created"

# Set up daily backup cron job
log "Step 20: Setting up daily backup cron job..."
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/leadflow-backups/backup.sh >> /var/log/leadflow/backup.log 2>&1") | crontab -
log "✓ Daily backup cron job configured (runs at 2 AM)"

# Set up automatic updates
log "Step 21: Configuring automatic security updates..."
apt-get install -y unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades
log "✓ Automatic updates configured"

# Display system information
log "=========================================="
log "Server Setup Complete!"
log "=========================================="
log "System Information:"
log "  OS: $(lsb_release -d | cut -f2)"
log "  Kernel: $(uname -r)"
log "  Python: $(python3 --version)"
log "  PostgreSQL: $(psql --version | cut -d' ' -f3)"
log "  Redis: $(redis-cli --version | cut -d' ' -f2)"
log "  Node.js: $(node --version)"
log "  PM2: $(pm2 --version)"
log "  Nginx: $(nginx -v 2>&1 | cut -d'/' -f2)"
log "  Public IP: $(curl -s ifconfig.me)"
log "=========================================="
log "Database Credentials:"
log "  Database: service_marketplace"
log "  Username: leadflow"
log "  Password: changeme_strong_password (CHANGE THIS!)"
log "  Redis Password: Saved in /root/.redis_password"
log "=========================================="
log "Next Steps:"
log "  1. Copy your application code to /opt/leadflow"
log "  2. Create .env.production file with your configuration"
log "  3. Update PostgreSQL password in backup script and .env"
log "  4. Run the deployment script: bash /opt/leadflow/deployment/deploy.sh"
log "  5. Configure SSL with: certbot --nginx -d yourdomain.com"
log "  6. Configure PM2 to save process list: pm2 save"
log "=========================================="
