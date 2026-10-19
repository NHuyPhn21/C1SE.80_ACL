"""ACL forgot password & SendGrid recovery page."""

from features.auth import render_auth_page


render_auth_page(initial_view="forgot")
