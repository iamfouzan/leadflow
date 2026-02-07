"""Authentication flow tests."""
import pytest
from fastapi import status
from unittest.mock import patch, MagicMock

from app.models.user import UserType
from app.core.security import create_access_token


class TestRegistration:
    """Test user registration."""

    def test_register_customer_success(self, client, db):
        """Test successful customer registration."""
        payload = {
            "email": "newcustomer@example.com",
            "password": "SecurePass123",
            "full_name": "New Customer",
            "user_type": "CUSTOMER",
        }
        response = client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["success"] is True
        assert data["data"]["email"] == payload["email"]
        assert data["data"]["user_type"] == "CUSTOMER"
        assert "password" not in data["data"]

    def test_register_business_owner_success(self, client, db):
        """Test successful business owner registration."""
        payload = {
            "email": "business@example.com",
            "password": "SecurePass123",
            "full_name": "Business Owner",
            "user_type": "BUSINESS_OWNER",
        }
        response = client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["success"] is True
        assert data["data"]["email"] == payload["email"]
        assert data["data"]["user_type"] == "BUSINESS_OWNER"

    def test_register_duplicate_email(self, client, test_user):
        """Test registration with existing email."""
        payload = {
            "email": test_user.email,
            "password": "SecurePass123",
            "full_name": "Duplicate User",
            "user_type": "CUSTOMER",
        }
        response = client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["success"] is False


class TestOTP:
    """Test OTP generation and verification."""

    @patch("app.services.email_service.EmailService.send_otp_email")
    @patch("app.services.otp_service.OTPService.create_and_send_otp")
    def test_send_otp_success(self, mock_create_otp, mock_send_email, client, test_user):
        """Test successful OTP sending."""
        mock_create_otp.return_value = "123456"
        mock_send_email.return_value = True

        payload = {"email": test_user.email}
        response = client.post("/api/v1/auth/send-otp", json=payload)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True

    def test_send_otp_user_not_found(self, client, db):
        """Test sending OTP to non-existent user."""
        payload = {"email": "nonexistent@example.com"}
        response = client.post("/api/v1/auth/send-otp", json=payload)

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestLogin:
    """Test user login."""

    def test_login_success(self, client, test_user):
        """Test successful login."""
        payload = {
            "email": test_user.email,
            "password": "testpass123",
        }
        response = client.post("/api/v1/auth/login", json=payload)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_user):
        """Test login with incorrect password."""
        payload = {
            "email": test_user.email,
            "password": "wrongpassword",
        }
        response = client.post("/api/v1/auth/login", json=payload)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["success"] is False

    def test_login_user_not_found(self, client, db):
        """Test login with non-existent user."""
        payload = {
            "email": "nonexistent@example.com",
            "password": "testpass123",
        }
        response = client.post("/api/v1/auth/login", json=payload)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestHealthCheck:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"

