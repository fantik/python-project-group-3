"""Provide a tiny ``rich`` stub so tests can run without the dependency."""

import builtins
import importlib
import sys
import types


def ensure_rich_stub():
    """Install a minimal ``rich`` stub only when ``rich`` is unavailable."""
    try:
        importlib.import_module("rich.console")
        importlib.import_module("rich.table")
        return
    except ModuleNotFoundError:
        pass

    rich_module = types.ModuleType("rich")
    console_module = types.ModuleType("rich.console")
    table_module = types.ModuleType("rich.table")

    class Console:
        def print(self, *args, **kwargs):
            return None

    class Table:
        def __init__(self, *args, **kwargs):
            return None

        def add_column(self, *args, **kwargs):
            return None

        def add_row(self, *args, **kwargs):
            return None

    console_module.Console = Console
    table_module.Table = Table
    rich_module.print = builtins.print
    sys.modules["rich"] = rich_module
    sys.modules["rich.console"] = console_module
    sys.modules["rich.table"] = table_module
