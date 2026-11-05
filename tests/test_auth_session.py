"""Tests for authentication token lifecycle in Streamlit session state."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from models.auth import AuthResult, AuthTokens, User
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

    def test_session_persistence_and_logout(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_session_file = Path(temp_dir) / ".auth_session.json"
            with patch.object(auth_session, "SESSION_FILE", temp_session_file):
                state: dict = {}
                with patch.object(auth_session.st, "session_state", state):
                    res = AuthResult(
                        user=User(id="99", email="test@example.com", full_name="Test User"),
                        tokens=AuthTokens(access_token="tok_123", expires_in=3600),
                    )
                    auth_session.establish_session(res, remember_me=True)
                    self.assertTrue(temp_session_file.exists())
                    self.assertTrue(state[auth_session.AUTHENTICATED])

                    # Simulate logout
                    auth_session.logout()
                    self.assertFalse(temp_session_file.exists())
                    self.assertFalse(state[auth_session.AUTHENTICATED])
                    self.assertTrue(state.get("auth.logged_out"))


if __name__ == "__main__":
    unittest.main()
