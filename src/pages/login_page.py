"""
pages/login_page.py
Page Object for the SauceDemo login page (/).
All locators use data-test attributes for maximum stability.
"""

from selenium.webdriver.common.by import By
from src.pages.base_page import BasePage


class LoginPage(BasePage):
    """Represents the /index.html login page."""

    # ── Locators (data-test first, fallback noted where data-test unavailable) ─
    _USERNAME_INPUT   = (By.CSS_SELECTOR, "[data-test='username']")
    _PASSWORD_INPUT   = (By.CSS_SELECTOR, "[data-test='password']")
    _LOGIN_BUTTON     = (By.CSS_SELECTOR, "[data-test='login-button']")
    _ERROR_MESSAGE    = (By.CSS_SELECTOR, "[data-test='error']")
    _ERROR_CLOSE_BTN  = (By.CSS_SELECTOR, "[data-test='error-button']")

    # ── Actions ───────────────────────────────────────────────────────────────

    def open_login_page(self) -> "LoginPage":
        self.open("")
        return self

    def enter_username(self, username: str) -> "LoginPage":
        self._type(self._USERNAME_INPUT, username)
        return self

    def enter_password(self, password: str) -> "LoginPage":
        self._type(self._PASSWORD_INPUT, password)
        return self

    def click_login(self) -> None:
        self._click(self._LOGIN_BUTTON)

    def login(self, username: str, password: str) -> None:
        """Complete the full login action."""
        self.open_login_page()
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()

    def close_error(self) -> "LoginPage":
        self._click(self._ERROR_CLOSE_BTN)
        return self

    # ── Queries ───────────────────────────────────────────────────────────────

    def get_error_message(self) -> str:
        return self._get_text(self._ERROR_MESSAGE)

    def is_error_displayed(self) -> bool:
        return self._is_displayed(self._ERROR_MESSAGE)

    def is_on_login_page(self) -> bool:
        return "saucedemo.com" in self.current_url and "inventory" not in self.current_url
