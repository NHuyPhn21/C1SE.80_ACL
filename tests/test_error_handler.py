"""Tests for normalized frontend API errors."""

import unittest
from unittest.mock import Mock

import requests

from models.api_error import ApiErrorCode
from services.error_handler import from_exception, from_http_response, parse_retry_after


def _response(
    status: int, payload: object, headers: dict[str, str] | None = None
) -> Mock:
    response = Mock(spec=requests.Response)
    response.status_code = status
    response.headers = headers or {}
    response.json.return_value = payload
    return response


class ErrorHandlerTests(unittest.TestCase):
    def test_rate_limit_includes_retry_after(self) -> None:
        error = from_http_response(
            _response(
                429,
                {"error": {"message": "Daily quota exceeded"}},
                {"Retry-After": "120"},
            )
        )

        self.assertEqual(error.code, ApiErrorCode.RATE_LIMITED)
        self.assertEqual(error.message, "Daily quota exceeded")
        self.assertEqual(error.retry_after, 120)
        self.assertTrue(error.retryable)

    def test_validation_fields_are_extracted(self) -> None:
        error = from_http_response(
            _response(
                422,
                {"detail": [{"loc": ["body", "email"], "msg": "invalid email"}]},
            )
        )

        self.assertEqual(error.code, ApiErrorCode.VALIDATION)
        self.assertEqual(error.field_errors, {"email": "invalid email"})

    def test_timeout_is_retryable(self) -> None:
        error = from_exception(requests.Timeout())
        self.assertEqual(error.code, ApiErrorCode.TIMEOUT)
        self.assertTrue(error.retryable)

    def test_invalid_retry_after_is_ignored(self) -> None:
        self.assertIsNone(parse_retry_after("not-a-date"))


if __name__ == "__main__":
    unittest.main()
