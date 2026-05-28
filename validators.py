"""Validation helpers shared across contact fields."""

from datetime import datetime
import re


class ContactNotFoundError(Exception):
    """Raised when a CLI command targets a missing contact."""

    def __str__(self):
        return "[red]Contact not found[/red]"


EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+"
    r"@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+$"
)


def validate_name(name):
    """Return a trimmed name or raise when it has fewer than two letters."""
    cleaned_name = name.strip() if name is not None else ""

    if sum(1 for char in cleaned_name if char.isalpha()) < 2:
        raise ValueError(
            "[red]Name must contain at least 2 letters[/red]"
        )

    return cleaned_name


def validate_address(address):
    """Return a trimmed address or raise when it is too short."""
    cleaned_address = address.strip() if address is not None else ""

    if len(cleaned_address) < 3:
        raise ValueError(
            "[red]Address must be at least 3 characters[/red]"
        )

    return cleaned_address


def validate_phone(phone):
    """Return a normalized Ukrainian phone number or raise ValueError."""
    cleaned_phone = phone.strip() if phone is not None else ""
    normalized_phone = re.sub(r"[\s()-]", "", cleaned_phone)

    if re.fullmatch(r"0\d{9}", normalized_phone):
        return normalized_phone

    if re.fullmatch(r"380\d{9}", normalized_phone):
        return f"0{normalized_phone[3:]}"

    if re.fullmatch(r"\+380\d{9}", normalized_phone):
        return f"0{normalized_phone[4:]}"

    raise ValueError(
        "[red]Phone must be a valid Ukrainian number "
        "(0XXXXXXXXX, 380XXXXXXXXX, or +380XXXXXXXXX)[/red]"
    )


def validate_email(email):
    """Return a normalized email or raise when the format is invalid."""
    cleaned_email = email.strip() if email is not None else ""

    if not EMAIL_PATTERN.fullmatch(cleaned_email):
        raise ValueError("[red]Invalid email format[/red]")

    return cleaned_email


def validate_birthday(date):
    """Return a parsed birthday or raise when the value is invalid."""
    cleaned_date = date.strip() if date is not None else ""

    try:
        parsed_date = datetime.strptime(cleaned_date, "%d.%m.%Y")
    except ValueError:
        raise ValueError("[red]Invalid date format. Use DD.MM.YYYY[/red]")

    if parsed_date.date() > datetime.today().date():
        raise ValueError("[red]Birthday cannot be in the future[/red]")

    return parsed_date

def validate_note(note):
    """Return a trimmed note or raise when it is too short."""
    cleaned_note = note.strip() if note is not None else ""

    if len(cleaned_note) < 3:
        raise ValueError(
            "[red]Note must be at least 3 characters[/red]"
        )

    if len(cleaned_note) > 100:
        raise ValueError(
            "[red]Note must be less than 100 characters[/red]"
        )

    return cleaned_note
