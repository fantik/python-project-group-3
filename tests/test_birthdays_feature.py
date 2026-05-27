"""Tests for upcoming birthday calculations."""

from datetime import datetime
import unittest
from unittest.mock import patch

from tests._rich_stub import ensure_rich_stub

ensure_rich_stub()

from handlers import birthdays
from models import AddressBook, Record


class FakeNonLeapDateTime(datetime):
    """Fixed current date in a non-leap year for birthday tests."""

    @classmethod
    def today(cls):
        return cls(2025, 2, 22)


class FakeRangeDateTime(datetime):
    """Fixed current date for range-based birthday handler tests."""

    @classmethod
    def today(cls):
        return cls(2025, 5, 27)


class CapturingTable:
    """Minimal Rich Table test double that captures columns and rows."""

    def __init__(self, title=None):
        self.title = title
        self.columns = []
        self.rows = []

    def add_column(self, name, style=None):
        self.columns.append((name, style))

    def add_row(self, *values):
        self.rows.append(values)


class BirthdayFeatureTests(unittest.TestCase):
    """Cover edge cases in the birthday reminder logic."""

    def test_leap_day_birthday_does_not_crash_in_non_leap_year(self):
        book = AddressBook()
        record = Record("Leap")
        record.add_birthday("29.02.2000")
        book.add_record(record)

        with patch("models.datetime", FakeNonLeapDateTime):
            upcoming = book.get_upcoming_birthdays()

        self.assertEqual(
            upcoming,
            [
                {
                    "name": "Leap",
                    "congratulation_date": "28.02.2025",
                    "days_left": 6,
                }
            ],
        )

    def test_get_upcoming_birthdays_accepts_custom_day_range(self):
        book = AddressBook()

        soon = Record("Soon")
        soon.add_birthday("30.05.2000")
        book.add_record(soon)

        later = Record("Later")
        later.add_birthday("08.06.2000")
        book.add_record(later)

        with patch("models.datetime", FakeRangeDateTime):
            upcoming = book.get_upcoming_birthdays(14)

        self.assertEqual(
            upcoming,
            [
                {
                    "name": "Soon",
                    "congratulation_date": "30.05.2025",
                    "days_left": 3,
                },
                {
                    "name": "Later",
                    "congratulation_date": "09.06.2025",
                    "days_left": 12,
                },
            ],
        )


class BirthdayHandlerTests(unittest.TestCase):
    """Cover CLI behavior for the birthdays command."""

    def test_birthdays_handler_defaults_to_seven_days(self):
        book = AddressBook()

        soon = Record("Soon")
        soon.add_birthday("30.05.2000")
        book.add_record(soon)

        later = Record("Later")
        later.add_birthday("08.06.2000")
        book.add_record(later)

        printed = []

        with (
            patch("handlers.Table", CapturingTable),
            patch("handlers.console.print", side_effect=printed.append),
            patch("models.datetime", FakeRangeDateTime),
        ):
            result = birthdays([], book)

        self.assertIsNone(result)
        self.assertEqual(len(printed), 1)
        self.assertEqual(printed[0].rows, [("Soon", "30.05.2025", "3")])

    def test_birthdays_handler_accepts_custom_range(self):
        book = AddressBook()

        soon = Record("Soon")
        soon.add_birthday("30.05.2000")
        book.add_record(soon)

        later = Record("Later")
        later.add_birthday("08.06.2000")
        book.add_record(later)

        printed = []

        with (
            patch("handlers.Table", CapturingTable),
            patch("handlers.console.print", side_effect=printed.append),
            patch("models.datetime", FakeRangeDateTime),
        ):
            result = birthdays(["14"], book)

        self.assertIsNone(result)
        self.assertEqual(
            printed[0].rows,
            [
                ("Soon", "30.05.2025", "3"),
                ("Later", "09.06.2025", "12"),
            ],
        )

    def test_birthdays_handler_rejects_invalid_days_argument(self):
        book = AddressBook()

        result = birthdays(["abc"], book)

        self.assertEqual(result, "[red]Days must be a positive integer[/red]")


if __name__ == "__main__":
    unittest.main()
