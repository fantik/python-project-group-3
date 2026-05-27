"""Tests for the `show-contact` command panel output."""

from datetime import datetime
import unittest
from unittest.mock import patch

from tests._rich_stub import ensure_rich_stub

ensure_rich_stub()

from handlers import show_contact
from models import AddressBook, Record


class FakeDateTime(datetime):
    """Fixed current date for deterministic birthday day counts."""

    @classmethod
    def today(cls):
        return cls(2025, 5, 27)


class CapturingPanel:
    """Minimal Rich Panel test double that captures init data."""

    def __init__(
        self,
        renderable,
        title=None,
        subtitle=None,
        border_style=None,
        expand=None,
    ):
        self.renderable = renderable
        self.title = title
        self.subtitle = subtitle
        self.border_style = border_style
        self.expand = expand


class ShowContactTests(unittest.TestCase):
    """Cover user-facing output structure for the `show-contact` command."""

    def test_show_contact_prints_panel_with_all_fields(self):
        book = AddressBook()
        record = Record("Alice Smith")
        record.add_phone("0671234567")
        record.add_email("alice@example.com")
        record.add_address("Main Street 10")
        record.add_birthday("30.05.2000")
        book.add_record(record)
        printed = []

        with (
            patch("handlers.Panel", CapturingPanel),
            patch("handlers.console.print", side_effect=printed.append),
            patch("models.datetime", FakeDateTime),
        ):
            result = show_contact(["Alice", "Smith"], book)

        self.assertIsNone(result)
        self.assertEqual(len(printed), 1)

        panel = printed[0]
        self.assertEqual(panel.title, "Contact details")
        self.assertEqual(panel.subtitle, "Alice Smith")
        self.assertEqual(panel.border_style, "cyan")
        self.assertFalse(panel.expand)
        self.assertEqual(
            panel.renderable,
            "\n".join(
                [
                    "[bold cyan]Name:[/bold cyan] Alice Smith",
                    "[bold green]Phones:[/bold green] 0671234567",
                    "[bold blue]Email:[/bold blue] alice@example.com",
                    "[bold magenta]Address:[/bold magenta] Main Street 10",
                    "[bold yellow]Birthday:[/bold yellow] 30.05.2000",
                    "[bold bright_yellow]Days to birthday:[/bold bright_yellow] 3",
                ]
            ),
        )

    def test_show_contact_uses_placeholders_for_missing_fields(self):
        book = AddressBook()
        record = Record("Bob")
        book.add_record(record)
        printed = []

        with (
            patch("handlers.Panel", CapturingPanel),
            patch("handlers.console.print", side_effect=printed.append),
        ):
            result = show_contact(["Bob"], book)

        self.assertIsNone(result)
        panel = printed[0]
        self.assertIn("[bold green]Phones:[/bold green] —", panel.renderable)
        self.assertIn("[bold blue]Email:[/bold blue] —", panel.renderable)
        self.assertIn("[bold magenta]Address:[/bold magenta] —", panel.renderable)
        self.assertIn("[bold yellow]Birthday:[/bold yellow] —", panel.renderable)
        self.assertIn(
            "[bold bright_yellow]Days to birthday:[/bold bright_yellow] —",
            panel.renderable,
        )

    def test_show_contact_requires_name_argument(self):
        book = AddressBook()

        result = show_contact([], book)

        self.assertEqual(
            result, "[red]Usage: show-contact [name][/red]"
        )

    def test_show_contact_returns_not_found_for_missing_contact(self):
        book = AddressBook()

        result = show_contact(["Alice"], book)

        self.assertEqual(result, "[red]Contact not found[/red]")


if __name__ == "__main__":
    unittest.main()
