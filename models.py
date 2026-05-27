"""Domain models for contacts and the address book."""

from collections import UserDict
from datetime import datetime, timedelta

from validators import (
    validate_address,
    validate_birthday,
    validate_email,
    validate_name,
    validate_phone,
)


class Field:
    """Base field wrapping a single value."""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    """Contact name field validated via the shared validator."""

    def __init__(self, value):
        super().__init__(validate_name(value))


class Phone(Field):
    """Phone number field for Ukrainian phone numbers."""

    def __init__(self, value):
        super().__init__(validate_phone(value))


class Birthday(Field):
    """Birthday field stored as datetime (DD.MM.YYYY input)."""

    def __init__(self, value):
        super().__init__(validate_birthday(value))


class Address(Field):
    """Address field validated via the shared validator."""

    def __init__(self, value):
        super().__init__(validate_address(value))


class Email(Field):
    """Email field validated via the shared validator."""

    def __init__(self, value):
        super().__init__(validate_email(value))


class Record:
    """A single contact with name, phones, and optional metadata."""

    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
        self.address = None
        self.email = None

    def __setstate__(self, state):
        """Restore older pickled records that do not have new fields yet."""
        self.__dict__.update(state)
        if "address" not in state:
            self.address = None
        if "email" not in state:
            self.email = None

    def add_phone(self, phone):
        """Append a validated phone number to this contact."""
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        """Remove a phone number by its value."""
        normalized_phone = validate_phone(phone)
        for ph in self.phones:
            if ph.value == normalized_phone:
                self.phones.remove(ph)
                return
        raise ValueError("[red]Phone not found[/red]")

    def edit_phone(self, old_phone, new_phone):
        """Replace an existing phone number with a new one."""
        normalized_old_phone = validate_phone(old_phone)
        for i in range(len(self.phones)):
            if self.phones[i].value == normalized_old_phone:
                self.phones[i] = Phone(new_phone)
                return
        raise ValueError("[red]Old phone not found[/red]")

    def find_phone(self, phone):
        """Return phone value if found, else a ValueError instance."""
        normalized_phone = validate_phone(phone)
        for ph in self.phones:
            if ph.value == normalized_phone:
                return ph.value
        return ValueError("[red]The phone was not found in the list[/red]")

    def add_birthday(self, birthday):
        """Set the contact birthday from a DD.MM.YYYY string."""
        self.birthday = Birthday(birthday)

    def edit_birthday(self, birthday):
        """Replace the contact birthday from a DD.MM.YYYY string."""
        self.birthday = Birthday(birthday)

    def edit_name(self, new_name):
        """Replace the contact name."""
        self.name = Name(new_name)

    def add_address(self, address):
        """Set the contact address."""
        self.address = Address(address)

    def edit_address(self, address):
        """Replace an existing contact address."""
        if getattr(self, "address", None) is None:
            raise ValueError("[red]Address not set[/red]")
        self.address = Address(address)

    def add_email(self, email):
        """Set the contact email."""
        self.email = Email(email)

    def edit_email(self, email):
        """Replace an existing contact email."""
        if getattr(self, "email", None) is None:
            raise ValueError("[red]Email not set[/red]")
        self.email = Email(email)

    def __str__(self):
        phones = "; ".join(p.value for p in self.phones)
        birthday = (
            self.birthday.value.strftime("%d.%m.%Y")
            if self.birthday
            else "None"
        )
        address_field = getattr(self, "address", None)
        address = address_field.value if address_field else "None"
        email_field = getattr(self, "email", None)
        email = email_field.value if email_field else "None"
        return (
            f"Contact name: {self.name.value}, phones: {phones}, "
            f"birthday: {birthday}, address: {address}, email: {email}"
        )


def _birthday_for_year(birthday, year):
    """Project a birthday into a target year, handling Feb 29 safely."""
    try:
        return birthday.replace(year=year)
    except ValueError:
        if birthday.month == 2 and birthday.day == 29:
            return birthday.replace(year=year, day=28)
        raise


class AddressBook(UserDict):
    """UserDict-backed storage for contact records."""

    def add_record(self, record):
        """Store a record keyed by contact name."""
        self.data[record.name.value] = record

    def find(self, name):
        """Return a record by name, or None."""
        return self.data.get(name)

    def delete(self, name):
        """Remove a record by name."""
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError("[red]Record not found[/red]")

    def get_upcoming_birthdays(self):
        """Return contacts with birthdays in the next 7 days."""
        results = []
        today = datetime.today().date()

        for record in self.data.values():
            if not record.birthday:
                continue

            birthday = record.birthday.value.date()
            birthday_this_year = _birthday_for_year(birthday, today.year)

            if birthday_this_year < today:
                birthday_this_year = _birthday_for_year(
                    birthday, today.year + 1
                )

            day_difference = (birthday_this_year - today).days
            if 0 <= day_difference <= 7:
                birth_date = birthday_this_year

                # Saturday -> Monday (+2); Sunday -> Monday (+1)
                if birth_date.weekday() == 5:
                    birth_date = birth_date + timedelta(days=2)
                elif birth_date.weekday() == 6:
                    birth_date = birth_date + timedelta(days=1)

                results.append(
                    {
                        "name": record.name.value,
                        "congratulation_date": birth_date.strftime(
                            "%d.%m.%Y"
                        ),
                    }
                )

        return results
