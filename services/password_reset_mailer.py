"""Optional SendGrid delivery for password-reset links."""

from __future__ import annotations

import os

import requests


def send_password_reset_email(email: str, reset_link: str) -> bool:
    """Send a reset email when SendGrid is configured; return False in local mode."""
    api_key = os.getenv("SENDGRID_API_KEY", "").strip()
    sender = os.getenv("SENDGRID_FROM_EMAIL", "").strip()
    if not api_key or not sender:
        return False

    try:
        response = requests.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "personalizations": [{"to": [{"email": email}]}],
                "from": {"email": sender, "name": "ACL Studio"},
                "subject": "Reset your ACL Studio password",
                "content": [
                    {
                        "type": "text/plain",
                        "value": (
                            "Use this single-use link to reset your ACL Studio password. "
                            f"The link expires in 15 minutes:\n\n{reset_link}"
                        ),
                    },
                    {
                        "type": "text/html",
                        "value": (
                            "<p>Use this single-use link to reset your ACL Studio "
                            "password. It expires in 15 minutes.</p>"
                            f'<p><a href="{reset_link}">Reset password</a></p>'
                        ),
                    },
                ],
            },
            timeout=10,
        )
    except requests.RequestException:
        return False
    return response.status_code == 202
