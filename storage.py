"""Persistence layer for the address book."""

import os
import pickle

from models import AddressBook

FILE_NAME = "addressbook.pkl"


def save_data(book, filename=FILE_NAME):
    """Serialize the address book to disk."""
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename=FILE_NAME):
    """Load the address book from disk, or return an empty book."""
    if os.path.exists(filename):
        try:
            with open(filename, "rb") as f:
                return pickle.load(f)
        except (pickle.UnpicklingError, EOFError, OSError):
            return AddressBook()
    return AddressBook()
