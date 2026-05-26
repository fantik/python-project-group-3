"""CLI command handlers and input parsing."""

from functools import wraps

from rich.console import Console
from rich.table import Table

from models import Record

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
def change_contact(args, book):
    """Change one phone number for an existing contact."""
    name, old_phone, new_phone = args
    record = book.find(name)

    if record is None:
        raise KeyError

    record.edit_phone(old_phone, new_phone)
    return "[green]Contact changed.[/green]"


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

    for record in book.data.values():
        phones = "; ".join(phone.value for phone in record.phones)

        birthday = (
            record.birthday.value.strftime("%d.%m.%Y")
            if record.birthday
            else "-"
        )

        table.add_row(
            record.name.value,
            phones,
            birthday,
        )

    console.print(table)


@input_error
def add_birthday(args, book):
    """Set a contact's birthday."""
    name, birthday = args
    record = book.find(name)

    if record is None:
        raise KeyError

    record.add_birthday(birthday)
    return "[green]Birthday added.[/green]"


@input_error
def show_birthday(args, book):
    """Show a contact's birthday."""
    name = args[0]
    record = book.find(name)

    if record is None:
        raise KeyError

    if record.birthday is None:
        return "[red]Birthday not set[/red]"

    return (
        f"[green]{name}'s birthday: [/green]"
        f"[green]{record.birthday.value.strftime('%d.%m.%Y')}[/green]"
    )


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
