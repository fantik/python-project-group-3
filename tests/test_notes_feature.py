"""Tests for contact notes and tags feature."""

import unittest
from unittest.mock import patch

from tests._rich_stub import ensure_rich_stub

ensure_rich_stub()

from handlers import (
    NOTE_BULLET,
    PLACEHOLDER,
    add_note,
    add_tag,
    all_notes,
    edit_note,
    find_note,
    find_notes_by_tag,
    format_notes_for_display,
    remove_note,
    remove_tag,
    search_contacts,
    sort_notes_by_tag,
)
from models import AddressBook, Name, Note, Record
from validators import validate_note, validate_tag


class CapturingTable:
    """Minimal Rich Table test double that captures columns and rows."""

    def __init__(self, title=None):
        self.title = title
        self.rows = []

    def add_column(self, *args, **kwargs):
        return None

    def add_row(self, *values):
        self.rows.append(values)


def _capture_table_output(handler, *handler_args):
    """Run a handler that prints a table and return printed objects."""
    printed = []
    with (
        patch("handlers.Table", CapturingTable),
        patch("handlers.console.print", side_effect=printed.append),
    ):
        result = handler(*handler_args)
    return result, printed


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


class TagValidationTests(unittest.TestCase):
    """Cover shared tag validation behavior."""

    def test_validate_tag_strips_hash_and_lowercases(self):
        self.assertEqual(validate_tag("#Shopping"), "shopping")

    def test_validate_tag_rejects_too_short_value(self):
        with self.assertRaisesRegex(ValueError, "at least 3 characters"):
            validate_tag("#ab")

    def test_validate_tag_rejects_too_long_value(self):
        with self.assertRaisesRegex(ValueError, "less than 20 characters"):
            validate_tag("#" + "x" * 21)

    def test_validate_tag_rejects_invalid_characters(self):
        with self.assertRaisesRegex(ValueError, "only letters"):
            validate_tag("#shop ping")


class RecordNoteTests(unittest.TestCase):
    """Cover note behavior on the domain model."""

    def test_add_note_stores_valid_note_with_empty_tags(self):
        record = Record("Alice")
        note_id = record.add_note("buy milk")
        self.assertEqual(note_id, 1)
        self.assertEqual(record.notes[0].id, 1)
        self.assertEqual(record.notes[0].value, "buy milk")
        self.assertEqual(record.notes[0].tags, [])

    def test_add_note_enforces_max_five_notes(self):
        record = Record("Alice")
        for index in range(Record.MAX_NOTES):
            record.add_note(f"note {index}")
        with self.assertRaisesRegex(ValueError, "at most 5 notes"):
            record.add_note("one too many")

    def test_remove_note_deletes_by_id(self):
        record = Record("Alice")
        record.add_note("buy milk")
        record.remove_note(1)
        self.assertEqual(record.notes, [])

    def test_edit_note_replaces_text_and_keeps_id(self):
        record = Record("Alice")
        record.add_note("buy milk")
        record.edit_note(1, "buy oat milk")
        self.assertEqual(record.notes[0].id, 1)
        self.assertEqual(record.notes[0].value, "buy oat milk")

    def test_edit_note_keeps_existing_tags(self):
        record = Record("Alice")
        record.add_note("buy milk")
        record.add_tags(1, "shopping")
        record.edit_note(1, "buy oat milk")
        self.assertEqual(record.notes[0].value, "buy oat milk")
        self.assertEqual([tag.value for tag in record.notes[0].tags], ["shopping"])

    def test_edit_note_requires_existing_id(self):
        record = Record("Alice")
        with self.assertRaisesRegex(ValueError, "Note with id 1 not found"):
            record.edit_note(1, "buy oat milk")

    def test_find_notes_by_query_matches_substring(self):
        record = Record("Olga")
        record.add_note("buy coffee now")
        matches = record.find_notes_by_query("cof")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].value, "buy coffee now")

    def test_find_notes_by_query_is_case_insensitive(self):
        record = Record("Olga")
        record.add_note("buy coffee")
        matches = record.find_notes_by_query("COF")
        self.assertEqual(matches[0].value, "buy coffee")

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

    def test_legacy_record_state_ensures_notes_have_tags_list(self):
        legacy_record = Record.__new__(Record)
        note = Note(1, "legacy note", tags=[])
        note.tags = []
        legacy_record.__setstate__(
            {
                "name": Name("Alice"),
                "phones": [],
                "birthday": None,
                "address": None,
                "email": None,
                "notes": [note],
                "_next_note_id": 2,
            }
        )
        self.assertEqual(legacy_record.notes[0].tags, [])


class RecordTagTests(unittest.TestCase):
    """Cover tag behavior on contact notes."""

    def test_add_tags_stores_normalized_tags(self):
        record = Record("Olga")
        record.add_note("buy coffee")
        record.add_tags(1, "#Shopping", "urgent")
        self.assertEqual(
            [tag.value for tag in record.notes[0].tags],
            ["shopping", "urgent"],
        )

    def test_add_tags_rejects_duplicate(self):
        record = Record("Olga")
        record.add_note("buy coffee")
        record.add_tags(1, "shopping")
        with self.assertRaisesRegex(ValueError, "already on note 1"):
            record.add_tags(1, "shopping")

    def test_add_tags_requires_existing_note_id(self):
        record = Record("Olga")
        with self.assertRaisesRegex(ValueError, "Note with id 1 not found"):
            record.add_tags(1, "shopping")

    def test_add_tags_enforces_max_tags_per_note(self):
        record = Record("Olga")
        record.add_note("buy coffee")
        for index in range(Record.MAX_TAGS_PER_NOTE):
            record.add_tags(1, f"tag{index}")
        with self.assertRaisesRegex(ValueError, "at most 5 tags"):
            record.add_tags(1, "extra")

    def test_remove_tag_deletes_existing_tag(self):
        record = Record("Olga")
        record.add_note("buy coffee")
        record.add_tags(1, "shopping", "urgent")
        record.remove_tag(1, "#shopping")
        self.assertEqual([tag.value for tag in record.notes[0].tags], ["urgent"])

    def test_remove_tag_requires_existing_tag(self):
        record = Record("Olga")
        record.add_note("buy coffee")
        with self.assertRaisesRegex(ValueError, "Tag not found"):
            record.remove_tag(1, "shopping")

    def test_find_notes_by_tag_supports_partial_match(self):
        record = Record("Olga")
        record.add_note("buy coffee")
        record.add_note("buy tea")
        record.add_tags(1, "shopping")
        record.add_tags(2, "work")
        matches = record.find_notes_by_tag("shop", partial=True)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].value, "buy coffee")

    def test_find_notes_by_tag_supports_exact_match(self):
        record = Record("Olga")
        record.add_note("buy coffee")
        record.add_note("buy tea")
        record.add_tags(1, "shopping")
        record.add_tags(2, "shop")
        matches = record.find_notes_by_tag("shop", partial=False)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].value, "buy tea")

    def test_sort_notes_by_tags_orders_tagged_notes_first(self):
        record = Record("Olga")
        record.add_note("no tags")
        record.add_note("work task")
        record.add_note("shop list")
        record.add_tags(2, "work")
        record.add_tags(3, "shopping")
        sorted_notes = record.sort_notes_by_tags()
        self.assertEqual(
            [note.value for note in sorted_notes],
            ["shop list", "work task", "no tags"],
        )


class NotesDisplayTests(unittest.TestCase):
    """Cover note formatting helpers used in tables and contact views."""

    def test_format_notes_for_display_shows_id_and_text(self):
        record = Record("Olga")
        record.add_note("buy milk")
        rendered = format_notes_for_display(record)
        self.assertIn("[note id: 1] buy milk", rendered)

    def test_format_notes_for_display_includes_tags(self):
        record = Record("Olga")
        record.add_note("buy coffee")
        record.add_tags(1, "shopping", "urgent")
        rendered = format_notes_for_display(record)
        self.assertIn("#shopping #urgent", rendered)


class NoteCommandTests(unittest.TestCase):
    """Cover note-related CLI handlers."""

    def test_add_note_handler_adds_note_to_contact(self):
        book = AddressBook()
        record = Record("Olga")
        book.add_record(record)

        result = add_note(["Olga", "buy", "milk"], book)

        self.assertEqual(result, "[green]Note added with id 1.[/green]")
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

        result, printed = _capture_table_output(find_note, ["Olga", "cof"], book)

        self.assertIsNone(result)
        self.assertEqual(len(printed), 1)
        self.assertEqual(printed[0].rows[0][0], "1")
        self.assertIn("buy coffee now", printed[0].rows[0][1])
        self.assertEqual(printed[0].rows[0][2], PLACEHOLDER)

    def test_all_notes_handler_prints_contact_notes(self):
        book = AddressBook()
        record = Record("Olga")
        record.add_note("buy milk")
        book.add_record(record)

        result, printed = _capture_table_output(all_notes, ["Olga"], book)

        self.assertIsNone(result)
        self.assertEqual(printed[0].rows[0][0], "1")
        self.assertEqual(printed[0].rows[0][1], f"{NOTE_BULLET} buy milk")
        self.assertEqual(printed[0].rows[0][2], PLACEHOLDER)

    def test_all_notes_handler_shows_tags_column(self):
        book = AddressBook()
        record = Record("Olga")
        record.add_note("buy coffee")
        record.add_tags(1, "shopping")
        book.add_record(record)

        _result, printed = _capture_table_output(all_notes, ["Olga"], book)

        self.assertEqual(printed[0].rows[0][2], "#shopping")

    def test_all_notes_handler_accepts_multi_word_contact_name(self):
        book = AddressBook()
        record = Record("Mary Jane")
        record.add_note("buy milk")
        book.add_record(record)

        result, printed = _capture_table_output(all_notes, ["Mary", "Jane"], book)

        self.assertIsNone(result)
        self.assertEqual(printed[0].title, "All notes for Mary Jane")

    def test_edit_note_handler_updates_note_by_id(self):
        book = AddressBook()
        record = Record("Olga")
        record.add_note("buy milk")
        book.add_record(record)

        result = edit_note(["Olga", "1", "buy oat milk"], book)

        self.assertEqual(result, "[green]Note 1 edited.[/green]")
        self.assertEqual(record.notes[0].value, "buy oat milk")

    def test_edit_note_handler_reports_missing_contact(self):
        book = AddressBook()
        result = edit_note(["Olga", "1", "buy oat milk"], book)
        self.assertEqual(result, "[red]Contact not found[/red]")

    def test_edit_note_handler_rejects_non_numeric_id(self):
        book = AddressBook()
        record = Record("Olga")
        record.add_note("buy milk")
        book.add_record(record)

        result = edit_note(["Olga", "buy milk", "buy oat milk"], book)

        self.assertEqual(result, "[red]Note id must be a positive integer.[/red]")

    def test_remove_note_handler_removes_note_by_id(self):
        book = AddressBook()
        record = Record("Olga")
        record.add_note("buy milk")
        book.add_record(record)

        result = remove_note(["Olga", "1"], book)

        self.assertEqual(result, "[green]Note 1 removed.[/green]")
        self.assertEqual(record.notes, [])

    def test_remove_note_handler_rejects_non_numeric_id(self):
        book = AddressBook()
        record = Record("Olga")
        record.add_note("buy milk")
        book.add_record(record)

        result = remove_note(["Olga", "buy milk"], book)

        self.assertEqual(result, "[red]Note id must be a positive integer.[/red]")
        self.assertEqual(len(record.notes), 1)


class TagCommandTests(unittest.TestCase):
    """Cover tag-related CLI handlers."""

    def test_add_tag_handler_adds_tags_to_note(self):
        book = AddressBook()
        record = Record("Olga")
        record.add_note("buy coffee")
        book.add_record(record)

        result = add_tag(["Olga", "1", "#shopping", "#urgent"], book)

        self.assertEqual(result, "[green]Tags added to note 1.[/green]")
        self.assertEqual(
            [tag.value for tag in record.notes[0].tags],
            ["shopping", "urgent"],
        )

    def test_add_tag_handler_rejects_token_without_hash(self):
        book = AddressBook()
        record = Record("Olga")
        record.add_note("buy coffee")
        book.add_record(record)

        result = add_tag(["Olga", "1", "shopping"], book)

        self.assertEqual(
            result,
            "[red]Each tag must start with #, e.g. #shopping[/red]",
        )

    def test_add_tag_handler_reports_missing_note_id(self):
        book = AddressBook()
        record = Record("Olga")
        record.add_note("buy coffee")
        book.add_record(record)

        result = add_tag(["Olga", "9", "#shopping"], book)

        self.assertEqual(result, "[red]Note with id 9 not found[/red]")

    def test_remove_tag_handler_removes_tag_from_note(self):
        book = AddressBook()
        record = Record("Olga")
        record.add_note("buy coffee")
        record.add_tags(1, "shopping", "urgent")
        book.add_record(record)

        result = remove_tag(["Olga", "1", "#shopping"], book)

        self.assertEqual(
            result,
            "[green]Tag #shopping removed from note 1.[/green]",
        )
        self.assertEqual([tag.value for tag in record.notes[0].tags], ["urgent"])

    def test_remove_tag_handler_rejects_token_without_hash(self):
        book = AddressBook()
        record = Record("Olga")
        record.add_note("buy coffee")
        record.add_tags(1, "shopping")
        book.add_record(record)

        result = remove_tag(["Olga", "1", "shopping"], book)

        self.assertEqual(
            result,
            "[red]Each tag must start with #, e.g. #shopping[/red]",
        )

    def test_find_notes_by_tag_handler_prints_matches(self):
        book = AddressBook()
        record = Record("Olga")
        record.add_note("buy coffee")
        record.add_tags(1, "shopping")
        book.add_record(record)

        result, printed = _capture_table_output(
            find_notes_by_tag,
            ["Olga", "#shop"],
            book,
        )

        self.assertIsNone(result)
        self.assertEqual(len(printed[0].rows), 1)
        self.assertIn("#shopping", printed[0].rows[0][2])

    def test_find_notes_by_tag_handler_reports_no_matches(self):
        book = AddressBook()
        record = Record("Olga")
        record.add_note("buy coffee")
        book.add_record(record)

        result = find_notes_by_tag(["Olga", "#shop"], book)

        self.assertIn("No notes with tag matching", result)

    def test_sort_notes_by_tag_handler_prints_sorted_notes(self):
        book = AddressBook()
        record = Record("Olga")
        record.add_note("plain note")
        record.add_note("shop list")
        record.add_tags(2, "shopping")
        book.add_record(record)

        result, printed = _capture_table_output(sort_notes_by_tag, ["Olga"], book)

        self.assertIsNone(result)
        self.assertEqual(
            [row[1] for row in printed[0].rows],
            [f"{NOTE_BULLET} shop list", f"{NOTE_BULLET} plain note"],
        )


class NotesSearchIntegrationTests(unittest.TestCase):
    """Cover global search matching note text and tags."""

    def test_search_global_query_matches_note_tag(self):
        book = AddressBook()
        record = Record("Olga")
        record.add_note("buy coffee")
        record.add_tags(1, "shopping")
        book.add_record(record)

        result, printed = _capture_table_output(search_contacts, ["shopping"], book)

        self.assertIsNone(result)
        self.assertEqual(printed[0].rows[0][0], "Olga")


if __name__ == "__main__":
    unittest.main()
