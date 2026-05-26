"""Domain models for contacts and the address book."""

from collections import UserDict
from datetime import datetime, timedelta


class Field:
    """Base field wrapping a single value."""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    """Contact name field with non-empty validation."""

    def __init__(self, value):
        if value == "" or value is None:
            raise ValueError("Name can't be empty")
        super().__init__(value)


class Phone(Field):
    """Phone number field (10 digits)."""

    def __init__(self, value):
        if len(value) != 10:
            raise ValueError("[red]Phone must be 10 digits[/red]")

        if not value.isdigit():
            raise ValueError("[red]Phone must have only digits[/red]")

        super().__init__(value)


class Birthday(Field):
    """Birthday field stored as datetime (DD.MM.YYYY input)."""

    def __init__(self, value):
        try:
            parsed_date = datetime.strptime(value, "%d.%m.%Y")
            super().__init__(parsed_date)
        except ValueError:
            raise ValueError(
                "[red]Invalid date format. Use DD.MM.YYYY[/red]"
            )


class Record:
    """A single contact with name, phones, and optional birthday."""

    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        """Append a validated phone number to this contact."""
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        """Remove a phone number by its value."""
        for ph in self.phones:
            if ph.value == phone:
                self.phones.remove(ph)
                return
        raise ValueError("[red]Phone not found[/red]")

    def edit_phone(self, old_phone, new_phone):
        """Replace an existing phone number with a new one."""
        for i in range(len(self.phones)):
            if self.phones[i].value == old_phone:
                self.phones[i] = Phone(new_phone)
                return
        raise ValueError("[red]Old phone not found[/red]")

    def find_phone(self, phone):
        """Return phone value if found, else a ValueError instance."""
        for ph in self.phones:
            if ph.value == phone:
                return ph.value
        return ValueError("[red]The phone was not found in the list[/red]")

    def add_birthday(self, birthday):
        """Set the contact birthday from a DD.MM.YYYY string."""
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = "; ".join(p.value for p in self.phones)
        birthday = (
            self.birthday.value.strftime("%d.%m.%Y")
            if self.birthday
            else "None"
        )
        return (
            f"Contact name: {self.name.value}, phones: {phones}, "
            f"birthday: {birthday}"
        )


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
            birthday_this_year = birthday.replace(year=today.year)

            if birthday_this_year < today:
                birthday_this_year = birthday.replace(year=today.year + 1)

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
