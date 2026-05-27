"""Tests for the `remove-contact` command."""

import unittest
from unittest.mock import patch

from tests._rich_stub import ensure_rich_stub

ensure_rich_stub()

from handlers import remove_contact
from models import AddressBook, Record


class RemoveContactTests(unittest.TestCase):
    """Cover user-facing behavior of the `remove-contact` handler."""

    def test_remove_contact_deletes_record_after_confirmation(self):
        book = AddressBook()
        record = Record("Alice Smith")
        book.add_record(record)

        with (
            patch("builtins.print"),
            patch("builtins.input", return_value="y"),
        ):
            result = remove_contact(["Alice", "Smith"], book)

        self.assertEqual(
            result,
            "[green]Contact 'Alice Smith' has been deleted successfully.[/green]",
        )
        self.assertIsNone(book.find("Alice Smith"))

    def test_remove_contact_keeps_record_when_cancelled(self):
        book = AddressBook()
        record = Record("Alice Smith")
        book.add_record(record)

        with (
            patch("builtins.print"),
            patch("builtins.input", return_value="n"),
        ):
            result = remove_contact(["Alice", "Smith"], book)

        self.assertEqual(result, "[yellow]Deletion cancelled.[/yellow]")
        self.assertIsNotNone(book.find("Alice Smith"))

    def test_remove_contact_keeps_record_when_confirmation_is_interrupted(self):
        book = AddressBook()
        record = Record("Alice Smith")
        book.add_record(record)

        with (
            patch("builtins.print"),
            patch("builtins.input", side_effect=KeyboardInterrupt),
        ):
            result = remove_contact(["Alice", "Smith"], book)

        self.assertEqual(result, "[yellow]Deletion cancelled.[/yellow]")
        self.assertIsNotNone(book.find("Alice Smith"))

    def test_remove_contact_keeps_record_when_confirmation_hits_eof(self):
        book = AddressBook()
        record = Record("Alice Smith")
        book.add_record(record)

        with (
            patch("builtins.print"),
            patch("builtins.input", side_effect=EOFError),
        ):
            result = remove_contact(["Alice", "Smith"], book)

        self.assertEqual(result, "[yellow]Deletion cancelled.[/yellow]")
        self.assertIsNotNone(book.find("Alice Smith"))

    def test_remove_contact_returns_not_found_for_missing_contact(self):
        book = AddressBook()

        result = remove_contact(["Missing"], book)

        self.assertEqual(result, "[red]Contact not found[/red]")

    def test_remove_contact_requires_name_argument(self):
        book = AddressBook()

        result = remove_contact([], book)

        self.assertEqual(
            result, "[red]Usage: remove-contact [name][/red]"
        )


if __name__ == "__main__":
    unittest.main()
