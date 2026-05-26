"""Address book CLI entry point."""

from rich import print as rprint

from handlers import (
    add_birthday,
    add_contact,
    birthdays,
    change_contact,
    parse_input,
    show_all,
    show_birthday,
    show_phone,
)
from storage import load_data, save_data


def main():
    """Run the address book CLI loop."""
    book = load_data()

    commands = {
        "hello": lambda args: "How can I help you?",
        "add": lambda args: add_contact(args, book),
        "change": lambda args: change_contact(args, book),
        "phone": lambda args: show_phone(args, book),
        "all": lambda args: show_all(book),
        "add-birthday": lambda args: add_birthday(args, book),
        "show-birthday": lambda args: show_birthday(args, book),
        "birthdays": lambda args: birthdays(book),
    }

    rprint("[cyan]Welcome to the assistant bot![/cyan]")

    try:
        while True:
            user_input = input("Enter a command: ")
            command, *args = parse_input(user_input)

            if command in ["close", "exit"]:
                rprint("[cyan]Good bye![/cyan]")
                break

            handler = commands.get(command)

            if handler:
                result = handler(args)

                if result is not None:
                    rprint(result)
            else:
                rprint("[red]Invalid command.[/red]")
    finally:
        save_data(book)


if __name__ == "__main__":
    main()
