"""
utils/assertions.py
Custom, descriptive assertion helpers.
Wraps standard assertions with clear failure messages, reducing boilerplate in tests.
"""


class Assertions:
    """Collection of reusable assertion helpers with descriptive failure messages."""

    @staticmethod
    def assert_url_contains(actual_url: str, expected_fragment: str) -> None:
        assert expected_fragment in actual_url, (
            f"URL assertion failed.\n"
            f"  Expected to contain: '{expected_fragment}'\n"
            f"  Actual URL:          '{actual_url}'"
        )

    @staticmethod
    def assert_text_equals(actual: str, expected: str, context: str = "") -> None:
        ctx = f" [{context}]" if context else ""
        assert actual == expected, (
            f"Text equality assertion failed{ctx}.\n"
            f"  Expected: '{expected}'\n"
            f"  Actual:   '{actual}'"
        )

    @staticmethod
    def assert_text_contains(actual: str, expected_fragment: str, context: str = "") -> None:
        ctx = f" [{context}]" if context else ""
        assert expected_fragment in actual, (
            f"Text contains assertion failed{ctx}.\n"
            f"  Expected to contain: '{expected_fragment}'\n"
            f"  Actual:              '{actual}'"
        )

    @staticmethod
    def assert_list_equals(actual: list, expected: list, context: str = "") -> None:
        ctx = f" [{context}]" if context else ""
        assert actual == expected, (
            f"List equality assertion failed{ctx}.\n"
            f"  Expected: {expected}\n"
            f"  Actual:   {actual}"
        )

    @staticmethod
    def assert_list_sorted_ascending(items: list, context: str = "") -> None:
        ctx = f" [{context}]" if context else ""
        assert items == sorted(items), (
            f"List is not sorted ascending{ctx}.\n"
            f"  Actual order:    {items}\n"
            f"  Expected order:  {sorted(items)}"
        )

    @staticmethod
    def assert_list_sorted_descending(items: list, context: str = "") -> None:
        ctx = f" [{context}]" if context else ""
        assert items == sorted(items, reverse=True), (
            f"List is not sorted descending{ctx}.\n"
            f"  Actual order:    {items}\n"
            f"  Expected order:  {sorted(items, reverse=True)}"
        )

    @staticmethod
    def assert_count_equals(actual: int, expected: int, entity: str = "items") -> None:
        assert actual == expected, (
            f"Count assertion failed for {entity}.\n"
            f"  Expected: {expected}\n"
            f"  Actual:   {actual}"
        )

    @staticmethod
    def assert_math_totals_correct(
        item_total: float, tax: float, final_total: float
    ) -> None:
        """Verify that item_total + tax == final_total (within floating-point tolerance)."""
        expected = round(item_total + tax, 2)
        actual = round(final_total, 2)
        assert abs(expected - actual) < 0.01, (
            f"Order total math is incorrect.\n"
            f"  Item total: {item_total}\n"
            f"  Tax:        {tax}\n"
            f"  Expected total (item+tax): {expected}\n"
            f"  Actual total on page:      {actual}"
        )

    @staticmethod
    def assert_true(condition: bool, message: str) -> None:
        assert condition, message

    @staticmethod
    def assert_false(condition: bool, message: str) -> None:
        assert not condition, message
