"""Tests for the `search` command (global query + positional filter)."""

import unittest
from unittest.mock import patch

from tests._rich_stub import ensure_rich_stub

ensure_rich_stub()

from handlers import search_contacts
from models import AddressBook, Record


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


class SearchContactsTests(unittest.TestCase):
    """Cover user-facing behavior for the `search` command."""

    def setUp(self):
        self.book = AddressBook()

        alice = Record("Alice Smith")
        alice.add_phone("0671234567")
        alice.add_email("alice@gmail.com")
        alice.add_address("Main Street 10, Kyiv")
        self.book.add_record(alice)

        bob = Record("Bob")
        bob.add_phone("0631230000")
        bob.add_email("bob@gmail.com")
        self.book.add_record(bob)

    def test_search_returns_nothing_found_when_no_matches(self):
        result = search_contacts(["Charlie", "-", "-", "-"], self.book)
        self.assertEqual(result, "[yellow]Nothing found[/yellow]")

    def test_search_default_partial_match_by_name(self):
        printed = []
        with (
            patch("handlers.Table", CapturingTable),
            patch("handlers.console.print", side_effect=printed.append),
        ):
            result = search_contacts(["Ali", "-", "-", "-"], self.book)

        self.assertIsNone(result)
        self.assertEqual(len(printed), 1)
        self.assertEqual(printed[0].title, "Contacts")
        self.assertEqual(printed[0].rows[0][0], "Alice Smith")

    def test_search_match_by_phone_normalized(self):
        printed = []
        with (
            patch("handlers.Table", CapturingTable),
            patch("handlers.console.print", side_effect=printed.append),
        ):
            result = search_contacts(["-", "+380671234567", "-", "-"], self.book)

        self.assertIsNone(result)
        self.assertEqual(printed[0].rows[0][0], "Alice Smith")

    def test_search_and_logic_multiple_criteria(self):
        printed = []
        with (
            patch("handlers.Table", CapturingTable),
            patch("handlers.console.print", side_effect=printed.append),
        ):
            result = search_contacts(
                ["Ali", "-", "alice@", "-"], self.book
            )

        self.assertIsNone(result)
        self.assertEqual(printed[0].rows[0][0], "Alice Smith")

    def test_search_partial_match_name_and_address(self):
        printed = []
        with (
            patch("handlers.Table", CapturingTable),
            patch("handlers.console.print", side_effect=printed.append),
        ):
            result = search_contacts(["ali", "-", "-", "kyiv"], self.book)

        self.assertIsNone(result)
        self.assertEqual(len(printed), 1)
        self.assertEqual(printed[0].title, "Contacts")
        self.assertEqual(printed[0].rows[0][0], "Alice Smith")

    def test_search_partial_match_phone_substring(self):
        printed = []
        with (
            patch("handlers.Table", CapturingTable),
            patch("handlers.console.print", side_effect=printed.append),
        ):
            result = search_contacts(["-", "1234", "-", "-"], self.book)

        self.assertIsNone(result)
        self.assertEqual(printed[0].rows[0][0], "Alice Smith")

    def test_search_global_query_matches_by_email_domain(self):
        printed = []
        with (
            patch("handlers.Table", CapturingTable),
            patch("handlers.console.print", side_effect=printed.append),
        ):
            result = search_contacts(["@gmail.com"], self.book)

        self.assertIsNone(result)
        self.assertEqual(len(printed), 1)
        self.assertEqual(printed[0].title, "Contacts")
        names = [row[0] for row in printed[0].rows if row and row[0]]
        self.assertEqual(set(names), {"Alice Smith", "Bob"})

    def test_search_global_query_matches_by_phone_substring(self):
        printed = []
        with (
            patch("handlers.Table", CapturingTable),
            patch("handlers.console.print", side_effect=printed.append),
        ):
            result = search_contacts(["123"], self.book)

        self.assertIsNone(result)
        names = [row[0] for row in printed[0].rows if row and row[0]]
        self.assertEqual(set(names), {"Alice Smith", "Bob"})


if __name__ == "__main__":
    unittest.main()

