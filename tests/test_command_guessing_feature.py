"""Tests for unknown-command detection and closest-command suggestions."""

import unittest

from tests._rich_stub import ensure_rich_stub

ensure_rich_stub()

from handlers import format_unknown_command, parse_input, suggest_command


class SuggestCommandTests(unittest.TestCase):
    """Cover fuzzy matching for mistyped command names."""

    def test_suggest_command_returns_closest_match_for_typo(self):
        self.assertEqual(suggest_command("serch"), "search")
        self.assertEqual(suggest_command("hepl"), "help")
        self.assertEqual(suggest_command("add-not"), "add-note")

    def test_suggest_command_returns_none_when_no_close_match(self):
        self.assertIsNone(suggest_command("xyz"))
        self.assertIsNone(suggest_command("qwerty"))

    def test_suggest_command_uses_custom_command_list(self):
        choices = ["alpha", "beta"]
        self.assertEqual(suggest_command("bta", commands=choices), "beta")
        self.assertIsNone(suggest_command("gamma", commands=choices))


class FormatUnknownCommandTests(unittest.TestCase):
    """Cover user-facing messages for unknown commands."""

    def test_format_unknown_command_includes_suggestion_when_available(self):
        message = format_unknown_command("serch")

        self.assertIn("Unknown command: serch.", message)
        self.assertIn("Did you mean [green]search[/green]?", message)

    def test_format_unknown_command_suggests_help_when_no_match(self):
        message = format_unknown_command("xyz")

        self.assertIn("Unknown command: xyz.", message)
        self.assertIn("Type 'help' to see usage.", message)
        self.assertNotIn("Did you mean", message)


class ParseInputCommandGuessingTests(unittest.TestCase):
    """Cover parse_input behavior for known and unknown commands."""

    def test_parse_input_passes_through_valid_command_and_args(self):
        self.assertEqual(parse_input("search Olga"), ("search", "Olga"))
        self.assertEqual(parse_input("add-note Olga buy milk"), ("add-note", "Olga", "buy", "milk"))

    def test_parse_input_normalizes_command_to_lowercase(self):
        self.assertEqual(parse_input("HELP"), ("help",))

    def test_parse_input_marks_unknown_command(self):
        command, *rest = parse_input("serch Olga")

        self.assertEqual(command, "unknown_command")
        self.assertEqual(rest, ["serch"])

    def test_parse_input_preserves_args_for_unknown_command(self):
        command, *rest = parse_input("add-not Olga buy milk")

        self.assertEqual(command, "unknown_command")
        self.assertEqual(rest[0], "add-not")

    def test_parse_input_returns_empty_command_for_blank_input(self):
        self.assertEqual(parse_input(""), ("",))
        self.assertEqual(parse_input("   "), ("",))


if __name__ == "__main__":
    unittest.main()
