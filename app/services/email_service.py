"""Email sending service with SMTP integration."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging

from app.config import settings
from app.utils.email import get_otp_email_template
from app.core.exceptions import ValidationException

logger = logging.getLogger(__name__)


class EmailService:
    """Email service for sending emails via SMTP."""

    def __init__(self):
        """Initialize email service."""
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL
        self.from_name = settings.SMTP_FROM_NAME

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """
        Send email via SMTP.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email content
            text_content: Plain text email content (optional)

        Returns:
            True if email sent successfully, False otherwise

        Raises:
            ValidationException: If email sending fails
        """
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email

            # Add text content if provided
            if text_content:
                text_part = MIMEText(text_content, "plain")
                msg.attach(text_part)

            # Add HTML content
            html_part = MIMEText(html_content, "html")
            msg.attach(html_part)

            # Connect to SMTP server and send
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            if settings.is_local:
                # In local environment, log error but don't fail
                logger.warning(f"Email sending failed in local environment: {str(e)}")
                return False
            raise ValidationException(f"Failed to send email: {str(e)}")

    def send_otp_email(self, to_email: str, otp_code: str) -> bool:
        """
        Send OTP verification email.

        Args:
            to_email: Recipient email address
            otp_code: 6-digit OTP code

        Returns:
            True if email sent successfully, False otherwise
        """
        subject = "Email Verification - Service Marketplace"
        html_content = get_otp_email_template(otp_code, settings.OTP_EXPIRY_MINUTES)
        text_content = f"Your verification code is: {otp_code}. This code will expire in {settings.OTP_EXPIRY_MINUTES} minutes."

        return self.send_email(to_email, subject, html_content, text_content)

    def send_password_reset_email(self, to_email: str, otp_code: str) -> bool:
        """
        Send password reset OTP email.

        Args:
            to_email: Recipient email address
            otp_code: 6-digit OTP code

        Returns:
            True if email sent successfully, False otherwise
        """
        subject = "Password Reset - Service Marketplace"
        html_content = get_otp_email_template(otp_code, settings.OTP_EXPIRY_MINUTES)
        html_content = html_content.replace("Verify Your Email", "Reset Your Password")
        html_content = html_content.replace("verification code", "password reset code")
        text_content = f"Your password reset code is: {otp_code}. This code will expire in {settings.OTP_EXPIRY_MINUTES} minutes."

        return self.send_email(to_email, subject, html_content, text_content)


# Global email service instance
email_service = EmailService()

