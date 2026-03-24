"""
utils/data_loader.py
Utility for loading test data from fixture files.
Provides a clean API so tests never reference file paths directly.
"""

import json
from pathlib import Path
from functools import lru_cache

from src.config import settings


@lru_cache(maxsize=None)
def _load_json(path: Path) -> dict | list:
    """Load and cache a JSON fixture file."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


class DataLoader:
    """Loads fixture data by logical name, not file path."""

    _FIXTURE_MAP = {
        "users": "users.json",
        "checkout": "checkout.json",
        "products": "products.json",
    }

    @classmethod
    def load(cls, fixture_name: str) -> dict | list:
        """
        Load a fixture by its logical name.

        Args:
            fixture_name: One of 'users', 'checkout', 'products'.

        Returns:
            Parsed fixture content as dict or list.
        """
        if fixture_name not in cls._FIXTURE_MAP:
            raise ValueError(
                f"Unknown fixture '{fixture_name}'. Available: {list(cls._FIXTURE_MAP)}"
            )
        path = settings.FIXTURES_DIR / cls._FIXTURE_MAP[fixture_name]
        return _load_json(path)

    @classmethod
    def get_user(cls, user_type: str) -> dict:
        """Convenience: get a specific user by type key."""
        users = cls.load("users")
        if user_type not in users:
            raise KeyError(f"User type '{user_type}' not found in users fixture.")
        return users[user_type]

    @classmethod
    def get_invalid_credentials(cls) -> list[dict]:
        """Convenience: get all invalid credential scenarios."""
        return cls.load("users")["invalid_credentials"]

    @classmethod
    def get_checkout_data(cls, scenario: str) -> dict:
        """Convenience: get a checkout data scenario by key."""
        checkout = cls.load("checkout")
        if scenario not in checkout:
            raise KeyError(f"Checkout scenario '{scenario}' not found.")
        return checkout[scenario]

    @classmethod
    def get_products(cls) -> dict:
        """Convenience: get all product fixture data."""
        return cls.load("products")
