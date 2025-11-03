"""Email template utilities."""
from typing import Dict


def get_otp_email_template(otp_code: str, expiry_minutes: int = 10) -> str:
    """
    Get OTP email HTML template.

    Args:
        otp_code: 6-digit OTP code
        expiry_minutes: OTP expiry in minutes

    Returns:
        HTML email template string
    """
    html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .otp-code {{ font-size: 32px; font-weight: bold; color: #007bff; text-align: center; padding: 20px; background: #f8f9fa; border-radius: 8px; }}
        .footer {{ margin-top: 30px; font-size: 12px; color: #6c757d; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Verify Your Email</h2>
        <p>Your verification code is:</p>
        <div class="otp-code">{otp_code}</div>
        <p>This code will expire in {expiry_minutes} minutes.</p>
        <p>If you didn't request this code, please ignore this email.</p>
        <div class="footer">
            <p>Service Marketplace Platform</p>
        </div>
    </div>
</body>
</html>
"""
    return html_template

