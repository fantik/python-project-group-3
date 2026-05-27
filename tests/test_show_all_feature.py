"""Tests for the `all` command table output."""

from datetime import datetime
import unittest
from unittest.mock import patch

from tests._rich_stub import ensure_rich_stub

ensure_rich_stub()

from handlers import show_all
from models import AddressBook, Record


class FakeDateTime(datetime):
    """Fixed current date for deterministic birthday day counts."""

    @classmethod
    def today(cls):
        return cls(2025, 5, 27)


class CapturingTable:
    """Minimal Rich Table test double that captures columns and rows."""

    def __init__(self, title=None):
        self.title = title
        self.columns = []
        self.rows = []

    def add_column(self, name, style=None, **kwargs):
        self.columns.append((name, style))

    def add_row(self, *values):
        self.rows.append(values)


class ShowAllTests(unittest.TestCase):
    """Cover user-facing output structure for the `all` command."""

    def test_show_all_uses_expected_columns_and_placeholders(self):
        book = AddressBook()

        full_record = Record("Alice")
        full_record.add_phone("0671234567")
        full_record.add_email("alice@example.com")
        full_record.add_address("Main Street 10")
        full_record.add_birthday("30.05.2000")
        book.add_record(full_record)

        empty_record = Record("Bob")
        book.add_record(empty_record)

        printed = []

        with (
            patch("handlers.Table", CapturingTable),
            patch("handlers.console.print", side_effect=printed.append),
            patch("models.datetime", FakeDateTime),
        ):
            result = show_all(book)

        self.assertIsNone(result)
        self.assertEqual(len(printed), 1)

        table = printed[0]
        self.assertEqual(
            [column[0] for column in table.columns],
            [
                "Name",
                "Phones",
                "Email",
                "Address",
                "Birthday",
                "Days to birthday",
                "Notes",
            ],
        )
        self.assertEqual(
            table.rows[0],
            (
                "Alice",
                "0671234567",
                "alice@example.com",
                "Main Street 10",
                "30.05.2000",
                "3",
                "—",
            ),
        )
        self.assertEqual(table.rows[1], ("", "", "", "", "", "", ""))
        self.assertEqual(
            table.rows[2],
            ("Bob", "—", "—", "—", "—", "—", "—"),
        )


if __name__ == "__main__":
    unittest.main()
