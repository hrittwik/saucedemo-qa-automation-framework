"""
utils/wait_helper.py
Smart wait utilities built on top of Selenium's WebDriverWait.
Centralises all wait logic — NO hardcoded sleeps or Thread.sleep equivalents.
All timeouts default to settings.EXPLICIT_WAIT but can be overridden per-call.
"""

from typing import Callable, TypeVar
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

from src.config import settings

T = TypeVar("T")


class WaitHelper:
    """Encapsulates all explicit wait patterns used across the framework."""

    def __init__(self, driver: WebDriver, timeout: int = None):
        self._driver = driver
        self._timeout = timeout or settings.EXPLICIT_WAIT

    def _wait(self, timeout: int = None) -> WebDriverWait:
        return WebDriverWait(
            self._driver,
            timeout or self._timeout,
            ignored_exceptions=[StaleElementReferenceException],
        )

    # ── Visibility waits ──────────────────────────────────────────────────────

    def for_element_visible(self, locator: tuple, timeout: int = None) -> WebElement:
        """Wait until an element is visible and return it."""
        return self._wait(timeout).until(EC.visibility_of_element_located(locator))

    def for_element_clickable(self, locator: tuple, timeout: int = None) -> WebElement:
        """Wait until an element is clickable and return it."""
        return self._wait(timeout).until(EC.element_to_be_clickable(locator))

    def for_element_present(self, locator: tuple, timeout: int = None) -> WebElement:
        """Wait until an element is present in DOM (may not be visible)."""
        return self._wait(timeout).until(EC.presence_of_element_located(locator))

    def for_elements_present(self, locator: tuple, timeout: int = None) -> list[WebElement]:
        """Wait until at least one element matching locator is present."""
        return self._wait(timeout).until(EC.presence_of_all_elements_located(locator))

    def for_element_invisible(self, locator: tuple, timeout: int = None) -> bool:
        """Wait until element is invisible / removed from DOM."""
        return self._wait(timeout).until(EC.invisibility_of_element_located(locator))

    # ── Text / attribute waits ────────────────────────────────────────────────

    def for_text_in_element(self, locator: tuple, text: str, timeout: int = None) -> bool:
        """Wait until element contains specific text."""
        return self._wait(timeout).until(EC.text_to_be_present_in_element(locator, text))

    def for_url_contains(self, partial_url: str, timeout: int = None) -> bool:
        """Wait until the current URL contains the given string."""
        return self._wait(timeout).until(EC.url_contains(partial_url))

    def for_url_to_be(self, url: str, timeout: int = None) -> bool:
        """Wait until the current URL exactly matches."""
        return self._wait(timeout).until(EC.url_to_be(url))

    # ── Page-load waits ───────────────────────────────────────────────────────

    def for_page_load(self, timeout: int = None) -> bool:
        """Wait until document.readyState == 'complete'."""
        t = timeout or settings.PAGE_LOAD_TIMEOUT
        return WebDriverWait(self._driver, t).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    # ── Generic condition ────────────────────────────────────────────────────

    def until(self, condition: Callable, timeout: int = None) -> T:
        """Wait for any custom callable condition."""
        return self._wait(timeout).until(condition)

    def until_not(self, condition: Callable, timeout: int = None) -> T:
        """Wait until a custom callable condition is falsy."""
        return self._wait(timeout).until_not(condition)

    # ── Safe checks ───────────────────────────────────────────────────────────

    def is_element_present(self, locator: tuple, timeout: int = 3) -> bool:
        """Return True if element appears within timeout, False otherwise. Does not raise."""
        try:
            self._wait(timeout).until(EC.presence_of_element_located(locator))
            return True
        except TimeoutException:
            return False
