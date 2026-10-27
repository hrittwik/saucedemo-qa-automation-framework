from unittest.mock import Mock, patch

import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

from src.pages.cart_page import CartPage
from src.pages.checkout_page import CheckoutStepTwoPage
from src.utils.screenshot_helper import ScreenshotHelper
from src.utils.wait_helper import WaitHelper


def test_cart_items_use_the_live_page_selector():
    assert CartPage._CART_ITEMS == (
        By.CSS_SELECTOR,
        "[data-test='inventory-item']",
    )


@pytest.mark.parametrize(
    ("label", "expected"),
    [
        ("Item total: $29.99", 29.99),
        ("Tax: $2.40", 2.40),
        ("Total: $32.39", 32.39),
    ],
)
def test_checkout_price_parser_extracts_amount(label, expected):
    page = object.__new__(CheckoutStepTwoPage)
    with patch.object(CheckoutStepTwoPage, "_get_text", return_value=label):
        assert page._extract_price((By.CSS_SELECTOR, "[data-test='total-label']")) == expected


def test_checkout_price_parser_rejects_malformed_label():
    page = object.__new__(CheckoutStepTwoPage)
    with patch.object(CheckoutStepTwoPage, "_get_text", return_value="Total unavailable"):
        with pytest.raises(ValueError, match="Could not parse a price"):
            page._extract_price((By.CSS_SELECTOR, "[data-test='total-label']"))


def test_visibility_check_returns_false_after_timeout():
    with patch("src.utils.wait_helper.WebDriverWait") as wait_factory:
        wait_factory.return_value.until.side_effect = TimeoutException
        helper = WaitHelper(Mock())

        assert not helper.is_element_visible((By.ID, "missing"))


def test_wait_helper_preserves_zero_timeout():
    with patch("src.utils.wait_helper.WebDriverWait") as wait_factory:
        WaitHelper(Mock(), timeout=0)._wait()

        assert wait_factory.call_args.args[1] == 0


def test_screenshot_failure_is_reported():
    driver = Mock()
    driver.save_screenshot.return_value = False
    helper = ScreenshotHelper(driver)

    with pytest.raises(OSError, match="failed to save screenshot"):
        helper.capture("failure")
