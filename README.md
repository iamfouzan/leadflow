# LeadFlow - Service Marketplace Backend

Production-grade FastAPI backend for a dual-app service marketplace platform connecting Potential Customers with Business Owners.

## 🚀 Quick Start

```bash
# Install UV (10-100x faster than pip)
bash setup-uv.sh

# Install dependencies
uv pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

**📚 Complete Setup Guide**: See [SETUP_COMPLETE_SUMMARY.md](./SETUP_COMPLETE_SUMMARY.md)

## ✅ Latest Updates (v2.0 - February 2026)

- ✅ **UUID-based IDs** (secure, non-sequential)
- ✅ **Enhanced Profile Fields** (address, city, state, country, picture, gender)
- ✅ **ADMIN User Type** added
- ✅ **UV Package Manager** (10-100x faster than pip)
- ✅ **PM2 Deployment** for AWS EC2 (production-ready)
- ✅ **OTP Verification** intact and working
- ✅ **Production-Ready** Nginx configuration

## Features

- Complete authentication system for Customer and Business Owner apps
- JWT-based authentication with access and refresh tokens
- OTP verification via email (SMTP)
- PostgreSQL database with SQLAlchemy ORM
- **UUID-based primary keys** for enhanced security and scalability
- Redis for OTP storage and session management
- REST API endpoints for authentication
- Environment-based configuration (local/production)
- Comprehensive testing with pytest
- Type hints throughout
- Professional code structure following best practices

## Tech Stack

- **Framework**: FastAPI 0.104.1
- **Language**: Python 3.11+
- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0+
- **Migrations**: Alembic
- **Caching**: Redis 5.0+
- **Authentication**: JWT (python-jose)
- **Validation**: Pydantic v2
- **Testing**: Pytest

## Project Structure

```
service-marketplace-backend/
├── app/
│   ├── core/              # Core functionality (security, dependencies, exceptions, middleware)
│   ├── db/                # Database connection and base models
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   ├── api/               # API routes
│   ├── services/          # Business logic layer
│   ├── repositories/      # Data access layer
│   ├── utils/             # Utility functions
│   └── tests/             # Test suite
├── alembic/               # Database migrations
├── scripts/               # Utility scripts
└── requirements.txt       # Python dependencies
```

## Setup Instructions

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 15 or higher
- Redis 5.0 or higher

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd service-marketplace-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   ```bash
   # On Windows
   venv\Scripts\activate
   
   # On Mac/Linux
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

5. **Set up environment variables**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your database, Redis, and email settings
   ```

6. **Set up PostgreSQL database**
   ```bash
   # Create database
   createdb service_marketplace
   ```

7. **Initialize Alembic and run migrations**
   ```bash
   alembic upgrade head
   ```
   
   **Note**: The database uses UUIDs for all primary keys. See `UUID_MIGRATION_GUIDE.md` for details.

8. **Run the development server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

The API will be available at `http://localhost:8000`

API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Production Deployment (AWS EC2 with PM2)

### Prerequisites
- AWS EC2 instance (Ubuntu 22.04 LTS recommended)
- Domain name (optional, for SSL)
- SSH access to the server

### Deployment Steps

1. **Prepare EC2 instance**
   ```bash
   # SSH into your EC2 instance
   ssh ubuntu@your-ec2-ip
   
   # Run the server setup script
   sudo bash setup-server.sh
   ```
   
   This script installs:
   - Python 3.11
   - PostgreSQL 15
   - Redis
   - Node.js & PM2
   - Nginx
   - Certbot (SSL)
   - UV (fast package manager)

2. **Copy application files**
   ```bash
   # From your local machine
   scp -r /path/to/leadflow ubuntu@your-ec2-ip:/opt/leadflow
   
   # Or clone from git
   cd /opt/leadflow
   git clone your-repo-url .
   ```

3. **Configure environment**
   ```bash
   cd /opt/leadflow
   cp .env.production.example .env.production
   nano .env.production  # Edit with your actual values
   ```

4. **Deploy the application**
   ```bash
   sudo bash deployment/deploy.sh
   ```
   
   This script will:
   - Create Python virtual environment
   - Install dependencies with UV
   - Run database migrations
   - Configure Nginx
   - Start application with PM2
   - Set up auto-restart on reboot

5. **Configure SSL (optional but recommended)**
   ```bash
   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
   ```

### PM2 Management Commands

```bash
# View application logs
pm2 logs leadflow-api

# Monitor application
pm2 monit

# Restart application
pm2 restart leadflow-api

# Stop application
pm2 stop leadflow-api

# View status
pm2 status

# View detailed info
pm2 info leadflow-api

# Save PM2 process list (auto-restart on reboot)
pm2 save

# View PM2 startup script
pm2 startup
```

### Database Management

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Connect to application database
sudo -u postgres psql -d service_marketplace

# Create database backup
pg_dump -U leadflow -h localhost service_marketplace | gzip > backup.sql.gz

# Restore database
gunzip < backup.sql.gz | psql -U leadflow -h localhost service_marketplace
```

### Troubleshooting

```bash
# Check application logs
pm2 logs leadflow-api --lines 100

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-15-main.log

# Check Redis status
redis-cli ping

# Restart services
sudo systemctl restart postgresql
sudo systemctl restart redis-server
sudo systemctl restart nginx
pm2 restart leadflow-api

# Check service status
sudo systemctl status postgresql
sudo systemctl status redis-server
sudo systemctl status nginx
pm2 status
```

## Environment Variables

See `.env.example` for all required environment variables. Key variables include:

- `ENVIRONMENT`: `local` or `production`
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: JWT secret key (generate with `openssl rand -hex 32`)
- `SMTP_*`: Email configuration for OTP delivery

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest app/tests/test_auth.py
```

## Code Quality

```bash
# Format code with Black
black app/ --line-length 100

# Check types with mypy
mypy app/

# Lint with flake8
flake8 app/
```

## API Endpoints

### Authentication (REST)

- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/send-otp` - Send OTP to email
- `POST /api/v1/auth/verify-otp` - Verify OTP and activate account
- `POST /api/v1/auth/login` - Login with email/password
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/forgot-password` - Request password reset
- `POST /api/v1/auth/reset-password` - Reset password with OTP
- `POST /api/v1/auth/logout` - Logout user

## Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Check current migration status
alembic current

# View migration history
alembic history
```

**Important**: This project uses UUIDs for all primary keys. See `UUID_MIGRATION_GUIDE.md` for migration details and API response format changes.

## Security Notes

- Never commit `.env` files to version control
- Use strong `SECRET_KEY` in production (generate with `openssl rand -hex 32`)
- For Gmail SMTP, use App Passwords, not your regular password
- Ensure PostgreSQL and Redis are properly secured in production

## Development

This project follows strict layered architecture:
- **API Layer**: Handles HTTP concerns only
- **Service Layer**: Contains all business logic
- **Repository Layer**: Handles all database operations
- **Model Layer**: Database schema definitions only

## License

[Add your license here]

## Support

[Add support information here]

