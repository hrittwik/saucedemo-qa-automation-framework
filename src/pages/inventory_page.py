"""
pages/inventory_page.py
Page Object for the SauceDemo inventory/products page (/inventory.html).
All locators use data-test attributes for maximum stability.
"""

from selenium.webdriver.common.by import By
from src.pages.base_page import BasePage


class InventoryPage(BasePage):
    """Represents the /inventory.html products listing page."""

    # ── Locators ──────────────────────────────────────────────────────────────
    _PAGE_TITLE      = (By.CSS_SELECTOR, "[data-test='title']")
    _PRODUCT_ITEMS   = (By.CSS_SELECTOR, "[data-test='inventory-item']")
    _PRODUCT_NAMES   = (By.CSS_SELECTOR, "[data-test='inventory-item-name']")
    _PRODUCT_PRICES  = (By.CSS_SELECTOR, "[data-test='inventory-item-price']")
    _SORT_DROPDOWN   = (By.CSS_SELECTOR, "[data-test='product-sort-container']")
    _CART_BADGE      = (By.CSS_SELECTOR, "[data-test='shopping-cart-badge']")
    _CART_LINK       = (By.CSS_SELECTOR, "[data-test='shopping-cart-link']")
    _MENU_BUTTON     = (By.CSS_SELECTOR, "[data-test='open-menu']")
    _LOGOUT_LINK     = (By.CSS_SELECTOR, "[data-test='logout-sidebar-link']")
    _MENU_CLOSE      = (By.CSS_SELECTOR, "[data-test='close-menu']")
    # Product images have no data-test — use class as stable fallback
    _PRODUCT_IMAGES  = (By.CLASS_NAME, "inventory_item_img")

    def _add_to_cart_btn(self, product_name: str) -> tuple:
        safe = (product_name.lower()
                .replace(" ", "-").replace(".", "")
                .replace("(", "").replace(")", "").replace("'", ""))
        return (By.CSS_SELECTOR, f"[data-test='add-to-cart-{safe}']")

    def _remove_from_cart_btn(self, product_name: str) -> tuple:
        safe = (product_name.lower()
                .replace(" ", "-").replace(".", "")
                .replace("(", "").replace(")", "").replace("'", ""))
        return (By.CSS_SELECTOR, f"[data-test='remove-{safe}']")

    # ── Actions ───────────────────────────────────────────────────────────────

    def open_inventory(self) -> "InventoryPage":
        self.open("inventory.html")
        return self

    def sort_by(self, sort_value: str) -> "InventoryPage":
        """Sort products. Values: 'az', 'za', 'lohi', 'hilo'."""
        self._select_by_value(self._SORT_DROPDOWN, sort_value)
        return self

    def add_item_to_cart(self, product_name: str) -> "InventoryPage":
        self._click(self._add_to_cart_btn(product_name))
        return self

    def remove_item_from_cart(self, product_name: str) -> "InventoryPage":
        self._click(self._remove_from_cart_btn(product_name))
        return self

    def go_to_cart(self) -> None:
        self._click(self._CART_LINK)

    def open_menu(self) -> "InventoryPage":
        self._click(self._MENU_BUTTON)
        return self

    def logout(self) -> None:
        self.open_menu()
        self._wait.for_element_clickable(self._LOGOUT_LINK)
        self._click(self._LOGOUT_LINK)

    # ── Queries ───────────────────────────────────────────────────────────────

    def get_page_title(self) -> str:
        return self._get_text(self._PAGE_TITLE)

    def get_product_names(self) -> list[str]:
        return [el.text.strip() for el in self._find_all(self._PRODUCT_NAMES)]

    def get_product_prices(self) -> list[float]:
        return [float(el.text.strip().replace("$", ""))
                for el in self._find_all(self._PRODUCT_PRICES)]

    def get_product_count(self) -> int:
        return len(self._find_all(self._PRODUCT_ITEMS))

    def get_cart_badge_count(self) -> int:
        if not self._is_displayed(self._CART_BADGE):
            return 0
        return int(self._get_text(self._CART_BADGE))

    def get_product_image_srcs(self) -> list[str]:
        """Returns all product image src attributes — used for visual regression."""
        from selenium.webdriver.common.by import By
        containers = self._find_all(self._PRODUCT_IMAGES)
        return [c.find_element(By.TAG_NAME, "img").get_attribute("src")
                for c in containers]

    def is_on_inventory_page(self) -> bool:
        return "inventory.html" in self.current_url
