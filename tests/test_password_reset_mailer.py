import os
import unittest
from unittest.mock import Mock, patch

import requests

from services.password_reset_mailer import (
    PasswordResetDeliveryError,
    send_password_reset_email,
)


class PasswordResetMailerTests(unittest.TestCase):
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_sendgrid_configuration_is_an_error(self) -> None:
        with self.assertRaisesRegex(PasswordResetDeliveryError, "not configured"):
            send_password_reset_email(
                "user@example.com", "https://acl.example/reset?token=secret"
            )

    @patch.dict(
        os.environ,
        {
            "SENDGRID_API_KEY": "sendgrid-key",
            "SENDGRID_FROM_EMAIL": "no-reply@acl.example",
        },
        clear=True,
    )
    @patch("services.password_reset_mailer.requests.post")
    def test_sendgrid_acceptance_completes_delivery(self, post: Mock) -> None:
        post.return_value.status_code = 202

        send_password_reset_email(
            "user@example.com", "https://acl.example/reset?token=secret"
        )

        payload = post.call_args.kwargs["json"]
        self.assertEqual(payload["personalizations"][0]["to"][0]["email"], "user@example.com")
        self.assertIn("https://acl.example/reset?token=secret", payload["content"][0]["value"])

    @patch.dict(
        os.environ,
        {
            "SENDGRID_API_KEY": "sendgrid-key",
            "SENDGRID_FROM_EMAIL": "no-reply@acl.example",
        },
        clear=True,
    )
    @patch("services.password_reset_mailer.requests.post")
    def test_sendgrid_failure_is_reported(self, post: Mock) -> None:
        post.side_effect = requests.Timeout("timeout")

        with self.assertRaisesRegex(PasswordResetDeliveryError, "could not be sent"):
            send_password_reset_email(
                "user@example.com", "https://acl.example/reset?token=secret"
            )


if __name__ == "__main__":
    unittest.main()
