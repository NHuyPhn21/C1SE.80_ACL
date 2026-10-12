"""Load the Figma-exported authentication assets as embeddable data URIs."""

import base64
from pathlib import Path


ASSET_DIR = Path(__file__).parents[2] / "assets" / "figma"

ASSET_FILES = {
    "logo": "login-logo.svg",
    "check": "login-check.svg",
    "valid": "input-valid.svg",
    "eye": "eye.svg",
    "eye_off": "eye-off.svg",
    "arrow": "arrow.svg",
    "sso": "studio-sso.svg",
    "register_sso": "register-sso.svg",
    "cli": "cli-token.svg",
    "alert": "alert.svg",
    "register_alert": "register-alert.svg",
    "error": "register-error.svg",
    "lock": "lock.svg",
}


def _svg_data_uri(filename: str) -> str:
    encoded = base64.b64encode((ASSET_DIR / filename).read_bytes()).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def load_auth_assets() -> dict[str, str]:
    return {name: _svg_data_uri(filename) for name, filename in ASSET_FILES.items()}
