# PM2 Deployment Guide for LeadFlow on AWS EC2

This guide covers deploying the LeadFlow FastAPI application to AWS EC2 using PM2 process manager.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [AWS EC2 Setup](#aws-ec2-setup)
3. [Server Configuration](#server-configuration)
4. [Application Deployment](#application-deployment)
5. [Nginx Configuration](#nginx-configuration)
6. [SSL/HTTPS Setup](#ssl-https-setup)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### AWS Requirements
- AWS Account
- EC2 instance (recommended: t3.small or larger)
- Ubuntu 22.04 LTS
- Security Group configured:
  - Port 22 (SSH)
  - Port 80 (HTTP)
  - Port 443 (HTTPS)
- Elastic IP (optional but recommended)
- Domain name (optional, for SSL)

### Local Requirements
- SSH client
- Git (for version control)
- Basic Linux knowledge

---

## AWS EC2 Setup

### 1. Launch EC2 Instance

```bash
# Recommended instance specifications:
Instance Type: t3.small (2 vCPU, 2 GB RAM)
AMI: Ubuntu Server 22.04 LTS
Storage: 20 GB gp3 SSD
```

### 2. Configure Security Group

```bash
# Inbound Rules:
SSH (22) - Your IP address
HTTP (80) - 0.0.0.0/0
HTTPS (443) - 0.0.0.0/0
Custom TCP (8000) - 0.0.0.0/0 (optional, for testing)

# Outbound Rules:
All traffic - 0.0.0.0/0
```

### 3. Associate Elastic IP

```bash
# From AWS Console:
1. Allocate new Elastic IP
2. Associate with your EC2 instance
3. Update DNS records (if using domain)
```

---

## Server Configuration

### 1. Initial Server Setup

```bash
# SSH into your server
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Copy setup script to server
scp -i your-key.pem deployment/setup-server.sh ubuntu@your-ec2-ip:/home/ubuntu/

# Run setup script
sudo bash /home/ubuntu/setup-server.sh
```

The setup script installs:
- Python 3.11
- PostgreSQL 15
- Redis 5+
- Node.js LTS
- PM2
- Nginx
- Certbot
- UV (fast Python package manager)
- AWS CLI
- Monitoring tools

### 2. Post-Setup Configuration

#### Update PostgreSQL Password

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Change password
ALTER USER leadflow WITH PASSWORD 'your_strong_password_here';

# Exit
\q
```

#### Configure Redis Password

```bash
# Redis password is auto-generated and saved
sudo cat /root/.redis_password

# Or set a custom password
sudo nano /etc/redis/redis.conf
# Find and update: requirepass your_redis_password

# Restart Redis
sudo systemctl restart redis-server
```

---

## Application Deployment

### 1. Copy Application Files

**Option A: From Local Machine**

```bash
# From your local machine
cd /path/to/leadflow
rsync -avz -e "ssh -i your-key.pem" \
  --exclude='venv' \
  --exclude='__pycache__' \
  --exclude='.git' \
  . ubuntu@your-ec2-ip:/opt/leadflow/
```

**Option B: From Git Repository**

```bash
# SSH into server
ssh ubuntu@your-ec2-ip

# Clone repository
cd /opt
sudo git clone your-repo-url leadflow
cd leadflow
```

### 2. Configure Environment Variables

```bash
cd /opt/leadflow

# Copy example to production
sudo cp .env.production.example .env.production

# Edit with your actual values
sudo nano .env.production
```

**Important Variables to Update:**

```bash
# Database
DATABASE_URL=postgresql://leadflow:YOUR_PASSWORD@localhost:5432/service_marketplace

# Redis
REDIS_URL=redis://:YOUR_REDIS_PASSWORD@localhost:6379/0

# JWT Secret (generate with: openssl rand -hex 32)
SECRET_KEY=your_generated_secret_key

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@yourdomain.com

# CORS
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 3. Run Deployment Script

```bash
cd /opt/leadflow
sudo bash deployment/deploy.sh
```

The deployment script will:
1. Create Python virtual environment
2. Install dependencies with UV (super fast!)
3. Run database migrations
4. Configure Nginx
5. Start application with PM2
6. Configure auto-restart

### 4. Verify Deployment

```bash
# Check PM2 status
pm2 status

# Check application health
curl http://localhost:8000/health

# Check logs
pm2 logs leadflow-api
```

---

## Nginx Configuration

### 1. Update Nginx Config

The deployment script automatically copies the Nginx configuration, but you can manually update:

```bash
# Edit Nginx config
sudo nano /etc/nginx/nginx.conf

# Update server_name with your domain
server_name yourdomain.com www.yourdomain.com;

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### 2. Verify Nginx

```bash
# Check Nginx status
sudo systemctl status nginx

# Test through Nginx
curl http://your-ec2-ip/health
```

---

## SSL/HTTPS Setup

### 1. Configure DNS

Before setting up SSL, ensure your domain points to your EC2 Elastic IP:

```bash
# A Record
yourdomain.com -> your-elastic-ip
www.yourdomain.com -> your-elastic-ip
```

### 2. Install SSL Certificate

```bash
# Using Let's Encrypt (free)
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Follow the prompts:
# - Enter email address
# - Agree to terms
# - Choose redirect option (recommended: 2)
```

### 3. Auto-Renewal

Certbot automatically sets up renewal. Verify:

```bash
# Test renewal
sudo certbot renew --dry-run

# Check renewal timer
sudo systemctl status certbot.timer
```

### 4. Verify HTTPS

```bash
# Test HTTPS
curl https://yourdomain.com/health

# Check certificate
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com
```

---

## Monitoring & Maintenance

### PM2 Monitoring

```bash
# Real-time monitoring
pm2 monit

# View logs
pm2 logs leadflow-api

# View specific number of lines
pm2 logs leadflow-api --lines 200

# Clear logs
pm2 flush

# Application metrics
pm2 show leadflow-api
```

### System Monitoring

```bash
# Check CPU and memory
htop

# Check disk usage
df -h

# Check network connections
netstat -tuln

# Check running processes
ps aux | grep python
```

### Database Monitoring

```bash
# Connect to database
sudo -u postgres psql -d service_marketplace

# Check active connections
SELECT count(*) FROM pg_stat_activity;

# Check database size
SELECT pg_size_pretty(pg_database_size('service_marketplace'));

# Check table sizes
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Redis Monitoring

```bash
# Connect to Redis
redis-cli -a $(cat /root/.redis_password)

# Check stats
INFO stats

# Monitor commands
MONITOR

# Check memory usage
INFO memory
```

### Automated Backups

Backups run automatically at 2 AM daily. Manual backup:

```bash
# Run backup script
sudo /opt/leadflow-backups/backup.sh

# View backup logs
sudo tail -f /var/log/leadflow/backup.log

# List backups
ls -lh /opt/leadflow-backups/
```

### Log Rotation

Logs are automatically rotated daily. Check configuration:

```bash
# View log rotation config
cat /etc/logrotate.d/leadflow

# Manually trigger rotation
sudo logrotate -f /etc/logrotate.d/leadflow
```

---

## Troubleshooting

### Application Won't Start

```bash
# Check PM2 logs
pm2 logs leadflow-api --lines 100

# Check if port is in use
sudo lsof -i :8000

# Restart application
pm2 restart leadflow-api

# Delete and restart
pm2 delete leadflow-api
pm2 start ecosystem.config.js --env production
```

### Database Connection Issues

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check if PostgreSQL is listening
sudo netstat -tulnp | grep 5432

# Check database connection
psql -U leadflow -h localhost -d service_marketplace

# View PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-15-main.log

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### Redis Connection Issues

```bash
# Check Redis status
sudo systemctl status redis-server

# Test Redis connection
redis-cli -a $(cat /root/.redis_password) ping

# View Redis logs
sudo tail -f /var/log/redis/redis-server.log

# Restart Redis
sudo systemctl restart redis-server
```

### Nginx Issues

```bash
# Test Nginx configuration
sudo nginx -t

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log

# Restart Nginx
sudo systemctl restart nginx

# Check if Nginx is running
sudo systemctl status nginx
```

### High Memory Usage

```bash
# Check PM2 app memory
pm2 status

# Restart app to clear memory
pm2 restart leadflow-api

# Reduce PM2 workers (in ecosystem.config.js)
# Change: --workers 4 to --workers 2

# Clear system cache
sudo sync && sudo sysctl -w vm.drop_caches=3
```

### Disk Space Issues

```bash
# Check disk usage
df -h

# Find large files
sudo du -h /opt/leadflow | sort -rh | head -20

# Clean old logs
sudo find /var/log -name "*.gz" -mtime +30 -delete

# Clean old backups
sudo find /opt/leadflow-backups -name "*.gz" -mtime +7 -delete

# Clean package cache
sudo apt clean
```

### Migration Issues

```bash
# Check migration status
cd /opt/leadflow
source venv/bin/activate
alembic current

# View migration history
alembic history

# Rollback migration
alembic downgrade -1

# Re-run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"
```

### Permission Issues

```bash
# Fix application directory permissions
sudo chown -R root:root /opt/leadflow

# Fix log directory permissions
sudo chown -R root:root /var/log/leadflow
sudo chmod 755 /var/log/leadflow

# Fix virtual environment permissions
sudo chown -R root:root /opt/leadflow/venv
```

---

## Performance Optimization

### 1. PM2 Configuration

```javascript
// ecosystem.config.js
{
  instances: 1,  // Use 1 for small instances
  max_memory_restart: '1G',  // Restart if memory exceeds 1GB
  exec_mode: 'fork'  // Use 'cluster' for multiple instances
}
```

### 2. PostgreSQL Tuning

```bash
# Edit PostgreSQL config
sudo nano /etc/postgresql/15/main/postgresql.conf

# Recommended settings for t3.small:
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
max_connections = 50

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### 3. Redis Tuning

```bash
# Edit Redis config
sudo nano /etc/redis/redis.conf

# Recommended settings:
maxmemory 256mb
maxmemory-policy allkeys-lru

# Restart Redis
sudo systemctl restart redis-server
```

### 4. Nginx Tuning

```nginx
# /etc/nginx/nginx.conf
worker_processes auto;
worker_connections 2048;
keepalive_timeout 65;
gzip on;
gzip_comp_level 6;
```

---

## Scaling Considerations

### Vertical Scaling (Upgrade Instance)

```bash
# Stop application
pm2 stop leadflow-api

# From AWS Console:
# 1. Stop EC2 instance
# 2. Change instance type (e.g., t3.small -> t3.medium)
# 3. Start instance

# Update PM2 workers
# Edit ecosystem.config.js
# Increase --workers parameter

# Restart application
pm2 restart leadflow-api
```

### Horizontal Scaling (Multiple Instances)

For high-traffic scenarios:

1. Set up Application Load Balancer (ALB)
2. Launch multiple EC2 instances
3. Use RDS for PostgreSQL (shared database)
4. Use ElastiCache for Redis (shared cache)
5. Configure PM2 cluster mode

---

## Security Checklist

- [ ] Changed default PostgreSQL password
- [ ] Set Redis password
- [ ] Generated strong JWT secret key
- [ ] Configured firewall (UFW) properly
- [ ] Enabled automatic security updates
- [ ] Installed SSL certificate
- [ ] Configured proper CORS origins
- [ ] Set up regular backups
- [ ] Enabled log rotation
- [ ] Reviewed and hardened SSH access
- [ ] Set up monitoring and alerts
- [ ] Disabled root login over SSH
- [ ] Changed default ports (optional)

---

## Useful Commands Reference

```bash
# PM2 Commands
pm2 start ecosystem.config.js --env production
pm2 restart leadflow-api
pm2 stop leadflow-api
pm2 delete leadflow-api
pm2 logs leadflow-api
pm2 monit
pm2 status
pm2 save
pm2 resurrect

# Service Management
sudo systemctl start postgresql
sudo systemctl stop postgresql
sudo systemctl restart postgresql
sudo systemctl status postgresql

sudo systemctl start redis-server
sudo systemctl stop redis-server
sudo systemctl restart redis-server
sudo systemctl status redis-server

sudo systemctl start nginx
sudo systemctl stop nginx
sudo systemctl restart nginx
sudo systemctl reload nginx
sudo systemctl status nginx

# Database
psql -U leadflow -h localhost -d service_marketplace
pg_dump -U leadflow -h localhost service_marketplace > backup.sql
psql -U leadflow -h localhost service_marketplace < backup.sql

# Redis
redis-cli -a password
redis-cli -a password INFO
redis-cli -a password MONITOR

# Logs
tail -f /var/log/leadflow/out.log
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
tail -f /var/log/postgresql/postgresql-15-main.log
pm2 logs leadflow-api --lines 200

# System
htop
df -h
free -h
netstat -tulnp
ps aux | grep python
```

---

## Support & Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **PM2 Documentation**: https://pm2.keymetrics.io/
- **Nginx Documentation**: https://nginx.org/en/docs/
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/
- **Redis Documentation**: https://redis.io/documentation
- **Let's Encrypt**: https://letsencrypt.org/
- **AWS EC2**: https://docs.aws.amazon.com/ec2/

---

## Changelog

- **v2.0** (Feb 2026) - Migrated from Docker to PM2 deployment
- **v1.0** (Jan 2026) - Initial deployment with Docker

---

**Deployment Status**: ✅ Production-Ready with PM2  
**Estimated Setup Time**: 30-45 minutes  
**Recommended Instance**: t3.small or larger  
**Tested On**: Ubuntu 22.04 LTS, AWS EC2
