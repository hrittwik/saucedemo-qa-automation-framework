"""
pages/cart_page.py
Page Object for the SauceDemo shopping cart page (/cart.html).
All locators use data-test attributes for maximum stability.
"""

from selenium.webdriver.common.by import By
from src.pages.base_page import BasePage


class CartPage(BasePage):
    """Represents the /cart.html shopping cart page."""

    # ── Locators ──────────────────────────────────────────────────────────────
    _PAGE_TITLE           = (By.CSS_SELECTOR, "[data-test='title']")
    _CART_ITEMS           = (By.CSS_SELECTOR, "[data-test='cart-item']")
    _ITEM_NAMES           = (By.CSS_SELECTOR, "[data-test='inventory-item-name']")
    _ITEM_PRICES          = (By.CSS_SELECTOR, "[data-test='inventory-item-price']")
    _ITEM_QUANTITIES      = (By.CSS_SELECTOR, "[data-test='item-quantity']")
    _CONTINUE_SHOPPING    = (By.CSS_SELECTOR, "[data-test='continue-shopping']")
    _CHECKOUT_BTN         = (By.CSS_SELECTOR, "[data-test='checkout']")

    def _remove_button(self, product_name: str) -> tuple:
        safe = (product_name.lower()
                .replace(" ", "-").replace(".", "")
                .replace("(", "").replace(")", "").replace("'", ""))
        return (By.CSS_SELECTOR, f"[data-test='remove-{safe}']")

    # ── Actions ───────────────────────────────────────────────────────────────

    def open_cart(self) -> "CartPage":
        self.open("cart.html")
        return self

    def continue_shopping(self) -> None:
        self._click(self._CONTINUE_SHOPPING)

    def proceed_to_checkout(self) -> None:
        self._click(self._CHECKOUT_BTN)

    def remove_item(self, product_name: str) -> "CartPage":
        self._click(self._remove_button(product_name))
        return self

    # ── Queries ───────────────────────────────────────────────────────────────

    def get_item_names(self) -> list[str]:
        return [el.text.strip() for el in self._find_all(self._ITEM_NAMES)]

    def get_item_count(self) -> int:
        if not self._is_displayed(self._CART_ITEMS):
            return 0
        return len(self._find_all(self._CART_ITEMS))

    def is_item_in_cart(self, product_name: str) -> bool:
        return product_name in self.get_item_names()

    def is_cart_empty(self) -> bool:
        return not self._is_displayed(self._CART_ITEMS)

    def is_on_cart_page(self) -> bool:
        return "cart.html" in self.current_url
