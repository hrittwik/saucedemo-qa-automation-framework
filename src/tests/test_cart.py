"""
tests/test_cart.py
Test suite for Part 2.3 — Shopping Cart.

Covers:
- Add a single item, verify cart badge updates
- Add multiple items, verify all appear in cart
- Remove an item from the cart
- Cart persists across page navigation
"""

import pytest
import allure

from src.pages import InventoryPage, CartPage
from src.utils.data_loader import DataLoader
from src.utils.assertions import Assertions


@allure.feature("Shopping Cart")
class TestAddToCart:
    """Tests for adding items to the cart."""

    @allure.story("Add single item")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_single_item_updates_badge(self, inventory_page: InventoryPage):
        """Adding one item increments the cart badge to 1."""
        products = DataLoader.get_products()
        product = products["items_to_add"][0]

        with allure.step(f"Add '{product}' to cart"):
            inventory_page.add_item_to_cart(product)

        with allure.step("Verify cart badge shows 1"):
            Assertions.assert_count_equals(
                inventory_page.get_cart_badge_count(), 1, entity="cart badge"
            )

    @allure.story("Add single item")
    def test_added_item_appears_in_cart(self, inventory_page: InventoryPage):
        """Item added from inventory appears in the cart page."""
        products = DataLoader.get_products()
        product = products["items_to_add"][0]

        inventory_page.add_item_to_cart(product)
        inventory_page.go_to_cart()

        cart = CartPage(inventory_page._driver)
        assert cart.is_item_in_cart(product), f"'{product}' should be in cart"

    @allure.story("Add multiple items")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_multiple_items_badge_updates(self, inventory_page: InventoryPage):
        """Adding multiple items correctly increments the badge count."""
        products = DataLoader.get_products()
        items = products["items_to_add"]

        for item in items:
            inventory_page.add_item_to_cart(item)

        Assertions.assert_count_equals(
            inventory_page.get_cart_badge_count(), len(items), entity="cart badge after multiple adds"
        )

    @allure.story("Add multiple items")
    def test_all_added_items_appear_in_cart(self, inventory_page: InventoryPage):
        """All items added from inventory all appear on the cart page."""
        products = DataLoader.get_products()
        items = products["items_to_add"]

        for item in items:
            inventory_page.add_item_to_cart(item)

        inventory_page.go_to_cart()
        cart = CartPage(inventory_page._driver)

        Assertions.assert_count_equals(cart.get_item_count(), len(items), entity="cart items")
        for item in items:
            assert cart.is_item_in_cart(item), f"'{item}' should be in cart"


@allure.feature("Shopping Cart")
class TestRemoveFromCart:
    """Tests for removing items from the cart."""

    @allure.story("Remove item")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_remove_item_from_cart_page(self, inventory_page: InventoryPage):
        """Removing an item from the cart page removes it from the list."""
        products = DataLoader.get_products()
        items = products["items_to_add"]

        for item in items:
            inventory_page.add_item_to_cart(item)

        inventory_page.go_to_cart()
        cart = CartPage(inventory_page._driver)

        item_to_remove = items[0]
        cart.remove_item(item_to_remove)

        assert not cart.is_item_in_cart(item_to_remove), (
            f"'{item_to_remove}' should be removed from cart"
        )
        Assertions.assert_count_equals(
            cart.get_item_count(), len(items) - 1, entity="remaining cart items"
        )

    @allure.story("Remove item")
    def test_cart_is_empty_after_removing_all_items(self, inventory_page: InventoryPage):
        """Cart shows empty state after all items are removed."""
        products = DataLoader.get_products()
        item = products["items_to_add"][0]

        inventory_page.add_item_to_cart(item)
        inventory_page.go_to_cart()

        cart = CartPage(inventory_page._driver)
        cart.remove_item(item)

        assert cart.is_cart_empty(), "Cart should be empty after removing the only item"


@allure.feature("Shopping Cart")
class TestCartPersistence:
    """Tests that cart state persists across navigation."""

    @allure.story("Cart persistence")
    def test_cart_persists_after_continuing_shopping(self, inventory_page: InventoryPage):
        """
        Items added to cart remain there after leaving cart and returning via
        the 'Continue Shopping' button.
        """
        products = DataLoader.get_products()
        item = products["items_to_add"][0]

        inventory_page.add_item_to_cart(item)
        inventory_page.go_to_cart()

        cart = CartPage(inventory_page._driver)
        cart.continue_shopping()

        # Return to inventory — cart badge should still show 1
        Assertions.assert_count_equals(
            inventory_page.get_cart_badge_count(), 1, entity="cart badge after continue shopping"
        )

        # Go back to cart and confirm item is still there
        inventory_page.go_to_cart()
        assert cart.is_item_in_cart(item), "Item should persist after navigating away and back"

    @allure.story("Cart persistence")
    def test_cart_badge_persists_after_navigating_back_to_inventory(
        self, inventory_page: InventoryPage
    ):
        """Cart badge count is maintained when navigating between pages."""
        products = DataLoader.get_products()
        items = products["items_to_add"]

        for item in items:
            inventory_page.add_item_to_cart(item)

        # Navigate away and come back
        inventory_page.open_inventory()

        Assertions.assert_count_equals(
            inventory_page.get_cart_badge_count(),
            len(items),
            entity="cart badge after re-visiting inventory",
        )
