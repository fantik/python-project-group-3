"""CLI command handlers and input parsing."""

from functools import wraps
import shlex

from rich.console import Console
from rich.table import Table

from models import Record
from validators import (
    ContactNotFoundError,
    validate_address,
    validate_birthday,
    validate_email,
    validate_name,
    validate_phone,
)

console = Console()


def parse_input(user_input):
    """Split user input into command and arguments."""
    try:
        lexer = shlex.shlex(user_input, posix=True)
        lexer.whitespace_split = True
        lexer.commenters = ""
        lexer.quotes = '"'
        parts = list(lexer)
    except ValueError as exc:
        return "__parse_error__", str(exc)

    if not parts:
        return ("",)

    cmd, *args = parts
    cmd = cmd.strip().lower()
    return cmd, *args


def input_error(func):
    """Decorator that returns exception messages instead of raising."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return str(e)

    return wrapper


def require_min_args(args, count, usage):
    """Validate minimum CLI arity for handlers with free-form trailing text."""
    if len(args) < count:
        raise ValueError(f"[red]Usage: {usage}[/red]")


def join_name_parts(parts):
    """Join CLI tokens into a contact name."""
    return " ".join(parts).strip()


def resolve_unique_existing_name(args, book):
    """Resolve a unique existing contact name prefix from CLI tokens."""
    matches = []
    for index in range(1, len(args)):
        name = join_name_parts(args[:index])
        record = book.find(name)
        if record is not None:
            matches.append((name, record, args[index:]))

    if not matches:
        return None, None, []

    if len(matches) > 1:
        raise ValueError(
            "[red]Ambiguous contact name. Please use a unique name.[/red]"
        )

    return matches[0]


@input_error
def add_contact(args, book):
    """Add or update a contact with a phone number."""
    require_min_args(args, 2, "add [name] [phone]")
    name = join_name_parts(args[:-1])
    phone = args[-1]
    record = book.find(name)

    if not record:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
        return "[green]Contact added.[/green]"

    record.add_phone(phone)
    return "[green]Contact updated.[/green]"


@input_error
def show_phone(args, book):
    """Show all phone numbers for a contact."""
    require_min_args(args, 1, "phone [name]")
    name = join_name_parts(args)
    record = book.find(name)

    if record is None:
        return "[red]Contact not found[/red]"

    phones = "; ".join(phone.value for phone in record.phones)
    return (
        f"[green]The {record.name.value}'s phones are:  {phones}[/green]"
    )


@input_error
def show_all(book):
    """Print a table of all contacts."""
    if not book.data:
        return "[red]No contacts found[/red]"

    placeholder = "—"
    table = Table(title="Contacts")
    table.add_column("Name", style="cyan")
    table.add_column("Phones", style="green")
    table.add_column("Email", style="blue")
    table.add_column("Address", style="magenta")
    table.add_column("Birthday", style="yellow")
    table.add_column("Days to birthday", style="bright_yellow")

    for record in book.data.values():
        phones = "; ".join(phone.value for phone in record.phones)
        phones = phones or placeholder

        email_field = getattr(record, "email", None)
        email = email_field.value if email_field else placeholder

        address_field = getattr(record, "address", None)
        address = address_field.value if address_field else placeholder

        birthday_value = (
            record.birthday.value.strftime("%d.%m.%Y")
            if record.birthday
            else placeholder
        )
        days_to_birthday = record.days_to_birthday()
        days_to_birthday = (
            str(days_to_birthday)
            if days_to_birthday is not None
            else placeholder
        )

        table.add_row(
            record.name.value,
            phones,
            email,
            address,
            birthday_value,
            days_to_birthday,
        )

    console.print(table)


@input_error
def add_birthday(args, book):
    """Set a contact's birthday."""
    require_min_args(args, 2, "add-birthday [name] [birthday]")
    name = join_name_parts(args[:-1])
    birthday = args[-1]
    record = book.find(name)

    if record is None:
        return "[red]Contact not found[/red]"

    record.add_birthday(birthday)
    return "[green]Birthday added.[/green]"


@input_error
def add_address(args, book):
    """Set a contact's address."""
    require_min_args(args, 2, "add-address [name] [address]")
    name, record, address_tokens = resolve_unique_existing_name(args, book)

    if record is None:
        return "[red]Contact not found[/red]"

    address = " ".join(address_tokens)
    record.add_address(address)
    return "[green]Address added.[/green]"


@input_error
def add_email(args, book):
    """Set a contact's email."""
    require_min_args(args, 2, "add-email [name] [email]")
    name = join_name_parts(args[:-1])
    email = args[-1]
    record = book.find(name)

    if record is None:
        return "[red]Contact not found[/red]"

    record.add_email(email)
    return "[green]Email added.[/green]"


@input_error
def show_birthday(args, book):
    """Show a contact's birthday."""
    require_min_args(args, 1, "show-birthday [name]")
    name = join_name_parts(args)
    record = book.find(name)

    if record is None:
        return "[red]Contact not found[/red]"

    if record.birthday is None:
        return "[red]Birthday not set[/red]"

    return (
        f"[green]{name}'s birthday: [/green]"
        f"[green]{record.birthday.value.strftime('%d.%m.%Y')}[/green]"
    )


_EDIT_CONTACT_FIELDS = frozenset(
    {"name", "email", "address", "phone", "birthday"}
)


def _has_plausible_later_edit_parse(args, start_index=2):
    """Return True when later tokens look like a valid alternate edit split."""
    for index in range(start_index, len(args)):
        field = args[index].lower()
        if field not in _EDIT_CONTACT_FIELDS:
            continue

        value_tokens = args[index + 1 :]
        try:
            if field == "name" and value_tokens:
                validate_name(" ".join(value_tokens))
                return True

            if field == "email" and value_tokens:
                validate_email(" ".join(value_tokens))
                return True

            if field == "address" and value_tokens:
                validate_address(" ".join(value_tokens))
                return True

            if field == "birthday" and len(value_tokens) == 1:
                validate_birthday(value_tokens[0])
                return True

            if field == "phone" and len(value_tokens) >= 2:
                validate_phone(value_tokens[0])
                validate_phone(value_tokens[1])
                return True
        except ValueError:
            continue

    return False


@input_error
def edit_contact(args, book):
    """Update a contact field (name, email, address, phone, or birthday)."""
    require_min_args(
        args,
        3,
        "edit-contact [name] [field] [value...]",
    )

    candidates = []
    for index in range(1, len(args)):
        raw_field_token = args[index]
        field_token = raw_field_token.lower()
        if field_token not in _EDIT_CONTACT_FIELDS:
            continue

        name = join_name_parts(args[:index])
        record = book.find(name)
        if record is not None:
            if (
                raw_field_token != field_token
                and _has_plausible_later_edit_parse(args, index + 1)
            ):
                continue
            candidates.append((name, field_token, args[index + 1 :], record))

    if len(candidates) > 1:
        raise ValueError(
            "[red]Ambiguous contact name. Please use quotes for multi-word names.[/red]"
        )

    if len(candidates) == 1:
        name, field, value_tokens, record = candidates[0]
        args = [name, field, *value_tokens]
    else:
        name = args[0]
        raw_field = args[1]
        normalized_field = raw_field.lower()
        later_field_exists = any(
            token.lower() in _EDIT_CONTACT_FIELDS for token in args[2:]
        )
        if normalized_field in _EDIT_CONTACT_FIELDS:
            if (
                raw_field != normalized_field
                and _has_plausible_later_edit_parse(args)
            ):
                raise ContactNotFoundError()
        elif later_field_exists:
            raise ContactNotFoundError()
        field = normalized_field
        record = book.find(name)

    if record is None:
        raise ContactNotFoundError()

    if field not in _EDIT_CONTACT_FIELDS:
        fields = ", ".join(sorted(_EDIT_CONTACT_FIELDS))
        raise ValueError(
            f"[red]Unknown field '{field}'. "
            f"Use one of: {fields}[/red]"
        )

    if field == "name":
        new_name = validate_name(" ".join(args[2:]))
        if book.find(new_name) and new_name != record.name.value:
            raise ValueError(
                "[red]Contact with this name already exists[/red]"
            )
        record.edit_name(new_name)
        del book.data[name]
        book.add_record(record)
        return "[green]Name updated.[/green]"

    if field == "email":
        new_email = " ".join(args[2:])
        if record.email is None:
            record.add_email(new_email)
        else:
            record.edit_email(new_email)
        return "[green]Email updated.[/green]"

    if field == "address":
        new_address = " ".join(args[2:])
        if record.address is None:
            record.add_address(new_address)
        else:
            record.edit_address(new_address)
        return "[green]Address updated.[/green]"

    if field == "birthday":
        if len(args) != 3:
            raise ValueError(
                "[red]Usage: edit-contact [name] birthday [date][/red]"
            )
        new_birthday = args[2]
        record.edit_birthday(new_birthday)
        return "[green]Birthday updated.[/green]"

    if field == "phone":
        if len(args) != 4:
            raise ValueError(
                "[red]Usage: edit-contact [name] phone [old_phone] [new_phone][/red]"
            )
        old_phone, new_phone = args[2], args[3]
        record.edit_phone(old_phone, new_phone)
        return "[green]Phone updated.[/green]"

    return None


@input_error
def birthdays(args, book):
    """Print upcoming birthdays within the next N days."""
    require_min_args(args, 0, "birthdays [days]")

    if len(args) > 1:
        raise ValueError("[red]Usage: birthdays [days][/red]")

    days = 7
    if args:
        try:
            days = int(args[0])
        except ValueError:
            raise ValueError("[red]Days must be a positive integer[/red]")

        if days < 1:
            raise ValueError("[red]Days must be a positive integer[/red]")

    upcoming = book.get_upcoming_birthdays(days)

    if not upcoming:
        return (
            f"[yellow]No upcoming birthdays in the next {days} days[/yellow]"
        )

    table = Table(title="Upcoming birthdays")
    table.add_column("Name", style="cyan")
    table.add_column("Congratulations date", style="green")
    table.add_column("Days left", style="yellow")

    for item in upcoming:
        table.add_row(
            item["name"],
            item["congratulation_date"],
            str(item["days_left"]),
        )

    console.print(table)
