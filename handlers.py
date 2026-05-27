"""CLI command handlers and input parsing."""

from functools import wraps

from rich.console import Console
from rich.table import Table

from models import Record
from validators import ContactNotFoundError, validate_name

console = Console()


def parse_input(user_input):
    """Split user input into command and arguments."""
    cmd, *args = user_input.split()
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


@input_error
def add_contact(args, book):
    """Add or update a contact with a phone number."""
    name, phone, *_ = args
    record = book.find(name)

    if not record:
        record = Record(name)
        book.add_record(record)
        message = "[green]Contact added.[/green]"
    else:
        message = "[green]Contact updated.[/green]"

    record.add_phone(phone)
    return message


@input_error
def show_phone(args, book):
    """Show all phone numbers for a contact."""
    name = args[0]
    record = book.find(name)

    if record is None:
        return "[red]Contact not found[/red]"

    phones = "; ".join(phone.value for phone in record.phones)
    return (
        f"[green]The {name.capitalize()}'s phones are:  {phones}[/green]"
    )


@input_error
def show_all(book):
    """Print a table of all contacts."""
    if not book.data:
        return "[red]No contacts found[/red]"

    table = Table(title="Contacts")
    table.add_column("Name", style="cyan")
    table.add_column("Phones", style="green")
    table.add_column("Birthday", style="yellow")
    table.add_column("Address", style="magenta")
    table.add_column("Email", style="blue")

    for record in book.data.values():
        phones = "; ".join(phone.value for phone in record.phones)

        birthday = (
            record.birthday.value.strftime("%d.%m.%Y")
            if record.birthday
            else "-"
        )
        address_field = getattr(record, "address", None)
        address = address_field.value if address_field else "-"
        email_field = getattr(record, "email", None)
        email = email_field.value if email_field else "-"

        table.add_row(
            record.name.value,
            phones,
            birthday,
            address,
            email,
        )

    console.print(table)


@input_error
def add_birthday(args, book):
    """Set a contact's birthday."""
    name, birthday = args
    record = book.find(name)

    if record is None:
        return "[red]Contact not found[/red]"

    record.add_birthday(birthday)
    return "[green]Birthday added.[/green]"


@input_error
def add_address(args, book):
    """Set a contact's address."""
    require_min_args(args, 2, "add-address [name] [address]")
    name = args[0]
    address = " ".join(args[1:])
    record = book.find(name)

    if record is None:
        return "[red]Contact not found[/red]"

    record.add_address(address)
    return "[green]Address added.[/green]"


@input_error
def add_email(args, book):
    """Set a contact's email."""
    require_min_args(args, 2, "add-email [name] [email]")
    name = args[0]
    email = " ".join(args[1:])
    record = book.find(name)

    if record is None:
        return "[red]Contact not found[/red]"

    record.add_email(email)
    return "[green]Email added.[/green]"


@input_error
def show_birthday(args, book):
    """Show a contact's birthday."""
    name = args[0]
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


@input_error
def edit_contact(args, book):
    """Update a contact field (name, email, address, phone, or birthday)."""
    require_min_args(
        args,
        3,
        "edit-contact [name] [field] [value...]",
    )
    name = args[0]
    field = args[1].lower()
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
        new_birthday = args[2]
        record.edit_birthday(new_birthday)
        return "[green]Birthday updated.[/green]"

    if field == "phone":
        if len(args) < 4:
            raise ValueError(
                "[red]Usage: edit-contact \\[name] phone \\[old_phone] \\[new_phone][/red]"
            )
        old_phone, new_phone = args[2], args[3]
        record.edit_phone(old_phone, new_phone)
        return "[green]Phone updated.[/green]"

    return None


@input_error
def birthdays(book):
    """Print upcoming birthdays within the next 7 days."""
    upcoming = book.get_upcoming_birthdays()

    if not upcoming:
        return "[yellow]No upcoming birthdays[/yellow]"

    table = Table(title="Upcoming birthdays")
    table.add_column("Name", style="cyan")
    table.add_column("Congratulations date", style="green")

    for item in upcoming:
        table.add_row(
            item["name"],
            item["congratulation_date"],
        )

    console.print(table)
