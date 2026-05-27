"""Tests for contact notes feature."""

import unittest
from unittest.mock import patch

from tests._rich_stub import ensure_rich_stub

ensure_rich_stub()

from handlers import (
    NOTE_BULLET,
    add_note,
    all_notes,
    edit_note,
    find_note,
    remove_note,
)
from models import AddressBook, Name, Record
from validators import validate_note


class NoteValidationTests(unittest.TestCase):
    """Cover shared note validation behavior."""

    def test_validate_note_returns_trimmed_value(self):
        self.assertEqual(validate_note("  buy milk  "), "buy milk")

    def test_validate_note_rejects_too_short_value(self):
        with self.assertRaisesRegex(ValueError, "at least 3 characters"):
            validate_note("ab")

    def test_validate_note_rejects_too_long_value(self):
        with self.assertRaisesRegex(ValueError, "less than 100 characters"):
            validate_note("x" * 101)


class RecordNoteTests(unittest.TestCase):
    """Cover note behavior on the domain model."""

    def test_add_note_stores_valid_note(self):
        record = Record("Alice")
        record.add_note("buy milk")
        self.assertEqual(record.notes[0].value, "buy milk")

    def test_add_note_enforces_max_five_notes(self):
        record = Record("Alice")
        for index in range(Record.MAX_NOTES):
            record.add_note(f"note {index}")
        with self.assertRaisesRegex(ValueError, "at most 5 notes"):
            record.add_note("one too many")

    def test_remove_note_deletes_existing_value(self):
        record = Record("Alice")
        record.add_note("buy milk")
        record.remove_note("buy milk")
        self.assertEqual(record.notes, [])

    def test_edit_note_replaces_existing_value(self):
        record = Record("Alice")
        record.add_note("buy milk")
        record.edit_note("buy milk", "buy oat milk")
        self.assertEqual(record.notes[0].value, "buy oat milk")

    def test_edit_note_requires_existing_note(self):
        record = Record("Alice")
        with self.assertRaisesRegex(ValueError, "Old note not found"):
            record.edit_note("buy milk", "buy oat milk")

    def test_find_notes_by_query_matches_substring(self):
        record = Record("Olga")
        record.add_note("buy coffee now")
        matches = record.find_notes_by_query("cof")
        self.assertEqual(matches, ["buy coffee now"])

    def test_find_notes_by_query_is_case_insensitive(self):
        record = Record("Olga")
        record.add_note("buy coffee")
        matches = record.find_notes_by_query("COF")
        self.assertEqual(matches, ["buy coffee"])

    def test_legacy_record_state_gets_default_notes_list(self):
        legacy_record = Record.__new__(Record)
        legacy_record.__setstate__(
            {
                "name": Name("Alice"),
                "phones": [],
                "birthday": None,
                "address": None,
                "email": None,
            }
        )
        self.assertEqual(legacy_record.notes, [])


class NoteCommandTests(unittest.TestCase):
    """Cover note-related CLI handlers."""

    def test_add_note_handler_adds_note_to_contact(self):
        book = AddressBook()
        record = Record("Olga")
        book.add_record(record)

        result = add_note(["Olga", "buy", "milk"], book)

        self.assertEqual(result, "[green]Note added.[/green]")
        self.assertEqual(record.notes[0].value, "buy milk")

    def test_add_note_handler_reports_missing_contact(self):
        book = AddressBook()
        result = add_note(["Olga", "buy milk"], book)
        self.assertEqual(result, "[red]Contact not found[/red]")

    def test_find_note_handler_matches_partial_text(self):
        book = AddressBook()
        record = Record("Olga")
        record.add_note("buy coffee now")
        book.add_record(record)
        printed = []

        class CapturingTable:
            def __init__(self, title=None):
                self.title = title
                self.rows = []

            def add_column(self, *args, **kwargs):
                return None

            def add_row(self, *values):
                self.rows.append(values)

        with (
            patch("handlers.Table", CapturingTable),
            patch("handlers.console.print", side_effect=printed.append),
        ):
            result = find_note(["Olga", "cof"], book)

        self.assertIsNone(result)
        self.assertEqual(len(printed), 1)
        self.assertIn("buy coffee now", printed[0].rows[0][0])

    def test_all_notes_handler_prints_contact_notes(self):
        book = AddressBook()
        record = Record("Olga")
        record.add_note("buy milk")
        book.add_record(record)
        printed = []

        class CapturingTable:
            def __init__(self, title=None):
                self.title = title
                self.rows = []

            def add_column(self, *args, **kwargs):
                return None

            def add_row(self, *values):
                self.rows.append(values)

        with (
            patch("handlers.Table", CapturingTable),
            patch("handlers.console.print", side_effect=printed.append),
        ):
            result = all_notes(["Olga"], book)

        self.assertIsNone(result)
        self.assertEqual(
            printed[0].rows[0][0],
            f"{NOTE_BULLET} buy milk",
        )

    def test_all_notes_handler_accepts_multi_word_contact_name(self):
        book = AddressBook()
        record = Record("Mary Jane")
        record.add_note("buy milk")
        book.add_record(record)
        printed = []

        class CapturingTable:
            def __init__(self, title=None):
                self.title = title
                self.rows = []

            def add_column(self, *args, **kwargs):
                return None

            def add_row(self, *values):
                self.rows.append(values)

        with (
            patch("handlers.Table", CapturingTable),
            patch("handlers.console.print", side_effect=printed.append),
        ):
            result = all_notes(["Mary", "Jane"], book)

        self.assertIsNone(result)
        self.assertEqual(printed[0].title, "All notes for Mary Jane")

    def test_edit_note_handler_updates_note(self):
        book = AddressBook()
        record = Record("Olga")
        record.add_note("buy milk")
        book.add_record(record)

        result = edit_note(["Olga", "buy milk", "buy oat milk"], book)

        self.assertEqual(result, "[green]Note edited.[/green]")
        self.assertEqual(record.notes[0].value, "buy oat milk")

    def test_edit_note_handler_reports_missing_contact(self):
        book = AddressBook()
        result = edit_note(["Olga", "buy milk", "buy oat milk"], book)
        self.assertEqual(result, "[red]Contact not found[/red]")

    def test_remove_note_handler_removes_note(self):
        book = AddressBook()
        record = Record("Olga")
        record.add_note("buy milk")
        book.add_record(record)

        result = remove_note(["Olga", "buy milk"], book)

        self.assertEqual(result, "[green]Note removed.[/green]")
        self.assertEqual(record.notes, [])


if __name__ == "__main__":
    unittest.main()
