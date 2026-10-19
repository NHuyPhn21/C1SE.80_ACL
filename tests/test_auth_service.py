"""Contract tests for the authentication HTTP adapter."""

import os
import unittest
from unittest.mock import Mock, patch

import requests

from models.auth import AuthResult, AuthTokens
from services.auth_service import (
    AuthApiConfig,
    AuthServiceError,
    HttpAuthService,
)


def _response(status: int, payload: object | None = None) -> Mock:
    response = Mock(spec=requests.Response)
    response.ok = 200 <= status < 300
    response.status_code = status
    response.content = b"" if payload is None else b"json"
    response.json.return_value = payload
    return response


class AuthModelTests(unittest.TestCase):
    def test_auth_result_accepts_wrapped_user_and_flat_tokens(self) -> None:
        result = AuthResult.from_mapping(
            {
                "data": {
                    "user": {"id": 7, "email": "editor@example.com", "name": "Editor"},
                    "accessToken": "access",
                    "refreshToken": "refresh",
                    "expiresIn": 900,
                }
            }
        )

        self.assertEqual(result.user.id, "7")
        self.assertEqual(result.tokens.access_token, "access")
        self.assertEqual(result.tokens.expires_in, 900)

    def test_tokens_accept_token_alias(self) -> None:
        tokens = AuthTokens.from_mapping({"token": "jwt"})
        self.assertEqual(tokens.access_token, "jwt")


class HttpAuthServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = Mock(spec=requests.Session)
        self.service = HttpAuthService(
            AuthApiConfig(
                base_url="http://api.example.test/v1",
                timeout=3,
                register_name_field="full_name",
            ),
            client=self.client,
        )

    def test_login_posts_credentials_and_parses_result(self) -> None:
        self.client.request.return_value = _response(
            200,
            {
                "data": {
                    "user": {"id": "u1", "email": "user@example.com"},
                    "tokens": {
                        "access_token": "access",
                        "refresh_token": "refresh",
                        "expires_in": 3600,
                    },
                }
            },
        )

        result = self.service.login("user@example.com", "password", True)

        self.assertEqual(result.tokens.access_token, "access")
        self.client.request.assert_called_once_with(
            "POST",
            "http://api.example.test/v1/auth/login",
            json={
                "email": "user@example.com",
                "password": "password",
                "remember_me": True,
            },
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            timeout=3,
        )

    def test_logout_accepts_empty_success_response(self) -> None:
        self.client.request.return_value = _response(204)

        self.service.logout("access")

        headers = self.client.request.call_args.kwargs["headers"]
        self.assertEqual(headers["Authorization"], "Bearer access")

    def test_register_posts_frontend_fields(self) -> None:
        self.client.request.return_value = _response(
            201,
            {
                "user": {"id": "u2", "email": "new@example.com"},
                "access_token": "access",
            },
        )

        result = self.service.register("New User", "new@example.com", "password")

        self.assertEqual(result.user.full_name, "new")
        self.assertEqual(
            self.client.request.call_args.kwargs["json"],
            {
                "full_name": "New User",
                "email": "new@example.com",
                "password": "password",
            },
        )

    def test_refresh_parses_flat_token_response(self) -> None:
        self.client.request.return_value = _response(
            200, {"access_token": "new-access", "expires_in": 1800}
        )

        tokens = self.service.refresh("refresh")

        self.assertEqual(tokens.access_token, "new-access")
        self.assertIsNone(tokens.refresh_token)
        self.assertEqual(
            self.client.request.call_args.kwargs["json"],
            {"refresh_token": "refresh"},
        )

    def test_fastapi_validation_errors_are_user_readable(self) -> None:
        self.client.request.return_value = _response(
            422, {"detail": [{"msg": "invalid email"}, {"msg": "password too short"}]}
        )

        with self.assertRaisesRegex(
            AuthServiceError, "invalid email; password too short"
        ):
            self.service.login("bad", "short", False)

    def test_network_failure_uses_safe_message(self) -> None:
        self.client.request.side_effect = requests.Timeout("timed out")

        with self.assertRaisesRegex(AuthServiceError, "service is unavailable"):
            self.service.login("user@example.com", "password", False)


class AuthApiConfigTests(unittest.TestCase):
    @patch.dict(
        os.environ,
        {
            "AUTH_API_BASE_URL": "http://localhost:8000/api/",
            "AUTH_LOGIN_PATH": "v1/login",
            "AUTH_API_TIMEOUT": "5.5",
        },
        clear=True,
    )
    def test_environment_configuration(self) -> None:
        config = AuthApiConfig.from_environment()

        self.assertEqual(config.base_url, "http://localhost:8000/api")
        self.assertEqual(config.login_path, "/v1/login")
        self.assertEqual(config.timeout, 5.5)
        self.assertEqual(config.login_identifier_field, "email")
        self.assertEqual(config.register_name_field, "username")


if __name__ == "__main__":
    unittest.main()
