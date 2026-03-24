"""
pages/base_page.py
Abstract base class for all Page Objects.
Provides shared navigation, element interaction, and wait methods.
Keeps all raw Selenium calls here so subclasses stay declarative.
"""

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from src.config import settings
from src.utils.wait_helper import WaitHelper
from src.utils.screenshot_helper import ScreenshotHelper


class BasePage:
    """
    Foundation class for the Page Object Model.
    All page objects inherit from this to get a consistent, DRY interaction layer.
    """

    def __init__(self, driver: WebDriver):
        self._driver = driver
        self._wait = WaitHelper(driver)
        self._screenshot = ScreenshotHelper(driver)

    # ── Navigation ────────────────────────────────────────────────────────────

    def open(self, path: str = "") -> None:
        """Navigate to BASE_URL + path."""
        url = settings.BASE_URL.rstrip("/") + "/" + path.lstrip("/")
        self._driver.get(url)
        self._wait.for_page_load()

    @property
    def current_url(self) -> str:
        return self._driver.current_url

    @property
    def title(self) -> str:
        return self._driver.title

    # ── Element interactions ──────────────────────────────────────────────────

    def _find(self, locator: tuple) -> WebElement:
        """Wait for and return a single visible element."""
        return self._wait.for_element_visible(locator)

    def _find_all(self, locator: tuple) -> list[WebElement]:
        """Wait for and return all matching elements."""
        return self._wait.for_elements_present(locator)

    def _click(self, locator: tuple) -> None:
        self._wait.for_element_clickable(locator).click()

    def _type(self, locator: tuple, text: str) -> None:
        element = self._wait.for_element_clickable(locator)
        element.clear()
        element.send_keys(text)

    def _get_text(self, locator: tuple) -> str:
        return self._find(locator).text.strip()

    def _get_attribute(self, locator: tuple, attribute: str) -> str:
        return self._find(locator).get_attribute(attribute)

    def _select_by_value(self, locator: tuple, value: str) -> None:
        element = self._wait.for_element_present(locator)
        Select(element).select_by_value(value)

    def _is_displayed(self, locator: tuple) -> bool:
        return self._wait.is_element_present(locator)

    # ── Utilities ─────────────────────────────────────────────────────────────

    def capture_screenshot(self, name: str) -> str:
        return self._screenshot.capture(name)
