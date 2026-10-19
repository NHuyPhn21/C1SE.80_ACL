"""Tests for authentication token lifecycle in Streamlit session state."""

import unittest
from unittest.mock import patch

from models.auth import AuthTokens
from utils import auth_session


class AuthSessionTests(unittest.TestCase):
    def test_refresh_keeps_existing_rotating_token_when_omitted(self) -> None:
        state = {auth_session.REFRESH_TOKEN: "existing-refresh"}

        with patch.object(auth_session.st, "session_state", state):
            auth_session._store_tokens(
                AuthTokens(access_token="new-access", expires_in=1200)
            )

        self.assertEqual(state[auth_session.ACCESS_TOKEN], "new-access")
        self.assertEqual(state[auth_session.REFRESH_TOKEN], "existing-refresh")

    def test_refresh_replaces_rotated_refresh_token(self) -> None:
        state = {auth_session.REFRESH_TOKEN: "old-refresh"}

        with patch.object(auth_session.st, "session_state", state):
            auth_session._store_tokens(
                AuthTokens(
                    access_token="new-access",
                    refresh_token="new-refresh",
                    expires_in=1200,
                )
            )

        self.assertEqual(state[auth_session.REFRESH_TOKEN], "new-refresh")


if __name__ == "__main__":
    unittest.main()
