"""
tests/test_auth.py
Test suite for Part 2.1 — Authentication.

Covers:
- Successful login (standard_user)
- Login failures: wrong password, empty fields, SQL injection
- Locked-out user behaviour
- Session persistence (navigating away doesn't log user out)
- Logout behaviour
"""

import pytest
import allure

from src.pages import LoginPage, InventoryPage
from src.utils.data_loader import DataLoader
from src.utils.assertions import Assertions


@allure.feature("Authentication")
class TestLogin:
    """Positive login scenarios."""

    @allure.story("Successful login")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_successful_login_standard_user(self, login_page: LoginPage):
        """Standard user can log in and lands on the inventory page."""
        user = DataLoader.get_user("standard_user")

        with allure.step("Navigate to login page and submit valid credentials"):
            login_page.login(user["username"], user["password"])

        with allure.step("Assert redirect to inventory page"):
            Assertions.assert_url_contains(login_page.current_url, "inventory.html")

    @allure.story("Successful login")
    def test_login_page_loads_correctly(self, login_page: LoginPage):
        """Login page loads with all required elements present."""
        login_page.open_login_page()
        assert login_page.is_on_login_page(), "Should be on login page"
        assert not login_page.is_error_displayed(), "No error should be visible on fresh load"


@allure.feature("Authentication")
class TestLoginFailures:
    """Negative and edge-case login scenarios."""

    @allure.story("Invalid credentials")
    @pytest.mark.parametrize("scenario", DataLoader.get_invalid_credentials())
    def test_login_with_invalid_credentials(self, login_page: LoginPage, scenario: dict):
        """Login fails for all invalid credential combinations with correct error message."""
        with allure.step(f"Attempt login: username='{scenario['username']}'"):
            login_page.open_login_page()
            login_page.enter_username(scenario["username"])
            login_page.enter_password(scenario["password"])
            login_page.click_login()

        with allure.step("Assert error message is displayed"):
            assert login_page.is_error_displayed(), "Error message should be visible"

        with allure.step("Assert correct error text"):
            Assertions.assert_text_equals(
                login_page.get_error_message(),
                scenario["expected_error"],
                context="Login error message",
            )

        with allure.step("Assert user stays on login page"):
            assert login_page.is_on_login_page(), "User should remain on login page after failure"

    @allure.story("Locked out user")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_locked_out_user_cannot_login(self, login_page: LoginPage):
        """Locked-out user sees a specific error and cannot proceed."""
        user = DataLoader.get_user("locked_out_user")

        login_page.login(user["username"], user["password"])

        assert login_page.is_error_displayed(), "Locked-out user should see error"
        Assertions.assert_text_contains(
            login_page.get_error_message(),
            "Sorry, this user has been locked out",
            context="Locked-out error message",
        )
        assert login_page.is_on_login_page(), "Locked-out user must stay on login page"

    @allure.story("Error dismissal")
    def test_error_message_can_be_dismissed(self, login_page: LoginPage):
        """Error message disappears after clicking the close (X) button."""
        login_page.open_login_page()
        login_page.enter_username("bad_user")
        login_page.enter_password("bad_pass")
        login_page.click_login()

        assert login_page.is_error_displayed(), "Error should be visible"
        login_page.close_error()
        assert not login_page.is_error_displayed(), "Error should be gone after dismissal"


@allure.feature("Authentication")
class TestSessionBehaviour:
    """Session persistence and logout tests."""

    @allure.story("Session persistence")
    def test_session_persists_after_page_navigation(self, authenticated_driver):
        """After logging in, navigating to inventory URL keeps the session active."""
        inventory = InventoryPage(authenticated_driver)
        inventory.open_inventory()

        Assertions.assert_url_contains(inventory.current_url, "inventory.html")
        assert inventory.is_on_inventory_page(), "User should still be on inventory after navigation"

    @allure.story("Logout")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_logout_redirects_to_login(self, authenticated_driver):
        """Clicking logout takes the user back to the login page."""
        inventory = InventoryPage(authenticated_driver)
        inventory.open_inventory()
        inventory.logout()

        login = LoginPage(authenticated_driver)
        assert login.is_on_login_page(), "After logout, user should be on login page"

    @allure.story("Logout")
    def test_cannot_access_inventory_after_logout(self, authenticated_driver):
        """After logout, directly navigating to /inventory.html redirects back to login."""
        inventory = InventoryPage(authenticated_driver)
        inventory.open_inventory()
        inventory.logout()

        # Try to bypass login by going directly to inventory
        inventory.open("inventory.html")
        login = LoginPage(authenticated_driver)
        assert login.is_on_login_page(), "Should be redirected to login after logout"
