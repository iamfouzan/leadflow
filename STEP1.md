# FastAPI Service Marketplace Platform - Backend Setup & Authentication

## Project Overview
Building a production-grade FastAPI backend for a dual-app service marketplace platform connecting Potential Customers with Business Owners. The system requires robust authentication, real-time communication capabilities, and scalable architecture supporting both REST and GraphQL APIs.

## Phase 1: Complete Project Setup & Authentication System

### Objectives
1. Create professional, industry-grade folder structure following best practices
2. Implement complete authentication system for both Customer and Business Owner apps
3. Set up PostgreSQL database with proper migrations
4. Configure environment-based settings (local/production)
5. Implement JWT-based authentication with OTP verification (email-based)

---

## Technical Stack

### Core Framework
- **FastAPI** (latest stable version)
- **Python 3.11+**
- **PostgreSQL 15+** as primary database
- **SQLAlchemy 2.0+** for ORM
- **Alembic** for database migrations

### API Technologies
- **REST API**: FastAPI native endpoints (for real-time operations, simple CRUD)
- **GraphQL**: Strawberry GraphQL (for complex queries, nested data fetching, customer/business profile queries)

### Authentication & Security
- **JWT tokens** (access + refresh token pattern)
- **Passlib + Bcrypt** for password hashing
- **Python built-in SMTP** for OTP email delivery
- **Redis** for OTP storage and session management

### Additional Libraries
- **Pydantic v2** for data validation
- **Python-multipart** for file uploads
- **Python-jose** for JWT
- **Redis** for caching and OTP storage
- **CORS middleware** for cross-origin requests

---

## Folder Structure

```
service-marketplace-backend/
│
├── app/
│   ├── __init__.py
│   │
│   ├── main.py                          # Application entry point
│   ├── config.py                        # Environment configuration management
│   │
│   ├── core/                            # Core functionality
│   │   ├── __init__.py
│   │   ├── security.py                  # JWT, password hashing, token management
│   │   ├── dependencies.py              # Dependency injection functions
│   │   ├── exceptions.py                # Custom exception handlers
│   │   └── middleware.py                # Custom middleware (logging, timing, etc.)
│   │
│   ├── db/                              # Database
│   │   ├── __init__.py
│   │   ├── base.py                      # Base class for models
│   │   ├── session.py                   # Database session management
│   │   └── init_db.py                   # Database initialization
│   │
│   ├── models/                          # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py                      # User base model
│   │   ├── customer.py                  # Potential Customer model
│   │   ├── business.py                  # Business Owner model
│   │   ├── otp.py                       # OTP storage model
│   │   ├── conversation.py              # Chat conversations
│   │   ├── message.py                   # Chat messages
│   │   ├── lead.py                      # Lead management
│   │   └── review.py                    # Reviews and ratings
│   │
│   ├── schemas/                         # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── auth.py                      # Authentication schemas
│   │   ├── user.py                      # User schemas
│   │   ├── customer.py                  # Customer schemas
│   │   ├── business.py                  # Business schemas
│   │   ├── token.py                     # Token schemas
│   │   └── response.py                  # Standard response schemas
│   │
│   ├── api/                             # API routes
│   │   ├── __init__.py
│   │   ├── deps.py                      # API dependencies
│   │   │
│   │   ├── v1/                          # API version 1
│   │   │   ├── __init__.py
│   │   │   ├── router.py                # Main v1 router
│   │   │   │
│   │   │   ├── endpoints/               # REST endpoints
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py              # Authentication endpoints
│   │   │   │   ├── customers.py         # Customer endpoints
│   │   │   │   ├── businesses.py        # Business endpoints
│   │   │   │   ├── search.py            # Search endpoints
│   │   │   │   ├── chat.py              # Chat endpoints
│   │   │   │   └── leads.py             # Lead management endpoints
│   │   │   │
│   │   │   └── graphql/                 # GraphQL
│   │   │       ├── __init__.py
│   │   │       ├── schema.py            # GraphQL schema definition
│   │   │       ├── queries.py           # GraphQL queries
│   │   │       ├── mutations.py         # GraphQL mutations
│   │   │       └── types.py             # GraphQL types
│   │
│   ├── services/                        # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py              # Authentication business logic
│   │   ├── otp_service.py               # OTP generation and validation
│   │   ├── email_service.py             # Email sending service
│   │   ├── customer_service.py          # Customer operations
│   │   ├── business_service.py          # Business operations
│   │   ├── search_service.py            # Search and matching logic
│   │   ├── chat_service.py              # Chat operations
│   │   └── lead_service.py              # Lead management
│   │
│   ├── repositories/                    # Data access layer
│   │   ├── __init__.py
│   │   ├── base.py                      # Base repository with common methods
│   │   ├── user_repository.py           # User data access
│   │   ├── customer_repository.py       # Customer data access
│   │   ├── business_repository.py       # Business data access
│   │   ├── otp_repository.py            # OTP data access
│   │   └── chat_repository.py           # Chat data access
│   │
│   ├── utils/                           # Utility functions
│   │   ├── __init__.py
│   │   ├── email.py                     # Email utilities
│   │   ├── validators.py                # Custom validators
│   │   ├── helpers.py                   # Helper functions
│   │   └── constants.py                 # Application constants
│   │
│   └── tests/                           # Test suite
│       ├── __init__.py
│       ├── conftest.py                  # Pytest configuration
│       ├── test_auth.py                 # Authentication tests
│       ├── test_customers.py            # Customer tests
│       └── test_businesses.py           # Business tests
│
├── alembic/                             # Database migrations
│   ├── versions/                        # Migration versions
│   ├── env.py                           # Alembic environment
│   └── script.py.mako                   # Migration template
│
├── scripts/                             # Utility scripts
│   ├── init_db.py                       # Database initialization script
│   └── seed_data.py                     # Sample data seeding
│
├── .env.example                         # Example environment variables
├── .env.local                           # Local environment (gitignored)
├── .env.production                      # Production environment (gitignored)
├── .gitignore                           # Git ignore file
├── alembic.ini                          # Alembic configuration
├── requirements.txt                     # Python dependencies
├── requirements-dev.txt                 # Development dependencies
├── pytest.ini                           # Pytest configuration
├── README.md                            # Project documentation
└── setup.py                             # Package setup file
```

---

## Requirements Files

### requirements.txt
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
email-validator==2.1.0
redis==5.0.1
strawberry-graphql[fastapi]==0.215.0
python-dotenv==1.0.0
```

### requirements-dev.txt
```txt
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.2
black==23.12.0
flake8==6.1.0
mypy==1.7.1
pre-commit==3.5.0
```

---

## Environment Configuration

### .env.example
```env
# Application Environment
ENVIRONMENT=local  # local or production

# Application Settings
APP_NAME="Service Marketplace API"
APP_VERSION="1.0.0"
DEBUG=true
API_V1_PREFIX="/api/v1"

# Server Settings
HOST=0.0.0.0
PORT=8000

# Database Settings
DATABASE_URL=postgresql://user:password@localhost:5432/service_marketplace
DB_ECHO=true  # Set to false in production

# Redis Settings
REDIS_URL=redis://localhost:6379/0
REDIS_OTP_DB=1  # Separate DB for OTP storage

# JWT Settings
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# OTP Settings
OTP_LENGTH=6
OTP_EXPIRY_MINUTES=10
OTP_MAX_ATTEMPTS=3

# Email Settings (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@servicemarketplace.com
SMTP_FROM_NAME="Service Marketplace"

# CORS Settings
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8081"]

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# File Upload
MAX_UPLOAD_SIZE=5242880  # 5MB in bytes
ALLOWED_EXTENSIONS=["jpg", "jpeg", "png", "pdf"]

# Pagination
DEFAULT_PAGE_SIZE=10
MAX_PAGE_SIZE=100
```

---

## Core Implementation Details

### Authentication Flow

#### REST API Endpoints (Use REST for Authentication)
**Why REST for Auth?** Authentication operations are simple, atomic, and stateless - perfect for REST.

1. **POST /api/v1/auth/register** - Register new user (Customer or Business Owner)
2. **POST /api/v1/auth/send-otp** - Send OTP to email
3. **POST /api/v1/auth/verify-otp** - Verify OTP and activate account
4. **POST /api/v1/auth/login** - Login with email/password
5. **POST /api/v1/auth/refresh** - Refresh access token
6. **POST /api/v1/auth/forgot-password** - Request password reset
7. **POST /api/v1/auth/reset-password** - Reset password with OTP
8. **POST /api/v1/auth/logout** - Logout user

### Database Models

#### User Types
- **UserType Enum**: `CUSTOMER`, `BUSINESS_OWNER`
- **UserStatus Enum**: `PENDING`, `ACTIVE`, `SUSPENDED`, `DELETED`

#### Core Authentication Tables
1. **users** - Base user table with common fields
2. **customers** - Customer-specific data (extends users)
3. **businesses** - Business-specific data (extends users)
4. **otps** - OTP storage with expiry and attempt tracking
5. **refresh_tokens** - Refresh token management

### OTP Implementation Strategy

**Storage**: Redis (fast, auto-expiry) with PostgreSQL backup
**Generation**: Cryptographically secure random 6-digit code
**Validation**: Time-based expiry + attempt limiting
**Email**: Python SMTP (no third-party services)

#### OTP Workflow
1. User requests OTP → Generate 6-digit code
2. Store in Redis with 10-minute TTL
3. Store in PostgreSQL for audit trail
4. Send via SMTP email
5. User submits OTP → Validate from Redis
6. Track failed attempts (max 3)
7. Delete OTP after successful verification

### JWT Token Strategy

**Two-Token Pattern**:
- **Access Token**: Short-lived (30 minutes), used for API requests
- **Refresh Token**: Long-lived (7 days), used to get new access tokens

**Token Payload**:
```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "user_type": "CUSTOMER",
  "exp": 1234567890,
  "iat": 1234567890,
  "jti": "unique_token_id"
}
```

### Security Features

1. **Password Hashing**: Bcrypt with salt
2. **Token Blacklisting**: Redis-based for logout
3. **Rate Limiting**: Per-IP and per-user
4. **CORS Configuration**: Environment-based origins
5. **SQL Injection Prevention**: SQLAlchemy ORM + parameterized queries
6. **XSS Protection**: Pydantic validation + sanitization
7. **Environment Isolation**: Separate configs for local/production

---

## Configuration Management

### Environment-Based Settings (config.py)

```python
# Key Features:
- Pydantic Settings for type-safe configuration
- Automatic environment detection (local/production)
- Validation of required environment variables
- Different settings for different environments
- Database connection pooling configuration
- Redis connection settings
- Email configuration with validation
- JWT settings with secure defaults
```

### Local vs Production Differences

**Local Environment**:
- Debug mode enabled
- Database query logging
- Verbose error messages
- CORS allows localhost origins
- Shorter token expiry for testing
- Console email backend (optional)

**Production Environment**:
- Debug mode disabled
- No query logging
- Generic error messages
- Strict CORS configuration
- Standard token expiry
- Real SMTP email backend
- Database connection pooling optimized
- Redis connection pooling

---

## Database Design

### Key Relationships

```
users (base table)
  ├── customers (one-to-one)
  │   └── search_history
  │   └── conversations
  │   └── reviews
  │
  └── businesses (one-to-one)
      ├── services
      ├── business_hours
      ├── conversations
      ├── leads
      └── subscription

otps (standalone with user_id foreign key)
refresh_tokens (standalone with user_id foreign key)
```

### Indexes for Performance

- Email (unique, indexed)
- Phone (unique, indexed)
- User type (indexed)
- Business location (PostGIS spatial index)
- OTP expiry (indexed for cleanup)
- Token expiry (indexed for cleanup)

---

## API Design Decisions

### When to Use REST vs GraphQL

**REST APIs** (use for):
✅ Authentication (simple, atomic operations)
✅ Real-time chat (WebSocket connections)
✅ File uploads
✅ Simple CRUD operations
✅ Operations requiring specific HTTP methods (POST, PUT, DELETE)
✅ Webhooks and callbacks
✅ Health checks and monitoring

**GraphQL APIs** (use for):
✅ Complex nested queries (business profile with reviews, services, ratings)
✅ Customer searching with filtering (fetch only needed fields)
✅ Dashboard data aggregation
✅ Profile fetching with related data
✅ Analytics queries with multiple data sources
✅ Mobile app data fetching (reduce over-fetching)

### Example Implementation Split

**REST**:
- `/api/v1/auth/*` - All authentication endpoints
- `/api/v1/upload/*` - File upload endpoints
- `/api/v1/ws/*` - WebSocket endpoints for chat

**GraphQL**:
- `/graphql` - Single endpoint for:
  - Business search and filtering
  - Profile queries with nested data
  - Dashboard analytics
  - Review and rating queries

---

## Implementation Instructions for Cursor

### Step 1: Initial Setup
1. Create project directory structure as specified above
2. Set up virtual environment: `python -m venv venv`
3. Install dependencies from requirements.txt
4. Create .env.local file from .env.example template
5. Initialize Git repository with .gitignore

### Step 2: Core Configuration
1. Implement `app/config.py` with environment-based settings using Pydantic Settings
2. Create database session management in `app/db/session.py`
3. Set up base model class in `app/db/base.py`
4. Configure Alembic for database migrations

### Step 3: Security & Authentication Core
1. Implement password hashing utilities in `app/core/security.py`
2. Create JWT token generation and validation functions
3. Set up Redis connection for OTP and session management
4. Implement OTP generation logic in `app/services/otp_service.py`
5. Create email service with SMTP integration in `app/services/email_service.py`

### Step 4: Database Models
1. Create base User model with common fields (id, email, password_hash, user_type, status, timestamps)
2. Create Customer model extending User
3. Create Business model extending User
4. Create OTP model with expiry and attempt tracking
5. Create RefreshToken model for token management
6. Generate initial Alembic migration

### Step 5: Pydantic Schemas
1. Create authentication schemas (RegisterRequest, LoginRequest, OTPRequest, TokenResponse)
2. Create user schemas (UserBase, UserCreate, UserResponse)
3. Create customer and business schemas
4. Create standard response schemas for consistent API responses

### Step 6: Repository Layer
1. Implement base repository with common CRUD operations
2. Create user repository with email lookup methods
3. Create OTP repository with validation methods
4. Create customer and business repositories

### Step 7: Service Layer
1. Implement auth_service.py with registration, login, logout logic
2. Implement otp_service.py with generation, validation, cleanup
3. Implement email_service.py with template rendering
4. Create user service for profile management

### Step 8: API Endpoints (REST)
1. Create authentication endpoints in `app/api/v1/endpoints/auth.py`:
   - POST /register (customer and business owner)
   - POST /send-otp
   - POST /verify-otp
   - POST /login
   - POST /refresh
   - POST /forgot-password
   - POST /reset-password
   - POST /logout
2. Implement dependency functions for JWT validation
3. Add rate limiting middleware
4. Implement error handlers

### Step 9: Main Application
1. Create FastAPI application instance in `app/main.py`
2. Configure CORS middleware
3. Include API routers
4. Add exception handlers
5. Set up startup and shutdown events
6. Configure logging

### Step 10: Testing & Documentation
1. Write pytest tests for authentication flow
2. Create test fixtures for database and users
3. Test OTP generation and validation
4. Test JWT token flow
5. Verify environment switching (local/production)

---

## Code Quality Standards

### Type Hints
- Use Python type hints throughout
- Validate with mypy

### Code Formatting
- Use Black for code formatting
- Configure line length: 100 characters
- Use isort for import sorting

### Documentation
- Docstrings for all functions (Google style)
- OpenAPI documentation via FastAPI
- README with setup instructions

### Error Handling
- Custom exception classes
- Consistent error response format
- Proper HTTP status codes
- Environment-aware error messages (detailed in local, generic in production)

### Security Best Practices
- Never log sensitive data (passwords, tokens)
- Use environment variables for secrets
- Implement rate limiting
- Validate all inputs with Pydantic
- Sanitize error messages in production

---

## Testing Strategy

### Unit Tests
- Test individual functions in isolation
- Mock external dependencies (email, Redis)
- Test edge cases and error conditions

### Integration Tests
- Test API endpoints end-to-end
- Test database operations
- Test authentication flow

### Test Coverage
- Aim for 80%+ code coverage
- Focus on critical paths (authentication, data validation)

---

## Email Template for OTP

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .otp-code { font-size: 32px; font-weight: bold; color: #007bff; text-align: center; padding: 20px; background: #f8f9fa; border-radius: 8px; }
        .footer { margin-top: 30px; font-size: 12px; color: #6c757d; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Verify Your Email</h2>
        <p>Your verification code is:</p>
        <div class="otp-code">{{ otp_code }}</div>
        <p>This code will expire in {{ expiry_minutes }} minutes.</p>
        <p>If you didn't request this code, please ignore this email.</p>
        <div class="footer">
            <p>Service Marketplace Platform</p>
        </div>
    </div>
</body>
</html>
```

---

## Next Steps After Phase 1

Once authentication is complete and tested, Phase 2 will cover:
- GraphQL schema setup for complex queries
- Business search and matching algorithm
- Real-time chat with WebSocket
- Lead management system
- File upload and storage
- Notification system

---

## Success Criteria for Phase 1

✅ Virtual environment set up with all dependencies installed
✅ Professional folder structure created
✅ PostgreSQL database connected and migrations working
✅ Redis connected for OTP storage
✅ Complete authentication flow working:
   - Customer registration
   - Business owner registration
   - OTP email sending
   - OTP verification
   - Login with JWT tokens
   - Token refresh
   - Password reset
✅ Environment switching (local/production) working correctly
✅ All authentication endpoints tested
✅ Code follows quality standards (type hints, formatting, documentation)
✅ Basic tests passing

---

## Important Notes

1. **Database Connection**: Ensure PostgreSQL is installed and running locally
2. **Redis Setup**: Install and start Redis server locally
3. **Email Testing**: For local development, consider using a fake SMTP server or MailHog for testing emails
4. **Environment Variables**: Never commit .env files to Git
5. **Password Security**: Use strong SECRET_KEY in production (generate with `openssl rand -hex 32`)
6. **SMTP Credentials**: For Gmail, use App Passwords, not your regular password

---

## Commands to Run

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Initialize database
alembic init alembic

# Create first migration
alembic revision --autogenerate -m "Initial migration"

# Run migrations
alembic upgrade head

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest

# Format code
black app/

# Check types
mypy app/
```

---

This specification provides everything needed to build a production-grade authentication system for your service marketplace platform. The structure is scalable, maintainable, and follows industry best practices.