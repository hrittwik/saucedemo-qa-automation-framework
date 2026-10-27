"""
conftest.py
Pytest fixtures and hooks for the entire test suite.

Responsibilities:
- WebDriver lifecycle (setup / teardown per test)
- Pre-authenticated session fixture (avoids repeating login in every test)
- Automatic screenshot on failure
- Page Object injection into tests
"""

import base64
import pytest
from pathlib import Path

# Ensure required directories exist before pytest tries to write reports
for _d in ["reports", "screenshots", "allure-results"]:
    (Path(__file__).resolve().parent / _d).mkdir(exist_ok=True)
from selenium.webdriver.remote.webdriver import WebDriver

from src.utils.driver_factory import create_driver
from src.utils.screenshot_helper import ScreenshotHelper
from src.pages import (
    LoginPage,
    InventoryPage,
    CartPage,
    CheckoutStepOnePage,
    CheckoutStepTwoPage,
    CheckoutCompletePage,
)
from src.utils.data_loader import DataLoader


# ── Driver lifecycle ──────────────────────────────────────────────────────────


@pytest.fixture(scope="function")
def driver() -> WebDriver:
    """
    Creates a fresh WebDriver instance for each test function.
    Guaranteed teardown even if the test fails.
    """
    _driver = create_driver()
    try:
        yield _driver
    finally:
        _driver.quit()


# ── Authenticated session fixture ─────────────────────────────────────────────

@pytest.fixture(scope="function")
def authenticated_driver(driver: WebDriver) -> WebDriver:
    """
    Returns a driver that is already logged in as standard_user.
    Use this fixture for tests that don't care about the login flow itself.
    """
    user = DataLoader.get_user("standard_user")
    login_page = LoginPage(driver)
    login_page.login(user["username"], user["password"])
    return driver


# ── Page Object fixtures ───────────────────────────────────────────────────────

@pytest.fixture
def login_page(driver: WebDriver) -> LoginPage:
    return LoginPage(driver)


@pytest.fixture
def inventory_page(authenticated_driver: WebDriver) -> InventoryPage:
    page = InventoryPage(authenticated_driver)
    page.open_inventory()
    return page


@pytest.fixture
def cart_page(authenticated_driver: WebDriver) -> CartPage:
    return CartPage(authenticated_driver)


@pytest.fixture
def checkout_step_one(authenticated_driver: WebDriver) -> CheckoutStepOnePage:
    return CheckoutStepOnePage(authenticated_driver)


@pytest.fixture
def checkout_step_two(authenticated_driver: WebDriver) -> CheckoutStepTwoPage:
    return CheckoutStepTwoPage(authenticated_driver)


@pytest.fixture
def checkout_complete(authenticated_driver: WebDriver) -> CheckoutCompletePage:
    return CheckoutCompletePage(authenticated_driver)


# ── Report path ────────────────────────────────────────────────────────────────

@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    """Anchor the HTML report to the project root, whatever directory pytest runs from."""
    htmlpath = getattr(config.option, "htmlpath", None)
    if htmlpath and not Path(htmlpath).is_absolute():
        config.option.htmlpath = str(config.rootpath / htmlpath)


# ── Failure hooks ──────────────────────────────────────────────────────────────

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    After each test, if it failed, capture a screenshot automatically.
    Attaches the screenshot path to the test report for traceability.
    Compatible with pytest 7+ on Windows, macOS, and Linux.
    """
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        driver_fixture = item.funcargs.get("driver") or item.funcargs.get("authenticated_driver")
        if driver_fixture:
            screenshot_helper = ScreenshotHelper(driver_fixture)
            path = screenshot_helper.capture_on_failure(item.name)
            if path:
                extras = getattr(report, "extras", [])
                try:
                    from pytest_html import extras as html_extras
                except ImportError:
                    return
                image_data = base64.b64encode(Path(path).read_bytes()).decode("ascii")
                extras.append(html_extras.image(image_data))
                report.extras = extras