"""
utils/screenshot_helper.py
Handles screenshot capture on test failure (and on demand).
Screenshots are saved to settings.SCREENSHOTS_DIR with timestamped filenames.
"""

import os
import re
import time
from pathlib import Path

from selenium.webdriver.remote.webdriver import WebDriver

from src.config import settings


class ScreenshotHelper:
    """Captures and persists screenshots from a WebDriver session."""

    def __init__(self, driver: WebDriver):
        self._driver = driver
        self._dir = settings.SCREENSHOTS_DIR
        self._dir.mkdir(parents=True, exist_ok=True)

    def capture(self, name: str) -> str:
        """
        Take a screenshot and save it.

        Args:
            name: Human-readable label for the screenshot (e.g. test name).

        Returns:
            Absolute path to the saved screenshot file.
        """
        safe_name = re.sub(r"[^\w\-]", "_", name)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_name}_{timestamp}.png"
        filepath = self._dir / filename

        self._driver.save_screenshot(str(filepath))
        return str(filepath)

    def capture_on_failure(self, test_name: str) -> str | None:
        """Capture a screenshot only if SCREENSHOT_ON_FAILURE is enabled."""
        if not settings.SCREENSHOT_ON_FAILURE:
            return None
        return self.capture(f"FAIL_{test_name}")
