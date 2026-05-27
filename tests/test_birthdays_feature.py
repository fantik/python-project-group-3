"""Tests for upcoming birthday calculations."""

from datetime import datetime
import unittest
from unittest.mock import patch

from models import AddressBook, Record


class FakeNonLeapDateTime(datetime):
    """Fixed current date in a non-leap year for birthday tests."""

    @classmethod
    def today(cls):
        return cls(2025, 2, 22)


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
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
