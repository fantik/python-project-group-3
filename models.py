"""Domain models for contacts and the address book."""

from collections import UserDict
from datetime import datetime, timedelta

from validators import (
    validate_address,
    validate_birthday,
    validate_email,
    validate_name,
    validate_phone,
    validate_note,
    validate_tag
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

class Tag(Field):
    """Tag field validated via the shared validator."""

    def __init__(self, value):
        super().__init__(validate_tag(value))

class Note:
    """Contact note with a per-contact numeric id, text, and optional tags."""

    def __init__(self, note_id, text, tags=None):
        self.id = int(note_id)
        self.text = validate_note(text)
        self.tags = [Tag(tag) for tag in (tags or [])]

    @property
    def value(self):
        """Read-only alias for note text used in display helpers."""
        return self.text

    @value.setter
    def value(self, new_text):
        self.text = validate_note(new_text)


class Record:
    """A single contact with name, phones, notes and optional metadata."""

    MAX_NOTES = 5
    MAX_TAGS_PER_NOTE = 5

    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
        self.address = None
        self.email = None
        self.notes = []
        self._next_note_id = 1

    def __setstate__(self, state):
        """Restore older pickled records that do not have new fields yet."""
        self.__dict__.update(state)
        if "address" not in state:
            self.address = None
        if "email" not in state:
            self.email = None
        if "notes" not in state:
            self.notes = []
        if "_next_note_id" not in state:
            self._next_note_id = max((note.id for note in self.notes), default=0) + 1
        for note in self.notes:
            if not getattr(note, "tags", None):
                note.tags = []

    def _get_note_by_id(self, note_id):
        """Return a note by id or raise ValueError."""
        for item in self.notes:
            if item.id == int(note_id):
                return item
        raise ValueError(f"[red]Note with id {note_id} not found[/red]")

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
        """Return phone value if found, else raise ValueError."""
        normalized_phone = validate_phone(phone)
        for ph in self.phones:
            if ph.value == normalized_phone:
                return ph.value
        raise ValueError("[red]The phone was not found in the list[/red]")

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

    def add_note(self, note):
        """Append a validated note to this contact and return its id."""
        if len(self.notes) >= self.MAX_NOTES:
            raise ValueError(
                f"[red]A contact can have at most {self.MAX_NOTES} notes[/red]"
            )
        note_id = self._next_note_id
        self._next_note_id += 1
        self.notes.append(Note(note_id, note, tags=[]))
        return note_id

    def remove_note(self, note_id):
        """Remove a note by its id."""
        self.notes.remove(self._get_note_by_id(note_id))

    def edit_note(self, note_id, new_note):
        """Replace a note's text by id."""
        self._get_note_by_id(note_id).value = new_note

    def find_notes_by_query(self, query):
        """Return notes whose text contains the query (case-insensitive)."""
        part = (query or "").strip().lower()
        if not part:
            return []
        return [
            item
            for item in self.notes
            if part in item.value.lower()
        ]

    def add_tags(self, note_id, *tags):
        """Add one or more tags to a note identified by id."""
        note = self._get_note_by_id(note_id)
        for tag in tags:
            normalized_tag = validate_tag(tag)
            if any(item.value == normalized_tag for item in note.tags):
                raise ValueError(
                    f"[red]Tag '{normalized_tag}' already on note {note_id}[/red]"
                )
            if len(note.tags) >= self.MAX_TAGS_PER_NOTE:
                raise ValueError(
                    f"[red]A note can have at most "
                    f"{self.MAX_TAGS_PER_NOTE} tags[/red]"
                )
            note.tags.append(Tag(normalized_tag))

    def remove_tag(self, note_id, tag):
        """Remove a tag from a note identified by id."""
        note = self._get_note_by_id(note_id)
        normalized_tag = validate_tag(tag)
        for item in note.tags:
            if item.value == normalized_tag:
                note.tags.remove(item)
                return
        raise ValueError("[red]Tag not found[/red]")

    def find_notes_by_tag(self, tag, *, partial=True):
        """Return notes that contain a tag (partial match by default)."""
        query = (tag or "").strip().lstrip("#").lower()
        if not query:
            return []

        if partial:
            return [
                note
                for note in self.notes
                if any(query in item.value for item in note.tags)
            ]

        normalized_tag = validate_tag(tag)
        return [
            note
            for note in self.notes
            if any(item.value == normalized_tag for item in note.tags)
        ]

    def sort_notes_by_tags(self):
        """Return notes sorted by first tag, then untagged notes by id."""
        def sort_key(note):
            if note.tags:
                return (0, note.tags[0].value, note.id)
            return (1, "", note.id)

        return sorted(self.notes, key=sort_key)

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
        notes = "; ".join(n.value for n in self.notes) or "None"
        return (
            f"Contact name: {self.name.value}, phones: {phones}, "
            f"birthday: {birthday}, address: {address}, email: {email}, "
            f"notes: {notes}"
        )

    def days_to_birthday(self, today=None):
        """Return days until the next birthday, or None if not set."""
        if self.birthday is None:
            return None

        today = today or datetime.today().date()
        birthday = self.birthday.value.date()
        next_birthday = _birthday_for_year(birthday, today.year)

        if next_birthday < today:
            next_birthday = _birthday_for_year(birthday, today.year + 1)

        return (next_birthday - today).days


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

    def get_upcoming_birthdays(self, days=7):
        """Return contacts with birthdays in the next ``days`` days."""
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
            if 0 <= day_difference <= days:
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
                        "days_left": day_difference,
                    }
                )

        return results
