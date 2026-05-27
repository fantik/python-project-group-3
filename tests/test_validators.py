"""Tests for shared validation helpers."""

from datetime import datetime, timedelta
import unittest

from models import Birthday, Phone, Record
from validators import validate_birthday, validate_email, validate_phone


class PhoneValidatorTests(unittest.TestCase):
    """Cover Ukrainian phone validation rules."""

    def test_validate_phone_accepts_local_ukrainian_number(self):
        self.assertEqual(validate_phone("0671234567"), "0671234567")

    def test_validate_phone_accepts_country_code_without_plus(self):
        self.assertEqual(validate_phone("380671234567"), "0671234567")

    def test_validate_phone_accepts_country_code_with_plus(self):
        self.assertEqual(validate_phone("+380671234567"), "0671234567")

    def test_validate_phone_rejects_invalid_number(self):
        with self.assertRaisesRegex(
            ValueError, "Phone must be a valid Ukrainian number"
        ):
            validate_phone("12345")

    def test_phone_model_uses_normalized_validator_output(self):
        self.assertEqual(Phone("+380671234567").value, "0671234567")


class PhoneRecordTests(unittest.TestCase):
    """Cover phone operations after normalization."""

    def test_find_phone_accepts_alternative_ukrainian_formats(self):
        record = Record("Alice")
        record.add_phone("+380671234567")

        self.assertEqual(record.find_phone("380671234567"), "0671234567")

    def test_edit_phone_accepts_original_plus_format(self):
        record = Record("Alice")
        record.add_phone("+380671234567")

        record.edit_phone("+380671234567", "0501234567")

        self.assertEqual(record.phones[0].value, "0501234567")

    def test_remove_phone_accepts_original_plus_format(self):
        record = Record("Alice")
        record.add_phone("+380671234567")

        record.remove_phone("+380671234567")

        self.assertEqual(record.phones, [])


class BirthdayValidatorTests(unittest.TestCase):
    """Cover birthday validation rules."""

    def test_validate_birthday_accepts_past_date(self):
        parsed_date = validate_birthday("01.01.2000")

        self.assertEqual(parsed_date, datetime(2000, 1, 1))

    def test_validate_birthday_rejects_invalid_format(self):
        with self.assertRaisesRegex(
            ValueError, "Invalid date format. Use DD.MM.YYYY"
        ):
            validate_birthday("2000-01-01")

    def test_validate_birthday_rejects_future_date(self):
        future_date = (
            datetime.today() + timedelta(days=1)
        ).strftime("%d.%m.%Y")

        with self.assertRaisesRegex(
            ValueError, "Birthday cannot be in the future"
        ):
            validate_birthday(future_date)

    def test_birthday_model_rejects_future_date(self):
        future_date = (
            datetime.today() + timedelta(days=1)
        ).strftime("%d.%m.%Y")

        with self.assertRaisesRegex(
            ValueError, "Birthday cannot be in the future"
        ):
            Birthday(future_date)


class EmailValidatorTests(unittest.TestCase):
    """Cover shared email validation rules."""

    def test_validate_email_accepts_trimmed_email(self):
        self.assertEqual(
            validate_email("  alice@example.com  "),
            "alice@example.com",
        )

    def test_validate_email_rejects_invalid_value(self):
        with self.assertRaisesRegex(ValueError, "Invalid email format"):
            validate_email("alice.example.com")


if __name__ == "__main__":
    unittest.main()
