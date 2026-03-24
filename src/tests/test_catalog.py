"""
tests/test_catalog.py
Test suite for Part 2.2 — Product Catalog.

Covers:
- Product listing loads correctly (count, names, prices)
- Sorting: Name A→Z, Z→A, Price Low→High, Price High→Low
- problem_user visual regression (broken/mismatched product images)
"""

import pytest
import allure

from src.pages import LoginPage, InventoryPage
from src.utils.data_loader import DataLoader
from src.utils.assertions import Assertions


@allure.feature("Product Catalog")
class TestProductListing:
    """Tests for the product listing page."""

    @allure.story("Product listing loads")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_correct_product_count(self, inventory_page: InventoryPage):
        """Inventory page displays the expected number of products."""
        products = DataLoader.get_products()
        expected_count = products["expected_product_count"]

        actual_count = inventory_page.get_product_count()
        Assertions.assert_count_equals(actual_count, expected_count, entity="products")

    @allure.story("Product listing loads")
    def test_all_product_names_visible(self, inventory_page: InventoryPage):
        """All expected product names appear in the listing."""
        products = DataLoader.get_products()
        expected_names = sorted(products["expected_products"])

        actual_names = sorted(inventory_page.get_product_names())
        Assertions.assert_list_equals(actual_names, expected_names, context="Product names")

    @allure.story("Product listing loads")
    def test_all_products_have_prices(self, inventory_page: InventoryPage):
        """Every product has a non-zero price displayed."""
        prices = inventory_page.get_product_prices()
        assert len(prices) > 0, "No prices found on inventory page"
        for price in prices:
            assert price > 0, f"Product has invalid price: {price}"

    @allure.story("Product listing loads")
    def test_page_title_is_products(self, inventory_page: InventoryPage):
        """Page title reads 'Products'."""
        Assertions.assert_text_equals(
            inventory_page.get_page_title(), "Products", context="Inventory page title"
        )


@allure.feature("Product Catalog")
class TestProductSorting:
    """Tests for the product sort functionality."""

    @allure.story("Sort by name A→Z")
    def test_sort_name_ascending(self, inventory_page: InventoryPage):
        """Products sort alphabetically A→Z."""
        inventory_page.sort_by("az")
        names = inventory_page.get_product_names()
        Assertions.assert_list_sorted_ascending(names, context="Name A→Z sort")

    @allure.story("Sort by name Z→A")
    def test_sort_name_descending(self, inventory_page: InventoryPage):
        """Products sort alphabetically Z→A."""
        inventory_page.sort_by("za")
        names = inventory_page.get_product_names()
        Assertions.assert_list_sorted_descending(names, context="Name Z→A sort")

    @allure.story("Sort by price Low→High")
    def test_sort_price_ascending(self, inventory_page: InventoryPage):
        """Products sort by price lowest to highest."""
        inventory_page.sort_by("lohi")
        prices = inventory_page.get_product_prices()
        Assertions.assert_list_sorted_ascending(prices, context="Price Low→High sort")

    @allure.story("Sort by price High→Low")
    def test_sort_price_descending(self, inventory_page: InventoryPage):
        """Products sort by price highest to lowest."""
        inventory_page.sort_by("hilo")
        prices = inventory_page.get_product_prices()
        Assertions.assert_list_sorted_descending(prices, context="Price High→Low sort")


@allure.feature("Product Catalog")
class TestProblemUserVisualRegression:
    """
    Visual regression tests for problem_user.
    The problem_user has broken/mismatched product images.
    We detect this by comparing image src attributes against what standard_user sees.
    No pixel comparison needed — the bug manifests as wrong src values.
    """

    @allure.story("Visual regression - problem_user")
    @allure.severity(allure.severity_level.NORMAL)
    def test_standard_user_images_are_unique(self, driver):
        """
        Standard user: each product image should be unique (different src).
        This establishes the baseline.
        """
        user = DataLoader.get_user("standard_user")
        login = LoginPage(driver)
        login.login(user["username"], user["password"])

        inventory = InventoryPage(driver)
        srcs = inventory.get_product_image_srcs()

        assert len(srcs) > 0, "No images found"
        unique_srcs = set(srcs)
        Assertions.assert_count_equals(
            len(unique_srcs), len(srcs), entity="unique product images for standard_user"
        )

    @allure.story("Visual regression - problem_user")
    @allure.severity(allure.severity_level.NORMAL)
    def test_problem_user_has_broken_images(self, driver):
        """
        problem_user: product images are mismatched — the same broken src
        is repeated for multiple products. We assert this anomaly is detectable.
        """
        user = DataLoader.get_user("problem_user")
        login = LoginPage(driver)
        login.login(user["username"], user["password"])

        inventory = InventoryPage(driver)
        srcs = inventory.get_product_image_srcs()

        assert len(srcs) > 0, "No images found for problem_user"
        unique_srcs = set(srcs)

        # problem_user's images are NOT all unique — multiple products share the same image
        has_duplicates = len(unique_srcs) < len(srcs)
        Assertions.assert_true(
            has_duplicates,
            f"Expected problem_user to have duplicate image srcs (visual bug), "
            f"but all {len(srcs)} images were unique. "
            f"SRCs: {srcs}",
        )
