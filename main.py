"""Address book CLI entry point."""

from rich import print as rprint

from handlers import (
    add_address,
    add_birthday,
    add_contact,
    add_email,
    birthdays,
    edit_contact,
    search_contacts,
    parse_input,
    show_help,
    show_all,
    show_contact,
    show_birthday,
    show_phone,
    remove_contact,
    add_note,
    remove_note,
    edit_note,
    find_note,
    all_notes,
)
from greeting import print_goodbye_banner, print_welcome_banner
from storage import StorageError, StorageSaveError, load_data, save_data


def main():
    """Run the address book CLI loop."""
    try:
        book = load_data()
    except StorageError as exc:
        rprint(str(exc))
        return

    commands = {
        "hello": lambda args: "How can I help you?",
        "help": lambda args: show_help(),
        "add": lambda args: add_contact(args, book),
        "search": lambda args: search_contacts(args, book),
        "phone": lambda args: show_phone(args, book),
        "all": lambda args: show_all(book),
        "show-contact": lambda args: show_contact(args, book),
        "add-address": lambda args: add_address(args, book),
        "add-email": lambda args: add_email(args, book),
        "edit-contact": lambda args: edit_contact(args, book),
        "add-birthday": lambda args: add_birthday(args, book),
        "show-birthday": lambda args: show_birthday(args, book),
        "birthdays": lambda args: birthdays(args, book),
        "remove-contact": lambda args: remove_contact(args, book),
        "add-note": lambda args: add_note(args, book),
        "remove-note": lambda args: remove_note(args, book),
        "edit-note": lambda args: edit_note(args, book),
        "find-note": lambda args: find_note(args, book),
        "all-notes": lambda args: all_notes(args, book),
    }

    print_welcome_banner()

    try:
        while True:
            try:
                user_input = input("Enter a command: ")
            except (EOFError, KeyboardInterrupt):
                print_goodbye_banner()
                break

            command, *args = parse_input(user_input)

            if command == "__parse_error__":
                rprint(f"[red]Invalid input: {args[0]}[/red]")
                continue

            if not command:
                continue

            if command in ["close", "exit"]:
                print_goodbye_banner()
                break

            handler = commands.get(command)

            if handler:
                result = handler(args)

                if result is not None:
                    rprint(result)
            else:
                rprint("[red]Invalid command.[/red]")
    finally:
        try:
            save_data(book)
        except StorageSaveError as exc:
            rprint(str(exc))


if __name__ == "__main__":
    main()
