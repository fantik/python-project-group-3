"""CLI command handlers and input parsing."""

from functools import wraps
import shlex
import re
import difflib

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from models import Record
from validators import (
    ContactNotFoundError,
    validate_address,
    validate_birthday,
    validate_email,
    validate_name,
    validate_phone,
    validate_tag,
)

console = Console()
PLACEHOLDER = "—"
NOTE_BULLET = "*"

KNOWN_COMMANDS = frozenset(
    [
        "add",
        "search",
        "phone",
        "all",
        "show-contact",
        "add-email",
        "add-address",
        "edit-contact",
        "remove-contact",
        "add-birthday",
        "show-birthday",
        "birthdays",
        "add-note",
        "edit-note",
        "remove-note",
        "find-note",
        "all-notes",
        "add-tag",
        "remove-tag",
        "find-notes-by-tag",
        "sort-notes-by-tag",
        "hello",
        "help",
        "exit",
        "close",
    ]
)


def suggest_command(command, *, commands=None):
    """Return the closest matching command from known commands."""
    choices = commands or KNOWN_COMMANDS
    matches = difflib.get_close_matches(command, choices, n=1, cutoff=0.6)
    return matches[0] if matches else None


def format_unknown_command(command):
    """Format an unknown command message with a suggested close match."""
    suggestion = suggest_command(command)
    if suggestion:
        return (
            f"[red]Unknown command '{command}'. "
            f"Did you mean '{suggestion}'?[/red]"
        )
    return f"[red]Unknown command '{command}'. Type 'help' to see usage.[/red]"


def input_error(func):
    """Decorator that returns exception messages instead of raising."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ContactNotFoundError as exc:
            return str(exc)
        except (ValueError, KeyError, IndexError) as exc:
            # These should generally be raised with user-friendly messages
            # by handlers/validators. If not, fall back to a helpful hint.
            message = str(exc).strip()
            if message:
                return message
            return "[red]Invalid input. Type 'help' to see usage.[/red]"
        except TypeError:
            # Most often indicates wrong handler arity or incorrect internal call.
            return (
                "[red]Invalid input for this command. "
                "Type 'help' to see usage.[/red]"
            )
        except Exception:
            # Catch-all: avoid exposing internal tracebacks to the user.
            return (
                "[red]Something went wrong while processing the command. "
                "Type 'help' to see available commands.[/red]"
            )

    return wrapper


@input_error
def show_help():
    """Print a help panel with available commands."""
    contacts_lines = [
        "[bold]add[/bold] <name> <phone>",
        "[bold]search[/bold] <query>  (search in all fields)",
        "[bold]search[/bold] <name|-> <phone|-> <email|-> <address|->  (advanced filter)",
        "[bold]phone[/bold] <name>",
        "[bold]all[/bold]",
        "[bold]show-contact[/bold] <name>",
        "[bold]add-email[/bold] <name> <email>",
        "[bold]add-address[/bold] <name> <address>",
        "[bold]edit-contact[/bold] <name> <field> <value...>",
        "[bold]remove-contact[/bold] <name>",
    ]

    birthdays_lines = [
        "[bold]add-birthday[/bold] <name> <DD.MM.YYYY>",
        "[bold]show-birthday[/bold] <name>",
        "[bold]birthdays[/bold] <days>",
    ]

    notes_lines = [
        "[bold]add-note[/bold] <name> <note...>",
        "[bold]edit-note[/bold] <name> <id> <new_note...>",
        "[bold]remove-note[/bold] <name> <id>",
        "[bold]find-note[/bold] <name> <query...>",
        "[bold]all-notes[/bold] <name>",
        "[bold]add-tag[/bold] <name> <id> #tag [#tag...]",
        "[bold]remove-tag[/bold] <name> <id> #tag",
        "[bold]find-notes-by-tag[/bold] <name> #tag",
        "[bold]sort-notes-by-tag[/bold] <name>",
    ]

    general_lines = [
        "[bold]hello[/bold]",
        "[bold]help[/bold]",
        "[bold]exit[/bold] / [bold]close[/bold]",
    ]

    body = "\n".join(
        [
            "[bold cyan]Contacts[/bold cyan] 🤝",
            *[f"  - {line}" for line in contacts_lines],
            "",
            "[bold yellow]Birthdays[/bold yellow] 🎁",
            *[f"  - {line}" for line in birthdays_lines],
            "",
            "[bold bright_blue]Notes[/bold bright_blue] 📝",
            *[f"  - {line}" for line in notes_lines],
            "",
            "[bold green]General[/bold green] ⭐",
            *[f"  - {line}" for line in general_lines],
            "",
            "[magenta]Tip: Use quotes for multi-word names or notes,[/magenta]",
            "[bright_blue]e.g. add-note 'Lina Kostenko' 'buy tickets tomorrow'[/bright_blue]",
            "[bright_yellow]e.g. add-tag Olga 1 #shopping #urgent[/bright_yellow]",
        ]
    )

    console.print(Panel(body, title="Help", border_style="cyan", expand=False))


def parse_input(user_input):
    """Split user input into command and arguments."""
    try:
        lexer = shlex.shlex(user_input, posix=True)
        lexer.whitespace_split = True
        lexer.commenters = ""
        lexer.quotes = "\"'"
        parts = list(lexer)
    except ValueError as exc:
        return "__parse_error__", str(exc)

    if not parts:
        return ("",)

    cmd, *args = parts
    cmd = cmd.strip().lower()
    if cmd and cmd not in KNOWN_COMMANDS:
        suggestion = suggest_command(cmd)
        return "unknown_command", cmd, suggestion
    return cmd, *args

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

    table = Table(title="Contacts")
    table.add_column("Name", style="cyan")
    table.add_column("Phones", style="green")
    table.add_column("Email", style="blue")
    table.add_column("Address", style="magenta")
    table.add_column("Birthday", style="yellow")
    table.add_column("Days to birthday", style="bright_yellow")
    table.add_column("Notes", style="bright_blue", overflow="fold")

    records = list(book.data.values())
    for index, record in enumerate(records):
        details = get_contact_details(record)

        table.add_row(
            details["name"],
            details["phones"],
            details["email"],
            details["address"],
            details["birthday"],
            details["days_to_birthday"],
            details["notes"],
        )
        if index < len(records) - 1:
            table.add_row(*([""] * 7))

    console.print(table)


def _build_contacts_table(title="Contacts"):
    """Create a Rich Table for displaying contacts in a consistent format."""
    table = Table(title=title)
    table.add_column("Name", style="cyan")
    table.add_column("Phones", style="green")
    table.add_column("Email", style="blue")
    table.add_column("Address", style="magenta")
    table.add_column("Birthday", style="yellow")
    table.add_column("Days to birthday", style="bright_yellow")
    table.add_column("Notes", style="bright_blue", overflow="fold")
    return table


def _normalize_search_token(value):
    """Treat '-' and empty tokens as missing criteria."""
    if value is None:
        return None
    cleaned = str(value).strip()
    if not cleaned or cleaned == "-":
        return None
    return cleaned


def _text_matches(candidate, query, *, partial):
    if query is None:
        return True
    candidate = candidate or ""
    if partial:
        return query.lower() in candidate.lower()
    return candidate == query


def _phone_partial_query(query):
    """Return a best-effort normalized phone query for partial matching."""
    if query is None:
        return None

    # If it's a full valid phone, reuse the normal validator for consistency.
    try:
        return validate_phone(query)
    except ValueError:
        pass

    digits = re.sub(r"\D", "", query)
    if not digits:
        return None
    if digits.startswith("380") and len(digits) >= 12:
        return f"0{digits[3:12]}"
    return digits


def _phone_matches(record, query, *, partial):
    if query is None:
        return True
    record_phones = [phone.value for phone in getattr(record, "phones", [])]
    if not record_phones:
        return False

    if partial:
        part = _phone_partial_query(query)
        if part is None:
            return False
        return any(part in phone for phone in record_phones)

    normalized = validate_phone(query)
    return any(phone == normalized for phone in record_phones)


def _note_matches(record, query, *, partial):
    """Return True when any note text or tag matches the query."""
    if query is None:
        return True
    notes = getattr(record, "notes", []) or []
    if not notes:
        return False
    if partial:
        part = query.lower()
        return any(
            part in (note.value or "").lower()
            or any(part in tag.value for tag in getattr(note, "tags", []))
            for note in notes
        )
    return any((note.value or "") == query for note in notes)


def _render_contacts(records, *, title="Contacts"):
    """Render contacts to Rich Table using the standard columns."""
    table = _build_contacts_table(title)
    for index, record in enumerate(records):
        details = get_contact_details(record)
        table.add_row(
            details["name"],
            details["phones"],
            details["email"],
            details["address"],
            details["birthday"],
            details["days_to_birthday"],
            details["notes"],
        )
        if index < len(records) - 1:
            table.add_row(*([""] * 7))
    console.print(table)


@input_error
def search_contacts(args, book):
    """Search contacts by partial (contains) match.

    Modes:
    - search <query>                          -> global OR across fields
    - search <name|-> <phone|-> <email|-> <address|-> -> AND across provided fields
    """
    partial = True

    if len(args) > 4:
        raise ValueError(
            "[red]Usage: search <name|-> <phone|-> <email|-> <address|->[/red]"
        )

    if len(args) == 1:
        query = _normalize_search_token(args[0])
        if query is not None:
            matches = []
            for record in book.data.values():
                email_val = getattr(getattr(record, "email", None), "value", "")
                address_val = getattr(getattr(record, "address", None), "value", "")
                if (
                    _text_matches(record.name.value, query, partial=partial)
                    or _phone_matches(record, query, partial=partial)
                    or _text_matches(email_val, query, partial=partial)
                    or _text_matches(address_val, query, partial=partial)
                    or _note_matches(record, query, partial=partial)
                ):
                    matches.append(record)

            if not matches:
                return "[yellow]Nothing found[/yellow]"

            _render_contacts(matches, title="Contacts")
            return None

    padded = list(args) + ["-"] * (4 - len(args))
    name_q, phone_q, email_q, address_q = (
        _normalize_search_token(padded[0]),
        _normalize_search_token(padded[1]),
        _normalize_search_token(padded[2]),
        _normalize_search_token(padded[3]),
    )

    matches = []
    for record in book.data.values():
        email_val = getattr(getattr(record, "email", None), "value", "")
        address_val = getattr(getattr(record, "address", None), "value", "")
        if not _text_matches(record.name.value, name_q, partial=partial):
            continue
        if not _phone_matches(record, phone_q, partial=partial):
            continue
        if not _text_matches(email_val, email_q, partial=partial):
            continue
        if not _text_matches(address_val, address_q, partial=partial):
            continue
        matches.append(record)

    if not matches:
        return "[yellow]Nothing found[/yellow]"

    _render_contacts(matches, title="Contacts")
    return None


def format_notes_for_display(record):
    """Return notes as a bulleted multiline string for Rich output."""
    if not record.notes:
        return PLACEHOLDER
    lines = []
    for note in record.notes:
        tags = _format_note_tags(note)
        suffix = f" ({tags})" if tags != PLACEHOLDER else ""
        lines.append(
            f"{NOTE_BULLET} \\[note id: {note.id}] "
            f"{note.value}{suffix}"
        )
    return "\n".join(lines)


def _format_note_tags(note):
    """Return note tags as a space-separated #tag string."""
    if not note.tags:
        return PLACEHOLDER
    return " ".join(f"#{tag.value}" for tag in note.tags)


def _parse_note_id(token):
    """Return note id or raise when the token is not a positive integer."""
    if token.isdigit() and int(token) > 0:
        return int(token)
    raise ValueError("[red]Note id must be a positive integer.[/red]")


def _render_notes_table(notes, title):
    """Print notes in a table with id, text, and tags columns."""
    table = Table(title=title)
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Note", style="bright_blue", overflow="fold")
    table.add_column("Tags", style="magenta", overflow="fold")
    for note in notes:
        table.add_row(
            str(note.id),
            f"{NOTE_BULLET} {note.value}",
            _format_note_tags(note),
        )
    console.print(table)


def _parse_tag_tokens(tokens):
    """Parse CLI tokens that must start with # into validated tag names."""
    if not tokens:
        raise ValueError(
            "[red]Usage: provide at least one tag starting with #, "
            "e.g. #shopping[/red]"
        )

    parsed = []
    for token in tokens:
        if not token.startswith("#") or len(token) < 2:
            raise ValueError(
                "[red]Each tag must start with #, e.g. #shopping[/red]"
            )
        parsed.append(validate_tag(token))
    return parsed


def _parse_tag_query(token):
    """Parse a single tag query token (# prefix optional for search)."""
    cleaned = (token or "").strip()
    if not cleaned:
        raise ValueError(
            "[red]Usage: find-notes-by-tag [name] #tag[/red]"
        )
    if not cleaned.startswith("#"):
        cleaned = f"#{cleaned}"
    if len(cleaned) < 2:
        raise ValueError(
            "[red]Tag query must start with #, e.g. #shopping[/red]"
        )
    return cleaned.lstrip("#")


def resolve_contact_note_id_and_tail(args, book, *, min_tail=0):
    """Resolve contact name, record, note id, and remaining CLI tokens."""
    _name, record, remaining = resolve_contact_for_note_args(args, book)
    if record is None:
        return None, None, None, []

    if len(remaining) < 1 + min_tail:
        raise ValueError(
            "[red]Usage: command requires contact name, note id, "
            "and additional arguments[/red]"
        )

    note_id = _parse_note_id(remaining[0])
    return _name, record, note_id, remaining[1:]


def get_contact_details(record):
    """Return a user-facing mapping of contact fields."""
    phones = "; ".join(phone.value for phone in record.phones) or PLACEHOLDER
    email_field = getattr(record, "email", None)
    address_field = getattr(record, "address", None)
    days_to_birthday = record.days_to_birthday()
    notes = format_notes_for_display(record)
    return {
        "name": record.name.value,
        "phones": phones,
        "email": email_field.value if email_field else PLACEHOLDER,
        "address": (
            address_field.value if address_field else PLACEHOLDER
        ),
        "birthday": (
            record.birthday.value.strftime("%d.%m.%Y")
            if record.birthday
            else PLACEHOLDER
        ),
        "days_to_birthday": (
            str(days_to_birthday)
            if days_to_birthday is not None
            else PLACEHOLDER
        ),
        "notes": notes,
    }


@input_error
def show_contact(args, book):
    """Print a single contact in a Rich panel."""
    require_min_args(args, 1, "show-contact [name]")
    name = join_name_parts(args)
    record = book.find(name)

    if record is None:
        return "[red]Contact not found[/red]"

    details = get_contact_details(record)
    panel_body = "\n".join(
        [
            f"[bold cyan]Name:[/bold cyan] {details['name']}",
            f"[bold green]Phones:[/bold green] {details['phones']}",
            f"[bold blue]Email:[/bold blue] {details['email']}",
            f"[bold magenta]Address:[/bold magenta] {details['address']}",
            f"[bold yellow]Birthday:[/bold yellow] {details['birthday']}",
            (
                "[bold bright_yellow]Days to birthday:"
                f"[/bold bright_yellow] {details['days_to_birthday']}"
            ),
            (
                "[bold bright_blue]Notes:[/bold bright_blue]\n"
                f"{details['notes']}"
            ),
        ]
    )
    panel = Panel(
        panel_body,
        title="Contact details",
        subtitle=details["name"],
        border_style="cyan",
        expand=False,
    )
    console.print(panel)


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


def resolve_contact_for_note_args(args, book, *, name_only=False):
    """Split note-command tokens into contact name, record, and note text tail.

    Unlike single-value fields (email, phone), note text can contain spaces.
    We find existing contact-name prefix matches; the rest is note-related
    tokens (one note, or old/new pair for edit-note).

    When ``name_only`` is True (``all-notes``), every token must belong to the
    contact name and the longest matching name is used.
    """
    matches = []
    for index in range(1, len(args) + 1):
        if name_only and index != len(args):
            continue

        name = join_name_parts(args[:index])
        record = book.find(name)
        if record is not None:
            matches.append((name, record, args[index:]))

    if not matches:
        return None, None, []

    if name_only:
        return matches[-1]

    if len(matches) > 1:
        raise ValueError(
            "[red]Ambiguous contact name. Please use a unique name.[/red]"
        )

    return matches[0]

@input_error
def add_note(args, book):
    """Add a note to a contact."""
    require_min_args(args, 2, "add-note [name] [note]")
    _name, record, remaining = resolve_contact_for_note_args(args, book)
    if record is None:
        return "[red]Contact not found[/red]"

    note = " ".join(remaining).strip()
    if not note:
        raise ValueError("[red]Usage: add-note [name] [note][/red]")

    note_id = record.add_note(note)
    return f"[green]Note added with id {note_id}.[/green]"


@input_error
def remove_note(args, book):
    """Remove a note from a contact by id."""
    require_min_args(args, 2, "remove-note [name] <id>")
    _name, record, note_id, tail = resolve_contact_note_id_and_tail(args, book)
    if record is None:
        return "[red]Contact not found[/red]"

    if tail:
        raise ValueError("[red]Usage: remove-note [name] <id>[/red]")

    record.remove_note(note_id)
    return f"[green]Note {note_id} removed.[/green]"


@input_error
def edit_note(args, book):
    """Edit a note in a contact by id."""
    require_min_args(args, 3, "edit-note [name] <id> <new_note...>")
    _name, record, note_id, tail = resolve_contact_note_id_and_tail(
        args, book, min_tail=1
    )
    if record is None:
        return "[red]Contact not found[/red]"

    new_note = " ".join(tail).strip()
    if not new_note:
        raise ValueError(
            "[red]Usage: edit-note [name] <id> <new_note...>[/red]"
        )

    record.edit_note(note_id, new_note)
    return f"[green]Note {note_id} edited.[/green]"


@input_error
def find_note(args, book):
    """Find contact notes whose text contains the query (case-insensitive)."""
    require_min_args(args, 2, "find-note [name] [query]")
    name, record, remaining = resolve_contact_for_note_args(args, book)
    if record is None:
        return "[red]Contact not found[/red]"

    query = " ".join(remaining).strip()
    if not query:
        raise ValueError("[red]Usage: find-note [name] [query][/red]")

    matches = record.find_notes_by_query(query)
    if not matches:
        return (
            f"[yellow]No notes matching '{query}' "
            f"for contact '{name}'.[/yellow]"
        )

    _render_notes_table(matches, title=f"Notes matching '{query}' — {name}")

@input_error
def all_notes(args, book):
    """Show all notes for a contact."""
    require_min_args(args, 1, "all-notes [name]")
    name, record, remaining = resolve_contact_for_note_args(
        args, book, name_only=True
    )
    if record is None:
        return "[red]Contact not found[/red]"

    if remaining:
        raise ValueError("[red]Usage: all-notes [name][/red]")

    if not record.notes:
        return f"[yellow]No notes for contact '{name}'.[/yellow]"

    _render_notes_table(record.notes, title=f"All notes for {name}")


@input_error
def add_tag(args, book):
    """Add one or more tags to a contact note."""
    require_min_args(args, 3, "add-tag [name] <id> #tag [#tag...]")
    _name, record, note_id, tag_tokens = resolve_contact_note_id_and_tail(
        args, book, min_tail=1
    )
    if record is None:
        return "[red]Contact not found[/red]"

    tags = _parse_tag_tokens(tag_tokens)
    record.add_tags(note_id, *tags)
    return f"[green]Tags added to note {note_id}.[/green]"


@input_error
def remove_tag(args, book):
    """Remove a tag from a contact note."""
    require_min_args(args, 3, "remove-tag [name] <id> #tag")
    _name, record, note_id, tag_tokens = resolve_contact_note_id_and_tail(
        args, book, min_tail=1
    )
    if record is None:
        return "[red]Contact not found[/red]"

    if len(tag_tokens) != 1:
        raise ValueError("[red]Usage: remove-tag [name] <id> #tag[/red]")

    tag = _parse_tag_tokens(tag_tokens)[0]
    record.remove_tag(note_id, tag)
    return f"[green]Tag #{tag} removed from note {note_id}.[/green]"


@input_error
def find_notes_by_tag(args, book):
    """Find contact notes that contain a tag (partial match)."""
    require_min_args(args, 2, "find-notes-by-tag [name] #tag")
    name, record, remaining = resolve_contact_for_note_args(args, book)
    if record is None:
        return "[red]Contact not found[/red]"

    if len(remaining) != 1:
        raise ValueError("[red]Usage: find-notes-by-tag [name] #tag[/red]")

    tag_query = _parse_tag_query(remaining[0])
    matches = record.find_notes_by_tag(tag_query, partial=True)
    if not matches:
        return (
            f"[yellow]No notes with tag matching '#{tag_query}' "
            f"for contact '{name}'.[/yellow]"
        )

    _render_notes_table(
        matches,
        title=f"Notes with tag '#{tag_query}' — {name}",
    )


@input_error
def sort_notes_by_tag(args, book):
    """Show contact notes sorted by their first tag."""
    require_min_args(args, 1, "sort-notes-by-tag [name]")
    name, record, remaining = resolve_contact_for_note_args(
        args, book, name_only=True
    )
    if record is None:
        return "[red]Contact not found[/red]"

    if remaining:
        raise ValueError("[red]Usage: sort-notes-by-tag [name][/red]")

    if not record.notes:
        return f"[yellow]No notes for contact '{name}'.[/yellow]"

    sorted_notes = record.sort_notes_by_tags()
    _render_notes_table(
        sorted_notes,
        title=f"Notes sorted by tag — {name}",
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

@input_error
def remove_contact(args, book):
    """Remove a contact completely after confirmation."""
    require_min_args(args, 1, "remove-contact [name]")
    name = join_name_parts(args)

    record = book.find(name)
    if record is None:
        raise ContactNotFoundError()

    print(f"  You are about to delete contact '{name}'")
    try:
        confirm = input("Are you sure? (y/n): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return "[yellow]Deletion cancelled.[/yellow]"

    if confirm in ["y", "yes"]:
        book.delete(name)
        return f"[green]Contact '{name}' has been deleted successfully.[/green]"

    return "[yellow]Deletion cancelled.[/yellow]"

