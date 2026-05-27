"""Tests for the contact address feature."""

import unittest

from tests._rich_stub import ensure_rich_stub

ensure_rich_stub()

from handlers import add_address, edit_address
from models import AddressBook, Name, Record


class RecordAddressTests(unittest.TestCase):
    """Cover address behavior on the domain model."""

    def test_add_address_stores_trimmed_value(self):
        record = Record("Alice")

        record.add_address("  Main Street 10  ")

        self.assertEqual(record.address.value, "Main Street 10")

    def test_add_address_rejects_too_short_value(self):
        record = Record("Alice")

        with self.assertRaisesRegex(
            ValueError, "Address must be at least 3 characters"
        ):
            record.add_address(" a ")

    def test_edit_address_replaces_existing_value(self):
        record = Record("Alice")
        record.add_address("Main Street 10")

        record.edit_address("Long Avenue 22")

        self.assertEqual(record.address.value, "Long Avenue 22")

    def test_edit_address_requires_existing_address(self):
        record = Record("Alice")

        with self.assertRaisesRegex(ValueError, "Address not set"):
            record.edit_address("New Street 5")

    def test_legacy_record_state_gets_default_address(self):
        legacy_record = Record.__new__(Record)

        legacy_record.__setstate__(
            {
                "name": Name("Alice"),
                "phones": [],
                "birthday": None,
            }
        )

        self.assertIsNone(legacy_record.address)


class AddressCommandTests(unittest.TestCase):
    """Cover address-related CLI handlers."""

    def test_add_address_handler_accepts_spaces(self):
        book = AddressBook()
        record = Record("Alice")
        book.add_record(record)

        result = add_address(["Alice", "Main", "Street", "10"], book)

        self.assertEqual(result, "[green]Address added.[/green]")
        self.assertEqual(record.address.value, "Main Street 10")

    def test_edit_address_handler_updates_value(self):
        book = AddressBook()
        record = Record("Alice")
        record.add_address("Main Street 10")
        book.add_record(record)

        result = edit_address(["Alice", "Long", "Avenue", "22"], book)

        self.assertEqual(result, "[green]Address updated.[/green]")
        self.assertEqual(record.address.value, "Long Avenue 22")

    def test_add_address_handler_requires_existing_contact(self):
        book = AddressBook()

        result = add_address(["Alice", "Main", "Street", "10"], book)

        self.assertEqual(result, "[red]Contact not found[/red]")

    def test_add_address_handler_requires_arguments(self):
        book = AddressBook()

        result = add_address([], book)

        self.assertEqual(
            result, "[red]Usage: add-address [name] [address][/red]"
        )

    def test_edit_address_handler_returns_validation_error(self):
        book = AddressBook()
        record = Record("Alice")
        record.add_address("Main Street 10")
        book.add_record(record)

        result = edit_address(["Alice", "xy"], book)

        self.assertEqual(
            result, "[red]Address must be at least 3 characters[/red]"
        )

    def test_edit_address_handler_requires_arguments(self):
        book = AddressBook()

        result = edit_address(["Alice"], book)

        self.assertEqual(
            result, "[red]Usage: edit-address [name] [new_address][/red]"
        )


if __name__ == "__main__":
    unittest.main()
