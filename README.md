# Service Marketplace Backend

Production-grade FastAPI backend for a dual-app service marketplace platform connecting Potential Customers with Business Owners.

## Features

- Complete authentication system for Customer and Business Owner apps
- JWT-based authentication with access and refresh tokens
- OTP verification via email (SMTP)
- PostgreSQL database with SQLAlchemy ORM
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

8. **Run the development server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

The API will be available at `http://localhost:8000`

API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

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
```

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

