"""Tests for the contact email feature."""

import unittest

from tests._rich_stub import ensure_rich_stub

ensure_rich_stub()

from handlers import add_email
from models import AddressBook, Name, Record
from validators import validate_email


class EmailValidationTests(unittest.TestCase):
    """Cover shared email validation behavior."""

    def test_validate_email_returns_trimmed_value(self):
        self.assertEqual(
            validate_email("  alice@example.com  "),
            "alice@example.com",
        )

    def test_validate_email_rejects_invalid_value(self):
        with self.assertRaisesRegex(ValueError, "Invalid email format"):
            validate_email("alice.example.com")


class RecordEmailTests(unittest.TestCase):
    """Cover email behavior on the domain model."""

    def test_add_email_stores_valid_email(self):
        record = Record("Alice")

        record.add_email("alice@example.com")

        self.assertEqual(record.email.value, "alice@example.com")

    def test_add_email_rejects_invalid_value(self):
        record = Record("Alice")

        with self.assertRaisesRegex(ValueError, "Invalid email format"):
            record.add_email("alice.example.com")

    def test_edit_email_replaces_existing_value(self):
        record = Record("Alice")
        record.add_email("alice@example.com")

        record.edit_email("alice.work@example.com")

        self.assertEqual(record.email.value, "alice.work@example.com")

    def test_edit_email_requires_existing_email(self):
        record = Record("Alice")

        with self.assertRaisesRegex(ValueError, "Email not set"):
            record.edit_email("alice@example.com")

    def test_legacy_record_state_gets_default_email(self):
        legacy_record = Record.__new__(Record)

        legacy_record.__setstate__(
            {
                "name": Name("Alice"),
                "phones": [],
                "birthday": None,
                "address": None,
            }
        )

        self.assertIsNone(legacy_record.email)


class EmailCommandTests(unittest.TestCase):
    """Cover email-related CLI handlers."""

    def test_add_email_handler_sets_email(self):
        book = AddressBook()
        record = Record("Alice")
        book.add_record(record)

        result = add_email(["Alice", "alice@example.com"], book)

        self.assertEqual(result, "[green]Email added.[/green]")
        self.assertEqual(record.email.value, "alice@example.com")

    def test_add_email_handler_returns_validation_error(self):
        book = AddressBook()
        record = Record("Alice")
        book.add_record(record)

        result = add_email(["Alice", "alice.example.com"], book)

        self.assertEqual(result, "[red]Invalid email format[/red]")

    def test_add_email_handler_requires_arguments(self):
        book = AddressBook()

        result = add_email([], book)

        self.assertEqual(
            result, "[red]Usage: add-email \\[name] \\[email][/red]"
        )


if __name__ == "__main__":
    unittest.main()
