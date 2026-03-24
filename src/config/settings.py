"""
config/settings.py
Centralised, environment-aware configuration loader.
All values are read from environment variables (or a .env file).
Nothing is hard-coded here — callers import `settings` and access attributes.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root if it exists (ignored in CI where env vars are set directly)
_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_ROOT / ".env", override=False)


class Settings:
    """Single source of truth for all runtime configuration."""

    # ── Application ──────────────────────────────────────────────────────────
    BASE_URL: str = os.getenv("BASE_URL", "https://www.saucedemo.com")

    # ── Browser ───────────────────────────────────────────────────────────────
    BROWSER: str = os.getenv("BROWSER", "chrome").lower()
    HEADLESS: bool = os.getenv("HEADLESS", "true").lower() == "true"

    # ── Timeouts (seconds) ────────────────────────────────────────────────────
    IMPLICIT_WAIT: int = int(os.getenv("IMPLICIT_WAIT", "10"))
    EXPLICIT_WAIT: int = int(os.getenv("EXPLICIT_WAIT", "15"))
    PAGE_LOAD_TIMEOUT: int = int(os.getenv("PAGE_LOAD_TIMEOUT", "30"))

    # ── Reporting ─────────────────────────────────────────────────────────────
    SCREENSHOT_ON_FAILURE: bool = os.getenv("SCREENSHOT_ON_FAILURE", "true").lower() == "true"
    REPORTS_DIR: Path = _ROOT / "reports"
    SCREENSHOTS_DIR: Path = _ROOT / "screenshots"

    # ── Paths ─────────────────────────────────────────────────────────────────
    FIXTURES_DIR: Path = _ROOT / "src" / "fixtures"


settings = Settings()
