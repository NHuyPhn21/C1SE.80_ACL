"""Convert transport and HTTP failures into stable frontend error states."""

from __future__ import annotations

from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from typing import Any, Mapping

import requests

from models.api_error import ApiError, ApiErrorCode


DEFAULT_MESSAGES = {
    ApiErrorCode.NETWORK: "Unable to connect to the service.",
    ApiErrorCode.TIMEOUT: "The request took too long to complete.",
    ApiErrorCode.VALIDATION: "Please check the submitted information.",
    ApiErrorCode.UNAUTHORIZED: "Your session has expired. Please sign in again.",
    ApiErrorCode.FORBIDDEN: "You do not have permission to perform this action.",
    ApiErrorCode.NOT_FOUND: "The requested resource could not be found.",
    ApiErrorCode.CONFLICT: "The request conflicts with the current resource state.",
    ApiErrorCode.RATE_LIMITED: "The API quota has been reached.",
    ApiErrorCode.SERVER: "The service is temporarily unavailable.",
    ApiErrorCode.INVALID_RESPONSE: "The service returned an invalid response.",
    ApiErrorCode.UNKNOWN: "Something went wrong. Please try again.",
}


def from_exception(exc: Exception) -> ApiError:
    if isinstance(exc, requests.Timeout):
        return _error(ApiErrorCode.TIMEOUT, retryable=True)
    if isinstance(exc, requests.ConnectionError):
        return _error(ApiErrorCode.NETWORK, retryable=True)
    if isinstance(exc, requests.RequestException):
        return _error(ApiErrorCode.NETWORK, retryable=True)
    return _error(ApiErrorCode.UNKNOWN)


def from_http_response(response: requests.Response) -> ApiError:
    payload = _json_payload(response)
    status = response.status_code
    code = _code_for_status(status)
    message = _extract_message(payload) or DEFAULT_MESSAGES[code]
    return ApiError(
        code=code,
        message=message,
        status_code=status,
        retryable=status == 429 or 500 <= status < 600,
        retry_after=parse_retry_after(response.headers.get("Retry-After")),
        field_errors=_extract_field_errors(payload),
    )


def parse_retry_after(value: str | None) -> int | None:
    if not value:
        return None
    try:
        return max(int(value), 0)
    except ValueError:
        try:
            parsed = parsedate_to_datetime(value)
        except (TypeError, ValueError, OverflowError):
            return None
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)
        return max(round((parsed - datetime.now(UTC)).total_seconds()), 0)


def _error(code: ApiErrorCode, *, retryable: bool = False) -> ApiError:
    return ApiError(code=code, message=DEFAULT_MESSAGES[code], retryable=retryable)


def _code_for_status(status: int) -> ApiErrorCode:
    if status in {400, 422}:
        return ApiErrorCode.VALIDATION
    if status == 401:
        return ApiErrorCode.UNAUTHORIZED
    if status == 403:
        return ApiErrorCode.FORBIDDEN
    if status == 404:
        return ApiErrorCode.NOT_FOUND
    if status == 409:
        return ApiErrorCode.CONFLICT
    if status == 429:
        return ApiErrorCode.RATE_LIMITED
    if 500 <= status < 600:
        return ApiErrorCode.SERVER
    return ApiErrorCode.UNKNOWN


def _json_payload(response: requests.Response) -> Mapping[str, Any]:
    try:
        payload = response.json()
    except requests.ValueError:
        return {}
    return payload if isinstance(payload, Mapping) else {}


def _extract_message(payload: Mapping[str, Any]) -> str | None:
    error = payload.get("error")
    if isinstance(error, Mapping):
        message = error.get("message") or error.get("detail")
        if message:
            return str(message)
    for key in ("message", "detail", "error"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
        if isinstance(value, list):
            messages = [
                str(item.get("msg") or item.get("message"))
                for item in value
                if isinstance(item, Mapping)
                and (item.get("msg") or item.get("message"))
            ]
            if messages:
                return "; ".join(messages)
    return None


def _extract_field_errors(payload: Mapping[str, Any]) -> dict[str, str]:
    detail = payload.get("detail")
    if not isinstance(detail, list):
        return {}
    errors: dict[str, str] = {}
    for item in detail:
        if not isinstance(item, Mapping):
            continue
        location = item.get("loc")
        message = item.get("msg")
        if isinstance(location, (list, tuple)) and message:
            errors[str(location[-1])] = str(message)
    return errors
