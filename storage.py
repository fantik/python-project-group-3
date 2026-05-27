"""Persistence layer for the address book."""

import os
import pickle
import tempfile

from models import AddressBook

FILE_NAME = "addressbook.pkl"


class StorageError(Exception):
    """Raised when persisted contacts cannot be loaded safely."""

    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return (
            f"[red]Could not load saved contacts from {self.filename}. "
            "The file may be corrupted or unreadable.[/red]"
        )


class StorageSaveError(Exception):
    """Raised when contacts cannot be saved safely."""

    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return (
            f"[red]Could not save contacts to {self.filename}. "
            "Your existing saved data was left unchanged.[/red]"
        )


def save_data(book, filename=FILE_NAME):
    """Serialize the address book to disk."""
    directory = os.path.dirname(os.path.abspath(filename)) or "."
    prefix = f".{os.path.basename(filename)}."
    file_descriptor = None
    temp_filename = None

    try:
        file_descriptor, temp_filename = tempfile.mkstemp(
            dir=directory,
            prefix=prefix,
            suffix=".tmp",
        )
        with os.fdopen(file_descriptor, "wb") as stream:
            pickle.dump(book, stream)
        file_descriptor = None
        os.replace(temp_filename, filename)
    except Exception as exc:
        if file_descriptor is not None:
            try:
                os.close(file_descriptor)
            except OSError:
                pass

        try:
            if temp_filename is not None:
                os.remove(temp_filename)
        except OSError:
            pass
        raise StorageSaveError(filename) from exc


def load_data(filename=FILE_NAME):
    """Load the address book from disk, or return an empty book."""
    if os.path.exists(filename):
        try:
            with open(filename, "rb") as f:
                loaded_data = pickle.load(f)
        except (
            pickle.UnpicklingError,
            EOFError,
            OSError,
            ImportError,
            AttributeError,
            ValueError,
        ) as exc:
            raise StorageError(filename) from exc

        if not isinstance(loaded_data, AddressBook):
            raise StorageError(filename)

        return loaded_data
    return AddressBook()
