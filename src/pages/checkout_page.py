"""
pages/checkout_page.py
Page Objects for the SauceDemo multi-step checkout flow.
All locators use data-test attributes for maximum stability.

Three focused classes matching the three checkout screens:
  CheckoutStepOnePage  — /checkout-step-one.html  (customer info form)
  CheckoutStepTwoPage  — /checkout-step-two.html  (order summary)
  CheckoutCompletePage — /checkout-complete.html  (confirmation)
"""

import re
from selenium.webdriver.common.by import By
from src.pages.base_page import BasePage


class CheckoutStepOnePage(BasePage):
    """Customer information form — first step of checkout."""

    # ── Locators ──────────────────────────────────────────────────────────────
    _FIRST_NAME    = (By.CSS_SELECTOR, "[data-test='firstName']")
    _LAST_NAME     = (By.CSS_SELECTOR, "[data-test='lastName']")
    _POSTAL_CODE   = (By.CSS_SELECTOR, "[data-test='postalCode']")
    _CONTINUE_BTN  = (By.CSS_SELECTOR, "[data-test='continue']")
    _CANCEL_BTN    = (By.CSS_SELECTOR, "[data-test='cancel']")
    _ERROR_MESSAGE = (By.CSS_SELECTOR, "[data-test='error']")

    # ── Actions ───────────────────────────────────────────────────────────────

    def enter_first_name(self, value: str) -> "CheckoutStepOnePage":
        self._type(self._FIRST_NAME, value)
        return self

    def enter_last_name(self, value: str) -> "CheckoutStepOnePage":
        self._type(self._LAST_NAME, value)
        return self

    def enter_postal_code(self, value: str) -> "CheckoutStepOnePage":
        self._type(self._POSTAL_CODE, value)
        return self

    def click_continue(self) -> None:
        self._click(self._CONTINUE_BTN)

    def fill_and_continue(self, first_name: str, last_name: str, postal_code: str) -> None:
        """Fill the complete form and click Continue."""
        self.enter_first_name(first_name)
        self.enter_last_name(last_name)
        self.enter_postal_code(postal_code)
        self.click_continue()

    # ── Queries ───────────────────────────────────────────────────────────────

    def get_error_message(self) -> str:
        return self._get_text(self._ERROR_MESSAGE)

    def is_error_displayed(self) -> bool:
        return self._is_displayed(self._ERROR_MESSAGE)


class CheckoutStepTwoPage(BasePage):
    """Order summary page — second step of checkout."""

    # ── Locators ──────────────────────────────────────────────────────────────
    _CART_ITEMS        = (By.CSS_SELECTOR, "[data-test='cart-item']")
    _ITEM_TOTAL_LABEL  = (By.CSS_SELECTOR, "[data-test='subtotal-label']")
    _TAX_LABEL         = (By.CSS_SELECTOR, "[data-test='tax-label']")
    _TOTAL_LABEL       = (By.CSS_SELECTOR, "[data-test='total-label']")
    _FINISH_BTN        = (By.CSS_SELECTOR, "[data-test='finish']")
    _CANCEL_BTN        = (By.CSS_SELECTOR, "[data-test='cancel']")

    # ── Actions ───────────────────────────────────────────────────────────────

    def click_finish(self) -> None:
        self._click(self._FINISH_BTN)

    # ── Queries ───────────────────────────────────────────────────────────────

    def _extract_price(self, locator: tuple) -> float:
        text = self._get_text(locator)
        match = re.search(r"[\d.]+", text)
        return float(match.group()) if match else 0.0

    def get_item_total(self) -> float:
        return self._extract_price(self._ITEM_TOTAL_LABEL)

    def get_tax(self) -> float:
        return self._extract_price(self._TAX_LABEL)

    def get_final_total(self) -> float:
        return self._extract_price(self._TOTAL_LABEL)

    def is_on_step_two(self) -> bool:
        return "checkout-step-two" in self.current_url


class CheckoutCompletePage(BasePage):
    """Order confirmation page — final step of checkout."""

    # ── Locators ──────────────────────────────────────────────────────────────
    _COMPLETE_HEADER  = (By.CSS_SELECTOR, "[data-test='complete-header']")
    _COMPLETE_TEXT    = (By.CSS_SELECTOR, "[data-test='complete-text']")
    _BACK_HOME_BTN    = (By.CSS_SELECTOR, "[data-test='back-to-products']")
    _PONY_EXPRESS_IMG = (By.CSS_SELECTOR, "[data-test='pony-express']")

    # ── Queries ───────────────────────────────────────────────────────────────

    def get_confirmation_header(self) -> str:
        return self._get_text(self._COMPLETE_HEADER)

    def get_confirmation_text(self) -> str:
        return self._get_text(self._COMPLETE_TEXT)

    def is_confirmation_image_displayed(self) -> bool:
        return self._is_displayed(self._PONY_EXPRESS_IMG)

    def is_on_complete_page(self) -> bool:
        return "checkout-complete" in self.current_url

    def click_back_home(self) -> None:
        self._click(self._BACK_HOME_BTN)
