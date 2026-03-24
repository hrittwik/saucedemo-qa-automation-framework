"""
tests/test_checkout.py
Test suite for Part 2.4 — Checkout Flow (End-to-End).

Covers:
- Complete a full purchase with valid details
- Checkout blocked when required fields are missing
- Order summary math (item total + tax == final total)
- Confirmation screen content after successful order
"""

import pytest
import allure

from src.pages import InventoryPage, CartPage, CheckoutStepOnePage, CheckoutStepTwoPage, CheckoutCompletePage
from src.utils.data_loader import DataLoader
from src.utils.assertions import Assertions


def _add_items_and_go_to_checkout(inventory_page: InventoryPage):
    """Helper: adds items to cart and navigates to checkout step one."""
    products = DataLoader.get_products()
    for item in products["items_to_add"]:
        inventory_page.add_item_to_cart(item)
    inventory_page.go_to_cart()

    cart = CartPage(inventory_page._driver)
    cart.proceed_to_checkout()
    return CheckoutStepOnePage(inventory_page._driver)


@allure.feature("Checkout")
class TestSuccessfulCheckout:
    """End-to-end happy path through checkout."""

    @allure.story("Complete purchase")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_complete_full_purchase(self, inventory_page: InventoryPage):
        """User can complete a purchase from inventory to confirmation screen."""
        customer = DataLoader.get_checkout_data("valid_customer")

        step_one = _add_items_and_go_to_checkout(inventory_page)

        with allure.step("Fill customer information"):
            step_one.fill_and_continue(
                customer["first_name"], customer["last_name"], customer["postal_code"]
            )

        with allure.step("Verify navigation to order summary"):
            step_two = CheckoutStepTwoPage(inventory_page._driver)
            assert step_two.is_on_step_two(), "Should be on checkout step two (order summary)"

        with allure.step("Click Finish"):
            step_two.click_finish()

        with allure.step("Verify confirmation page"):
            complete = CheckoutCompletePage(inventory_page._driver)
            assert complete.is_on_complete_page(), "Should be on checkout complete page"

    @allure.story("Confirmation screen content")
    def test_confirmation_header_text(self, inventory_page: InventoryPage):
        """Confirmation page shows the expected header message."""
        customer = DataLoader.get_checkout_data("valid_customer")
        step_one = _add_items_and_go_to_checkout(inventory_page)
        step_one.fill_and_continue(
            customer["first_name"], customer["last_name"], customer["postal_code"]
        )
        CheckoutStepTwoPage(inventory_page._driver).click_finish()

        complete = CheckoutCompletePage(inventory_page._driver)
        Assertions.assert_text_equals(
            complete.get_confirmation_header(),
            "Thank you for your order!",
            context="Confirmation header",
        )

    @allure.story("Confirmation screen content")
    def test_confirmation_image_is_displayed(self, inventory_page: InventoryPage):
        """The Pony Express confirmation image appears on the complete page."""
        customer = DataLoader.get_checkout_data("valid_customer")
        step_one = _add_items_and_go_to_checkout(inventory_page)
        step_one.fill_and_continue(
            customer["first_name"], customer["last_name"], customer["postal_code"]
        )
        CheckoutStepTwoPage(inventory_page._driver).click_finish()

        complete = CheckoutCompletePage(inventory_page._driver)
        assert complete.is_confirmation_image_displayed(), "Confirmation image should be shown"

    @allure.story("Confirmation screen content")
    def test_back_home_returns_to_inventory(self, inventory_page: InventoryPage):
        """'Back Home' button on confirmation page returns user to inventory."""
        customer = DataLoader.get_checkout_data("valid_customer")
        step_one = _add_items_and_go_to_checkout(inventory_page)
        step_one.fill_and_continue(
            customer["first_name"], customer["last_name"], customer["postal_code"]
        )
        CheckoutStepTwoPage(inventory_page._driver).click_finish()

        complete = CheckoutCompletePage(inventory_page._driver)
        complete.click_back_home()
        Assertions.assert_url_contains(complete.current_url, "inventory.html")


@allure.feature("Checkout")
class TestCheckoutValidation:
    """Tests for checkout form field validation."""

    @allure.story("Missing required fields")
    @pytest.mark.parametrize(
        "scenario_key",
        ["missing_first_name", "missing_last_name", "missing_postal_code"],
    )
    def test_checkout_blocked_with_missing_field(
        self, inventory_page: InventoryPage, scenario_key: str
    ):
        """Checkout is blocked and an appropriate error is shown for each missing required field."""
        scenario = DataLoader.get_checkout_data(scenario_key)
        step_one = _add_items_and_go_to_checkout(inventory_page)

        with allure.step(f"Submit form with missing field: {scenario_key}"):
            step_one.fill_and_continue(
                scenario["first_name"], scenario["last_name"], scenario["postal_code"]
            )

        with allure.step("Assert error is displayed"):
            assert step_one.is_error_displayed(), "Validation error should be shown"

        with allure.step("Assert correct error message"):
            Assertions.assert_text_equals(
                step_one.get_error_message(),
                scenario["expected_error"],
                context=f"Validation error for {scenario_key}",
            )


@allure.feature("Checkout")
class TestOrderSummaryMath:
    """Tests for the mathematical correctness of the order summary."""

    @allure.story("Order total calculation")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_order_total_equals_item_total_plus_tax(self, inventory_page: InventoryPage):
        """
        The final order total shown must equal item subtotal + tax.
        Verifies the page is not showing a hardcoded or miscalculated total.
        """
        customer = DataLoader.get_checkout_data("valid_customer")
        step_one = _add_items_and_go_to_checkout(inventory_page)
        step_one.fill_and_continue(
            customer["first_name"], customer["last_name"], customer["postal_code"]
        )

        step_two = CheckoutStepTwoPage(inventory_page._driver)
        item_total = step_two.get_item_total()
        tax = step_two.get_tax()
        final_total = step_two.get_final_total()

        with allure.step(f"Verify: {item_total} + {tax} == {final_total}"):
            Assertions.assert_math_totals_correct(item_total, tax, final_total)
